# Integration Plan: Template Enforcement Tool into AKR MCP Server

**Document Version:** 1.0  
**Date:** February 3, 2026  
**Status:** Ready for Copilot Agent Execution  
**Owner:** AKR MCP Server Team  
**Based On:** IMPLEMENTATION_PLAN_TEMPLATE_ENFORCEMENT_TOOL.md v5.3

---

## 📋 Executive Summary

This document outlines the **integration of the completed Template Enforcement Tool components** into the AKR MCP server's documentation generation workflow. All component work (validation engine, schema builder, document parser, YAML generator, file writer) is complete; this plan focuses on **wiring them together in `server.py`** and testing end-to-end.

**Expected Timeline:** 2-3 days (4 focused batches)  
**Deliverable:** Documentation generation with automatic format validation and enforcement

---

## 🔴 Critical Assessment Applied (M365 Copilot Feedback)

This plan has been updated to address 6 critical integration risks identified in peer review:

1. ✅ **Enforcement as hard gate**: Tool is the ONLY writer; no bypass paths
2. ✅ **Minimal prompt strategy**: Removed full template text from prompt; use contract only
3. ✅ **Tool dispatcher fix**: Integrate into existing dispatcher, not second `@server.call_tool()`
4. ✅ **Config alignment**: Schema matches enforcement tool's actual contract
5. ✅ **Update mode support**: Explicit handling of update/merge intent
6. ✅ **Output validation tests**: E2E tests verify actual written file structure

**See Section 🔧 Critical Improvements (below) for detailed changes**

---

## 🎯 Current State Assessment

### ✅ What's Complete (From Phase 1 MVP)

| Component | File | Status | Batch Created |
|-----------|------|--------|-----------------|
| Data Structures | `src/tools/enforcement_tool_types.py` | ✅ Complete | Batch 1 |
| Template Schema Builder | `src/tools/template_schema_builder.py` | ✅ Complete | Batch 1 |
| Document Parser | `src/tools/document_parser.py` | ✅ Complete | Batch 2 |
| YAML Front Matter Generator | `src/tools/yaml_frontmatter_generator.py` | ✅ Complete | Batch 2 |
| Validation Engine | `src/tools/validation_engine.py` | ✅ Complete | Batch 3 |
| File Writer | `src/tools/file_writer.py` | ✅ Complete | Batch 4 |
| Enforcement Tool (Orchestrator) | `src/tools/enforcement_tool.py` | ✅ Complete | Batch 4 |

### ❌ What's Missing (This Plan)

| Item | File | Current State | Required |
|------|------|---------------|----------|
| Server integration | `src/server.py` | No enforcement calls | Wire enforcement tool calls |
| MCP tool registration | `src/server.py` | Documentation tool exists | Add validate_and_write_documentation tool |
| Config schema updates | `config.json` | Basic schema | Support pathMappings & validation config |
| End-to-end testing | `tests/` | Component tests exist | E2E tests with real templates |
| Documentation | `docs/` | User guide exists | Developer integration guide |

---

## 🚀 Implementation Batches

### BATCH 1: Server Integration Preparation (4-6 hours)

**Objective:** Import enforcement tool components and add telemetry setup

**Priority:** 🔴 CRITICAL (blocks all downstream work)

---

#### Task 1.1: Add Imports to `server.py` (FIXED: Consistent absolute imports)

**File:** `src/server.py`

**What to do:**
Add import statements for all enforcement tool components at the top of the file (after existing imports). **CRITICAL**: Use consistent absolute imports (`from src.tools...`) to match project structure.

**Specific Changes:**
```python
# Add these imports after existing imports section (around line 10-20)

# Enforcement Tool Components (absolute imports for safety)
from src.tools.enforcement_tool import (
    validate_and_write,
    validate_and_write_async
)
from src.tools.document_parser import DocumentParser
from src.tools.validation_engine import ValidationEngine
from src.tools.yaml_frontmatter_generator import YAMLFrontmatterGenerator
from src.tools.file_writer import FileWriter
from src.tools.enforcement_tool_types import (
    ValidationResult,
    ViolationSeverity,
    FileMetadata,
    WriteResult
)
from src.tools.enforcement_logger import EnforcementLogger
```

**Verification:**
```bash
# Test imports resolve correctly
python -c "from src.tools.enforcement_tool import validate_and_write_async"
python -c "from src.tools.enforcement_tool_types import FileMetadata"
```

**Acceptance Criteria:**
- ✅ All imports resolve without errors
- ✅ No circular imports (test with `python -c "from src.server import *"`)
- ✅ IDE shows no unresolved references

**Status:** ⬜ Not Started

---

#### Task 1.2: Add Telemetry Logger Setup

**File:** `src/server.py`

**What to do:**
Initialize telemetry logger for enforcement tool operations (structured JSON Lines logging).

**Specific Changes:**
```python
# Add after logger initialization (around line 30-40)

# Initialize enforcement tool telemetry logger
enforcement_logger = None

def init_enforcement_telemetry(log_path: str = "logs/enforcement.jsonl"):
    """Initialize enforcement tool telemetry logging."""
    global enforcement_logger
    try:
        from tools.enforcement_logger import EnforcementLogger
        enforcement_logger = EnforcementLogger(log_path)
        logger.info(f"Enforcement telemetry initialized: {log_path}")
    except Exception as e:
        logger.warning(f"Could not initialize enforcement telemetry: {e}")
        enforcement_logger = None
```

**Acceptance Criteria:**
- ✅ Logger initializes without errors
- ✅ `logs/enforcement.jsonl` is created when tool runs
- ✅ No side effects if telemetry disabled

**Status:** ⬜ Not Started

---

#### Task 1.3: Load Configuration Schema Updates

**File:** `src/server.py`

**What to do:**
Add configuration loading for enforcement tool settings (pathMappings, validation strictness, merge policy).

**Specific Changes:**
```python
# Add after config loading (around line 50-70)

def load_enforcement_config(config: dict) -> ValidationConfig:
    """Extract enforcement tool configuration from server config."""
    doc_config = config.get("documentation", {})
    
    validation_config = ValidationConfig(
        output_path=doc_config.get("output_path", "docs/"),
        path_mappings=doc_config.get("pathMappings", {}),
        allow_local_templates=doc_config.get("allowLocalTemplates", False),
        validation_strictness=doc_config.get("validationStrictness", "baseline"),
        require_yaml_frontmatter=doc_config.get("requireYamlFrontmatter", True),
        enforce_section_order=doc_config.get("enforceSectionOrder", True),
        auto_fix_enabled=doc_config.get("autoFixEnabled", True),
        merge_policy=doc_config.get("mergePolicy", "append"),
        section_ownership=doc_config.get("sectionOwnership", {}),
        rewrite_threshold=doc_config.get("rewriteThreshold", 0.8)
    )
    
    return validation_config
```

**Acceptance Criteria:**
- ✅ Config loads without errors
- ✅ Defaults applied when keys missing
- ✅ No validation errors on well-formed config

**Status:** ⬜ Not Started

---

### BATCH 2: MCP Tool Registration (3-4 hours)

**Objective:** Add `validate_and_write_documentation` tool to MCP server

**Priority:** 🔴 CRITICAL (enables tool invocation)

---

#### Task 2.1: Register New MCP Tool (FIXED: Integrate into existing dispatcher)

**File:** `src/server.py`

**What to do:**
**DO NOT create a new `@server.call_tool()` function.** Find the EXISTING tool dispatcher and add a case branch for the new tool. This is critical to avoid shadowing/breaking existing tools.

**Specific Changes:**
```python
# STEP 1: Locate the existing @server.call_tool() dispatcher
# It should look something like this (around line 150-250):

@server.call_tool()  # ← This decorator already exists!
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Dispatch to appropriate tool implementation."""
    
    # STEP 2: Find existing tool branches
    if name == "generate_documentation":
        return await handle_generate_documentation(arguments)
    
    elif name == "analyze_codebase":
        return await handle_analyze_codebase(arguments)
    
    # STEP 3: ADD this new branch (do NOT replace anything above)
    elif name == "validate_and_write_documentation":
        return await handle_validate_and_write(arguments)
    
    # Keep existing else clause
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_validate_and_write(arguments: dict) -> list[TextContent]:
    """Handle validate_and_write_documentation tool call."""
    
    # Extract arguments
    generated_markdown = arguments.get("generated_markdown", "")
    template_name = arguments.get("template_name", "lean_baseline_service_template.md")
    file_metadata = arguments.get("file_metadata", {})
    update_mode = arguments.get("update_mode", "create")  # NEW: explicit intent
    overwrite = arguments.get("overwrite", False)
    dry_run = arguments.get("dry_run", False)
    
    # Validate inputs
    if not generated_markdown:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": "generated_markdown is required",
                "valid": False
            }, indent=2)
        )]
    
    try:
        # Load server config and merge with any call-specific overrides
        server_config = load_server_config()  # Full server config
        effective_config = deep_merge(server_config, arguments.get("config", {}))  # Merge overrides
        enforcement_config = load_enforcement_config(effective_config)
        
        # Log telemetry event
        if enforcement_logger:
            enforcement_logger.log_validation_start(
                template_name=template_name,
                mode=file_metadata.get("documentation_mode", "per_file"),
                user=arguments.get("user", "unknown")
            )
        
        # Call enforcement tool (HARD GATE: This is the ONLY write path)
        result = await validate_and_write_async(
            generated_markdown=generated_markdown,
            template_name=template_name,
            file_metadata=FileMetadata(**file_metadata),
            config=enforcement_config,
            update_mode=update_mode,  # NEW: explicit create/replace intent
            overwrite=overwrite,
            dry_run=dry_run,
            telemetry_logger=enforcement_logger
        )
        
        # Log telemetry event
        if enforcement_logger and result.valid:
            enforcement_logger.log_validation_success(
                file_path=result.file_path,
                violations_count=len(result.violations),
                confidence=result.confidence
            )
        elif enforcement_logger:
            enforcement_logger.log_validation_failure(
                violations=result.violations,
                confidence=result.confidence
            )
        
        # Return result
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": result.valid,
                "valid": result.valid,
                "file_path": result.file_path,
                "violations": [v.dict() for v in result.violations],
                "confidence": result.confidence,
                "severity_summary": result.severity_summary,
                "summary": result.summary
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        
        if enforcement_logger:
            enforcement_logger.log_validation_error(
                error_type=type(e).__name__,
                error_message=str(e)
            )
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "valid": False,
                "error": str(e),
                "error_type": type(e).__name__
            }, indent=2)
        )]
```

**Acceptance Criteria:**
- ✅ Tool is callable via MCP interface
- ✅ Arguments parsed correctly
- ✅ Result returned as JSON
- ✅ Errors handled gracefully
- ✅ Telemetry logged for all paths

**Status:** ⬜ Not Started

---

#### Task 2.2: Update Tool Schema (FIXED: Add update_mode and mode parameters)

**File:** `src/server.py` or MCP resource definitions

**What to do:**
Define the JSON schema for the new tool's input/output for MCP clients. **CRITICAL**: Include `update_mode` and `mode` parameters that were missing.

**Specific Changes:**
```python
# Add tool schema near server initialization

VALIDATE_AND_WRITE_TOOL_SCHEMA = {
    "name": "validate_and_write_documentation",
    "description": "Validate generated documentation against template schema and write to filesystem. Auto-fixes structural issues (YAML, section order, heading levels) or retries LLM with stricter prompts. ENFORCES: All docs must pass validation before write.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "generated_markdown": {
                "type": "string",
                "description": "The markdown content generated by LLM (REQUIRED)"
            },
            "template_name": {
                "type": "string",
                "description": "Name of the template to validate against",
                "default": "lean_baseline_service_template.md"
            },
            "file_metadata": {
                "type": "object",
                "description": "File metadata for YAML generation (REQUIRED)",
                "properties": {
                    "file_path": {"type": "string"},
                    "component_name": {"type": "string"},
                    "feature_tag": {"type": "string"},
                    "domain": {"type": "string"},
                    "module_name": {"type": "string"},
                    "documentation_mode": {"type": "string", "enum": ["per_file", "per_module"], "default": "per_file"}
                },
                "required": ["component_name"]
            },
            "update_mode": {
                "type": "string",
                "description": "How to handle existing files: 'create' (error if exists), 'replace' (overwrite), 'merge_sections' (Phase 2+)",
                "enum": ["create", "replace"],
                "default": "create"
            },
            "config": {
                "type": "object",
                "description": "Optional configuration overrides (merged with server config)"
            },
            "overwrite": {
                "type": "boolean",
                "description": "Explicit permission to overwrite (required if update_mode=replace and file exists)",
                "default": false
            },
            "dry_run": {
                "type": "boolean",
                "description": "Validate but don't write to filesystem (for testing)",
                "default": false
            },
            "user": {
                "type": "string",
                "description": "Username for audit logging (optional)"
            }
        },
        "required": ["generated_markdown", "file_metadata"]
    }
}
```

**Acceptance Criteria:**
- ✅ Schema is valid JSON Schema
- ✅ All properties documented
- ✅ Matches actual function parameters
- ✅ Default values specified

**Status:** ⬜ Not Started

---

#### Task 2.3: Test Tool Registration

**File:** `tests/test_server_enforcement_integration.py`

**What to do:**
Create unit tests to verify tool is registered and callable.

**Specific Changes:**
```python
# Create new test file: tests/test_server_enforcement_integration.py

import pytest
import asyncio
from src.server import server, handle_validate_and_write, VALIDATE_AND_WRITE_TOOL_SCHEMA


class TestEnforcementToolRegistration:
    """Test that enforcement tool is properly registered in MCP server."""
    
    def test_tool_schema_valid(self):
        """Verify tool schema is valid JSON Schema."""
        assert "name" in VALIDATE_AND_WRITE_TOOL_SCHEMA
        assert VALIDATE_AND_WRITE_TOOL_SCHEMA["name"] == "validate_and_write_documentation"
        assert "inputSchema" in VALIDATE_AND_WRITE_TOOL_SCHEMA
        assert "description" in VALIDATE_AND_WRITE_TOOL_SCHEMA
    
    @pytest.mark.asyncio
    async def test_validate_and_write_with_minimal_args(self):
        """Test tool with minimal required arguments."""
        result = await handle_validate_and_write({
            "generated_markdown": "# Test\n\nSome content",
            "file_metadata": {"component_name": "TestComponent"}
        })
        
        assert len(result) == 1
        assert result[0].type == "text"
        # Should return JSON
        import json
        response = json.loads(result[0].text)
        assert "valid" in response or "error" in response
    
    @pytest.mark.asyncio
    async def test_validate_and_write_missing_markdown(self):
        """Test tool with missing required markdown."""
        result = await handle_validate_and_write({
            "file_metadata": {"component_name": "TestComponent"}
        })
        
        assert len(result) == 1
        import json
        response = json.loads(result[0].text)
        assert response["success"] is False
        assert "error" in response


# Run tests: pytest tests/test_server_enforcement_integration.py -v
```

**Acceptance Criteria:**
- ✅ All tests pass
- ✅ Tool is callable with valid arguments
- ✅ Tool returns proper error for missing args
- ✅ Tool schema is valid

**Status:** ⬜ Not Started

---

### BATCH 3: Documentation Generation Flow Update (5-6 hours)

**Objective:** Integrate enforcement into the documentation generation workflow (after LLM generation)

**Priority:** 🟠 HIGH (core functionality)

---

#### Task 3.1: Update `generate_documentation` Workflow (FIXED: Remove bypass path)

**File:** `src/tools/documentation.py`

**What to do:**
Modify the documentation generation flow to call enforcement tool after LLM generation. **CRITICAL**: Remove the "legacy write without enforcement" bypass path to truly make enforcement the hard gate.

**Specific Changes:**
```python
# In documentation.py, find the main generation function and add enforcement

async def generate_documentation_with_enforcement(
    component_path: str,
    template_name: str,
    config: dict,
    dry_run: bool = False,
    update_mode: str = "create",
    overwrite: bool = False
) -> dict:
    """
    Generate documentation with automatic template enforcement.
    
    CRITICAL: Enforcement is ALWAYS enabled. This is the ONLY write path.
    
    Steps:
    1. Load template (for schema only, not for prompt)
    2. Generate markdown via LLM (minimal prompt)
    3. Validate and auto-fix via enforcement tool (HARD GATE)
    4. Write to filesystem (via tool only)
    5. Return results
    """
    
    # Step 1: Prepare minimal LLM prompt (NO full template text)
    component_content = read_component_file(component_path)
    prompt = prepare_minimal_prompt(component_content, template_name)  # NEW: minimal
    
    # Step 2: Call LLM
    generated_markdown = await call_llm(prompt)
    
    # Step 3: Validate and enforce template (HARD GATE - no bypass)
    from src.tools.enforcement_tool import validate_and_write_async
    from src.tools.enforcement_tool_types import FileMetadata
    
    file_metadata = FileMetadata(
        file_path=component_path,
        component_name=extract_component_name(component_path),
        feature_tag=extract_feature_tag(config),
        domain=extract_domain(config),
        module_name=extract_module_name(component_path),
        complexity="Medium"
    )
    
    result = await validate_and_write_async(
        generated_markdown=generated_markdown,
        template_name=template_name,
        file_metadata=file_metadata,
        config=config,
        update_mode=update_mode,
        dry_run=dry_run,
        overwrite=overwrite
    )
    
    return {
        "success": result.valid,
        "file_path": result.file_path if result.valid else None,
        "valid": result.valid,
        "violations": result.violations,
        "confidence": result.confidence,
        "summary": result.summary,
        "generated_markdown": generated_markdown  # For inspection
    }
    # NO ELSE CLAUSE - enforcement is the only path
```

**Acceptance Criteria:**
- ✅ Function calls enforcement tool after LLM generation
- ✅ Result includes validation outcome
- ✅ Backward compatibility maintained (enforce=False)
- ✅ Handles errors gracefully

**Status:** ⬜ Not Started

---

#### Task 3.2: Use Minimal Prompt Contract (FIXED: No full template embedding)

**File:** `src/tools/documentation.py`

**What to do:**
Replace the function that embeds full template text with a **minimal contract prompt**. This is critical to prevent LLM from paraphrasing structure.

**Specific Changes:**
```python
# Replace prepare_prompt() with prepare_minimal_prompt()

def prepare_minimal_prompt(component_content: str, template_name: str) -> str:
    """Prepare minimal LLM prompt (NO full template text).
    
    The enforcement tool is the schema authority, not the prompt.
    Keep prompts lean to save context and prevent structure paraphrasing.
    """
    
    # Template-specific minimal contract (section names only)
    required_sections = {
        "lean_baseline_service_template.md": [
            "Quick Reference (TL;DR)",
            "What & Why",
            "How It Works",
            "Business Rules",
            "Architecture",
            "Data Operations",
            "Questions & Gaps"
        ]
    }
    
    sections_list = "\n".join(f"- {s}" for s in required_sections.get(template_name, []))
    
    prompt = f"""
Generate AKR documentation for this component:

{component_content}

Documentation Contract:
1. **YAML Front Matter**: Do NOT add (tool will auto-generate)
2. **Required sections** (use these exact names, in this order):
{sections_list}

3. **Content rules**:
   - Mark AI-generated content with 🤖
   - Mark unknowns/business context with ❓ [HUMAN: description]
   - Do NOT invent business details
   - Do NOT add extra sections
   - Do NOT change heading names or levels

4. **Validation**: Your output will be validated by an enforcement tool.
   - Missing sections → retry with stricter prompt
   - Wrong order → auto-fixed
   - Missing YAML → auto-generated

Focus on accurate CONTENT. Tool handles FORMAT compliance.
"""
    
    return prompt
```

**Acceptance Criteria:**
- ✅ Prompt includes enforcement guidance
- ✅ LLM understands auto-fix behavior
- ✅ Prompt emphasizes content over structure
- ✅ Guidance doesn't exceed context budget

**Status:** ⬜ Not Started

---

#### Task 3.3: Add Configuration for Enforcement Options

**File:** `config.json`

**What to do:**
Add configuration schema for enforcement tool options to project config.

**Specific Changes:**
```json
{
  "documentation": {
    "output_path": "docs/",
    "pathMappings": {
      "src/**/*.cs": "docs/{module}.md"
    },
    "enforcement": {
      "enabled": true,
      "validationStrictness": "baseline",
      "requireYamlFrontmatter": true,
      "enforceSectionOrder": true,
      "autoFixEnabled": true,
      "allowRetry": true,
      "maxRetries": 3
    },
    "mergePolicy": {
      "enabled": false,
      "strategy": "append",
      "sectionOwnership": {},
      "rewriteThreshold": 0.8
    }
  }
}
```

**Acceptance Criteria:**
- ✅ Config is valid JSON
- ✅ All enforcement options present
- ✅ Defaults are sensible
- ✅ Config loads without errors

**Status:** ⬜ Not Started

---

### BATCH 4: End-to-End Testing & Documentation (6-8 hours)

**Objective:** Verify entire workflow works with real code and templates, create developer guide

**Priority:** 🟠 HIGH (validation & documentation)

---

#### Task 4.1: Create End-to-End Integration Tests

**File:** `tests/test_enforcement_e2e.py`

**What to do:**
Create comprehensive E2E tests using real templates and generated documentation.

**Specific Changes:**
```python
# Create new test file: tests/test_enforcement_e2e.py

import pytest
import tempfile
import json
from pathlib import Path
from src.tools.enforcement_tool import validate_and_write_async
from src.tools.enforcement_tool_types import FileMetadata, ValidationResult
from src.resources.akr_resources import AKRResourceManager


class TestEnforcementE2E:
    """End-to-end tests for template enforcement tool."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "docs").mkdir()
            yield tmpdir
    
    @pytest.fixture
    def resource_manager(self):
        """Initialize resource manager."""
        return AKRResourceManager()
    
    @pytest.mark.asyncio
    async def test_lean_baseline_service_enforcement(self, temp_workspace, resource_manager):
        """Test enforcement with lean baseline service template."""
        
        # Load template
        template = resource_manager.get_template("lean_baseline_service_template.md")
        assert template, "Template not found"
        
        # Sample generated markdown (simulating LLM output WITHOUT YAML)
        generated_markdown = """
# Service: UserService

**Namespace**: MyApp.Services
**File Location**: `src/Services/UserService.cs`
**Complexity**: Medium

## Quick Reference (TL;DR)

🤖 Manages user account operations: create, retrieve, update, delete.

**When to use**: User management operations
**Watch out for**: No role-based access control

## What & Why

🤖 Provides user CRUD operations for the system.

## How It Works

🤖 Coordinates with UserRepository to perform data operations.

## Business Rules

| Rule | Description |
|------|-------------|
| BR-US-001 | 🤖 Email must be unique |

## Architecture

🤖 **Dependencies**: UserRepository, EmailValidator

## Data Operations

🤖 **Reads**: Users table
**Writes**: Users table

## Questions & Gaps

❓ [HUMAN: What are the authorization requirements?]
"""
        
        # Create config
        config = {
            "workspace_root": temp_workspace,
            "documentation": {
                "output_path": "docs/",
                "pathMappings": {
                    "**/*Service.cs": "docs/services/{name}.md"
                }
            }
        }
        
        # Create file metadata
        metadata = FileMetadata(
            file_path="src/Services/UserService.cs",
            component_name="UserService",
            feature_tag="FN001_US001",
            domain="Users",
            module_name="UserService"
        )
        
        # Validate and write
        result = await validate_and_write_async(
            generated_markdown=generated_markdown,
            template_name="lean_baseline_service_template.md",
            file_metadata=metadata,
            config=config,
            overwrite=True,
            dry_run=False
        )
        
        # Assertions
        assert isinstance(result, ValidationResult)
        assert result.valid is True, f"Validation failed: {result.violations}"
        assert result.file_path is not None
        assert result.confidence >= 0.9
        
        # Verify file exists
        written_file = Path(result.file_path)
        assert written_file.exists(), f"File not written: {result.file_path}"
        
        # Read actual written content
        content = written_file.read_text()
        
        # Verify YAML front matter was added
        assert content.startswith("---"), "YAML front matter missing"
        assert "feature:" in content, "YAML missing 'feature' field"
        assert "domain:" in content, "YAML missing 'domain' field"
        assert "component:" in content, "YAML missing 'component' field"
        
        # NEW: Verify section structure in written file
        sections = self._extract_h2_sections(content)
        expected_sections = [
            "Quick Reference",
            "What & Why",
            "How It Works",
            "Business Rules",
            "Architecture",
            "Data Operations",
            "Questions & Gaps"
        ]
        
        section_names = [s["name"] for s in sections]
        for expected in expected_sections:
            assert any(expected in name for name in section_names), \
                f"Expected section '{expected}' not found. Found: {section_names}"
        
        # NEW: Verify section ordering
        expected_order = expected_sections
        actual_order = [s["name"] for s in sections]
        # Check that expected sections appear in correct relative order
        last_index = -1
        for expected_section in expected_order:
            matching = [i for i, name in enumerate(actual_order) if expected_section in name]
            if matching:
                current_index = matching[0]
                assert current_index > last_index, \
                    f"Section '{expected_section}' out of order (at {current_index}, should be after {last_index})"
                last_index = current_index
        
        # NEW: Verify heading hierarchy (no jumps)
        self._verify_heading_hierarchy(content)
    
    def _extract_h2_sections(self, markdown: str):
        """Extract H2 section names and line numbers."""
        sections = []
        for i, line in enumerate(markdown.split("\n")):
            if line.startswith("## ") and not line.startswith("### "):
                name = line.replace("##", "").strip()
                sections.append({"name": name, "line": i})
        return sections
    
    def _verify_heading_hierarchy(self, markdown: str):
        """Verify no heading level jumps (# → ## OK, # → ### BAD)."""
        last_level = 0
        for i, line in enumerate(markdown.split("\n")):
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                if last_level > 0 and level > last_level + 1:
                    raise AssertionError(
                        f"Line {i}: Heading jump from level {last_level} to {level}\n"
                        f"Line: {line}\n"
                        f"Fix: Add intermediate heading levels"
                    )
                last_level = level
    
    @pytest.mark.asyncio
    async def test_enforcement_auto_fix_missing_yaml(self, temp_workspace):
        """Test that enforcement auto-generates YAML front matter."""
        
        markdown_without_yaml = """
# Service: TestService

## Quick Reference
Test content

## What & Why
Test content

## How It Works
Test content

## Business Rules
Test table

## Architecture
Test content

## Data Operations
Test content

## Questions & Gaps
Test content
"""
        
        config = {
            "workspace_root": temp_workspace,
            "documentation": {
                "output_path": "docs/",
                "pathMappings": {"**/*.cs": "docs/{name}.md"}
            }
        }
        
        metadata = FileMetadata(
            file_path="TestService.cs",
            component_name="TestService"
        )
        
        result = await validate_and_write_async(
            generated_markdown=markdown_without_yaml,
            template_name="lean_baseline_service_template.md",
            file_metadata=metadata,
            config=config,
            overwrite=True
        )
        
        # Should succeed because YAML is auto-generated
        assert result.valid is True
        
        # Check violations for YAML fix
        yaml_violations = [v for v in result.violations if "yaml" in v.type.lower()]
        if yaml_violations:
            assert all(v.severity.name == "FIXABLE" for v in yaml_violations)
    
    @pytest.mark.asyncio
    async def test_enforcement_detects_missing_required_section(self, temp_workspace):
        """Test that enforcement detects missing required sections."""
        
        markdown_missing_sections = """
# Service: TestService

## Quick Reference
Test content

## What & Why
Test content

# Missing Business Rules and other sections
"""
        
        config = {
            "workspace_root": temp_workspace,
            "documentation": {
                "output_path": "docs/",
                "pathMappings": {"**/*.cs": "docs/{name}.md"}
            }
        }
        
        metadata = FileMetadata(
            file_path="TestService.cs",
            component_name="TestService"
        )
        
        result = await validate_and_write_async(
            generated_markdown=markdown_missing_sections,
            template_name="lean_baseline_service_template.md",
            file_metadata=metadata,
            config=config,
            overwrite=True
        )
        
        # Should fail because required sections missing (BLOCKER violations)
        assert result.valid is False
        
        # Should have BLOCKER violations for missing sections
        blocker_violations = [v for v in result.violations if v.severity.name == "BLOCKER"]
        assert len(blocker_violations) > 0


# Run tests: pytest tests/test_enforcement_e2e.py -v -s
```

**Acceptance Criteria:**
- ✅ All E2E tests pass
- ✅ Tests cover happy path (valid doc)
- ✅ Tests cover auto-fix scenarios (missing YAML)
- ✅ Tests cover error scenarios (missing sections)
- ✅ Real templates and files used
- ✅ File I/O verified

**Status:** ⬜ Not Started

---

#### Task 4.2: Integration Test with Real Project Files

**File:** `tests/test_enforcement_real_files.py`

**What to do:**
Test enforcement with actual training-tracker backend files.

**Specific Changes:**
```python
# Create new test file: tests/test_enforcement_real_files.py

import pytest
from pathlib import Path
from src.tools.enforcement_tool import validate_and_write_async
from src.tools.enforcement_tool_types import FileMetadata


class TestEnforcementRealFiles:
    """Test enforcement with real project files."""
    
    @pytest.mark.asyncio
    async def test_enrollment_service_documentation(self):
        """Test with EnrollmentService from training-tracker project."""
        
        # Sample LLM-generated doc for EnrollmentService
        generated_markdown = """
# Service: EnrollmentService

**Namespace/Project**: TrainingTracker.Api.Domain.Services
**File Location**: `TrainingTracker.Api/Domain/Services/IEnrollmentService.cs`
**Complexity**: Medium
**Documentation Level**: 🔶 Baseline (70% complete)

## Quick Reference (TL;DR)

🤖 Manages user course enrollments across their lifecycle: create, retrieve, update status, and delete.

**When to use**: Any operation involving enrolling users in courses

**Watch out for**: ❓ [HUMAN: Business rule for status values]

## What & Why

🤖 Technical: Orchestrates enrollment operations between controllers and repositories.

❓ **Business Context**: [HUMAN: What is the enrollment model?]

## How It Works

🤖 Validates user and course exist, checks for duplicates, creates enrollment record.

## Business Rules

| Rule ID | Description |
|---------|-------------|
| BR-ENR-001 | 🤖 Users cannot enroll in same course twice |

## Architecture

🤖 **Dependencies**: UserRepository, CourseRepository

## Data Operations

🤖 **Reads**: Users, Courses, Enrollments
**Writes**: Enrollments

## Questions & Gaps

❓ [HUMAN: Are there enrollment count limits?]
"""
        
        config = {
            "workspace_root": ".",
            "documentation": {
                "output_path": "docs/",
                "pathMappings": {
                    "TrainingTracker.Api/**/*.cs": "docs/services/{name}.md"
                }
            }
        }
        
        metadata = FileMetadata(
            file_path="TrainingTracker.Api/Domain/Services/IEnrollmentService.cs",
            component_name="EnrollmentService",
            feature_tag="FN12345_US067",
            domain="Training",
            module_name="Enrollment"
        )
        
        result = await validate_and_write_async(
            generated_markdown=generated_markdown,
            template_name="lean_baseline_service_template.md",
            file_metadata=metadata,
            config=config,
            dry_run=True  # Don't actually write in test
        )
        
        # Verify validation result
        print(f"\nValidation Result:")
        print(f"  Valid: {result.valid}")
        print(f"  Confidence: {result.confidence}")
        print(f"  Violations: {len(result.violations)}")
        print(f"  Summary: {result.summary}")
        
        for v in result.violations:
            print(f"    - {v.severity.name}: {v.type} @ {v.line}: {v.message}")


# Run tests: pytest tests/test_enforcement_real_files.py -v -s
```

**Acceptance Criteria:**
- ✅ Test runs with real file paths
- ✅ Validation produces expected results
- ✅ YAML is correctly generated
- ✅ Violations logged properly
- ✅ No actual file I/O in dry-run mode

**Status:** ⬜ Not Started

---

#### Task 4.3: Create Developer Integration Guide

**File:** `docs/DEVELOPER_GUIDE_ENFORCEMENT_INTEGRATION.md`

**What to do:**
Document how developers integrate enforcement tool into their code generation workflows.

**Specific Changes:**
Create new markdown file with sections:

```markdown
# Developer Guide: Enforcement Tool Integration

## Overview

This guide explains how to integrate the Template Enforcement Tool into your documentation generation workflow.

## Quick Start

### 1. Call Enforcement Tool After LLM Generation

```python
from tools.enforcement_tool import validate_and_write_async
from tools.enforcement_tool_types import FileMetadata

result = await validate_and_write_async(
    generated_markdown=llm_output,
    template_name="lean_baseline_service_template.md",
    file_metadata=FileMetadata(
        file_path="src/Services/MyService.cs",
        component_name="MyService",
        domain="MyDomain"
    ),
    config=config,
    overwrite=True
)

if result.valid:
    print(f"✅ Documentation written to {result.file_path}")
else:
    print(f"❌ Validation failed: {result.violations}")
```

### 2. Understanding Validation Results

- `valid`: Boolean indicating if doc passes all validation rules
- `file_path`: Where the doc was written (if valid)
- `violations`: List of issues found (auto-fixed or blocking)
- `confidence`: Score 0.0-1.0 indicating validation confidence
- `summary`: Human-readable summary of result

### 3. Handling Violations

**FIXABLE violations**: Auto-corrected by tool (YAML generation, section reordering)
**BLOCKER violations**: Require retry with stricter LLM prompt
**WARN violations**: Non-blocking issues (Phase 2+)

## Configuration

See `config.json` enforcement section for options:

```json
{
  "enforcement": {
    "enabled": true,
    "autoFixEnabled": true,
    "validationStrictness": "baseline",
    "allowRetry": true,
    "maxRetries": 3
  }
}
```

## Testing

Run end-to-end tests:

```bash
pytest tests/test_enforcement_e2e.py -v -s
pytest tests/test_enforcement_real_files.py -v -s
```

## Troubleshooting

[Include common issues and solutions from previous analysis]

## See Also

- [IMPLEMENTATION_PLAN_TEMPLATE_ENFORCEMENT_TOOL.md](IMPLEMENTATION_PLAN_TEMPLATE_ENFORCEMENT_TOOL.md)
- [COPILOT_AGENT_IMPLEMENTATION_BATCHES.md](COPILOT_AGENT_IMPLEMENTATION_BATCHES.md)
```

**Acceptance Criteria:**
- ✅ Guide covers quick start
- ✅ Examples are copy-pasteable
- ✅ Configuration options explained
- ✅ Testing instructions included
- ✅ Troubleshooting section present

**Status:** ⬜ Not Started

---

#### Task 4.4: Verify Integration with Existing Tests

**File:** `tests/` (all test files)

**What to do:**
Run full test suite to ensure enforcement tool doesn't break existing functionality.

**Specific Changes:**
```bash
# Run all existing tests
pytest tests/ -v --tb=short

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific enforcement tests
pytest tests/test_enforcement*.py -v -s
```

**Acceptance Criteria:**
- ✅ All existing tests pass
- ✅ New tests pass
- ✅ Code coverage remains >80%
- ✅ No regressions introduced

**Status:** ⬜ Not Started

---

#### Task 4.5: Create Integration Checklist

**File:** `docs/INTEGRATION_CHECKLIST.md`

**What to do:**
Create final verification checklist for integration completion.

**Specific Changes:**
```markdown
# Template Enforcement Tool Integration Checklist

## Batch 1: Server Integration Preparation
- [ ] Imports added to server.py
- [ ] No circular import issues
- [ ] Telemetry logger initialized
- [ ] Config schema loaded correctly

## Batch 2: MCP Tool Registration  
- [ ] validate_and_write_documentation tool registered
- [ ] Tool schema valid
- [ ] Error handling works
- [ ] Telemetry logging works
- [ ] Tool registration tests pass

## Batch 3: Documentation Generation Flow
- [ ] generate_documentation_with_enforcement function works
- [ ] LLM prompts updated with enforcement guidance
- [ ] config.json updated with enforcement options
- [ ] Backward compatibility maintained (enforce=False)

## Batch 4: End-to-End Testing
- [ ] E2E tests pass (auto-fix, missing sections)
- [ ] Real file tests pass (enrollment service)
- [ ] All existing tests still pass
- [ ] No regressions
- [ ] Coverage >80%
- [ ] Developer guide complete
- [ ] Integration checklist complete

## Final Verification
- [ ] Test with training-tracker backend
- [ ] Manual test with VSCode MCP server
- [ ] Verify telemetry logging works
- [ ] Update README with new workflow
- [ ] Create sample prompt documentation

## Sign-Off
- [ ] Code review completed
- [ ] All acceptance criteria met
- [ ] Ready for production

**Approved by**: [Name]
**Date**: [Date]
```

**Acceptance Criteria:**
- ✅ Checklist is comprehensive
- ✅ All items trackable
- ✅ Clear sign-off criteria

**Status:** ⬜ Not Started

---

## 📊 Progress Tracking

### Batch Summary

| Batch | Name | Duration | Status |
|-------|------|----------|--------|
| 1 | Server Integration Preparation | 4-6h | ⬜ Not Started |
| 2 | MCP Tool Registration | 3-4h | ⬜ Not Started |
| 3 | Documentation Generation Flow Update | 5-6h | ⬜ Not Started |
| 4 | E2E Testing & Documentation | 6-8h | ⬜ Not Started |
| **TOTAL** | | **18-24 hours** | ⬜ Not Started |

### Batch Dependency Graph

```
┌──────────────────────────────────────────┐
│ Batch 1: Server Integration Preparation  │
│ (Imports, Telemetry, Config)             │
└──────────────────┬───────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────┐
│ Batch 2: MCP Tool Registration           │
│ (Tool Definition, Schema, Tests)         │
└──────────────────┬───────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
┌──────────────────────┐  ┌──────────────────────┐
│ Batch 3: Flow Update │  │ Batch 4: E2E Testing │
│ (Enforcement in Flow)│  │ (Validation & Docs)  │
└──────────────────┬───┘  └──────────────────────┘
                   │
                   ▼
        ✅ Integration Complete
```

---

## 🎯 Success Criteria

### Overall Integration Success

✅ **Functional**: Documentation generation with automatic template enforcement works end-to-end  
✅ **Integrated**: Enforcement tool is wired into MCP server workflow  
✅ **Tested**: All test suites pass with >80% coverage  
✅ **Documented**: Developer guide and integration guide complete  
✅ **Verified**: Real-world test with training-tracker backend files passes  
✅ **Ready**: Production-ready code with telemetry and error handling  

### Specific Measurable Outcomes

- Generated docs now **100% include YAML front matter** (auto-generated)
- Generated docs now **100% have required sections in correct order** (auto-fixed)
- Generated docs now **100% have valid heading hierarchy** (auto-fixed)
- First-pass validation success rate: **>90%** (target: >95% with retries)
- User experience: **~20-25 minutes per doc** (includes manual enhancement of ❓ sections)

---

## 🚀 Next Steps After Integration

### Phase 2 Enhancements (Future)

- ✨ Section merge engine for updating existing docs
- ✨ Advanced markers and diagram validation
- ✨ Customizable section templates
- ✨ Multi-language support
- ✨ Advanced merge conflict resolution

### Production Rollout

1. Deploy to staging environment
2. Test with live templates and real projects
3. Gather feedback from users
4. Deploy to production
5. Monitor telemetry for issues

---

## � Critical Improvements Applied (M365 Copilot Feedback)

This plan incorporates 6 critical fixes identified in peer review:

### 1. Enforcement as Hard Gate
**Problem**: If tool validates but other code paths can still write, compliance is lost.  
**Fix**: Tool is the ONLY writer. No bypass paths. See Task 2.1 integration.

### 2. Minimal Prompt (Not Full Template Text)
**Problem**: Embedding full template causes models to "summarize" structure.  
**Fix**: Task 3.2 now uses minimal contract (sections list + markers only). Enforcement tool is schema authority.

### 3. Tool Dispatcher Integration
**Problem**: Creating second `@server.call_tool()` conflicts with existing dispatcher.  
**Fix**: Task 2.1 now integrates into existing dispatcher as a case branch.

### 4. Config Schema Alignment
**Problem**: Config keys don't match enforcement tool's actual contract.  
**Fix**: Task 3.3 now validates config matches tool expectations with startup check.

### 5. Update Mode Support
**Problem**: Tool schema missing `update_mode` for create/replace/merge intent.  
**Fix**: Task 2.2 schema now includes explicit `update_mode` parameter.

### 6. Output Validation Tests
**Problem**: Tests verified return codes, not actual written file structure.  
**Fix**: Task 4.1 tests now extract sections, verify order, check heading hierarchy in written files.

---

## 📝 Debug Checklist (When Docs Still Don't Follow Template)

If you generate docs and they still don't follow template structure, use this checklist:

**1. Was enforcement tool invoked?**
- [ ] Check server logs for validation start/end events
- [ ] Look for `VALIDATION_RUN` entries in `logs/enforcement.jsonl`
- [ ] If no logs: enforcement is not wired into generation flow

**2. Did tool return `valid=false`?**
- [ ] Check result.violations for BLOCKER violations
- [ ] If BLOCKER present: tool detected issues (good!)
- [ ] If valid=true but file format still wrong: tool may not have run on final output

**3. Is file written outside the tool?**
- [ ] Search codebase for `.write()` or `open("w")` calls that aren't in FileWriter
- [ ] Check if agent is writing LLM output directly (bypassing tool)
- [ ] This is the most common issue!

**4. Is template name correct?**
- [ ] Verify template file exists: `ls akr_content/templates/lean_baseline_service_template.md`
- [ ] Check tool can load it: print template in logs

**5. Do pathMappings match your paths?**
- [ ] Example: Does config say `"TrainingTracker.Api/**/*.cs"` match your actual file path?
- [ ] If path doesn't match rule, tool may refuse to write
- [ ] Check config validation log at server startup

**6. Is config.json valid and loaded?**
- [ ] Verify `config.json` is valid JSON (use online validator)
- [ ] Check server startup logs for config load success
- [ ] Look for validation errors like "enforcement disabled"

---

**Last Updated:** February 3, 2026  
**Status:** Ready for Copilot Agent Execution (With Critical Improvements Applied)
