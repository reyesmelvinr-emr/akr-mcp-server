"""Unit tests for TemplateSchemaBuilder."""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.template_schema_builder import TemplateSchemaBuilder

TEMPLATES_DIR = Path(__file__).parent.parent / "akr_content" / "templates"


@pytest.mark.parametrize(
    "template_file",
    [
        "lean_baseline_service_template.md",
        "standard_service_template.md",
        "comprehensive_service_template.md",
    ],
)
def test_build_schema_from_real_templates(template_file):
    content = (TEMPLATES_DIR / template_file).read_text(encoding="utf-8")
    builder = TemplateSchemaBuilder()
    schema = builder.build_schema(template_file, content)

    assert schema.template_name == template_file
    assert schema.checksum
    assert len(schema.required_sections) > 0
    assert all(section.heading_level == 2 for section in schema.required_sections)


def test_get_required_sections_extracts_h2_headings():
    content = """
# Title

## Overview
Some text.

### Details
More text.

## Usage
"""
    builder = TemplateSchemaBuilder()
    sections = builder.get_required_sections(content)

    assert [section.name for section in sections] == ["Overview", "Usage"]
    assert [section.order_index for section in sections] == [0, 1]


def test_extract_heading_hierarchy_returns_levels():
    content = """
# Title
## Overview
### Details
#### Notes
"""
    builder = TemplateSchemaBuilder()
    hierarchy = builder.extract_heading_hierarchy(content)

    assert hierarchy["Title"] == 1
    assert hierarchy["Overview"] == 2
    assert hierarchy["Details"] == 3
    assert hierarchy["Notes"] == 4


def test_schema_cache_hits_for_same_content():
    content = """
## Overview
## Usage
"""
    builder = TemplateSchemaBuilder()
    schema_first = builder.build_schema("test.md", content)
    schema_cached = builder.get_cached_schema("test.md")
    schema_second = builder.build_schema("test.md", content)

    assert schema_cached is not None
    assert schema_first.checksum == schema_second.checksum
    assert schema_cached.checksum == schema_first.checksum


def test_schema_cache_miss_on_checksum_change():
    content_v1 = """
## Overview
## Usage
"""
    content_v2 = """
## Overview
## Usage
## Dependencies
"""
    builder = TemplateSchemaBuilder()
    schema_v1 = builder.build_schema("test.md", content_v1)
    schema_v2 = builder.build_schema("test.md", content_v2)

    assert schema_v1.checksum != schema_v2.checksum
    assert len(schema_v2.required_sections) == 3


def test_load_template_content_uses_resource_manager():
    builder = TemplateSchemaBuilder()
    content = builder.load_template_content("lean_baseline_service_template.md")

    assert content is not None
    assert "##" in content
