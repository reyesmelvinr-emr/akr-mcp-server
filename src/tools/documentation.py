"""
Documentation Tools Module

Provides MCP tools for template listing, selection, and documentation generation support.
These tools help Copilot understand what documentation templates are available and
recommend appropriate templates based on file types.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger("akr-mcp-server.tools.documentation")


class ProjectType(Enum):
    """Project types for documentation templates."""
    BACKEND = "backend"
    UI = "ui"
    DATABASE = "database"
    GENERAL = "general"


class TemplateComplexity(Enum):
    """Complexity levels for documentation templates."""
    MINIMAL = "minimal"
    LEAN = "lean"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


@dataclass
class TemplateMetadata:
    """
    Metadata for a documentation template.
    
    Attributes:
        name: Template filename (without path)
        display_name: Human-readable name
        description: What this template is for
        project_type: Backend, UI, Database, or General
        complexity: Minimal, Lean, Standard, or Comprehensive
        use_cases: List of when to use this template
        file_extensions: File extensions this template is suited for
        required_sections: List of required section names
        uri: MCP resource URI for this template
    """
    name: str
    display_name: str
    description: str
    project_type: ProjectType
    complexity: TemplateComplexity
    use_cases: list[str] = field(default_factory=list)
    file_extensions: list[str] = field(default_factory=list)
    required_sections: list[str] = field(default_factory=list)
    uri: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "displayName": self.display_name,
            "description": self.description,
            "projectType": self.project_type.value,
            "complexity": self.complexity.value,
            "useCases": self.use_cases,
            "fileExtensions": self.file_extensions,
            "requiredSections": self.required_sections,
            "uri": self.uri
        }


# Template metadata registry
# This defines all available templates and their characteristics
TEMPLATE_REGISTRY: dict[str, TemplateMetadata] = {
    "comprehensive_service_template.md": TemplateMetadata(
        name="comprehensive_service_template.md",
        display_name="Comprehensive Service Template",
        description="Full-featured documentation template with all sections for complex services. Use when you need thorough documentation including architecture diagrams, sequence flows, and detailed API specifications.",
        project_type=ProjectType.BACKEND,
        complexity=TemplateComplexity.COMPREHENSIVE,
        use_cases=[
            "Complex services with multiple dependencies",
            "Public APIs requiring detailed documentation",
            "Services with complex business logic",
            "New team member onboarding documentation",
            "Architecture decision records"
        ],
        file_extensions=[".cs", ".java", ".py", ".ts", ".js", ".go"],
        required_sections=[
            "Service Overview",
            "Architecture",
            "Dependencies",
            "API Reference",
            "Data Models",
            "Error Handling",
            "Configuration",
            "Testing",
            "Deployment"
        ],
        uri="akr://template/comprehensive_service_template.md"
    ),
    
    "standard_service_template.md": TemplateMetadata(
        name="standard_service_template.md",
        display_name="Standard Service Template",
        description="Balanced documentation template for most backend services. Covers essential sections without overwhelming detail. Recommended default for most services.",
        project_type=ProjectType.BACKEND,
        complexity=TemplateComplexity.STANDARD,
        use_cases=[
            "Most backend services",
            "Services with moderate complexity",
            "Internal APIs and services",
            "Standard CRUD operations",
            "Microservices"
        ],
        file_extensions=[".cs", ".java", ".py", ".ts", ".js", ".go"],
        required_sections=[
            "Service Overview",
            "Dependencies",
            "Public Methods",
            "Data Models",
            "Configuration",
            "Usage Examples"
        ],
        uri="akr://template/standard_service_template.md"
    ),
    
    "lean_baseline_service_template.md": TemplateMetadata(
        name="lean_baseline_service_template.md",
        display_name="Lean Baseline Service Template",
        description="Lightweight documentation template for simpler services. Focuses on essential information with minimal overhead. Good for utility classes and helper services.",
        project_type=ProjectType.BACKEND,
        complexity=TemplateComplexity.LEAN,
        use_cases=[
            "Simple utility services",
            "Helper classes",
            "Wrapper services",
            "Internal tools",
            "Quick documentation needs"
        ],
        file_extensions=[".cs", ".java", ".py", ".ts", ".js", ".go"],
        required_sections=[
            "Overview",
            "Public Methods",
            "Dependencies",
            "Usage"
        ],
        uri="akr://template/lean_baseline_service_template.md"
    ),
    
    "minimal_service_template.md": TemplateMetadata(
        name="minimal_service_template.md",
        display_name="Minimal Service Template",
        description="Ultra-minimal documentation for very simple components. Just the basics: what it does and how to use it. Use for trivial classes or when time is extremely limited.",
        project_type=ProjectType.BACKEND,
        complexity=TemplateComplexity.MINIMAL,
        use_cases=[
            "Very simple classes",
            "Single-purpose utilities",
            "Temporary documentation",
            "Proof of concept code",
            "Time-constrained situations"
        ],
        file_extensions=[".cs", ".java", ".py", ".ts", ".js", ".go"],
        required_sections=[
            "Overview",
            "Usage"
        ],
        uri="akr://template/minimal_service_template.md"
    ),
    
    "table_doc_template.md": TemplateMetadata(
        name="table_doc_template.md",
        display_name="Database Table Template",
        description="Documentation template for database tables and schemas. Covers table structure, relationships, indexes, and data dictionary information.",
        project_type=ProjectType.DATABASE,
        complexity=TemplateComplexity.STANDARD,
        use_cases=[
            "Database table documentation",
            "Schema documentation",
            "Data dictionary entries",
            "Entity documentation",
            "Migration documentation"
        ],
        file_extensions=[".sql", ".ddl"],
        required_sections=[
            "Table Overview",
            "Columns",
            "Primary Key",
            "Foreign Keys",
            "Indexes",
            "Relationships",
            "Sample Data"
        ],
        uri="akr://template/table_doc_template.md"
    ),
    
    "ui_component_template.md": TemplateMetadata(
        name="ui_component_template.md",
        display_name="UI Component Template",
        description="Documentation template for UI components and frontend elements. Covers props, state, events, styling, and accessibility considerations.",
        project_type=ProjectType.UI,
        complexity=TemplateComplexity.STANDARD,
        use_cases=[
            "React components",
            "Angular components",
            "Vue components",
            "Web components",
            "UI library components",
            "Reusable frontend elements"
        ],
        file_extensions=[".tsx", ".jsx", ".vue", ".svelte", ".html", ".razor"],
        required_sections=[
            "Component Overview",
            "Props/Inputs",
            "State",
            "Events/Outputs",
            "Styling",
            "Accessibility",
            "Usage Examples"
        ],
        uri="akr://template/ui_component_template.md"
    )
}


# File extension to project type mapping
EXTENSION_TO_PROJECT_TYPE: dict[str, ProjectType] = {
    # Backend extensions
    ".cs": ProjectType.BACKEND,
    ".java": ProjectType.BACKEND,
    ".py": ProjectType.BACKEND,
    ".go": ProjectType.BACKEND,
    ".rb": ProjectType.BACKEND,
    ".php": ProjectType.BACKEND,
    ".rs": ProjectType.BACKEND,
    
    # UI extensions
    ".tsx": ProjectType.UI,
    ".jsx": ProjectType.UI,
    ".vue": ProjectType.UI,
    ".svelte": ProjectType.UI,
    ".razor": ProjectType.UI,
    ".blade.php": ProjectType.UI,
    
    # Database extensions
    ".sql": ProjectType.DATABASE,
    ".ddl": ProjectType.DATABASE,
    
    # Could be either backend or UI
    ".ts": ProjectType.BACKEND,  # Default to backend, can be overridden
    ".js": ProjectType.BACKEND,  # Default to backend, can be overridden
    ".html": ProjectType.UI,
    ".css": ProjectType.UI,
    ".scss": ProjectType.UI,
}


def get_template_metadata(template_name: str) -> Optional[TemplateMetadata]:
    """
    Get metadata for a specific template by name.
    
    Args:
        template_name: Template filename
        
    Returns:
        TemplateMetadata or None if not found
    """
    return TEMPLATE_REGISTRY.get(template_name)


def list_all_templates() -> list[TemplateMetadata]:
    """
    Get all available templates.
    
    Returns:
        List of all TemplateMetadata objects
    """
    return list(TEMPLATE_REGISTRY.values())


def list_templates_by_project_type(project_type: ProjectType) -> list[TemplateMetadata]:
    """
    Get templates filtered by project type.
    
    Args:
        project_type: The project type to filter by
        
    Returns:
        List of matching TemplateMetadata objects
    """
    return [t for t in TEMPLATE_REGISTRY.values() if t.project_type == project_type]


def list_templates_by_complexity(complexity: TemplateComplexity) -> list[TemplateMetadata]:
    """
    Get templates filtered by complexity level.
    
    Args:
        complexity: The complexity level to filter by
        
    Returns:
        List of matching TemplateMetadata objects
    """
    return [t for t in TEMPLATE_REGISTRY.values() if t.complexity == complexity]


def suggest_template_for_file(
    file_path: str,
    complexity: Optional[TemplateComplexity] = None
) -> Optional[TemplateMetadata]:
    """
    Suggest the most appropriate template for a given file.
    
    Args:
        file_path: Path to the file being documented
        complexity: Optional preferred complexity level
        
    Returns:
        Best matching TemplateMetadata or None
    """
    path = Path(file_path)
    extension = path.suffix.lower()
    
    # Handle compound extensions like .blade.php
    if path.stem.endswith('.blade'):
        extension = '.blade.php'
    
    # Determine project type from extension
    project_type = EXTENSION_TO_PROJECT_TYPE.get(extension, ProjectType.GENERAL)
    
    logger.debug(f"Suggesting template for {file_path} (ext={extension}, type={project_type})")
    
    # Get templates for this project type
    candidates = list_templates_by_project_type(project_type)
    
    if not candidates:
        # Fall back to backend templates for unknown types
        candidates = list_templates_by_project_type(ProjectType.BACKEND)
    
    if not candidates:
        return None
    
    # If complexity specified, try to match it
    if complexity:
        matching = [t for t in candidates if t.complexity == complexity]
        if matching:
            return matching[0]
    
    # Default to standard complexity
    standard = [t for t in candidates if t.complexity == TemplateComplexity.STANDARD]
    if standard:
        return standard[0]
    
    # Just return the first candidate
    return candidates[0]


def format_templates_list(templates: list[TemplateMetadata], verbose: bool = False) -> str:
    """
    Format a list of templates as markdown for display.
    
    Args:
        templates: List of templates to format
        verbose: Include detailed information if True
        
    Returns:
        Formatted markdown string
    """
    if not templates:
        return "No templates found."
    
    lines = ["# Available Documentation Templates\n"]
    
    # Group by project type
    by_type: dict[ProjectType, list[TemplateMetadata]] = {}
    for template in templates:
        if template.project_type not in by_type:
            by_type[template.project_type] = []
        by_type[template.project_type].append(template)
    
    for project_type in [ProjectType.BACKEND, ProjectType.UI, ProjectType.DATABASE, ProjectType.GENERAL]:
        if project_type not in by_type:
            continue
        
        type_templates = by_type[project_type]
        lines.append(f"\n## {project_type.value.title()} Templates\n")
        
        for template in sorted(type_templates, key=lambda t: t.complexity.value):
            lines.append(f"### {template.display_name}")
            lines.append(f"**Complexity:** {template.complexity.value.title()}")
            lines.append(f"**URI:** `{template.uri}`\n")
            lines.append(f"{template.description}\n")
            
            if verbose:
                lines.append("**Use Cases:**")
                for use_case in template.use_cases:
                    lines.append(f"- {use_case}")
                
                lines.append("\n**Supported File Extensions:**")
                lines.append(", ".join(f"`{ext}`" for ext in template.file_extensions))
                
                lines.append("\n**Required Sections:**")
                for section in template.required_sections:
                    lines.append(f"- {section}")
                
                lines.append("")
    
    return "\n".join(lines)


def format_template_suggestion(
    file_path: str,
    template: TemplateMetadata,
    alternatives: list[TemplateMetadata] = None
) -> str:
    """
    Format a template suggestion as markdown.
    
    Args:
        file_path: The file being documented
        template: The suggested template
        alternatives: Optional list of alternative templates
        
    Returns:
        Formatted markdown string
    """
    lines = [
        "# Template Suggestion\n",
        f"**For file:** `{file_path}`\n",
        "## Recommended Template\n",
        f"### {template.display_name}",
        f"**Complexity:** {template.complexity.value.title()}",
        f"**Project Type:** {template.project_type.value.title()}",
        f"**URI:** `{template.uri}`\n",
        f"{template.description}\n",
        "**Required Sections:**"
    ]
    
    for section in template.required_sections:
        lines.append(f"- {section}")
    
    if alternatives:
        lines.append("\n## Alternative Templates\n")
        lines.append("If the recommended template doesn't fit your needs:\n")
        
        for alt in alternatives:
            if alt.name != template.name:
                lines.append(f"- **{alt.display_name}** ({alt.complexity.value}) - `{alt.uri}`")
    
    lines.append("\n## How to Use\n")
    lines.append("Ask Copilot to generate documentation using this template:")
    lines.append(f'```\n"Document {Path(file_path).name} using the {template.display_name}"\n```')
    
    return "\n".join(lines)
