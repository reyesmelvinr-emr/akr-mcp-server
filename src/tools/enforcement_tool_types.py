"""
Data structures for the Template Enforcement Tool (Phase 1).

Defines dataclasses and enums used across schema building, parsing, validation,
and file writing components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ViolationSeverity(Enum):
    """Severity tiers for validation violations."""

    BLOCKER = "BLOCKER"
    FIXABLE = "FIXABLE"
    WARN = "WARN"


@dataclass
class Section:
    """Represents a documentation section in a template schema.

    Attributes:
        name: Section title text (e.g., "Overview").
        heading_level: Markdown heading level (1-6).
        required: Whether the section is required in Phase 1 validation.
        order_index: Order of appearance in the template.
    """

    name: str
    heading_level: int
    required: bool
    order_index: int


@dataclass
class TemplateSchema:
    """Schema derived from a template markdown document.

    Attributes:
        required_sections: Ordered list of required sections.
        heading_rules: Mapping of section title to expected heading level.
        format_rules: Placeholder for future format rules (Phase 2+).
        template_name: Template filename (or identifier).
        checksum: Hash of template content used for cache validation.
    """

    required_sections: list[Section] = field(default_factory=list)
    heading_rules: dict[str, int] = field(default_factory=dict)
    format_rules: dict[str, str] = field(default_factory=dict)
    template_name: str = ""
    checksum: str = ""


@dataclass
class Heading:
    """Represents a heading found in generated markdown."""

    level: int
    text: str
    line_number: int


@dataclass
class Violation:
    """Represents a validation violation."""

    type: str
    severity: ViolationSeverity
    line: Optional[int]
    message: str
    section_name: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validation against a template schema."""

    valid: bool
    violations: list[Violation] = field(default_factory=list)
    confidence: float = 1.0
    severity_summary: dict[str, int] = field(default_factory=dict)
    corrected_markdown: Optional[str] = None
    retry_prompt: Optional[str] = None


@dataclass
class FileMetadata:
    """Metadata used for YAML front matter generation and routing."""

    file_path: str
    component_name: str
    feature_tag: Optional[str] = None
    domain: Optional[str] = None
    module_name: Optional[str] = None
    complexity: Optional[str] = None


@dataclass
class WriteResult:
    """Result of writing a validated markdown file to disk."""

    success: bool
    file_path: Optional[str] = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
