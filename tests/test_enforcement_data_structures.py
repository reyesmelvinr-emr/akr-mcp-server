"""Unit tests for enforcement tool data structures."""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.enforcement_tool_types import (
    FileMetadata,
    Heading,
    Section,
    TemplateSchema,
    ValidationResult,
    Violation,
    ViolationSeverity,
    WriteResult,
)


def test_section_dataclass_instantiation():
    section = Section(name="Overview", heading_level=2, required=True, order_index=0)
    assert section.name == "Overview"
    assert section.heading_level == 2
    assert section.required is True
    assert section.order_index == 0


def test_template_schema_defaults():
    schema = TemplateSchema(template_name="template.md", checksum="abc")
    assert schema.required_sections == []
    assert schema.heading_rules == {}
    assert schema.format_rules == {}
    assert schema.template_name == "template.md"
    assert schema.checksum == "abc"


def test_heading_dataclass_instantiation():
    heading = Heading(level=2, text="Overview", line_number=10)
    assert heading.level == 2
    assert heading.text == "Overview"
    assert heading.line_number == 10


def test_violation_dataclass_instantiation():
    violation = Violation(
        type="missing_section",
        severity=ViolationSeverity.BLOCKER,
        line=5,
        message="Missing required section",
        section_name="Overview",
    )
    assert violation.type == "missing_section"
    assert violation.severity == ViolationSeverity.BLOCKER
    assert violation.line == 5
    assert violation.section_name == "Overview"


def test_validation_result_defaults():
    result = ValidationResult(valid=True)
    assert result.valid is True
    assert result.violations == []
    assert result.confidence == 1.0
    assert result.severity_summary == {}
    assert result.corrected_markdown is None
    assert result.retry_prompt is None


def test_file_metadata_defaults():
    metadata = FileMetadata(file_path="src/foo.py", component_name="Foo")
    assert metadata.file_path == "src/foo.py"
    assert metadata.component_name == "Foo"
    assert metadata.feature_tag is None
    assert metadata.domain is None
    assert metadata.module_name is None
    assert metadata.complexity is None


def test_write_result_defaults():
    result = WriteResult(success=True, file_path="docs/foo.md")
    assert result.success is True
    assert result.file_path == "docs/foo.md"
    assert result.errors == []
    assert result.warnings == []


def test_violation_severity_enum_values():
    assert ViolationSeverity.BLOCKER.value == "BLOCKER"
    assert ViolationSeverity.FIXABLE.value == "FIXABLE"
    assert ViolationSeverity.WARN.value == "WARN"


@pytest.mark.parametrize("severity", list(ViolationSeverity))
def test_violation_severity_enum_iterable(severity):
    assert isinstance(severity.value, str)
