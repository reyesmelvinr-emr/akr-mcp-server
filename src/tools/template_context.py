"""
Template context models for Jinja2 rendering.

Defines data classes that represent the structured context passed to Jinja2
templates during rendering. These classes serve as the bridge between extracted
code data and template variables.

Classes:
    - EndpointContext: API endpoint information
    - DependencyContext: Dependency injection information
    - ValidationRuleContext: Validation rules from validators
    - MethodContext: Detailed method information
    - BusinessRuleContext: Business logic constraints
    - DataOperationContext: Data read/write patterns
    - ServiceTemplateContext: Complete service documentation context
    
    - PropContext: React/UI component prop
    - EventContext: Component event handlers
    - StateContext: Component state variables
    - VariantContext: Component style variants
    - ComponentTemplateContext: Complete component documentation context
    
    - ColumnContext: Database column information
    - ConstraintContext: Database constraint information
    - ForeignKeyContext: Foreign key relationship
    - TableTemplateContext: Complete table documentation context
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============================================================================
# SERVICE/BACKEND CONTEXT MODELS
# ============================================================================

@dataclass
class EndpointContext:
    """Represents an API endpoint."""
    method: str  # GET, POST, PUT, DELETE
    path: str  # /api/users/{id}
    handler: str  # GetUserById
    summary: str  # "Retrieve user by ID"
    requires_auth: bool = False
    status_codes: List[int] = field(default_factory=list)
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    response_types: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class DependencyContext:
    """Represents a dependency injection or import."""
    name: str  # e.g., "IUserRepository"
    type: str  # Type name
    purpose: str  # What it's used for
    code_location: str  # Full path and line number
    is_critical: bool = False
    namespace: Optional[str] = None
    failure_impact: Optional[str] = None  # PHASE 10.2: Possible failure modes


@dataclass
class ValidationRuleContext:
    """Represents a validation rule."""
    property: str  # e.g., "Email"
    rule_type: str  # NotEmpty, MaxLength, Pattern
    error_message: str
    code_location: str
    rule_value: Optional[str] = None


@dataclass
class MethodContext:
    """Represents a detailed method/function."""
    name: str
    return_type: Optional[str] = None
    is_async: bool = False
    is_public: bool = True
    summary: Optional[str] = None
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    line_number: Optional[int] = None


@dataclass
class BusinessRuleContext:
    """Represents a business rule or constraint."""
    title: str
    description: str
    enforcement_point: str  # e.g., "Service logic", "Database constraint"
    impact_level: str  # High, Medium, Low
    related_code: Optional[str] = None


@dataclass
class DataOperationContext:
    """Represents a data read or write operation."""
    operation_type: str  # CREATE, READ, UPDATE, DELETE
    table_name: str
    method_name: str
    filters: List[str] = field(default_factory=list)
    fields_touched: List[str] = field(default_factory=list)


@dataclass
class ServiceTemplateContext:
    """Complete context for service/backend documentation."""
    # Metadata
    service_name: str
    namespace: Optional[str] = None
    domain: Optional[str] = None
    status: str = "Active"
    version: str = "1.0"
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Extracted content
    service_summary: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[DependencyContext] = field(default_factory=list)
    endpoints: List[EndpointContext] = field(default_factory=list)
    validation_rules: List[ValidationRuleContext] = field(default_factory=list)
    business_rules: List[BusinessRuleContext] = field(default_factory=list)
    primary_method: Optional[MethodContext] = None
    all_methods: List[MethodContext] = field(default_factory=list)
    
    # Data access patterns
    data_reads: List[DataOperationContext] = field(default_factory=list)
    data_writes: List[DataOperationContext] = field(default_factory=list)
    
    # PHASE 7: DTO & Request-Response Models
    request_response_examples: Dict[str, Any] = field(default_factory=dict)
    request_response_schemas: Dict[str, Any] = field(default_factory=dict)
    
    # PHASE 8: Operation Flow Diagrams
    operation_flows: List[Dict[str, Any]] = field(default_factory=list)
    
    # PHASE 9: Business Rules, Use Cases, and FAQ
    enhanced_business_rules: List[Dict[str, Any]] = field(default_factory=list)
    use_cases: List[Dict[str, Any]] = field(default_factory=list)
    faq_items: List[Dict[str, Any]] = field(default_factory=list)
    
    # PHASE 10.2: Failure Modes and Exception Handling
    failure_modes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Source files analyzed
    source_files: List[str] = field(default_factory=list)


# ============================================================================
# UI/COMPONENT CONTEXT MODELS
# ============================================================================

@dataclass
class PropContext:
    """Represents a component prop."""
    name: str
    type: str
    required: bool = False
    default: Optional[str] = None
    description: str = ""


@dataclass
class EventContext:
    """Represents a component event."""
    name: str
    handler_type: str
    triggered_when: str
    business_impact: Optional[str] = None
    parameters: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class StateContext:
    """Represents component state."""
    name: str
    type: str
    initial_value: Optional[str] = None
    purpose: str = ""
    modified_by: List[str] = field(default_factory=list)


@dataclass
class VariantContext:
    """Represents component style variants."""
    name: str
    description: str = ""
    css_classes: List[str] = field(default_factory=list)


@dataclass
class ComponentTemplateContext:
    """Complete context for component documentation."""
    # Metadata
    component_name: str
    file_path: Optional[str] = None
    component_type: str = "Functional"  # Presentational, Container, HOC, etc.
    complexity: str = "Medium"  # Simple, Medium, Complex
    status: str = "Active"
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Extracted content
    props: List[PropContext] = field(default_factory=list)
    events: List[EventContext] = field(default_factory=list)
    state_vars: List[StateContext] = field(default_factory=list)
    variants: List[VariantContext] = field(default_factory=list)
    children_components: List[str] = field(default_factory=list)
    
    # Component details
    purpose: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    accessibility_notes: Optional[str] = None
    performance_notes: Optional[str] = None


# ============================================================================
# DATABASE CONTEXT MODELS
# ============================================================================

@dataclass
class ColumnContext:
    """Represents a database column."""
    name: str
    type: str
    nullable: bool = True
    default: Optional[str] = None
    description: str = ""
    native_type: Optional[str] = None  # SQL Server, PostgreSQL specific
    is_primary_key: bool = False
    is_foreign_key: bool = False
    constraints: List[str] = field(default_factory=list)


@dataclass
class ConstraintContext:
    """Represents a database constraint."""
    name: str
    constraint_type: str  # CHECK, UNIQUE, FK, etc.
    description: str = ""
    sql_expression: Optional[str] = None
    affected_columns: List[str] = field(default_factory=list)


@dataclass
class ForeignKeyContext:
    """Represents a foreign key relationship."""
    column: str
    referenced_schema: Optional[str] = None
    referenced_table: str = ""
    referenced_column: str = ""
    relationship: str = "1:N"  # 1:N, 1:1, N:N
    cascade_delete: bool = False


@dataclass
class TableTemplateContext:
    """Complete context for table documentation."""
    # Metadata
    table_name: str
    schema_name: Optional[str] = None
    status: str = "Active"
    version: str = "1.0"
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Extracted content
    purpose: Optional[str] = None
    columns: List[ColumnContext] = field(default_factory=list)
    check_constraints: List[ConstraintContext] = field(default_factory=list)
    unique_constraints: List[ConstraintContext] = field(default_factory=list)
    foreign_keys: List[ForeignKeyContext] = field(default_factory=list)
    business_rules: List[BusinessRuleContext] = field(default_factory=list)
    
    # Related objects
    related_tables: List[str] = field(default_factory=list)
    referenced_by: List[str] = field(default_factory=list)
    
    # Indexing
    indexes: List[Dict[str, Any]] = field(default_factory=list)


# ============================================================================
# TRANSFORMATION HELPER FUNCTIONS
# ============================================================================

def extracted_data_to_context_errors(extracted_data_list: List) -> Dict[str, List[str]]:
    """
    Collect extraction errors and warnings into a report.
    
    Args:
        extracted_data_list: List of ExtractedData objects
        
    Returns:
        Dictionary with 'errors' and 'warnings' keys containing lists of messages
    """
    errors = []
    warnings = []
    
    for extracted in extracted_data_list:
        errors.extend(extracted.extraction_errors)
        warnings.extend(extracted.extraction_warnings)
    
    return {
        'errors': errors,
        'warnings': warnings
    }
