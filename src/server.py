import os
import sys
import logging
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource, ResourceTemplate
from mcp.server.models import (
    InitializationOptions,
    ServerCapabilities
)


# Import AKR resource manager and resolver
from resources import AKRResourceManager, ResourceCategory, create_resource_manager
from resources.template_resolver import TemplateResolver, create_template_resolver

# ==================== FIXED: Remove invalid imports ====================
# Import workspace tools
from tools.workspace import create_workspace_manager
from tools.config_utils import validate_enforcement_config

# CANONICAL IMPORTS (used consistently throughout)
from tools.enforcement_tool import enforce_and_fix
from tools.enforcement_tool_types import FileMetadata
from tools.write_operations import (
    write_documentation,
    write_documentation_async,
    update_documentation_sections_and_commit,
    update_documentation_sections_and_commit_async
)
from tools.progress_tracker import ProgressTracker
from tools.operation_metrics import OperationMetrics
from tools.workflow_tracker import WorkflowTracker
from tools.duplicate_detector import DuplicateDetector
from tools.template_schema_builder import TEMPLATE_BASELINE_SECTIONS
from tools.code_analytics import CodeAnalyzer

# ---- Lazy managers (avoid heavy work during import/startup) ----
resource_manager = None  # type: ignore

def get_resource_manager():
    """
    Create the AKRResourceManager on first use and return it.
    Safe to call repeatedly.
    """
    global resource_manager
    if resource_manager is None:
        # requires: from resources import create_resource_manager
        resource_manager = create_resource_manager()
    return resource_manager


def get_template_resolver():
    """
    Create the TemplateResolver on first use and return it.
    Safe to call repeatedly.
    """
    global template_resolver
    if template_resolver is None:
        # Create TemplateResolver with configured settings
        repo_root = Path(__file__).parent.parent  # src/.. → repo root
        cfg = load_config() if config is None else config
        template_resolver = create_template_resolver(repo_root, cfg)
    return template_resolver


# ==================== PHASE 3: SESSION CACHE ====================
session_cache = None  # type: ignore

def get_session_cache():
    """
    Create SessionCache on first use and return it.
    Caches validation results across tool calls for 20-30% speedup.
    """
    global session_cache
    if session_cache is None:
        from tools.session_cache import SessionCache
        session_cache = SessionCache(ttl_seconds=1800, max_entries=1000)
    return session_cache
# ================================================================



# Don't import load_config - we'll implement it inline
# from tools.config import load_config
# ======================================================================

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("akr-mcp-server")


# ==================== NEW CODE: FAST MODE DETECTION ====================
# Check for fast mode flag from environment variable
FAST_MODE = os.getenv('AKR_FAST_MODE', 'false').lower() == 'true'
SKIP_INITIALIZATION = os.getenv('AKR_SKIP_INITIALIZATION', 'false').lower() == 'true'
WRITE_OPS_ENABLED = os.getenv('AKR_ENABLE_WRITE_OPS', 'false').lower() == 'true'

logger.info(f"🚀 Server starting in mode: FAST_MODE={FAST_MODE}, SKIP_INIT={SKIP_INITIALIZATION}")
logger.info("Write operations: %s", "ENABLED" if WRITE_OPS_ENABLED else "DISABLED (default)")
# ======================================================================

# Create MCP server instance
server = Server("akr-documentation-server")

# Global state (initialized lazily in fast mode)
resource_manager: Optional[AKRResourceManager] = None
template_resolver: Optional[TemplateResolver] = None
workspace_manager: Optional[object] = None
config: Optional[dict] = None
enforcement_logger = None
workflow_tracker: Optional[WorkflowTracker] = None
duplicate_detector: Optional[DuplicateDetector] = None


# ==================== NEW CODE: CONFIG LOADER FUNCTION ====================
def load_config() -> dict:
    """
    Load server configuration from config.json.
    
    Returns:
        Configuration dictionary, or default config if file not found.
    """
    try:
        # Get path to config.json (in akr-mcp-server root)
        server_root = Path(__file__).parent.parent
        config_path = server_root / "config.json"
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            logger.debug(f"Configuration loaded from {config_path}")
            return config_data
        else:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
    
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}
# ======================================================================


# ==================== NEW CODE: ENFORCEMENT TELEMETRY ====================
def init_enforcement_telemetry(log_path: str = "logs/enforcement.jsonl"):
    global enforcement_logger
    try:
        from tools.enforcement_logger import EnforcementLogger
        enforcement_logger = EnforcementLogger(log_path)
    except Exception as e:
        logger.warning(f"Could not init enforcement telemetry: {e}")
# ======================================================================


# ==================== NEW CODE: LAZY INITIALIZATION FUNCTION ====================
def ensure_initialized():
    """
    Initialize resources only when first needed (lazy loading).
    This function is called before any tool/resource is accessed,
    but skipped during server startup in fast mode.
    """
    global resource_manager, template_resolver, workspace_manager, config, workflow_tracker, duplicate_detector
    
    if resource_manager is not None:
        # Already initialized
        return
    
    logger.info("⏳ Lazy-initializing resources...")
    
    try:
        # Load configuration
        config = load_config()
        logger.info("✅ Configuration loaded")

        valid, errors = validate_enforcement_config(config)
        if not valid:
            logger.error(f"Invalid enforcement config: {errors}")
            raise ValueError(f"Enforcement config validation failed: {errors}")

        init_enforcement_telemetry()
        
        # Create workflow tracker
        workflow_tracker = WorkflowTracker(ttl_seconds=1800)  # 30 minutes TTL
        logger.info("✅ Workflow tracker initialized")
        
        # Create duplicate detector
        duplicate_detector = DuplicateDetector()
        logger.info("✅ Duplicate detector initialized")
        
        # Create resource manager (minimal, no scanning)
        resource_manager = create_resource_manager()
        logger.info("✅ Resource manager created")
        
        # Create template resolver (Phase 1 - TemplateResolver)
        repo_root = Path(__file__).parent.parent
        template_resolver = create_template_resolver(repo_root, config)
        logger.info("✅ Template resolver created (3-layer loading enabled)")
        
        # Create workspace manager (no workspace scan in fast mode)
        if not FAST_MODE:
            workspace_manager = create_workspace_manager(load_config=False)
            logger.info("✅ Workspace manager created")
        
        logger.info("✅ All resources initialized")
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        raise
# ================================================================================


@server.list_resources()
async def list_resources() -> list[Resource]:
    """
    List all available AKR resources (templates, charters).
    
    Uses TemplateResolver (Phase 1) with 3-layer loading:
    1. Submodule (templates/core/) - primary
    2. Local overrides (akr_content/templates/) - fallback
    3. Remote HTTP fetch (optional) - preview
    """
    ensure_initialized()
    resolver = get_template_resolver()
    
    resources: list[Resource] = []
    
    # Add all available templates as resources
    template_ids = resolver.list_templates()
    for template_id in template_ids:
        uri = f"akr://template/{template_id}"
        resources.append(
            Resource(
                uri=uri,
                name=f"Template: {template_id}",
                description=f"AKR documentation template: {template_id}",
                mimeType="text/markdown",
            )
        )
    
    # Add charters as resources  
    # (Note: charters loaded from akr_content/ via legacy AKRResourceManager)
    mgr = get_resource_manager()
    for charter in mgr.list_charters():
        uri = f"akr://charter/{charter.name}"
        resources.append(
            Resource(
                uri=uri,
                name=f"Charter: {charter.name}",
                description=charter.description,
                mimeType="text/markdown",
            )
        )
    
    logger.info(f"✅ Listed {len(resources)} resources ({len(template_ids)} templates + {len(mgr.list_charters())} charters)")
    return resources


@server.read_resource(uri_pattern="akr://template/{template_id}")
async def read_template_resource(uri: str) -> str:
    """
    Read a specific template resource.
    
    Args:
        uri: Resource URI (e.g., akr://template/lean_baseline_service_template)
    
    Returns:
        Template content as markdown
    """
    ensure_initialized()
    resolver = get_template_resolver()
    
    # Extract template_id from URI
    template_id = uri.replace("akr://template/", "")
    
    content = resolver.get_template(template_id)
    if content:
        logger.debug(f"✅ Read template resource: {uri}")
        return content
    
    # Template not found - return helpful error
    available = resolver.list_templates()
    error_msg = f"Template not found: {template_id}\n\nAvailable templates:\n"
    error_msg += "\n".join(f"  - akr://template/{t}" for t in sorted(available))
    return error_msg


@server.read_resource(uri_pattern="akr://charter/{domain}")
async def read_charter_resource(uri: str) -> str:
    """
    Read a specific charter resource.
    
    Args:
        uri: Resource URI (e.g., akr://charter/backend)
    
    Returns:
        Charter content as markdown
    """
    ensure_initialized()
    mgr = get_resource_manager()
    
    # Extract domain from URI
    domain = uri.replace("akr://charter/", "")
    
    charter = mgr.get_charter(domain)
    if charter:
        content = charter.load_content()
        logger.debug(f"✅ Read charter resource: {uri}")
        return content
    
    # Charter not found - return helpful error
    available_domains = ["ui", "backend", "database"]
    error_msg = f"Charter not found for domain: {domain}\n\nAvailable charters:\n"
    error_msg += "\n".join(f"  - akr://charter/{d}" for d in available_domains)
    return error_msg


@server.list_resource_templates()
async def list_resource_templates() -> list[ResourceTemplate]:
    """
    List MCP resource templates that allow clients to construct resource URIs dynamically.
    
    MCP clients (like Copilot Chat) use these templates to discover how to construct
    valid resource URIs without enumerating all resources first.
    
    Returns:
        List of ResourceTemplate objects with uriTemplate patterns
    """
    ensure_initialized()
    
    templates = [
        ResourceTemplate(
            uriTemplate="akr://template/{id}",
            name="AKR Documentation Templates",
            description="Access AKR documentation templates by ID (e.g., lean_baseline_service_template, standard_service_template)"
        ),
        ResourceTemplate(
            uriTemplate="akr://charter/{domain}",
            name="AKR Charters",
            description="Access AKR domain charters by domain: backend, ui, database"
        )
    ]
    
    logger.info(f"✅ Listed {len(templates)} resource templates")
    return templates


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available AKR documentation tools."""
    tools = [
        Tool(
            name="extract_code_context",
            description=(
                "Extract code context (methods, classes, imports, SQL schema) from source files. "
                "Uses deterministic extractors for C# and SQL DDL files. "
                "Returns structured metadata for documentation and analysis workflows."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to repository or source file to analyze"
                    },
                    "extraction_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Extraction types: methods, classes, imports, sql_tables"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language override (csharp, sql). Auto-detects if omitted"
                    },
                    "file_filter": {
                        "type": "string",
                        "description": "File pattern filter (e.g., *.cs)"
                    }
                },
                "required": ["repo_path"]
            }
        ),
        Tool(
            name="generate_documentation",
            description=(
                "**PRIMARY ENTRY POINT for new documentation.** "
                "Creates AKR-compliant documentation stubs with ❓ placeholders for human input. "
                "This tool MUST be used before write_documentation for new files. "
                "\n\n"
                "**Workflow:** generate_documentation → human review → write_documentation\n"
                "**DO NOT** generate full documentation content yourself—this tool creates structured stubs."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "component_name": {
                        "type": "string",
                        "description": "Name of the component to document"
                    },
                    "component_type": {
                        "type": "string",
                        "enum": ["ui_component", "service", "database", "table"],
                        "description": "Type of component (ui_component, service, database, table)"
                    },
                    "template": {
                        "type": "string",
                        "description": "Template filename or shortcut (optional; defaults based on component_type)"
                    },
                    "allowWrites": {
                        "type": "boolean",
                        "default": False,
                        "description": "Must be true to allow file writes"
                    }
                },
                "required": ["component_name", "component_type"]
            }
        ),
        Tool(
            name="validate_documentation",
            description=(
                "Validate documentation against template standards using tier-level rules. "
                "Returns structured violations, completeness estimate, and optional auto-fixes. "
                "Default: dry_run=true (returns diff without writing)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_path": {
                        "type": "string",
                        "description": "Path to the documentation file to validate (e.g., docs/API.md)"
                    },
                    "template_id": {
                        "type": "string",
                        "description": "Template ID to validate against (e.g., lean_baseline_service_template)"
                    },
                    "tier_level": {
                        "type": "string",
                        "enum": ["TIER_1", "TIER_2", "TIER_3"],
                        "default": "TIER_2",
                        "description": "Validation strictness: TIER_1=strict (≥80% complete), TIER_2=moderate (≥60%), TIER_3=lenient (≥30%)"
                    },
                    "auto_fix": {
                        "type": "boolean",
                        "default": False,
                        "description": "Attempt auto-fixes for common violations"
                    },
                    "dry_run": {
                        "type": "boolean",
                        "default": True,
                        "description": "If true with auto_fix, return diff without writing to file"
                    }
                },
                "required": ["doc_path", "template_id"]
            }
        ),
        Tool(
            name="get_charter",
            description="Get the AKR charter for a specific documentation domain",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "enum": ["ui", "backend", "database"],
                        "description": "Documentation domain (ui, backend, database)"
                    }
                },
                "required": ["domain"]
            }
        ),
    ]

    write_tools = [
        Tool(
            name="generate_and_write_documentation",
            description=(
                "**UNIFIED WORKFLOW:** Generate and write AKR documentation in a single operation. "
                "Combines scaffolding (full template structure) with intelligent placeholder replacement and writes the file. "
                "\n\n"
                "**What it does:**\n"
                "1. Auto-detects project type (backend/ui/database) or uses component_type\n"
                "2. Selects appropriate template (lean_baseline_service_template.md, ui_component_template.md, etc.)\n"
                "3. Generates full template structure with all sections\n"
                "4. Replaces placeholders ([SERVICE_NAME], [DOMAIN], dates, etc.)\n"
                "5. Adds source file metadata as comments\n"
                "6. Validates and writes file using enforcement gates\n"
                "\n"
                "**Output:** Complete template with structure + placeholders ready for human enhancement.\n"
                "**Use when:** You want to create documentation in one step instead of scaffold → generate → write."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "component_name": {
                        "type": "string",
                        "description": "Name of the component to document (e.g., 'EnrollmentService', 'Button', 'Courses')"
                    },
                    "source_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of source files to document (e.g., ['Domain/Services/IEnrollmentService.cs', 'Controllers/EnrollmentsController.cs'])"
                    },
                    "component_type": {
                        "type": "string",
                        "enum": ["service", "ui_component", "table", "api"],
                        "description": "Type of component (optional; auto-detected from project structure if not provided)"
                    },
                    "template": {
                        "type": "string",
                        "description": "Template filename or shortcut (optional; auto-selected based on component_type/project_type)"
                    },
                    "doc_path": {
                        "type": "string",
                        "description": "Output documentation path (optional; auto-determined based on project type, e.g., 'docs/services/EnrollmentService_doc.md')"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether to overwrite existing file"
                    },
                    "allowWrites": {
                        "type": "boolean",
                        "default": False,
                        "description": "Must be true to allow file writes"
                    }
                },
                "required": ["component_name"]
            }
        ),
        Tool(
            name="write_documentation",
            description=(
                "Writes validated documentation to disk with git commit. "
                "**IMPORTANT:** For NEW documentation, use generate_documentation first. "
                "This tool is for:\n"
                "- Writing AI-generated stubs from generate_documentation\n"
                "- Updating existing documentation files\n"
                "- Writing documentation you've manually created (use force_workflow_bypass=true)\n"
                "\n"
                "Performs template enforcement validation before writing."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Markdown content (REQUIRED)"},
                    "source_file": {"type": "string", "description": "Repo-relative source code file path, e.g. src/handler.cs"},
                    "doc_path": {"type": "string", "description": "Repo-relative output doc path, e.g. docs/api.md"},
                    "template": {"type": "string", "description": "Template filename or shortcut, e.g. lean_baseline_service_template.md or lean"},
                    "component_type": {"type": "string", "description": "Component type, e.g. service, controller"},
                    "overwrite": {"type": "boolean", "default": False},
                    "force_workflow_bypass": {
                        "type": "boolean",
                        "default": False,
                        "description": "Allow direct write for new files without generate_documentation (emergency use)"
                    },
                    "allowWrites": {
                        "type": "boolean",
                        "default": False,
                        "description": "Must be true to allow file writes"
                    }
                },
                "required": ["content", "source_file", "doc_path"]
            }
        ),
        Tool(
            name="update_documentation_sections",
            description="Update specific doc sections with enforcement gate. Surgical updates: pass section names + new content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_path": {"type": "string", "description": "Repo-relative doc path, e.g. docs/api.md"},
                    "section_updates": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                        "description": "Map of section_id to new content"
                    },
                    "template": {"type": "string", "description": "Template filename or shortcut, e.g. lean_baseline_service_template.md or lean"},
                    "source_file": {"type": "string", "description": "Repo-relative source code file path"},
                    "component_type": {"type": "string", "description": "Component type, e.g. service, controller"},
                    "add_changelog": {"type": "boolean", "default": True},
                    "overwrite": {"type": "boolean", "default": True},
                    "allowWrites": {
                        "type": "boolean",
                        "default": False,
                        "description": "Must be true to allow file writes"
                    }
                },
                "required": ["doc_path", "section_updates"]
            }
        )
    ]

    if WRITE_OPS_ENABLED:
        tools.extend(write_tools)
    else:
        logger.info("Write operations disabled; write tools not registered")

    return tools


# ============ PROGRESS TRACKING HELPERS ============

# Global progress token storage for current operation
_progress_token: Optional[str] = None

async def send_progress_notification(progress: int, message: str) -> None:
    """
    Send a progress notification to the client via real MCP notifications/progress API.
    
    This is called by ProgressTracker to update the client on operation progress.
    If no progress token is set, falls back to debug logging.
    
    Args:
        progress: Progress percentage (0-100)
        message: Status message to display with stage indicator
    """
    global _progress_token
    
    logger.debug(f"Progress: {progress}% - {message}")
    
    if not _progress_token:
        return  # Progress tracking not active for this operation
    
    try:
        await server.send_notification(
            "notifications/progress",
            {
                "progressToken": _progress_token,
                "progress": progress,
                "total": 100,
                "message": message
            }
        )
    except Exception as e:
        logger.warning(f"Failed to send progress notification: {e}")


def _get_stub_title(component_name: str, component_type: str, template: str) -> str:
    if template == "ui_component_template.md" or component_type == "ui_component":
        return f"# Component: {component_name}"
    if template == "table_doc_template.md" or component_type == "table":
        return f"# Table: {component_name}"
    if template == "embedded_database_template.md" or component_type == "database":
        return f"# Database: {component_name}"
    return f"# Service: {component_name}"


def _section_placeholder(section_name: str) -> str:
    if section_name == "Business Rules":
        return (
            "| Rule ID | Description | Why It Exists | Since When |\n"
            "|---|---|---|---|\n"
            "| ❓ BR-XXX-001 | [HUMAN: Add rule] | [HUMAN: Rationale] | [HUMAN: Date] |"
        )
    if section_name == "Questions & Gaps":
        return "- ❓ [HUMAN: Add open question]\n- ❓ [HUMAN: Add assumption]"
    if section_name == "Quick Reference (TL;DR)":
        return "❓ [HUMAN: Add brief 1-2 sentence summary]"
    if section_name == "API Contract (AI Context)":
        return "❓ [HUMAN: List endpoints, request/response, and auth requirements]"
    if "Validation Rules" in section_name:
        return "❓ [HUMAN: Summarize validation rules or note none]"
    return f"❓ [HUMAN: Add {section_name} details]"


def _detect_project_type(workspace_root: Path) -> str:
    """
    Auto-detect project type by checking .akr-config.json or file patterns
    
    Returns: "backend", "ui", "database", or "unknown"
    """
    # Strategy 1: Read .akr-config.json
    config_path = workspace_root / ".akr-config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
                # Check for explicit domain field (root level)
                if "domain" in config_data:
                    domain = config_data["domain"].lower()
                    if domain in ["backend", "ui", "database"]:
                        return domain
                
                # Check for projectType field (root level)
                if "projectType" in config_data:
                    proj_type = config_data["projectType"].lower()
                    if proj_type in ["backend", "ui", "database"]:
                        return proj_type
                
                # Check for nested project.type field
                if "project" in config_data and isinstance(config_data["project"], dict):
                    if "type" in config_data["project"]:
                        proj_type = config_data["project"]["type"].lower()
                        if proj_type in ["backend", "ui", "database"]:
                            return proj_type
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Could not read .akr-config.json: {e}")
    
    # Strategy 2: File pattern detection
    # Check for backend indicators
    if list(workspace_root.rglob("*.csproj")) or list(workspace_root.rglob("*.sln")):
        return "backend"
    
    # Check for UI indicators
    package_json = workspace_root / "package.json"
    if package_json.exists():
        if (workspace_root / "src" / "components").exists() or \
           (workspace_root / "src" / "pages").exists():
            return "ui"
        return "backend"  # Node.js backend
    
    # Check for database indicators
    if list(workspace_root.rglob("*.sqlproj")):
        return "database"
    
    return "unknown"


def _replace_placeholders(content: str, module_name: str, project_type: str, source_files: list[str]) -> str:
    """Replace template placeholders with actual values"""
    # Replace common placeholders
    content = content.replace("[SERVICE_NAME]", module_name)
    content = content.replace("[COMPONENT_NAME]", module_name)
    content = content.replace("[TABLE_NAME]", module_name)
    content = content.replace("[FEATURE_NAME]", module_name)
    
    # Replace placeholders with spaces
    content = content.replace("[Component Name]", module_name)
    content = content.replace("[Service Name]", module_name)
    content = content.replace("[Table Name]", module_name)
    
    # Replace camelCase/PascalCase placeholders
    content = content.replace("[ComponentName]", module_name)
    content = content.replace("[ServiceName]", module_name)
    content = content.replace("[TableName]", module_name)
    
    # Replace date placeholders
    today = datetime.now().strftime("%Y-%m-%d")
    content = content.replace("[YYYY-MM-DD]", today)
    content = content.replace("YYYY-MM-DD", today)
    
    # Replace domain placeholder with project type
    domain_map = {
        "backend": "Backend",
        "ui": "UI",
        "database": "Database"
    }
    content = content.replace("[DOMAIN]", domain_map.get(project_type, "Unknown"))
    
    # Add source files comment if provided
    if source_files:
        files_list = "\n".join(f"- {f}" for f in source_files)
        source_comment = f"\n<!-- Source files used for documentation:\n{files_list}\n-->\n"
        # Insert after front matter if it exists
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = f"---{parts[1]}---{source_comment}{parts[2]}"
        else:
            # No front matter, add comment at the top
            content = source_comment + content
    
    return content


def _build_stub_content(
    component_name: str,
    component_type: str,
    template: str,
    baseline_sections: list[str],
) -> str:
    lines = [
        "---",
        f"component: {component_name}",
        f"componentType: {component_type}",
        "status: draft",
        "version: 0.1.0",
        f"lastUpdated: {datetime.now().strftime('%Y-%m-%d')}",
        "domain: TBD",
        "feature: TBD",
        "layer: TBD",
        "priority: medium",
        "---",
        "",
        _get_stub_title(component_name, component_type, template),
        "",
    ]

    for section_name in baseline_sections:
        lines.append(f"## {section_name}")
        lines.append(_section_placeholder(section_name))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _resolve_template_name(template: str) -> tuple[Optional[str], list[str]]:
    """Resolve template name shortcuts to a concrete filename.

    Returns (resolved_name, matches). If resolved_name is None and matches
    is non-empty, the input is ambiguous.
    """
    rm = get_resource_manager()
    if hasattr(rm, "resolve_template_filename"):
        return rm.resolve_template_filename(template)
    return template, []


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute an AKR documentation tool."""
    ensure_initialized()

    global config
    cfg = config
    
    logger.info(f"🔧 Tool called: {name}")
    
    if name == "extract_code_context":
        repo_path = arguments.get("repo_path")
        extraction_types = arguments.get("extraction_types")
        
        try:
            analyzer = CodeAnalyzer()
            result = analyzer.analyze(
                file_path=repo_path,
                extraction_types=extraction_types
            )
            
            result["metadata"]["server_version"] = "0.2.0"
            result["metadata"]["extractor"] = "CodeAnalyzer"
            result["metadata"]["timestamp"] = datetime.utcnow().isoformat()
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "error_type": "EXTRACTION_ERROR",
                "metadata": {
                    "file_path": repo_path,
                    "extraction_errors": [str(e)]
                }
            }
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
    
    elif name == "generate_documentation":
        # Generate a template-compliant documentation stub with ❓ placeholders
        if not WRITE_OPS_ENABLED:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Write operations are disabled by default. Set AKR_ENABLE_WRITE_OPS=true to enable.",
                "error_type": "PERMISSION_DENIED"
            }, indent=2))]

        allow_writes = arguments.get("allowWrites", False)
        if not allow_writes:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Write operations require allowWrites=true to proceed.",
                "error_type": "PERMISSION_DENIED"
            }, indent=2))]

        component_name = arguments.get("component_name")
        component_type = arguments.get("component_type", "service")
        template = arguments.get("template", "lean_baseline_service_template.md")
        source_file = arguments.get("source_file", "")
        doc_path = arguments.get("doc_path", f"docs/{component_name}.md")

        resolved_template, template_matches = _resolve_template_name(template)
        if not resolved_template:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"Template '{template}' is ambiguous." if template_matches else f"Template '{template}' not found.",
                "matches": template_matches,
                "hint": "Specify the full template filename if multiple matches exist"
            }, indent=2))]
        template = resolved_template
        
        # Validate template exists BEFORE attempting to use it
        try:
            rm = get_resource_manager()
            template_content = rm.get_resource_content("template", template)
            if not template_content:
                available_templates = [t.filename for t in rm.list_templates()]
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": f"Template '{template}' not found in akr_content/templates/",
                    "availableTemplates": available_templates,
                    "hint": "Use one of the available templates or check that the template file exists"
                }, indent=2))]
        except Exception as e:
            logger.error(f"Template validation error: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"Failed to validate template: {str(e)}",
                "hint": "Check server logs for details"
            }, indent=2))]
        
        baseline_sections = TEMPLATE_BASELINE_SECTIONS.get(template)
        if not baseline_sections:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"Template '{template}' is not mapped to baseline sections for stub generation.",
                "guidance": "Use a known template or add it to TEMPLATE_BASELINE_SECTIONS.",
                "availableTemplates": sorted(TEMPLATE_BASELINE_SECTIONS.keys())
            }, indent=2))]

        # Generate template-compliant content with human input placeholders
        stub_content = _build_stub_content(
            component_name=component_name,
            component_type=component_type,
            template=template,
            baseline_sections=baseline_sections,
        )
        
        # Use write_documentation_async to ensure enforcement
        try:
            repo_path = str(Path(__file__).parent.parent)
            
            # Create operation metrics
            metrics = OperationMetrics(template_name=template)

            # Create progress tracker
            progress_token = arguments.get("_meta", {}).get("progressToken")
            tracker = ProgressTracker(
                progress_token=progress_token,
                send_progress=send_progress_notification if progress_token else None,
                estimate_remaining=metrics.estimate_remaining_ms
            )
            
            result = await write_documentation_async(
                repo_path=repo_path,
                content=stub_content,
                source_file=source_file or f"src/{component_name}.cs",
                doc_path=doc_path,
                template=template,
                component_type=component_type,
                overwrite=arguments.get("overwrite", False),
                config=cfg,
                telemetry_logger=enforcement_logger,
                progress_tracker=tracker,
                operation_metrics=metrics,
                workflow_tracker=workflow_tracker,
                duplicate_detector=duplicate_detector,
                resource_manager=get_resource_manager(),
                session_cache=get_session_cache(),
                allowWrites=allow_writes,
            )
            
            # Add guidance message
            if result.get("success"):
                # Mark stub as generated in workflow tracker
                if workflow_tracker:
                    await workflow_tracker.mark_stub_generated(doc_path, template)
                
                result["message"] = (
                    f"✅ Generated template-compliant documentation stub for {component_name}. "
                    f"All sections marked with ❓ require human input. Please review and enhance with business context before finalizing."
                )
                result["nextSteps"] = [
                    "Review the generated file and replace all ❓ placeholders with actual content",
                    "Update YAML front matter with correct domain, feature, and layer values",
                    "Add specific business rules and architectural details",
                    "Use update_documentation_sections to make targeted updates after review"
                ]
                result["workflow"] = {
                    "stub_generated": True,
                    "next_tool": "write_documentation",
                    "workflow_id": doc_path
                }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        except asyncio.CancelledError:
            logger.warning("generate_documentation cancelled by client")
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Operation cancelled",
                "cancelled": True
            }))]
        
        except Exception as e:
            logger.error(f"generate_documentation error: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"Failed to generate documentation: {e}",
                "guidance": "Use write_documentation instead with your own content, or check the error above."
            }))]
    
    elif name == "generate_and_write_documentation":
        # Unified scaffolding + generation + writing in a single operation
        try:
            if not WRITE_OPS_ENABLED:
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "Write operations are disabled by default. Set AKR_ENABLE_WRITE_OPS=true to enable.",
                    "error_type": "PERMISSION_DENIED"
                }, indent=2))]

            allow_writes = arguments.get("allowWrites", False)
            if not allow_writes:
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "Write operations require allowWrites=true to proceed.",
                    "error_type": "PERMISSION_DENIED"
                }, indent=2))]

            component_name = arguments.get("component_name")
            source_files = arguments.get("source_files", [])
            template = arguments.get("template")
            doc_path = arguments.get("doc_path")
            component_type = arguments.get("component_type")
            
            if not component_name:
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "component_name is required"
                }, indent=2))]
            
            # Get workspace root
            workspace_root = Path(os.environ.get("VSCODE_WORKSPACE_FOLDER", Path.cwd()))
            
            # Auto-detect project type if not specified
            if not component_type:
                project_type = _detect_project_type(workspace_root)
                if project_type == "unknown":
                    return [TextContent(type="text", text=json.dumps({
                        "success": False,
                        "error": "Could not detect project type",
                        "guidance": (
                            "Please either:\n"
                            "1. Add 'domain' field to .akr-config.json (backend/ui/database), or\n"
                            "2. Specify component_type parameter explicitly"
                        )
                    }, indent=2))]
                
                # Map project type to component type
                type_map = {
                    "backend": "service",
                    "ui": "ui_component",
                    "database": "table"
                }
                component_type = type_map.get(project_type, "service")
            else:
                # Derive project type from component type
                if component_type in ["service", "api"]:
                    project_type = "backend"
                elif component_type in ["ui_component", "component"]:
                    project_type = "ui"
                elif component_type == "table":
                    project_type = "database"
                else:
                    project_type = "backend"  # default
            
            # Auto-select template if not specified
            if not template:
                template_map = {
                    "backend": "lean_baseline_service_template.md",
                    "ui": "ui_component_template.md",
                    "database": "table_doc_template.md"
                }
                template = template_map.get(project_type, "lean_baseline_service_template.md")

            resolved_template, template_matches = _resolve_template_name(template)
            if not resolved_template:
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": f"Template '{template}' is ambiguous." if template_matches else f"Template '{template}' not found.",
                    "matches": template_matches,
                    "hint": "Specify the full template filename if multiple matches exist"
                }, indent=2))]
            template = resolved_template
            
            # Validate template exists
            try:
                rm = get_resource_manager()
                template_content = rm.get_resource_content("template", template)
                if not template_content:
                    available_templates = [t.filename for t in rm.list_templates()]
                    return [TextContent(type="text", text=json.dumps({
                        "success": False,
                        "error": f"Template '{template}' not found in akr_content/templates/",
                        "availableTemplates": available_templates,
                        "hint": "Use one of the available templates or check that the template file exists"
                    }, indent=2))]
            except Exception as e:
                logger.error(f"Template validation error: {e}", exc_info=True)
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": f"Failed to validate template: {str(e)}",
                    "hint": "Check server logs for details"
                }, indent=2))]
            
            # Replace placeholders in template
            scaffolded_content = _replace_placeholders(
                template_content,
                component_name,
                project_type,
                source_files
            )
            
            # Auto-determine doc_path if not specified
            if not doc_path:
                output_path_map = {
                    "backend": "docs/services/",
                    "ui": "docs/components/",
                    "database": "docs/tables/"
                }
                naming_suffix_map = {
                    "backend": "_doc.md",
                    "ui": "_doc.md",
                    "database": ".md"
                }
                output_path = output_path_map.get(project_type, "docs/services/")
                naming_suffix = naming_suffix_map.get(project_type, "_doc.md")
                doc_path = f"{output_path}{component_name}{naming_suffix}"
            
            # Prepare for writing
            repo_path = str(Path(__file__).parent.parent)
            
            # Create operation metrics
            metrics = OperationMetrics(template_name=template)

            # Create progress tracker
            progress_token = arguments.get("_meta", {}).get("progressToken")
            tracker = ProgressTracker(
                progress_token=progress_token,
                send_progress=send_progress_notification if progress_token else None,
                estimate_remaining=metrics.estimate_remaining_ms
            )
            
            # Use first source file as primary source_file for metadata
            primary_source_file = source_files[0] if source_files else f"src/{component_name}.cs"
            
            # Write documentation with enforcement
            result = await write_documentation_async(
                repo_path=repo_path,
                content=scaffolded_content,
                source_file=primary_source_file,
                doc_path=doc_path,
                template=template,
                component_type=component_type,
                overwrite=arguments.get("overwrite", False),
                config=cfg,
                telemetry_logger=enforcement_logger,
                progress_tracker=tracker,
                operation_metrics=metrics,
                workflow_tracker=workflow_tracker,
                duplicate_detector=duplicate_detector,
                resource_manager=get_resource_manager(),
                session_cache=get_session_cache(),
                allowWrites=allow_writes,
            )
            
            # Enhance result message
            if result.get("success"):
                if workflow_tracker:
                    await workflow_tracker.mark_stub_generated(doc_path, template)
                
                result["message"] = (
                    f"✅ Generated and wrote AKR documentation for {component_name}. "
                    f"Template structure complete with placeholders. Review and enhance sections marked with ❓."
                )
                result["nextSteps"] = [
                    "Review the generated file - template structure is complete",
                    "Replace ❓ placeholders in sections requiring human context (Business Rules, What & Why, etc.)",
                    "Update YAML front matter with correct domain, feature, and layer values if needed",
                    "Run 'AKR: Validate Documentation (file)' to check compliance",
                    "Commit to git when ready"
                ]
                result["workflow"] = {
                    "unified_generation": True,
                    "scaffolded": True,
                    "written": True,
                    "validation_passed": result.get("fixesApplied", 0) == 0,
                    "file_path": doc_path
                }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        except asyncio.CancelledError:
            logger.warning("generate_and_write_documentation cancelled by client")
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Operation cancelled",
                "cancelled": True
            }))]
        
        except Exception as e:
            logger.error(f"generate_and_write_documentation error: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"Failed to generate and write documentation: {e}",
                "guidance": "Check the error above or try using generate_documentation + write_documentation separately."
            }))]
    
    elif name == "validate_documentation":
        try:
            doc_path = arguments.get("doc_path")
            template_id = arguments.get("template_id")
            tier_level = arguments.get("tier_level", "TIER_2")
            auto_fix = arguments.get("auto_fix", False)
            dry_run = arguments.get("dry_run", True)
            
            if not doc_path or not template_id:
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "Missing required parameters: doc_path and template_id"
                }, indent=2))]
            
            # Read document content
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    doc_content = f.read()
            except FileNotFoundError:
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": f"Document not found: {doc_path}"
                }, indent=2))]
            except Exception as e:
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": f"Failed to read document: {str(e)}"
                }, indent=2))]
            
            # Import validation engine
            from tools.validation_library import ValidationEngine, ValidationTier
            from tools.template_schema_builder import get_or_create_schema_builder
            
            # Get schema builder and validation engine
            schema_builder = get_or_create_schema_builder(resolver)
            validation_engine = ValidationEngine(schema_builder=schema_builder, config=config)
            
            # Perform validation
            result = validation_engine.validate(
                doc_content=doc_content,
                template_id=template_id,
                tier_level=tier_level,
                auto_fix=auto_fix,
                dry_run=dry_run
            )
            
            # Convert to JSON-serializable format
            output = {
                "success": True,
                "is_valid": result.is_valid,
                "completeness": round(result.completeness * 100, 1),  # Convert to percentage
                "tier_level": result.tier_level,
                "violations": [v.to_dict() for v in result.violations],
                "violation_count": len(result.violations),
                "blocker_count": sum(1 for v in result.violations if v.severity == "BLOCKER"),
                "fixable_count": sum(1 for v in result.violations if v.severity == "FIXABLE"),
                "warning_count": sum(1 for v in result.violations if v.severity == "WARN"),
            }
            
            if result.auto_fixed_content and result.diff:
                output["auto_fixed_available"] = True
                output["diff"] = result.diff
                output["suggestion"] = "Auto-fixes available. Review diff above. Use write_documentation to apply fixes."
            else:
                output["auto_fixed_available"] = False
            
            if result.metadata:
                output["metadata"] = {
                    "template_source": result.metadata.template_source,
                    "validated_at_utc": result.metadata.validated_at_utc,
                    "server_version": result.metadata.server_version
                }
            
            return [TextContent(type="text", text=json.dumps(output, indent=2))]
            
        except ImportError as e:
            logger.error(f"ValidationEngine import error: {str(e)}")
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Validation engine not available. Ensure jsonschema>=4.0.0 is installed.",
                "hint": "Run: pip install jsonschema>=4.0.0"
            }, indent=2))]
        
        except Exception as e:
            logger.error(f"validate_documentation error: {str(e)}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"Validation failed: {str(e)}"
            }, indent=2))]
    
    elif name == "get_charter":
        domain = arguments.get("domain")
        
        if resource_manager:
            charter = resource_manager.get_charter(domain)
            if charter:
                charter.load_content()  # Load content if not already loaded
                return [TextContent(type="text", text=charter.content)]
        
        return [TextContent(type="text", text=f"Charter not found for domain: {domain}")]

    elif name == "write_documentation":
        try:
            if not WRITE_OPS_ENABLED:
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "Write operations are disabled by default. Set AKR_ENABLE_WRITE_OPS=true to enable.",
                    "error_type": "PERMISSION_DENIED"
                }, indent=2))]

            allow_writes = arguments.get("allowWrites", False)
            if not allow_writes:
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "Write operations require allowWrites=true to proceed.",
                    "error_type": "PERMISSION_DENIED"
                }, indent=2))]

            repo_path = str(Path(__file__).parent.parent)

            template_input = arguments.get("template", "lean_baseline_service_template.md")
            resolved_template, template_matches = _resolve_template_name(template_input)
            if not resolved_template:
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": f"Template '{template_input}' is ambiguous." if template_matches else f"Template '{template_input}' not found.",
                    "matches": template_matches,
                    "hint": "Specify the full template filename if multiple matches exist"
                }, indent=2))]
            template = resolved_template
            
            # Extract progress token (if client supports it; MCP 2025-11-25+)
            progress_token = arguments.get("_meta", {}).get("progressToken")
            
            # Create operation metrics
            metrics = OperationMetrics(template_name=template)

            # Create progress tracker
            tracker = ProgressTracker(
                progress_token=progress_token,
                send_progress=send_progress_notification if progress_token else None,
                estimate_remaining=metrics.estimate_remaining_ms
            )
            
            # Call async version
            result = await write_documentation_async(
                repo_path=repo_path,
                content=arguments.get("content"),
                source_file=arguments.get("source_file"),
                doc_path=arguments.get("doc_path"),
                template=template,
                component_type=arguments.get("component_type", "unknown"),
                overwrite=arguments.get("overwrite", False),
                force_workflow_bypass=arguments.get("force_workflow_bypass", False),
                config=cfg,
                telemetry_logger=enforcement_logger,
                progress_tracker=tracker,
                operation_metrics=metrics,
                resource_manager=get_resource_manager(),
                session_cache=get_session_cache(),
                allowWrites=allow_writes,
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        except asyncio.CancelledError:
            logger.warning("write_documentation cancelled by client")
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Operation cancelled",
                "cancelled": True
            }))]
        
        except TypeError:
            # Fallback for compatibility (no progress tracking)
            repo_path = str(Path(__file__).parent.parent)
            result = write_documentation(
                repo_path=repo_path,
                content=arguments.get("content"),
                source_file=arguments.get("source_file"),
                doc_path=arguments.get("doc_path"),
                template=template,
                component_type=arguments.get("component_type", "unknown"),
                overwrite=arguments.get("overwrite", False),
                force_workflow_bypass=arguments.get("force_workflow_bypass", False),
                allowWrites=allow_writes,
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        except Exception as e:
            logger.error(f"write_documentation error: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": str(e)
            }))]

    elif name == "update_documentation_sections":
        try:
            if not WRITE_OPS_ENABLED:
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "Write operations are disabled by default. Set AKR_ENABLE_WRITE_OPS=true to enable.",
                    "error_type": "PERMISSION_DENIED"
                }, indent=2))]

            allow_writes = arguments.get("allowWrites", False)
            if not allow_writes:
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "Write operations require allowWrites=true to proceed.",
                    "error_type": "PERMISSION_DENIED"
                }, indent=2))]

            repo_path = str(Path(__file__).parent.parent)

            template_input = arguments.get("template", "lean_baseline_service_template.md")
            resolved_template, template_matches = _resolve_template_name(template_input)
            if not resolved_template:
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": f"Template '{template_input}' is ambiguous." if template_matches else f"Template '{template_input}' not found.",
                    "matches": template_matches,
                    "hint": "Specify the full template filename if multiple matches exist"
                }, indent=2))]
            template = resolved_template
            
            # Extract progress token (if client supports it)
            progress_token = arguments.get("_meta", {}).get("progressToken")
            
            # Create operation metrics
            metrics = OperationMetrics(template_name=template)

            # Create progress tracker
            tracker = ProgressTracker(
                progress_token=progress_token,
                send_progress=send_progress_notification if progress_token else None,
                estimate_remaining=metrics.estimate_remaining_ms
            )
            
            # Call async version
            result = await update_documentation_sections_and_commit_async(
                repo_path=repo_path,
                doc_path=arguments.get("doc_path"),
                section_updates=arguments.get("section_updates"),
                template=template,
                source_file=arguments.get("source_file", ""),
                component_type=arguments.get("component_type", "unknown"),
                add_changelog=arguments.get("add_changelog", True),
                overwrite=arguments.get("overwrite", True),
                config=cfg,
                telemetry_logger=enforcement_logger,
                progress_tracker=tracker,
                operation_metrics=metrics,
                allowWrites=allow_writes,
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        except asyncio.CancelledError:
            logger.warning("update_documentation_sections cancelled by client")
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Operation cancelled",
                "cancelled": True
            }))]
        
        except TypeError:
            # Fallback for compatibility
            repo_path = str(Path(__file__).parent.parent)
            result = update_documentation_sections_and_commit(
                repo_path=repo_path,
                doc_path=arguments.get("doc_path"),
                section_updates=arguments.get("section_updates"),
                template=template,
                source_file=arguments.get("source_file", ""),
                component_type=arguments.get("component_type", "unknown"),
                add_changelog=arguments.get("add_changelog", True),
                overwrite=arguments.get("overwrite", True),
                config=cfg,
                telemetry_logger=enforcement_logger,
                allowWrites=allow_writes,
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except TypeError:
            repo_path = str(Path(__file__).parent.parent)
            result = update_documentation_sections_and_commit(
                repo_path=repo_path,
                doc_path=arguments.get("doc_path"),
                section_updates=arguments.get("section_updates"),
                template=template,
                source_file=arguments.get("source_file", ""),
                component_type=arguments.get("component_type", "unknown"),
                add_changelog=arguments.get("add_changelog", True),
                overwrite=arguments.get("overwrite", True),
                allowWrites=allow_writes,
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            logger.error(f"update_documentation_sections error: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": str(e)
            }))]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

# =============================================================================
# MCP Prompts: "Generate Lean Backend Doc"
# =============================================================================
from typing import List, Dict, Any

# ---- Prompt metadata (what shows in the client's prompt picker) ----


def _read_akr_resource_text(filename: str) -> str:
    """
    Read a resource (template/charter/guide) by file name from AKR resources,
    logging what we actually retrieved so we can diagnose missing context.
    """
    mgr = get_resource_manager()

    # Try template folder first
    text = mgr.get_resource_content("template", filename)
    if text:
        logger.info(f"[PROMPT] Loaded template/{filename} ({len(text)} chars)")
        return text

    # Try charter folder
    text = mgr.get_resource_content("charter", filename)
    if text:
        logger.info(f"[PROMPT] Loaded charter/{filename} ({len(text)} chars)")
        return text

    # Try guide folder (fallback)
    text = mgr.get_resource_content("guide", filename)
    if text:
        logger.info(f"[PROMPT] Loaded guide/{filename} ({len(text)} chars)")
        return text

    logger.warning(f"[PROMPT] Could not load resource text: {filename}")
    return ""

# =============================================================================
# MCP Prompts: Definitions  (place ABOVE list_prompts/get_prompt handlers)
# =============================================================================
from typing import List, Dict, Any

AKR_PROMPTS: List[Dict[str, Any]] = [
    {
        "name": "generate_lean_backend_doc",
        "title": "Generate Lean Backend Doc",
        "description": (
            "Generate AKR documentation for a backend module using the Lean template. "
            "Strictly follow the template headings and include 'N/A' where not applicable."
        ),
        "arguments": [
            {
                "name": "module_name",
                "description": "Human-friendly module name (e.g., 'User').",
                "required": True,
            },
            # Lets you paste multiple paths in ONE field (one-per-line or CSV)
            {
                "name": "files_text",
                "description": "Paste file paths here (one per line or comma-separated).",
                "required": False,
            },
            # Also keep the array variant for JSON-style inputs
            {
                "name": "files",
                "description": "List of file paths as a JSON array.",
                "required": False,
            },
            {
                "name": "template",
                "description": "Template filename in AKR resources; defaults to lean baseline.",
                "required": False,
            },
        ],
    }
]

# ---- MCP prompt discovery ----
@server.list_prompts()
async def list_prompts() -> List[Dict[str, Any]]:
    """
    Return available prompts for this server: name/title/description/arguments.
    VS Code will surface these as slash commands.
    """
    return AKR_PROMPTS

# ---- MCP prompt retrieval ----
@server.get_prompt()
async def get_prompt(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name != "generate_lean_backend_doc":
        raise ValueError(f"Unknown prompt: {name}")

    module_name: str = (arguments.get("module_name") or "").strip()

    # ---------------------------------------------------------------------
    # NEW: normalize 'files' input from either:
    #  - a true JSON array:  files = ["a.cs", "b.cs", ...]
    #  - a string (user pasted JSON array, or CSV/newlines) into 'files'
    #  - a multi-line or CSV string pasted into 'files_text'
    # ---------------------------------------------------------------------
    raw_files = arguments.get("files")
    files_text = arguments.get("files_text")
    files: List[str] = []

    # Case 1: already a list
    if isinstance(raw_files, list):
        files = [str(p).strip() for p in raw_files if str(p).strip()]

    # Case 2: the 'files' field came in as a string (single input box)
    if not files and isinstance(raw_files, str) and raw_files.strip():
        s = raw_files.strip()
        # Try to parse as JSON array in string form
        if s.startswith("[") and s.endswith("]"):
            try:
                arr = json.loads(s)
                if isinstance(arr, list):
                    files = [str(p).strip() for p in arr if str(p).strip()]
            except Exception:
                pass
        # Or accept comma/newline separated
        if not files:
            parts = [ln.strip() for ln in s.replace(",", "\n").splitlines()]
            files = [p for p in parts if p]

    # Case 3: use files_text (the single multi-line field)
    if not files and isinstance(files_text, str) and files_text.strip():
        parts = [ln.strip() for ln in files_text.replace(",", "\n").splitlines()]
        files = [p for p in parts if p]

    template_file: str = arguments.get("template") or "lean_baseline_service_template.md"

    # Validate after normalization
    if not module_name or not files:
        raise ValueError("module_name and files are required. "
                         "Provide files as a JSON array (`files`) or paste paths into `files_text`.")

    # Load the Lean (backend) template and the backend charter from MCP resources
    lean_template_text = _read_akr_resource_text(template_file) or ""
    if not lean_template_text:
        # try a couple common fallbacks if team renamed files
        for alt in ("lean_baseline_service_template.md", "lean_service_template.md", "standard_service_template.md"):
            lean_template_text = _read_akr_resource_text(alt) or ""
            if lean_template_text:
                template_file = alt
                break

    backend_charter_text = _read_akr_resource_text("AKR_CHARTER_BACKEND.md") or ""

    # Log lengths so you can confirm the real content was injected
    logger.info(
        f"[PROMPT] lean_template='{template_file}' len={len(lean_template_text)}; "
        f"backend_charter len={len(backend_charter_text)}"
    )

    # Fail fast to prevent freestyle output without the real template/charter
    if not lean_template_text:
        raise ValueError(
            "AKR Lean template not found in MCP resources.\n"
            "Ensure 'akr_content/templates/lean_baseline_service_template.md' exists and restart the server, "
            "then re-run this prompt."
        )

    if not backend_charter_text:
        raise ValueError(
            "AKR backend charter not found in MCP resources.\n"
            "Ensure 'akr_content/charters/AKR_CHARTER_BACKEND.md' exists and restart the server."
        )

    # Strict instructions to prevent drift
    instructions = f"""
You are generating AKR documentation for the **{module_name}** backend module.

Follow these rules without exception:
1) Use the attached **Lean (backend)** template **exactly as written**. Preserve the section headings and their order.
2) Do **not** add headings that are not in the template. If a section is not applicable, include the heading and write: N/A (not applicable).
3) Align with the attached **AKR backend charter**. If there is a conflict, the charter wins.
4) Base the content on the provided code files only; do not invent implementation details.

Return a single Markdown document that starts with the exact template headings and fills content for each section.
""".strip()

    files_block = "\n".join(f"- {p}" for p in files)

    messages = [
        {"role": "user", "content": {"type": "text", "text": instructions}},
        {"role": "user", "content": {"type": "text", "text": f"# AKR Lean (backend) Template\n\n{lean_template_text}"}},
        {"role": "user", "content": {"type": "text", "text": f"# AKR Backend Charter\n\n{backend_charter_text}"}},
        {"role": "user", "content": {"type": "text", "text": f"# Files to analyze for {module_name}\n{files_block}"}},
    ]
    return {
        "description": "Generate AKR documentation using the Lean backend template and charter.",
        "messages": messages,
    }

# ==================== NEW CODE: MAIN FUNCTION WITH FAST MODE ====================
# ==================== FIXED: MAIN FUNCTION WITH CORRECT INITIALIZATION ====================
async def main():
    """
    Main entry point for the MCP server.
    
    In fast mode (AKR_FAST_MODE=true), skips all initialization until resources are accessed.
    In normal mode, performs full initialization at startup.
    """
    
    if SKIP_INITIALIZATION:
        logger.info("⚡ SKIP_INITIALIZATION mode: Starting with minimal setup")
        logger.info("   - No workspace scan")
        logger.info("   - No repository checks")
        logger.info("   - Resources loaded on-demand")
    elif FAST_MODE:
        logger.info("⚡ FAST_MODE enabled: Lazy initialization on first use")
        logger.info("   - Workspace detection delayed")
        logger.info("   - Repository checks deferred")
        logger.info("   - Server responds immediately")
    else:
        logger.info("🚀 Normal mode: Full initialization at startup")
        ensure_initialized()
    
    logger.info("✅ Server ready to accept connections")
    


    init_options = InitializationOptions(
        server_name="akr-documentation-server",
        server_version="0.1.0",
        capabilities=ServerCapabilities(
            resources={"listChanged": True},
            tools={"listChanged": True},
            prompts={"listChanged": True},   # <-- advertise prompts capability
        ),
        instructions="AKR documentation utilities (resources, tools, prompts).",
    )


    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, init_options)  # ← not None

# ================================================================================


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())