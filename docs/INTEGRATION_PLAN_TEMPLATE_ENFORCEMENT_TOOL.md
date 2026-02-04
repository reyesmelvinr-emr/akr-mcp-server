# Integration Plan: Template Enforcement Tool into AKR MCP Server
## FINAL VERSION WITH REPO-SPECIFIC FIXES

**Document Version:** 2.0 (Comprehensive Repository Assessment Applied)  
**Date:** February 3, 2026  
**Status:** Ready for Copilot Agent Execution  
**Owner:** AKR MCP Server Team  
**Revisions:** Applied critical M365 Copilot assessment identifying bypass paths in existing code

---

## 📋 Executive Summary

This document outlines integration of the completed Template Enforcement Tool components into the AKR MCP server's documentation generation workflow **with critical fixes for existing bypass paths** in your codebase.

**🔴 CRITICAL REPO REALITY:**
Your codebase currently has **THREE ways to write docs WITHOUT enforcement**:
1. `write_documentation()` → `DocumentationWriter.write_file()` (no enforcement gate)
2. `update_documentation_sections()` → direct `Path.write_text()` (bypasses git AND enforcement)
3. `add_ai_header()` prepends HTML comment BEFORE YAML (violates YAML-first rule)

**This plan makes enforcement the UNAVOIDABLE gate for all paths and fixes the YAML conflict.**

**Expected Timeline:** 2-3 days (4 focused batches, ~20-25 hours total)  
**Deliverable:** All doc writes enforced; no bypass paths; git workflow preserved

**Config Naming Convention:** JSON config uses **mixed-case naming for backward compatibility**:
- Existing keys are mixed: `output_path` (snake_case), `pathMappings` (camelCase legacy)
- New enforcement keys use camelCase: `writeMode`, `requireYamlFrontmatter`, `enforceSectionOrder`, `autoFixEnabled`, `allowRetry`, `maxRetries`

---

## 🎯 Architecture: How Enforcement Becomes the Only Writer

Your repo uses `DocumentationWriter` to handle git operations (stage, commit, push). The enforcement tool's role is:

1. **Validate** markdown against template schema (YAML, sections, order, heading hierarchy)
2. **Auto-fix** fixable issues (missing YAML, wrong order)
3. **Return validated markdown** to the caller
4. **Caller writes via `DocumentationWriter`** (which stages and commits)

**This diagram shows the hard-gate architecture:**

```
LLM Output
   │
   ▼
[ENFORCEMENT: enforce_and_fix()]  ◄── HARD GATE
   │
   ├─→ INVALID? Return error, no write
   │
   └─→ VALID? 
       │
       ▼
   [Inject AI header AFTER YAML]
       │
       ▼
   [DocumentationWriter.write_file()]
       │
       ▼
   stage → commit → push (git workflow)
```

**Key principle:** Enforcement is the ONLY path that can return "write-safe" markdown.

---

## 📊 Current State: What Needs Fixing

| Code Path | Current Issue | Fix in This Plan |
|-----------|---------------|------------------|
| `write_documentation()` | Writes without enforcement | Insert enforcement gate (Task 3.1) |
| `update_documentation_sections()` | Direct `Path.write_text()` | Convert to pure logic; move write+enforce+commit to new function (Task 3.2) |
| `add_ai_header()` | Prepends comment BEFORE YAML | Move insertion to AFTER YAML closing delimiter (Task 3.0) |
| MCP dispatcher | Only 4 tools; most are placeholders | Wire real write/update functions (Task 2.1) |
| Config schema | No enforcement controls | Add `enforcement` section with `writeMode` (Task 1.3) |

---

## 🚀 Implementation Batches (4 Sequential)

All batches must complete in order; each unblocks the next.

### BATCH 1: Server Preparation (4-6 hours)

**Objective:** Imports, config, telemetry (no logic changes yet)

#### Task 1.1: Add Enforcement Imports to `server.py`

**File:** `src/server.py` (after existing tool imports)

**IMPORTANT:** Use the same import style as your existing server.py (`from tools...`, not `from src.tools...`):

```python
# CANONICAL IMPORTS (used consistently throughout)
from tools.enforcement_tool import enforce_and_fix
from tools.enforcement_tool_types import FileMetadata
from tools.write_operations import (
    write_documentation,
    update_documentation_sections_and_commit
)
```

**Acceptance:** All imports resolve using `from tools...` pattern; no circular dependencies; matches existing `from tools.workspace` style.

#### Task 1.2: Add Telemetry Logger

**File:** `src/server.py`

```python
# Initialize enforcement telemetry
enforcement_logger = None

def init_enforcement_telemetry(log_path: str = "logs/enforcement.jsonl"):
    global enforcement_logger
    try:
        from tools.enforcement_logger import EnforcementLogger
        enforcement_logger = EnforcementLogger(log_path)
    except Exception as e:
        logger.warning(f"Could not init enforcement telemetry: {e}")
```

**Call this function in `ensure_initialized()`:**

```python
def ensure_initialized():
    global resource_manager
    if resource_manager is None:
        resource_manager = get_resource_manager()
        init_enforcement_telemetry()  # Add this line
```

**IMPORTANT:** Preserve `config = load_config()` inside `ensure_initialized()`—Task 2.1 relies on global `config` being set.

**Acceptance:** Logger initialized without errors at startup; `logs/enforcement.jsonl` file is created on first logged event (or immediately at startup depending on logger implementation); logger object passed to enforcement calls in dispatcher.

#### Task 1.3: Add Enforcement Config to `config.json`

**File:** `config.json`

```json
{
  "documentation": {
    "output_path": "docs/",
    "pathMappings": { "src/**/*.cs": "docs/{module}.md" },
    "enforcement": {
      "enabled": true,
      "validationStrictness": "baseline",
      "requireYamlFrontmatter": true,
      "enforceSectionOrder": true,
      "autoFixEnabled": true,
      "allowRetry": true,
      "maxRetries": 3,
      "writeMode": "git"
    }
  }
}
```

**Config Naming Convention Note:**
- Existing keys are mixed for backward compatibility: output_path (snake_case), pathMappings (camelCase legacy)
- New enforcement keys use camelCase: `writeMode`, `requireYamlFrontmatter`, `enforceSectionOrder`, `autoFixEnabled`, `allowRetry`, `maxRetries`

**Config Loading Clarification:**
`load_config()` returns the root dict. Enforcement settings are read via `config["documentation"]["enforcement"]`. Task 2.1 passes this loaded config directly to write functions, which access enforcement settings using the same path.

**Acceptance:** Config loads without error; all enforcement keys present.

---

### BATCH 2: Dispatcher & Tool Registration (4-5 hours)

**Objective:** Wire real write tools into dispatcher; add schemas

#### Task 2.1: Replace Placeholder Tools in `server.py` Dispatcher

**File:** `src/server.py` - in `call_tool()` function

Your current dispatcher has placeholders like `return [TextContent(type="text", text="Generating...")]`.

**Replace with real function calls:**

```python
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Dispatch tool calls to implementations."""
    
    # Use the global config loaded by ensure_initialized()
    # (Avoid reassigning global config in function scope)
    global config
    cfg = config  # Local reference to avoid scope issues
    
    if name == "get_charter":
        # Keep existing implementation
        ...
    
    elif name == "write_documentation":
        # ENFORCEMENT GATE 🔴
        try:
            # Log start of write operation
            if enforcement_logger:
                enforcement_logger.log_start(name, arguments)
            
            result = write_documentation(
                repo_path=".",
                content=arguments.get("content", ""),
                source_file=arguments.get("source_file", ""),
                doc_path=arguments.get("doc_path", ""),
                template=arguments.get("template", "lean_baseline_service_template.md"),
                component_type=arguments.get("component_type", "unknown"),
                overwrite=arguments.get("overwrite", False),
                config=cfg,  # PASS LOADED CONFIG (local reference)
                telemetry_logger=enforcement_logger  # Pass logger to function
            )
            
            # Log result
            if enforcement_logger:
                enforcement_logger.log_result(name, result)
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            logger.error(f"write_documentation error: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": str(e)
            }))]
    
    elif name == "update_documentation_sections":
        # ENFORCEMENT GATE 🔴
        try:
            # Log start of update operation
            if enforcement_logger:
                enforcement_logger.log_start(name, arguments)
            
            result = update_documentation_sections_and_commit(
                repo_path=".",
                doc_path=arguments.get("doc_path", ""),
                section_updates=arguments.get("section_updates", {}),
                template=arguments.get("template", "lean_baseline_service_template.md"),
                source_file=arguments.get("source_file", ""),
                component_type=arguments.get("component_type", "unknown"),
                config=cfg,  # PASS LOADED CONFIG (local reference)
                telemetry_logger=enforcement_logger  # Pass logger to function
            )
            
            # Log result
            if enforcement_logger:
                enforcement_logger.log_result(name, result)
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            logger.error(f"update_documentation_sections error: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": str(e)
            }))]
    
    else:
        raise ValueError(f"Unknown tool: {name}")
```

**Acceptance:** Tools call real functions; no more placeholders.

#### Task 2.2: Add Tool Schemas to `list_tools()`

**File:** `src/server.py` - in `list_tools()` return list

Add these schemas so Copilot discovers the tools:

```python
Tool(
    name="write_documentation",
    description="Write documentation with enforcement. Content validated against template before write. Staged and committed.",
    inputSchema={
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "Markdown content (REQUIRED)"},
            "source_file": {"type": "string", "description": "Repo-relative source code file path, e.g. src/handler.cs (REQUIRED)"},
            "doc_path": {"type": "string", "description": "Repo-relative output doc path, e.g. docs/api.md (REQUIRED)"},
            "template": {"type": "string", "default": "lean_baseline_service_template.md"},
            "component_type": {"type": "string", "default": "unknown"},
            "overwrite": {"type": "boolean", "default": False}
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
            "doc_path": {"type": "string", "description": "Repo-relative doc file to update, e.g. docs/api.md (REQUIRED)"},
            "section_updates": {"type": "object", "description": "Map of section_name -> new_content (REQUIRED)"},
            "template": {"type": "string", "default": "lean_baseline_service_template.md"},
            "source_file": {"type": "string", "description": "Repo-relative source code file path"},
            "component_type": {"type": "string", "default": "unknown"}
        },
        "required": ["doc_path", "section_updates"]
    }
)
```

**Acceptance:** Schemas are valid JSON Schema; match function parameters.

---

### BATCH 3: Fix Write Operations & Enforcement Gates (6-8 hours)

**Objective:** Insert enforcement gates; fix YAML/header conflict; eliminate bypass

#### Task 3.0: Fix YAML Front Matter / AI Header Conflict (1 hour) ⚠️ DO FIRST

**File:** `src/write_operations.py`

Your `add_ai_header()` currently prepends HTML comment BEFORE YAML. This violates "YAML must be first" when enforcement tool generates YAML.

**Add this helper function:**

```python
def _insert_ai_header_after_yaml(header: str, content: str) -> str:
    """
    Insert AI header AFTER YAML front matter (if present).
    Ensures YAML stays at top of file.
    """
    lines = content.splitlines(keepends=True)
    if not lines or not lines[0].strip().startswith("---"):
        # No YAML, prepend header
        return header + "\n\n" + content
    
    # Find closing YAML delimiter
    yaml_end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            yaml_end_idx = i
            break
    
    if yaml_end_idx is None:
        # Malformed YAML, prepend anyway
        return header + "\n\n" + content
    
    # Insert AFTER closing ---
    before = "".join(lines[:yaml_end_idx + 1])
    after = "".join(lines[yaml_end_idx + 1:])
    return before + "\n" + header + "\n" + after
```

**Add new `build_ai_header()` function that returns ONLY the header (not full content):**

```python
def build_ai_header(source_file: str, component_type: str = "unknown", template: str = "") -> str:
    """Return header text only (insertion deferred to write path)."""
    return f"""<!-- 🤖 Auto-generated by AKR MCP Server
  Source: {source_file}
  Component: {component_type}
  Template: {template}
  Enhance with ❓ [HUMAN: ...] before merging
-->"""
```

**Acceptance:** YAML preserved as first content; header inserted after closing `---`.

#### Task 3.1: Insert Enforcement Gate into `write_documentation()` (3 hours)

**File:** `src/write_operations.py`

Replace existing `write_documentation()` function:

```python
def write_documentation(
    repo_path: str,
    content: str,
    source_file: str,
    doc_path: str,
    template: str = "lean_baseline_service_template.md",
    component_type: str = "unknown",
    overwrite: bool = False,
    config: dict = None,  # ADDED: Actual server config (not reconstructed)
    telemetry_logger=None  # Add telemetry parameter
) -> dict:
    """
    Write documentation with ENFORCEMENT HARD GATE.
    
    Content MUST pass enforcement validation before any file write.
    No bypass paths.
    """
    
    from tools.enforcement_tool import enforce_and_fix
    from tools.enforcement_tool_types import FileMetadata
    
    # CRITICAL: Check if enforcement is enabled (hard gate)
    if config and not config.get("documentation", {}).get("enforcement", {}).get("enabled", True):
        return {
            "success": False,
            "error": "Documentation enforcement is disabled in config; writes refused for safety",
            "filePath": doc_path
        }
    
    writer = DocumentationWriter(repo_path)
    
    # SECURITY: Prevent path traversal attacks
    # Prefer Path.is_relative_to() (Python 3.9+) for robustness; fallback for compatibility
    # Note: This project targets Python 3.9+, but fallback retained for broader compatibility
    full_path = (Path(repo_path) / doc_path).resolve()
    repo_resolved = Path(repo_path).resolve()
    try:
        # Python 3.9+: use safe is_relative_to() method
        is_safe = full_path.is_relative_to(repo_resolved)
    except (AttributeError, ValueError):
        # Fallback for Python <3.9: check prefix with os.sep (platform-independent)
        import os
        repo_str = str(repo_resolved)
        full_str = str(full_path)
        is_safe = full_str == repo_str or full_str.startswith(repo_str + os.sep)
    
    if not is_safe:
        return {
            "success": False,
            "error": f"Path traversal blocked: {doc_path} is outside repo",
            "filePath": doc_path
        }
    
    # Check if file exists
    existing = writer.read_file(doc_path)
    if existing and not overwrite:
        return {
            "success": False,
            "error": f"File exists: {doc_path}. Set overwrite=True to replace.",
            "filePath": doc_path
        }
    
    # ========== ENFORCEMENT GATE 🔴 ==========
    try:
        metadata = FileMetadata(
            file_path=source_file,
            component_name=Path(source_file).stem,
            domain="Unknown",
            module_name=Path(source_file).stem,
            feature_tag="",
            complexity="Medium"
        )
        
        enforced = enforce_and_fix(
            generated_markdown=content,
            template_name=template,
            file_metadata=metadata,
            config=config,
            update_mode="replace" if overwrite else "create",
            overwrite=overwrite,
            dry_run=False
        )
        
        # CRITICAL: If not valid, STOP - do not write
        if not enforced.valid:
            return {
                "success": False,
                "error": "Template enforcement failed",
                "violations": [
                    {"type": v.type, "severity": v.severity.name, "message": v.message}
                    for v in enforced.violations
                ],
                "filePath": doc_path,
                "summary": enforced.summary
            }
        
        # Enforcement passed - safe to write
        enforced_content = enforced.content
        
    except Exception as e:
        logger.error(f"Enforcement error: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Enforcement error: {e}",
            "filePath": doc_path
        }
    # ========== END GATE ==========
    
    # Insert AI header AFTER YAML (safe)
    try:
        header = build_ai_header(source_file, component_type, template)
        final_content = _insert_ai_header_after_yaml(header, enforced_content)
    except Exception as e:
        logger.warning(f"Could not insert header: {e}")
        final_content = enforced_content
    
    # Write via DocumentationWriter (stages + commits)
    if not writer.write_file(doc_path, final_content):
        return {"success": False, "error": "Failed to write file", "filePath": doc_path}
    
    writer.stage_file(doc_path)
    
    msg = f"docs: add {Path(source_file).stem} documentation"
    if not writer.commit(msg, [doc_path]):
        return {"success": False, "error": "Failed to commit", "filePath": doc_path}
    
    return {
        "success": True,
        "filePath": doc_path,
        "branch": writer.get_current_branch(),
        "summary": f"Documentation written and committed. {enforced.summary}"
    }
```

**Acceptance:** Enforcement runs before write; invalid content returns error without writing; YAML/header correct.

#### Task 3.2: Eliminate `Path.write_text()` Bypass (3 hours)

**File:** `src/section_updater.py` (refactor) + `src/write_operations.py` (new function)

**In `section_updater.py`, change `update_documentation_sections()` to be TRUE PURE LOGIC (no I/O):**

**NOTE:** Accept content as parameter, don't read from filesystem. This makes it truly testable.

```python
def update_documentation_sections(
    existing_content: str,  # CHANGED: Accept content, not file path
    section_updates: dict[str, str],
    add_changelog: bool = True
) -> dict:
    """
    Compute updated documentation (pure logic, NO I/O).
    Returns updated_content for caller to write.
    Caller is responsible for reading file before calling this.
    """
    
    updater = SurgicalUpdater(existing_content)
    results = []
    
    for section_id, new_content in section_updates.items():
        r = updater.update_section(section_id, new_content)  # Returns UpdateResult dataclass
        results.append({
            "section_id": r.section_id,
            "action": r.action,
            "success": r.success,
            "message": r.message  # Use attribute access, not .get()
        })
    
    updated_content = updater.generate_updated_content(add_changelog)
    
    return {
        "success": True,
        "updates": results,
        "updated_content": updated_content,  # Caller writes this
        "message": "Computed (no write performed)"
    }
```

**In `write_operations.py`, add NEW function that handles write+commit:**

```python
def update_documentation_sections_and_commit(
    repo_path: str,
    doc_path: str,
    section_updates: dict[str, str],
    template: str = "lean_baseline_service_template.md",
    source_file: str = "",
    component_type: str = "unknown",
    add_changelog: bool = True,
    overwrite: bool = True,
    config: dict = None,  # ADDED: Actual server config
    telemetry_logger=None  # Add telemetry parameter
) -> dict:
    """
    Update doc sections WITH enforcement gate and git commit.
    
    HARD GATE: Updated content must pass enforcement before write.
    
    Flow: Read → Compute → ENFORCE → Write → Commit
    """
    
    from tools.enforcement_tool import enforce_and_fix
    from tools.enforcement_tool_types import FileMetadata
    from tools.section_updater import update_documentation_sections as compute_updates
    
    # CRITICAL: Check if enforcement is enabled (hard gate)
    if config and not config.get("documentation", {}).get("enforcement", {}).get("enabled", True):
        return {
            "success": False,
            "error": "Documentation enforcement is disabled in config; writes refused for safety",
            "filePath": doc_path
        }
    
    writer = DocumentationWriter(repo_path)
    
    # SECURITY: Prevent path traversal attacks
    full_path = (Path(repo_path) / doc_path).resolve()
    repo_resolved = Path(repo_path).resolve()
    
    # Use Path.is_relative_to() if available (Python 3.9+); otherwise fallback to prefix check
    try:
        is_safe = full_path.is_relative_to(repo_resolved)
    except (AttributeError, ValueError):
        # Fallback for Python <3.9: check prefix with os.sep (platform-independent)
        import os
        repo_str = str(repo_resolved)
        full_str = str(full_path)
        is_safe = full_str == repo_str or full_str.startswith(repo_str + os.sep)
    
    if not is_safe:
        return {
            "success": False,
            "error": f"Path traversal blocked: {doc_path} is outside repo",
            "filePath": doc_path
        }
    
    # Step 1: Read existing
    existing = writer.read_file(doc_path)
    if not existing:
        return {"success": False, "error": f"File not found: {doc_path}", "filePath": doc_path}
    
    # Step 2: Compute changes (pure logic, passing content not path)
    try:
        result = compute_updates(
            existing_content=existing,  # CHANGED: Pass content, not file path
            section_updates=section_updates,
            add_changelog=add_changelog
        )
        updated_content = result["updated_content"]
        update_results = result["updates"]
    except Exception as e:
        logger.error(f"Compute error: {e}", exc_info=True)
        return {"success": False, "error": str(e), "filePath": doc_path}
    
    # Step 3: ENFORCEMENT GATE 🔴
    try:
        metadata = FileMetadata(
            file_path=source_file or doc_path,
            component_name=Path(doc_path).stem,
            domain="Unknown",
            module_name=Path(doc_path).stem,
            feature_tag="",
            complexity="Medium"
        )
        
        enforced = enforce_and_fix(
            generated_markdown=updated_content,
            template_name=template,
            file_metadata=metadata,
            config=config,
            update_mode="replace",
            overwrite=True,
            dry_run=False
        )
        
        if not enforced.valid:
            return {
                "success": False,
                "error": "Updated content failed enforcement",
                "violations": [{"type": v.type, "severity": v.severity.name} for v in enforced.violations],
                "updates": update_results,
                "filePath": doc_path
            }
        
        enforced_content = enforced.content
        
    except Exception as e:
        logger.error(f"Enforcement error: {e}", exc_info=True)
        return {"success": False, "error": str(e), "filePath": doc_path}
    # ========== END GATE ==========
    
    # Step 4: Write + commit via DocumentationWriter
    try:
        header = build_ai_header(source_file, component_type, template)
        final_content = _insert_ai_header_after_yaml(header, enforced_content)
        
        if not writer.write_file(doc_path, final_content):
            return {"success": False, "error": "Failed to write", "filePath": doc_path}
        
        writer.stage_file(doc_path)
        msg = f"docs: update {Path(doc_path).stem} sections"
        if not writer.commit(msg, [doc_path]):
            return {"success": False, "error": "Failed to commit", "filePath": doc_path}
        
        return {
            "success": True,
            "filePath": doc_path,
            "branch": writer.get_current_branch(),
            "updates": update_results,
            "summary": "Sections updated, enforced, and committed"
        }
        
    except Exception as e:
        logger.error(f"Write error: {e}", exc_info=True)
        return {"success": False, "error": str(e), "filePath": doc_path}
```

**Acceptance:** No direct `Path.write_text()` outside of `DocumentationWriter`; enforcement gate required before any write; updates are committed.

---

### BATCH 4: Testing & Documentation (6-8 hours)

**Objective:** Verify enforcement works end-to-end; ensure no regressions

#### Task 4.1: Create E2E Tests

**File:** `tests/test_enforcement_e2e.py` (new)

Test both pathways. **Note:** Tests validate enforcement indirectly through the write path; we don't call `enforce_and_fix()` directly since enforcement is integrated into write operations.

```python
import pytest
from pathlib import Path
import subprocess
from tools.write_operations import write_documentation

@pytest.fixture
def git_repo(tmp_path):
    """Initialize a git repo in tmp_path."""
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True)
    # Create initial commit so "branch" exists
    (tmp_path / "README.md").write_text("# Test Repo")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True)
    return tmp_path

def test_write_documentation_enforces_before_write(git_repo):
    """Test that write_documentation refuses invalid content (no enforcement pass)."""
    
    invalid_markdown = "# Service\n\nNo required sections!"
    
    result = write_documentation(
        repo_path=str(git_repo),
        content=invalid_markdown,
        source_file="test.cs",
        doc_path="docs/test.md",  # Repo-relative path
        template="lean_baseline_service_template.md",
        overwrite=True
    )
    
    # Should fail due to enforcement
    assert result["success"] is False
    assert "enforcement" in result.get("error", "").lower() or "violations" in result
    
    # File should NOT be created
    assert not (git_repo / "docs" / "test.md").exists()

def test_write_documentation_with_valid_content(git_repo):
    """Test that write_documentation accepts valid enforced content."""
    
    valid_markdown = """---
component: TestService
feature: TEST001
domain: Testing
---

# Service: TestService

## Quick Reference
Testing service.

## What & Why
Testing.

## How It Works
Testing.

## Business Rules
| Rule | Desc |
|------|------|
| R1 | Test |

## Architecture
Testing.

## Data Operations
Testing.

## Questions & Gaps
Testing."""
    
    result = write_documentation(
        repo_path=str(git_repo),
        content=valid_markdown,
        source_file="test.cs",
        doc_path="docs/test.md",  # repo-relative
        overwrite=True
    )
    
    # Should succeed
    assert result["success"] is True
    assert (git_repo / "docs" / "test.md").exists()
    
    # File content should have header AFTER YAML
    written = (git_repo / "docs" / "test.md").read_text()
    assert written.startswith("---")
    yaml_end = written.find("---\n", 5)
    assert yaml_end > 0
    # Header should appear AFTER YAML
    header_pos = written.find("<!--")
    assert header_pos > yaml_end
```

**Acceptance:** Git repo initialized; enforcement gate tested; write refuses invalid; YAML/header correct; tests pass.

#### Task 4.2: Add Bypass Scan Task

**File:** Add to test suite or pre-commit hook

```bash
#!/bin/bash
# Scan for dangerous write patterns outside write_operations.py

echo "🔍 Scanning for doc write bypasses..."

# Find .write_text() calls outside write_operations.py
if grep -r --include="*.py" "\.write_text(" src/ tests/ | grep -v "write_operations.py"; then
  echo "❌ FAIL: Found .write_text() outside write_operations.py"
  exit 1
fi

# Find open(..., 'w') or open(..., "w") outside write_operations.py
if grep -r --include="*.py" "open([^)]*['\"]w['\"]" src/ tests/ | grep -v "write_operations.py"; then
  echo "❌ FAIL: Found open(..., 'w') outside write_operations.py"
  exit 1
fi

echo "✅ PASS: No direct write bypasses detected."
```

**Acceptance:** Scan completes; finds no undocumented write paths for `.md` files.

#### Task 4.3: Run Full Test Suite

```bash
pytest tests/ -v --cov=src
```

**Acceptance:** All existing tests pass; new E2E tests pass; no regressions; coverage remains >80%.

#### Task 4.4: Create Developer Guide

**File:** `docs/DEVELOPER_GUIDE_ENFORCEMENT.md`

Include sections:
- How enforcement works (diagram)
- API usage examples
- Configuration options
- Troubleshooting (bypass detection)

---

## ✅ Final Checklist

### Before Integration Starts
- [ ] All code reviewed for bypass paths
- [ ] Import structure confirmed
- [ ] Test data prepared

### Batch 1 Complete
- [x] Imports added
- [x] Telemetry initialized
- [x] Config schema updated

### Batch 2 Complete
- [x] Dispatcher wired to real functions
- [x] Tool schemas registered
- [ ] All tests compile

### Batch 3 Complete (Critical)
- [x] YAML/header fix applied
- [x] `write_documentation()` enforces
- [x] `update_documentation_sections()` is pure logic
- [x] `update_documentation_sections_and_commit()` works
- [ ] No `Path.write_text()` outside `DocumentationWriter`

### Batch 4 Complete
- [ ] E2E tests pass
- [ ] All existing tests pass
- [x] Dev guide written
- [ ] Bypass scan completes with zero violations

### Production Ready
- [ ] All enforcement gates confirmed
- [ ] No bypass paths remain
- [ ] Git workflow preserved
- [ ] Telemetry logging works

---

## 🔴 Critical Success Criteria

**Enforcement is unavoidable if and only if:**

1. ✅ `write_documentation()` calls enforcement; refuses to write if `valid=false`
2. ✅ `update_documentation_sections_and_commit()` calls enforcement; refuses to write if `valid=false`
3. ✅ No other code path writes docs (grep: no `Path.write_text()` for `.md` files)
4. ✅ AI header inserted AFTER YAML, not before
5. ✅ All writes stage and commit via `DocumentationWriter`
6. ✅ **If enforcement is `enabled=false` in config, write tools REFUSE to write** (no bypass fallback)
   - Return error: `"error": "Documentation enforcement is disabled in config; writes refused for safety"`
   - This prevents silent legacy behavior circumventing the hard gate

**If any of these fail, enforcement is NOT the hard gate.**

---

## 📋 Enforcement Tool Contract (What `enforce_and_fix()` Returns)

**The enforcement tool MUST return this exact contract for the integration to work:**

```python
@dataclass
class EnforcementResult:
    """Result of template validation and auto-fix."""
    valid: bool                           # True if content passes all validations
    content: str                          # The fixed markdown (may differ from input)
    violations: list[Violation]           # Non-fixable issues found
    summary: str                          # Human-readable summary of what changed
    auto_fixed: list[str]                 # List of auto-fixed issues
```

The plan assumes:
- `result.valid` is True if safe to write
- `result.content` is the validated/fixed markdown
- `result.violations` is a list of `Violation` objects with `.type`, `.severity`, `.message`
- `result.summary` describes what enforcement changed

**If your enforcement tool returns a different structure, update the dispatcher code in Batch 2.**

---

## 🗺️ Path Clarifications

### Repo-Relative vs Absolute Paths

**In this plan:**
- **`doc_path` is repo-relative:** `"docs/service.md"` not `"/absolute/path/docs/service.md"`
- **`source_file` is repo-relative:** `"src/handlers.cs"` not absolute
- **`repo_path` is absolute:** `"."` or `"/full/path/to/repo"`

The dispatcher resolves `doc_path` as `Path(repo_path) / doc_path`.

**Example:**
```python
write_documentation(
    repo_path="/home/user/myrepo",  # Absolute
    doc_path="docs/api.md",         # Relative to repo
    source_file="src/api.cs"        # Relative to repo
)
# Writes to: /home/user/myrepo/docs/api.md
```

### Import Path: `from tools...` not `from src.tools...`

**ALL imports use the pattern your server already uses:**

```python
from tools.enforcement_tool import enforce_and_fix      # ✅ NOT from src.tools (canonical module path)
from tools.write_operations import write_documentation    # ✅ NOT from src.tools
from resources import AKRResourceManager                  # ✅ Matches server.py
```

This avoids `ModuleNotFoundError` when the server runs as an MCP subprocess.

---

## ⚠️ Important Implementation Notes

### AI Header Refactoring (Option A: Backward Compatible)

**Current State:** `DocumentationWriter.add_ai_header()` is a method that modifies content.

**Refactoring Strategy (Task 3.0) - CHOSEN: Option A (Recommended)**

**Why Option A:** Preserves backward compatibility; prevents breaking existing callers.

**Implementation steps:**
1. Create NEW standalone function `build_ai_header(source_file, component_type, template) -> str`
   - Returns header text only (no content modification)
   - Located in `write_operations.py`

2. Create `_insert_ai_header_after_yaml(header: str, content: str) -> str` helper
   - Inserts header AFTER YAML closing delimiter
   - Located in `write_operations.py`

3. **Do NOT modify** `DocumentationWriter.add_ai_header()` method
   - It may have existing callers outside write_operations.py
   - Leaves compatibility door open for future refactor

4. In dispatcher + write functions:
   - Use: `header = build_ai_header(...)`
   - Then: `final_content = _insert_ai_header_after_yaml(header, enforced_content)`

**Result:** YAML-first requirement met; existing code unbroken; clear separation of concerns.

### Config Parameter Wiring

**Critical:** Pass the actual loaded server config through the dispatcher:

```python
# In call_tool() (Task 2.1):
global config
cfg = config  # Use global config already loaded by ensure_initialized()
result = write_documentation(..., config=cfg, ...)
```

**Why:** Your `ensure_initialized()` must call `config = load_config()` and set it globally. This config is then passed through to enforcement, which uses settings like `validationStrictness`, `maxRetries`, etc. Do NOT reconstruct a minimal config in the dispatcher.

### Telemetry Initialization Timing & Usage

**Initialization:**
```python
# In server initialization or main():
ensure_initialized()  # This now calls init_enforcement_telemetry()
```
This ensures telemetry is ready before the first tool call.

**Telemetry Event Contract (minimal schema):**

Log these 3 event types to `logs/enforcement.jsonl`:

1. **`enforcement_start`** (logged at enforcement invocation start):
   - `event_type`: "enforcement_start"
   - `tool`: name of write/update function
   - `template`: template_name being used
   - `doc_path`: path being written
   - `timestamp`: ISO 8601 datetime

2. **`enforcement_result`** (logged after enforcement completes):
   - `event_type`: "enforcement_result"
   - `tool`: name of write/update function
   - `valid`: boolean (True if passed)
   - `violations_count`: number of violations found
   - `auto_fixed_count`: number of issues auto-fixed
   - `duration_ms`: milliseconds to validate+fix
   - `timestamp`: ISO 8601 datetime

3. **`enforcement_error`** (logged if enforcement fails with exception):
   - `event_type`: "enforcement_error"
   - `tool`: name of write/update function
   - `error_type`: exception class name
   - `message`: error message
   - `timestamp`: ISO 8601 datetime

**Usage Inside write/update functions:**
Inside `write_documentation()` and `update_documentation_sections_and_commit()`:
- Log `enforcement_start` before calling `enforce_and_fix()`
- Log `enforcement_result` after enforcement completes (whether valid or not)
- Log `enforcement_error` in exception handler
- This helps trace which docs were enforced and what issues were found
- Pattern: `if telemetry_logger: telemetry_logger.log_event(event_dict)`

### Path Semantics Summary

- **`repo_path`** (absolute): Passed by dispatcher, typically `"."`
- **`doc_path`** (repo-relative): `"docs/api.md"` NOT `"/full/path/to/docs/api.md"`
- **`source_file`** (repo-relative): `"src/api.cs"` NOT absolute
- **Resolution:** Internally: `full_path = Path(repo_path) / doc_path`

### Overwrite / Update Mode Mapping

**Explicit mapping (already in plan, restated for clarity):**
- `overwrite=False` → `update_mode="create"` (fail if file exists)
- `overwrite=True` → `update_mode="replace"` (overwrite if exists)

---

## 📖 Supporting Batch 2 Extensions (Optional)

If you want Copilot to have full visibility into the update workflow, **optionally add these tools to `list_tools()` and dispatcher in Batch 2:**

```python
Tool(
    name="get_document_structure",
    description="Analyze existing doc structure: sections, hierarchy, YAML metadata.",
    inputSchema={
        "type": "object",
        "properties": {
            "doc_path": {"type": "string", "description": "Repo-relative path"}
        },
        "required": ["doc_path"]
    }
),
Tool(
    name="analyze_documentation_impact",
    description="Analyze impact of proposed changes: cross-references, dependencies.",
    inputSchema={
        "type": "object",
        "properties": {
            "doc_path": {"type": "string"},
            "changes": {"type": "object"}
        },
        "required": ["doc_path", "changes"]
    }
)
```

These already exist in `section_updater.py` and enable more coherent Copilot workflows (understand structure before proposing changes). **Mark as optional** because they're not strictly required for enforcement to work.

---

## � M365 Copilot Round 4 Feedback: Clarifications Applied

This section summarizes fixes applied to address Round 4 assessment (9 items).

### Blocking Issues Fixed

**1. Enforcement module import path unified:**
- Canonical import: `from tools.enforcement_tool import enforce_and_fix`
- Used consistently in Batch 1, Batch 2, Batch 3, tests, and Path Clarifications
- No aliases or alternate paths

**2. Dispatcher config scope corrected:**
- Changed from: `config = load_config() if config is None else config` (causes UnboundLocalError)
- Changed to: `global config; cfg = config` (local reference to global)
- Tool calls use `cfg` instead of reassigning `config`
- Prevents runtime errors in Python scope

### High-Value Improvements

**3. AI header strategy clarified (Option A chosen):**
- New standalone `build_ai_header()` returns header text only
- New `_insert_ai_header_after_yaml()` inserts after YAML closing delimiter
- **Do NOT modify** existing `DocumentationWriter.add_ai_header()` method (backward compatibility)
- Dispatcher uses new functions

**4. Path traversal guard added:**
- Both `write_documentation()` and `update_documentation_sections_and_commit()` validate `doc_path`
- Guard: resolve full path and ensure it's within `repo_path`
- Returns error if path tries to escape repo boundaries
- Prevents: `doc_path="../secret.md"` or `doc_path="/absolute/path"`

**5. Tool schemas clarified with repo-relative paths:**
- `doc_path` description now: "Repo-relative output doc path, e.g. docs/api.md"
- `source_file` description now: "Repo-relative source code file path, e.g. src/handler.cs"
- Eliminates client-side ambiguity about path format

**6. Bypass scan script simplified:**
- Removed fragile multi-pattern grep logic
- Now deterministically checks:
  - `.write_text()` outside write_operations.py → FAIL
  - `open(..., 'w')` outside write_operations.py → FAIL
- No false negatives/positives from "markdown" string detection

**7. Config key naming standardized:**
- JSON config uses camelCase: `writeMode`, `requireYamlFrontmatter`, `enforceSectionOrder`
- Consistent throughout plan

### Clarifications Addressed

**8. Telemetry logger usage documented:**
- Initialization: call `init_enforcement_telemetry()` in `ensure_initialized()`
- Usage in write/update functions: log enforcement start/result with template name + doc_path + violation count
- Pattern: `if telemetry_logger: telemetry_logger.log_enforcement(...)`

**9. Enforcement enabled flag behavior:**
- If `documentation.enforcement.enabled=false` in config: write tools REFUSE to write
- Error message: "Documentation enforcement is disabled in config; writes refused for safety"
- Prevents silent bypass fallback; maintains hard-gate guarantee

---

## �📚 Supporting Materials

- [CRITICAL_IMPROVEMENTS_M365_COPILOT_FEEDBACK.md](CRITICAL_IMPROVEMENTS_M365_COPILOT_FEEDBACK.md) — Details of feedback items
- [M365_FEEDBACK_MAPPING.md](M365_FEEDBACK_MAPPING.md) — Maps each feedback to specific tasks
- [QUICK_REFERENCE_CHANGES.md](QUICK_REFERENCE_CHANGES.md) — Task-by-task summary
- [Phase 1 Implementation Plan](IMPLEMENTATION_PLAN_TEMPLATE_ENFORCEMENT_TOOL.md) — Component build plan (completed)

---
