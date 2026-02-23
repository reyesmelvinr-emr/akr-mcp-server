"""Integration tests for TemplateResolver + TemplateSchemaBuilder (Phase 1)."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from resources.template_resolver import TemplateResolver
from tools.template_schema_builder import TemplateSchemaBuilder


def _create_repo_structure(base_path: Path) -> None:
    (base_path / "templates" / "core").mkdir(parents=True, exist_ok=True)
    (base_path / "akr_content" / "templates").mkdir(parents=True, exist_ok=True)


def test_schema_builder_loads_from_resolver(tmp_path: Path) -> None:
    _create_repo_structure(tmp_path)
    core_path = tmp_path / "templates" / "core"

    template_content = """
## Quick Reference (TL;DR)

## What & Why
"""
    (core_path / "lean_baseline_service_template.md").write_text(
        template_content.strip(),
        encoding="utf-8",
    )

    resolver = TemplateResolver(tmp_path, config={})
    builder = TemplateSchemaBuilder(resolver)

    content = builder.load_template_content("lean_baseline_service_template")
    assert content is not None
    assert "Quick Reference" in content

    schema = builder.build_schema("lean_baseline_service_template.md", content)
    assert schema.template_name == "lean_baseline_service_template.md"
    assert len(schema.required_sections) == 9
