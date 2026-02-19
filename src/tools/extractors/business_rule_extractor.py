"""
Business Rule & Use Case Extractor - Phase 9 Enhancement

Extracts business rules, constraints, invariants, and use cases from C# code.
Generates FAQ scaffolding from exception messages.

Key capabilities:
- Extracts business rules from validation patterns
- Identifies constraints from exception messages
- Infers invariants from conditional logic
- Maps use cases from service methods
- Generates FAQ items from common errors
"""

import re
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of business rules."""
    VALIDATION = "validation"  # From validation attributes
    CONSTRAINT = "constraint"  # From exception throws
    INVARIANT = "invariant"  # From conditional checks
    AUTHORIZATION = "authorization"  # From auth checks
    DATA_INTEGRITY = "data_integrity"  # From database constraints


@dataclass
class BusinessRule:
    """Represents a business rule extracted from code."""
    description: str
    rule_type: RuleType
    example: Optional[str] = None  # Example scenario
    violation_consequence: Optional[str] = None  # What happens if violated
    code_snippet: Optional[str] = None
    source_location: Optional[str] = None
    

@dataclass
class UseCase:
    """Represents a use case/scenario for the service."""
    title: str
    description: str
    actor: str = "User"  # Who performs this action
    preconditions: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)


@dataclass
class FAQItem:
    """Represents a frequently asked question."""
    question: str
    answer: str
    category: str = "General"  # "Error Handling", "Validation", "Business Logic", etc.


class BusinessRuleExtractor:
    """Extracts business rules, use cases, and FAQ items from C# source code."""
    
    def __init__(self):
        self.logger = logger
        
        # Exception patterns that indicate business rules
        # PHASE 10.1: Improved patterns to capture full exception messages (including internal quotes)
        self.exception_patterns = [
            (r'throw\s+new\s+(\w*Exception)\s*\(\s*"([^"]+)"', 'exception'),  # Double quotes
            (r"throw\s+new\s+(\w*Exception)\s*\(\s*'([^']+)'", 'exception_single'),  # Single quotes
            (r'throw\s+new\s+(\w+Exception)\s*\(\s*\$"([^"]+)"', 'exception_interpolated'),  # Interpolated strings
            (r'throw\s+new\s+(ArgumentNullException)\s*\(\s*nameof\s*\(\s*(\w+)\s*\)', 'argument_null'),
        ]
        
        # Validation patterns
        self.validation_patterns = [
            r'if\s*\(\s*!ModelState\.IsValid\s*\)',
            r'if\s*\(\s*string\.IsNullOrWhiteSpace\(',
            r'if\s*\(\s*\w+\s*==\s*null\s*\)',
            r'if\s*\(\s*!\w+\.Any\(',
        ]
        
        # Authorization patterns
        self.auth_patterns = [
            r'\[Authorize',
            r'User\.IsInRole\(',
            r'CheckPermission\(',
        ]
    
    def extract_business_rules(self, source_code: str, file_path: str) -> List[BusinessRule]:
        """
        Extract business rules from C# source code.
        
        Args:
            source_code: The C# source code to analyze
            file_path: Path to the source file
            
        Returns:
            List of BusinessRule objects
        """
        rules = []
        
        # Extract rules from exception throws
        rules.extend(self._extract_from_exceptions(source_code))
        
        # Extract rules from validation patterns
        rules.extend(self._extract_from_validations(source_code))
        
        # Extract rules from comments
        rules.extend(self._extract_from_comments(source_code))
        
        # Extract rules from DataAnnotations (if in DTO file)
        if 'dto' in file_path.lower() or 'request' in file_path.lower():
            rules.extend(self._extract_from_data_annotations(source_code))
        
        self.logger.info(f"Extracted {len(rules)} business rules from {file_path}")
        return rules
    
    def extract_use_cases(self, source_code: str, file_path: str) -> List[UseCase]:
        """
        Extract use cases from service methods.
        
        Args:
            source_code: The C# source code to analyze
            file_path: Path to the source file
            
        Returns:
            List of UseCase objects
        """
        use_cases = []
        
        # Pattern: Find public async Task methods (likely service operations)
        # Matches both Task<T> and Task (void)
        method_pattern = r'public\s+async\s+Task(?:<[\w<>]+>)?\s+(\w+)\s*\([^)]*\)'
        
        for match in re.finditer(method_pattern, source_code):
            method_name = match.group(1)
            
            # Infer use case from method name
            use_case = self._infer_use_case_from_method(method_name, source_code, match.start())
            if use_case:
                use_cases.append(use_case)
        
        self.logger.info(f"Extracted {len(use_cases)} use cases from {file_path}")
        return use_cases
    
    def extract_faq_items(self, source_code: str, file_path: str) -> List[FAQItem]:
        """
        Extract FAQ items from exception messages and validation errors.
        
        Args:
            source_code: The C# source code to analyze
            file_path: Path to the source file
            
        Returns:
            List of FAQItem objects
        """
        faq_items = []
        
        # Extract from exception messages
        for pattern, pattern_type in self.exception_patterns:
            for match in re.finditer(pattern, source_code, re.IGNORECASE):
                exception_type = match.group(1)
                message_or_param = match.group(2)
                
                # Handle ArgumentNullException with nameof() separately
                if pattern_type == 'argument_null':
                    message = f"{message_or_param} is required"
                else:
                    message = message_or_param
                
                # Generate FAQ from exception
                faq = self._generate_faq_from_exception(exception_type, message)
                if faq:
                    faq_items.append(faq)
        
        # Extract from validation error messages
        faq_items.extend(self._extract_faq_from_validations(source_code))
        
        self.logger.info(f"Extracted {len(faq_items)} FAQ items from {file_path}")
        return faq_items
    
    def _extract_from_exceptions(self, source_code: str) -> List[BusinessRule]:
        """Extract business rules from exception throws."""
        rules = []
        
        for pattern, pattern_type in self.exception_patterns:
            for match in re.finditer(pattern, source_code, re.IGNORECASE):
                exception_type = match.group(1)
                message_or_param = match.group(2)
                
                # Handle ArgumentNullException with nameof() separately
                if pattern_type == 'argument_null':
                    rule_type = RuleType.VALIDATION
                    description = f"{message_or_param} parameter must not be null"
                    violation = "400 BadRequest response"
                # Determine rule type from exception name for regular exceptions
                elif 'duplicate' in exception_type.lower() or 'conflict' in exception_type.lower():
                    rule_type = RuleType.CONSTRAINT
                    description = f"Uniqueness constraint: {message_or_param}"
                    violation = "409 Conflict response"
                elif 'notfound' in exception_type.lower():
                    rule_type = RuleType.CONSTRAINT
                    description = f"Existence requirement: {message_or_param}"
                    violation = "404 NotFound response"
                elif 'argument' in exception_type.lower():
                    rule_type = RuleType.VALIDATION
                    description = f"Parameter validation: {message_or_param}"
                    violation = "400 BadRequest response"
                elif 'invalidoperation' in exception_type.lower():
                    rule_type = RuleType.INVARIANT
                    description = f"Business invariant: {message_or_param}"
                    violation = "Operation fails with error"
                else:
                    rule_type = RuleType.CONSTRAINT
                    description = message_or_param
                    violation = f"{exception_type} thrown"
                
                rule = BusinessRule(
                    description=description,
                    rule_type=rule_type,
                    violation_consequence=violation,
                    code_snippet=match.group(0)
                )
                rules.append(rule)
        
        return rules
    
    def _extract_from_validations(self, source_code: str) -> List[BusinessRule]:
        """Extract business rules from validation patterns."""
        rules = []
        
        # Check for null validation
        null_check_pattern = r'if\s*\(\s*(\w+)\s*==\s*null\s*\)[\s\S]*?throw\s+new\s+\w+Exception\s*\(["\']([^"\']+)["\']'
        for match in re.finditer(null_check_pattern, source_code):
            param_name = match.group(1)
            message = match.group(2)
            
            rule = BusinessRule(
                description=f"{param_name} must not be null: {message}",
                rule_type=RuleType.VALIDATION,
                violation_consequence="ArgumentNullException",
                example=f"Ensure {param_name} is provided"
            )
            rules.append(rule)
        
        # Check for string validation
        string_check_pattern = r'if\s*\(\s*string\.IsNullOrWhiteSpace\(([^)]+)\)\s*\)[\s\S]*?throw'
        for match in re.finditer(string_check_pattern, source_code):
            param_name = match.group(1)
            
            rule = BusinessRule(
                description=f"{param_name} must not be empty or whitespace",
                rule_type=RuleType.VALIDATION,
                violation_consequence="ArgumentException",
                example=f"Provide a non-empty value for {param_name}"
            )
            rules.append(rule)
        
        return rules
    
    def _extract_from_comments(self, source_code: str) -> List[BusinessRule]:
        """Extract business rules from code comments."""
        rules = []
        
        # Pattern: // BR: Description or // Business Rule: Description
        comment_pattern = r'//\s*(?:BR|Business Rule):\s*(.+?)(?:\n|$)'
        for match in re.finditer(comment_pattern, source_code, re.IGNORECASE):
            description = match.group(1).strip()
            
            rule = BusinessRule(
                description=description,
                rule_type=RuleType.INVARIANT,
                source_location="code comment"
            )
            rules.append(rule)
        
        return rules
    
    def _extract_from_data_annotations(self, source_code: str) -> List[BusinessRule]:
        """Extract business rules from DataAnnotations attributes."""
        rules = []
        
        # [Required] attribute (allow other attributes in between)
        required_pattern = r"\[Required(?:\([^)]*ErrorMessage\s*=\s*[\"']([^\"']+)[\"'])?[^)]*\)?\][^\w]*(?:\[[^\]]+\][^\w]*)*public\s+\w+\s+(\w+)"
        for match in re.finditer(required_pattern, source_code, re.DOTALL):
            error_msg = match.group(1)
            property_name = match.group(2)
            
            description = error_msg if error_msg else f"{property_name} is required"
            
            rule = BusinessRule(
                description=description,
                rule_type=RuleType.VALIDATION,
                violation_consequence="Validation error",
                example=f"Must provide {property_name}"
            )
            rules.append(rule)
        
        # [StringLength] attribute (allow other attributes in between)
        length_pattern = r"\[StringLength\((\d+)(?:,\s*MinimumLength\s*=\s*(\d+))?[^)]*\)\][^\w]*(?:\[[^\]]+\][^\w]*)*public\s+string\s+(\w+)"
        for match in re.finditer(length_pattern, source_code, re.DOTALL):
            max_length = match.group(1)
            min_length = match.group(2)
            property_name = match.group(3)
            
            if min_length:
                description = f"{property_name} must be between {min_length} and {max_length} characters"
            else:
                description = f"{property_name} must not exceed {max_length} characters"
            
            rule = BusinessRule(
                description=description,
                rule_type=RuleType.VALIDATION,
                violation_consequence="Validation error"
            )
            rules.append(rule)
        
        # [Range] attribute (allow ErrorMessage parameter and other attributes)
        range_pattern = r"\[Range\(([^,]+),\s*([^,)]+)(?:,\s*ErrorMessage\s*=\s*[\"']([^\"']+)[\"'])?[^)]*\)\][^\w]*(?:\[[^\]]+\][^\w]*)*public\s+\w+\s+(\w+)"
        for match in re.finditer(range_pattern, source_code, re.DOTALL):
            min_val = match.group(1).strip()
            max_val = match.group(2).strip()
            error_msg = match.group(3)
            property_name = match.group(4)
            
            description = error_msg if error_msg else f"{property_name} must be between {min_val} and {max_val}"
            
            rule = BusinessRule(
                description=description,
                rule_type=RuleType.VALIDATION,
                violation_consequence="Validation error"
            )
            rules.append(rule)
        
        return rules
    
    def _infer_use_case_from_method(self, method_name: str, source_code: str, method_start: int) -> Optional[UseCase]:
        """Infer a use case from a method name and body."""
        method_lower = method_name.lower()
        
        # Determine the action
        if 'create' in method_lower or 'add' in method_lower:
            title = f"Create a new entity"
            description = f"User creates a new record using {method_name}"
            steps = [
                "User provides required information",
                "System validates the input",
                "System checks for duplicates",
                "System creates the entity",
                "System returns the created entity"
            ]
        elif 'update' in method_lower or 'modify' in method_lower:
            title = f"Update an existing entity"
            description = f"User updates an existing record using {method_name}"
            steps = [
                "User provides entity ID and updated data",
                "System validates the input",
                "System verifies entity exists",
                "System applies updates",
                "System returns the updated entity"
            ]
        elif 'delete' in method_lower or 'remove' in method_lower:
            title = f"Delete an entity"
            description = f"User deletes a record using {method_name}"
            steps = [
                "User provides entity ID",
                "System verifies entity exists",
                "System checks for dependencies",
                "System deletes the entity",
                "System confirms deletion"
            ]
        elif 'get' in method_lower or 'fetch' in method_lower or 'list' in method_lower:
            title = f"Retrieve entity information"
            description = f"User retrieves data using {method_name}"
            steps = [
                "User provides search criteria or ID",
                "System queries the database",
                "System returns matching results"
            ]
        else:
            return None
        
        use_case = UseCase(
            title=title,
            description=description,
            steps=steps,
            preconditions=["User is authenticated", "User has appropriate permissions"],
            postconditions=["Operation is logged", "Data is persisted or retrieved"]
        )
        
        return use_case
    
    def _generate_faq_from_exception(self, exception_type: str, message: str) -> Optional[FAQItem]:
        """Generate an FAQ item from an exception."""
        exception_lower = exception_type.lower()
        
        if 'duplicate' in exception_lower or 'conflict' in exception_lower:
            question = f"What does '{message}' mean?"
            answer = f"This error occurs when you try to create a record that already exists. {message}. Ensure the item is unique before creating it."
            category = "Error Handling"
        elif 'notfound' in exception_lower:
            question = f"Why am I getting a 'not found' error?"
            answer = f"{message}. This means the requested item doesn't exist in the system. Verify the ID is correct."
            category = "Error Handling"
        elif 'argument' in exception_lower:
            question = f"What validation error is '{message}'?"
            answer = f"{message}. Ensure all required fields are provided and meet the validation requirements."
            category = "Validation"
        else:
            return None
        
        return FAQItem(
            question=question,
            answer=answer,
            category=category
        )
    
    def _extract_faq_from_validations(self, source_code: str) -> List[FAQItem]:
        """Extract FAQ items from validation patterns."""
        faq_items = []
        
        # ModelState validation
        if 'ModelState.IsValid' in source_code:
            faq = FAQItem(
                question="What does 'validation failed' mean?",
                answer="This error occurs when the provided data doesn't meet the validation requirements. Check that all required fields are filled and values are within acceptable ranges.",
                category="Validation"
            )
            faq_items.append(faq)
        
        return faq_items
