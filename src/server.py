"""
AKR MCP Documentation Server

A Model Context Protocol server that provides AKR documentation resources
and tools to GitHub Copilot in VS Code.

This server enables Copilot to:
- Access AKR charter files (documentation standards)
- Use documentation templates for consistent formatting
- Reference developer guides for best practices
- Validate generated documentation against AKR standards
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource, ResourceTemplate

# Import AKR resource manager
from resources import AKRResourceManager, ResourceCategory, create_resource_manager

# Import documentation tools
from tools import (
    list_all_templates,
    list_templates_by_project_type,
    suggest_template_for_file,
    format_templates_list,
    format_template_suggestion,
    ProjectType,
    TemplateComplexity
)

# Import write capability tools
from tools.config import AKRConfigManager, ProjectConfig
from tools.branch_management import BranchManager, BranchStrategy
from tools.write_operations import (
    DocumentationWriter,
    write_documentation,
    write_config_file
)
from tools.section_updater import (
    analyze_documentation_impact,
    update_documentation_sections,
    get_document_structure
)
from tools.pr_operations import (
    PRManager,
    create_documentation_pr,
    check_documentation_pr_requirements
)

# Import human input interview tools
from tools.human_input_interview import (
    start_documentation_interview,
    get_next_interview_question,
    submit_interview_answer,
    skip_interview_question,
    get_interview_progress,
    end_documentation_interview,
    QuestionPriority
)

# Import cross-repository consolidation tools
from tools.cross_repository import CrossRepositoryManager

# Import workspace management
from tools.workspace import WorkspaceManager, create_workspace_manager

# Configure logging
def setup_logging(log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """Configure logging for the MCP server."""
    logger = logging.getLogger("akr-mcp-server")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(console_format)
        logger.addHandler(file_handler)
    
    return logger


# Load server configuration
def load_config() -> dict:
    """Load server configuration from config.json."""
    config_path = Path(__file__).parent.parent / "config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "server": {
            "name": "akr-documentation-server",
            "version": "0.1.0"
        },
        "logging": {
            "level": "INFO"
        }
    }


# Initialize configuration and logging
config = load_config()
log_file = Path(__file__).parent.parent / "logs" / "akr-mcp-server.log"
logger = setup_logging(
    log_level=config.get("logging", {}).get("level", "INFO"),
    log_file=str(log_file)
)

# Create MCP server instance
server = Server(config["server"]["name"])

# Initialize AKR resource manager
resource_manager = create_resource_manager()

# Initialize workspace manager
workspace_manager = create_workspace_manager()

# Server state for health tracking
server_state = {
    "start_time": None,
    "tool_calls": 0,
    "resource_reads": 0,
    "errors": 0
}

# Documentation session state (branch-based writes)
doc_session = {
    "active": False,
    "workspace_path": None,
    "branch_name": None,
    "config": None,
    "files_documented": [],
    "branch_manager": None,
    "config_manager": None
}

# Cross-repository consolidation state
cross_repo_state = {
    "manager": None,
    "config": None,
    "last_update": None
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools - optimized with consolidated actions."""
    logger.debug("Listing available tools")
    return [
        # ===== Server Utilities (Consolidated) =====
        Tool(
            name="server",
            description="Server utilities: health check and capabilities info",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["health", "info"]
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Include detailed statistics (for health action)",
                        "default": False
                    }
                },
                "required": ["action"]
            }
        ),
        
        # ===== Templates (Consolidated) =====
        Tool(
            name="templates",
            description="Documentation template operations: list, suggest, or get details",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["list", "suggest"]
                    },
                    "file_path": {
                        "type": "string",
                        "description": "File path (required for suggest action)"
                    },
                    "project_type": {
                        "type": "string",
                        "description": "Filter by type (for list action)",
                        "enum": ["backend", "ui", "database", "all"],
                        "default": "all"
                    },
                    "complexity": {
                        "type": "string",
                        "description": "Template complexity (for suggest action)",
                        "enum": ["minimal", "lean", "standard", "comprehensive"],
                        "default": "standard"
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Include detailed info",
                        "default": False
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination (for list action)",
                        "default": 1,
                        "minimum": 1
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Items per page (max 20)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": ["action"]
            }
        ),
        
        # ===== Session Management (Consolidated) =====
        Tool(
            name="session",
            description="Documentation session operations: initialize, get config, suggest paths, or end session",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["initialize", "get_config", "suggest_path", "end"]
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace/repository root path (required for most actions)"
                    },
                    "branch_strategy": {
                        "type": "string",
                        "description": "Branch strategy (for initialize)",
                        "enum": ["create_new", "use_current", "use_existing"],
                        "default": "create_new"
                    },
                    "branch_name": {
                        "type": "string",
                        "description": "Branch name (for use_existing strategy)"
                    },
                    "source_file": {
                        "type": "string",
                        "description": "Source file path (for suggest_path action)"
                    },
                    "create_pr": {
                        "type": "boolean",
                        "description": "Create PR when ending session",
                        "default": False
                    },
                    "pr_title": {
                        "type": "string",
                        "description": "PR title (if create_pr is true)"
                    },
                    "pr_description": {
                        "type": "string",
                        "description": "PR description (if create_pr is true)"
                    }
                },
                "required": ["action"]
            }
        ),
        
        # ===== Documentation Operations (Consolidated) =====
        Tool(
            name="documentation",
            description="Documentation operations: write, analyze impact, update sections, get structure, create PR, or check requirements",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["write", "analyze_impact", "update_sections", "get_structure", "create_pr", "check_pr_requirements"]
                    },
                    "doc_path": {
                        "type": "string",
                        "description": "Documentation file path (for write)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Documentation content (for write)"
                    },
                    "source_file": {
                        "type": "string",
                        "description": "Source file being documented (for write)"
                    },
                    "component_type": {
                        "type": "string",
                        "description": "Component type (for write)"
                    },
                    "template_used": {
                        "type": "string",
                        "description": "Template name used (for write)"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Allow overwriting (for write)",
                        "default": False
                    },
                    "file_path": {
                        "type": "string",
                        "description": "File path (for analyze_impact, update_sections, get_structure)"
                    },
                    "proposed_sections": {
                        "type": "object",
                        "description": "Section updates (for analyze_impact)"
                    },
                    "section_updates": {
                        "type": "object",
                        "description": "Section updates (for update_sections)"
                    },
                    "add_changelog": {
                        "type": "boolean",
                        "description": "Add changelog entry (for update_sections)",
                        "default": True
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Preview changes only (for update_sections)",
                        "default": False
                    },
                    "title": {
                        "type": "string",
                        "description": "PR title (for create_pr)"
                    },
                    "description": {
                        "type": "string",
                        "description": "PR description (for create_pr)"
                    },
                    "draft": {
                        "type": "boolean",
                        "description": "Create draft PR (for create_pr)",
                        "default": True
                    }
                },
                "required": ["action"]
            }
        ),
        
        # ===== Interview Operations (Consolidated) =====
        Tool(
            name="interview",
            description="Interactive documentation interview: start, get question, submit answer, skip, check progress, or end session",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["start", "get_question", "submit_answer", "skip", "progress", "end"]
                    },
                    "source_file": {
                        "type": "string",
                        "description": "Source file path (for start)"
                    },
                    "template_content": {
                        "type": "string",
                        "description": "Template/generated content to analyze (for start)"
                    },
                    "template_name": {
                        "type": "string",
                        "description": "Template name (for start)"
                    },
                    "component_type": {
                        "type": "string",
                        "description": "Component type (for start)"
                    },
                    "priority_filter": {
                        "type": "string",
                        "description": "Question priority filter (for start)",
                        "enum": ["critical", "important", "optional"],
                        "default": "optional"
                    },
                    "role": {
                        "type": "string",
                        "description": "Interview role (for start)",
                        "enum": ["technical_lead", "developer", "product_owner", "qa_tester", "scrum_master", "general"],
                        "default": "general"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session ID (required for all actions except start)"
                    },
                    "answer": {
                        "type": "string",
                        "description": "Answer text (for submit_answer)"
                    },
                    "generate_draft": {
                        "type": "boolean",
                        "description": "Auto-generate polished draft (for submit_answer)",
                        "default": True
                    },
                    "reason": {
                        "type": "string",
                        "description": "Skip reason (for skip)",
                        "default": "Will provide later"
                    }
                },
                "required": ["action"]
            }
        ),
        
        # ===== Cross-Repository Operations (Consolidated) =====
        Tool(
            name="cross_repository",
            description="Cross-repo operations: consolidate feature, generate testing docs, detect changes, list features, refresh repos, or check states",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["consolidate_feature", "generate_testing", "detect_changes", "list_features", "refresh_repos", "check_states", "validate_traceability"]
                    },
                    "feature_name": {
                        "type": "string",
                        "description": "Feature name (for consolidate_feature, generate_testing)"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace path (required for most actions)"
                    },
                    "test_type": {
                        "type": "string",
                        "description": "Test type (for generate_testing)",
                        "default": "integration"
                    },
                    "since": {
                        "type": "string",
                        "description": "Time reference (for detect_changes)"
                    },
                    "author": {
                        "type": "string",
                        "description": "Author filter (for detect_changes)"
                    },
                    "docs_dir": {
                        "type": "string",
                        "description": "Docs directory (for validate_traceability)",
                        "default": "docs"
                    },
                    "features_dir": {
                        "type": "string",
                        "description": "Features directory (for validate_traceability)"
                    },
                    "testing_dir": {
                        "type": "string",
                        "description": "Testing directory (for validate_traceability)"
                    }
                },
                "required": ["action"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls with consolidated action-based routing."""
    logger.info(f"Tool called: {name} with action: {arguments.get('action', 'N/A')}")
    server_state["tool_calls"] += 1
    
    try:
        # Server utilities
        if name == "server":
            action = arguments.get("action")
            if action == "health":
                return await health_check(arguments.get("verbose", False))
            elif action == "info":
                return await get_server_info()
            else:
                raise ValueError(f"Unknown server action: {action}")
        
        # Templates
        elif name == "templates":
            action = arguments.get("action")
            if action == "list":
                return await handle_list_templates(
                    project_type=arguments.get("project_type", "all"),
                    verbose=arguments.get("verbose", False),
                    page=arguments.get("page", 1),
                    page_size=arguments.get("page_size", 10)
                )
            elif action == "suggest":
                return await handle_suggest_template(
                    file_path=arguments.get("file_path", ""),
                    complexity=arguments.get("complexity", "standard")
                )
            else:
                raise ValueError(f"Unknown templates action: {action}")
        
        # Session management
        elif name == "session":
            action = arguments.get("action")
            if action == "initialize":
                return await handle_initialize_session(
                    workspace_path=arguments.get("workspace_path"),
                    branch_strategy=arguments.get("branch_strategy", "create_new"),
                    branch_name=arguments.get("branch_name")
                )
            elif action == "get_config":
                return await handle_get_project_config(
                    workspace_path=arguments.get("workspace_path")
                )
            elif action == "suggest_path":
                return await handle_suggest_doc_path(
                    source_file=arguments.get("source_file"),
                    workspace_path=arguments.get("workspace_path")
                )
            elif action == "end":
                return await handle_end_session(
                    create_pr=arguments.get("create_pr", False),
                    pr_title=arguments.get("pr_title"),
                    pr_description=arguments.get("pr_description")
                )
            else:
                raise ValueError(f"Unknown session action: {action}")
        
        # Documentation operations
        elif name == "documentation":
            action = arguments.get("action")
            if action == "write":
                return await handle_write_documentation(
                    doc_path=arguments.get("doc_path"),
                    content=arguments.get("content"),
                    source_file=arguments.get("source_file"),
                    component_type=arguments.get("component_type", "unknown"),
                    template_used=arguments.get("template_used", "standard"),
                    overwrite=arguments.get("overwrite", False)
                )
            elif action == "analyze_impact":
                return await handle_analyze_impact(
                    file_path=arguments.get("file_path"),
                    proposed_sections=arguments.get("proposed_sections", {})
                )
            elif action == "update_sections":
                return await handle_update_sections(
                    file_path=arguments.get("file_path"),
                    section_updates=arguments.get("section_updates", {}),
                    add_changelog=arguments.get("add_changelog", True),
                    dry_run=arguments.get("dry_run", False)
                )
            elif action == "get_structure":
                return await handle_get_structure(
                    file_path=arguments.get("file_path")
                )
            elif action == "create_pr":
                return await handle_create_pr(
                    title=arguments.get("title"),
                    description=arguments.get("description"),
                    draft=arguments.get("draft", True)
                )
            elif action == "check_pr_requirements":
                return await handle_check_pr_requirements()
            else:
                raise ValueError(f"Unknown documentation action: {action}")
        
        # Interview operations
        elif name == "interview":
            action = arguments.get("action")
            if action == "start":
                return await handle_start_interview(
                    source_file=arguments.get("source_file"),
                    template_content=arguments.get("template_content"),
                    template_name=arguments.get("template_name"),
                    component_type=arguments.get("component_type"),
                    priority_filter=arguments.get("priority_filter", "optional"),
                    role=arguments.get("role", "general")
                )
            elif action == "get_question":
                return await handle_get_next_question(
                    session_id=arguments.get("session_id")
                )
            elif action == "submit_answer":
                return await handle_submit_answer(
                    session_id=arguments.get("session_id"),
                    answer=arguments.get("answer"),
                    generate_draft=arguments.get("generate_draft", True)
                )
            elif action == "skip":
                return await handle_skip_question(
                    session_id=arguments.get("session_id"),
                    reason=arguments.get("reason", "Will provide later")
                )
            elif action == "progress":
                return await handle_get_progress(
                    session_id=arguments.get("session_id")
                )
            elif action == "end":
                return await handle_end_interview(
                    session_id=arguments.get("session_id")
                )
            else:
                raise ValueError(f"Unknown interview action: {action}")
        
        # Cross-repository operations
        elif name == "cross_repository":
            action = arguments.get("action")
            if action == "consolidate_feature":
                return await handle_consolidate_feature(
                    feature_name=arguments.get("feature_name"),
                    workspace_path=arguments.get("workspace_path")
                )
            elif action == "generate_testing":
                return await handle_generate_testing(
                    feature_name=arguments.get("feature_name"),
                    workspace_path=arguments.get("workspace_path"),
                    test_type=arguments.get("test_type", "integration")
                )
            elif action == "detect_changes":
                return await handle_detect_changes(
                    since=arguments.get("since"),
                    author=arguments.get("author"),
                    workspace_path=arguments.get("workspace_path")
                )
            elif action == "list_features":
                return await handle_list_features(
                    workspace_path=arguments.get("workspace_path")
                )
            elif action == "refresh_repos":
                return await handle_refresh_repos(
                    workspace_path=arguments.get("workspace_path")
                )
            elif action == "check_states":
                return await handle_check_states(
                    workspace_path=arguments.get("workspace_path")
                )
            elif action == "validate_traceability":
                return await handle_validate_traceability(
                    docs_dir=arguments.get("docs_dir", "docs"),
                    features_dir=arguments.get("features_dir"),
                    testing_dir=arguments.get("testing_dir")
                )
            else:
                raise ValueError(f"Unknown cross_repository action: {action}")
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"❌ Error executing {name}: {str(e)}"
        )]


# =============================================================================
# Resource Handlers
# =============================================================================
        logger.error(f"Error in tool {name}: {str(e)}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


# =============================================================================
# MCP Resource Handlers
# =============================================================================

@server.list_resources()
async def list_resources() -> list[Resource]:
    """
    List all available AKR resources.
    
    Returns resources organized by category (charters, templates, guides).
    Each resource has a URI in the format: akr://<category>/<filename>
    """
    logger.debug("Listing available resources")
    
    resources = []
    for akr_resource in resource_manager.list_resources():
        resources.append(Resource(
            uri=akr_resource.uri,
            name=akr_resource.name,
            description=akr_resource.description,
            mimeType=akr_resource.mime_type
        ))
    
    logger.info(f"Listed {len(resources)} resources")
    return resources


@server.list_resource_templates()
async def list_resource_templates() -> list[ResourceTemplate]:
    """
    List resource templates for dynamic resource discovery.
    
    Provides URI templates that clients can use to access resources
    by category.
    """
    logger.debug("Listing resource templates")
    
    return [
        ResourceTemplate(
            uriTemplate="akr://charter/{filename}",
            name="AKR Charter",
            description="Access AKR charter files by filename. Charters define documentation standards and requirements.",
            mimeType="text/markdown"
        ),
        ResourceTemplate(
            uriTemplate="akr://template/{filename}",
            name="AKR Template",
            description="Access documentation templates by filename. Templates provide structure for consistent documentation.",
            mimeType="text/markdown"
        ),
        ResourceTemplate(
            uriTemplate="akr://guide/{filename}",
            name="AKR Guide",
            description="Access developer guides by filename. Guides provide best practices and detailed instructions.",
            mimeType="text/markdown"
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """
    Read the content of an AKR resource by URI.
    
    Args:
        uri: Resource URI (e.g., "akr://charter/AKR_CHARTER_BACKEND.md")
        
    Returns:
        Resource content as string
    """
    logger.info(f"Reading resource: {uri}")
    server_state["resource_reads"] += 1
    
    content = resource_manager.read_resource(uri)
    
    if content is None:
        # Try to provide helpful error message
        available = resource_manager.list_resources()
        available_uris = [r.uri for r in available]
        
        error_msg = f"Resource not found: {uri}\n\n"
        error_msg += "Available resources:\n"
        for available_uri in sorted(available_uris):
            error_msg += f"  - {available_uri}\n"
        
        logger.warning(f"Resource not found: {uri}")
        raise ValueError(error_msg)
    
    logger.debug(f"Successfully read resource: {uri} ({len(content)} bytes)")
    return content


# =============================================================================
# Tool Handlers
# =============================================================================

async def handle_list_templates(
    project_type: str = "all", 
    verbose: bool = False,
    page: int = 1,
    page_size: int = 10
) -> list[TextContent]:
    """
    Handle the list_templates tool call with pagination support.
    
    Args:
        project_type: Filter by project type ('backend', 'ui', 'database', 'all')
        verbose: Include detailed information if True
        page: Page number (1-indexed)
        page_size: Items per page (max 20)
        
    Returns:
        Formatted list of templates with pagination info
    """
    logger.debug(f"list_templates called (project_type={project_type}, verbose={verbose}, page={page}, page_size={page_size})")
    
    # Get all templates first
    if project_type == "all":
        all_templates = list_all_templates()
    else:
        try:
            pt = ProjectType(project_type)
            all_templates = list_templates_by_project_type(pt)
        except ValueError:
            return [TextContent(
                type="text",
                text=f"Invalid project type: '{project_type}'. Use 'backend', 'ui', 'database', or 'all'."
            )]
    
    # Apply pagination
    total_templates = len(all_templates)
    page_size = min(page_size, 20)  # Max 20 per page
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    templates_page = all_templates[start_idx:end_idx]
    total_pages = (total_templates + page_size - 1) // page_size
    has_more = end_idx < total_templates
    
    # Format the results
    result = format_templates_list(templates_page, verbose=verbose)
    
    # Add pagination info
    pagination_info = f"\n\n📄 **Pagination**: Page {page} of {total_pages} | Showing {len(templates_page)} of {total_templates} templates"
    if has_more:
        pagination_info += f"\n💡 Use `page={page + 1}` to see more templates"
    
    result += pagination_info
    
    return [TextContent(type="text", text=result)]


async def handle_suggest_template(file_path: str, complexity: str = "standard") -> list[TextContent]:
    """
    Handle the suggest_template tool call.
    
    Args:
        file_path: Path to the file to document
        complexity: Preferred complexity level
        
    Returns:
        Template suggestion with alternatives
    """
    logger.debug(f"suggest_template called (file_path={file_path}, complexity={complexity})")
    
    if not file_path:
        return [TextContent(
            type="text",
            text="Error: file_path is required. Please provide the path to the file you want to document."
        )]
    
    # Parse complexity
    try:
        complexity_enum = TemplateComplexity(complexity) if complexity else None
    except ValueError:
        complexity_enum = None
        logger.warning(f"Invalid complexity: {complexity}, using default")
    
    # Get suggestion
    suggested = suggest_template_for_file(file_path, complexity_enum)
    
    if not suggested:
        return [TextContent(
            type="text",
            text=f"Could not find a suitable template for: {file_path}\n\nTry using `list_templates` to see all available templates."
        )]
    
    # Get alternatives (other templates of the same project type)
    alternatives = list_templates_by_project_type(suggested.project_type)
    
    result = format_template_suggestion(file_path, suggested, alternatives)
    return [TextContent(type="text", text=result)]


# =============================================================================
# Write Capability Tool Handlers
# =============================================================================

async def handle_initialize_session(
    workspace_path: str,
    branch_strategy: str = "create_new",
    branch_name: str = None
) -> list[TextContent]:
    """
    Initialize a documentation session for a workspace.
    
    Args:
        workspace_path: Path to the workspace/repository
        branch_strategy: Branch strategy to use
        branch_name: Branch name (for 'use_existing' strategy)
        
    Returns:
        Session initialization status
    """
    global doc_session
    
    logger.info(f"Initializing documentation session for: {workspace_path}")
    
    if not workspace_path:
        return [TextContent(
            type="text",
            text="Error: workspace_path is required. Provide the absolute path to your repository."
        )]
    
    # Check if workspace exists
    workspace = Path(workspace_path)
    if not workspace.exists():
        return [TextContent(
            type="text",
            text=f"Error: Workspace path does not exist: {workspace_path}"
        )]
    
    # Initialize managers
    config_manager = AKRConfigManager(workspace_path)
    branch_manager = BranchManager(workspace_path)
    
    # Load or suggest config
    config = config_manager.load_config()
    config_status = "loaded" if config else "using defaults"
    
    if not config:
        suggested = config_manager.suggest_initial_config()
        config_status = "suggested (not saved)"
    
    # Handle branch strategy
    strategy = BranchStrategy(branch_strategy)
    branch_result = None
    
    if strategy == BranchStrategy.CREATE_NEW:
        branch_result = branch_manager.create_documentation_branch()
    elif strategy == BranchStrategy.USE_EXISTING:
        if not branch_name:
            return [TextContent(
                type="text",
                text="Error: branch_name is required when using 'use_existing' strategy"
            )]
        branch_result = branch_manager.switch_branch(branch_name)
    elif strategy == BranchStrategy.USE_CURRENT:
        current = branch_manager.get_current_branch()
        main = branch_manager.get_main_branch()
        if current == main:
            return [TextContent(
                type="text",
                text=f"Error: Currently on {main} branch. Cannot write documentation to main branch. Use 'create_new' strategy instead."
            )]
        branch_result = {"success": True, "branch": current}
    
    if not branch_result or not branch_result.get("success"):
        error = branch_result.get("error", "Unknown error") if branch_result else "Branch operation failed"
        return [TextContent(
            type="text",
            text=f"Error setting up documentation branch: {error}"
        )]
    
    # Update session state
    doc_session.update({
        "active": True,
        "workspace_path": workspace_path,
        "branch_name": branch_result.get("branch"),
        "config": config,
        "files_documented": [],
        "branch_manager": branch_manager,
        "config_manager": config_manager
    })
    
    response = f"""# Documentation Session Initialized

## Session Details
- **Workspace:** `{workspace_path}`
- **Branch:** `{doc_session['branch_name']}`
- **Configuration:** {config_status}

## Ready for Documentation
You can now use the following tools:
- `write_documentation` - Create new documentation files
- `update_documentation_sections` - Update existing documentation
- `suggest_documentation_path` - Get suggested paths for new docs

When done, use `end_documentation_session` to create a PR.

## Safety Note
All changes will be made on branch `{doc_session['branch_name']}`.
The main branch is protected from direct writes.
"""

    return [TextContent(type="text", text=response)]


async def handle_get_project_config(workspace_path: str) -> list[TextContent]:
    """Get project configuration."""
    logger.debug(f"Getting project config for: {workspace_path}")
    
    if not workspace_path:
        # Use session workspace if available
        if doc_session.get("active") and doc_session.get("workspace_path"):
            workspace_path = doc_session["workspace_path"]
        else:
            return [TextContent(
                type="text",
                text="Error: workspace_path is required or initialize a session first."
            )]
    
    config_manager = AKRConfigManager(workspace_path)
    config = config_manager.load_config()
    
    if config:
        import json
        response = f"""# Project Configuration

**File:** `.akr-config.json`
**Status:** ✅ Found

## Configuration Details
```json
{json.dumps(config.__dict__ if hasattr(config, '__dict__') else config, indent=2, default=str)}
```
"""
    else:
        suggested = config_manager.suggest_initial_config()
        import json
        response = f"""# Project Configuration

**File:** `.akr-config.json`
**Status:** ⚠️ Not Found

## Suggested Configuration
The following configuration was auto-detected. You can create `.akr-config.json` with this content:

```json
{json.dumps(suggested, indent=2)}
```

## To Create Configuration
Use the command palette or run the setup wizard to create this file.
"""
    
    return [TextContent(type="text", text=response)]


async def handle_suggest_doc_path(source_file: str, workspace_path: str) -> list[TextContent]:
    """Suggest documentation path for a source file."""
    logger.debug(f"Suggesting doc path for: {source_file}")
    
    if not workspace_path:
        if doc_session.get("active"):
            workspace_path = doc_session["workspace_path"]
        else:
            return [TextContent(
                type="text",
                text="Error: workspace_path is required or initialize a session first."
            )]
    
    config_manager = AKRConfigManager(workspace_path)
    result = config_manager.get_documentation_path(source_file)
    
    response = f"""# Documentation Path Suggestion

## Source File
`{source_file}`

## Suggested Documentation Path
`{result['doc_path']}`

## Details
- **Component Type:** {result['component_type']}
- **Template:** {result['template']}

## Usage
Use this path when calling `write_documentation`:
```
write_documentation(
    doc_path="{result['doc_path']}",
    source_file="{source_file}",
    component_type="{result['component_type']}"
)
```
"""
    
    return [TextContent(type="text", text=response)]


async def handle_write_documentation(
    doc_path: str,
    content: str,
    source_file: str,
    component_type: str = "unknown",
    template_used: str = "standard",
    overwrite: bool = False
) -> list[TextContent]:
    """Write new documentation to the repository."""
    global doc_session
    
    logger.info(f"Writing documentation to: {doc_path}")
    
    # Check session is active
    if not doc_session.get("active"):
        return [TextContent(
            type="text",
            text="Error: No active documentation session. Call `initialize_documentation_session` first."
        )]
    
    # Validate required parameters
    if not doc_path or not content or not source_file:
        return [TextContent(
            type="text",
            text="Error: doc_path, content, and source_file are all required."
        )]
    
    workspace_path = doc_session["workspace_path"]
    
    # Write the documentation
    result = write_documentation(
        repo_path=workspace_path,
        doc_path=doc_path,
        content=content,
        source_file=source_file,
        component_type=component_type,
        template=template_used,
        overwrite=overwrite
    )
    
    if result.get("success"):
        # Track documented file
        doc_session["files_documented"].append({
            "source": source_file,
            "doc_path": doc_path,
            "component_type": component_type
        })
        
        response = f"""# ✅ Documentation Written Successfully

## File Created
- **Path:** `{result['filePath']}`
- **Source:** `{source_file}`
- **Type:** {component_type}
- **Template:** {template_used}

## Git Status
- **Branch:** `{result['branch']}`
- **Committed:** {'✅ Yes' if result.get('committed') else '❌ No'}
- **Commit Message:** {result.get('commitMessage', 'N/A')}

## Next Steps
1. Continue documenting more files, or
2. Call `create_documentation_pr` to create a Pull Request
"""
    else:
        response = f"""# ❌ Documentation Write Failed

## Error
{result.get('error', 'Unknown error occurred')}

## Details
- **Path:** `{doc_path}`
- **File Exists:** {'Yes' if result.get('exists') else 'No'}

## Suggestions
- If file exists, use `update_documentation_sections` for surgical updates
- Or set `overwrite=true` to replace the entire file
"""
    
    return [TextContent(type="text", text=response)]


async def handle_analyze_impact(file_path: str, proposed_sections: dict) -> list[TextContent]:
    """Analyze impact of proposed documentation updates."""
    logger.debug(f"Analyzing documentation impact for: {file_path}")
    
    result = analyze_documentation_impact(file_path, proposed_sections)
    
    if not result.get("success"):
        return [TextContent(
            type="text",
            text=f"Error: {result.get('error', 'Unknown error')}"
        )]
    
    response = f"""# Documentation Impact Analysis

## File
`{file_path}`

## Summary
- **Total Sections:** {result['total_sections']}
- **Sections to Update:** {len(result['sections_to_update'])}
- **Sections to Add:** {len(result['sections_to_add'])}
- **Sections Preserved:** {len(result['sections_preserved'])}

## Sections to Update (AI-Generated)
"""
    
    if result['sections_to_update']:
        for section in result['sections_to_update']:
            response += f"- **{section['title']}** (ID: `{section['id']}`)\n"
    else:
        response += "_No sections will be updated_\n"
    
    response += "\n## Sections Preserved (Human-Authored)\n"
    
    if result['sections_preserved']:
        for section in result['sections_preserved']:
            response += f"- **{section['title']}** - {section['reason']}\n"
    else:
        response += "_No sections will be preserved (all are AI-generated)_\n"
    
    if result['warnings']:
        response += "\n## ⚠️ Warnings\n"
        for warning in result['warnings']:
            response += f"- {warning}\n"
    
    return [TextContent(type="text", text=response)]


async def handle_update_sections(
    file_path: str,
    section_updates: dict,
    add_changelog: bool = True,
    dry_run: bool = False
) -> list[TextContent]:
    """Update documentation sections surgically."""
    logger.info(f"Updating documentation sections in: {file_path}")
    
    result = update_documentation_sections(
        file_path=file_path,
        section_updates=section_updates,
        add_changelog=add_changelog,
        dry_run=dry_run
    )
    
    if not result.get("success"):
        return [TextContent(
            type="text",
            text=f"Error: {result.get('error', 'Unknown error')}"
        )]
    
    if dry_run:
        response = f"""# Dry Run - Documentation Update Preview

## File
`{file_path}`

## Changes Preview
- **Lines after update:** {result['preview_lines']}
- **Total characters:** {result['preview_length']}

## Updates Applied (Preview)
"""
    else:
        response = f"""# ✅ Documentation Updated Successfully

## File
`{file_path}`

## Update Summary
- **Sections Updated:** {result.get('sections_updated', 0)}
- **Sections Preserved:** {result.get('sections_preserved', 0)}
- **Sections Not Found:** {result.get('sections_not_found', 0)}

## Update Details
"""
    
    for update in result.get('updates', []):
        status = '✅' if update['success'] else '❌'
        response += f"- {status} **{update['section_title']}** - {update['action']}\n"
    
    return [TextContent(type="text", text=response)]


async def handle_get_structure(file_path: str) -> list[TextContent]:
    """Get the structure of a documentation file."""
    logger.debug(f"Getting document structure for: {file_path}")
    
    result = get_document_structure(file_path)
    
    if not result.get("success"):
        return [TextContent(
            type="text",
            text=f"Error: {result.get('error', 'Unknown error')}"
        )]
    
    response = f"""# Document Structure

## File
`{file_path}`

## Overview
- **Total Sections:** {result['total_sections']}
- **AI-Generated Sections:** {result['ai_generated_sections']} 🤖
- **Sections Needing Input:** {result['sections_needing_input']} ❓
- **Section Types:** {', '.join(result['section_types_found'])}

## Sections
"""
    
    for section in result['sections']:
        markers = ""
        if section['is_ai_generated']:
            markers += " 🤖"
        if section['needs_human_input']:
            markers += " ❓"
        
        indent = "  " * (section['level'] - 1)
        response += f"{indent}- **{section['title']}**{markers}\n"
        response += f"{indent}  - ID: `{section['id']}`\n"
        response += f"{indent}  - Type: {section['type']}\n"
        response += f"{indent}  - Lines: {section['start_line']}-{section['end_line']}\n"
    
    return [TextContent(type="text", text=response)]


async def handle_create_pr(title: str, description: str, draft: bool = True) -> list[TextContent]:
    """Create a documentation Pull Request."""
    global doc_session
    
    logger.info(f"Creating PR: {title}")
    
    if not doc_session.get("active"):
        return [TextContent(
            type="text",
            text="Error: No active documentation session. Initialize a session and write some documentation first."
        )]
    
    if not doc_session.get("files_documented"):
        return [TextContent(
            type="text",
            text="Error: No files have been documented in this session. Write documentation first using `write_documentation`."
        )]
    
    workspace_path = doc_session["workspace_path"]
    files_documented = [f["doc_path"] for f in doc_session["files_documented"]]
    component_types = list(set(f["component_type"] for f in doc_session["files_documented"]))
    
    result = create_documentation_pr(
        repo_path=workspace_path,
        title=title,
        description=description,
        files_documented=files_documented,
        component_types=component_types,
        draft=draft
    )
    
    if result.get("success"):
        response = f"""# ✅ Pull Request Created Successfully

## PR Details
- **Number:** #{result['pr_number']}
- **Title:** {result['title']}
- **URL:** {result['pr_url']}
- **Status:** {'Draft' if result['draft'] else 'Ready for Review'}

## Branch Information
- **Source Branch:** `{result['branch']}`
- **Target Branch:** `{result['base_branch']}`

## Files Documented
"""
        for f in doc_session["files_documented"]:
            response += f"- `{f['doc_path']}` (from `{f['source']}`)\n"
        
        response += f"""
## Next Steps
1. Review the PR at {result['pr_url']}
2. Add business context where marked with ❓
3. Request reviews from team members
4. Merge when approved
"""
    else:
        action = result.get('action_needed', '')
        action_help = ""
        if action == "install_gh":
            action_help = "\n\n**To fix:** Install GitHub CLI from https://cli.github.com/"
        elif action == "auth_gh":
            action_help = "\n\n**To fix:** Run `gh auth login` in your terminal"
        
        response = f"""# ❌ Pull Request Creation Failed

## Error
{result.get('error', 'Unknown error')}{action_help}

## Session Status
Your documentation changes are still saved on branch `{doc_session['branch_name']}`.
You can:
1. Fix the issue and try again
2. Create the PR manually using: `gh pr create --title "{title}" --draft`
"""
    
    return [TextContent(type="text", text=response)]


async def handle_check_pr_requirements() -> list[TextContent]:
    """Check requirements for creating a PR."""
    logger.debug("Checking PR requirements")
    
    if not doc_session.get("active"):
        return [TextContent(
            type="text",
            text="Error: No active documentation session. Initialize a session first."
        )]
    
    workspace_path = doc_session["workspace_path"]
    result = check_documentation_pr_requirements(workspace_path)
    
    all_good = result.get('ready_for_pr', False)
    status = "✅ Ready" if all_good else "❌ Not Ready"
    
    response = f"""# PR Requirements Check

## Status: {status}

## Requirements
- **GitHub CLI Installed:** {'✅' if result['gh_installed'] else '❌'}
- **GitHub CLI Authenticated:** {'✅' if result['gh_authenticated'] else '❌'}
- **On Feature Branch:** {'✅' if result['on_feature_branch'] else '❌'}
- **No Uncommitted Changes:** {'✅' if not result['has_uncommitted_changes'] else '❌'}

## Branch Information
- **Current Branch:** `{result['current_branch']}`
- **Main Branch:** `{result['main_branch']}`
"""
    
    if result.get('issues'):
        response += "\n## Issues to Resolve\n"
        for issue in result['issues']:
            response += f"- ⚠️ {issue}\n"
    
    return [TextContent(type="text", text=response)]


async def handle_end_session(
    create_pr: bool = False,
    pr_title: str = None,
    pr_description: str = None
) -> list[TextContent]:
    """End the documentation session."""
    global doc_session
    
    logger.info("Ending documentation session")
    
    if not doc_session.get("active"):
        return [TextContent(
            type="text",
            text="No active documentation session to end."
        )]
    
    # Create PR if requested
    pr_result = None
    if create_pr:
        if not pr_title or not pr_description:
            return [TextContent(
                type="text",
                text="Error: pr_title and pr_description are required when create_pr is true."
            )]
        pr_result = await handle_create_pr(pr_title, pr_description)
    
    # Build summary
    files_count = len(doc_session.get("files_documented", []))
    branch = doc_session.get("branch_name", "unknown")
    
    response = f"""# Documentation Session Ended

## Session Summary
- **Workspace:** `{doc_session.get('workspace_path')}`
- **Branch:** `{branch}`
- **Files Documented:** {files_count}
"""
    
    if doc_session.get("files_documented"):
        response += "\n## Files Created/Updated\n"
        for f in doc_session["files_documented"]:
            response += f"- `{f['doc_path']}` ({f['component_type']})\n"
    
    if pr_result:
        response += "\n---\n"
        response += pr_result[0].text
    elif files_count > 0:
        response += f"""
## Next Steps
Your documentation is saved on branch `{branch}`.

To create a PR later:
```bash
git checkout {branch}
gh pr create --title "docs: Add documentation" --draft
```
"""
    
    # Reset session
    doc_session = {
        "active": False,
        "workspace_path": None,
        "branch_name": None,
        "config": None,
        "files_documented": [],
        "branch_manager": None,
        "config_manager": None
    }
    
    return [TextContent(type="text", text=response)]


async def health_check(verbose: bool = False) -> list[TextContent]:
    """
    Check server health and return status information.
    
    Returns:
        Server status, uptime, and optionally detailed statistics
    """
    logger.debug(f"Health check called (verbose={verbose})")
    
    # Calculate uptime
    uptime_seconds = 0
    if server_state["start_time"]:
        uptime_seconds = (datetime.now() - server_state["start_time"]).total_seconds()
    
    # Format uptime
    hours, remainder = divmod(int(uptime_seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    
    # Check AKR content availability
    akr_content_path = Path(__file__).parent.parent / "akr_content"
    charters_count = len(list((akr_content_path / "charters").glob("*.md"))) if (akr_content_path / "charters").exists() else 0
    templates_count = len(list((akr_content_path / "templates").glob("*.md"))) if (akr_content_path / "templates").exists() else 0
    guides_count = len(list((akr_content_path / "guides").glob("*.md"))) if (akr_content_path / "guides").exists() else 0
    
    status = {
        "status": "healthy",
        "server": config["server"]["name"],
        "version": config["server"].get("version", "0.1.0"),
        "uptime": uptime_str,
        "akr_content": {
            "charters": charters_count,
            "templates": templates_count,
            "guides": guides_count
        }
    }
    
    if verbose:
        status["statistics"] = {
            "tool_calls": server_state["tool_calls"],
            "resource_reads": server_state["resource_reads"],
            "errors": server_state["errors"]
        }
        status["paths"] = {
            "akr_content": str(akr_content_path),
            "logs": str(log_file)
        }
    
    response = f"""# AKR Documentation Server - Health Check

**Status:** ✅ {status['status'].upper()}

## Server Information
- **Name:** {status['server']}
- **Version:** {status['version']}
- **Uptime:** {status['uptime']}

## AKR Content Available
- **Charters:** {status['akr_content']['charters']} files
- **Templates:** {status['akr_content']['templates']} files
- **Guides:** {status['akr_content']['guides']} files
"""

    if verbose:
        response += f"""
## Statistics
- **Tool Calls:** {status['statistics']['tool_calls']}
- **Resource Reads:** {status['statistics']['resource_reads']}
- **Errors:** {status['statistics']['errors']}

## Paths
- **AKR Content:** `{status['paths']['akr_content']}`
- **Log File:** `{status['paths']['logs']}`
"""

    return [TextContent(type="text", text=response)]


async def get_server_info() -> list[TextContent]:
    """
    Get detailed information about server capabilities.
    
    Returns:
        Server capabilities, available tools, and resources
    """
    logger.debug("Get server info called")
    
    info = f"""# AKR Documentation Server

## Overview
This MCP server provides AKR (Application Knowledge Repository) documentation 
resources and tools to help generate consistent, high-quality documentation 
for your codebase.

## How It Works
1. **You ask Copilot** to document a file (e.g., "Document UserService.cs")
2. **Copilot calls this server** to get the appropriate charter and template
3. **This server returns** documentation standards and structure
4. **Copilot generates** the documentation following those guidelines
5. **You save** the generated documentation where you choose

## Available Tools

### `health_check`
Check server status and see available AKR content.
- Use: "Check the AKR documentation server health"

### `get_server_info`
Get this help information about the server.
- Use: "What can the AKR documentation server do?"

### `list_templates`
List all available documentation templates with metadata.
- Use: "List all documentation templates"
- Use: "Show backend templates"
- Use: "What templates are available for UI components?"

### `suggest_template`
Get template recommendation for a specific file.
- Use: "What template should I use for UserService.cs?"
- Use: "Suggest a template for my React component"

## Coming Soon
- `get_project_config` - Read project configuration
- `suggest_documentation_path` - Get recommended output path
- `validate_documentation` - Validate documentation against charter

## Project Configuration
Projects can include a `.akr-config.json` file to customize:
- Documentation output location
- Template selection per file type
- Validation requirements

Without a config file, sensible defaults are used.

## Server Version
- **Version:** {config["server"].get("version", "0.1.0")}
- **MCP SDK:** 1.22.0
"""

    return [TextContent(type="text", text=info)]


# =============================================================================
# Human Input Interview Tool Handlers
# =============================================================================

async def handle_start_interview(
    source_file: str,
    template_content: str,
    template_name: str,
    component_type: str,
    priority_filter: str = "optional",
    role: str = "general"
) -> list[TextContent]:
    """
    Start an interactive interview session for documentation.
    
    Args:
        source_file: Path to the source file being documented
        template_content: Template or generated doc content
        template_name: Name of the template used
        component_type: Type of component
        priority_filter: Filter questions by priority
        role: Interview role for question filtering
        
    Returns:
        Session info with first question
    """
    logger.info(f"Starting documentation interview for: {source_file} (role: {role})")
    
    if not source_file or not template_content:
        return [TextContent(
            type="text",
            text="Error: source_file and template_content are required to start an interview."
        )]
    
    # Load custom role profiles from project config if session is active
    custom_role_profiles = None
    if doc_session.get("active") and doc_session.get("config_manager"):
        config = doc_session["config_manager"].load_config()
        if config and hasattr(config, 'interview_roles') and config.interview_roles:
            custom_role_profiles = config.interview_roles.to_dict() if hasattr(config.interview_roles, 'to_dict') else None
    
    result = start_documentation_interview(
        source_file=source_file,
        template_content=template_content,
        template_name=template_name or "unknown",
        component_type=component_type or "unknown",
        priority_filter=priority_filter,
        role=role,
        custom_role_profiles=custom_role_profiles
    )
    
    if not result.get("success"):
        return [TextContent(
            type="text",
            text=f"Error starting interview: {result.get('error', 'Unknown error')}"
        )]
    
    # Format the response
    first_q = result.get("first_question")
    
    response = f"""# 🎤 Documentation Interview Started

## Session Details
- **Session ID:** `{result['session_id']}`
- **Source File:** `{result['source_file']}`
- **Template:** {result['template_name']}
- **Role:** {result.get('role_display_name', 'General')} ({result.get('role', 'general')})
- **Total Questions:** {result['total_questions']}
- **Questions Delegated to Other Roles:** {result.get('questions_delegated_to_others', 0)}

## Questions by Priority
- 🔴 **Critical:** {result['questions_by_priority']['critical']}
- 🟡 **Important:** {result['questions_by_priority']['important']}
- 🟢 **Optional:** {result['questions_by_priority']['optional']}

---

## First Question
"""

    if first_q:
        priority_emoji = {"critical": "🔴", "important": "🟡", "optional": "🟢"}
        response += f"""
**{first_q['question']}**

- **Section:** {first_q['section_title']}
- **Category:** {first_q['category']}
- **Priority:** {priority_emoji.get(first_q['priority'], '')} {first_q['priority'].capitalize()}

### Follow-up prompts (optional):
"""
        for prompt in first_q.get('follow_up_prompts', []):
            response += f"- {prompt}\n"
        
        if first_q.get('examples'):
            response += "\n### Example answers:\n"
            for example in first_q['examples']:
                response += f"> {example}\n\n"
        
        response += f"""
---

**To answer:** Use `submit_interview_answer` with session_id=`{result['session_id']}`
**To skip:** Use `skip_interview_question` if you don't have this info right now
**To see progress:** Use `get_interview_progress`
"""
    else:
        response += "\n_No questions detected that require human input._"
    
    return [TextContent(type="text", text=response)]


async def handle_get_next_question(session_id: str) -> list[TextContent]:
    """Get the current/next question in the interview."""
    logger.debug(f"Getting next question for session: {session_id}")
    
    if not session_id:
        return [TextContent(
            type="text",
            text="Error: session_id is required."
        )]
    
    result = get_next_interview_question(session_id)
    
    if not result.get("success"):
        return [TextContent(
            type="text",
            text=f"Error: {result.get('error', 'Unknown error')}"
        )]
    
    if result.get("is_complete"):
        summary = result.get("summary", {})
        response = f"""# ✅ Interview Complete!

## Summary
- **Total Questions:** {summary.get('progress', {}).get('total_questions', 0)}
- **Answered:** {summary.get('progress', {}).get('answered', 0)}
- **Skipped:** {summary.get('progress', {}).get('skipped', 0)}

Use `end_documentation_interview` to get all drafted content.
"""
        return [TextContent(type="text", text=response)]
    
    # Format current question
    priority_emoji = {"critical": "🔴", "important": "🟡", "optional": "🟢"}
    progress = result.get('progress', {})
    
    response = f"""# Question {result['question_number']} of {result['total_questions']}

**{result['question']}**

- **Section:** {result['section_title']}
- **Category:** {result['category']}
- **Priority:** {priority_emoji.get(result['priority'], '')} {result['priority'].capitalize()}

### Follow-up prompts:
"""
    for prompt in result.get('follow_up_prompts', []):
        response += f"- {prompt}\n"
    
    if result.get('examples'):
        response += "\n### Examples:\n"
        for example in result['examples']:
            response += f"> {example}\n\n"
    
    response += f"""
---

**Progress:** {progress.get('percent_complete', 0)}% complete ({progress.get('answered', 0)} answered, {progress.get('skipped', 0)} skipped)

**To answer:** Use `submit_interview_answer` with your response
**To skip:** Use `skip_interview_question` to skip for now
"""
    
    return [TextContent(type="text", text=response)]


async def handle_submit_answer(
    session_id: str,
    answer: str,
    generate_draft: bool = True
) -> list[TextContent]:
    """Submit an answer to the current interview question."""
    logger.info(f"Submitting answer for session: {session_id}")
    
    if not session_id or not answer:
        return [TextContent(
            type="text",
            text="Error: session_id and answer are required."
        )]
    
    result = submit_interview_answer(session_id, answer, generate_draft)
    
    if not result.get("success"):
        return [TextContent(
            type="text",
            text=f"Error: {result.get('error', 'Unknown error')}"
        )]
    
    progress = result.get('progress', {})
    
    response = f"""# ✅ Answer Recorded

## Section: {result['section_title']}

### Your Answer:
> {result['raw_answer']}
"""
    
    if result.get('drafted_content'):
        response += f"""
### 🤖 Drafted Content (ready for documentation):
```markdown
{result['drafted_content']}
```
"""
    
    response += f"""
---

**Progress:** {progress.get('percent_complete', 0)}% complete ({progress.get('answered', 0)} answered, {progress.get('skipped', 0)} skipped, {progress.get('remaining', 0)} remaining)
"""
    
    if result.get('is_complete'):
        response += """
## 🎉 Interview Complete!
All questions have been addressed. Use `end_documentation_interview` to get all drafted content.
"""
    else:
        next_q = result.get('next_question')
        if next_q:
            response += f"""
## Next Question:
**{next_q['question']}**
- Section: {next_q['section_title']}
- Priority: {next_q['priority'].capitalize()}
"""
    
    return [TextContent(type="text", text=response)]


async def handle_skip_question(session_id: str, reason: str = "Will provide later") -> list[TextContent]:
    """Skip the current interview question."""
    logger.info(f"Skipping question for session: {session_id}")
    
    if not session_id:
        return [TextContent(
            type="text",
            text="Error: session_id is required."
        )]
    
    result = skip_interview_question(session_id, reason)
    
    if not result.get("success"):
        return [TextContent(
            type="text",
            text=f"Error: {result.get('error', 'Unknown error')}"
        )]
    
    progress = result.get('progress', {})
    
    response = f"""# ⏭️ Question Skipped

**Section:** {result['section_id']}
**Reason:** {result['skip_reason']}

---

**Progress:** {progress.get('percent_complete', 0)}% complete ({progress.get('answered', 0)} answered, {progress.get('skipped', 0)} skipped, {progress.get('remaining', 0)} remaining)
"""
    
    if result.get('is_complete'):
        response += """
## Interview Complete!
Use `end_documentation_interview` to get all drafted content.
"""
    else:
        next_q = result.get('next_question')
        if next_q:
            response += f"""
## Next Question:
**{next_q['question']}**
- Section: {next_q['section_title']}
- Priority: {next_q['priority'].capitalize()}
"""
    
    return [TextContent(type="text", text=response)]


async def handle_get_progress(session_id: str) -> list[TextContent]:
    """Get the current progress of the documentation interview."""
    logger.debug(f"Getting interview progress for session: {session_id}")
    
    if not session_id:
        return [TextContent(
            type="text",
            text="Error: session_id is required."
        )]
    
    result = get_interview_progress(session_id)
    
    if not result.get("success"):
        return [TextContent(
            type="text",
            text=f"Error: {result.get('error', 'Unknown error')}"
        )]
    
    progress = result.get('progress', {})
    
    response = f"""# 📊 Interview Progress

## Session: `{result['session_id']}`
- **Source File:** `{result['source_file']}`
- **Template:** {result['template_name']}
- **Status:** {'✅ Complete' if result['is_complete'] else '🔄 In Progress'}

## Progress: {progress.get('percent_complete', 0)}%

| Status | Count |
|--------|-------|
| ✅ Answered | {progress.get('answered', 0)} |
| ⏭️ Skipped | {progress.get('skipped', 0)} |
| 📝 Remaining | {progress.get('remaining', 0)} |
| **Total** | {progress.get('total_questions', 0)} |

## Answered Sections
"""
    
    for section in result.get('answered_sections', []):
        draft_status = "📄 Draft ready" if section.get('has_draft') else ""
        response += f"- ✅ `{section['section_id']}` {draft_status}\n"
    
    if result.get('skipped_sections'):
        response += "\n## Skipped Sections (to revisit)\n"
        for section in result['skipped_sections']:
            response += f"- ⏭️ `{section['section_id']}`: {section['reason']}\n"
    
    return [TextContent(type="text", text=response)]


async def handle_end_interview(session_id: str) -> list[TextContent]:
    """End the interview session and get all drafted content."""
    logger.info(f"Ending interview session: {session_id}")
    
    if not session_id:
        return [TextContent(
            type="text",
            text="Error: session_id is required."
        )]
    
    result = end_documentation_interview(session_id)
    
    if not result.get("success"):
        return [TextContent(
            type="text",
            text=f"Error: {result.get('error', 'Unknown error')}"
        )]
    
    progress = result.get('progress', {})
    
    response = f"""# 🎉 Interview Session Complete

## Summary
- **Source File:** `{result['source_file']}`
- **Template:** {result['template_name']}
- **Role:** {result.get('role_display_name', 'General')}
- **Questions Answered:** {progress.get('answered', 0)}
- **Questions Skipped:** {progress.get('skipped', 0)}
- **Started:** {result.get('started_at', 'N/A')}
- **Completed:** {result.get('completed_at', 'N/A')}

## Drafted Content

Use the following content to enhance your documentation:

"""
    
    drafted = result.get('drafted_content', {})
    if drafted:
        for section_id, content in drafted.items():
            response += f"""### Section: `{section_id}`
```markdown
{content}
```

"""
    else:
        response += "_No drafted content (all questions were skipped)._\n"
    
    if result.get('skipped_sections'):
        response += "\n## Sections to Revisit\n"
        response += "The following sections were skipped and may need attention:\n\n"
        for section in result['skipped_sections']:
            response += f"- ❓ `{section['section_id']}`: {section['reason']}\n"
    
    # Add questions delegated to other roles
    questions_for_others = result.get('questions_for_other_roles', [])
    if questions_for_others:
        response += f"\n## 👥 Questions for Other Roles ({len(questions_for_others)} questions)\n"
        response += "The following questions were not asked because they are better suited for other team members:\n\n"
        
        # Group by suggested role
        by_role = {}
        for q in questions_for_others:
            role = q.get('suggested_role', 'Other')
            if role not in by_role:
                by_role[role] = []
            by_role[role].append(q)
        
        for role_name, questions in by_role.items():
            response += f"### 📋 For {role_name}:\n"
            for q in questions:
                priority_emoji = {"critical": "🔴", "important": "🟡", "optional": "🟢"}
                emoji = priority_emoji.get(q.get('priority', ''), '')
                response += f"- {emoji} **{q['section_title']}** ({q['category']})\n"
                response += f"  - Question: {q['question']}\n"
            response += "\n"
        
        response += "**Tip:** Start separate interview sessions with other team members to collect this context.\n"
    
    response += """
---

## Next Steps
1. Copy the drafted content above into your documentation file
2. Use `update_documentation_sections` to surgically update the file
3. Review and enhance the drafted content with additional details
4. Create a PR when ready using `create_documentation_pr`
"""
    
    return [TextContent(type="text", text=response)]


# =============================================================================
# Cross-Repository Consolidation Handlers
# =============================================================================

def _initialize_cross_repo_manager(workspace_path: str) -> CrossRepositoryManager:
    """Initialize or get the CrossRepositoryManager for a workspace."""
    global cross_repo_state
    
    workspace_path = Path(workspace_path)
    
    # Check if we already have a manager for this workspace
    if (cross_repo_state["manager"] is not None and 
        cross_repo_state["config"] and
        Path(cross_repo_state["config"].get("workspace_path", "")) == workspace_path):
        return cross_repo_state["manager"]
    
    # Load .akr-config.json from workspace
    config_path = workspace_path / ".akr-config.json"
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            f"Please ensure .akr-config.json exists in the workspace root."
        )
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Validate cross-repository configuration
    if 'crossRepository' not in config:
        raise ValueError(
            "Configuration missing 'crossRepository' section.\n"
            "Cross-repository consolidation requires proper configuration."
        )
    
    # Create manager
    manager = CrossRepositoryManager(config)
    
    # Store in state
    cross_repo_state["manager"] = manager
    cross_repo_state["config"] = {
        "workspace_path": str(workspace_path),
        **config.get('crossRepository', {})
    }
    cross_repo_state["last_update"] = datetime.now()
    
    logger.info(f"Initialized CrossRepositoryManager for {workspace_path}")
    return manager


async def handle_consolidate_feature(feature_name: str, workspace_path: str) -> list[TextContent]:
    """Handle feature consolidation request."""
    logger.info(f"Consolidating feature: {feature_name}")
    
    if not feature_name:
        return [TextContent(
            type="text",
            text="Error: feature_name is required."
        )]
    
    if not workspace_path:
        return [TextContent(
            type="text",
            text="Error: workspace_path is required."
        )]
    
    try:
        # Initialize manager
        manager = _initialize_cross_repo_manager(workspace_path)
        
        # Update repositories first
        logger.info("Updating related repositories...")
        manager.clone_or_update_repositories()
        
        # Consolidate the feature
        result = manager.consolidate_feature(feature_name)
        
        response = f"""# ✅ Feature Documentation Consolidated

## Feature: {feature_name}

### 📄 Output
- **Branch:** `{result['feature_branch']}`
- **File:** `{result['output_file']}`
- **Components:** {result['component_count']}

### 🌿 Feature Branch Workflow
The consolidated documentation has been committed to a **feature branch** for team review:
1. Branch created: `{result['feature_branch']}`
2. Documentation committed to branch
3. Branch pushed to remote

"""
        
        if result.get('pr_url'):
            response += f"""### 🔗 Pull Request
A pull request has been created for review:
- **URL:** {result['pr_url']}
- **Status:** Ready for review
- **Next Steps:**
  1. Review the consolidated documentation
  2. Verify technical accuracy
  3. Check architecture diagrams
  4. Approve and merge when ready

"""
        else:
            response += """### 📋 Next Steps
1. Review the generated documentation in the feature branch
2. Create a pull request manually with:
   ```bash
   gh pr create --title "Update {feature} docs" --base main --head {branch}
   ```
3. Request reviews from team members
4. Merge to main after approval

"""
        
        response += f"""
### ⚠️ Important Notes
- **Source:** Documentation collected from main branches ONLY
- **Quality:** Auto-generated - requires human review
- **Sections:** AI-generated sections marked for future updates
- **Review:** Must be reviewed before merging to main

---
📊 **Component Statistics:**
- Repositories scanned: {len(manager.repositories)} repositories
- Feature tags matched: {result['component_count']} components
- Documentation generated: 1 consolidated file

**Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return [TextContent(type="text", text=response)]
    
    except Exception as e:
        logger.error(f"Failed to consolidate feature {feature_name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error consolidating feature '{feature_name}': {str(e)}"
        )]


async def handle_generate_testing(
    feature_name: str,
    workspace_path: str,
    test_type: str = "integration"
) -> list[TextContent]:
    """Handle testing documentation generation request."""
    logger.info(f"Generating testing documentation for feature: {feature_name}")
    
    if not feature_name:
        return [TextContent(
            type="text",
            text="Error: feature_name is required."
        )]
    
    if not workspace_path:
        return [TextContent(
            type="text",
            text="Error: workspace_path is required."
        )]
    
    try:
        import subprocess
        from pathlib import Path
        
        # Build command to run consolidator with --outputs testing flag
        cmd = [
            "python",
            "scripts/aggregation/consolidator.py",
            "--feature", feature_name,
            "--workspace", workspace_path,
            "--outputs", "testing"
        ]
        
        # Run consolidator
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            return [TextContent(
                type="text",
                text=f"""Error generating testing documentation:

**Exit Code:** {result.returncode}

**Output:**
```
{result.stdout}
```

**Error:**
```
{result.stderr}
```

**Troubleshooting:**
1. Ensure feature documentation exists for '{feature_name}'
2. Check that .akr-config.json is properly configured
3. Verify consolidation-config.json is in place
4. Run consolidation on feature documentation first
"""
            )]
        
        # Parse output to find generated file
        output_lines = result.stdout.split('\n')
        testing_file = None
        for line in output_lines:
            if 'testing-' in line.lower() and '.md' in line:
                testing_file = line.strip()
                break
        
        response = f"""# ✅ Testing Documentation Generated

## Feature: {feature_name}

### 📄 Output
- **Type:** {test_type.capitalize()} Testing Documentation
- **Template:** feature-testing-consolidated.md
- **Status:** Generated successfully

"""
        
        if testing_file:
            response += f"""### 📁 Generated File
- **Path:** `{testing_file}`

"""
        
        response += f"""### 📋 Document Structure
The testing documentation includes:
- **Test Context:** Feature overview and testing scope
- **Test Scenarios:** Key scenarios to validate
- **Test Cases:** Detailed test case specifications
- **Expected Results:** Success criteria for each test
- **Traceability:** Links back to feature documentation

### 🔗 Bidirectional Traceability
The generated testing documentation automatically includes:
- `relatedFeature:` link pointing to `{feature_name}`
- Feature documentation should have `relatedTesting:` array including this doc

### 📋 Next Steps
1. Review the generated testing documentation
2. Verify test scenarios match feature requirements
3. Validate traceability links using `/docs.validate-testing-traceability`
4. Add detailed test steps and assertions
5. Commit to feature branch for review

---

**Console Output:**
```
{result.stdout}
```

**Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return [TextContent(type="text", text=response)]
    
    except FileNotFoundError:
        return [TextContent(
            type="text",
            text="""Error: consolidator.py script not found.

Expected location: scripts/aggregation/consolidator.py

Please ensure the consolidation script exists in the akr-mcp-server directory.
"""
        )]
    except Exception as e:
        logger.error(f"Failed to generate testing documentation: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error generating testing documentation: {str(e)}"
        )]


async def handle_detect_changes(since: str, author: Optional[str], workspace_path: str) -> list[TextContent]:
    """Handle change detection request."""
    logger.info(f"Detecting changes since: {since}")
    
    if not since:
        return [TextContent(
            type="text",
            text="Error: 'since' parameter is required (e.g., 'yesterday', '7d', '2026-01-10')."
        )]
    
    if not workspace_path:
        return [TextContent(
            type="text",
            text="Error: workspace_path is required."
        )]
    
    try:
        # Initialize manager
        manager = _initialize_cross_repo_manager(workspace_path)
        
        # Update repositories first
        logger.info("Updating related repositories...")
        manager.clone_or_update_repositories()
        
        # Detect changes
        affected_features = manager.detect_changes(since, author)
        
        if not affected_features:
            return [TextContent(
                type="text",
                text=f"""# 🔍 No Feature Changes Detected

**Time Range:** Since {since}
**Author Filter:** {author if author else "All authors"}
**Branch Scanned:** Main branches only

No changes found that affect documented features.

**Note:** Only changes on main/stable branches are tracked for consolidation.
Feature branches are intentionally excluded.
"""
            )]
        
        response = f"""# 🔍 Feature Change Detection

**Time Range:** Since {since}
**Author Filter:** {author if author else "All authors"}
**Affected Features:** {len(affected_features)}

---

"""
        
        for feature, changes in affected_features.items():
            response += f"""## 📦 {feature}
**Changes:** {len(changes)} component(s) modified

"""
            # Group by repository
            by_repo = {}
            for change in changes:
                repo = change['repository']
                if repo not in by_repo:
                    by_repo[repo] = []
                by_repo[repo].append(change)
            
            for repo, repo_changes in by_repo.items():
                response += f"### {repo}\n"
                for change in repo_changes:
                    response += f"- `{change['file']}` ({change['layer']})\n"
                    response += f"  - **Modified:** {change['timestamp']}\n"
                    response += f"  - **Author:** {change['author']}\n"
            
            response += "\n"
        
        response += """---

## 📋 Recommended Actions
1. Review the changed components above
2. Decide which features need documentation updates
3. Use `consolidate_feature` to regenerate affected feature docs
4. Create PRs for consolidated documentation updates

**Example:**
```
For feature "user-authentication":
  consolidate_feature(feature_name="user-authentication", workspace_path="...")
```
"""
        
        return [TextContent(type="text", text=response)]
    
    except Exception as e:
        logger.error(f"Failed to detect changes: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error detecting changes: {str(e)}"
        )]


async def handle_list_features(workspace_path: str) -> list[TextContent]:
    """Handle list features request."""
    logger.info("Listing all features")
    
    if not workspace_path:
        return [TextContent(
            type="text",
            text="Error: workspace_path is required."
        )]
    
    try:
        # Initialize manager
        manager = _initialize_cross_repo_manager(workspace_path)
        
        # Update repositories first
        logger.info("Updating related repositories...")
        manager.clone_or_update_repositories()
        
        # Collect all features
        features = {}
        for repo in manager.repositories:
            if not repo.get('enabled', True):
                continue
            
            repo_name = repo['name']
            repo_path = manager.cache_dir / repo_name
            docs_path = repo_path / repo.get('docsPath', 'docs/')
            
            if not docs_path.exists():
                continue
            
            # Scan all .md files
            for md_file in docs_path.rglob('*.md'):
                feature = manager._extract_feature_from_file(md_file)
                if feature:
                    if feature not in features:
                        features[feature] = {
                            'components': [],
                            'layers': set()
                        }
                    features[feature]['components'].append({
                        'name': md_file.stem,
                        'repository': repo_name,
                        'layer': repo['layer']
                    })
                    features[feature]['layers'].add(repo['layer'])
        
        if not features:
            return [TextContent(
                type="text",
                text="""# 📦 No Features Found

No features were discovered in the related repositories.

**Possible Reasons:**
1. No documentation files have feature tags in YAML front matter
2. Repositories haven't been cloned yet (run `refresh_repositories`)
3. Documentation paths may be misconfigured

**Example Feature Tag in Documentation:**
```yaml
---
feature: user-authentication
layer: API
---
```
"""
            )]
        
        response = f"""# 📦 Available Features

**Total Features:** {len(features)}
**Repositories Scanned:** {len([r for r in manager.repositories if r.get('enabled', True)])}

---

"""
        
        for feature_name, feature_data in sorted(features.items()):
            components = feature_data['components']
            layers = sorted(feature_data['layers'])
            
            response += f"""## {feature_name}
- **Components:** {len(components)}
- **Layers:** {', '.join(layers)}

"""
            # Group by repository
            by_repo = {}
            for comp in components:
                repo = comp['repository']
                if repo not in by_repo:
                    by_repo[repo] = []
                by_repo[repo].append(comp)
            
            for repo_name, repo_comps in by_repo.items():
                response += f"### {repo_name}\n"
                for comp in repo_comps:
                    response += f"- {comp['name']} ({comp['layer']})\n"
            
            response += "\n"
        
        response += """---

## 📋 Next Steps
1. Choose a feature to consolidate
2. Run `consolidate_feature(feature_name="...", workspace_path="...")`
3. Review the generated consolidated documentation
4. Create a PR for team review
"""
        
        return [TextContent(type="text", text=response)]
    
    except Exception as e:
        logger.error(f"Failed to list features: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error listing features: {str(e)}"
        )]


async def handle_refresh_repos(workspace_path: str) -> list[TextContent]:
    """Handle repository refresh request."""
    logger.info("Refreshing repositories")
    
    if not workspace_path:
        return [TextContent(
            type="text",
            text="Error: workspace_path is required."
        )]
    
    try:
        # Initialize manager
        manager = _initialize_cross_repo_manager(workspace_path)
        
        # Clone/update all repositories
        manager.clone_or_update_repositories()
        
        response = """# ✅ Repositories Refreshed

All related repositories have been cloned or updated to the latest versions.

"""
        
        # Show repository states
        response += "## 📊 Repository States\n\n"
        
        for repo in manager.repositories:
            if not repo.get('enabled', True):
                response += f"- ⊗ **{repo['name']}** (disabled)\n"
                continue
            
            repo_name = repo['name']
            repo_path = manager.cache_dir / repo_name
            branch = repo['branch']
            
            if repo_path.exists():
                try:
                    current_branch = manager._get_current_branch(repo_path)
                    response += f"- ✅ **{repo['name']}**\n"
                    response += f"  - Branch: `{current_branch}` (expected: `{branch}`)\n"
                    response += f"  - Layer: {repo['layer']}\n"
                except Exception as e:
                    response += f"- ⚠️  **{repo['name']}**: {str(e)}\n"
            else:
                response += f"- ❌ **{repo['name']}**: Not cloned\n"
        
        response += f"""
---

**Cache Directory:** `{manager.cache_dir}`
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 Next Steps
1. Use `list_features` to see all available features
2. Use `detect_feature_changes` to find recently modified features
3. Use `consolidate_feature` to generate consolidated documentation
"""
        
        return [TextContent(type="text", text=response)]
    
    except Exception as e:
        logger.error(f"Failed to refresh repositories: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error refreshing repositories: {str(e)}"
        )]


async def handle_check_states(workspace_path: str) -> list[TextContent]:
    """Handle repository state check request."""
    logger.info("Checking repository states")
    
    if not workspace_path:
        return [TextContent(
            type="text",
            text="Error: workspace_path is required."
        )]
    
    try:
        # Initialize manager
        manager = _initialize_cross_repo_manager(workspace_path)
        
        # Log repository states (this logs to console/file)
        manager.log_repository_states()
        
        response = """# 📊 Repository States

"""
        
        for repo in manager.repositories:
            if not repo.get('enabled', True):
                response += f"## ⊗ {repo['name']} (Disabled)\n\n"
                continue
            
            repo_name = repo['name']
            repo_path = manager.cache_dir / repo_name
            branch = repo['branch']
            
            response += f"## {repo_name}\n"
            
            if not repo_path.exists():
                response += """- **Status:** ❌ Not cloned
- **Action Required:** Run `refresh_repositories` to clone

"""
                continue
            
            try:
                # Get current branch
                current_branch = manager._get_current_branch(repo_path)
                
                # Get latest commit
                result = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                commit_sha = result.stdout.strip()[:7]
                
                # Get commit message
                result = subprocess.run(
                    ['git', 'log', '-1', '--format=%s'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                commit_msg = result.stdout.strip()
                
                # Get commit date
                result = subprocess.run(
                    ['git', 'log', '-1', '--format=%cd', '--date=relative'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                commit_date = result.stdout.strip()
                
                # Check if branch matches config
                branch_status = "✅" if current_branch == branch else "⚠️"
                
                response += f"""- **Status:** ✅ Cloned and up-to-date
- **Branch:** {branch_status} `{current_branch}` (expected: `{branch}`)
- **Latest Commit:** `{commit_sha}` - {commit_msg}
- **Updated:** {commit_date}
- **Layer:** {repo['layer']}
- **Docs Path:** `{repo.get('docsPath', 'docs/')}`

"""
            except Exception as e:
                response += f"- **Status:** ⚠️  Error: {str(e)}\n\n"
        
        response += f"""---

**Cache Directory:** `{manager.cache_dir}`
**Checked At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🔍 Branch Management Notes
- **Main Branch Only:** Consolidation reads from configured branches (main/master)
- **Feature Branches Excluded:** Unapproved changes are not included
- **⚠️  Branch Mismatch:** If current != expected, run `refresh_repositories`
"""
        
        return [TextContent(type="text", text=response)]
    
    except Exception as e:
        logger.error(f"Failed to check repository states: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error checking repository states: {str(e)}"
        )]


async def handle_validate_traceability(
    docs_dir: str = "docs",
    features_dir: str = None,
    testing_dir: str = None
) -> list[TextContent]:
    """Handle traceability validation request."""
    logger.info(f"Validating traceability for docs_dir: {docs_dir}")
    
    try:
        import subprocess
        import json
        from pathlib import Path
        
        # Build command arguments
        cmd = [
            "python",
            "scripts/validation/validate_traceability.py",
            "--json"
        ]
        
        if features_dir and testing_dir:
            cmd.extend(["--features-dir", features_dir, "--testing-dir", testing_dir])
        else:
            cmd.extend(["--docs-dir", docs_dir])
        
        # Run validation script
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False  # Don't raise on non-zero exit (validation warnings/errors)
        )
        
        # Parse JSON output
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            # If JSON parsing fails, return raw output
            return [TextContent(
                type="text",
                text=f"Validation script output:\n{result.stdout}\n\nErrors:\n{result.stderr}"
            )]
        
        # Format response
        response = f"""# 🔗 Traceability Validation

## 📊 Summary
- **Features:** {report.get('total_features', 0)}
- **Testing Docs:** {report.get('total_testing_docs', 0)}
- **Matched Pairs:** {report.get('matched_pairs', 0)}
- **Errors:** {len(report.get('errors', []))}
- **Warnings:** {len(report.get('warnings', []))}

"""
        
        # Add errors section
        errors = report.get('errors', [])
        if errors:
            response += "## ❌ Errors\n\n"
            for error in errors[:10]:  # Show first 10 errors
                response += f"- {error}\n"
            if len(errors) > 10:
                response += f"\n...and {len(errors) - 10} more errors\n"
            response += "\n"
        
        # Add warnings section
        warnings = report.get('warnings', [])
        if warnings:
            response += "## ⚠️  Warnings\n\n"
            for warning in warnings[:10]:  # Show first 10 warnings
                response += f"- {warning}\n"
            if len(warnings) > 10:
                response += f"\n...and {len(warnings) - 10} more warnings\n"
            response += "\n"
        
        # Add validated pairs section
        validated = report.get('validated_pairs', [])
        if validated:
            response += "## ✅ Validated Pairs\n\n"
            for pair in validated[:5]:  # Show first 5
                response += f"- Feature `{pair['feature']}` ↔️ Testing `{pair['testing']}`\n"
            if len(validated) > 5:
                response += f"\n...and {len(validated) - 5} more validated pairs\n"
            response += "\n"
        
        # Add recommendations
        if errors or warnings:
            response += """## 📋 Next Steps

"""
            if errors:
                response += """### Fix Critical Issues
1. Review errors above and create missing documentation files
2. Update front matter with correct `relatedTesting`/`relatedFeature` links
3. Ensure all linked files exist at the specified paths

"""
            if warnings:
                response += """### Address Warnings
1. Consider creating testing documentation for features without tests
2. Add `relatedTesting` fields to feature documents
3. Add `relatedFeature` fields to testing documents

"""
        else:
            response += """## 🎉 All Validation Checks Passed!

All feature and testing documents have proper bidirectional links.
"""
        
        # Add exit code context
        exit_code = result.returncode
        if exit_code == 0:
            response += "\n**Status:** ✅ No issues found\n"
        elif exit_code == 1:
            response += "\n**Status:** ❌ Critical errors found (see above)\n"
        elif exit_code == 2:
            response += "\n**Status:** ⚠️  Warnings found (non-blocking)\n"
        
        return [TextContent(type="text", text=response)]
    
    except FileNotFoundError:
        return [TextContent(
            type="text",
            text="""Error: validate_traceability.py script not found.

Expected location: scripts/validation/validate_traceability.py

Please ensure the validation script exists in the akr-mcp-server directory.
"""
        )]
    except Exception as e:
        logger.error(f"Failed to validate traceability: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error validating traceability: {str(e)}"
        )]


async def main():

    """Main entry point for the MCP server."""
    logger.info("=" * 60)
    logger.info("Starting AKR Documentation Server")
    logger.info(f"Version: {config['server'].get('version', '0.1.0')}")
    logger.info("=" * 60)
    
    # Record start time
    server_state["start_time"] = datetime.now()
    
    try:
        # Run the server using stdio transport
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server initialized, waiting for connections...")
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("Server shutting down")


if __name__ == "__main__":
    asyncio.run(main())


