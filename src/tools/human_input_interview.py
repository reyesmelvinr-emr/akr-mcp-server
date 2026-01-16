"""
Human Input Interview Module

Provides an iterative interview process to collect human context for documentation sections
that cannot be derived from source code analysis alone.

This module enables:
- Detection of sections requiring human input (marked with ❓)
- Interactive Q&A session with skip capability
- Role-based question filtering (Tech Lead, Developer, PO, QA, Scrum Master)
- AI-assisted draft generation from user answers
- Progressive documentation enhancement
- Configurable role-to-category mappings via .akr-config.json
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger("akr-mcp-server.tools.human_input_interview")


class InputCategory(Enum):
    """Categories of human input required."""
    BUSINESS_CONTEXT = "business_context"
    HISTORICAL_CONTEXT = "historical_context"
    BUSINESS_RULES = "business_rules"
    ACCESSIBILITY = "accessibility"
    SECURITY_COMPLIANCE = "security_compliance"
    PERFORMANCE = "performance"
    EXTERNAL_INTEGRATION = "external_integration"
    TEAM_OWNERSHIP = "team_ownership"
    KNOWN_ISSUES = "known_issues"
    FUTURE_PLANS = "future_plans"
    DESIGN_RATIONALE = "design_rationale"
    CONFIGURATION = "configuration"
    ERROR_HANDLING = "error_handling"
    TESTING = "testing"
    EDGE_CASES = "edge_cases"
    USER_CONTEXT = "user_context"


class QuestionPriority(Enum):
    """Priority levels for interview questions."""
    CRITICAL = "critical"      # Must have for baseline documentation
    IMPORTANT = "important"    # Strongly recommended
    OPTIONAL = "optional"      # Nice to have, can skip


class AnswerStatus(Enum):
    """Status of an answer."""
    PENDING = "pending"
    ANSWERED = "answered"
    SKIPPED = "skipped"
    DRAFTED = "drafted"  # AI drafted from user input


class InterviewRole(Enum):
    """
    Roles that can participate in documentation interviews.
    
    Each role has specialized knowledge domains that determine which
    questions they are best suited to answer. The system filters
    questions based on the selected role to reduce irrelevant questions
    and improve answer quality.
    """
    TECHNICAL_LEAD = "technical_lead"
    DEVELOPER = "developer"
    PRODUCT_OWNER = "product_owner"
    QA_TESTER = "qa_tester"
    SCRUM_MASTER = "scrum_master"
    GENERAL = "general"  # No filtering, all questions shown


@dataclass
class RoleProfile:
    """
    Defines what question categories a role should answer.
    
    Role profiles control interview question filtering:
    - primary_categories: Questions this role SHOULD answer (their expertise)
    - secondary_categories: Questions this role CAN answer (familiar with)
    - excluded_categories: Questions to skip (better answered by others)
    
    Categories not in any list are shown but marked as optional for the role.
    """
    role: InterviewRole
    display_name: str
    description: str
    primary_categories: list[InputCategory] = field(default_factory=list)
    secondary_categories: list[InputCategory] = field(default_factory=list)
    excluded_categories: list[InputCategory] = field(default_factory=list)
    
    def should_ask(self, category: InputCategory) -> bool:
        """Check if this role should be asked questions in this category."""
        # If no excluded categories, show all questions (GENERAL role behavior)
        # This also allows custom roles to define their own filtering
        if not self.excluded_categories:
            return True
        return category not in self.excluded_categories
    
    def is_primary(self, category: InputCategory) -> bool:
        """Check if this category is primary expertise for the role."""
        return category in self.primary_categories
    
    def is_secondary(self, category: InputCategory) -> bool:
        """Check if this category is secondary expertise for the role."""
        return category in self.secondary_categories
    
    def get_delegation_target(self, category: InputCategory) -> Optional[str]:
        """
        Suggest which role should answer a question in an excluded category.
        
        Returns display name of suggested role, or None if no specific suggestion.
        """
        # Map excluded categories to suggested roles
        delegation_map = {
            InputCategory.BUSINESS_CONTEXT: "Product Owner",
            InputCategory.BUSINESS_RULES: "Product Owner",
            InputCategory.FUTURE_PLANS: "Product Owner",
            InputCategory.USER_CONTEXT: "Product Owner",
            InputCategory.DESIGN_RATIONALE: "Technical Lead",
            InputCategory.PERFORMANCE: "Technical Lead",
            InputCategory.SECURITY_COMPLIANCE: "Technical Lead",
            InputCategory.CONFIGURATION: "Developer",
            InputCategory.ERROR_HANDLING: "Developer",
            InputCategory.TEAM_OWNERSHIP: "Scrum Master",
            InputCategory.HISTORICAL_CONTEXT: "Scrum Master",
            InputCategory.TESTING: "QA Tester",
            InputCategory.EDGE_CASES: "QA Tester",
            InputCategory.KNOWN_ISSUES: "Developer",
        }
        
        if category in self.excluded_categories:
            return delegation_map.get(category)
        return None
    
    @classmethod
    def from_dict(cls, role_key: str, data: dict) -> "RoleProfile":
        """
        Create a RoleProfile from a configuration dictionary.
        
        Args:
            role_key: The role identifier (e.g., 'technical_lead')
            data: Dictionary with role configuration
            
        Returns:
            RoleProfile instance
        """
        # Try to match to existing enum, or use GENERAL as fallback
        try:
            role_enum = InterviewRole(role_key)
        except ValueError:
            role_enum = InterviewRole.GENERAL
            logger.warning(f"Unknown role '{role_key}', using GENERAL")
        
        # Parse categories
        def parse_categories(category_list: list[str]) -> list[InputCategory]:
            result = []
            for cat_str in category_list:
                try:
                    result.append(InputCategory(cat_str))
                except ValueError:
                    logger.warning(f"Unknown category '{cat_str}' in role config")
            return result
        
        return cls(
            role=role_enum,
            display_name=data.get("displayName", role_key.replace("_", " ").title()),
            description=data.get("description", ""),
            primary_categories=parse_categories(data.get("primaryCategories", [])),
            secondary_categories=parse_categories(data.get("secondaryCategories", [])),
            excluded_categories=parse_categories(data.get("excludedCategories", []))
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "displayName": self.display_name,
            "description": self.description,
            "primaryCategories": [c.value for c in self.primary_categories],
            "secondaryCategories": [c.value for c in self.secondary_categories],
            "excludedCategories": [c.value for c in self.excluded_categories]
        }


# =============================================================================
# Default Role Profiles
# =============================================================================

DEFAULT_ROLE_PROFILES: dict[InterviewRole, RoleProfile] = {
    InterviewRole.TECHNICAL_LEAD: RoleProfile(
        role=InterviewRole.TECHNICAL_LEAD,
        display_name="Technical Lead",
        description="Architecture, design decisions, and technical strategy",
        primary_categories=[
            InputCategory.DESIGN_RATIONALE,
            InputCategory.PERFORMANCE,
            InputCategory.SECURITY_COMPLIANCE,
            InputCategory.KNOWN_ISSUES,
        ],
        secondary_categories=[
            InputCategory.HISTORICAL_CONTEXT,
            InputCategory.TEAM_OWNERSHIP,
            InputCategory.EXTERNAL_INTEGRATION,
        ],
        excluded_categories=[
            InputCategory.BUSINESS_CONTEXT,
            InputCategory.BUSINESS_RULES,
            InputCategory.FUTURE_PLANS,
            InputCategory.USER_CONTEXT,
        ]
    ),
    
    InterviewRole.DEVELOPER: RoleProfile(
        role=InterviewRole.DEVELOPER,
        display_name="Developer",
        description="Implementation details, configuration, and hands-on knowledge",
        primary_categories=[
            InputCategory.CONFIGURATION,
            InputCategory.ERROR_HANDLING,
            InputCategory.KNOWN_ISSUES,
            InputCategory.EXTERNAL_INTEGRATION,
        ],
        secondary_categories=[
            InputCategory.DESIGN_RATIONALE,
            InputCategory.PERFORMANCE,
            InputCategory.TESTING,
        ],
        excluded_categories=[
            InputCategory.BUSINESS_CONTEXT,
            InputCategory.BUSINESS_RULES,
            InputCategory.TEAM_OWNERSHIP,
            InputCategory.FUTURE_PLANS,
        ]
    ),
    
    InterviewRole.PRODUCT_OWNER: RoleProfile(
        role=InterviewRole.PRODUCT_OWNER,
        display_name="Product Owner",
        description="Business context, user value, and product strategy",
        primary_categories=[
            InputCategory.BUSINESS_CONTEXT,
            InputCategory.BUSINESS_RULES,
            InputCategory.FUTURE_PLANS,
            InputCategory.USER_CONTEXT,
        ],
        secondary_categories=[
            InputCategory.HISTORICAL_CONTEXT,
            InputCategory.TEAM_OWNERSHIP,
            InputCategory.ACCESSIBILITY,
        ],
        excluded_categories=[
            InputCategory.CONFIGURATION,
            InputCategory.ERROR_HANDLING,
            InputCategory.PERFORMANCE,
            InputCategory.DESIGN_RATIONALE,
        ]
    ),
    
    InterviewRole.QA_TESTER: RoleProfile(
        role=InterviewRole.QA_TESTER,
        display_name="QA Tester",
        description="Quality, testing, edge cases, and known issues",
        primary_categories=[
            InputCategory.TESTING,
            InputCategory.KNOWN_ISSUES,
            InputCategory.EDGE_CASES,
        ],
        secondary_categories=[
            InputCategory.ERROR_HANDLING,
            InputCategory.ACCESSIBILITY,
            InputCategory.PERFORMANCE,
        ],
        excluded_categories=[
            InputCategory.BUSINESS_CONTEXT,
            InputCategory.BUSINESS_RULES,
            InputCategory.DESIGN_RATIONALE,
            InputCategory.FUTURE_PLANS,
        ]
    ),
    
    InterviewRole.SCRUM_MASTER: RoleProfile(
        role=InterviewRole.SCRUM_MASTER,
        display_name="Scrum Master",
        description="Process, team dynamics, and delivery context",
        primary_categories=[
            InputCategory.TEAM_OWNERSHIP,
            InputCategory.HISTORICAL_CONTEXT,
        ],
        secondary_categories=[
            InputCategory.KNOWN_ISSUES,
            InputCategory.FUTURE_PLANS,
        ],
        excluded_categories=[
            InputCategory.CONFIGURATION,
            InputCategory.ERROR_HANDLING,
            InputCategory.DESIGN_RATIONALE,
            InputCategory.PERFORMANCE,
            InputCategory.SECURITY_COMPLIANCE,
        ]
    ),
    
    InterviewRole.GENERAL: RoleProfile(
        role=InterviewRole.GENERAL,
        display_name="General",
        description="All questions (no filtering)",
        primary_categories=[],  # Empty means all are shown
        secondary_categories=[],
        excluded_categories=[]  # Empty means nothing excluded
    ),
}


class RoleProfileManager:
    """
    Manages role profiles with support for customization via configuration.
    
    Features:
    - Default profiles for all built-in roles
    - Custom profiles from .akr-config.json
    - Partial override (only override specified roles)
    - Custom role support (add new roles beyond defaults)
    """
    
    def __init__(self, custom_profiles: Optional[dict] = None):
        """
        Initialize the role profile manager.
        
        Args:
            custom_profiles: Optional dictionary of custom role configurations
                            from .akr-config.json interviewRoles section
        """
        self._profiles: dict[str, RoleProfile] = {}
        self._load_defaults()
        
        if custom_profiles:
            self._load_custom_profiles(custom_profiles)
    
    def _load_defaults(self):
        """Load default role profiles."""
        for role, profile in DEFAULT_ROLE_PROFILES.items():
            self._profiles[role.value] = profile
    
    def _load_custom_profiles(self, custom_profiles: dict):
        """
        Load custom profiles from configuration, merging with defaults.
        
        Custom profiles can:
        - Override existing roles (partial or complete)
        - Add entirely new roles
        """
        for role_key, role_config in custom_profiles.items():
            if isinstance(role_config, dict):
                profile = RoleProfile.from_dict(role_key, role_config)
                self._profiles[role_key] = profile
                logger.info(f"Loaded custom role profile: {role_key}")
    
    def get_profile(self, role: str | InterviewRole) -> RoleProfile:
        """
        Get a role profile by name or enum.
        
        Args:
            role: Role identifier (string or InterviewRole enum)
            
        Returns:
            RoleProfile for the role, or GENERAL profile if not found
        """
        if isinstance(role, InterviewRole):
            role_key = role.value
        else:
            role_key = role
        
        return self._profiles.get(role_key, self._profiles.get("general"))
    
    def get_all_profiles(self) -> dict[str, RoleProfile]:
        """Get all available role profiles."""
        return self._profiles.copy()
    
    def list_roles(self) -> list[dict]:
        """
        List all available roles with their descriptions.
        
        Returns:
            List of role information dictionaries
        """
        roles = []
        for role_key, profile in self._profiles.items():
            roles.append({
                "role": role_key,
                "display_name": profile.display_name,
                "description": profile.description,
                "is_builtin": role_key in [r.value for r in InterviewRole],
                "primary_category_count": len(profile.primary_categories),
                "excluded_category_count": len(profile.excluded_categories)
            })
        return roles


# Module-level default manager (can be replaced with custom config)
_role_profile_manager: Optional[RoleProfileManager] = None


def get_role_profile_manager(custom_profiles: Optional[dict] = None) -> RoleProfileManager:
    """
    Get or create the role profile manager.
    
    Args:
        custom_profiles: Optional custom profiles to merge with defaults.
                        If provided, creates a new manager with these profiles.
                        
    Returns:
        RoleProfileManager instance
    """
    global _role_profile_manager
    
    if custom_profiles is not None:
        # Create new manager with custom profiles
        _role_profile_manager = RoleProfileManager(custom_profiles)
    elif _role_profile_manager is None:
        # Create default manager
        _role_profile_manager = RoleProfileManager()
    
    return _role_profile_manager


def reset_role_profile_manager():
    """Reset the role profile manager to defaults (useful for testing)."""
    global _role_profile_manager
    _role_profile_manager = None


def load_role_profiles_from_config(workspace_path: Optional[str] = None) -> RoleProfileManager:
    """
    Load role profiles from project configuration file.
    
    This function attempts to load custom role profiles from the project's
    .akr-config.json file. If no custom profiles are found, it returns
    a manager with default profiles.
    
    Args:
        workspace_path: Path to the project workspace. If None, uses defaults.
        
    Returns:
        RoleProfileManager with custom profiles merged with defaults
        
    Usage:
        # From MCP server handler
        manager = load_role_profiles_from_config("/path/to/project")
        profile = manager.get_profile("developer")
    """
    if workspace_path is None:
        # No workspace, use defaults
        return get_role_profile_manager()
    
    try:
        # Try to import and use the config module
        from tools.config import AKRConfigManager
        
        config_manager = AKRConfigManager(workspace_path)
        config = config_manager.load_config()
        
        if config and hasattr(config, 'interview_roles') and config.interview_roles:
            # Get custom profiles from config
            custom_profiles = config.interview_roles.to_dict() if hasattr(config.interview_roles, 'to_dict') else None
            if custom_profiles:
                logger.info(f"Loaded custom role profiles from {workspace_path}")
                return get_role_profile_manager(custom_profiles)
        
        logger.debug(f"No custom role profiles found in {workspace_path}, using defaults")
        return get_role_profile_manager()
        
    except ImportError:
        logger.warning("Config module not available, using default role profiles")
        return get_role_profile_manager()
    except Exception as e:
        logger.warning(f"Error loading config from {workspace_path}: {e}, using defaults")
        return get_role_profile_manager()


def list_available_roles(workspace_path: Optional[str] = None) -> list[dict]:
    """
    List all available interview roles.
    
    This function returns information about all available roles,
    including both built-in roles and any custom roles defined
    in the project configuration.
    
    Args:
        workspace_path: Optional path to load custom roles from config
        
    Returns:
        List of role information dictionaries with:
        - role: Role key (e.g., 'technical_lead')
        - display_name: Human-readable name
        - description: Role description
        - is_builtin: Whether it's a built-in role
        - primary_category_count: Number of primary expertise categories
        - excluded_category_count: Number of excluded categories
    """
    manager = load_role_profiles_from_config(workspace_path)
    return manager.list_roles()


@dataclass
class HumanInputSection:
    """
    Represents a section in a template that requires human input.
    
    Detected from template markers:
    - ❓ [HUMAN: description]
    - ❓ _description_
    - Sections with placeholder text like [Business rationale]
    """
    section_id: str
    section_title: str
    category: InputCategory
    priority: QuestionPriority
    template_placeholder: str
    question: str
    follow_up_prompts: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    context_hints: str = ""


@dataclass
class InterviewAnswer:
    """User's answer to an interview question."""
    section_id: str
    raw_answer: str
    drafted_content: Optional[str] = None
    status: AnswerStatus = AnswerStatus.PENDING
    timestamp: Optional[datetime] = None
    skip_reason: Optional[str] = None


@dataclass
class InterviewSession:
    """
    Manages an interactive interview session for documentation.
    
    Tracks:
    - Questions to ask (filtered by role)
    - Answers received
    - Skip status
    - Draft content generation
    - Questions delegated to other roles
    """
    session_id: str
    source_file: str
    template_name: str
    component_type: str
    role: InterviewRole = InterviewRole.GENERAL
    role_profile: Optional[RoleProfile] = None
    questions: list[HumanInputSection] = field(default_factory=list)
    excluded_questions: list[HumanInputSection] = field(default_factory=list)  # Questions for other roles
    answers: dict[str, InterviewAnswer] = field(default_factory=dict)
    current_index: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if all questions have been addressed (answered or skipped)."""
        if not self.questions:
            return True
        return self.current_index >= len(self.questions)
    
    @property
    def progress(self) -> dict:
        """Get interview progress statistics."""
        total = len(self.questions)
        answered = sum(1 for a in self.answers.values() if a.status == AnswerStatus.ANSWERED)
        skipped = sum(1 for a in self.answers.values() if a.status == AnswerStatus.SKIPPED)
        drafted = sum(1 for a in self.answers.values() if a.status == AnswerStatus.DRAFTED)
        
        return {
            "total_questions": total,
            "answered": answered,
            "skipped": skipped,
            "drafted": drafted,
            "remaining": total - answered - skipped,
            "current_index": self.current_index,
            "percent_complete": round((answered + skipped) / total * 100) if total > 0 else 100
        }


class HumanInputDetector:
    """
    Detects sections requiring human input from templates or generated documentation.
    
    Recognizes patterns:
    - ❓ markers for human input
    - [HUMAN: ...] directives
    - Placeholder text patterns
    - Empty sections with human-input indicators
    """
    
    # Patterns that indicate human input is required
    HUMAN_INPUT_PATTERNS = [
        r"❓\s*\[HUMAN:\s*([^\]]+)\]",  # ❓ [HUMAN: description]
        r"❓\s*_([^_]+)_",               # ❓ _description in italics_
        r"❓\s*\*\*([^*]+)\*\*",         # ❓ **description in bold**
        r"\[(?:Business rationale|Why|Historical context|Business context)[^\]]*\]",
        r"\[(?:Team/Person responsible|Owner|Contact)[^\]]*\]",
        r"\[(?:Date|Timeline|Version|Since when)[^\]]*\]",
    ]
    
    # Section title to category mapping
    SECTION_CATEGORY_MAP = {
        # Business Context
        "business": InputCategory.BUSINESS_CONTEXT,
        "purpose": InputCategory.BUSINESS_CONTEXT,
        "why": InputCategory.BUSINESS_CONTEXT,
        "value": InputCategory.BUSINESS_CONTEXT,
        "stakeholder": InputCategory.BUSINESS_CONTEXT,
        
        # Historical Context
        "historical": InputCategory.HISTORICAL_CONTEXT,
        "history": InputCategory.HISTORICAL_CONTEXT,
        "evolution": InputCategory.HISTORICAL_CONTEXT,
        "migration": InputCategory.HISTORICAL_CONTEXT,
        "replaced": InputCategory.HISTORICAL_CONTEXT,
        
        # Business Rules
        "rule": InputCategory.BUSINESS_RULES,
        "constraint": InputCategory.BUSINESS_RULES,
        "validation": InputCategory.BUSINESS_RULES,
        "requirement": InputCategory.BUSINESS_RULES,
        
        # Accessibility
        "accessibility": InputCategory.ACCESSIBILITY,
        "wcag": InputCategory.ACCESSIBILITY,
        "screen reader": InputCategory.ACCESSIBILITY,
        "keyboard": InputCategory.ACCESSIBILITY,
        
        # Security/Compliance
        "security": InputCategory.SECURITY_COMPLIANCE,
        "compliance": InputCategory.SECURITY_COMPLIANCE,
        "gdpr": InputCategory.SECURITY_COMPLIANCE,
        "pii": InputCategory.SECURITY_COMPLIANCE,
        "audit": InputCategory.SECURITY_COMPLIANCE,
        
        # Performance
        "performance": InputCategory.PERFORMANCE,
        "sla": InputCategory.PERFORMANCE,
        "latency": InputCategory.PERFORMANCE,
        "throughput": InputCategory.PERFORMANCE,
        
        # External Integration
        "external": InputCategory.EXTERNAL_INTEGRATION,
        "integration": InputCategory.EXTERNAL_INTEGRATION,
        "api": InputCategory.EXTERNAL_INTEGRATION,
        "third-party": InputCategory.EXTERNAL_INTEGRATION,
        
        # Team/Ownership
        "owner": InputCategory.TEAM_OWNERSHIP,
        "team": InputCategory.TEAM_OWNERSHIP,
        "contact": InputCategory.TEAM_OWNERSHIP,
        "responsible": InputCategory.TEAM_OWNERSHIP,
        "on-call": InputCategory.TEAM_OWNERSHIP,
        
        # Known Issues
        "issue": InputCategory.KNOWN_ISSUES,
        "limitation": InputCategory.KNOWN_ISSUES,
        "debt": InputCategory.KNOWN_ISSUES,
        "workaround": InputCategory.KNOWN_ISSUES,
        "bug": InputCategory.KNOWN_ISSUES,
        
        # Future Plans
        "future": InputCategory.FUTURE_PLANS,
        "planned": InputCategory.FUTURE_PLANS,
        "roadmap": InputCategory.FUTURE_PLANS,
        "enhancement": InputCategory.FUTURE_PLANS,
        
        # Design Rationale
        "design": InputCategory.DESIGN_RATIONALE,
        "decision": InputCategory.DESIGN_RATIONALE,
        "rationale": InputCategory.DESIGN_RATIONALE,
        "compromise": InputCategory.DESIGN_RATIONALE,
    }
    
    # Priority keywords
    CRITICAL_KEYWORDS = ["business", "purpose", "why", "owner", "sla", "security"]
    IMPORTANT_KEYWORDS = ["rule", "historical", "integration", "issue", "accessibility"]
    
    def __init__(self):
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.HUMAN_INPUT_PATTERNS]
    
    def detect_category(self, section_title: str, context: str = "") -> InputCategory:
        """Detect the category of a human input section."""
        combined = f"{section_title} {context}".lower()
        
        for keyword, category in self.SECTION_CATEGORY_MAP.items():
            if keyword in combined:
                return category
        
        return InputCategory.BUSINESS_CONTEXT  # Default
    
    def detect_priority(self, section_title: str, category: InputCategory) -> QuestionPriority:
        """Determine the priority of a question."""
        title_lower = section_title.lower()
        
        # Critical sections
        if any(kw in title_lower for kw in self.CRITICAL_KEYWORDS):
            return QuestionPriority.CRITICAL
        
        # Important sections
        if any(kw in title_lower for kw in self.IMPORTANT_KEYWORDS):
            return QuestionPriority.IMPORTANT
        
        # Category-based priority
        if category in [InputCategory.BUSINESS_CONTEXT, InputCategory.SECURITY_COMPLIANCE]:
            return QuestionPriority.CRITICAL
        elif category in [InputCategory.BUSINESS_RULES, InputCategory.TEAM_OWNERSHIP]:
            return QuestionPriority.IMPORTANT
        
        return QuestionPriority.OPTIONAL
    
    def extract_sections_from_template(self, template_content: str) -> list[HumanInputSection]:
        """
        Extract all human-input sections from a template.
        
        Args:
            template_content: Markdown template content
            
        Returns:
            List of HumanInputSection objects
        """
        sections = []
        
        # Parse markdown into sections
        lines = template_content.split('\n')
        current_section_title = ""
        current_section_id = ""
        current_section_content = []
        section_start_line = 0
        
        for i, line in enumerate(lines):
            # Detect section headers
            header_match = re.match(r'^(#{1,4})\s+(.+)$', line)
            
            if header_match:
                # Process previous section if any
                if current_section_title and current_section_content:
                    section_text = '\n'.join(current_section_content)
                    detected = self._detect_human_input_in_section(
                        current_section_id,
                        current_section_title,
                        section_text
                    )
                    if detected:
                        sections.append(detected)
                
                # Start new section
                level = len(header_match.group(1))
                current_section_title = header_match.group(2).strip()
                current_section_id = self._generate_section_id(current_section_title, i)
                current_section_content = []
                section_start_line = i
            else:
                current_section_content.append(line)
        
        # Process last section
        if current_section_title and current_section_content:
            section_text = '\n'.join(current_section_content)
            detected = self._detect_human_input_in_section(
                current_section_id,
                current_section_title,
                section_text
            )
            if detected:
                sections.append(detected)
        
        return sections
    
    def _generate_section_id(self, title: str, line_number: int) -> str:
        """Generate a unique section ID."""
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        return f"{slug}-{line_number}"
    
    def _detect_human_input_in_section(
        self, 
        section_id: str,
        section_title: str, 
        section_content: str
    ) -> Optional[HumanInputSection]:
        """
        Detect if a section requires human input.
        
        Returns HumanInputSection if human input needed, None otherwise.
        """
        # Check for human input markers
        has_human_marker = False
        placeholder_text = ""
        
        for pattern in self.compiled_patterns:
            match = pattern.search(section_content)
            if match:
                has_human_marker = True
                if match.groups():
                    placeholder_text = match.group(1)
                break
        
        # Also check for ❓ marker anywhere
        if "❓" in section_content:
            has_human_marker = True
        
        if not has_human_marker:
            return None
        
        # Detect category and priority
        category = self.detect_category(section_title, section_content)
        priority = self.detect_priority(section_title, category)
        
        # Generate appropriate question
        question, follow_ups, examples = self._generate_question(
            section_title, category, placeholder_text
        )
        
        return HumanInputSection(
            section_id=section_id,
            section_title=section_title,
            category=category,
            priority=priority,
            template_placeholder=placeholder_text,
            question=question,
            follow_up_prompts=follow_ups,
            examples=examples,
            context_hints=section_content[:200] if len(section_content) > 200 else section_content
        )
    
    def _generate_question(
        self, 
        section_title: str, 
        category: InputCategory,
        placeholder: str
    ) -> tuple[str, list[str], list[str]]:
        """Generate an interview question based on section and category."""
        
        questions_by_category = {
            InputCategory.BUSINESS_CONTEXT: {
                "question": f"What is the **business purpose** of this {section_title.lower()}?",
                "follow_ups": [
                    "What business problem does it solve?",
                    "Which teams or stakeholders benefit from this?",
                    "What would happen if this didn't exist?"
                ],
                "examples": [
                    "This service enables course enrollment for adult learners, supporting the company's key revenue stream.",
                    "Handles payment processing for subscriptions, critical for monthly recurring revenue."
                ]
            },
            InputCategory.HISTORICAL_CONTEXT: {
                "question": f"What is the **history** behind this {section_title.lower()}?",
                "follow_ups": [
                    "When was this built and why?",
                    "Did it replace something else?",
                    "Were there significant changes or migrations?"
                ],
                "examples": [
                    "Built in Q2 2023 to replace legacy PHP enrollment system. Migrated 50K user records.",
                    "Originally part of monolith, extracted as microservice in 2024 refactor."
                ]
            },
            InputCategory.BUSINESS_RULES: {
                "question": f"Why does this **business rule** exist?",
                "follow_ups": [
                    "What prompted this rule?",
                    "Was there an incident or compliance requirement?",
                    "When was it added?"
                ],
                "examples": [
                    "Added after Q1 2023 audit finding - users were bypassing approval workflow.",
                    "Compliance requirement from SOC2 certification in 2022."
                ]
            },
            InputCategory.ACCESSIBILITY: {
                "question": f"What are the **accessibility** requirements for this component?",
                "follow_ups": [
                    "What WCAG level are you targeting (AA/AAA)?",
                    "Has this been tested with screen readers?",
                    "Are there specific keyboard navigation requirements?"
                ],
                "examples": [
                    "WCAG 2.1 AA compliant, tested with NVDA and VoiceOver.",
                    "Keyboard navigation required for all interactive elements."
                ]
            },
            InputCategory.SECURITY_COMPLIANCE: {
                "question": f"What **security or compliance** considerations apply here?",
                "follow_ups": [
                    "Is there PII or sensitive data involved?",
                    "Are there specific regulatory requirements (GDPR, HIPAA, PCI)?",
                    "What access controls are needed?"
                ],
                "examples": [
                    "Handles PII (email, name), subject to GDPR. Data encrypted at rest.",
                    "PCI-DSS compliant for payment card handling."
                ]
            },
            InputCategory.PERFORMANCE: {
                "question": f"What are the **performance** requirements or SLAs?",
                "follow_ups": [
                    "What response time targets exist?",
                    "What's the expected load/volume?",
                    "Are there peak usage periods?"
                ],
                "examples": [
                    "P99 latency must be under 200ms. Peak load during enrollment periods (3x normal).",
                    "SLA: 99.9% uptime, <100ms response time for reads."
                ]
            },
            InputCategory.EXTERNAL_INTEGRATION: {
                "question": f"Tell me about this **external integration**.",
                "follow_ups": [
                    "Who is the vendor/provider?",
                    "What happens when it's unavailable?",
                    "Who do you contact for issues?"
                ],
                "examples": [
                    "Stripe for payments. Circuit breaker if unavailable, support via Stripe dashboard.",
                    "Auth0 for authentication. Fallback to local cache for 5 minutes."
                ]
            },
            InputCategory.TEAM_OWNERSHIP: {
                "question": f"Who **owns** this and who should be contacted?",
                "follow_ups": [
                    "Which team is responsible?",
                    "Who is the technical lead?",
                    "What's the on-call escalation path?"
                ],
                "examples": [
                    "Platform Team owns this. Tech lead: @johndoe. PagerDuty for on-call.",
                    "Backend Team, escalate to #backend-support Slack channel."
                ]
            },
            InputCategory.KNOWN_ISSUES: {
                "question": f"What **known issues or limitations** should developers be aware of?",
                "follow_ups": [
                    "Are there any workarounds in place?",
                    "Is there planned work to address this?",
                    "What's the impact on users?"
                ],
                "examples": [
                    "Known memory leak under high load. Workaround: restart nightly. Fix planned Q2.",
                    "Doesn't support batch operations yet. Create items one at a time for now."
                ]
            },
            InputCategory.FUTURE_PLANS: {
                "question": f"What are the **future plans** for this?",
                "follow_ups": [
                    "Are there planned enhancements?",
                    "Is deprecation planned?",
                    "What's the timeline?"
                ],
                "examples": [
                    "Adding async processing in Q3 2025 (Epic #456).",
                    "Planned migration to GraphQL API in 2026."
                ]
            },
            InputCategory.DESIGN_RATIONALE: {
                "question": f"What was the **rationale** behind this design decision?",
                "follow_ups": [
                    "Were there alternatives considered?",
                    "What trade-offs were made?",
                    "Would you make the same choice today?"
                ],
                "examples": [
                    "Chose SQL over NoSQL for ACID guarantees on financial transactions.",
                    "Synchronous calls chosen for simplicity; will move to async when queue infra ready."
                ]
            }
        }
        
        defaults = {
            "question": f"Please provide additional context for **{section_title}**:",
            "follow_ups": ["What additional details would help other developers?"],
            "examples": []
        }
        
        config = questions_by_category.get(category, defaults)
        
        # Use placeholder if available
        if placeholder:
            config["question"] = f"Please provide: **{placeholder}**"
        
        return config["question"], config["follow_ups"], config["examples"]


class InterviewManager:
    """
    Manages interview sessions for documentation.
    
    Features:
    - Session lifecycle management
    - Question navigation (next, previous, skip)
    - Answer collection and draft generation
    - Progress tracking
    """
    
    def __init__(self):
        self.sessions: dict[str, InterviewSession] = {}
        self.detector = HumanInputDetector()
    
    def start_session(
        self,
        source_file: str,
        template_content: str,
        template_name: str,
        component_type: str,
        priority_filter: Optional[QuestionPriority] = None,
        role: Optional[str | InterviewRole] = None,
        custom_role_profiles: Optional[dict] = None
    ) -> InterviewSession:
        """
        Start a new interview session for a documentation file.
        
        Args:
            source_file: Source file being documented
            template_content: Template or generated doc content
            template_name: Name of the template used
            component_type: Type of component
            priority_filter: Only include questions of this priority or higher
            role: Interview role for filtering questions (string or InterviewRole enum)
            custom_role_profiles: Custom role profiles from .akr-config.json
            
        Returns:
            New InterviewSession
        """
        # Detect human input sections
        all_sections = self.detector.extract_sections_from_template(template_content)
        
        # Get role profile manager (with custom profiles if provided)
        role_manager = get_role_profile_manager(custom_role_profiles)
        
        # Resolve role and get profile
        if role is None:
            interview_role = InterviewRole.GENERAL
        elif isinstance(role, InterviewRole):
            interview_role = role
        else:
            try:
                interview_role = InterviewRole(role)
            except ValueError:
                # Custom role - use GENERAL enum but custom profile
                interview_role = InterviewRole.GENERAL
                logger.info(f"Using custom role: {role}")
        
        role_profile = role_manager.get_profile(role if isinstance(role, str) else interview_role.value)
        
        # Filter by role - separate included and excluded questions
        included_sections = []
        excluded_sections = []
        
        for section in all_sections:
            if role_profile.should_ask(section.category):
                included_sections.append(section)
            else:
                excluded_sections.append(section)
        
        # Filter by priority if specified
        if priority_filter:
            priority_order = [QuestionPriority.CRITICAL, QuestionPriority.IMPORTANT, QuestionPriority.OPTIONAL]
            filter_index = priority_order.index(priority_filter)
            sections = [s for s in included_sections if priority_order.index(s.priority) <= filter_index]
        else:
            sections = included_sections
        
        # Sort by priority (critical first), then by primary/secondary for role
        def sort_key(section: HumanInputSection):
            priority_order = {QuestionPriority.CRITICAL: 0, QuestionPriority.IMPORTANT: 1, QuestionPriority.OPTIONAL: 2}
            primary_bonus = 0 if role_profile.is_primary(section.category) else (
                1 if role_profile.is_secondary(section.category) else 2
            )
            return (priority_order.get(section.priority, 3), primary_bonus)
        
        sections.sort(key=sort_key)
        
        # Create session
        session_id = f"{Path(source_file).stem}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        session = InterviewSession(
            session_id=session_id,
            source_file=source_file,
            template_name=template_name,
            component_type=component_type,
            role=interview_role,
            role_profile=role_profile,
            questions=sections,
            excluded_questions=excluded_sections,
            started_at=datetime.now()
        )
        
        self.sessions[session_id] = session
        logger.info(f"Started interview session {session_id} with {len(sections)} questions "
                   f"for role '{role_profile.display_name}' ({len(excluded_sections)} delegated to other roles)")
        
        return session
    
    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Get an existing session by ID."""
        return self.sessions.get(session_id)
    
    def get_current_question(self, session_id: str) -> Optional[dict]:
        """
        Get the current question in the session.
        
        Returns:
            Question details or None if session complete
        """
        session = self.get_session(session_id)
        if not session or session.is_complete:
            return None
        
        question = session.questions[session.current_index]
        
        return {
            "session_id": session_id,
            "question_number": session.current_index + 1,
            "total_questions": len(session.questions),
            "section_id": question.section_id,
            "section_title": question.section_title,
            "category": question.category.value,
            "priority": question.priority.value,
            "question": question.question,
            "follow_up_prompts": question.follow_up_prompts,
            "examples": question.examples,
            "context_hints": question.context_hints,
            "can_skip": True,
            "progress": session.progress
        }
    
    def submit_answer(
        self, 
        session_id: str, 
        answer: str,
        generate_draft: bool = True
    ) -> dict:
        """
        Submit an answer to the current question.
        
        Args:
            session_id: Session ID
            answer: User's answer text
            generate_draft: Whether to generate polished draft from answer
            
        Returns:
            Result with drafted content if requested
        """
        session = self.get_session(session_id)
        if not session or session.is_complete:
            return {"success": False, "error": "Session not found or complete"}
        
        current_question = session.questions[session.current_index]
        
        # Create answer record
        interview_answer = InterviewAnswer(
            section_id=current_question.section_id,
            raw_answer=answer,
            status=AnswerStatus.ANSWERED,
            timestamp=datetime.now()
        )
        
        # Generate draft if requested
        if generate_draft:
            drafted = self._generate_draft_content(current_question, answer)
            interview_answer.drafted_content = drafted
            interview_answer.status = AnswerStatus.DRAFTED
        
        # Store answer
        session.answers[current_question.section_id] = interview_answer
        
        # Move to next question
        session.current_index += 1
        
        # Check if complete
        if session.is_complete:
            session.completed_at = datetime.now()
        
        return {
            "success": True,
            "section_id": current_question.section_id,
            "section_title": current_question.section_title,
            "raw_answer": answer,
            "drafted_content": interview_answer.drafted_content,
            "is_complete": session.is_complete,
            "progress": session.progress,
            "next_question": self.get_current_question(session_id)
        }
    
    def skip_question(self, session_id: str, reason: str = "Will provide later") -> dict:
        """
        Skip the current question.
        
        Args:
            session_id: Session ID
            reason: Reason for skipping
            
        Returns:
            Result with next question
        """
        session = self.get_session(session_id)
        if not session or session.is_complete:
            return {"success": False, "error": "Session not found or complete"}
        
        current_question = session.questions[session.current_index]
        
        # Create skip record
        interview_answer = InterviewAnswer(
            section_id=current_question.section_id,
            raw_answer="",
            status=AnswerStatus.SKIPPED,
            timestamp=datetime.now(),
            skip_reason=reason
        )
        
        session.answers[current_question.section_id] = interview_answer
        session.current_index += 1
        
        if session.is_complete:
            session.completed_at = datetime.now()
        
        return {
            "success": True,
            "section_id": current_question.section_id,
            "skipped": True,
            "skip_reason": reason,
            "is_complete": session.is_complete,
            "progress": session.progress,
            "next_question": self.get_current_question(session_id)
        }
    
    def get_session_summary(self, session_id: str) -> dict:
        """Get a summary of the interview session including questions for other roles."""
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}
        
        answered_sections = []
        skipped_sections = []
        drafted_content = {}
        
        for section_id, answer in session.answers.items():
            if answer.status == AnswerStatus.SKIPPED:
                skipped_sections.append({
                    "section_id": section_id,
                    "reason": answer.skip_reason
                })
            else:
                answered_sections.append({
                    "section_id": section_id,
                    "raw_answer": answer.raw_answer,
                    "has_draft": answer.drafted_content is not None
                })
                if answer.drafted_content:
                    drafted_content[section_id] = answer.drafted_content
        
        # Build questions delegated to other roles (excluded from this role's interview)
        questions_for_other_roles = []
        if session.excluded_questions and session.role_profile:
            for excluded_q in session.excluded_questions:
                suggested_role = session.role_profile.get_delegation_target(excluded_q.category)
                questions_for_other_roles.append({
                    "section_id": excluded_q.section_id,
                    "section_title": excluded_q.section_title,
                    "category": excluded_q.category.value,
                    "priority": excluded_q.priority.value,
                    "question": excluded_q.question,
                    "suggested_role": suggested_role or "Another team member"
                })
        
        return {
            "success": True,
            "session_id": session_id,
            "source_file": session.source_file,
            "template_name": session.template_name,
            "component_type": session.component_type,
            "role": session.role.value,
            "role_display_name": session.role_profile.display_name if session.role_profile else "General",
            "is_complete": session.is_complete,
            "progress": session.progress,
            "answered_sections": answered_sections,
            "skipped_sections": skipped_sections,
            "drafted_content": drafted_content,
            "questions_for_other_roles": questions_for_other_roles,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None
        }
    
    def _generate_draft_content(
        self, 
        question: HumanInputSection, 
        raw_answer: str
    ) -> str:
        """
        Generate polished draft content from user's raw answer.
        
        This creates well-formatted markdown based on the section category
        and the user's input.
        """
        # Clean up the answer
        answer = raw_answer.strip()
        
        # Format based on category
        if question.category == InputCategory.BUSINESS_CONTEXT:
            return self._format_business_context(answer)
        elif question.category == InputCategory.HISTORICAL_CONTEXT:
            return self._format_historical_context(answer)
        elif question.category == InputCategory.BUSINESS_RULES:
            return self._format_business_rule(answer)
        elif question.category == InputCategory.TEAM_OWNERSHIP:
            return self._format_team_ownership(answer)
        elif question.category == InputCategory.KNOWN_ISSUES:
            return self._format_known_issues(answer)
        elif question.category == InputCategory.SECURITY_COMPLIANCE:
            return self._format_security_compliance(answer)
        elif question.category == InputCategory.PERFORMANCE:
            return self._format_performance(answer)
        else:
            return answer  # Return as-is for other categories
    
    def _format_business_context(self, answer: str) -> str:
        """Format business context answer."""
        lines = answer.split('\n')
        if len(lines) == 1:
            return answer
        
        # Try to structure if multi-line
        formatted = []
        for line in lines:
            line = line.strip()
            if line:
                if line.startswith('-') or line.startswith('*'):
                    formatted.append(line)
                else:
                    formatted.append(f"- {line}")
        
        return '\n'.join(formatted) if formatted else answer
    
    def _format_historical_context(self, answer: str) -> str:
        """Format historical context answer."""
        # Look for date patterns and format nicely
        return answer
    
    def _format_business_rule(self, answer: str) -> str:
        """Format business rule answer."""
        return answer
    
    def _format_team_ownership(self, answer: str) -> str:
        """Format team ownership answer."""
        # Try to extract structured info
        result = []
        
        # Look for team mentions
        if 'team' in answer.lower():
            result.append(f"**Team:** {answer}")
        
        # Look for contact info
        if '@' in answer or 'slack' in answer.lower():
            return f"**Contact:** {answer}"
        
        return answer if not result else '\n'.join(result)
    
    def _format_known_issues(self, answer: str) -> str:
        """Format known issues answer."""
        lines = answer.split('\n')
        formatted = []
        
        for line in lines:
            line = line.strip()
            if line:
                if not line.startswith('- ⚠️') and not line.startswith('-'):
                    formatted.append(f"- ⚠️ {line}")
                else:
                    formatted.append(line)
        
        return '\n'.join(formatted) if formatted else answer
    
    def _format_security_compliance(self, answer: str) -> str:
        """Format security/compliance answer."""
        return answer
    
    def _format_performance(self, answer: str) -> str:
        """Format performance answer."""
        return answer
    
    def end_session(self, session_id: str) -> Optional[InterviewSession]:
        """End and remove a session, returning its final state."""
        return self.sessions.pop(session_id, None)


# Module-level instance for use across the MCP server
_interview_manager: Optional[InterviewManager] = None


def get_interview_manager() -> InterviewManager:
    """Get or create the interview manager instance."""
    global _interview_manager
    if _interview_manager is None:
        _interview_manager = InterviewManager()
    return _interview_manager


# =============================================================================
# Public API Functions for MCP Tools
# =============================================================================

def start_documentation_interview(
    source_file: str,
    template_content: str,
    template_name: str,
    component_type: str,
    priority_filter: str = None,
    role: str = None,
    custom_role_profiles: Optional[dict] = None
) -> dict:
    """
    Start an interactive interview session for documentation.
    
    Args:
        source_file: Path to the source file being documented
        template_content: Template or generated documentation content
        template_name: Name of the template used
        component_type: Type of component (services, ui, database)
        priority_filter: Filter questions by priority ('critical', 'important', 'optional')
        role: Interview role for question filtering ('technical_lead', 'developer', 
              'product_owner', 'qa_tester', 'scrum_master', 'general'). 
              Defaults to 'general' (all questions).
        custom_role_profiles: Optional custom role profiles from .akr-config.json
        
    Returns:
        Session information with first question
    """
    manager = get_interview_manager()
    
    # Convert priority filter
    priority_enum = None
    if priority_filter:
        try:
            priority_enum = QuestionPriority(priority_filter)
        except ValueError:
            pass
    
    session = manager.start_session(
        source_file=source_file,
        template_content=template_content,
        template_name=template_name,
        component_type=component_type,
        priority_filter=priority_enum,
        role=role,
        custom_role_profiles=custom_role_profiles
    )
    
    first_question = manager.get_current_question(session.session_id)
    
    # Build role info for response
    role_info = {
        "role": session.role.value,
        "role_display_name": session.role_profile.display_name if session.role_profile else "General",
        "role_description": session.role_profile.description if session.role_profile else "All questions (no filtering)"
    }
    
    return {
        "success": True,
        "session_id": session.session_id,
        "source_file": source_file,
        "template_name": template_name,
        **role_info,
        "total_questions": len(session.questions),
        "questions_delegated_to_others": len(session.excluded_questions),
        "questions_by_priority": {
            "critical": sum(1 for q in session.questions if q.priority == QuestionPriority.CRITICAL),
            "important": sum(1 for q in session.questions if q.priority == QuestionPriority.IMPORTANT),
            "optional": sum(1 for q in session.questions if q.priority == QuestionPriority.OPTIONAL)
        },
        "first_question": first_question,
        "message": f"Interview started for {role_info['role_display_name']} with {len(session.questions)} questions. "
                   f"{len(session.excluded_questions)} questions delegated to other roles."
    }


def get_next_interview_question(session_id: str) -> dict:
    """
    Get the current/next question in the interview.
    
    Args:
        session_id: Active session ID
        
    Returns:
        Current question details or completion status
    """
    manager = get_interview_manager()
    question = manager.get_current_question(session_id)
    
    if question is None:
        # Session complete or not found
        session = manager.get_session(session_id)
        if session is None:
            return {"success": False, "error": f"Session not found: {session_id}"}
        else:
            summary = manager.get_session_summary(session_id)
            return {
                "success": True,
                "is_complete": True,
                "message": "All questions have been addressed!",
                "summary": summary
            }
    
    return {
        "success": True,
        "is_complete": False,
        **question
    }


def submit_interview_answer(
    session_id: str,
    answer: str,
    generate_draft: bool = True
) -> dict:
    """
    Submit an answer to the current interview question.
    
    Args:
        session_id: Active session ID
        answer: User's answer to the question
        generate_draft: Auto-generate polished draft from answer
        
    Returns:
        Result with drafted content and next question
    """
    manager = get_interview_manager()
    return manager.submit_answer(session_id, answer, generate_draft)


def skip_interview_question(
    session_id: str,
    reason: str = "Will provide later"
) -> dict:
    """
    Skip the current question to answer later.
    
    Args:
        session_id: Active session ID
        reason: Reason for skipping (e.g., "Need to check with team lead")
        
    Returns:
        Result with next question
    """
    manager = get_interview_manager()
    return manager.skip_question(session_id, reason)


def get_interview_progress(session_id: str) -> dict:
    """
    Get current interview progress and summary.
    
    Args:
        session_id: Active session ID
        
    Returns:
        Progress statistics and answered questions
    """
    manager = get_interview_manager()
    return manager.get_session_summary(session_id)


def end_documentation_interview(session_id: str) -> dict:
    """
    End the interview session and get all drafted content.
    
    Args:
        session_id: Active session ID
        
    Returns:
        Final summary with all drafted content for insertion
    """
    manager = get_interview_manager()
    summary = manager.get_session_summary(session_id)
    
    if not summary.get("success"):
        return summary
    
    # End the session
    manager.end_session(session_id)
    
    summary["session_ended"] = True
    summary["message"] = "Interview complete. Use the drafted_content to update your documentation."
    
    return summary
