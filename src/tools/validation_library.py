"""
Phase 3 Validation Library - Dual-Faceted Validation Engine.

Provides comprehensive document validation with:
- JSON Schema validation for front-matter (using jsonschema library)
- Tier-based severity thresholds (TIER_1: strict, TIER_2: moderate, TIER_3: lenient)
- Auto-fix capabilities for common issues
- Unified diff generation for dry-run mode
- Provenance metadata tracking (templateSource, templateCommit)

This module is the foundation for both MCP tool and CLI implementations.
Dependency: TemplateSchemaBuilder → TemplateResolver

Usage:
    from validation_library import ValidationEngine, ValidationTier
    
    engine = ValidationEngine(schema_builder=builder, config=config)
    result = engine.validate(
        doc_content=markdown_text,
        template_id="lean_baseline_service_template",
        tier_level=ValidationTier.TIER_2,
        auto_fix=True,
        dry_run=True
    )
    print(f"Valid: {result.is_valid}")
    print(f"Violations: {result.violations}")
    if result.auto_fixed_content:
        print(f"Suggested fixes:\n{result.diff}")
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Union
from datetime import datetime
from difflib import unified_diff

import jsonschema
from jsonschema import ValidationError

from .document_parser import BasicDocumentParser, BasicDocumentStructure
from .template_schema_builder import TemplateSchemaBuilder
from .enforcement_tool_types import Violation, ViolationSeverity


# ==================== PHASE 3: TIER-BASED VALIDATION ====================


class ValidationTier(Enum):
    """Validation strictness levels."""

    TIER_1 = "TIER_1"  # Strict: BLOCKER for missing sections, wrong order; ≥80% completeness
    TIER_2 = "TIER_2"  # Moderate: FIXABLE for missing sections; ≥60% completeness
    TIER_3 = "TIER_3"  # Lenient: FIXABLE for missing sections; ≥30% completeness


class ViolationType(Enum):
    """Detailed violation types for Phase 3."""

    MISSING_YAML_FRONTMATTER = "missing_yaml_frontmatter"
    INVALID_YAML_SYNTAX = "invalid_yaml_syntax"
    MISSING_YAML_FIELD = "missing_yaml_field"
    INVALID_YAML_FIELD_TYPE = "invalid_yaml_field_type"  # jsonschema violation
    YAML_SCHEMA_VALIDATION_FAILED = "yaml_schema_validation_failed"
    MISSING_REQUIRED_SECTION = "missing_required_section"
    WRONG_SECTION_ORDER = "wrong_section_order"
    INCOMPLETE_SECTION = "incomplete_section"
    INVALID_HEADING_HIERARCHY = "invalid_heading_hierarchy"
    MALFORMED_MARKDOWN = "malformed_markdown"


@dataclass
class FieldPathElement:
    """Represents a path element in JSON validation errors."""

    field_name: str
    index: Optional[int] = None

    def to_dot_notation(self) -> str:
        """Convert to dot notation: 'frontmatter.field' or 'frontmatter.array[0]'."""
        if self.index is not None:
            return f"{self.field_name}[{self.index}]"
        return self.field_name


@dataclass
class EnhancedViolation:
    """Phase 3 enhanced violation with rich context."""

    type: str
    severity: str  # "BLOCKER" | "FIXABLE" | "WARN"
    field: str  # "frontmatter", "section", "heading", etc.
    field_path: str  # "frontmatter.project" or "section.0"
    message: str
    suggestion: str
    auto_fixable: bool
    validator: Optional[str] = None  # "type", "enum", "pattern", "required", etc.
    line: Optional[int] = None
    expected: Optional[str] = None  # Expected value for enum/pattern violations
    actual: Optional[str] = None  # Actual value

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ProvenzanceMetadata:
    """Provenance tracking for validation results."""

    template_source: str  # "submodule" | "local-override" | "remote-preview"
    template_commit: Optional[str]  # Git commit SHA or version tag
    template_version: Optional[str]  # Version from manifest
    validated_at_utc: str
    server_version: str = "0.2.0"


@dataclass
class ValidationResult:
    """Phase 3 validation result with rich metadata."""

    is_valid: bool
    violations: List[EnhancedViolation] = field(default_factory=list)
    auto_fixed_content: Optional[str] = None
    diff: Optional[str] = None  # Unified diff if auto_fix=True and dry_run=True
    metadata: Optional[ProvenzanceMetadata] = None
    completeness: float = 0.0  # 0.0-1.0 estimate of section fill
    tier_level: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = {
            "is_valid": self.is_valid,
            "violations": [v.to_dict() for v in self.violations],
            "auto_fixed_content": self.auto_fixed_content,
            "diff": self.diff,
            "completeness": self.completeness,
            "tier_level": self.tier_level,
        }
        if self.metadata:
            data["metadata"] = asdict(self.metadata)
        return data


# ==================== PHASE 3: VALIDATION ENGINE ====================


class ValidationEngine:
    """Phase 3 validation engine with JSON Schema, tier-based checks, and auto-fix."""

    def __init__(
        self,
        schema_builder: TemplateSchemaBuilder,
        config: Optional[Dict] = None,
    ):
        """
        Initialize validation engine.

        Args:
            schema_builder: TemplateSchemaBuilder instance for loading schemas
            config: Optional configuration dict with validation settings
        """
        self.schema_builder = schema_builder
        self.config = config or {}
        self.parser = BasicDocumentParser()

        # Tier-based thresholds
        self.tier_thresholds = {
            ValidationTier.TIER_1: {"completeness": 0.80, "severity": "BLOCKER"},
            ValidationTier.TIER_2: {"completeness": 0.60, "severity": "FIXABLE"},
            ValidationTier.TIER_3: {"completeness": 0.30, "severity": "FIXABLE"},
        }

    def validate(
        self,
        doc_content: str,
        template_id: str,
        tier_level: Union[ValidationTier, str] = ValidationTier.TIER_2,
        auto_fix: bool = False,
        dry_run: bool = True,
    ) -> ValidationResult:
        """
        Validate a document against a template schema.

        Args:
            doc_content: Markdown document content
            template_id: Template ID to validate against
            tier_level: ValidationTier level (TIER_1, TIER_2, TIER_3)
            auto_fix: Whether to attempt auto-fixes
            dry_run: If True with auto_fix, return diff without writing

        Returns:
            ValidationResult with violations, auto-fixed content, and metadata
        """
        # Normalize tier_level
        if isinstance(tier_level, str):
            tier_level = ValidationTier[tier_level]

        # Parse document
        parsed = self.parser.parse_document(doc_content)

        # Initialize violation list
        violations: List[EnhancedViolation] = []

        # 1. Validate YAML front matter
        violations.extend(self._validate_yaml_frontmatter(parsed, template_id))

        # 2. Get template schema for section/heading validation
        try:
            # Get template content - supports both TemplateResolver and AKRResourceManager
            template_content = None
            from src.resources.template_resolver import TemplateResolver
            from src.resources.akr_resources import AKRResourceManager
            
            if isinstance(self.schema_builder._resolver, TemplateResolver):
                template_content = self.schema_builder._resolver.get_template(template_id)
            elif isinstance(self.schema_builder._resolver, AKRResourceManager):
                template_content = self.schema_builder._resolver.get_resource_content("template", f"{template_id}.md")
            
            if not template_content:
                raise ValueError(f"Template '{template_id}' not found")
            template_schema = self.schema_builder.build_schema(template_id, template_content)
        except Exception as e:
            violations.append(
                EnhancedViolation(
                    type="template_schema_load_failed",
                    severity="BLOCKER",
                    field="schema",
                    field_path="schema",
                    message=f"Failed to load template schema: {str(e)}",
                    suggestion="Verify template_id is valid; check template manifest",
                    auto_fixable=False,
                    line=1,
                )
            )
            return ValidationResult(
                is_valid=False,
                violations=violations,
                tier_level=tier_level.value,
            )

        # 3. Validate sections against schema
        violations.extend(
            self._validate_sections(
                parsed, template_schema, tier_level, doc_content
            )
        )

        # 4. Calculate completeness
        completeness = self._calculate_completeness(parsed)

        # 5. Apply tier-based severity adjustments
        self._apply_tier_severity(violations, tier_level)

        # 6. Determine validity (no BLOCKER violations)
        is_valid = not any(v.severity == "BLOCKER" for v in violations)

        # 7. Auto-fix if requested
        auto_fixed_content = None
        diff = None
        if auto_fix and violations:
            auto_fixed_content = self._auto_fix(doc_content, violations)
            if dry_run and auto_fixed_content != doc_content:
                diff = self._generate_diff(doc_content, auto_fixed_content)

        # 8. Build metadata
        metadata = ProvenzanceMetadata(
            template_source="submodule",  # TODO: track actual source
            template_commit=None,  # TODO: get from resolver
            template_version=None,  # TODO: get from manifest
            validated_at_utc=datetime.utcnow().isoformat() + "Z",
        )

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            auto_fixed_content=auto_fixed_content,
            diff=diff,
            metadata=metadata,
            completeness=completeness,
            tier_level=tier_level.value,
        )

    # ==================== VALIDATION METHODS ====================

    def _validate_yaml_frontmatter(
        self, parsed: BasicDocumentStructure, template_id: str
    ) -> List[EnhancedViolation]:
        """Validate YAML front matter presence and schema compliance."""
        violations: List[EnhancedViolation] = []

        if not parsed.yaml_data:
            violations.append(
                EnhancedViolation(
                    type=ViolationType.MISSING_YAML_FRONTMATTER.value,
                    severity="BLOCKER",
                    field="frontmatter",
                    field_path="frontmatter",
                    message="YAML front matter is missing.",
                    suggestion="Add YAML front matter at the start of the document with --- markers.",
                    auto_fixable=True,
                    line=1,
                )
            )
            return violations

        # Validate front matter against JSON Schema (if available)
        try:
            # Load front-matter schema from manifest
            frontmatter_schema = self._get_frontmatter_schema(template_id)
            if frontmatter_schema:
                try:
                    jsonschema.validate(parsed.yaml_data, frontmatter_schema)
                except ValidationError as e:
                    # Extract field path and validator type
                    field_path = ".".join(
                        str(p) for p in e.path
                    ) or "frontmatter"
                    if not field_path.startswith("frontmatter"):
                        field_path = f"frontmatter.{field_path}"

                    violations.append(
                        EnhancedViolation(
                            type=ViolationType.YAML_SCHEMA_VALIDATION_FAILED.value,
                            severity="BLOCKER",
                            field="frontmatter",
                            field_path=field_path,
                            message=f"Front matter validation failed: {e.message}",
                            suggestion=f"Check field '{field_path}': {e.validator} constraint failed. {e.message}",
                            auto_fixable=False,
                            validator=str(e.validator) if e.validator else None,
                            line=1,
                        )
                    )
        except Exception as e:
            # Log but don't fail on schema load issues
            pass

        return violations

    def _validate_sections(
        self,
        parsed: BasicDocumentStructure,
        template_schema,
        tier_level: ValidationTier,
        doc_content: str,
    ) -> List[EnhancedViolation]:
        """Validate section presence, order, and completeness."""
        violations: List[EnhancedViolation] = []

        # Check required sections
        required_sections = getattr(template_schema, "required_sections", [])
        for section in required_sections:
            if section.name not in parsed.section_order:
                violations.append(
                    EnhancedViolation(
                        type=ViolationType.MISSING_REQUIRED_SECTION.value,
                        severity="FIXABLE",  # Will be adjusted by tier
                        field="section",
                        field_path=f"section.{section.name}",
                        message=f"Required section '{section.name}' is missing.",
                        suggestion=f"Add a ## {section.name} section to your document.",
                        auto_fixable=True,
                    )
                )

        # Check section order
        expected_order = [s.name for s in required_sections]
        actual_order = [
            s
            for s in parsed.section_order
            if any(req.name == s for req in required_sections)
        ]
        if actual_order != expected_order:
            violations.append(
                EnhancedViolation(
                    type=ViolationType.WRONG_SECTION_ORDER.value,
                    severity="FIXABLE",
                    field="section",
                    field_path="section.order",
                    message=f"Section order is incorrect. Expected: {expected_order}, got: {actual_order}",
                    suggestion="Reorder sections to match the required order.",
                    auto_fixable=True,
                    expected=str(expected_order),
                    actual=str(actual_order),
                )
            )

        return violations

    def _calculate_completeness(self, parsed: BasicDocumentStructure) -> float:
        """
        Calculate completeness as percentage of sections with substantial content.

        A section is considered "filled" if it has:
        - >50 words of content, OR
        - A table (| ... |), OR
        - A list (- or *)
        """
        if not parsed.section_order:
            return 0.0

        filled_count = 0
        for section_name in parsed.section_order:
            # Find section content between this heading and next
            section_pattern = (
                rf"## {re.escape(section_name)}\n(.*?)(?:^##|$)"
            )
            match = re.search(
                section_pattern,
                parsed.raw_content,
                re.MULTILINE | re.DOTALL,
            )
            if not match:
                continue

            section_content = match.group(1)

            # Skip content inside fenced code blocks
            cleaned_content = re.sub(
                r"```[^`]*```", "", section_content, flags=re.DOTALL
            )

            # Count words
            word_count = len(cleaned_content.split())

            # Check for tables
            has_table = "|" in cleaned_content and re.search(
                r"\|---", cleaned_content
            )

            # Check for lists
            has_list = re.search(r"\n\s*[-*]\s+", cleaned_content)

            # Section is "filled" if it has >50 words, table, or list
            if word_count > 50 or has_table or has_list:
                filled_count += 1

        return filled_count / len(parsed.section_order) if parsed.section_order else 0.0

    def _apply_tier_severity(
        self, violations: List[EnhancedViolation], tier_level: ValidationTier
    ) -> None:
        """Adjust violation severity based on tier level."""
        tier_config = self.tier_thresholds.get(
            tier_level, self.tier_thresholds[ValidationTier.TIER_2]
        )

        for violation in violations:
            if violation.severity == "FIXABLE":
                # In TIER_3, downgrade FIXABLE to WARN if auto-fixable
                if (
                    tier_level == ValidationTier.TIER_3
                    and violation.auto_fixable
                ):
                    violation.severity = "WARN"

    # ==================== AUTO-FIX METHODS ====================

    def _auto_fix(
        self,
        doc_content: str,
        violations: List[EnhancedViolation],
    ) -> str:
        """
        Attempt to auto-fix common violations.

        Returns patched content (or original if no fixes applied).
        """
        patched = doc_content

        for violation in violations:
            if not violation.auto_fixable:
                continue

            if violation.type == ViolationType.MISSING_YAML_FRONTMATTER.value:
                patched = self._fix_missing_yaml_frontmatter(patched)
            elif (
                violation.type
                == ViolationType.MISSING_REQUIRED_SECTION.value
            ):
                patched = self._fix_missing_section(
                    patched, violation.field_path
                )
            elif violation.type == ViolationType.WRONG_SECTION_ORDER.value:
                patched = self._fix_section_order(patched, violation)

        return patched

    def _fix_missing_yaml_frontmatter(self, content: str) -> str:
        """Add minimal YAML frontmatter if missing."""
        if content.startswith("---"):
            return content

        minimal_yaml = """---
templateId: unknown
project: Project
repo: org/repo
branch: main
commitSha: unknown
generator: akr-mcp-server
generatorVersion: 0.2.0
generatedAtUTC: 2026-02-24T00:00:00Z
---

"""
        return minimal_yaml + content

    def _fix_missing_section(self, content: str, field_path: str) -> str:
        """Add a stub section if missing."""
        # Extract section name from field_path: "section.Section Name"
        parts = field_path.split(".", 1)
        if len(parts) < 2:
            return content

        section_name = parts[1]
        section_stub = f"\n## {section_name}\n\nTODO: Add content for {section_name}\n"

        # Append to end of document
        return content.rstrip() + section_stub

    def _fix_section_order(
        self, content: str, violation: EnhancedViolation
    ) -> str:
        """Reorder sections to match expected order."""
        # Parse sections
        sections = {}
        pattern = r"^## (.+)$"

        for match in re.finditer(pattern, content, re.MULTILINE):
            section_name = match.group(1)
            start = match.start()
            # Find next section or end
            next_match = re.search(
                pattern, content[match.end() :], re.MULTILINE
            )
            end = (
                match.end() + next_match.start()
                if next_match
                else len(content)
            )
            sections[section_name] = content[start:end]

        # TODO: Implement intelligent reordering
        # For now, return original
        return content

    # ==================== DIFF GENERATION ====================

    def _generate_diff(self, original: str, patched: str) -> str:
        """Generate unified diff between original and patched content."""
        original_lines = original.splitlines(keepends=True)
        patched_lines = patched.splitlines(keepends=True)

        diff_lines = unified_diff(
            original_lines,
            patched_lines,
            fromfile="original",
            tofile="patched",
            lineterm="",
        )

        return "\n".join(diff_lines)

    # ==================== HELPER METHODS ====================

    def _get_frontmatter_schema(self, template_id: str) -> Optional[Dict]:
        """
        Load front-matter JSON Schema from template manifest.

        Returns the frontmatterSchema dict if available, or None.
        """
        try:
            # TODO: Load from manifest when available
            # For now, return a generic schema
            return {
                "type": "object",
                "required": [
                    "templateId",
                    "project",
                    "repo",
                    "generatedAtUTC",
                ],
                "properties": {
                    "templateId": {"type": "string"},
                    "templateVersion": {
                        "type": "string",
                        "pattern": r"^\d+\.\d+\.\d+$",
                    },
                    "project": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 200,
                    },
                    "repo": {
                        "type": "string",
                        "pattern": r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$",
                    },
                    "branch": {"type": "string"},
                    "commitSha": {
                        "type": "string",
                        "pattern": r"^[a-f0-9]{7,40}$",
                    },
                    "generatorVersion": {
                        "type": "string",
                        "pattern": r"^\d+\.\d+\.\d+$",
                    },
                    "generatedAtUTC": {
                        "type": "string",
                        "format": "date-time",
                    },
                },
            }
        except Exception:
            return None
