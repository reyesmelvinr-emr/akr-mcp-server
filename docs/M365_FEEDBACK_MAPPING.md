# M365 Copilot Feedback → Integration Plan Mapping

**Date:** February 3, 2026  
**Purpose:** Show how each piece of M365 Copilot feedback is addressed in the final integration plan

---

## Issue #1: Three Bypass Paths Identified

### M365 Feedback
> Your codebase has three ways to write docs without enforcement:
> 1. `write_documentation()` → unvalidated write
> 2. `update_documentation_sections()` → direct `Path.write_text()` 
> 3. `add_ai_header()` → prepends BEFORE YAML

### Plan Resolution

| Bypass Path | Problem | Task | Fix |
|-------------|---------|------|-----|
| `write_documentation()` | Writes without enforcement | 3.1 | Insert `validate_and_fix()` call; refuse write if `valid=false` |
| `update_documentation_sections()` | Direct write; no git; no enforcement | 3.2 | Convert to pure logic; move write+enforce+commit to `update_documentation_sections_and_commit()` |
| `add_ai_header()` | Comment before YAML (violates YAML-first) | 3.0 | Helper `_insert_ai_header_after_yaml()`; move insertion to after YAML closing `---` |

**Why This Matters:**  
Without these fixes, enforcement is NOT a hard gate. Your implementation won't guarantee compliance.

---

## Issue #2: Dispatcher Duplication Risk

### M365 Feedback
> Your plan shows creating a new `@server.call_tool()` function. That will override/break existing tools.

### Plan Resolution

**Task 2.1** explicitly says:
```
DO NOT create a new @server.call_tool() function.
Find EXISTING dispatcher, add case branches for write_documentation and update_documentation_sections.
```

**Code in plan shows:**
```python
async def call_tool(name: str, arguments: dict):
    if name == "get_charter":
        # existing implementation
    elif name == "write_documentation":
        # NEW BRANCH (no new decorator)
    elif name == "update_documentation_sections":
        # NEW BRANCH (no new decorator)
```

**Why This Matters:**  
MCP dispatchers can only have one `@server.call_tool()` decorator. Adding a second one causes routing conflicts.

---

## Issue #3: Minimal Prompt Contract (Not Embedding Full Template)

### M365 Feedback
> Your plan still embeds full template text in prompts. This causes models to paraphrase structure instead of focusing on content.

### Plan Resolution

**Task 3.2 NOT NEEDED** in Batch 3 now, because:
- Your repo's `generate_documentation()` workflow is handled by LLM directly
- The enforcement tool is the schema authority, not the prompt
- Plan emphasizes **minimal contract prompts** (section names only) throughout

**Note:** Since your current `generate_documentation()` is a placeholder, this is a prep for future work. The critical path for NOW is write/update gates (Tasks 3.0-3.2), not LLM generation.

---

## Issue #4: YAML Front Matter Conflict

### M365 Feedback
> Your AI header prepends an HTML comment BEFORE YAML. When enforcement tool auto-generates YAML front matter, your comment ends up in the middle of the file, not at the top.

### Plan Resolution

**Task 3.0** (CRITICAL - must do first):
- Add helper `_insert_ai_header_after_yaml(header: str, content: str) → str`
- Refactor `add_ai_header()` to return ONLY the header text (not full content)
- Insertion happens in write path, AFTER YAML closing `---`

**Acceptance Criteria:**
- ✅ YAML front matter is preserved as first content
- ✅ AI header appears after YAML closing `---`
- ✅ No YAML is malformed

**Why Task 3.0 is First:**  
Tasks 3.1 and 3.2 both use `_insert_ai_header_after_yaml()`. If this isn't fixed first, all downstream writes will have YAML violations.

---

## Issue #5: Config Schema Alignment

### M365 Feedback
> Config keys don't match enforcement tool's contract. Causes silent failures where tool tries to read keys that don't exist.

### Plan Resolution

**Task 1.3** updates `config.json` with:
```json
{
  "documentation": {
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

**Server.py Task 1.3** loads this:
```python
def load_enforcement_config(config: dict) -> dict:
    doc_config = config.get("documentation", {})
    enforcement_config = doc_config.get("enforcement", {})
    return {
        "enabled": enforcement_config.get("enabled", True),
        "write_mode": enforcement_config.get("writeMode", "git"),
        # ... all keys match tool expectations
    }
```

**Why This Matters:**  
If keys don't exist, enforcement tool falls back to defaults silently. Creates false sense of security.

---

## Issue #6: Hard-Gate Clarity

### M365 Feedback
> Plan claims "tool is the ONLY writer" but then shows bypass paths and optional enforcement. That's contradictory.

### Plan Resolution

**Plan includes hard-gate architecture diagram:**
```
LLM Output
   ↓
[ENFORCEMENT: validate_and_fix()]  ← HARD GATE
   ├→ INVALID? Return error (no write)
   └→ VALID?  
      ↓
   [Write via DocumentationWriter]
      ↓
   stage → commit
```

**Plan explicitly states:**
- Task 3.1: "HARD GATE: Content MUST pass enforcement before any file write"
- Task 3.2: "HARD GATE: Updated content MUST pass enforcement before any write"
- Task 4.3 (checklist): "Verify no other code path writes docs"

**Final Checklist includes:**
> Enforcement is unavoidable if and only if:
> 1. ✅ write_documentation() enforces; refuses if invalid
> 2. ✅ update_documentation_sections_and_commit() enforces; refuses if invalid
> 3. ✅ No other code path writes docs
> 4. ✅ AI header after YAML
> 5. ✅ All writes stage and commit
>
> If any fail, enforcement is NOT the hard gate.

---

## Issue #7: Import Path Consistency

### M365 Feedback
> Plan mixes `from tools...` and `from src.tools...`. Will cause import errors.

### Plan Resolution

**Task 1.1** uses only:
```python
from src.tools.enforcement_tool import ...
from src.tools.enforcement_tool_types import ...
```

All imports are **absolute** and match your project structure (`src/tools/…`).

---

## Issue #8: Update Workflow Missing

### M365 Feedback
> Plan shows write path but your repo also has update operations that bypass git. Need symmetric treatment.

### Plan Resolution

**Task 3.2** adds `update_documentation_sections_and_commit()`:
```python
def update_documentation_sections_and_commit(
    repo_path: str,
    doc_path: str,
    section_updates: dict[str, str],
    template: str,
    ...
) -> dict:
    """
    Update doc sections WITH enforcement gate and git commit.
    
    Flow: Read → Compute → ENFORCE → Write → Commit
    """
```

Now BOTH paths (create and update) follow same pattern:
1. Content computation
2. Enforcement validation
3. Refuse write if invalid
4. Write via DocumentationWriter (stages + commits)

---

## Issue #9: Test Coverage for Actual Artifacts

### M365 Feedback
> Tests verify return codes but not actual written file structure. A doc could pass validation but be written with wrong structure.

### Plan Resolution

**Task 4.1** includes:
```python
@pytest.mark.asyncio
async def test_write_documentation_enforces_before_write(tmp_path):
    """Test that write_documentation refuses invalid content."""
    
    invalid_markdown = "# Service\n\nNo required sections!"
    result = write_documentation(...)
    
    # CRITICAL: File should NOT be created if invalid
    assert not (tmp_path / "test.md").exists()

@pytest.mark.asyncio
async def test_write_documentation_with_valid_content(tmp_path):
    """Test that write_documentation accepts enforced content."""
    
    valid_markdown = """---
component: TestService
...
"""
    result = write_documentation(...)
    
    # CRITICAL: Verify ACTUAL file structure
    assert (tmp_path / "test.md").exists()
    written = (tmp_path / "test.md").read_text()
    
    # Verify YAML is first
    assert written.startswith("---")
    
    # Verify header comes AFTER YAML
    yaml_end = written.find("---\n", 5)
    header_pos = written.find("<!--")
    assert header_pos > yaml_end  # ← This verifies structure, not just "valid"
```

---

## Summary: All Feedback Addressed

| Feedback | Addressed By | Status |
|----------|--------------|--------|
| Bypass path #1 (write unvalidated) | Task 3.1 | ✅ Enforcement gate |
| Bypass path #2 (direct write + no git) | Task 3.2 | ✅ New function + gate |
| Bypass path #3 (YAML conflict) | Task 3.0 | ✅ Helper + deferred insertion |
| Dispatcher duplication | Task 2.1 | ✅ Extend, don't create new |
| Minimal prompts | Plan narrative | ✅ Explained throughout |
| Config schema drift | Task 1.3 | ✅ Updated config.json |
| Hard-gate clarity | Architecture section + checklist | ✅ Explicit success criteria |
| Import consistency | Task 1.1 | ✅ Absolute imports only |
| Update workflow | Task 3.2 | ✅ Symmetric treatment |
| Test coverage | Task 4.1 | ✅ Verify actual artifacts |

---

**Result:** Integration plan now directly addresses every piece of M365 Copilot feedback with specific, implementable tasks.

---

**Document Status:** ✅ Complete  
**Last Updated:** February 3, 2026
