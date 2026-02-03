"""
YAML front matter generator for Phase 1 validation.

Generates deterministic YAML blocks from file metadata and template names.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import date
from typing import List

import yaml

from .enforcement_tool_types import FileMetadata


class YAMLFrontmatterGenerator:
    """Generates and validates YAML front matter blocks."""

    def generate(self, metadata: FileMetadata, template_name: str) -> str:
        """Generate YAML front matter for a document.

        Args:
            metadata: File metadata used for fields.
            template_name: Template filename used to infer component type.

        Returns:
            YAML front matter block including delimiters.
        """
        payload = {
            "feature": metadata.feature_tag or "TBD",
            "domain": metadata.domain or "TBD",
            "layer": self.infer_layer_from_path(metadata.file_path),
            "component": metadata.component_name,
            "status": "deployed",
            "version": "1.0",
            "componentType": self.infer_component_type(template_name),
            "priority": "TBD",
            "lastUpdated": date.today().isoformat(),
        }
        yaml_str = yaml.safe_dump(payload, sort_keys=False).strip()
        return f"---\n{yaml_str}\n---"

    def infer_layer_from_path(self, file_path: str) -> str:
        """Infer documentation layer based on file path conventions."""
        lowered = file_path.lower().replace("\\", "/")
        mapping = [
            ("/controllers/", "API"),
            ("/controller/", "API"),
            ("/services/", "Service"),
            ("/service/", "Service"),
            ("/repositories/", "Repository"),
            ("/repository/", "Repository"),
            ("/data/", "Data"),
            ("/models/", "Model"),
            ("/ui/", "UI"),
        ]
        for token, layer in mapping:
            if token in lowered:
                return layer
        return "TBD"

    def infer_component_type(self, template_name: str) -> str:
        """Infer component type from template name."""
        lowered = template_name.lower()
        if "service" in lowered:
            return "Service"
        if "ui" in lowered or "component" in lowered:
            return "Component"
        if "table" in lowered:
            return "Table"
        if "database" in lowered:
            return "Database"
        return "TBD"

    def validate_yaml_syntax(self, yaml_str: str) -> List[str]:
        """Validate YAML syntax, returning list of errors if any."""
        try:
            yaml.safe_load(yaml_str)
            return []
        except yaml.YAMLError as exc:
            return [str(exc)]
