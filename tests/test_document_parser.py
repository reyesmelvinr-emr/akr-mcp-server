"""Unit tests for BasicDocumentParser."""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.document_parser import BasicDocumentParser


def test_parse_document_extracts_yaml_and_headings():
    content = """
---
feature: Billing
layer: Service
---
# Title
## Overview
Text
## Usage
More text
"""
    parser = BasicDocumentParser()
    result = parser.parse_document(content)

    assert result.yaml_data["feature"] == "Billing"
    assert result.yaml_data["layer"] == "Service"
    assert [h.text for h in result.headings] == ["Title", "Overview", "Usage"]
    assert result.section_order == ["Title", "Overview", "Usage"]


def test_extract_yaml_frontmatter_missing_returns_empty():
    content = "# Title\n## Overview"
    parser = BasicDocumentParser()

    yaml_data = parser.extract_yaml_frontmatter(content)
    assert yaml_data == {}


def test_extract_headings_all_levels():
    content = """
# H1
## H2
### H3
#### H4
##### H5
###### H6
"""
    parser = BasicDocumentParser()
    headings = parser.extract_headings(content)

    assert [h.level for h in headings] == [1, 2, 3, 4, 5, 6]
    assert [h.text for h in headings] == ["H1", "H2", "H3", "H4", "H5", "H6"]


def test_section_order_matches_heading_sequence():
    content = """
# Title
## First
## Second
### Child
"""
    parser = BasicDocumentParser()
    order = parser.get_section_order(content)

    assert order == ["Title", "First", "Second", "Child"]


def test_yaml_only_document():
    content = """
---
feature: Test
---
"""
    parser = BasicDocumentParser()
    result = parser.parse_document(content)

    assert result.yaml_data["feature"] == "Test"
    assert result.headings == []
    assert result.section_order == []


def test_real_template_parsing():
    templates_dir = Path(__file__).parent.parent / "akr_content" / "templates"
    template_path = templates_dir / "lean_baseline_service_template.md"
    content = template_path.read_text(encoding="utf-8")

    parser = BasicDocumentParser()
    result = parser.parse_document(content)

    assert result.raw_content
    assert len(result.headings) > 0
    assert len(result.section_order) == len(result.headings)
