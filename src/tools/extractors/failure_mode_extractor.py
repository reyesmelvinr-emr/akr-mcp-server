"""
⚠️ DEPRECATED in v0.2.0

Failure mode extractor for identifying and documenting exception scenarios.

DEPRECATION NOTICE:
- This extractor uses heuristic-based regex to identify failure modes from exception handling.
- Results are often incomplete or incorrect due to reliance on code patterns.
- For comprehensive failure mode analysis, use Copilot Chat with failure mode charters.
- This module will be removed in v1.0.0.

For better semantic analysis, consider:
1. Copy-paste exception handling code into Copilot Chat
2. Ask Chat to identify all possible failure modes
3. Document failure modes against the backend charter

Legacy behavior:
Parses try/catch/finally blocks, extracts exception types, and correlates them
with dependency usage and operation types to create failure scenario documentation.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class FailureMode:
    """Represents a potential failure scenario for a service/dependency."""
    exception_type: str
    operation: str  # e.g., "CreateAsync", "GetAsync"
    trigger: str  # What causes this exception
    impact: str  # Business impact of this failure
    mitigation: str  # How to handle this failure
    is_expected: bool = False  # Is this a known, expected exception?


class FailureModeExtractor:
    """Extract failure modes from C# code exception handling."""
    
    def __init__(self):
        """Initialize the failure mode extractor."""
        self.exception_mappings = self._build_exception_mappings()
    
    def _build_exception_mappings(self) -> Dict[str, Dict[str, str]]:
        """Build mappings of exception types to business meaning."""
        return {
            'InvalidOperationException': {
                'meaning': 'Operation invalid in current state',
                'common_causes': 'Constraint violation, duplicate entry, missing dependency',
                'typical_response': '409 Conflict or 400 BadRequest'
            },
            'ArgumentException': {
                'meaning': 'Invalid argument provided',
                'common_causes': 'Bad input validation, null reference',
                'typical_response': '400 BadRequest'
            },
            'ArgumentNullException': {
                'meaning': 'Required argument is null',
                'common_causes': 'Missing required parameter',
                'typical_response': '400 BadRequest'
            },
            'NotFound': {
                'meaning': 'Resource not found',
                'common_causes': 'Invalid ID, soft-deleted resource',
                'typical_response': '404 NotFound'
            },
            'KeyNotFoundException': {
                'meaning': 'Key does not exist in collection',
                'common_causes': 'Invalid ID lookup',
                'typical_response': '404 NotFound'
            },
            'SqlException': {
                'meaning': 'Database operation failed',
                'common_causes': 'Connection timeout, constraint violation, deadlock',
                'typical_response': '500 InternalServerError'
            },
            'DbUpdateException': {
                'meaning': 'Entity Framework update failed',
                'common_causes': 'Constraint violation, concurrency issue',
                'typical_response': '409 Conflict'
            },
            'DbUpdateConcurrencyException': {
                'meaning': 'Concurrency conflict detected',
                'common_causes': 'Entity modified by another user',
                'typical_response': '409 Conflict'
            },
            'TimeoutException': {
                'meaning': 'Operation timed out',
                'common_causes': 'Long-running query, slow network',
                'typical_response': '504 GatewayTimeout or 500 InternalServerError'
            },
            'OperationCanceledException': {
                'meaning': 'Operation was cancelled',
                'common_causes': 'Request timeout, cancellation token triggered',
                'typical_response': '408 RequestTimeout'
            }
        }
    
    def extract_failure_modes_from_content(self, content: str, method_names: Optional[List[str]] = None) -> List[FailureMode]:
        """Extract failure modes from C# code content.
        
        Args:
            content: C# source code
            method_names: Optional list of method names to focus on
            
        Returns:
            List of failure modes found
        """
        failure_modes = []
        
        # Find all try-catch blocks
        try_catch_pattern = r'try\s*{(.*?)}(?:\s*catch\s*\(([^)]+)\)[^{]*{(.*?)})?'
        
        for match in re.finditer(try_catch_pattern, content, re.DOTALL):
            try_body = match.group(1)
            catch_clause = match.group(2)
            catch_body = match.group(3)
            
            if not catch_clause:
                continue
            
            # Extract exception type
            exception_match = re.search(r'(\w+(?:<[^>]*>)?)\s+(\w+)', catch_clause)
            if not exception_match:
                continue
            
            exception_type = exception_match.group(1)
            exception_var = exception_match.group(2)
            
            # Extract what operation might throw this
            operation = self._infer_operation_from_try_block(try_body)
            
            # Analyze the catch block to understand the mitigation
            mitigation = self._extract_mitigation_from_catch(catch_body, exception_var)
            
            # Get exception info
            exception_info = self.exception_mappings.get(exception_type, {})
            
            # Determine if this is expected (logged and handled) vs unexpected (rethrown)
            is_expected = 'throw' not in catch_body.lower() or 'throw new' in catch_body.lower()
            
            failure_mode = FailureMode(
                exception_type=exception_type,
                operation=operation or 'Unknown operation',
                trigger=exception_info.get('common_causes', 'See exception type documentation'),
                impact=exception_info.get('meaning', 'Operation failed'),
                mitigation=mitigation or 'Try/catch handling',
                is_expected=is_expected
            )
            
            failure_modes.append(failure_mode)
            logger.info(f"PHASE 10.2: Extracted failure mode: {exception_type} in {operation}")
        
        return failure_modes
    
    def _infer_operation_from_try_block(self, try_body: str) -> Optional[str]:
        """Infer what operation is being attempted from the try block content."""
        # Look for common async operation patterns
        operations = ['CreateAsync', 'UpdateAsync', 'DeleteAsync', 'GetAsync', 'ListAsync',
                      'Save', 'SaveAsync', 'Delete', 'Update', 'ValidateAsync', 'CheckAsync']
        
        for op in operations:
            if op in try_body:
                return op
        
        # Look for method calls
        method_pattern = r'\.(\w+Async)\(|\.(\w+)\('
        match = re.search(method_pattern, try_body)
        if match:
            return match.group(1) or match.group(2)
        
        return None
    
    def _extract_mitigation_from_catch(self, catch_body: str, exception_var: str) -> Optional[str]:
        """Extract the mitigation strategy from the catch block."""
        if not catch_body or not catch_body.strip():
            return None
        
        # Check for common mitigation patterns
        mitigations = []
        
        # Check if logging is done
        if re.search(r'(?:_logger|logger|log|Console)\.(Log|Warning|Error|WriteLine)', catch_body, re.IGNORECASE):
            mitigations.append('Logged for diagnostics')
        
        # Check if exception is wrapped/transformed
        if 'throw new' in catch_body:
            # Extract the new exception type
            new_exc_pattern = r'throw new (\w+)'
            new_exc_match = re.search(new_exc_pattern, catch_body)
            if new_exc_match:
                mitigations.append(f"Transform to {new_exc_match.group(1)}")
        elif 'throw;' in catch_body:
            mitigations.append('Re-thrown to caller')
        else:
            # Check if exception is suppressed
            if 'return' in catch_body or 'return null' in catch_body:
                mitigations.append('Suppressed with default return')
            elif 'default' in catch_body or 'Empty' in catch_body:
                mitigations.append('Suppressed with default value')
        
        # Check for retry logic
        if 'retry' in catch_body.lower():
            mitigations.append('Retry attempted')
        
        # Check for fallback
        if 'fallback' in catch_body.lower() or 'alternative' in catch_body.lower():
            mitigations.append('Fallback mechanism used')
        
        return ' → '.join(mitigations) if mitigations else None
    
    def format_failure_modes(self, failure_modes: List[FailureMode]) -> str:
        """Format failure modes as markdown documentation."""
        if not failure_modes:
            return "No documented failure modes found."
        
        # Group by exception type
        grouped = {}
        for fm in failure_modes:
            if fm.exception_type not in grouped:
                grouped[fm.exception_type] = []
            grouped[fm.exception_type].append(fm)
        
        md = "## Failure Modes\n\n"
        md += "| Exception | Operation | Trigger | Impact | Mitigation |\n"
        md += "|-----------|-----------|---------|--------|------------|\n"
        
        for exc_type, modes in grouped.items():
            for mode in modes:
                trigger_short = mode.trigger[:30] + '...' if len(mode.trigger) > 30 else mode.trigger
                impact_short = mode.impact[:25] + '...' if len(mode.impact) > 25 else mode.impact
                mitigation_short = mode.mitigation[:35] + '...' if len(mode.mitigation) > 35 else mode.mitigation
                
                md += f"| `{exc_type}` | {mode.operation} | {trigger_short} | {impact_short} | {mitigation_short} |\n"
        
        return md
    
    def correlate_with_dependencies(self, failure_modes: List[FailureMode], 
                                    dependency_names: List[str]) -> Dict[str, List[FailureMode]]:
        """Correlate failure modes with specific dependencies.
        
        Args:
            failure_modes: List of extracted failure modes
            dependency_names: Names of injected dependencies (e.g., ICourseService)
            
        Returns:
            Dict mapping dependency name to potential failure modes
        """
        correlated = {dep: [] for dep in dependency_names}
        
        for mode in failure_modes:
            # Logic: database exceptions likely come from repository dependencies
            # Invalid operation from domain service, timeout from external API, etc.
            if 'DbUpdateException' in mode.exception_type or 'SqlException' in mode.exception_type:
                # Likely from repository/database
                for dep in dependency_names:
                    if 'Repository' in dep or 'Db' in dep:
                        correlated[dep].append(mode)
            elif mode.exception_type in ['TimeoutException', 'OperationCanceledException']:
                # Could be from any async operation
                for dep in dependency_names:
                    correlated[dep].append(mode)
            elif 'InvalidOperationException' in mode.exception_type:
                # Likely from domain service
                for dep in dependency_names:
                    if 'Service' in dep and 'Repository' not in dep:
                        correlated[dep].append(mode)
            else:
                # Default: apply to all dependencies
                for dep in dependency_names:
                    correlated[dep].append(mode)
        
        return correlated
