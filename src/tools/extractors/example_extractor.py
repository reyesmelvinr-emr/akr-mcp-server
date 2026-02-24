"""
⚠️ DEPRECATED in v0.2.0

Example data extractor for generating realistic request/response examples.

DEPRECATION NOTICE:
- This extractor uses heuristic-based type inference to generate example data.
- Generated examples are often incomplete or unrealistic.
- For realistic examples, ask Copilot Chat to generate them from your code context.
- This module will be removed in v1.0.0.

For better results, consider:
1. Copy-paste DTO definitions and usage examples into Copilot Chat
2. Ask Chat to generate realistic request/response examples
3. Reference API contracts and validation rules for accuracy

Legacy behavior:
Parses DTO classes and generates realistic example JSON based on field types,
validation rules, and comments.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ExampleDataExtractor:
    """Extract realistic example data from C# DTOs."""
    
    def __init__(self):
        """Initialize the example extractor."""
        self.example_cache: Dict[str, Dict[str, Any]] = {}
    
    def extract_examples_from_content(self, content: str, dto_name: str) -> Optional[Dict[str, Any]]:
        """Extract example data for a specific DTO from content.
        
        Args:
            content: C# source code content
            dto_name: Name of the DTO class to extract examples for
            
        Returns:
            Example data dictionary, or None if not found
        """
        # Find the DTO class definition
        dto_pattern = rf'(?:public|sealed|class)?\s*(?:class|record)\s+{dto_name}\s*(?:<[^>]*>)?\s*{{(.*?)\n\s*}}'
        match = re.search(dto_pattern, content, re.DOTALL)
        
        if not match:
            logger.debug(f"Could not find DTO class: {dto_name}")
            return None
        
        dto_body = match.group(1)
        
        # Extract properties and generate examples
        examples = {}
        
        # PHASE 10.2: Fixed pattern that captures nullable types correctly
        # Matches: public string PropertyName { ... } or public int? PropertyName { ... }
        # Pattern: public Type PropertyName { (where Type can include ? and generics)
        prop_pattern = r'public\s+(\w+(?:\?)?(?:<[^>]*>)?)\s+(\w+)\s*{'
        
        for prop_match in re.finditer(prop_pattern, dto_body):
            prop_type = prop_match.group(1).strip()
            prop_name = prop_match.group(2).strip()
            
            logger.debug(f"PHASE 10.2: Found property {prop_name} of type {prop_type}")
            
            # Get constraints for this property
            constraints = self._extract_constraints_for_property(dto_body, prop_name)
            
            # Generate example value
            example_value = self._generate_example_value(prop_type, prop_name, constraints)
            if example_value is not None:
                examples[prop_name] = example_value
                logger.debug(f"PHASE 10.2: Generated example for {prop_name}: {example_value}")
        
        logger.info(f"PHASE 10.2: Extracted {len(examples)} example properties for {dto_name}")
        return examples if examples else None
    
    def _extract_constraints_for_property(self, dto_body: str, prop_name: str) -> Dict[str, Any]:
        """Extract validation constraints for a property.
        
        Looks for DataAnnotation attributes like [Required], [StringLength], [Range], etc.
        """
        constraints = {}
        
        # Find the property and attributes immediately before it
        # Look backwards from property name to find its attributes
        lines = dto_body.split('\n')
        prop_line_idx = -1
        
        # Find the line with this property
        for idx, line in enumerate(lines):
            if f' {prop_name} {{' in line or f'\t{prop_name} {{' in line:
                prop_line_idx = idx
                break
        
        if prop_line_idx == -1:
            return constraints
        
        # Scan backwards up to 10 lines to find attributes
        attr_start = max(0, prop_line_idx - 10)
        attrs_section = '\n'.join(lines[attr_start:prop_line_idx])
        
        # Extract constraints from attributes
        if re.search(r'\[Required', attrs_section):
            constraints['required'] = True
        
        string_length = re.search(r'\[StringLength\((\d+)(?:,\s*MinimumLength\s*=\s*(\d+))?\)', attrs_section)
        if string_length:
            constraints['max_length'] = int(string_length.group(1))
            if string_length.group(2):
                constraints['min_length'] = int(string_length.group(2))
        
        range_match = re.search(r'\[Range\((\d+),\s*(\d+)\)', attrs_section)
        if range_match:
            constraints['min'] = int(range_match.group(1))
            constraints['max'] = int(range_match.group(2))
        
        return constraints
    
    def _generate_example_value(self, prop_type: str, prop_name: str, constraints: Dict[str, Any]) -> Any:
        """Generate realistic example value based on type and constraints.
        
        Args:
            prop_type: C# type (string, int, bool, DateTime, Guid, etc.)
            prop_name: Property name (used for context)
            constraints: Validation constraints dictionary
            
        Returns:
            Example value of appropriate type
        """
        prop_type_lower = prop_type.lower()
        
        # Handle nullable types
        if prop_type_lower.startswith('string?') or 'string' in prop_type_lower:
            # Smart string examples based on property name
            if 'title' in prop_name.lower():
                return "Introduction to C#"
            elif 'description' in prop_name.lower():
                return "Learn the fundamentals of C# programming language"
            elif 'category' in prop_name.lower():
                return "Programming"
            elif 'name' in prop_name.lower():
                return "John Smith"
            elif 'email' in prop_name.lower():
                return "user@example.com"
            else:
                # Use constraints to generate appropriate string
                max_len = constraints.get('max_length', 50)
                return "Sample value"[:max_len]
        
        elif 'int' in prop_type_lower:
            min_val = constraints.get('min', 0)
            max_val = constraints.get('max', 100)
            
            # Smart integer examples
            if 'page' in prop_name.lower():
                return 1
            elif 'pagesize' in prop_name.lower():
                return 10
            elif 'validity' in prop_name.lower() or 'months' in prop_name.lower():
                return min(12, max_val)  # 12 months as example
            else:
                return min_val + (max_val - min_val) // 2
        
        elif 'bool' in prop_type_lower:
            # Smart boolean examples based on property name
            if 'active' in prop_name.lower():
                return True
            elif 'required' in prop_name.lower():
                return True
            elif 'disabled' in prop_name.lower():
                return False
            else:
                return True
        
        elif 'datetime' in prop_type_lower or 'date' in prop_type_lower:
            return "2026-02-17T10:30:00Z"
        
        elif 'guid' in prop_type_lower:
            return "550e8400-e29b-41d4-a716-446655440000"
        
        elif 'decimal' in prop_type_lower or 'float' in prop_type_lower or 'double' in prop_type_lower:
            min_val = constraints.get('min', 0)
            max_val = constraints.get('max', 100)
            return float(min_val + (max_val - min_val) / 2)
        
        elif 'list' in prop_type_lower or 'ienumerable' in prop_type_lower or 'ireadonly' in prop_type_lower:
            # Handle collections
            if 'CourseSummaryDto' in prop_type or 'CourseDetailDto' in prop_type:
                return [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Introduction to C#",
                        "isRequired": True,
                        "isActive": True,
                        "validityMonths": 12,
                        "category": "Programming"
                    }
                ]
            return []
        
        elif 'pageresponse' in prop_type_lower or 'pagedresponse' in prop_type_lower:
            return {
                "items": [],
                "page": 1,
                "pageSize": 10,
                "totalCount": 0
            }
        
        return None
    
    def generate_paged_response_example(self, item_example: Dict[str, Any], 
                                       page: int = 1, page_size: int = 10, 
                                       total_count: int = 25) -> Dict[str, Any]:
        """Generate example for a paged response.
        
        Args:
            item_example: Example item to include in items array
            page: Page number
            page_size: Items per page
            total_count: Total count of items
            
        Returns:
            Paged response example
        """
        return {
            "items": [item_example],
            "page": page,
            "pageSize": page_size,
            "totalCount": total_count
        }
    
    def generate_json_example(self, example_dict: Dict[str, Any], 
                              pretty: bool = True) -> str:
        """Generate formatted JSON string from example dictionary.
        
        Args:
            example_dict: Example data dictionary
            pretty: Whether to pretty-print JSON
            
        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(example_dict, indent=2)
        else:
            return json.dumps(example_dict)
    
    def get_create_request_example(self, create_dto_name: str,
                                  file_path: Path) -> Optional[str]:
        """Get JSON example for a Create request DTO.
        
        Args:
            create_dto_name: Name of create request DTO (e.g., CreateCourseRequest)
            file_path: Path to DTOs file
            
        Returns:
            Pretty-printed JSON example, or None if not found
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            example_data = self.extract_examples_from_content(content, create_dto_name)
            if example_data:
                return self.generate_json_example(example_data)
        except Exception as e:
            logger.warning(f"Failed to extract create request example: {e}")
        
        return None
    
    def get_response_example(self, response_dto_name: str,
                            file_path: Path) -> Optional[str]:
        """Get JSON example for a response DTO.
        
        Args:
            response_dto_name: Name of response DTO (e.g., CourseDetailDto)
            file_path: Path to DTOs file
            
        Returns:
            Pretty-printed JSON example, or None if not found
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            example_data = self.extract_examples_from_content(content, response_dto_name)
            if example_data:
                return self.generate_json_example(example_data)
        except Exception as e:
            logger.warning(f"Failed to extract response example: {e}")
        
        return None
