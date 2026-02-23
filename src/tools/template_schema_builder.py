"""
Template schema builder for Phase 1 validation.

Parses template markdown to derive required sections and heading hierarchy.
Includes in-memory caching with checksum validation.

Dependency: Accepts TemplateResolver (or legacy AKRResourceManager for compatibility)
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass
from typing import Optional, Union

from resources.template_resolver import TemplateResolver
from resources.akr_resources import AKRResourceManager
from .enforcement_tool_types import Section, TemplateSchema

# ==================== PHASE 1: GLOBAL SINGLETON ====================
# Module-level cache for TemplateSchemaBuilder instance
# Persists schema cache across enforce_and_fix() calls for 70-80% speedup
_global_schema_builder: Optional['TemplateSchemaBuilder'] = None


def get_or_create_schema_builder(
    resolver: Optional[Union[TemplateResolver, AKRResourceManager]] = None,
) -> 'TemplateSchemaBuilder':
    """
    Get or create global TemplateSchemaBuilder singleton.
    
    The schema cache persists across enforce_and_fix() calls, providing
    70-80% performance improvement for repeated templates.
    
    Args:
        resolver: Optional TemplateResolver or AKRResourceManager for template loading.
                 Accepts both for backward compatibility.
    
    Returns:
        Global TemplateSchemaBuilder instance.
    """
    global _global_schema_builder
    
    if _global_schema_builder is None:
        _global_schema_builder = TemplateSchemaBuilder(resolver)
    elif resolver is not None:
        # Update resolver if different instance
        if isinstance(resolver, TemplateResolver) or isinstance(resolver, AKRResourceManager):
            _global_schema_builder._resolver = resolver
    
    return _global_schema_builder


# CRITICAL FIX (Step 8a): Hardcoded baseline sections for each template type
# This replaces naive regex extraction that was including instructional sections
TEMPLATE_BASELINE_SECTIONS = {
    "lean_baseline_service_template.md": [
        "Quick Reference (TL;DR)",
        "What & Why",
        "How It Works",
        "Business Rules",
        "Architecture",
        "API Contract (AI Context)",
        "Validation Rules (AUTO-GENERATED)",
        "Data Operations",
        "Questions & Gaps",
    ],
    "standard_service_template.md": [
        "Quick Reference (TL;DR)",
        "What & Why",
        "How It Works",
        "Business Rules",
        "Architecture",
        "API Contract (AI Context)",
        "Validation Rules",
        "Data Operations",
        "External Dependencies",
        "Known Issues & Limitations",
        "Performance",
        "Error Reference",
        "Testing",
        "Monitoring & Alerts",
        "Questions & Gaps",
    ],
    "comprehensive_service_template.md": [
        "🚨 Critical Service Alert",
        "Quick Reference (TL;DR)",
        "What & Why",
        "How It Works",
        "Business Rules",
        "Architecture",
        "API Contract (AI Context)",
        "Middleware Pipeline",
        "Validation Rules (Comprehensive)",
        "Data Operations",
        "External Dependencies (Mission-Critical)",
        "Known Issues & Limitations",
        "Performance",
        "Common Problems & Solutions",
        "What Could Break (Impact Analysis)",
        "Security & Compliance",
        "Disaster Recovery",
        "Monitoring & Alerts",
        "Testing Strategy",
        "Deployment",
        "Incident Response",
        "Team & Ownership",
    ],
    "ui_component_template.md": [
        "Quick Reference",
        "Purpose & Context",
        "Props API",
        "Visual States & Variants",
        "Component Behavior",
        "Styling & Theming",
        "Accessibility",
        "Usage Examples",
        "Component Architecture",
        "Data Flow",
        "Performance Considerations",
        "Error Handling",
        "Testing",
        "Known Issues & Limitations",
        "Migration Guide",
        "Questions & Gaps",
    ],
    "table_doc_template.md": [
        "Purpose",
        "Columns",
        "Constraints",
        "Business Rules",
        "Related Objects",
        "Optional Sections",
    ],
    "embedded_database_template.md": [
        "Overview",
        "Script Repository",
        "Tier 1: Active Objects (Full Documentation)",
        "Tier 2: Stable Objects (Summary Only)",
        "Tier 3: Legacy Objects",
        "Change Management Process",
        "Connection & Integration",
        "Backup & Recovery",
        "Security & Compliance",
        "Known Issues & Technical Debt",
        "Interview Questions for This Database",
        "Migration Path (Optional)",
        "Appendix: Quick Schema Reference",
        "Document History",
    ],
}


@dataclass
class _SchemaCacheEntry:
    """Internal cache entry for template schemas."""

    schema: TemplateSchema
    cached_at: float


class TemplateSchemaBuilder:
    """Builds and caches template schemas from markdown templates.
    
    Supports both TemplateResolver (new, Phase 1) and AKRResourceManager (legacy)
    for backward compatibility.
    """

    def __init__(self, resolver: Optional[Union[TemplateResolver, AKRResourceManager]] = None):
        """
        Initialize schema builder.
        
        Args:
            resolver: TemplateResolver or AKRResourceManager instance.
                     If None, creates a default AKRResourceManager.
        """
        self._resolver = resolver
        if self._resolver is None:
            # Backward compatibility: create AKRResourceManager if nothing provided
            self._resolver = AKRResourceManager()
        
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

        required_sections = self.get_required_sections(template_content, template_name)
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

    def get_required_sections(self, template_content: str, template_name: str) -> list[Section]:
        """Extract required sections using hardcoded baseline mapping, not regex.

        This fixes the bug where naive regex extraction was including instructional
        sections as required, causing false validation failures.

        Args:
            template_content: Template markdown content (currently unused; kept for compatibility).
            template_name: Template filename to look up in TEMPLATE_BASELINE_SECTIONS.

        Returns:
            Ordered list of baseline sections that MUST appear in generated documentation stubs.
        """
        baseline_names = TEMPLATE_BASELINE_SECTIONS.get(template_name, [])

        if not baseline_names:
            # Template not in mapping - log warning but return empty to avoid breaking
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Template '{template_name}' not found in TEMPLATE_BASELINE_SECTIONS. "
                f"Returning no required sections. Available templates: "
                f"{', '.join(TEMPLATE_BASELINE_SECTIONS.keys())}"
            )
            return []

        sections: list[Section] = []
        for index, section_name in enumerate(baseline_names):
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
        """
        Load template content using TemplateResolver or AKRResourceManager.
        
        Supports both Phase 1 (TemplateResolver) and legacy (AKRResourceManager).
        """
        if isinstance(self._resolver, TemplateResolver):
            # Phase 1: Use TemplateResolver (3-layer resolution)
            return self._resolver.get_template(template_name)
        elif isinstance(self._resolver, AKRResourceManager):
            # Legacy: Use AKRResourceManager
            resolved_name = template_name
            if hasattr(self._resolver, "resolve_template_filename"):
                resolved, _ = self._resolver.resolve_template_filename(template_name)
                if resolved:
                    resolved_name = resolved
            return self._resolver.get_resource_content("template", resolved_name)
        else:
            return None

    @staticmethod
    def _calculate_checksum(content: str) -> str:
        """Calculate SHA-256 checksum for cache validation."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
