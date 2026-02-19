"""
Base extractor interface and data models for code analysis.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path


@dataclass
class ExtractedParameter:
    """Represents a method or function parameter."""
    name: str
    type: Optional[str] = None
    default_value: Optional[str] = None
    is_optional: bool = False
    description: Optional[str] = None


@dataclass
class ExtractedMethod:
    """Represents a method or function extracted from source code."""
    name: str
    parameters: List[ExtractedParameter] = field(default_factory=list)
    return_type: Optional[str] = None
    is_async: bool = False
    is_public: bool = True
    decorators: List[str] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)
    description: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class ExtractedClass:
    """Represents a class extracted from source code."""
    name: str
    base_classes: List[str] = field(default_factory=list)
    methods: List[ExtractedMethod] = field(default_factory=list)
    properties: List[Dict[str, Any]] = field(default_factory=list)
    description: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class ExtractedValidation:
    """Represents a validation rule extracted from source code."""
    field_name: str
    rule_type: str  # e.g., "NotEmpty", "MaxLength", "Must", etc.
    rule_value: Optional[str] = None
    error_message: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ExtractedRoute:
    """Represents an API route extracted from source code."""
    method: str  # HTTP method: GET, POST, PUT, DELETE, etc.
    path: str
    handler_name: str
    parameters: List[ExtractedParameter] = field(default_factory=list)
    response_types: List[str] = field(default_factory=list)
    status_codes: List[int] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class ExtractedDependency:
    """Represents a dependency injection or import."""
    name: str
    type: str
    description: Optional[str] = None


@dataclass
class ExtractedBusinessRule:
    """Represents a business rule inferred from code logic."""
    rule_id: Optional[str] = None  # e.g., "BR-CRS-001"
    description: str = ""
    affected_validations: List[str] = field(default_factory=list)  # Validation rule IDs it enforces
    code_location: Optional[str] = None  # File + line number
    source_type: str = "validation"  # "validation", "conditional", "comment"


@dataclass
class ExtractedDataOperation:
    """Represents a data read/write operation (query, INSERT, UPDATE, DELETE)."""
    operation_type: str  # "READ", "CREATE", "UPDATE", "DELETE"
    method_name: str  # Method calling the operation
    target_table: Optional[str] = None
    target_columns: List[str] = field(default_factory=list)
    query_pattern: Optional[str] = None  # "OFFSET/FETCH", "PK lookup", etc.
    performance_notes: Optional[str] = None
    code_location: Optional[str] = None


@dataclass
class ExtractedColumn:
    """Represents a database column extracted from SQL."""
    name: str
    data_type: str
    is_nullable: bool = True
    default_value: Optional[str] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_table: Optional[str] = None
    foreign_key_column: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class ExtractedTable:
    """Represents a database table extracted from SQL."""
    name: str
    schema: Optional[str] = None
    columns: List[ExtractedColumn] = field(default_factory=list)
    indexes: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class ExtractedProp:
    """Represents a React/UI component prop extracted from TypeScript."""
    name: str
    type: str
    is_required: bool = True
    default_value: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ExtractedComponent:
    """Represents a UI component extracted from TypeScript/React."""
    name: str
    props: List[ExtractedProp] = field(default_factory=list)
    state_variables: List[Dict[str, Any]] = field(default_factory=list)
    event_handlers: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)
    child_components: List[str] = field(default_factory=list)
    css_classes: List[str] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class ExtractedData:
    """Aggregated extracted data from source code analysis."""
    language: str
    file_path: str
    classes: List[ExtractedClass] = field(default_factory=list)
    methods: List[ExtractedMethod] = field(default_factory=list)
    routes: List[ExtractedRoute] = field(default_factory=list)
    validations: List[ExtractedValidation] = field(default_factory=list)
    dependencies: List[ExtractedDependency] = field(default_factory=list)
    business_rules: List[ExtractedBusinessRule] = field(default_factory=list)
    data_operations: List[ExtractedDataOperation] = field(default_factory=list)
    dtos: List['ExtractedDTO'] = field(default_factory=list)
    operation_flows: List['OperationFlow'] = field(default_factory=list)  # PHASE 8: Operation flow diagrams
    use_cases: List['UseCase'] = field(default_factory=list)  # PHASE 9: Use cases
    faq_items: List['FAQItem'] = field(default_factory=list)  # PHASE 9: FAQ items
    enhanced_business_rules: List['BusinessRule'] = field(default_factory=list)  # PHASE 9: Enhanced rules
    tables: List[ExtractedTable] = field(default_factory=list)
    components: List[ExtractedComponent] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    extraction_errors: List[str] = field(default_factory=list)
    extraction_warnings: List[str] = field(default_factory=list)


class BaseExtractor(ABC):
    """Base class for language-specific code extractors."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the extractor.
        
        Args:
            config: Optional configuration dictionary with extraction settings
        """
        self.config = config or {}
        self.depth = self.config.get('depth', 'full')
        self.timeout = self.config.get('timeout_seconds', 30)
    
    @abstractmethod
    def can_extract(self, file_path: Path) -> bool:
        """
        Check if this extractor can handle the given file.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            True if this extractor can process the file
        """
        pass
    
    @abstractmethod
    def extract(self, file_path: Path) -> ExtractedData:
        """
        Extract information from the source file.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            ExtractedData object containing parsed information
            
        Raises:
            Exception: If extraction fails critically
        """
        pass
    
    def safe_extract(self, file_path: Path) -> ExtractedData:
        """
        Safely extract information, catching and logging errors.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            ExtractedData object, possibly with errors recorded
        """
        try:
            return self.extract(file_path)
        except Exception as e:
            # Return minimal data with error recorded
            data = ExtractedData(
                language=self.__class__.__name__.replace('Extractor', ''),
                file_path=str(file_path)
            )
            data.extraction_errors.append(f"Failed to extract from {file_path}: {str(e)}")
            return data
