"""Unit tests for ValidationEngine."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.document_parser import BasicDocumentParser
from tools.enforcement_tool_types import Section, TemplateSchema, ViolationSeverity
from tools.validation_engine import ValidationEngine


def _schema_with_sections(names: list[str]) -> TemplateSchema:
    return TemplateSchema(
        required_sections=[
            Section(name=name, heading_level=2, required=True, order_index=i)
            for i, name in enumerate(names)
        ]
    )


def test_check_yaml_frontmatter_detects_missing_yaml():
    engine = ValidationEngine()
    violations = engine.check_yaml_frontmatter({})

    assert violations
    assert violations[0].severity == ViolationSeverity.FIXABLE


def test_check_yaml_frontmatter_detects_missing_fields():
    engine = ValidationEngine()
    violations = engine.check_yaml_frontmatter({"feature": "Billing"})

    assert violations
    assert violations[0].severity == ViolationSeverity.BLOCKER


def test_check_required_sections_detects_missing_section():
    engine = ValidationEngine()
    schema = _schema_with_sections(["Overview", "Usage"])

    violations = engine.check_required_sections(["Overview"], schema)
    assert len(violations) == 1
    assert violations[0].severity == ViolationSeverity.BLOCKER


def test_check_section_order_detects_out_of_order():
    engine = ValidationEngine()
    schema = _schema_with_sections(["Overview", "Usage", "Dependencies"])
    sections = ["Overview", "Dependencies", "Usage"]

    violations = engine.check_section_order(sections, schema)
    assert violations
    assert violations[0].severity == ViolationSeverity.FIXABLE


def test_check_heading_hierarchy_detects_jump():
    parser = BasicDocumentParser()
    content = """
# Title
### Skipped
"""
    headings = parser.extract_headings(content)
    engine = ValidationEngine()

    violations = engine.check_heading_hierarchy(headings)
    assert violations
    assert violations[0].severity == ViolationSeverity.FIXABLE


def test_calculate_confidence():
    engine = ValidationEngine()
    violations = engine.check_yaml_frontmatter({})
    confidence = engine.calculate_confidence(violations)

    assert confidence < 1.0


def test_validate_phase1_combines_checks():
    parser = BasicDocumentParser()
    schema = _schema_with_sections(["Overview", "Usage"])
    content = """
---
feature: Billing
domain: Finance
layer: Service
component: BillingService
status: deployed
version: 1.0
componentType: Service
priority: TBD
lastUpdated: 2026-02-03
---
# Title
## Overview
## Usage
"""
    parsed = parser.parse_document(content)
    engine = ValidationEngine()

    result = engine.validate_phase1(parsed, schema)
    assert result.valid is True
    assert result.violations == []


def test_validate_phase1_missing_section_fails():
    parser = BasicDocumentParser()
    schema = _schema_with_sections(["Overview", "Usage"])
    content = """
---
feature: Billing
domain: Finance
layer: Service
component: BillingService
status: deployed
version: 1.0
componentType: Service
priority: TBD
lastUpdated: 2026-02-03
---
# Title
## Overview
"""
    parsed = parser.parse_document(content)
    engine = ValidationEngine()

    result = engine.validate_phase1(parsed, schema)
    assert result.valid is False
    assert any(v.severity == ViolationSeverity.BLOCKER for v in result.violations)
