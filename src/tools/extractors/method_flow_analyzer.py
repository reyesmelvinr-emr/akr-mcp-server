"""
⚠️ DEPRECATED in v0.2.0

Method Flow Analyzer - Phase 8 Enhancement

DEPRECATION NOTICE:
- This extractor uses heuristic-based regex to trace method execution flows.
- Flow diagrams are often incomplete or incorrect due to complex control flow.
- For accurate operation flow analysis, use Copilot Chat with flow context.
- This module will be removed in v1.0.0.

For better semantic analysis, consider:
1. Copy-paste relevant method code into Copilot Chat
2. Ask Chat to generate step-by-step operation flow
3. Request ASCII diagrams for complex flows

Legacy behavior:
Extracts step-by-step operation flows from C# method bodies.
Generates ASCII flow diagrams for documentation.

Key legacy capabilities:
- Identifies validation steps
- Detects database queries and persistence operations
- Extracts business logic steps
- Maps error handling paths
- Generates visual flow diagrams
"""

import re
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


logger = logging.getLogger(__name__)


class FlowStepType(Enum):
    """Types of steps in an operation flow."""
    VALIDATION = "validation"
    QUERY = "query"
    BUSINESS_LOGIC = "business_logic"
    PERSISTENCE = "persistence"
    MAPPING = "mapping"
    ERROR_HANDLING = "error_handling"
    AUTHORIZATION = "authorization"
    LOGGING = "logging"


@dataclass
class FlowStep:
    """Represents a single step in an operation flow."""
    step_number: int
    step_type: FlowStepType
    description: str
    what: str  # What this step does
    why: str  # Why this step is needed
    error_path: Optional[str] = None  # What happens if this step fails
    code_snippet: Optional[str] = None
    
    
@dataclass
class OperationFlow:
    """Represents the complete flow of an operation/method."""
    method_name: str
    operation_type: str  # "Create", "Update", "Delete", "Query", etc.
    steps: List[FlowStep] = field(default_factory=list)
    success_path: str = "Operation completed successfully"
    failure_paths: List[str] = field(default_factory=list)
    
    def generate_ascii_diagram(self) -> str:
        """Generate ASCII flow diagram for this operation."""
        lines = []
        
        for i, step in enumerate(self.steps):
            # Step box
            lines.append("┌─────────────────────────────────────────────────────────────┐")
            lines.append(f"│ Step {step.step_number}: {step.description[:46]:<46} │")
            lines.append(f"│  What  → {step.what[:50]:<50} │")
            lines.append(f"│  Why   → {step.why[:50]:<50} │")
            if step.error_path:
                lines.append(f"│  Error → {step.error_path[:50]:<50} │")
            lines.append("└─────────────────────────────────────────────────────────────┘")
            
            # Arrow to next step (if not last)
            if i < len(self.steps) - 1:
                lines.append("                          ↓")
        
        # Success path
        lines.append("                    [SUCCESS - " + self.success_path + "]")
        
        return "\n".join(lines)


class MethodFlowAnalyzer:
    """Analyzes C# method bodies to extract operation flows."""
    
    def __init__(self):
        self.logger = logger
        
        # Patterns for identifying different step types
        self.validation_patterns = [
            r'if\s*\([^)]*==\s*null\)',  # Null checks
            r'if\s*\(!\w+\.\w+\)',  # Boolean validation
            r'if\s*\([^)]*\.IsValid',  # Validation results
            r'throw\s+new\s+ArgumentException',
            r'throw\s+new\s+ArgumentNullException',
            r'ModelState\.IsValid',
            r'\.Validate\(',
        ]
        
        self.query_patterns = [
            r'\.FirstOrDefaultAsync\(',
            r'\.FindAsync\(',
            r'\.Where\(',
            r'\.GetByIdAsync\(',
            r'\.GetAsync\(',
            r'\.ToListAsync\(',
            r'\.AnyAsync\(',
            r'\.CountAsync\(',
        ]
        
        self.persistence_patterns = [
            r'\.Add\(',
            r'\.Update\(',
            r'\.Remove\(',
            r'\.SaveChangesAsync\(',
            r'\.InsertAsync\(',
            r'\.UpdateAsync\(',
            r'\.DeleteAsync\(',
        ]
        
        self.mapping_patterns = [
            r'\.Map<',
            r'\.MapTo<',
            r'new\s+\w+Dto\s*\{',
            r'new\s+\w+Response\s*\{',
        ]
    
    def extract_flows(self, source_code: str, file_path: str) -> List[OperationFlow]:
        """
        Extract operation flows from C# source code.
        
        Args:
            source_code: The C# source code to analyze
            file_path: Path to the source file
            
        Returns:
            List of OperationFlow objects
        """
        flows = []
        
        # Simpler pattern - find method signatures
        method_sig_pattern = r'(?:public|private|protected|internal)?\s+(?:async\s+)?(?:virtual\s+)?(?:override\s+)?(?:static\s+)?(?:Task<?)?[\w<>]+>?\s+(\w+)\s*\([^)]*\)\s*\{'
        
        for match in re.finditer(method_sig_pattern, source_code, re.MULTILINE):
            method_name = match.group(1)
            
            # Only analyze CRUD operations
            if not self._is_crud_operation(method_name):
                continue
            
            # Extract method body using brace matching
            method_start = match.end() - 1  # Position of opening brace
            method_body = self._extract_method_body(source_code, method_start)
            
            if not method_body:
                continue
            
            self.logger.info(f"Analyzing flow for method: {method_name}")
            
            flow = self._analyze_method_body(method_name, method_body)
            if flow and flow.steps:
                flows.append(flow)
        
        self.logger.info(f"Extracted {len(flows)} operation flows from {file_path}")
        return flows
    
    def _extract_method_body(self, source_code: str, start_pos: int) -> str:
        """
        Extract method body by matching braces.
        
        Args:
            source_code: The full source code
            start_pos: Position of the opening brace
            
        Returns:
            The method body text
        """
        if start_pos >= len(source_code) or source_code[start_pos] != '{':
            return ""
        
        brace_count = 0
        end_pos = start_pos
        
        for i in range(start_pos, len(source_code)):
            if source_code[i] == '{':
                brace_count += 1
            elif source_code[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i
                    break
        
        return source_code[start_pos+1:end_pos]  # Exclude the braces
    
    def _is_crud_operation(self, method_name: str) -> bool:
        """Check if method is a CRUD operation worth analyzing."""
        crud_keywords = ['create', 'add', 'insert', 'update', 'modify', 'delete', 'remove', 'get', 'fetch', 'query']
        method_lower = method_name.lower()
        return any(keyword in method_lower for keyword in crud_keywords)
    
    def _analyze_method_body(self, method_name: str, method_body: str) -> Optional[OperationFlow]:
        """
        Analyze a method body to extract its operation flow.
        
        Args:
            method_name: Name of the method
            method_body: The method body source code
            
        Returns:
            OperationFlow object or None
        """
        # Determine operation type
        operation_type = self._determine_operation_type(method_name)
        
        flow = OperationFlow(
            method_name=method_name,
            operation_type=operation_type
        )
        
        step_number = 1
        
        # Step 1: Check for validation
        if self._contains_pattern(method_body, self.validation_patterns):
            flow.steps.append(FlowStep(
                step_number=step_number,
                step_type=FlowStepType.VALIDATION,
                description="Validate Inputs",
                what="Check parameters and business rules",
                why="Ensure request is valid before processing",
                error_path="Invalid parameters → 400 BadRequest"
            ))
            step_number += 1
        
        # Step 2: Check for queries
        if self._contains_pattern(method_body, self.query_patterns):
            flow.steps.append(FlowStep(
                step_number=step_number,
                step_type=FlowStepType.QUERY,
                description="Query Requirements",
                what="Fetch dependent data from repositories",
                why="Verify prerequisites are met",
                error_path="Data not found → 404 NotFound"
            ))
            step_number += 1
        
        # Step 3: Check for business logic (heuristic: code between query and persistence)
        has_business_logic = len(method_body.split('\n')) > 10  # Simple heuristic
        if has_business_logic:
            flow.steps.append(FlowStep(
                step_number=step_number,
                step_type=FlowStepType.BUSINESS_LOGIC,
                description="Execute Business Logic",
                what="Apply domain rules and transformations",
                why="Enforce business constraints",
                error_path="Rule violation → 409 Conflict"
            ))
            step_number += 1
        
        # Step 4: Check for persistence
        if self._contains_pattern(method_body, self.persistence_patterns):
            flow.steps.append(FlowStep(
                step_number=step_number,
                step_type=FlowStepType.PERSISTENCE,
                description="Persist Results",
                what="Save changes to database",
                why="Make changes durable",
                error_path="Database failure → 500 InternalServerError"
            ))
            step_number += 1
        
        # Step 5: Check for mapping/transformation
        if self._contains_pattern(method_body, self.mapping_patterns):
            # Only add if not already covered
            if not any(s.step_type == FlowStepType.MAPPING for s in flow.steps):
                flow.steps.append(FlowStep(
                    step_number=step_number,
                    step_type=FlowStepType.MAPPING,
                    description="Transform Results",
                    what="Map entity to DTO/response",
                    why="Return client-friendly format",
                    error_path="Mapping failure → 500 InternalServerError"
                ))
        
        return flow if flow.steps else None
    
    def _determine_operation_type(self, method_name: str) -> str:
        """Determine the type of operation from method name."""
        method_lower = method_name.lower()
        
        if 'create' in method_lower or 'add' in method_lower or 'insert' in method_lower:
            return "Create"
        elif 'update' in method_lower or 'modify' in method_lower:
            return "Update"
        elif 'delete' in method_lower or 'remove' in method_lower:
            return "Delete"
        elif 'get' in method_lower or 'fetch' in method_lower or 'query' in method_lower:
            return "Query"
        else:
            return "Operation"
    
    def _contains_pattern(self, text: str, patterns: List[str]) -> bool:
        """Check if text contains any of the regex patterns."""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
