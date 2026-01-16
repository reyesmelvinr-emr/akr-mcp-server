#!/usr/bin/env python3
"""
AKR Documentation Validator

Validates AKR documentation against Charter requirements:
- Required sections present
- Transparency markers included
- Minimum content length
- Proper structure and formatting
- Completeness scoring

Usage:
    python validate_documentation.py <file_path>
    python validate_documentation.py --changed-files  # Validate only changed files
    python validate_documentation.py --all docs/      # Validate all files in directory
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class Severity(Enum):
    """Validation issue severity levels"""
    ERROR = "error"
    WARNING = "warning"
    SUGGESTION = "suggestion"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    severity: Severity
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    rule: Optional[str] = None
    suggestion: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "severity": self.severity.value,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "rule": self.rule,
            "suggestion": self.suggestion
        }


@dataclass
class ValidationResult:
    """Result of documentation validation"""
    file_path: str
    valid: bool
    completeness_score: float
    issues: List[ValidationIssue] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == Severity.ERROR)
    
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == Severity.WARNING)
    
    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "valid": self.valid,
            "completeness_score": self.completeness_score,
            "error_count": self.error_count(),
            "warning_count": self.warning_count(),
            "issues": [issue.to_dict() for issue in self.issues],
            "metadata": self.metadata
        }


class AKRDocumentationValidator:
    """Validates AKR documentation files"""
    
    # Required sections per AKR Charter
    REQUIRED_SECTIONS_BACKEND = [
        "overview",
        "purpose and scope",
        "dependencies",
        "key methods"
    ]
    
    REQUIRED_SECTIONS_UI = [
        "overview",
        "props",
        "usage",
        "examples"
    ]
    
    REQUIRED_SECTIONS_DB = [
        "overview",
        "schema",
        "relationships",
        "indexes"
    ]
    
    # Transparency markers
    AI_MARKER = "🤖"
    HUMAN_INPUT_MARKER = "❓"
    HUMAN_AUTHORED_MARKER = "👤"
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content = ""
        self.lines: List[str] = []
        self.issues: List[ValidationIssue] = []
        
    def validate(self) -> ValidationResult:
        """Run all validation checks"""
        if not self.file_path.exists():
            return ValidationResult(
                file_path=str(self.file_path),
                valid=False,
                completeness_score=0.0,
                issues=[ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"File not found: {self.file_path}",
                    rule="file-existence"
                )]
            )
        
        # Load file content
        self.content = self.file_path.read_text(encoding='utf-8')
        self.lines = self.content.split('\n')
        
        # Run validation checks
        self._check_required_sections()
        self._check_transparency_markers()
        self._check_minimum_length()
        self._check_heading_structure()
        self._check_code_examples()
        self._check_links()
        
        # Calculate completeness score
        completeness = self._calculate_completeness()
        
        # Determine if document is valid (no errors)
        valid = self.error_count() == 0 and completeness >= 0.7
        
        return ValidationResult(
            file_path=str(self.file_path),
            valid=valid,
            completeness_score=completeness,
            issues=self.issues,
            metadata={
                "line_count": len(self.lines),
                "word_count": len(self.content.split()),
                "has_code_examples": "```" in self.content,
                "section_count": len(re.findall(r'^##\s+', self.content, re.MULTILINE))
            }
        )
    
    def _check_required_sections(self):
        """Check for required sections based on document type"""
        # Detect document type from path or content
        doc_type = self._detect_document_type()
        
        required_sections = {
            "backend": self.REQUIRED_SECTIONS_BACKEND,
            "ui": self.REQUIRED_SECTIONS_UI,
            "database": self.REQUIRED_SECTIONS_DB
        }.get(doc_type, self.REQUIRED_SECTIONS_BACKEND)
        
        # Extract all h2 headings
        headings = re.findall(r'^##\s+(.+)$', self.content, re.MULTILINE)
        headings_lower = [h.lower().strip() for h in headings]
        
        # Check each required section
        for required in required_sections:
            if required not in headings_lower:
                self.issues.append(ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Missing required section: '{required.title()}'",
                    rule="required-sections",
                    suggestion=f"Add section: ## {required.title()}"
                ))
    
    def _check_transparency_markers(self):
        """Check for transparency markers"""
        has_ai_marker = self.AI_MARKER in self.content
        has_human_input = self.HUMAN_INPUT_MARKER in self.content
        has_human_authored = self.HUMAN_AUTHORED_MARKER in self.content
        
        if not (has_ai_marker or has_human_input or has_human_authored):
            self.issues.append(ValidationIssue(
                severity=Severity.ERROR,
                message="Document must include transparency markers (🤖 AI-generated, ❓ Human input needed, 👤 Human-authored)",
                rule="transparency-markers",
                suggestion="Add transparency markers at the beginning of sections to indicate content source"
            ))
    
    def _check_minimum_length(self):
        """Check if sections meet minimum length requirements"""
        sections = re.split(r'^##\s+(.+)$', self.content, flags=re.MULTILINE)
        
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                section_name = sections[i].strip()
                section_content = sections[i + 1].strip()
                
                # Minimum 50 characters per section (excluding whitespace)
                if len(section_content) < 50:
                    line_num = self._find_line_number(f"## {section_name}")
                    self.issues.append(ValidationIssue(
                        severity=Severity.WARNING,
                        message=f"Section '{section_name}' is too short ({len(section_content)} chars, minimum 50 recommended)",
                        line=line_num,
                        rule="minimum-length",
                        suggestion="Provide more detailed content for this section"
                    ))
    
    def _check_heading_structure(self):
        """Check heading hierarchy and formatting"""
        # Check for proper heading hierarchy (no skipping levels)
        headings = re.finditer(r'^(#{1,6})\s+(.+)$', self.content, re.MULTILINE)
        prev_level = 0
        
        for match in headings:
            level = len(match.group(1))
            heading_text = match.group(2)
            line_num = self.content[:match.start()].count('\n') + 1
            
            # Check for skipped levels
            if level > prev_level + 1 and prev_level > 0:
                self.issues.append(ValidationIssue(
                    severity=Severity.WARNING,
                    message=f"Heading level skipped (from h{prev_level} to h{level}): {heading_text}",
                    line=line_num,
                    rule="heading-hierarchy"
                ))
            
            prev_level = level
    
    def _check_code_examples(self):
        """Check for code examples where helpful"""
        # If document describes methods/functions, recommend code examples
        has_methods_section = bool(re.search(r'##\s+(key methods|methods|functions)', self.content, re.IGNORECASE))
        has_code_blocks = "```" in self.content
        
        if has_methods_section and not has_code_blocks:
            self.issues.append(ValidationIssue(
                severity=Severity.SUGGESTION,
                message="Consider adding code examples for clarity",
                rule="code-examples",
                suggestion="Add fenced code blocks (```) with examples of how to use the documented methods"
            ))
    
    def _check_links(self):
        """Check for broken internal links"""
        # Find all markdown links
        links = re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', self.content)
        
        for match in links:
            link_text = match.group(1)
            link_url = match.group(2)
            line_num = self.content[:match.start()].count('\n') + 1
            
            # Check internal links (relative paths)
            if not link_url.startswith(('http://', 'https://', '#', 'mailto:')):
                link_path = self.file_path.parent / link_url
                if not link_path.exists():
                    self.issues.append(ValidationIssue(
                        severity=Severity.WARNING,
                        message=f"Broken internal link: {link_url}",
                        line=line_num,
                        rule="broken-links",
                        suggestion=f"Verify link target exists or update link"
                    ))
    
    def _calculate_completeness(self) -> float:
        """Calculate documentation completeness score (0-1)"""
        score = 1.0
        
        # Deduct for each error
        score -= self.error_count() * 0.15
        
        # Deduct for each warning
        score -= self.warning_count() * 0.05
        
        # Bonus for code examples
        if "```" in self.content:
            score += 0.05
        
        # Bonus for diagrams
        if "```mermaid" in self.content or "![" in self.content:
            score += 0.05
        
        return max(0.0, min(1.0, score))
    
    def _detect_document_type(self) -> str:
        """Detect document type from path or content"""
        path_lower = str(self.file_path).lower()
        
        if any(x in path_lower for x in ['service', 'api', 'backend', 'controller']):
            return "backend"
        elif any(x in path_lower for x in ['component', 'ui', 'frontend', 'view']):
            return "ui"
        elif any(x in path_lower for x in ['database', 'table', 'schema', 'db']):
            return "database"
        
        return "backend"  # Default
    
    def _find_line_number(self, text: str) -> Optional[int]:
        """Find line number of text in content"""
        for i, line in enumerate(self.lines, start=1):
            if text in line:
                return i
        return None
    
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == Severity.ERROR)
    
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == Severity.WARNING)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Validate AKR documentation")
    parser.add_argument("file_path", nargs="?", help="Path to documentation file")
    parser.add_argument("--all", metavar="DIR", help="Validate all markdown files in directory")
    parser.add_argument("--changed-files", action="store_true", help="Validate only changed files (uses git diff)")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--fail-on-error", action="store_true", help="Exit with non-zero code if errors found")
    parser.add_argument("--min-score", type=float, default=0.7, help="Minimum completeness score (0-1)")
    
    args = parser.parse_args()
    
    # Collect files to validate
    files_to_check: List[Path] = []
    
    if args.all:
        dir_path = Path(args.all)
        if not dir_path.is_dir():
            print(f"Error: {args.all} is not a directory", file=sys.stderr)
            sys.exit(1)
        files_to_check = list(dir_path.rglob("*.md"))
    elif args.changed_files:
        # Get changed files from git
        import subprocess
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=AM", "HEAD"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            files_to_check = [
                Path(f) for f in result.stdout.strip().split('\n')
                if f.endswith('.md') and Path(f).exists()
            ]
    elif args.file_path:
        files_to_check = [Path(args.file_path)]
    else:
        parser.print_help()
        sys.exit(1)
    
    # Validate each file
    results: List[ValidationResult] = []
    for file_path in files_to_check:
        validator = AKRDocumentationValidator(str(file_path))
        result = validator.validate()
        results.append(result)
    
    # Output results
    if args.output == "json":
        output = {
            "results": [r.to_dict() for r in results],
            "summary": {
                "total_files": len(results),
                "valid_files": sum(1 for r in results if r.valid),
                "invalid_files": sum(1 for r in results if not r.valid),
                "average_completeness": sum(r.completeness_score for r in results) / len(results) if results else 0,
                "total_errors": sum(r.error_count() for r in results),
                "total_warnings": sum(r.warning_count() for r in results)
            }
        }
        print(json.dumps(output, indent=2))
    else:
        # Text output
        for result in results:
            print(f"\n{'='*80}")
            print(f"File: {result.file_path}")
            print(f"Status: {'✅ VALID' if result.valid else '❌ INVALID'}")
            print(f"Completeness: {result.completeness_score:.0%}")
            print(f"Errors: {result.error_count()}, Warnings: {result.warning_count()}")
            
            if result.issues:
                print(f"\nIssues:")
                for issue in result.issues:
                    icon = {"error": "❌", "warning": "⚠️", "suggestion": "💡", "info": "ℹ️"}[issue.severity.value]
                    location = f" (line {issue.line})" if issue.line else ""
                    print(f"  {icon} {issue.severity.value.upper()}{location}: {issue.message}")
                    if issue.suggestion:
                        print(f"     Suggestion: {issue.suggestion}")
        
        # Summary
        print(f"\n{'='*80}")
        print("Summary:")
        print(f"  Total files: {len(results)}")
        print(f"  Valid: {sum(1 for r in results if r.valid)}")
        print(f"  Invalid: {sum(1 for r in results if not r.valid)}")
        print(f"  Average completeness: {sum(r.completeness_score for r in results) / len(results):.0%}" if results else "  N/A")
    
    # Exit code
    if args.fail_on_error:
        has_errors = any(r.error_count() > 0 for r in results)
        below_min_score = any(r.completeness_score < args.min_score for r in results)
        if has_errors or below_min_score:
            sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
