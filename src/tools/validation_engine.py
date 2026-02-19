"""
Validation engine for Phase 1 template enforcement.

Compares parsed document structure against a template schema and returns
structured violations with severity tiers and confidence scoring.
"""

from __future__ import annotations

from typing import Dict, List

from .document_parser import BasicDocumentStructure
from .enforcement_tool_types import (
    Heading,
    Section,
    TemplateSchema,
    ValidationResult,
    Violation,
    ViolationSeverity,
)


class ValidationEngine:
    """Phase 1 validation engine."""

    _required_yaml_fields = {
        "feature",
        "domain",
        "layer",
        "component",
        "status",
        "version",
        "componentType",
        "priority",
        "lastUpdated",
    }

    def validate_phase1(
        self, parsed_doc: BasicDocumentStructure, schema: TemplateSchema
    ) -> ValidationResult:
        """Validate a parsed document against the schema (Phase 1 rules)."""
        violations: List[Violation] = []
        violations.extend(self.check_yaml_frontmatter(parsed_doc.yaml_data))
        violations.extend(
            self.check_required_sections(parsed_doc.section_order, schema)
        )
        violations.extend(self.check_section_order(parsed_doc.section_order, schema))
        violations.extend(self.check_heading_hierarchy(parsed_doc.headings))

        severity_summary = self.calculate_severity_summary(violations)
        confidence = self.calculate_confidence(violations)
        valid = severity_summary.get("blockers", 0) == 0

        return ValidationResult(
            valid=valid,
            violations=violations,
            confidence=confidence,
            severity_summary=severity_summary,
        )

    def check_yaml_frontmatter(self, yaml_data: Dict[str, str]) -> List[Violation]:
        """Check YAML front matter for required fields."""
        violations: List[Violation] = []
        if not yaml_data:
            violations.append(
                Violation(
                    type="missing_yaml_frontmatter",
                    severity=ViolationSeverity.FIXABLE,
                    line=1,
                    message="YAML front matter is missing.",
                )
            )
            return violations

        missing_fields = [
            field
            for field in self._required_yaml_fields
            if field not in yaml_data or not yaml_data[field]
        ]
        if missing_fields:
            # Enhanced message with actionable guidance
            message = (
                f"Missing or empty YAML fields: {', '.join(sorted(missing_fields))}. "
                f"Add these fields to the document's YAML front matter at the top. "
                f"Example:\n"
                f"---\n"
                f"feature: <feature-name>\n"
                f"domain: <ui|backend|database>\n"
                f"component: <component-name>\n"
                f"... (see AKR charter for all required fields)\n"
                f"---"
            )
            violations.append(
                Violation(
                    type="missing_yaml_fields",
                    severity=ViolationSeverity.BLOCKER,
                    line=1,
                    message=message,
                )
            )
        return violations

    def check_required_sections(
        self, sections: List[str], schema: TemplateSchema
    ) -> List[Violation]:
        """Check that all required sections are present."""
        violations: List[Violation] = []
        required_names = [section.name for section in schema.required_sections]
        present_lower = {section.lower() for section in sections}

        for required in required_names:
            if required.lower() not in present_lower:
                # Enhanced message with guidance on how to add missing sections
                message = (
                    f"Missing required section: {required}. "
                    f"Add this section to your document. "
                    f"Use generate_documentation to create a complete stub with all required sections."
                )
                violations.append(
                    Violation(
                        type="missing_required_section",
                        severity=ViolationSeverity.BLOCKER,
                        line=None,
                        message=message,
                        section_name=required,
                    )
                )
        return violations

    def check_section_order(
        self, sections: List[str], schema: TemplateSchema
    ) -> List[Violation]:
        """Check ordering of required sections matches template order."""
        violations: List[Violation] = []
        required = [section.name for section in schema.required_sections]
        required_positions = [
            sections.index(section)
            for section in required
            if section in sections
        ]

        if required_positions != sorted(required_positions):
            # Enhanced message with expected vs. found order
            found_order = [s for s in sections if s in required]
            message = (
                "Sections are out of order. "
                f"Expected order: {', '.join(required)}. "
                f"Found order: {', '.join(found_order)}. "
                f"Use update_documentation_sections to reorder, or regenerate with generate_documentation."
            )
            violations.append(
                Violation(
                    type="section_order",
                    severity=ViolationSeverity.FIXABLE,
                    line=None,
                    message=message,
                )
            )
        return violations

    def check_heading_hierarchy(self, headings: List[Heading]) -> List[Violation]:
        """Check that heading levels do not jump."""
        violations: List[Violation] = []
        if not headings:
            return violations

        previous_level = headings[0].level
        for heading in headings[1:]:
            if heading.level > previous_level + 1:
                violations.append(
                    Violation(
                        type="heading_hierarchy",
                        severity=ViolationSeverity.FIXABLE,
                        line=heading.line_number,
                        message=(
                            "Heading level jump detected: "
                            f"{previous_level} → {heading.level}"
                        ),
                        section_name=heading.text,
                    )
                )
            previous_level = heading.level
        return violations

    def calculate_severity_summary(self, violations: List[Violation]) -> Dict[str, int]:
        """Return counts of violations by severity."""
        summary = {"blockers": 0, "fixable": 0, "warnings": 0}
        for violation in violations:
            if violation.severity == ViolationSeverity.BLOCKER:
                summary["blockers"] += 1
            elif violation.severity == ViolationSeverity.FIXABLE:
                summary["fixable"] += 1
            elif violation.severity == ViolationSeverity.WARN:
                summary["warnings"] += 1
        return summary

    def calculate_confidence(self, violations: List[Violation]) -> float:
        """Calculate confidence score from violation counts."""
        blockers = sum(1 for v in violations if v.severity == ViolationSeverity.BLOCKER)
        fixable = sum(1 for v in violations if v.severity == ViolationSeverity.FIXABLE)
        warnings = sum(1 for v in violations if v.severity == ViolationSeverity.WARN)

        confidence = 1.0
        confidence -= 0.3 * blockers
        confidence -= 0.1 * fixable
        confidence -= 0.05 * warnings
        return max(0.0, confidence)
