"""
AKR Tools Module

MCP tools for health check, templates, validation, and write operations.
"""

from .documentation import (
    ProjectType,
    TemplateComplexity,
    TemplateMetadata,
    TEMPLATE_REGISTRY,
    get_template_metadata,
    list_all_templates,
    list_templates_by_project_type,
    list_templates_by_complexity,
    suggest_template_for_file,
    format_templates_list,
    format_template_suggestion,
)

# Write capability modules
from .config import (
    ProjectConfig,
    ComponentMapping,
    AKRConfigManager,
)

from .branch_management import (
    BranchManager,
    BranchStrategy,
)

from .write_operations import (
    DocumentationWriter,
    write_documentation,
    write_config_file,
)

from .section_updater import (
    SectionType,
    Section,
    UpdateResult,
    MarkdownSectionParser,
    SurgicalUpdater,
    analyze_documentation_impact,
    update_documentation_sections,
    get_document_structure,
)

from .pr_operations import (
    PRManager,
    PRInfo,
    create_documentation_pr,
    check_documentation_pr_requirements,
)

# Human input interview tools
from .human_input_interview import (
    InputCategory,
    QuestionPriority,
    AnswerStatus,
    HumanInputSection,
    InterviewAnswer,
    InterviewSession,
    HumanInputDetector,
    InterviewManager,
    get_interview_manager,
    start_documentation_interview,
    get_next_interview_question,
    submit_interview_answer,
    skip_interview_question,
    get_interview_progress,
    end_documentation_interview,
    # Role-based interview
    InterviewRole,
    RoleProfile,
    RoleProfileManager,
    DEFAULT_ROLE_PROFILES,
    get_role_profile_manager,
    reset_role_profile_manager,
    load_role_profiles_from_config,
    list_available_roles,
)

__all__ = [
    # Documentation tools
    "ProjectType",
    "TemplateComplexity",
    "TemplateMetadata",
    "TEMPLATE_REGISTRY",
    "get_template_metadata",
    "list_all_templates",
    "list_templates_by_project_type",
    "list_templates_by_complexity",
    "suggest_template_for_file",
    "format_templates_list",
    "format_template_suggestion",
    # Config tools
    "ProjectConfig",
    "ComponentMapping",
    "AKRConfigManager",
    # Branch management
    "BranchManager",
    "BranchStrategy",
    # Write operations
    "DocumentationWriter",
    "write_documentation",
    "write_config_file",
    # Section updater
    "SectionType",
    "Section",
    "UpdateResult",
    "MarkdownSectionParser",
    "SurgicalUpdater",
    "analyze_documentation_impact",
    "update_documentation_sections",
    "get_document_structure",
    # PR operations
    "PRManager",
    "PRInfo",
    "create_documentation_pr",
    "check_documentation_pr_requirements",
    # Human input interview
    "InputCategory",
    "QuestionPriority",
    "AnswerStatus",
    "HumanInputSection",
    "InterviewAnswer",
    "InterviewSession",
    "HumanInputDetector",
    "InterviewManager",
    "get_interview_manager",
    "start_documentation_interview",
    "get_next_interview_question",
    "submit_interview_answer",
    "skip_interview_question",
    "get_interview_progress",
    "end_documentation_interview",
    # Role-based interview
    "InterviewRole",
    "RoleProfile",
    "RoleProfileManager",
    "DEFAULT_ROLE_PROFILES",
    "get_role_profile_manager",
    "reset_role_profile_manager",
    "load_role_profiles_from_config",
    "list_available_roles",
]
