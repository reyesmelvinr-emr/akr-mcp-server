import os
import sys
import logging
import json
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


# Import AKR resource manager
from resources import AKRResourceManager, ResourceCategory, create_resource_manager

# ==================== FIXED: Remove invalid imports ====================
# Import workspace tools
from tools.workspace import create_workspace_manager

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

logger.info(f"🚀 Server starting in mode: FAST_MODE={FAST_MODE}, SKIP_INIT={SKIP_INITIALIZATION}")
# ======================================================================

# Create MCP server instance
server = Server("akr-documentation-server")

# Global state (initialized lazily in fast mode)
resource_manager: Optional[AKRResourceManager] = None
workspace_manager: Optional[object] = None
config: Optional[dict] = None


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


# ==================== NEW CODE: LAZY INITIALIZATION FUNCTION ====================
def ensure_initialized():
    """
    Initialize resources only when first needed (lazy loading).
    This function is called before any tool/resource is accessed,
    but skipped during server startup in fast mode.
    """
    global resource_manager, workspace_manager, config
    
    if resource_manager is not None:
        # Already initialized
        return
    
    logger.info("⏳ Lazy-initializing resources...")
    
    try:
        # Load configuration
        config = load_config()
        logger.info("✅ Configuration loaded")
        
        # Create resource manager (minimal, no scanning)
        resource_manager = create_resource_manager()
        logger.info("✅ Resource manager created")
        
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
    mgr = get_resource_manager()
    resources: list[Resource] = []
    for r in mgr.list_resources():
        resources.append(
            Resource(
                uri=r.uri,
                name=r.name,
                description=r.description,
                mimeType=r.mime_type,
            )
        )
    return resources


@server.read_resource()
async def read_resource(uri: str) -> str:
    mgr = get_resource_manager()
    content = mgr.read_resource(uri)
    if content is None:
        available = [res.uri for res in mgr.list_resources()]
        msg = "Resource not found: {0}\n\nAvailable resources:\n{1}".format(
            uri, "\n".join(f" - {u}" for u in sorted(available))
        )
        return msg
    return content


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available AKR documentation tools."""
    tools = [
        Tool(
            name="analyze_codebase",
            description="Analyze a codebase structure and identify components for documentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "codebase_path": {
                        "type": "string",
                        "description": "Path to the codebase to analyze"
                    },
                    "file_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "File types to analyze (e.g., ['.ts', '.tsx', '.py'])"
                    }
                },
                "required": ["codebase_path"]
            }
        ),
        Tool(
            name="generate_documentation",
            description="Generate AKR-compliant documentation from codebase analysis",
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
                        "description": "Template to use (optional; defaults based on component_type)"
                    }
                },
                "required": ["component_name", "component_type"]
            }
        ),
        Tool(
            name="validate_documentation",
            description="Validate documentation against AKR standards",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the documentation file to validate"
                    }
                },
                "required": ["file_path"]
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
        )
    ]
    
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute an AKR documentation tool."""
    ensure_initialized()
    
    logger.info(f"🔧 Tool called: {name}")
    
    if name == "analyze_codebase":
        codebase_path = arguments.get("codebase_path")
        file_types = arguments.get("file_types", [".ts", ".tsx", ".py", ".java"])
        
        # Placeholder implementation
        result = f"Analyzing codebase at {codebase_path} for file types {file_types}..."
        return [TextContent(type="text", text=result)]
    
    elif name == "generate_documentation":
        component_name = arguments.get("component_name")
        component_type = arguments.get("component_type")
        template = arguments.get("template")
        
        # Placeholder implementation
        result = f"Generating {component_type} documentation for '{component_name}'..."
        return [TextContent(type="text", text=result)]
    
    elif name == "validate_documentation":
        file_path = arguments.get("file_path")
        
        # Placeholder implementation
        result = f"Validating documentation at {file_path}..."
        return [TextContent(type="text", text=result)]
    
    elif name == "get_charter":
        domain = arguments.get("domain")
        
        if resource_manager:
            charter = resource_manager.get_charter(domain)
            if charter:
                charter.load_content()  # Load content if not already loaded
                return [TextContent(type="text", text=charter.content)]
        
        return [TextContent(type="text", text=f"Charter not found for domain: {domain}")]
    
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