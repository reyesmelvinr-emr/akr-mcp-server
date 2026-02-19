"""
Transformation logic: ExtractedData → Template Context Models.

Provides factory functions to transform ExtractedData objects (from code analysis)
into template context models (for Jinja2 rendering).

Functions:
    - build_service_context(): ExtractedData list → ServiceTemplateContext
    - build_component_context(): ExtractedData list → ComponentTemplateContext
    - build_table_context(): ExtractedData list → TableTemplateContext
"""

import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from .extractors.base_extractor import ExtractedData
from .extractors.example_extractor import ExampleDataExtractor
from .template_context import (
    ServiceTemplateContext, ComponentTemplateContext, TableTemplateContext,
    EndpointContext, DependencyContext, ValidationRuleContext, MethodContext,
    BusinessRuleContext, DataOperationContext,
    PropContext, EventContext, StateContext, VariantContext,
    ColumnContext, ConstraintContext, ForeignKeyContext
)


logger = logging.getLogger(__name__)


def build_service_context(
    service_name: str,
    extracted_data_list: List[ExtractedData],
    namespace: Optional[str] = None,
    domain: Optional[str] = None
) -> ServiceTemplateContext:
    """
    Transform extracted C# data into ServiceTemplateContext.
    
    Args:
        service_name: Name of the service being documented (can be overridden by extracted data)
        extracted_data_list: List of ExtractedData from C# files
        namespace: Optional C# namespace
        domain: Optional domain/folder name
        
    Returns:
        ServiceTemplateContext ready for Jinja2 rendering
    """
    # PHASE 10: Improve service name extraction - prioritize interface files
    actual_service_name = _extract_actual_service_name(extracted_data_list, service_name)
    actual_namespace = _extract_namespace(extracted_data_list) or namespace
    
    context = ServiceTemplateContext(
        service_name=actual_service_name,
        namespace=actual_namespace,
        domain=domain
    )
    
    # Collect data from all extracted sources
    all_extracted = _aggregate_extracted_data(extracted_data_list)
    
    # Transform endpoints from routes
    context.endpoints = [
        EndpointContext(
            method=route.method,
            path=route.path,
            handler=route.handler_name,
            summary=route.description or f"{route.method} {route.path}",
            status_codes=route.status_codes,
            response_types=route.response_types,
            parameters=[{'name': p.name, 'type': p.type} for p in route.parameters]
        )
        for route in all_extracted['routes']
    ]
    
    # Transform dependencies
    # PHASE 10.2/10.3: Include failure mode information for each dependency
    failure_modes = {}
    for extracted in extracted_data_list:
        for fm_data in extracted.raw_data.get('failure_modes', []):
            exc_type = fm_data.get('exception_type', '')
            if exc_type not in failure_modes:
                failure_modes[exc_type] = []
            failure_modes[exc_type].append(fm_data)
    
    context.dependencies = []
    for dep in all_extracted['dependencies']:
        dep_context = DependencyContext(
            name=dep.name,
            type=dep.type,
            purpose=dep.description or "Injected dependency",
            code_location="<source>"
        )
        
        # PHASE 10.3: Improved failure impact matching using heuristics
        possible_failures = []
        
        # Heuristic 1: If extracted failure modes exist, try to match by dependency type
        if failure_modes:
            if 'Repository' in dep.type or 'Db' in dep.type:
                for exc_type in ['DbUpdateException', 'SqlException', 'TimeoutException', 'InvalidOperationException']:
                    if exc_type in failure_modes:
                        possible_failures.extend([f"{exc_type}: {fm.get('impact', '')}" 
                                                for fm in failure_modes[exc_type][:1]])  # First match only
            else:
                for exc_type in ['InvalidOperationException', 'TimeoutException', 'OperationCanceledException']:
                    if exc_type in failure_modes:
                        possible_failures.extend([f"{exc_type}: {fm.get('impact', '')}" 
                                                for fm in failure_modes[exc_type][:1]])
        
        # Heuristic 2: If no failure modes found, infer from dependency type
        if not possible_failures:
            if 'Repository' in dep.type or 'Db' in dep.type:
                possible_failures = ["DbUpdateException: Constraint/data integrity issue | SqlException: Database unavailable"]
            elif 'Service' in dep.type:
                possible_failures = ["InvalidOperationException: Business rule violation | TimeoutException: Service slow or unavailable"]
            elif 'Logger' in dep.type:
                possible_failures = ["NullReferenceException: Non-blocking, logging skipped"]
            else:
                possible_failures = ["Timeout or null reference: Service degradation"]
        
        if possible_failures:
            dep_context.failure_impact = " | ".join(possible_failures[:2])  # PHASE 10.3: Limit to 2 items
            logger.info(f"PHASE 10.3: Added failure impact for {dep.name}: {dep_context.failure_impact}")
        
        context.dependencies.append(dep_context)
    
    # Transform DTOs (request/response models) - PHASE 7 ENHANCEMENT
    logger.info(f"Phase 7 DTO transformation: 'dtos' in all_extracted = {'dtos' in all_extracted}")
    if 'dtos' in all_extracted:
        logger.info(f"Phase 7: Found {len(all_extracted['dtos'])} DTOs")
    
    if 'dtos' in all_extracted and all_extracted['dtos']:
        context.request_response_examples = {}
        context.request_response_schemas = {}
        
        # PHASE 10.2: Initialize example extractor for realistic examples
        example_extractor = ExampleDataExtractor()
        
        for dto in all_extracted['dtos']:
            logger.info(f"Phase 7: Processing DTO {dto.name} (type: {dto.dto_type})")
            # Generate sample JSON for each DTO
            extractor = None
            try:
                from .extractors.dto_extractor import DTOExtractor
                extractor = DTOExtractor()
            except:
                pass
            
            # PHASE 10.2: Try to extract realistic examples using new extractor
            sample_json = {}
            dto_file_path = None
            
            # Find source file for this DTO if available - PHASE 10.2 IMPROVED
            logger.info(f"PHASE 10.2: Looking for DTO {dto.name} in {len(extracted_data_list)} extracted files")
            for extracted in extracted_data_list:
                dto_names_in_file = extracted.raw_data.get('dto_names', [])
                logger.debug(f"  File {extracted.file_path}: DTOs = {dto_names_in_file}")
                if extracted.file_path and dto.name in dto_names_in_file:
                    dto_file_path = Path(extracted.file_path)
                    logger.info(f"PHASE 10.2: Found DTO {dto.name} in {dto_file_path}")
                    break
            
            # Try to extract examples from DTO source
            if dto_file_path and dto_file_path.exists():
                try:
                    file_content = dto_file_path.read_text(encoding='utf-8')
                    example_data = example_extractor.extract_examples_from_content(
                        file_content, 
                        dto.name
                    )
                    if example_data and len(example_data) > 0:  # PHASE 10.2: Check for non-empty dict
                        sample_json = example_data
                        logger.info(f"PHASE 10.2: ✅ Extracted realistic examples for DTO {dto.name}")
                    else:
                        logger.debug(f"PHASE 10.2: Example extractor returned empty for {dto.name}")
                except Exception as e:
                    logger.debug(f"PHASE 10.2: Could not extract examples from {dto_file_path}: {e}")
            else:
                if dto_file_path:
                    logger.debug(f"PHASE 10.2: DTO file path does not exist: {dto_file_path}")
                else:
                    logger.debug(f"PHASE 10.2: No source file found for DTO {dto.name}")
            
            # Fall back to DTOExtractor if no realistic examples found
            if not sample_json and extractor:
                sample_json = extractor.generate_sample_json(dto)
                validation_matrix = extractor.generate_validation_matrix(dto)
                logger.info(f"PHASE 10.2: Used DTOExtractor fallback for {dto.name}")
            else:
                validation_matrix = []
            
            # Map DTO to endpoints
            if 'Request' in dto.dto_type:
                logger.info(f"Phase 7: Adding {dto.name} to request_response_examples as request")
                context.request_response_examples[f"{dto.name}_request"] = {
                    'json': sample_json,
                    'properties': [{'name': p.name, 'type': p.type, 'required': p.required} for p in dto.properties]
                }
            elif 'Response' in dto.dto_type or 'Detail' in dto.dto_type:
                logger.info(f"Phase 7: Adding {dto.name} to request_response_examples as response")
                context.request_response_examples[f"{dto.name}_response"] = {
                    'json': sample_json,
                    'properties': [{'name': p.name, 'type': p.type, 'required': p.required} for p in dto.properties]
                }
            
            # Store validation matrix
            context.request_response_schemas[dto.name] = {
                'validations': validation_matrix,
                'properties': [{'name': p.name, 'type': p.type, 'required': p.required} for p in dto.properties]
            }
        
        logger.info(f"Phase 7 complete: {len(context.request_response_examples)} examples, {len(context.request_response_schemas)} schemas")
    
    # Transform operation flows - PHASE 8 ENHANCEMENT
    logger.info(f"Phase 8 flow transformation: 'operation_flows' in all_extracted = {'operation_flows' in all_extracted}")
    if 'operation_flows' in all_extracted:
        logger.info(f"Phase 8: Found {len(all_extracted['operation_flows'])} operation flows")
    
    if 'operation_flows' in all_extracted and all_extracted['operation_flows']:
        context.operation_flows = []
        
        for flow in all_extracted['operation_flows']:
            logger.info(f"Phase 8: Processing flow for {flow.method_name} ({flow.operation_type})")
            
            # Generate ASCII diagram
            ascii_diagram = flow.generate_ascii_diagram()
            
            # Convert to dict for template context
            flow_dict = {
                'method_name': flow.method_name,
                'operation_type': flow.operation_type,
                'ascii_diagram': ascii_diagram,
                'steps': [{
                    'number': step.step_number,
                    'type': step.step_type.value,
                    'description': step.description,
                    'what': step.what,
                    'why': step.why,
                    'error_path': step.error_path
                } for step in flow.steps],
                'success_path': flow.success_path,
                'failure_paths': flow.failure_paths
            }
            
            context.operation_flows.append(flow_dict)
        
        logger.info(f"Phase 8 complete: {len(context.operation_flows)} flows transformed")
    
    # Transform enhanced business rules, use cases, and FAQ - PHASE 9 ENHANCEMENT
    logger.info(f"Phase 9 transformation: 'enhanced_business_rules' in all_extracted = {'enhanced_business_rules' in all_extracted}")
    if 'enhanced_business_rules' in all_extracted:
        logger.info(f"Phase 9: Found {len(all_extracted['enhanced_business_rules'])} business rules")
    
    if 'enhanced_business_rules' in all_extracted and all_extracted['enhanced_business_rules']:
        context.enhanced_business_rules = []
        
        # PHASE 10.1: Deduplicate business rules by description + type
        seen_rules = set()
        duplicates_removed = 0
        
        for rule in all_extracted['enhanced_business_rules']:
            # Create composite key from description and rule type
            rule_key = (rule.description.strip(), rule.rule_type.value)
            
            if rule_key not in seen_rules:
                seen_rules.add(rule_key)
                rule_dict = {
                    'description': rule.description,
                    'rule_type': rule.rule_type.value,
                    'example': rule.example,
                    'violation_consequence': rule.violation_consequence,
                    'code_snippet': rule.code_snippet
                }
                context.enhanced_business_rules.append(rule_dict)
            else:
                duplicates_removed += 1
        
        logger.info(f"Phase 9: Transformed {len(context.enhanced_business_rules)} business rules (removed {duplicates_removed} duplicates)")
    
    # Transform use cases
    if 'use_cases' in all_extracted and all_extracted['use_cases']:
        context.use_cases = []
        
        # PHASE 10.1: Deduplicate use cases by title (operation type)
        seen_use_cases = {}
        use_case_duplicates = 0
        
        for use_case in all_extracted['use_cases']:
            title_key = use_case.title.strip()
            
            if title_key not in seen_use_cases:
                use_case_dict = {
                    'title': use_case.title,
                    'description': use_case.description,
                    'actor': use_case.actor,
                    'preconditions': use_case.preconditions,
                    'steps': use_case.steps,
                    'postconditions': use_case.postconditions
                }
                context.use_cases.append(use_case_dict)
                seen_use_cases[title_key] = True
            else:
                use_case_duplicates += 1
        
        logger.info(f"Phase 9: Transformed {len(context.use_cases)} use cases (removed {use_case_duplicates} duplicates)")
    
    # Transform FAQ items
    if 'faq_items' in all_extracted and all_extracted['faq_items']:
        context.faq_items = []
        
        # Group FAQ by category
        faq_by_category = {}
        for faq in all_extracted['faq_items']:
            if faq.category not in faq_by_category:
                faq_by_category[faq.category] = []
            faq_by_category[faq.category].append({
                'question': faq.question,
                'answer': faq.answer
            })
        
        # Convert to list format
        for category, items in faq_by_category.items():
            for item in items:
                item['category'] = category
                context.faq_items.append(item)
        
        logger.info(f"Phase 9: Transformed {len(context.faq_items)} FAQ items across {len(faq_by_category)} categories")
    
    logger.info(f"Phase 9 complete: {len(context.enhanced_business_rules)} rules, {len(context.use_cases)} use cases, {len(context.faq_items)} FAQs")
    
    # PHASE 10.2: Transform failure modes from raw_data
    logger.info("Phase 10.2: Processing failure modes from extracted data")
    for extracted in extracted_data_list:
        for fm_data in extracted.raw_data.get('failure_modes', []):
            fm_context = {
                'exception_type': fm_data.get('exception_type', 'Unknown'),
                'operation': fm_data.get('operation', 'Unknown operation'),
                'trigger': fm_data.get('trigger', 'Unspecified trigger'),
                'impact': fm_data.get('impact', 'Service unavailability'),
                'mitigation': fm_data.get('mitigation', 'Log and retry'),
                'is_expected': fm_data.get('is_expected', False),
                'source': fm_data.get('source', 'Code analysis'),
            }
            context.failure_modes.append(fm_context)
    
    if context.failure_modes:
        logger.info(f"Phase 10.2: Extracted {len(context.failure_modes)} failure modes")
        # Group by exception type for better documentation
        by_exception = {}
        for fm in context.failure_modes:
            exc_type = fm['exception_type']
            if exc_type not in by_exception:
                by_exception[exc_type] = []
            by_exception[exc_type].append(fm)
        logger.info(f"Phase 10.2: Grouped into {len(by_exception)} exception types: {list(by_exception.keys())}")
    
    # Transform validation rules
    context.validation_rules = [
        ValidationRuleContext(
            property=val.field_name,
            rule_type=val.rule_type,
            error_message=val.error_message or f"Validation failed: {val.rule_type}",
            code_location="<source>",
            rule_value=val.rule_value
        )
        for val in all_extracted['validations']
    ]
    
    # Transform business rules
    context.business_rules = [
        BusinessRuleContext(
            title=br.rule_id or f"Rule {i+1}",
            description=br.description,
            enforcement_point="Service logic" if br.source_type == "validation" else "Code documentation",
            impact_level="High",
            related_code=br.code_location
        )
        for i, br in enumerate(all_extracted['business_rules'])
    ]
    
    # Transform data operations
    for data_op in all_extracted['data_operations']:
        op_context = DataOperationContext(
            operation_type=data_op.operation_type,
            table_name=data_op.target_table or "Unknown",
            method_name=data_op.method_name,
            fields_touched=data_op.target_columns
        )
        
        if data_op.operation_type == 'READ':
            context.data_reads.append(op_context)
        else:
            context.data_writes.append(op_context)
    
    # Transform methods
    context.all_methods = [
        MethodContext(
            name=method.name,
            return_type=method.return_type,
            is_async=method.is_async,
            is_public=method.is_public,
            summary=method.description,
            parameters=[{'name': p.name, 'type': p.type} for p in method.parameters],
            decorators=method.decorators,
            line_number=method.line_number
        )
        for method in all_extracted['methods']
    ]
    
    # Set primary method (first public method)
    if context.all_methods:
        # PHASE 10: Prioritize operations: Create > Read > Update > Delete
        context.primary_method = _select_primary_operation(context.all_methods)
    
    # Track source files
    context.source_files = [ed.file_path for ed in extracted_data_list]
    
    logger.info(
        f"Built ServiceTemplateContext: {service_name} with "
        f"{len(context.endpoints)} endpoints, "
        f"{len(context.dependencies)} dependencies, "
        f"{len(context.validation_rules)} validations"
    )
    
    return context


def build_component_context(
    component_name: str,
    extracted_data_list: List[ExtractedData]
) -> ComponentTemplateContext:
    """
    Transform extracted TypeScript/React data into ComponentTemplateContext.
    
    Args:
        component_name: Name of the component
        extracted_data_list: List of ExtractedData from TypeScript files
        
    Returns:
        ComponentTemplateContext ready for Jinja2 rendering
    """
    context = ComponentTemplateContext(component_name=component_name)
    
    # Collect data from all extracted sources
    all_extracted = _aggregate_extracted_data(extracted_data_list)
    
    # Usually one component per file
    if all_extracted['components']:
        component = all_extracted['components'][0]
        
        # Transform props
        context.props = [
            PropContext(
                name=prop.name,
                type=prop.type,
                required=prop.is_required,
                default=prop.default_value,
                description=prop.description or ""
            )
            for prop in component.props
        ]
        
        # Transform state variables
        context.state_vars = [
            StateContext(
                name=state.get('name', 'unknown'),
                type=state.get('type', 'unknown'),
                initial_value=state.get('initial_value'),
                purpose=state.get('description', '')
            )
            for state in component.state_variables
        ]
        
        # Transform event handlers
        context.events = [
            EventContext(
                name=handler,
                handler_type="click|change|submit",
                triggered_when="User interaction"
            )
            for handler in component.event_handlers
        ]
        
        # Set child components
        context.children_components = component.child_components
    
    # Track source files
    context.file_path = extracted_data_list[0].file_path if extracted_data_list else None
    
    logger.info(
        f"Built ComponentTemplateContext: {component_name} with "
        f"{len(context.props)} props, "
        f"{len(context.state_vars)} state variables, "
        f"{len(context.events)} events"
    )
    
    return context


def build_table_context(
    table_name: str,
    extracted_data_list: List[ExtractedData],
    schema_name: Optional[str] = None
) -> TableTemplateContext:
    """
    Transform extracted SQL data into TableTemplateContext.
    
    Args:
        table_name: Name of the table
        extracted_data_list: List of ExtractedData from SQL files
        schema_name: Optional schema name (e.g., 'dbo')
        
    Returns:
        TableTemplateContext ready for Jinja2 rendering
    """
    context = TableTemplateContext(
        table_name=table_name,
        schema_name=schema_name
    )
    
    # Collect data from all extracted sources
    all_extracted = _aggregate_extracted_data(extracted_data_list)
    
    # Usually one table per file
    if all_extracted['tables']:
        table = all_extracted['tables'][0]
        
        # Transform columns
        context.columns = [
            ColumnContext(
                name=col.name,
                type=col.data_type,
                nullable=col.is_nullable,
                default=col.default_value,
                description=col.description or "",
                is_primary_key=col.is_primary_key,
                is_foreign_key=col.is_foreign_key,
                constraints=col.constraints
            )
            for col in table.columns
        ]
        
        # Transform constraints (from the constraint list)
        context.check_constraints = [
            ConstraintContext(
                name=f"CHECK_{idx}",
                constraint_type="CHECK",
                sql_expression=constraint
            )
            for idx, constraint in enumerate(table.constraints)
            if "CHECK" in constraint.upper()
        ]
        
        # Extract foreign keys from columns
        context.foreign_keys = [
            ForeignKeyContext(
                column=col.name,
                referenced_table=col.foreign_key_table or "",
                referenced_column=col.foreign_key_column or ""
            )
            for col in table.columns
            if col.is_foreign_key
        ]
    
    # Track source files
    context.related_tables = []
    context.referenced_by = []
    
    logger.info(
        f"Built TableTemplateContext: {table_name} with "
        f"{len(context.columns)} columns, "
        f"{len(context.foreign_keys)} foreign keys, "
        f"{len(context.check_constraints)} constraints"
    )
    
    return context


def _aggregate_extracted_data(extracted_data_list: List[ExtractedData]) -> Dict[str, List]:
    """
    Aggregate all extracted data from multiple files.
    
    Args:
        extracted_data_list: List of ExtractedData objects
        
    Returns:
        Dictionary with aggregated lists of each data type
    """
    aggregated = {
        'classes': [],
        'methods': [],
        'routes': [],
        'validations': [],
        'dependencies': [],
        'business_rules': [],
        'data_operations': [],
        'tables': [],
        'components': [],
        'dtos': [],  # PHASE 7: DTO aggregation
        'operation_flows': [],  # PHASE 8: Operation flow diagrams
        'use_cases': [],  # PHASE 9: Use cases
        'faq_items': [],  # PHASE 9: FAQ items
        'enhanced_business_rules': [],  # PHASE 9: Enhanced business rules
    }
    
    for extracted in extracted_data_list:
        aggregated['classes'].extend(extracted.classes)
        aggregated['methods'].extend(extracted.methods)
        aggregated['routes'].extend(extracted.routes)
        aggregated['validations'].extend(extracted.validations)
        aggregated['dependencies'].extend(extracted.dependencies)
        aggregated['business_rules'].extend(extracted.business_rules)
        aggregated['data_operations'].extend(extracted.data_operations)
        aggregated['tables'].extend(extracted.tables)
        aggregated['components'].extend(extracted.components)
        aggregated['dtos'].extend(extracted.dtos)  # PHASE 7: Aggregate DTOs from all files
        aggregated['operation_flows'].extend(extracted.operation_flows)  # PHASE 8: Aggregate flows
        aggregated['use_cases'].extend(extracted.use_cases)  # PHASE 9: Aggregate use cases
        aggregated['faq_items'].extend(extracted.faq_items)  # PHASE 9: Aggregate FAQ items
        aggregated['enhanced_business_rules'].extend(extracted.enhanced_business_rules)  # PHASE 9
    
    return aggregated


def _extract_actual_service_name(extracted_data_list: List[ExtractedData], fallback: str) -> str:
    """
    Extract the actual service name from source files.
    Prioritizes interface files (IServiceName.cs) over controller files.
    
    Args:
        extracted_data_list: List of ExtractedData objects
        fallback: Fallback service name if extraction fails
        
    Returns:
        Extracted service name or fallback
    """
    # Priority 1: Interface files (IServiceName.cs)
    for data in extracted_data_list:
        if data.file_path:
            # Handle both string and Path objects
            file_path_str = str(data.file_path)
            if 'IService' in file_path_str:
                # Extract class name from interface file
                for cls in data.classes:
                    if cls.name.startswith('I') and 'Service' in cls.name:
                        # Remove 'I' prefix: IEnrollmentService -> EnrollmentService
                        return cls.name[1:] if cls.name.startswith('I') else cls.name
    
    # Priority 2: Service implementation files (ServiceName.cs)
    for data in extracted_data_list:
        if data.file_path:
            file_path_str = str(data.file_path)
            if 'Service' in file_path_str and 'Controller' not in file_path_str:
                for cls in data.classes:
                    if 'Service' in cls.name and not cls.name.startswith('I'):
                        return cls.name
    
    # Priority 3: First class with 'Service' in name
    for data in extracted_data_list:
        for cls in data.classes:
            if 'Service' in cls.name:
                return cls.name[1:] if cls.name.startswith('I') else cls.name
    
    # Priority 4: Use fallback (user-provided module name)
    return fallback


def _extract_namespace(extracted_data_list: List[ExtractedData]) -> Optional[str]:
    """
    Extract the C# namespace from source files.
    
    Args:
        extracted_data_list: List of ExtractedData objects
        
    Returns:
        Namespace string or None
    """
    for data in extracted_data_list:
        # Try to extract namespace from raw_data if available
        if hasattr(data, 'raw_data') and isinstance(data.raw_data, dict):
            if 'namespace' in data.raw_data:
                return data.raw_data['namespace']
    
    # Namespace extraction not implemented yet - return None
    return None


def _select_primary_operation(methods: List[MethodContext]) -> MethodContext:
    """
    Select the primary operation from a list of methods.
    Prioritizes: Create > Read > Update > Delete, and Async over sync.
    
    Args:
        methods: List of MethodContext objects
        
    Returns:
        Primary MethodContext
    """
    # Define operation priority (higher number = higher priority)
    operation_priority = {
        'create': 4,
        'add': 4,
        'insert': 4,
        'post': 4,
        'get': 3,
        'read': 3,
        'list': 3,
        'retrieve': 3,
        'update': 2,
        'put': 2,
        'patch': 2,
        'modify': 2,
        'delete': 1,
        'remove': 1,
        'destroy': 1
    }
    
    def score_method(method: MethodContext) -> int:
        """Calculate priority score for a method."""
        score = 0
        method_name_lower = method.name.lower()
        
        # Check for operation keywords
        for keyword, priority in operation_priority.items():
            if keyword in method_name_lower:
                score = max(score, priority * 100)
                break
        
        # Bonus for async methods
        if method.is_async:
            score += 10
        
        # Bonus for public methods
        if method.is_public:
            score += 5
        
        # Prefer service methods over controller methods (heuristic: has more params)
        if method.parameters and len(method.parameters) > 1:
            score += 3
        
        return score
    
    # Score all methods and select highest
    scored_methods = [(score_method(m), m) for m in methods]
    scored_methods.sort(reverse=True, key=lambda x: x[0])
    
    return scored_methods[0][1] if scored_methods else methods[0]


# ============================================================================
# DIAGNOSTIC FUNCTIONS FOR PHASE 2 VALIDATION
# ============================================================================

def report_extraction_gaps(
    extracted_data_list: List[ExtractedData],
    project_type: str
) -> Dict[str, Any]:
    """
    Report what data was extracted vs. what we need for templates.
    
    Helps identify gaps that extractors need to fill for each project type.
    
    Args:
        extracted_data_list: List of extracted data
        project_type: 'backend', 'ui', or 'database'
        
    Returns:
        Dictionary with available data, missing data, and recommendations
    """
    aggregated = _aggregate_extracted_data(extracted_data_list)
    
    report = {
        'project_type': project_type,
        'extraction_summary': {
            'classes': len(aggregated['classes']),
            'methods': len(aggregated['methods']),
            'routes': len(aggregated['routes']),
            'validations': len(aggregated['validations']),
            'dependencies': len(aggregated['dependencies']),
            'tables': len(aggregated['tables']),
            'components': len(aggregated['components']),
        },
        'gaps': [],
        'recommendations': []
    }
    
    # Check project-specific gaps
    if project_type == 'backend':
        if not aggregated['routes']:
            report['gaps'].append("No API routes extracted - check if file is a controller")
            report['recommendations'].append(
                "Ensure CSharpExtractor._extract_routes() is finding [HttpGet], [HttpPost], etc."
            )
        
        if not aggregated['dependencies']:
            report['gaps'].append("No dependencies extracted - check constructor injection")
            report['recommendations'].append(
                "Ensure CSharpExtractor._extract_dependencies() parses constructors correctly"
            )
        
        if not aggregated['validations']:
            report['gaps'].append(
                "No validation rules extracted - FluentValidation may not be recognized"
            )
            report['recommendations'].append(
                "Add validation rule extraction for FluentValidation syntax"
            )
    
    elif project_type == 'ui':
        if not aggregated['components']:
            report['gaps'].append("No components extracted - check if file exports a React component")
            report['recommendations'].append(
                "Ensure TypeScriptExtractor recognizes export default or export const patterns"
            )
        
        if aggregated['components'] and not aggregated['components'][0].props:
            report['gaps'].append("Props not extracted - check PropTypes or TypeScript interface")
            report['recommendations'].append(
                "Ensure TypeScriptExtractor._extract_props() parses interface/type definitions"
            )
    
    elif project_type == 'database':
        if not aggregated['tables']:
            report['gaps'].append("No tables extracted - check SQL syntax")
            report['recommendations'].append(
                "Ensure SQLExtractor._extract_tables() parses CREATE TABLE statements"
            )
        
        if aggregated['tables'] and not aggregated['tables'][0].columns:
            report['gaps'].append("Columns not extracted from table definition")
            report['recommendations'].append(
                "Ensure SQLExtractor._extract_columns() parses column definitions"
            )
    
    return report
