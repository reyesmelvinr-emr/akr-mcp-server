"""
C# code extractor for analyzing .NET source files.

Extracts classes, methods, API routes, validation rules, and dependencies
from C# source files (controllers, services, validators).
"""

import re
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base_extractor import (
    BaseExtractor, ExtractedData, ExtractedClass, ExtractedMethod,
    ExtractedParameter, ExtractedRoute, ExtractedValidation, ExtractedDependency,
    ExtractedBusinessRule, ExtractedDataOperation
)
from .dto_extractor import DTOExtractor


logger = logging.getLogger(__name__)


class CSharpExtractor(BaseExtractor):
    """Extractor for C# source code."""
    
    def can_extract(self, file_path: Path) -> bool:
        """Check if file is a C# source file."""
        return file_path.suffix.lower() in ['.cs']
    
    def extract(self, file_path: Path) -> ExtractedData:
        """Extract information from C# source file."""
        logger.info(f"Extracting C# data from {file_path}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"Failed to read file: {e}")
        
        # Initialize extracted data
        data = ExtractedData(language='csharp', file_path=str(file_path))
        
        try:
            # PHASE 10.2: Extract namespace from file
            namespace = self._extract_namespace(content)
            if namespace:
                data.raw_data['namespace'] = namespace
                logger.info(f"PHASE 10.2: Extracted namespace: {namespace}")
            
            # Extract classes
            data.classes = self._extract_classes(content)
            
            # Extract methods from classes
            for cls in data.classes:
                data.methods.extend(cls.methods)
            
            # Extract DTOs (request/response models)
            dto_extractor = DTOExtractor()
            data.dtos = dto_extractor.extract_dtos(content, str(file_path))
            
            # PHASE 10.2: Store DTO names in raw_data for context_builder lookup
            if data.dtos:
                data.raw_data['dto_names'] = [dto.name for dto in data.dtos]
                logger.info(f"PHASE 10.2: Stored {len(data.dtos)} DTO names for example extraction")
            
            # PHASE 8: Extract operation flows from method bodies
            from .method_flow_analyzer import MethodFlowAnalyzer
            flow_analyzer = MethodFlowAnalyzer()
            data.operation_flows = flow_analyzer.extract_flows(content, str(file_path))
            
            # PHASE 9: Extract enhanced business rules, use cases, and FAQ
            from .business_rule_extractor import BusinessRuleExtractor
            biz_rule_extractor = BusinessRuleExtractor()
            data.enhanced_business_rules = biz_rule_extractor.extract_business_rules(content, str(file_path))
            data.use_cases = biz_rule_extractor.extract_use_cases(content, str(file_path))
            data.faq_items = biz_rule_extractor.extract_faq_items(content, str(file_path))
            
            # Extract API routes (if controller)
            data.routes = self._extract_routes(content, data.classes)
            
            # Extract validation rules (if validator)
            data.validations = self._extract_validations(content)
            
            # Extract dependencies from constructors
            data.dependencies = self._extract_dependencies(content, data.classes)
            
            # Extract business rules from code patterns
            data.business_rules = self._extract_business_rules(content, data.validations)
            
            # Extract data operations (reads, writes)
            data.data_operations = self._extract_data_operations(content, data.methods)
            
            # PHASE 10.2: Extract failure modes from exception handling
            failure_mode_extractor = None
            try:
                from .failure_mode_extractor import FailureModeExtractor
                failure_mode_extractor = FailureModeExtractor()
                failure_modes = failure_mode_extractor.extract_failure_modes_from_content(
                    content, 
                    [m.name for m in data.methods]
                )
                
                # Store failure modes in raw_data for context builder
                if failure_modes:
                    data.raw_data['failure_modes'] = [
                        {
                            'exception_type': fm.exception_type,
                            'operation': fm.operation,
                            'trigger': fm.trigger,
                            'impact': fm.impact,
                            'mitigation': fm.mitigation,
                            'is_expected': fm.is_expected
                        }
                        for fm in failure_modes
                    ]
                    logger.info(f"PHASE 10.2: Extracted {len(failure_modes)} failure modes")
            except ImportError:
                logger.debug("Failure mode extractor not available")
            
        except Exception as e:
            data.extraction_errors.append(f"Extraction error: {str(e)}")
            logger.error(f"Error extracting from {file_path}: {e}", exc_info=True)
        
        return data
    
    def _extract_namespace(self, content: str) -> Optional[str]:
        """Extract namespace from C# code.
        
        Pattern: namespace X.Y.Z; or namespace X.Y.Z {}
        """
        namespace_pattern = r'^\s*namespace\s+([\w\.]+)\s*[;{]'
        match = re.search(namespace_pattern, content, re.MULTILINE)
        if match:
            return match.group(1)
        return None
    
    def _extract_classes(self, content: str) -> List[ExtractedClass]:
        """Extract class declarations from C# code."""
        classes = []
        
        # Pattern: public class ClassName : BaseClass, IInterface
        class_pattern = r'public\s+(?:sealed\s+)?(?:abstract\s+)?class\s+(\w+)\s*(?::\s*([^\{]+))?'
        
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            inheritance = match.group(2)
            
            base_classes = []
            if inheritance:
                # Parse base classes and interfaces
                base_classes = [b.strip() for b in inheritance.split(',')]
            
            # Find class body
            class_start = match.end()
            class_body = self._extract_block(content, class_start)
            
            # Extract methods from class body
            methods = self._extract_methods(class_body)
            
            cls = ExtractedClass(
                name=class_name,
                base_classes=base_classes,
                methods=methods,
                line_number=content[:match.start()].count('\n') + 1
            )
            classes.append(cls)
            
            logger.debug(f"Extracted class: {class_name} with {len(methods)} methods")
        
        return classes
    
    def _extract_methods(self, class_body: str) -> List[ExtractedMethod]:
        """Extract method declarations from class body."""
        methods = []
        
        # PHASE 10.2 FIX: Improved pattern to handle complex generic return types
        # Pattern: public async Task<ReturnType> MethodName(params)
        # Matches complex types like: ActionResult<PagedResponse<CourseSummaryDto>>
        method_pattern = r'(public|private|protected|internal)\s+(?:(async|static)\s+)*(?:((?:[\w\.]+\s+)*(?:[\w<>,\s\.]*?)[\w>]+)\s+)?(\w+)\s*\(([^\)]*)\)'
        
        for match in re.finditer(method_pattern, class_body):
            visibility = match.group(1)
            modifiers = match.group(2) or ''
            return_type = (match.group(3) or '').strip() if match.group(3) else None
            method_name = match.group(4)
            params_str = match.group(5)
            
            # Skip constructors, properties, and common non-method patterns
            if not return_type or return_type in ['if', 'for', 'while', 'switch']:
                continue
            
            # Skip if method name looks like a variable or property
            if method_name in ['get', 'set']:
                continue
            
            # Extract attributes above method
            method_start = match.start()
            attributes = self._extract_attributes_before_position(class_body, method_start)
            
            # Parse parameters
            parameters = self._parse_parameters(params_str)
            
            method = ExtractedMethod(
                name=method_name,
                parameters=parameters,
                return_type=return_type,
                is_async='async' in modifiers,
                is_public=visibility == 'public',
                attributes=attributes,
                line_number=class_body[:match.start()].count('\n') + 1
            )
            methods.append(method)
            
            logger.debug(f"PHASE 10.2: Extracted method: {method_name} (return: {return_type}) with {len(parameters)} parameters and {len(attributes)} attributes")
        
        return methods
    
    def _parse_parameters(self, params_str: str) -> List[ExtractedParameter]:
        """Parse method parameter string."""
        if not params_str.strip():
            return []
        
        parameters = []
        
        # Split by comma (handling generic types)
        param_parts = self._smart_split(params_str, ',')
        
        for param in param_parts:
            param = param.strip()
            if not param:
                continue
            
            # Pattern: [FromBody] Type paramName = default
            # Remove attributes
            param = re.sub(r'\[[\w\(\)]+\]', '', param).strip()
            
            # Check for default value
            default_value = None
            if '=' in param:
                param, default_value = param.split('=', 1)
                param = param.strip()
                default_value = default_value.strip()
            
            # Split type and name
            parts = param.rsplit(None, 1)
            if len(parts) == 2:
                param_type, param_name = parts
                
                # Check if optional (nullable type)
                is_optional = '?' in param_type or default_value is not None
                
                parameters.append(ExtractedParameter(
                    name=param_name,
                    type=param_type,
                    default_value=default_value,
                    is_optional=is_optional
                ))
        
        return parameters
    
    def _extract_routes(self, content: str, classes: List[ExtractedClass]) -> List[ExtractedRoute]:
        """Extract API routes from controllers."""
        routes = []
        
        # Check if this is a controller
        is_controller = re.search(r':\s*\w*Controller', content)
        if not is_controller:
            logger.debug(f"PHASE 10.2: File is not a controller (no : *Controller inheritance)")
            return routes
        
        # Extract controller-level route
        controller_route = ""
        route_attr = re.search(r'\[Route\(["\']([^"\']+)["\']\)\]', content)
        if route_attr:
            controller_route = route_attr.group(1)
        
        logger.info(f"PHASE 10.2: Found controller with route: {controller_route or '[default]'}")
        
        # Extract method-level routes
        http_methods = ['HttpGet', 'HttpPost', 'HttpPut', 'HttpDelete', 'HttpPatch']
        
        for cls in classes:
            logger.debug(f"PHASE 10.2: Processing class {cls.name} with {len(cls.methods)} methods")
            for method in cls.methods:
                # Find HTTP method attributes
                found_http_attr = False
                for http_method in http_methods:
                    for attr in method.attributes:
                        if http_method in attr:
                            found_http_attr = True
                            logger.debug(f"PHASE 10.2: Found {http_method} on method {method.name}")
                            
                            # Extract route template from attribute
                            route_template = ""
                            route_match = re.search(r'\(["\']([^"\']+)["\']\)', attr)
                            if route_match:
                                route_template = route_match.group(1)
                            
                            # Combine controller and method routes
                            full_path = controller_route
                            if route_template:
                                full_path += '/' + route_template if not route_template.startswith('/') else route_template
                            
                            full_path = full_path.strip('/')
                            if full_path:
                                full_path = '/' + full_path
                            
                            # Extract response types
                            response_types = []
                            for attr2 in method.attributes:
                                if 'ProducesResponseType' in attr2:
                                    type_match = re.search(r'typeof\(([^)]+)\)', attr2)
                                    if type_match:
                                        response_types.append(type_match.group(1))
                            
                            # Extract status codes
                            status_codes = []
                            for attr2 in method.attributes:
                                if 'ProducesResponseType' in attr2:
                                    status_match = re.search(r'StatusCodes\.(\w+)|(\d{3})', attr2)
                                    if status_match:
                                        status = status_match.group(1) or status_match.group(2)
                                        if status.isdigit():
                                            status_codes.append(int(status))
                            
                            route = ExtractedRoute(
                                method=http_method.replace('Http', '').upper(),
                                path=full_path,
                                handler_name=method.name,
                                parameters=method.parameters,
                                response_types=response_types,
                                status_codes=status_codes
                            )
                            routes.append(route)
                            
                            logger.info(f"PHASE 10.2: Extracted route: {route.method} {route.path}")
                
                if not found_http_attr and method.name and method.visibility == 'public':
                    logger.debug(f"PHASE 10.2: Public method {method.name} has no HTTP attributes; attributes: {method.attributes}")
        
        logger.info(f"PHASE 10.2: Extracted {len(routes)} routes total from controller")
        return routes
    
    def _extract_validations(self, content: str) -> List[ExtractedValidation]:
        """Extract FluentValidation rules."""
        validations = []
        
        # Check if this is a validator
        if 'AbstractValidator' not in content:
            return validations
        
        # Pattern: RuleFor(x => x.PropertyName).RuleType(value).WithMessage("message")
        rule_pattern = r'RuleFor\([^)]+\.(\w+)\)\.(\w+)\(([^)]*)\)(?:\.WithMessage\(["\']([^"\']+)["\']\))?'
        
        for match in re.finditer(rule_pattern, content):
            field_name = match.group(1)
            rule_type = match.group(2)
            rule_value = match.group(3).strip() if match.group(3) else None
            error_message = match.group(4)
            
            # Clean up rule value
            if rule_value:
                rule_value = rule_value.strip('"\'')
            
            validation = ExtractedValidation(
                field_name=field_name,
                rule_type=rule_type,
                rule_value=rule_value,
                error_message=error_message
            )
            validations.append(validation)
            
            logger.debug(f"Extracted validation: {field_name}.{rule_type}")
        
        return validations
    
    def _extract_dependencies(self, content: str, classes: List[ExtractedClass]) -> List[ExtractedDependency]:
        """Extract constructor dependencies (dependency injection)."""
        dependencies = []
        
        for cls in classes:
            # Find constructor
            constructor_pattern = rf'public\s+{cls.name}\s*\(([^\)]+)\)'
            constructor_match = re.search(constructor_pattern, content)
            
            if constructor_match:
                params_str = constructor_match.group(1)
                params = self._parse_parameters(params_str)
                
                for param in params:
                    dep = ExtractedDependency(
                        name=param.name,
                        type=param.type or 'unknown'
                    )
                    dependencies.append(dep)
                    
                    logger.debug(f"Extracted dependency: {param.name} ({param.type})")
        
        return dependencies
    
    def _extract_attributes_before_position(self, content: str, position: int) -> List[str]:
        """Extract [Attribute] declarations before a given position."""
        attributes = []
        
        # Look backwards for attributes - check more lines (up to 50)
        before_content = content[:position]
        lines = before_content.split('\n')
        
        # PHASE 10.2 FIX: Extended search from 10 lines to 50 lines to catch all attributes
        # Scan backwards from the position - look at more context
        attr_end_idx = len(lines) - 1
        seen_non_attr = False
        
        for idx in range(len(lines) - 1, max(0, len(lines) - 50), -1):
            line = lines[idx].strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('//'):
                continue
            
            # Collect attribute lines
            if line.startswith('[') and (line.endswith(']') or line.endswith(',') or not '(' in line or ')' in line):
                attributes.insert(0, line)
            elif line.startswith('['):
                # Multi-line attribute - collect it
                attributes.insert(0, line)
            elif line and not seen_non_attr:
                # First non-attribute line - stop searching
                seen_non_attr = True
                # But continue a bit more to catch closing brackets
                if ']' not in line:
                    break
        
        logger.debug(f"PHASE 10.2: Extracted {len(attributes)} attributes before position {position}: {attributes}")
        return attributes
    
    def _extract_block(self, content: str, start_pos: int) -> str:
        """Extract a code block starting from position (matching braces)."""
        brace_count = 0
        in_block = False
        block_start = -1
        
        for i in range(start_pos, len(content)):
            char = content[i]
            
            if char == '{':
                if not in_block:
                    in_block = True
                    block_start = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and in_block:
                    return content[block_start:i+1]
        
        return ""
    
    def _smart_split(self, text: str, delimiter: str) -> List[str]:
        """Split text by delimiter, respecting nested brackets/generics."""
        parts = []
        current = []
        depth = 0
        
        for char in text:
            if char in '<([':
                depth += 1
            elif char in '>)]':
                depth -= 1
            
            if char == delimiter and depth == 0:
                parts.append(''.join(current))
                current = []
            else:
                current.append(char)
        
        if current:
            parts.append(''.join(current))
        
        return parts
    
    def _extract_business_rules(self, content: str, validations: List[ExtractedValidation]) -> List[ExtractedBusinessRule]:
        """
        Extract business rules from code patterns.
        
        Business rules are inferred from:
        1. Validation rule chains and their error messages
        2. Conditional logic checks for business constraints
        3. Comments documenting business rules
        """
        rules = []
        
        # Pattern 1: BR-*** markers in comments
        br_pattern = r'//\s*(BR-\w+)\s*:\s*(.+?)\n'
        for match in re.finditer(br_pattern, content):
            rule_id = match.group(1)
            description = match.group(2).strip()
            
            # Find which validations enforce this rule
            affected_validations = [
                v.field_name for v in validations 
                if rule_id.lower() in v.error_message.lower() if v.error_message
            ]
            
            rule = ExtractedBusinessRule(
                rule_id=rule_id,
                description=description,
                affected_validations=affected_validations,
                source_type="comment",
                code_location=f"Line {content[:match.start()].count(chr(10)) + 1}"
            )
            rules.append(rule)
        
        # Pattern 2: Infer from validation rules
        validation_rule_map = {}
        for val in validations:
            # Group validations by field
            if val.field_name not in validation_rule_map:
                validation_rule_map[val.field_name] = []
            validation_rule_map[val.field_name].append(val)
        
        # Create synthetic rules from validation chains
        for field, vals in validation_rule_map.items():
            # If field has multiple validation rules, create a composite rule
            if len(vals) > 1:
                rule_types = [v.rule_type for v in vals]
                description = f"Validates {field} with: {', '.join(rule_types)}"
                
                rule = ExtractedBusinessRule(
                    rule_id=None,  # Auto-generated rules don't have IDs
                    description=description,
                    affected_validations=[v.field_name for v in vals],
                    source_type="validation"
                )
                rules.append(rule)
        
        logger.debug(f"Extracted {len(rules)} business rules")
        return rules
    
    def _extract_data_operations(self, content: str, methods: List[ExtractedMethod]) -> List[ExtractedDataOperation]:
        """
        Extract data read/write operations from repository calls.
        
        Detects:
        - Repository method calls (CreateAsync, UpdateAsync, DeleteAsync, GetAsync, ListAsync, etc.)
        - SQL-like patterns in LINQ queries
        - Table references and column accesses
        
        PHASE 10.2: Enhanced to infer table names and operation patterns better.
        """
        operations = []
        
        # PHASE 10.2: Improved operation type mappings
        repo_operations = {
            r'\.CreateAsync\(': ('CREATE', 'INSERT'),
            r'\.UpdateAsync\(': ('UPDATE', 'UPDATE'),
            r'\.DeleteAsync\(': ('DELETE', 'DELETE'),
            r'\.GetAsync\(': ('READ', 'SELECT single'),
            r'\.ListAsync\(': ('READ', 'SELECT list'),
            r'\.ExistsByAsync\(': ('READ', 'SELECT count'),
            r'\.FindAsync\(': ('READ', 'SELECT single'),
            r'\.ToListAsync\(': ('READ', 'SELECT list'),
            r'\.FirstOrDefaultAsync\(': ('READ', 'SELECT single'),
            r'\.AnyAsync\(': ('READ', 'SELECT count'),
            r'\.CountAsync\(': ('READ', 'SELECT count'),
        }
        
        for method in methods:
            # PHASE 10.2: Better operation type detection from method name
            op_type = None
            pattern = None
            table_name = None
            performance_notes = None
            
            method_name_lower = method.name.lower()
            
            # Infer operation type from method name
            if 'create' in method_name_lower or 'add' in method_name_lower:
                op_type = 'CREATE'
                pattern = 'INSERT with validation'
                performance_notes = 'Single INSERT; check for batch alternatives'
                
            elif 'update' in method_name_lower:
                op_type = 'UPDATE'
                pattern = 'UPDATE by primary key'
                performance_notes = 'WHERE by ID; consider indexed lookup'
                
            elif 'delete' in method_name_lower or 'remove' in method_name_lower:
                op_type = 'DELETE'
                # PHASE 10.2: Smarter DELETE pattern detection
                if 'byid' in method_name_lower or 'by_id' in method_name_lower:
                    pattern = 'DELETE by ID (physical delete)'
                    performance_notes = 'Single row DELETE; index on ID crucial'
                elif 'bulk' in method_name_lower or 'many' in method_name_lower:
                    pattern = 'DELETE multiple rows (filtered)'
                    performance_notes = 'Bulk DELETE; use transaction; check WHERE clause'
                else:
                    pattern = 'DELETE by ID'
                    performance_notes = 'Single DELETE; ensure ID indexed'
                
            elif 'get' in method_name_lower or 'find' in method_name_lower or 'fetch' in method_name_lower:
                op_type = 'READ'
                # PHASE 10.2: Smarter GET pattern detection
                if 'byid' in method_name_lower or 'getbyid' in method_name_lower or 'getone' in method_name_lower:
                    pattern = 'SELECT single by primary key'
                    performance_notes = 'Indexed lookup; consider SELECT specific columns'
                elif method.name.startswith('Get') and method.parameters and len(method.parameters) == 1:
                    pattern = 'Single row lookup'
                    performance_notes = 'Verify index on lookup column'
                else:
                    pattern = 'Single row fetch'
                    performance_notes = 'Check for N+1 problem'
                
            elif 'list' in method_name_lower or 'getall' in method_name_lower or 'search' in method_name_lower:
                op_type = 'READ'
                # PHASE 10.2: Smarter LIST pattern detection
                if 'paged' in method_name_lower or 'pagination' in method_name_lower or \
                   ('page' in method_name_lower and 'size' in method_name_lower):
                    pattern = 'Paginated query with OFFSET/FETCH'
                    performance_notes = 'Use OFFSET/FETCH for large datasets; add covering index'
                elif 'search' in method_name_lower or 'filter' in method_name_lower:
                    pattern = 'Filtered list query'
                    performance_notes = 'Ensure indexes on filter columns'
                else:
                    pattern = 'Full table list (possibly filtered)'
                    performance_notes = 'Consider pagination to avoid large result sets'
                
            elif 'exists' in method_name_lower or 'has' in method_name_lower or 'contains' in method_name_lower or 'any' in method_name_lower:
                op_type = 'READ'
                pattern = 'Existence check (COUNT or ANY)'
                performance_notes = 'Use EXISTS/ANY instead of COUNT(*) > 0 for efficiency'
                
            elif 'count' in method_name_lower:
                op_type = 'READ'
                pattern = 'Row count query'
                performance_notes = 'Filter before counting for large tables'
                
            else:
                # Unknown operation
                continue
            
            # PHASE 10.2: Improved table name inference from multiple sources
            table_name = self._infer_table_name(method, content)
            
            if op_type and table_name:
                operation = ExtractedDataOperation(
                    operation_type=op_type,
                    method_name=method.name,
                    target_table=table_name,
                    query_pattern=pattern,
                    performance_notes=performance_notes
                )
                operations.append(operation)
                
                logger.info(f"PHASE 10.2: Extracted data operation: {method.name} → {op_type} on {table_name}")
        
        return operations
    
    def _infer_table_name(self, method: ExtractedMethod, content: str) -> Optional[str]:
        """PHASE 10.2: Infer database table name from method signature and context.
        
        Uses multiple heuristics:
        1. Method parameter types (e.g., Course, CourseDetailDto → Courses table)
        2. Return types
        3. Method name keywords
        4. Generic type parameters
        """
        inferred_names = set()
        
        # Check method parameters for entity types
        for param in method.parameters:
            param_type_lower = (param.type or '').lower()
            
            # Match common entity naming patterns
            if 'course' in param_type_lower:
                inferred_names.add('Courses')
            elif 'enrollment' in param_type_lower:
                inferred_names.add('Enrollments')
            elif 'user' in param_type_lower:
                inferred_names.add('Users')
            elif 'trainin' in param_type_lower:  # Training
                inferred_names.add('Trainings')
        
        # Check method name for entity keywords
        method_name_lower = method.name.lower()
        if 'course' in method_name_lower:
            inferred_names.add('Courses')
        elif 'enrollment' in method_name_lower:
            inferred_names.add('Enrollments')
        elif 'user' in method_name_lower:
            inferred_names.add('Users')
        
        # Check return type
        if method.return_type:
            return_type_lower = method.return_type.lower()
            if 'course' in return_type_lower:
                inferred_names.add('Courses')
            elif 'enrollment' in return_type_lower:
                inferred_names.add('Enrollments')
            elif 'user' in return_type_lower:
                inferred_names.add('Users')
        
        # Return first inferred table (or best guess)
        if inferred_names:
            # Prefer singular/plural consistency with actual schema
            for table in ['Courses', 'Enrollments', 'Users', 'Trainings']:
                if table in inferred_names:
                    return f'training.{table}'
            
            # Fallback: return first inferred
            return f'training.{list(inferred_names)[0]}'
        
        return None

