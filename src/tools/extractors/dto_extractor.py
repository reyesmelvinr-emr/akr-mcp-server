"""DTO and Request-Response Extractor for C# code.

This extractor identifies and analyzes Data Transfer Objects (DTOs),
request models, and response models to extract:
- Property definitions and types
- DataAnnotations attributes ([Required], [StringLength], etc.)
- Sample JSON examples for requests/responses
- Validation rules matrices
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

logger = None  # Will be initialized when imported


@dataclass
class DTOProperty:
    """Represents a single DTO property."""
    name: str
    type: str
    nullable: bool
    required: bool = False
    max_length: Optional[int] = None
    attributes: List[str] = field(default_factory=list)
    description: str = ""
    example_value: Optional[str] = None

    @property
    def is_primitive(self) -> bool:
        """Check if type is primitive (string, int, bool, etc)."""
        primitives = {'string', 'int', 'bool', 'float', 'double', 'decimal', 'datetime', 'guid'}
        return self.type.lower() in primitives

    def get_example_value(self) -> str:
        """Generate example value for JSON serialization."""
        if self.example_value:
            return self.example_value
        
        type_lower = self.type.lower()
        if type_lower == 'string':
            return f'"{self.name} value"'
        elif type_lower == 'bool':
            return 'true'
        elif type_lower in ('int', 'decimal', 'float', 'double'):
            return '0'
        elif type_lower == 'datetime':
            return '"2026-02-17T12:00:00Z"'
        elif type_lower == 'guid':
            return '"550e8400-e29b-41d4-a716-446655440000"'
        else:
            return 'null'


@dataclass
class ValidationRule:
    """Represents a validation rule for a DTO property."""
    property_name: str
    attribute_name: str
    error_message: str
    rule_description: str = ""
    constraint_value: Optional[str] = None  # e.g., "255" for StringLength


@dataclass
class ExtractedDTO:
    """Represents an extracted DTO with its properties and validations."""
    name: str
    file_path: str
    namespace: str
    properties: List[DTOProperty] = field(default_factory=list)
    validations: List[ValidationRule] = field(default_factory=list)
    dto_type: str = "unknown"  # "Request", "Response", "DTO", "Contract", etc.
    is_generic: bool = False
    generic_args: List[str] = field(default_factory=list)
    description: str = ""

    @property
    def required_properties(self) -> List[DTOProperty]:
        """Get list of required properties."""
        return [p for p in self.properties if p.required]

    @property
    def optional_properties(self) -> List[DTOProperty]:
        """Get list of optional properties."""
        return [p for p in self.properties if not p.required]


class DTOExtractor:
    """Extracts DTO definitions, properties, and validation rules from C# code."""

    def __init__(self):
        pass
        
    # Regex patterns for DTO extraction
    DTO_CLASS_PATTERN = re.compile(
        r'(?:public\s+)?(?:class|record)\s+(\w+(?:<[\w,\s]+>)?)\s*{',
        re.MULTILINE
    )
    
    PROPERTY_PATTERN = re.compile(
        r'(?:public\s+)?(\w+(?:\?\s*)?)\s+(\w+)\s*{\s*(?:get|set)',
        re.MULTILINE
    )
    
    # DataAnnotations patterns
    REQUIRED_PATTERN = re.compile(r'\[Required\]|\brequired\b', re.IGNORECASE)
    STRING_LENGTH_PATTERN = re.compile(r'\[StringLength\((\d+)(?:,\s*MinimumLength\s*=\s*(\d+))?\)\]')
    RANGE_PATTERN = re.compile(r'\[Range\((\d+),\s*(\d+)\)\]')
    REGEX_PATTERN = re.compile(r'\[RegularExpression\("([^"]+)"\)\]')
    MAX_LENGTH_PATTERN = re.compile(r'\[MaxLength\((\d+)\)\]')
    MIN_LENGTH_PATTERN = re.compile(r'\[MinLength\((\d+)\)\]')
    DISPLAY_PATTERN = re.compile(r'\[Display\(Name\s*=\s*"([^"]+)"\)\]')

    def extract_dtos(self, file_content: str, file_path: str) -> List[ExtractedDTO]:
        """Extract all DTOs from a C# file.
        
        Args:
            file_content: Content of the C# file
            file_path: Path to the file (for reference)
            
        Returns:
            List of extracted DTOs
        """
        dtos = []
        
        # Extract namespace
        namespace_match = re.search(r'namespace\s+([\w.]+)', file_content)
        namespace = namespace_match.group(1) if namespace_match else "Unknown"
        
        # Find all class definitions
        for match in re.finditer(self.DTO_CLASS_PATTERN, file_content):
            class_name = match.group(1)
            class_start = match.start()
            
            # Find matching closing brace
            brace_count = 1
            pos = match.end()
            while pos < len(file_content) and brace_count > 0:
                if file_content[pos] == '{':
                    brace_count += 1
                elif file_content[pos] == '}':
                    brace_count -= 1
                pos += 1
            
            class_body = file_content[class_start:pos]
            
            # Extract properties and validations
            properties = self._extract_properties(class_body)
            validations = self._extract_validations(class_body, [p.name for p in properties])
            
            # Determine DTO type
            dto_type = self._determine_dto_type(class_name)
            
            # Create ExtractedDTO
            dto = ExtractedDTO(
                name=class_name.replace('<', '[').replace('>', ']'),  # Handle generics
                file_path=file_path,
                namespace=namespace,
                properties=properties,
                validations=validations,
                dto_type=dto_type,
                is_generic='<' in class_name,
                generic_args=self._extract_generic_args(class_name)
            )
            
            dtos.append(dto)
        
        return dtos

    def _extract_properties(self, class_body: str) -> List[DTOProperty]:
        """Extract properties from class body.
        
        Args:
            class_body: Body of the class definition
            
        Returns:
            List of extracted properties
        """
        properties = []
        
        # Split by lines and look for property definitions
        lines = class_body.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for property pattern
            if 'public' in line and ('{' in line or 'get' in line or 'set' in line):
                # Extract type and property name
                prop_match = re.search(r'public\s+(\w+\??)\s+(\w+)\s*{', line)
                if prop_match:
                    prop_type = prop_match.group(1)
                    prop_name = prop_match.group(2)
                    
                    # Check if nullable
                    nullable = prop_type.endswith('?')
                    if nullable:
                        prop_type = prop_type[:-1]  # Remove ?
                    
                    # Look for attributes above this property
                    attributes = []
                    j = i - 1
                    while j >= 0 and lines[j].strip().startswith('['):
                        attr_line = lines[j].strip()
                        attr_name = re.search(r'\[(\w+)', attr_line)
                        if attr_name:
                            attributes.append(attr_name.group(1))
                        j -= 1
                    
                    properties.append(DTOProperty(
                        name=prop_name,
                        type=prop_type,
                        nullable=nullable,
                        required='Required' in attributes,
                        attributes=attributes,
                        description=f"Property: {prop_name}"
                    ))
            
            i += 1
        
        return properties

    def _extract_validations(self, class_body: str, property_names: List[str]) -> List[ValidationRule]:
        """Extract validation rules from class body.
        
        Args:
            class_body: Body of the class definition
            property_names: List of property names to match validations with
            
        Returns:
            List of extracted validation rules
        """
        validations = []
        lines = class_body.split('\n')
        
        for i, line in enumerate(lines):
            # String length validation
            match = self.STRING_LENGTH_PATTERN.search(line)
            if match:
                max_len = match.group(1)
                prop_name = self._find_associated_property(lines, i)
                if prop_name:
                    validations.append(ValidationRule(
                        property_name=prop_name,
                        attribute_name="StringLength",
                        error_message=f"{prop_name} must not exceed {max_len} characters",
                        constraint_value=max_len
                    ))
            
            # Required validation
            if self.REQUIRED_PATTERN.search(line):
                prop_name = self._find_associated_property(lines, i)
                if prop_name:
                    validations.append(ValidationRule(
                        property_name=prop_name,
                        attribute_name="Required",
                        error_message=f"{prop_name} is required"
                    ))
            
            # Range validation
            match = self.RANGE_PATTERN.search(line)
            if match:
                min_val, max_val = match.group(1), match.group(2)
                prop_name = self._find_associated_property(lines, i)
                if prop_name:
                    validations.append(ValidationRule(
                        property_name=prop_name,
                        attribute_name="Range",
                        error_message=f"{prop_name} must be between {min_val} and {max_val}",
                        constraint_value=f"{min_val}-{max_val}"
                    ))
        
        return validations

    def _find_associated_property(self, lines: List[str], attribute_line_index: int) -> Optional[str]:
        """Find the property name associated with an attribute.
        
        Assumes attribute is immediately above the property definition.
        """
        # Look at the next few lines for a property definition
        for i in range(attribute_line_index + 1, min(attribute_line_index + 5, len(lines))):
            line = lines[i].strip()
            prop_match = re.search(r'public\s+\w+\??\s+(\w+)\s*{', line)
            if prop_match:
                return prop_match.group(1)
        return None

    def _determine_dto_type(self, class_name: str) -> str:
        """Infer DTO type from class name.
        
        Args:
            class_name: Name of the class
            
        Returns:
            Type classification: "Request", "Response", "DTO", "Contract", etc.
        """
        name_lower = class_name.lower()
        
        # Check specific types before generic ones
        if 'createadmin' in name_lower:
            return "CreateRequestAdmin"
        elif 'create' in name_lower:
            return "CreateRequest"
        elif 'update' in name_lower:
            return "UpdateRequest"
        elif 'delete' in name_lower:
            return "DeleteRequest"
        elif 'detail' in name_lower or 'get' in name_lower:
            return "DetailResponse"
        elif 'list' in name_lower:
            return "ListResponse"
        elif 'request' in name_lower:
            return "Request"
        elif 'response' in name_lower:
            return "Response"
        elif 'contract' in name_lower:
            return "Contract"
        elif 'dto' in name_lower:
            return "DTO"
        else:
            return "DTO"

    @staticmethod
    def _extract_generic_args(class_name: str) -> List[str]:
        """Extract generic type arguments from class name.
        
        Args:
            class_name: Class name with possible generic args (e.g., "PagedResponse<T>")
            
        Returns:
            List of generic argument names
        """
        match = re.search(r'<([^>]+)>', class_name)
        if match:
            return [arg.strip() for arg in match.group(1).split(',')]
        return []

    def generate_sample_json(self, dto: ExtractedDTO) -> Dict[str, Any]:
        """Generate sample JSON for a DTO.
        
        Args:
            dto: The DTO to generate JSON for
            
        Returns:
            Dictionary representing sample JSON object
        """
        sample = {}
        
        for prop in dto.properties:
            # Generate appropriate example value
            type_lower = prop.type.lower()
            
            if type_lower == 'string':
                sample[prop.name] = f"{prop.name} example" if not prop.example_value else prop.example_value
            elif type_lower == 'bool':
                sample[prop.name] = True
            elif type_lower in ('int', 'integer'):
                sample[prop.name] = 0
            elif type_lower in ('decimal', 'float', 'double'):
                sample[prop.name] = 0.0
            elif type_lower == 'datetime':
                sample[prop.name] = "2026-02-17T12:00:00Z"
            elif type_lower == 'guid':
                sample[prop.name] = "550e8400-e29b-41d4-a716-446655440000"
            elif type_lower in ('list', 'array', 'list[]', 'ienumerable'):
                sample[prop.name] = []
            elif prop.nullable:
                sample[prop.name] = None
            else:
                sample[prop.name] = f"<{type_lower}>"
        
        return sample

    def generate_validation_matrix(self, dto: ExtractedDTO) -> List[Dict[str, str]]:
        """Generate validation rule matrix for template rendering.
        
        Args:
            dto: The DTO to generate matrix for
            
        Returns:
            List of dictionaries suitable for Markdown table rendering
        """
        matrix = []
        
        for validation in dto.validations:
            matrix.append({
                'property': validation.property_name,
                'rule': validation.attribute_name,
                'error_message': validation.error_message,
                'constraint': validation.constraint_value or ''
            })
        
        # Add required properties as validation rows
        for prop in dto.required_properties:
            if not any(v.property_name == prop.name and v.attribute_name == 'Required' for v in dto.validations):
                matrix.append({
                    'property': prop.name,
                    'rule': 'Required',
                    'error_message': f"{prop.name} is required",
                    'constraint': ''
                })
        
        return matrix
