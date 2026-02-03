"""
Template schema builder for Phase 1 validation.

Parses template markdown to derive required sections and heading hierarchy.
Includes in-memory caching with checksum validation.
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass
from typing import Optional

from resources.akr_resources import AKRResourceManager
from .enforcement_tool_types import Section, TemplateSchema


@dataclass
class _SchemaCacheEntry:
    """Internal cache entry for template schemas."""

    schema: TemplateSchema
    cached_at: float


class TemplateSchemaBuilder:
    """Builds and caches template schemas from markdown templates."""

    def __init__(self, resource_manager: Optional[AKRResourceManager] = None):
        self._resource_manager = resource_manager or AKRResourceManager()
        self._schema_cache: dict[str, _SchemaCacheEntry] = {}

    def build_schema(self, template_name: str, template_content: str) -> TemplateSchema:
        """Build schema from template markdown content.

        Args:
            template_name: Template filename or identifier.
            template_content: Full markdown content of the template.

        Returns:
            TemplateSchema derived from the template content.
        """
        checksum = self._calculate_checksum(template_content)
        cached = self._schema_cache.get(template_name)
        if cached and cached.schema.checksum == checksum:
            return cached.schema

        required_sections = self.get_required_sections(template_content)
        heading_rules = self.extract_heading_hierarchy(template_content)
        schema = TemplateSchema(
            required_sections=required_sections,
            heading_rules=heading_rules,
            format_rules={},
            template_name=template_name,
            checksum=checksum,
        )
        self.cache_schema(template_name, schema)
        return schema

    def get_required_sections(self, template_content: str) -> list[Section]:
        """Extract required sections based on H2 headings (Phase 1).

        Args:
            template_content: Template markdown content.

        Returns:
            Ordered list of required sections.
        """
        sections: list[Section] = []
        heading_pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)

        for index, match in enumerate(heading_pattern.finditer(template_content)):
            section_name = match.group(1).strip()
            sections.append(
                Section(
                    name=section_name,
                    heading_level=2,
                    required=True,
                    order_index=index,
                )
            )
        return sections

    def extract_heading_hierarchy(self, template_content: str) -> dict[str, int]:
        """Extract heading hierarchy from template markdown.

        Args:
            template_content: Template markdown content.

        Returns:
            Mapping of heading text to heading level.
        """
        heading_rules: dict[str, int] = {}
        heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

        for match in heading_pattern.finditer(template_content):
            level = len(match.group(1))
            title = match.group(2).strip()
            if title not in heading_rules:
                heading_rules[title] = level
        return heading_rules

    def cache_schema(self, template_name: str, schema: TemplateSchema) -> None:
        """Cache a schema with timestamp."""
        self._schema_cache[template_name] = _SchemaCacheEntry(
            schema=schema, cached_at=time.time()
        )

    def get_cached_schema(self, template_name: str) -> Optional[TemplateSchema]:
        """Get cached schema by template name if available."""
        cached = self._schema_cache.get(template_name)
        return cached.schema if cached else None

    def load_template_content(self, template_name: str) -> Optional[str]:
        """Load template content using AKRResourceManager."""
        return self._resource_manager.get_resource_content("template", template_name)

    @staticmethod
    def _calculate_checksum(content: str) -> str:
        """Calculate SHA-256 checksum for cache validation."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
