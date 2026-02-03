"""
Basic document parser for Phase 1 validation.

Parses generated markdown for YAML front matter, headings, and section order
using regex-based scanning (no AST parsing).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from .enforcement_tool_types import Heading


@dataclass
class BasicDocumentStructure:
    """Parsed structure of a markdown document."""

    yaml_data: Dict[str, str] = field(default_factory=dict)
    headings: List[Heading] = field(default_factory=list)
    section_order: List[str] = field(default_factory=list)
    raw_content: str = ""


class BasicDocumentParser:
    """Regex-based parser for Phase 1 structure extraction."""

    _yaml_delimiter = re.compile(r"^---\s*$", re.MULTILINE)
    _heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    def parse_document(self, content: str) -> BasicDocumentStructure:
        """Parse markdown content into a BasicDocumentStructure."""
        yaml_data = self.extract_yaml_frontmatter(content)
        headings = self.extract_headings(content)
        section_order = self.get_section_order(content)
        return BasicDocumentStructure(
            yaml_data=yaml_data,
            headings=headings,
            section_order=section_order,
            raw_content=content,
        )

    def extract_yaml_frontmatter(self, content: str) -> Dict[str, str]:
        """Extract YAML front matter as a flat key-value dict.

        Only parses YAML if it appears at the start of the document.
        """
        lines = content.splitlines()
        if not lines:
            return {}

        start_index = 0
        while start_index < len(lines) and not lines[start_index].strip():
            start_index += 1

        if start_index >= len(lines) or lines[start_index].strip() != "---":
            return {}

        yaml_lines: list[str] = []
        for line in lines[start_index + 1 :]:
            if line.strip() == "---":
                break
            yaml_lines.append(line)

        yaml_data: Dict[str, str] = {}
        for line in yaml_lines:
            if not line.strip() or line.strip().startswith("#"):
                continue
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            yaml_data[key.strip()] = value.strip()
        return yaml_data

    def extract_headings(self, content: str) -> List[Heading]:
        """Extract headings from markdown content with line numbers."""
        headings: List[Heading] = []
        for match in self._heading_pattern.finditer(content):
            level = len(match.group(1))
            text = match.group(2).strip()
            line_number = content[: match.start()].count("\n") + 1
            headings.append(Heading(level=level, text=text, line_number=line_number))
        return headings

    def get_section_order(self, content: str) -> List[str]:
        """Return ordered list of heading titles."""
        return [heading.text for heading in self.extract_headings(content)]
