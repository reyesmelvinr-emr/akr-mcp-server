"""
Section Updater Module

Provides surgical update capabilities for existing documentation.
Parses markdown sections and enables targeted updates while preserving
human-authored content.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger("akr-mcp-server.tools.section_updater")


class SectionType(Enum):
    """Types of sections that can be identified in documentation."""
    HEADER = "header"
    OVERVIEW = "overview"
    CONFIGURATION = "configuration"
    PARAMETERS = "parameters"
    DEPENDENCIES = "dependencies"
    METHODS = "methods"
    API_ENDPOINTS = "api_endpoints"
    EXAMPLES = "examples"
    ERROR_HANDLING = "error_handling"
    RELATED_DOCUMENTATION = "related_documentation"
    CHANGELOG = "changelog"
    CUSTOM = "custom"


@dataclass
class Section:
    """Represents a parsed section of documentation."""
    id: str
    title: str
    level: int  # Heading level (1-6)
    content: str
    start_line: int
    end_line: int
    section_type: SectionType
    is_ai_generated: bool = False
    needs_human_input: bool = False


@dataclass
class UpdateResult:
    """Result of a section update operation."""
    success: bool
    section_id: str
    section_title: str
    action: str  # "updated", "added", "preserved"
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    message: str = ""


class MarkdownSectionParser:
    """
    Parses markdown documents into structured sections.
    
    Features:
    - Identifies heading hierarchy
    - Detects AI-generated markers
    - Detects "needs human input" markers
    - Maps sections to standard types
    """
    
    # Section title patterns for classification
    SECTION_PATTERNS = {
        SectionType.OVERVIEW: r'^(overview|introduction|summary|description)$',
        SectionType.CONFIGURATION: r'^(configuration|settings|config|environment)$',
        SectionType.PARAMETERS: r'^(parameters|props|properties|inputs|arguments)$',
        SectionType.DEPENDENCIES: r'^(dependencies|requirements|prerequisites)$',
        SectionType.METHODS: r'^(methods|functions|api|interface|public\s+methods)$',
        SectionType.API_ENDPOINTS: r'^(api\s*endpoints?|endpoints?|routes?)$',
        SectionType.EXAMPLES: r'^(examples?|usage|samples?|code\s+examples?)$',
        SectionType.ERROR_HANDLING: r'^(error\s*handling|errors|exceptions)$',
        SectionType.RELATED_DOCUMENTATION: r'^(related|see\s+also|references|links)$',
        SectionType.CHANGELOG: r'^(changelog|history|changes|version\s+history)$',
    }
    
    AI_MARKER = "🤖"
    HUMAN_NEEDED_MARKER = "❓"
    
    def __init__(self, content: str):
        """Initialize parser with markdown content."""
        self.content = content
        self.lines = content.split('\n')
        self.sections: list[Section] = []
    
    def parse(self) -> list[Section]:
        """
        Parse the markdown content into sections.
        
        Returns:
            List of Section objects
        """
        self.sections = []
        current_section = None
        section_lines = []
        
        for i, line in enumerate(self.lines):
            # Check for heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if heading_match:
                # Save previous section
                if current_section:
                    current_section.content = '\n'.join(section_lines)
                    current_section.end_line = i - 1
                    self.sections.append(current_section)
                
                # Start new section
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                
                current_section = Section(
                    id=self._generate_id(title),
                    title=title,
                    level=level,
                    content="",
                    start_line=i,
                    end_line=i,
                    section_type=self._classify_section(title),
                    is_ai_generated=self.AI_MARKER in title,
                    needs_human_input=self.HUMAN_NEEDED_MARKER in title
                )
                section_lines = []
            else:
                section_lines.append(line)
                
                # Check for markers in content
                if current_section:
                    if self.AI_MARKER in line:
                        current_section.is_ai_generated = True
                    if self.HUMAN_NEEDED_MARKER in line:
                        current_section.needs_human_input = True
        
        # Save last section
        if current_section:
            current_section.content = '\n'.join(section_lines)
            current_section.end_line = len(self.lines) - 1
            self.sections.append(current_section)
        
        return self.sections
    
    def _generate_id(self, title: str) -> str:
        """Generate a URL-friendly ID from title."""
        # Remove markers
        clean_title = title.replace(self.AI_MARKER, '').replace(self.HUMAN_NEEDED_MARKER, '')
        # Convert to lowercase and replace spaces/special chars
        return re.sub(r'[^a-z0-9]+', '-', clean_title.lower()).strip('-')
    
    def _classify_section(self, title: str) -> SectionType:
        """Classify section type based on title."""
        clean_title = title.replace(self.AI_MARKER, '').replace(self.HUMAN_NEEDED_MARKER, '').strip().lower()
        
        for section_type, pattern in self.SECTION_PATTERNS.items():
            if re.match(pattern, clean_title, re.IGNORECASE):
                return section_type
        
        return SectionType.CUSTOM
    
    def get_section(self, section_id: str) -> Optional[Section]:
        """Get a section by ID."""
        for section in self.sections:
            if section.id == section_id:
                return section
        return None
    
    def get_sections_by_type(self, section_type: SectionType) -> list[Section]:
        """Get all sections of a specific type."""
        return [s for s in self.sections if s.section_type == section_type]
    
    def get_ai_generated_sections(self) -> list[Section]:
        """Get all AI-generated sections."""
        return [s for s in self.sections if s.is_ai_generated]
    
    def get_sections_needing_input(self) -> list[Section]:
        """Get all sections marked as needing human input."""
        return [s for s in self.sections if s.needs_human_input]


class SurgicalUpdater:
    """
    Performs surgical updates to documentation sections.
    
    Features:
    - Updates only AI-generated sections
    - Preserves human-authored content
    - Adds changelog entries for updates
    - Validates section existence before updates
    """
    
    def __init__(self, content: str):
        """Initialize with document content."""
        self.content = content
        self.parser = MarkdownSectionParser(content)
        self.sections = self.parser.parse()
        self.updates: list[UpdateResult] = []
    
    def analyze_impact(self, proposed_sections: dict[str, str]) -> dict:
        """
        Analyze the impact of proposed section updates.
        
        Args:
            proposed_sections: Dict of section_id -> new_content
            
        Returns:
            Analysis of what would be updated/preserved/added
        """
        analysis = {
            "sections_to_update": [],
            "sections_to_add": [],
            "sections_preserved": [],
            "warnings": [],
            "total_sections": len(self.sections)
        }
        
        existing_ids = {s.id for s in self.sections}
        
        for section_id, new_content in proposed_sections.items():
            section = self.parser.get_section(section_id)
            
            if section:
                if section.is_ai_generated:
                    analysis["sections_to_update"].append({
                        "id": section_id,
                        "title": section.title,
                        "current_lines": section.end_line - section.start_line,
                        "ai_generated": True
                    })
                else:
                    analysis["sections_preserved"].append({
                        "id": section_id,
                        "title": section.title,
                        "reason": "Human-authored content - not modifiable"
                    })
                    analysis["warnings"].append(
                        f"Section '{section.title}' appears to be human-authored and will not be updated"
                    )
            else:
                analysis["sections_to_add"].append({
                    "id": section_id,
                    "proposed_title": self._id_to_title(section_id)
                })
        
        return analysis
    
    def update_section(self, section_id: str, new_content: str, 
                       force: bool = False) -> UpdateResult:
        """
        Update a specific section.
        
        Args:
            section_id: ID of section to update
            new_content: New content for the section
            force: Force update even if not AI-generated (use with caution)
            
        Returns:
            UpdateResult with details of the operation
        """
        section = self.parser.get_section(section_id)
        
        if not section:
            return UpdateResult(
                success=False,
                section_id=section_id,
                section_title="",
                action="not_found",
                message=f"Section '{section_id}' not found in document"
            )
        
        # Check if section can be updated
        if not section.is_ai_generated and not force:
            return UpdateResult(
                success=False,
                section_id=section_id,
                section_title=section.title,
                action="preserved",
                old_content=section.content,
                message=f"Section '{section.title}' is human-authored. Use force=true to override."
            )
        
        # Perform update
        old_content = section.content
        section.content = new_content
        
        result = UpdateResult(
            success=True,
            section_id=section_id,
            section_title=section.title,
            action="updated",
            old_content=old_content,
            new_content=new_content,
            message=f"Section '{section.title}' updated successfully"
        )
        
        self.updates.append(result)
        return result
    
    def add_section(self, title: str, content: str, 
                    after_section_id: Optional[str] = None,
                    level: int = 2) -> UpdateResult:
        """
        Add a new section to the document.
        
        Args:
            title: Section title
            content: Section content
            after_section_id: ID of section to insert after (or end if None)
            level: Heading level (1-6)
            
        Returns:
            UpdateResult with details
        """
        section_id = MarkdownSectionParser("")._generate_id(title)
        
        # Check if section already exists
        if self.parser.get_section(section_id):
            return UpdateResult(
                success=False,
                section_id=section_id,
                section_title=title,
                action="exists",
                message=f"Section '{title}' already exists"
            )
        
        # Create new section with AI marker
        new_section = Section(
            id=section_id,
            title=f"🤖 {title}",
            level=level,
            content=content,
            start_line=-1,
            end_line=-1,
            section_type=SectionType.CUSTOM,
            is_ai_generated=True
        )
        
        # Find insertion point
        if after_section_id:
            insert_idx = None
            for i, s in enumerate(self.sections):
                if s.id == after_section_id:
                    insert_idx = i + 1
                    break
            if insert_idx:
                self.sections.insert(insert_idx, new_section)
            else:
                self.sections.append(new_section)
        else:
            self.sections.append(new_section)
        
        result = UpdateResult(
            success=True,
            section_id=section_id,
            section_title=title,
            action="added",
            new_content=content,
            message=f"Section '{title}' added successfully"
        )
        
        self.updates.append(result)
        return result
    
    def generate_updated_content(self, add_changelog: bool = True) -> str:
        """
        Generate the updated document content.
        
        Args:
            add_changelog: Add/update changelog section with update info
            
        Returns:
            Updated document content as string
        """
        lines = []
        
        for section in self.sections:
            # Add heading
            heading = "#" * section.level + " " + section.title
            lines.append(heading)
            
            # Add content
            lines.append(section.content)
            lines.append("")  # Blank line after section
        
        # Add changelog entry if requested
        if add_changelog and self.updates:
            lines.append(self._generate_changelog_entry())
        
        return '\n'.join(lines)
    
    def _generate_changelog_entry(self) -> str:
        """Generate a changelog entry for recent updates."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entries = []
        for update in self.updates:
            entries.append(f"  - {update.action.capitalize()}: {update.section_title}")
        
        return f"""
## 🤖 Changelog

### {timestamp} - AI Update
{chr(10).join(entries)}
"""
    
    def _id_to_title(self, section_id: str) -> str:
        """Convert section ID back to a title format."""
        return section_id.replace('-', ' ').title()


def analyze_documentation_impact(
    file_path: str,
    proposed_updates: dict[str, str]
) -> dict:
    """
    Analyze the impact of proposed documentation updates.
    
    Args:
        file_path: Path to the documentation file
        proposed_updates: Dict of section_id -> new_content
        
    Returns:
        Impact analysis
    """
    path = Path(file_path)
    
    if not path.exists():
        return {
            "success": False,
            "error": f"File not found: {file_path}",
            "file_exists": False
        }
    
    try:
        content = path.read_text(encoding='utf-8')
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read file: {e}"
        }
    
    updater = SurgicalUpdater(content)
    analysis = updater.analyze_impact(proposed_updates)
    
    return {
        "success": True,
        "file_path": str(file_path),
        **analysis,
        "sections_in_document": [
            {
                "id": s.id,
                "title": s.title,
                "type": s.section_type.value,
                "is_ai_generated": s.is_ai_generated,
                "needs_human_input": s.needs_human_input,
                "line_range": f"{s.start_line}-{s.end_line}"
            }
            for s in updater.sections
        ]
    }


def update_documentation_sections(
    file_path: str,
    section_updates: dict[str, str],
    add_changelog: bool = True,
    dry_run: bool = False
) -> dict:
    """
    Perform surgical updates to documentation sections.
    
    Args:
        file_path: Path to the documentation file
        section_updates: Dict of section_id -> new_content
        add_changelog: Add changelog entry for updates
        dry_run: If True, returns preview without writing
        
    Returns:
        Update results
    """
    path = Path(file_path)
    
    if not path.exists():
        return {
            "success": False,
            "error": f"File not found: {file_path}",
            "file_exists": False
        }
    
    try:
        content = path.read_text(encoding='utf-8')
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read file: {e}"
        }
    
    updater = SurgicalUpdater(content)
    
    # Perform updates
    results = []
    for section_id, new_content in section_updates.items():
        result = updater.update_section(section_id, new_content)
        results.append({
            "section_id": result.section_id,
            "section_title": result.section_title,
            "action": result.action,
            "success": result.success,
            "message": result.message
        })
    
    # Generate updated content
    updated_content = updater.generate_updated_content(add_changelog)
    
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "file_path": str(file_path),
            "updates": results,
            "preview_length": len(updated_content),
            "preview_lines": updated_content.count('\n') + 1,
            "message": "Dry run - no changes written"
        }
    
    # Write updated content
    try:
        path.write_text(updated_content, encoding='utf-8')
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to write file: {e}",
            "updates": results
        }
    
    return {
        "success": True,
        "file_path": str(file_path),
        "updates": results,
        "sections_updated": sum(1 for r in results if r["action"] == "updated"),
        "sections_preserved": sum(1 for r in results if r["action"] == "preserved"),
        "sections_not_found": sum(1 for r in results if r["action"] == "not_found"),
        "message": "Documentation updated successfully"
    }


def get_document_structure(file_path: str) -> dict:
    """
    Get the structure of a documentation file.
    
    Args:
        file_path: Path to the documentation file
        
    Returns:
        Document structure information
    """
    path = Path(file_path)
    
    if not path.exists():
        return {
            "success": False,
            "error": f"File not found: {file_path}"
        }
    
    try:
        content = path.read_text(encoding='utf-8')
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read file: {e}"
        }
    
    parser = MarkdownSectionParser(content)
    sections = parser.parse()
    
    return {
        "success": True,
        "file_path": str(file_path),
        "total_sections": len(sections),
        "ai_generated_sections": len(parser.get_ai_generated_sections()),
        "sections_needing_input": len(parser.get_sections_needing_input()),
        "sections": [
            {
                "id": s.id,
                "title": s.title,
                "level": s.level,
                "type": s.section_type.value,
                "is_ai_generated": s.is_ai_generated,
                "needs_human_input": s.needs_human_input,
                "start_line": s.start_line,
                "end_line": s.end_line,
                "content_length": len(s.content)
            }
            for s in sections
        ],
        "section_types_found": list(set(s.section_type.value for s in sections))
    }
