"""Unit tests for YAMLFrontmatterGenerator."""

import sys
from datetime import date
from pathlib import Path

import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.enforcement_tool_types import FileMetadata
from tools.yaml_frontmatter_generator import YAMLFrontmatterGenerator


def test_generate_contains_required_fields():
    metadata = FileMetadata(
        file_path="src/services/billing/BillingService.cs",
        component_name="BillingService",
        feature_tag="Billing",
        domain="Finance",
    )
    generator = YAMLFrontmatterGenerator()
    yaml_block = generator.generate(metadata, "standard_service_template.md")

    assert yaml_block.startswith("---")
    assert yaml_block.endswith("---")

    parsed = yaml.safe_load(yaml_block.strip("-\n"))
    assert parsed["feature"] == "Billing"
    assert parsed["domain"] == "Finance"
    assert parsed["layer"] == "Service"
    assert parsed["component"] == "BillingService"
    assert parsed["status"] == "deployed"
    assert parsed["version"] == "1.0"
    assert parsed["componentType"] == "Service"
    assert parsed["priority"] == "TBD"
    assert parsed["lastUpdated"] == date.today().isoformat()


def test_generate_defaults_to_tbd_when_missing_metadata():
    metadata = FileMetadata(file_path="src/unknown/Thing.cs", component_name="Thing")
    generator = YAMLFrontmatterGenerator()
    yaml_block = generator.generate(metadata, "minimal_service_template.md")

    parsed = yaml.safe_load(yaml_block.strip("-\n"))
    assert parsed["feature"] == "TBD"
    assert parsed["domain"] == "TBD"
    assert parsed["layer"] == "TBD"


def test_infer_layer_from_path_common_patterns():
    generator = YAMLFrontmatterGenerator()
    assert (
        generator.infer_layer_from_path("src/controllers/UserController.cs") == "API"
    )
    assert generator.infer_layer_from_path("src/services/UserService.cs") == "Service"
    assert (
        generator.infer_layer_from_path("src/repositories/UserRepository.cs")
        == "Repository"
    )


def test_infer_component_type_from_template_name():
    generator = YAMLFrontmatterGenerator()
    assert generator.infer_component_type("standard_service_template.md") == "Service"
    assert generator.infer_component_type("ui_component_template.md") == "Component"
    assert generator.infer_component_type("table_doc_template.md") == "Table"


def test_validate_yaml_syntax_returns_errors_for_invalid_yaml():
    generator = YAMLFrontmatterGenerator()
    errors = generator.validate_yaml_syntax("feature: [unterminated")
    assert errors
