"""
Project Configuration Module

Handles reading, creating, and managing .akr-config.json files.
Provides component-type detection and path resolution for documentation.
Also supports interview role customization for role-based interviews.
"""

import fnmatch
import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger("akr-mcp-server.tools.config")

# Default interview role configurations
# These can be overridden in .akr-config.json under "interviewRoles"
DEFAULT_INTERVIEW_ROLES = {
    "technical_lead": {
        "displayName": "Technical Lead",
        "description": "Architecture, design decisions, and technical strategy",
        "primaryCategories": ["design_rationale", "performance", "security_compliance", "known_issues"],
        "secondaryCategories": ["historical_context", "team_ownership", "external_integration"],
        "excludedCategories": ["business_context", "business_rules", "future_plans", "user_context"]
    },
    "developer": {
        "displayName": "Developer",
        "description": "Implementation details, configuration, and hands-on knowledge",
        "primaryCategories": ["configuration", "error_handling", "known_issues", "external_integration"],
        "secondaryCategories": ["design_rationale", "performance", "testing"],
        "excludedCategories": ["business_context", "business_rules", "team_ownership", "future_plans"]
    },
    "product_owner": {
        "displayName": "Product Owner",
        "description": "Business context, user value, and product strategy",
        "primaryCategories": ["business_context", "business_rules", "future_plans", "user_context"],
        "secondaryCategories": ["historical_context", "team_ownership", "accessibility"],
        "excludedCategories": ["configuration", "error_handling", "performance", "design_rationale"]
    },
    "qa_tester": {
        "displayName": "QA Tester",
        "description": "Quality, testing, edge cases, and known issues",
        "primaryCategories": ["testing", "known_issues", "edge_cases"],
        "secondaryCategories": ["error_handling", "accessibility", "performance"],
        "excludedCategories": ["business_context", "business_rules", "design_rationale", "future_plans"]
    },
    "scrum_master": {
        "displayName": "Scrum Master",
        "description": "Process, team dynamics, and delivery context",
        "primaryCategories": ["team_ownership", "historical_context"],
        "secondaryCategories": ["known_issues", "future_plans"],
        "excludedCategories": ["configuration", "error_handling", "design_rationale", "performance", "security_compliance"]
    }
}

# Default configuration template
DEFAULT_CONFIG_TEMPLATE = {
    "$schema": "https://akr.example.com/config-schema.json",
    "version": "1.0",
    
    "project": {
        "name": "",
        "type": "backend",
        "mainBranch": "main"
    },
    
    "documentation": {
        "outputRoot": "docs",
        "defaultTemplate": "standard_service_template.md",
        "filenamePattern": "{name}_doc.md",
        
        "componentMappings": [
            {
                "type": "services",
                "sourcePatterns": ["**/Services/**/*.cs", "**/services/**/*.py", "**/services/**/*.ts"],
                "outputPath": "docs/backend/services",
                "template": "comprehensive_service_template.md",
                "charter": "AKR_CHARTER_BACKEND.md"
            },
            {
                "type": "controllers",
                "sourcePatterns": ["**/Controllers/**/*.cs", "**/controllers/**/*.py", "**/controllers/**/*.ts"],
                "outputPath": "docs/backend/controllers",
                "template": "lean_baseline_service_template.md",
                "charter": "AKR_CHARTER_BACKEND.md"
            },
            {
                "type": "repositories",
                "sourcePatterns": ["**/Repositories/**/*.cs", "**/repositories/**/*.py"],
                "outputPath": "docs/backend/repositories",
                "template": "lean_baseline_service_template.md",
                "charter": "AKR_CHARTER_BACKEND.md"
            },
            {
                "type": "models",
                "sourcePatterns": ["**/Models/**/*.cs", "**/models/**/*.py", "**/DTOs/**/*.cs", "**/dtos/**/*.ts"],
                "outputPath": "docs/backend/models",
                "template": "minimal_service_template.md",
                "charter": "AKR_CHARTER_BACKEND.md"
            },
            {
                "type": "middleware",
                "sourcePatterns": ["**/Middleware/**/*.cs", "**/middleware/**/*.py", "**/middleware/**/*.ts"],
                "outputPath": "docs/backend/middleware",
                "template": "lean_baseline_service_template.md",
                "charter": "AKR_CHARTER_BACKEND.md"
            },
            {
                "type": "components",
                "sourcePatterns": ["**/components/**/*.tsx", "**/components/**/*.jsx", "**/components/**/*.vue"],
                "outputPath": "docs/ui/components",
                "template": "ui_component_template.md",
                "charter": "AKR_CHARTER_UI.md"
            },
            {
                "type": "pages",
                "sourcePatterns": ["**/pages/**/*.tsx", "**/pages/**/*.jsx", "**/views/**/*.vue"],
                "outputPath": "docs/ui/pages",
                "template": "ui_component_template.md",
                "charter": "AKR_CHARTER_UI.md"
            },
            {
                "type": "hooks",
                "sourcePatterns": ["**/hooks/**/*.ts", "**/hooks/**/*.tsx", "**/composables/**/*.ts"],
                "outputPath": "docs/ui/hooks",
                "template": "lean_baseline_service_template.md",
                "charter": "AKR_CHARTER_UI.md"
            },
            {
                "type": "tables",
                "sourcePatterns": ["**/Tables/**/*.sql", "**/database/**/*.sql", "**/migrations/**/*.sql"],
                "outputPath": "docs/database/tables",
                "template": "table_doc_template.md",
                "charter": "AKR_CHARTER_DB.md"
            },
            {
                "type": "storedProcedures",
                "sourcePatterns": ["**/StoredProcedures/**/*.sql", "**/sprocs/**/*.sql", "**/procedures/**/*.sql"],
                "outputPath": "docs/database/stored-procedures",
                "template": "table_doc_template.md",
                "charter": "AKR_CHARTER_DB.md"
            }
        ]
    },
    
    "branching": {
        "documentationBranchPrefix": "docs/",
        "autoCreateBranch": True,
        "defaultBranchStrategy": "new"
    },
    
    "pullRequests": {
        "autoCreate": False,
        "defaultLabels": ["documentation", "ai-generated"],
        "titleTemplate": "📖 Documentation: {componentType} - {fileName}",
        "defaultReviewers": []
    },
    
    # Interview roles configuration - can be customized per project
    # Set to None to use defaults, or provide overrides
    "interviewRoles": None
}


@dataclass
class ComponentMapping:
    """Mapping from source file patterns to documentation configuration."""
    type: str
    source_patterns: list[str]
    output_path: str
    template: str
    charter: str
    
    @classmethod
    def from_dict(cls, data: dict) -> "ComponentMapping":
        return cls(
            type=data.get("type", "unknown"),
            source_patterns=data.get("sourcePatterns", []),
            output_path=data.get("outputPath", "docs"),
            template=data.get("template", "standard_service_template.md"),
            charter=data.get("charter", "AKR_CHARTER.md")
        )


@dataclass
class DocumentationConfig:
    """Documentation configuration from .akr-config.json."""
    output_root: str = "docs"
    default_template: str = "standard_service_template.md"
    filename_pattern: str = "{name}_doc.md"
    component_mappings: list[ComponentMapping] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> "DocumentationConfig":
        mappings = [
            ComponentMapping.from_dict(m) 
            for m in data.get("componentMappings", [])
        ]
        return cls(
            output_root=data.get("outputRoot", "docs"),
            default_template=data.get("defaultTemplate", "standard_service_template.md"),
            filename_pattern=data.get("filenamePattern", "{name}_doc.md"),
            component_mappings=mappings
        )


@dataclass
class BranchingConfig:
    """Branching configuration."""
    documentation_branch_prefix: str = "docs/"
    auto_create_branch: bool = True
    default_branch_strategy: str = "new"  # "new", "current", "custom"
    
    @classmethod
    def from_dict(cls, data: dict) -> "BranchingConfig":
        return cls(
            documentation_branch_prefix=data.get("documentationBranchPrefix", "docs/"),
            auto_create_branch=data.get("autoCreateBranch", True),
            default_branch_strategy=data.get("defaultBranchStrategy", "new")
        )


@dataclass
class PRConfig:
    """Pull request configuration."""
    auto_create: bool = False
    default_labels: list[str] = field(default_factory=lambda: ["documentation", "ai-generated"])
    title_template: str = "📖 Documentation: {componentType} - {fileName}"
    default_reviewers: list[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> "PRConfig":
        return cls(
            auto_create=data.get("autoCreate", False),
            default_labels=data.get("defaultLabels", ["documentation", "ai-generated"]),
            title_template=data.get("titleTemplate", "📖 Documentation: {componentType} - {fileName}"),
            default_reviewers=data.get("defaultReviewers", [])
        )


@dataclass
class InterviewRoleConfig:
    """
    Configuration for a single interview role.
    
    Defines which question categories a role should answer during
    documentation interviews.
    """
    role_key: str
    display_name: str
    description: str
    primary_categories: list[str] = field(default_factory=list)
    secondary_categories: list[str] = field(default_factory=list)
    excluded_categories: list[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, role_key: str, data: dict) -> "InterviewRoleConfig":
        return cls(
            role_key=role_key,
            display_name=data.get("displayName", role_key.replace("_", " ").title()),
            description=data.get("description", ""),
            primary_categories=data.get("primaryCategories", []),
            secondary_categories=data.get("secondaryCategories", []),
            excluded_categories=data.get("excludedCategories", [])
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "displayName": self.display_name,
            "description": self.description,
            "primaryCategories": self.primary_categories,
            "secondaryCategories": self.secondary_categories,
            "excludedCategories": self.excluded_categories
        }


@dataclass
class InterviewRolesConfig:
    """
    Configuration for all interview roles.
    
    Manages role profiles that control question filtering during
    documentation interviews. Supports:
    - Default built-in roles
    - Custom role overrides
    - New custom roles
    """
    roles: dict[str, InterviewRoleConfig] = field(default_factory=dict)
    use_defaults: bool = True  # Whether to fall back to defaults for missing roles
    
    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "InterviewRolesConfig":
        """
        Create InterviewRolesConfig from configuration dictionary.
        
        Args:
            data: Dictionary of role configurations, or None to use all defaults
            
        Returns:
            InterviewRolesConfig instance
        """
        if data is None:
            # Use all defaults
            return cls(roles={}, use_defaults=True)
        
        roles = {}
        for role_key, role_data in data.items():
            if isinstance(role_data, dict):
                roles[role_key] = InterviewRoleConfig.from_dict(role_key, role_data)
        
        return cls(roles=roles, use_defaults=True)
    
    def get_role_config(self, role_key: str) -> Optional[InterviewRoleConfig]:
        """Get configuration for a specific role."""
        if role_key in self.roles:
            return self.roles[role_key]
        
        # Fall back to defaults if enabled
        if self.use_defaults and role_key in DEFAULT_INTERVIEW_ROLES:
            return InterviewRoleConfig.from_dict(role_key, DEFAULT_INTERVIEW_ROLES[role_key])
        
        return None
    
    def get_all_roles(self) -> dict[str, InterviewRoleConfig]:
        """
        Get all available roles (custom + defaults if enabled).
        
        Returns:
            Dictionary of role_key -> InterviewRoleConfig
        """
        all_roles = {}
        
        # Add defaults first if enabled
        if self.use_defaults:
            for role_key, role_data in DEFAULT_INTERVIEW_ROLES.items():
                all_roles[role_key] = InterviewRoleConfig.from_dict(role_key, role_data)
        
        # Override/add custom roles
        all_roles.update(self.roles)
        
        return all_roles
    
    def to_dict(self) -> Optional[dict]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns None if using all defaults (no custom config needed).
        """
        if not self.roles:
            return None  # Use defaults
        
        return {
            role_key: role_config.to_dict()
            for role_key, role_config in self.roles.items()
        }


@dataclass
class ProjectConfig:
    """Complete project configuration."""
    name: str = ""
    type: str = "backend"
    main_branch: str = "main"
    documentation: DocumentationConfig = field(default_factory=DocumentationConfig)
    branching: BranchingConfig = field(default_factory=BranchingConfig)
    pull_requests: PRConfig = field(default_factory=PRConfig)
    interview_roles: InterviewRolesConfig = field(default_factory=InterviewRolesConfig)
    config_path: Optional[Path] = None
    
    @classmethod
    def from_dict(cls, data: dict, config_path: Optional[Path] = None) -> "ProjectConfig":
        project_data = data.get("project", {})
        return cls(
            name=project_data.get("name", ""),
            type=project_data.get("type", "backend"),
            main_branch=project_data.get("mainBranch", "main"),
            documentation=DocumentationConfig.from_dict(data.get("documentation", {})),
            branching=BranchingConfig.from_dict(data.get("branching", {})),
            pull_requests=PRConfig.from_dict(data.get("pullRequests", {})),
            interview_roles=InterviewRolesConfig.from_dict(data.get("interviewRoles")),
            config_path=config_path
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "$schema": "https://akr.example.com/config-schema.json",
            "version": "1.0",
            "project": {
                "name": self.name,
                "type": self.type,
                "mainBranch": self.main_branch
            },
            "documentation": {
                "outputRoot": self.documentation.output_root,
                "defaultTemplate": self.documentation.default_template,
                "filenamePattern": self.documentation.filename_pattern,
                "componentMappings": [
                    {
                        "type": m.type,
                        "sourcePatterns": m.source_patterns,
                        "outputPath": m.output_path,
                        "template": m.template,
                        "charter": m.charter
                    }
                    for m in self.documentation.component_mappings
                ]
            },
            "branching": {
                "documentationBranchPrefix": self.branching.documentation_branch_prefix,
                "autoCreateBranch": self.branching.auto_create_branch,
                "defaultBranchStrategy": self.branching.default_branch_strategy
            },
            "pullRequests": {
                "autoCreate": self.pull_requests.auto_create,
                "defaultLabels": self.pull_requests.default_labels,
                "titleTemplate": self.pull_requests.title_template,
                "defaultReviewers": self.pull_requests.default_reviewers
            }
        }
        
        # Only include interviewRoles if custom roles are configured
        interview_roles_dict = self.interview_roles.to_dict()
        if interview_roles_dict:
            result["interviewRoles"] = interview_roles_dict
        
        return result


class ProjectConfigManager:
    """
    Manages project configuration for AKR documentation.
    
    Handles:
    - Loading .akr-config.json from workspace
    - Creating default configuration for new projects
    - Matching source files to component types
    - Resolving documentation output paths
    """
    
    CONFIG_FILENAME = ".akr-config.json"
    
    def __init__(self, workspace_path: str):
        """
        Initialize config manager for a workspace.
        
        Args:
            workspace_path: Path to the project workspace root
        """
        self.workspace_path = Path(workspace_path)
        self._config: Optional[ProjectConfig] = None
        self._config_loaded = False
    
    @property
    def config_file_path(self) -> Path:
        """Get the path to .akr-config.json."""
        return self.workspace_path / self.CONFIG_FILENAME
    
    def config_exists(self) -> bool:
        """Check if .akr-config.json exists in the workspace."""
        return self.config_file_path.exists()
    
    def load_config(self) -> ProjectConfig:
        """
        Load configuration from .akr-config.json.
        
        Returns:
            ProjectConfig with loaded or default values
        """
        if self._config_loaded and self._config:
            return self._config
        
        if self.config_exists():
            try:
                with open(self.config_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._config = ProjectConfig.from_dict(data, self.config_file_path)
                logger.info(f"Loaded config from {self.config_file_path}")
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                self._config = self._create_default_config()
        else:
            logger.info("No config file found, using defaults")
            self._config = self._create_default_config()
        
        self._config_loaded = True
        return self._config
    
    def _create_default_config(self) -> ProjectConfig:
        """Create default configuration based on workspace analysis."""
        config = ProjectConfig.from_dict(DEFAULT_CONFIG_TEMPLATE)
        config.name = self.workspace_path.name
        config.config_path = self.config_file_path
        
        # Detect project type from workspace
        detected_type = self._detect_project_type()
        if detected_type:
            config.type = detected_type
        
        # Detect main branch
        detected_branch = self._detect_main_branch()
        if detected_branch:
            config.main_branch = detected_branch
        
        return config
    
    def _detect_project_type(self) -> Optional[str]:
        """Detect project type from file patterns in workspace."""
        # Check for common patterns
        patterns = {
            "backend": [
                "**/*.cs", "**/*.java", "**/Services/**", "**/Controllers/**",
                "**/*.csproj", "**/pom.xml", "**/requirements.txt"
            ],
            "ui": [
                "**/components/**/*.tsx", "**/components/**/*.jsx",
                "**/pages/**", "**/package.json", "**/angular.json"
            ],
            "database": [
                "**/Tables/**/*.sql", "**/migrations/**", "**/database/**/*.sql"
            ]
        }
        
        for project_type, type_patterns in patterns.items():
            for pattern in type_patterns:
                matches = list(self.workspace_path.glob(pattern))
                if matches:
                    logger.debug(f"Detected project type: {project_type} (matched {pattern})")
                    return project_type
        
        return "backend"  # Default
    
    def _detect_main_branch(self) -> Optional[str]:
        """Detect main branch from git configuration."""
        import subprocess
        
        try:
            # Check for common branch names
            result = subprocess.run(
                ["git", "branch", "-l"],
                capture_output=True,
                text=True,
                cwd=self.workspace_path
            )
            
            if result.returncode == 0:
                branches = result.stdout.strip().split('\n')
                branches = [b.strip().lstrip('* ') for b in branches if b.strip()]
                
                for candidate in ['main', 'master', 'develop']:
                    if candidate in branches:
                        return candidate
        except Exception as e:
            logger.debug(f"Could not detect main branch: {e}")
        
        return "main"
    
    def save_config(self, config: Optional[ProjectConfig] = None) -> bool:
        """
        Save configuration to .akr-config.json.
        
        Args:
            config: Configuration to save (uses current if None)
            
        Returns:
            True if successful
        """
        if config:
            self._config = config
        
        if not self._config:
            self._config = self._create_default_config()
        
        try:
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config.to_dict(), f, indent=2)
            logger.info(f"Saved config to {self.config_file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def match_component(self, source_file: str) -> Optional[ComponentMapping]:
        """
        Match a source file to a component mapping.
        
        Args:
            source_file: Relative or absolute path to source file
            
        Returns:
            Matching ComponentMapping or None
        """
        config = self.load_config()
        
        # Normalize path to relative
        source_path = Path(source_file)
        if source_path.is_absolute():
            try:
                source_path = source_path.relative_to(self.workspace_path)
            except ValueError:
                pass
        
        source_str = str(source_path).replace('\\', '/')
        
        for mapping in config.documentation.component_mappings:
            for pattern in mapping.source_patterns:
                # Convert glob pattern to work with fnmatch
                if fnmatch.fnmatch(source_str, pattern):
                    logger.debug(f"Matched {source_file} to {mapping.type} via {pattern}")
                    return mapping
                
                # Also try with ** handling
                if '**' in pattern:
                    # Simple ** handling: replace ** with *
                    simple_pattern = pattern.replace('**/', '*').replace('**', '*')
                    if fnmatch.fnmatch(source_str, simple_pattern):
                        logger.debug(f"Matched {source_file} to {mapping.type} via {pattern}")
                        return mapping
        
        logger.debug(f"No component mapping found for {source_file}")
        return None
    
    def resolve_doc_path(self, source_file: str) -> tuple[str, Optional[ComponentMapping]]:
        """
        Resolve the documentation output path for a source file.
        
        Args:
            source_file: Path to the source file
            
        Returns:
            Tuple of (documentation_path, component_mapping)
        """
        config = self.load_config()
        mapping = self.match_component(source_file)
        
        # Get source file name without extension
        source_path = Path(source_file)
        source_name = source_path.stem
        
        # Apply filename pattern
        filename_pattern = config.documentation.filename_pattern
        doc_filename = filename_pattern.replace("{name}", source_name)
        
        if mapping:
            doc_path = f"{mapping.output_path}/{doc_filename}"
        else:
            # Use default path
            doc_path = f"{config.documentation.output_root}/{doc_filename}"
        
        return doc_path, mapping
    
    def get_setup_prompt(self) -> str:
        """
        Generate a setup prompt for first-time configuration.
        
        Returns:
            Formatted markdown prompt for user
        """
        detected_type = self._detect_project_type()
        detected_branch = self._detect_main_branch()
        
        # Detect existing folder structure
        detected_folders = self._detect_source_folders()
        
        prompt = f"""# AKR Documentation Setup

I notice this project doesn't have AKR documentation configuration yet. 
This is a **one-time setup** that will be shared with your entire team.

## Detected Project Information

| Setting | Detected Value |
|---------|----------------|
| **Project Name** | `{self.workspace_path.name}` |
| **Project Type** | `{detected_type}` |
| **Main Branch** | `{detected_branch}` |

## Detected Source Folders

"""
        if detected_folders:
            for folder_type, folders in detected_folders.items():
                prompt += f"**{folder_type.title()}:**\n"
                for folder in folders[:3]:  # Limit to 3 examples
                    prompt += f"- `{folder}`\n"
                prompt += "\n"
        else:
            prompt += "*No standard source folders detected.*\n\n"
        
        prompt += """## Suggested Configuration

Based on your project structure, I recommend:

| Component Type | Source Pattern | Documentation Path |
|----------------|----------------|-------------------|
"""
        # Add relevant mappings based on detected type
        config = self._create_default_config()
        for mapping in config.documentation.component_mappings[:5]:
            prompt += f"| {mapping.type} | `{mapping.source_patterns[0]}` | `{mapping.output_path}` |\n"
        
        prompt += """
## Next Steps

1. **Accept defaults** - I'll create `.akr-config.json` with the settings above
2. **Customize** - Tell me what changes you'd like to make
3. **Skip setup** - Use defaults without saving (not recommended)

What would you like to do?
"""
        return prompt
    
    def _detect_source_folders(self) -> dict[str, list[str]]:
        """Detect existing source folder structure."""
        detected = {}
        
        folder_patterns = {
            "services": ["Services", "services", "Service"],
            "controllers": ["Controllers", "controllers", "Controller"],
            "models": ["Models", "models", "DTOs", "dtos", "Entities"],
            "components": ["components", "Components"],
            "pages": ["pages", "Pages", "views", "Views"],
            "database": ["Tables", "database", "migrations", "Database"]
        }
        
        for folder_type, patterns in folder_patterns.items():
            found = []
            for pattern in patterns:
                matches = list(self.workspace_path.glob(f"**/{pattern}"))
                for match in matches:
                    if match.is_dir():
                        try:
                            rel_path = match.relative_to(self.workspace_path)
                            found.append(str(rel_path))
                        except ValueError:
                            pass
            
            if found:
                detected[folder_type] = list(set(found))[:5]  # Limit and dedupe
        
        return detected
    
    def add_component_mapping(self, mapping: ComponentMapping) -> bool:
        """
        Add a new component mapping to the configuration.
        
        Args:
            mapping: ComponentMapping to add
            
        Returns:
            True if successful
        """
        config = self.load_config()
        
        # Check for existing mapping with same type
        for i, existing in enumerate(config.documentation.component_mappings):
            if existing.type == mapping.type:
                # Replace existing
                config.documentation.component_mappings[i] = mapping
                return self.save_config(config)
        
        # Add new mapping
        config.documentation.component_mappings.append(mapping)
        return self.save_config(config)


# Convenience function for getting config
def get_project_config(workspace_path: str) -> ProjectConfig:
    """
    Get project configuration for a workspace.
    
    Args:
        workspace_path: Path to workspace root
        
    Returns:
        ProjectConfig instance
    """
    manager = ProjectConfigManager(workspace_path)
    return manager.load_config()


def resolve_documentation_path(workspace_path: str, source_file: str) -> dict:
    """
    Resolve documentation path for a source file.
    
    Args:
        workspace_path: Path to workspace root
        source_file: Path to source file
        
    Returns:
        Dictionary with path info and component details
    """
    manager = ProjectConfigManager(workspace_path)
    doc_path, mapping = manager.resolve_doc_path(source_file)
    
    result = {
        "sourceFile": source_file,
        "documentationPath": doc_path,
        "fullPath": str(Path(workspace_path) / doc_path),
        "componentType": mapping.type if mapping else "unknown",
        "template": mapping.template if mapping else manager.load_config().documentation.default_template,
        "charter": mapping.charter if mapping else "AKR_CHARTER.md",
        "configExists": manager.config_exists()
    }
    
    return result


# Alias for backward compatibility
AKRConfigManager = ProjectConfigManager
