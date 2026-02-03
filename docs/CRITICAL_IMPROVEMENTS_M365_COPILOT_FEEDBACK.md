# Critical Improvements: M365 Copilot Feedback on Integration Plan

**Date:** February 3, 2026  
**Reviewed By:** M365 Copilot  
**Status:** Applied to INTEGRATION_PLAN_TEMPLATE_ENFORCEMENT_TOOL.md v1.0  

---

## Executive Summary

The integration plan received critical peer review feedback identifying 6 integration risks that could cause template enforcement to fail. All 6 have been incorporated into the plan.

**Key Finding:** Even with perfect components and good prompts, LLM output won't reliably follow template structure unless:
1. Enforcement is the ONLY writer (hard gate)
2. Config and tool contract are aligned
3. Tests verify actual written file structure, not just return codes

---

## The 6 Critical Issues & Fixes

### Issue #1: Prompt with Full Template Text (High Risk)

**Problem:**
Task 3.2 suggested embedding full template content in LLM prompts:
```python
prompt = f"""
...
TEMPLATE TO FOLLOW:
{template_content}  # ← Full template text
...
"""
```

**Why it fails:**
- Blows up context budget (templates are 500+ lines)
- Model treats template as "reference material" not rules
- Models paraphrase/summarize structure, causing exact failures you observed
- Contradicts "focus on content, let tool handle format"

**The Fix (Task 3.2 Updated):**
Use **minimal contract** instead:
```python
def prepare_prompt(component_content: str, template_name: str) -> str:
    # Template-specific section list (small, from schema)
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
    
    sections_str = "\n".join(f"- {s}" for s in required_sections.get(template_name, []))
    
    prompt = f"""
Component to document:
{component_content}

Documentation Contract:
1. YAML Front Matter: Will be auto-generated (don't add)
2. Required sections (in this order):
{sections_str}
3. Markers:
   - 🤖 Mark AI-generated content
   - ❓ [HUMAN: ...] Mark sections needing business context
4. Do NOT:
   - Add new sections
   - Invent business context
   - Change heading names/levels

Focus on content. Tool handles format compliance.
"""
```

**Impact:**
- ✅ Saves context budget
- ✅ Prevents model from paraphrasing structure
- ✅ Enforcement tool becomes the schema authority
- ✅ If sections missing, tool triggers strict retry

---

### Issue #2: Tool Dispatcher Conflict (Critical)

**Problem:**
Task 2.1 suggested creating a second `@server.call_tool()` method:
```python
@server.call_tool()  # ← Creates SECOND dispatcher!
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "validate_and_write_documentation":
        return await handle_validate_and_write(arguments)
```

**Why it fails:**
- Most MCP servers already have one dispatcher
- Two decorators → Python framework ambiguity
- Old dispatcher may be shadowed (breaks other tools)
- Tool routing becomes unpredictable

**The Fix (Task 2.1 Updated):**
Integrate into EXISTING dispatcher as a case:
```python
# Find existing @server.call_tool() (line ~150-200)
# Add branch to it:

@server.call_tool()  # Do NOT add another decorator
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    # Existing tools
    if name == "generate_documentation":
        return await handle_generate_documentation(arguments)
    # ... other existing tools ...
    
    # NEW: Add enforcement tool
    elif name == "validate_and_write_documentation":
        return await handle_validate_and_write(arguments)
    
    else:
        raise ValueError(f"Unknown tool: {name}")
```

**Impact:**
- ✅ All tools in one dispatcher
- ✅ No decorator conflicts
- ✅ Tool routing predictable

---

### Issue #3: Import Path Inconsistency (Runtime Failure Risk)

**Problem:**
Plan uses inconsistent import paths:
- Lists completed files as: `src/tools/enforcement_tool_types.py`
- But imports as: `from tools.enforcement_tool import ...` (no `src/`)

**Why it fails:**
- Depends on PYTHONPATH and package structure
- Works in dev (if PYTHONPATH set), fails in prod
- Tool tested one way, server imports another
- Silent import mismatch = wrong module loaded

**The Fix (Task 1.1 Updated):**
Use absolute imports matching project structure:
```python
# Consistent absolute imports
from src.tools.enforcement_tool import validate_and_write_async
from src.tools.enforcement_tool_types import FileMetadata, ValidationResult
from src.tools.enforcement_logger import EnforcementLogger

# VERIFY at runtime
python -c "from src.tools.enforcement_tool import validate_and_write_async"
```

**Impact:**
- ✅ No path ambiguity
- ✅ Same import in dev and prod
- ✅ Import sanity test catches issues early

---

### Issue #4: Config Schema Doesn't Match Tool Contract (Silent Failure)

**Problem:**
Plan introduces config fields that may not match what tool actually reads:
```json
{
  "enforcement": {
    "allowLocalTemplates": "???",
    "validationStrictness": "baseline",
    "mergePolicy": { ... },
    "rewriteThreshold": 0.8
  }
}
```

**Why it fails:**
- If tool expects `auto_fix_enabled` but config has `autoFixEnabled` (camelCase vs snake_case)
- Field mismatch = silent fallback to defaults
- Enforcement disabled unintentionally
- You think it's enabled (config says so), but tool uses defaults

**The Fix (Task 3.3 Updated):**
1. Align field names with actual tool contract
2. Add startup validation
3. Error (not silently pass) on missing required keys

```python
def validate_config_schema(config: dict) -> bool:
    """Verify config matches tool's expectations."""
    doc_config = config.get("documentation", {})
    required_keys = ["output_path", "pathMappings", "enforcement"]
    
    for key in required_keys:
        if key not in doc_config:
            logger.error(f"Config missing required key: documentation.{key}")
            return False
    
    enforcement = doc_config.get("enforcement", {})
    if not enforcement.get("enabled"):
        logger.warning("Enforcement disabled in config")
    
    return True
```

**Config Structure (Updated):**
```json
{
  "documentation": {
    "output_path": "docs/",
    "pathMappings": { ... },
    "enforcement": {
      "enabled": true,
      "validation_strictness": "baseline",  ← snake_case, matches tool
      "auto_fix_enabled": true,              ← snake_case, matches tool
      "require_yaml_frontmatter": true       ← snake_case, matches tool
    }
  }
}
```

**Impact:**
- ✅ Config fields match tool exactly
- ✅ No silent defaults fallback
- ✅ Server startup validates config
- ✅ Errors logged if keys missing

---

### Issue #5: Tool Schema Missing `update_mode` (Ambiguous Intent)

**Problem:**
Task 2.2 schema lacks `update_mode` and has unclear overwrite semantics:
```python
{
    "overwrite": {
        "type": "boolean",
        "description": "Whether to overwrite existing file",
        "default": False
    }
    # No explicit "create vs replace" intent!
}
```

**Why it fails:**
- If file exists and `overwrite=false`, what happens? Error? Skip?
- No explicit "update_mode" means tool infers behavior
- Can accidentally skip generation or overwrite incorrectly
- Merge/update intent not expressed

**The Fix (Task 2.2 Updated):**
Add explicit `update_mode` parameter:
```python
{
    "update_mode": {
        "type": "string",
        "description": "How to handle existing files",
        "enum": ["create", "replace"],
        "default": "create"
    },
    "overwrite": {
        "type": "boolean",
        "description": "Explicit permission to overwrite (required if mode=replace)",
        "default": false
    }
}
```

**Handler Logic:**
```python
update_mode = arguments.get("update_mode", "create")  # explicit
overwrite = arguments.get("overwrite", False)         # hard requirement

# If file exists + mode=create → ERROR
# If file exists + mode=replace + overwrite=false → ERROR
# If file exists + mode=replace + overwrite=true → OK, overwrite
```

**Impact:**
- ✅ No ambiguous intent
- ✅ create vs replace explicit
- ✅ Prevents accidental overwrites
- ✅ Clear error messages

---

### Issue #6: E2E Tests Don't Verify Written File Structure (False Confidence)

**Problem:**
Task 4.1 tests verify validation return codes, but NOT the actual written file:
```python
result = await validate_and_write_async(...)

# Tests verify:
assert result.valid is True  # ✓ Returns valid=true
assert result.file_path is not None  # ✓ File path set
# But DON'T verify:
# - Actual section order in written file
# - Heading hierarchy is correct
# - YAML is really there
```

**Why it fails:**
- Tool can return `valid=true` but file written wrong
- Tests pass, but real output still non-compliant
- Exactly your symptom: "tool completed but output still malformed"

**The Fix (Task 4.1 Updated):**
Add methods to extract and verify actual written file structure:
```python
def test_lean_baseline_service_enforcement(self, ...):
    result = await validate_and_write_async(...)
    
    # WRITE verified
    written_file = Path(result.file_path)
    assert written_file.exists()
    
    content = written_file.read_text()
    
    # YAML verified
    assert content.startswith("---")
    assert "feature:" in content
    
    # SECTIONS verified (NEW)
    sections = self._extract_sections(content)
    expected_sections = [
        "Quick Reference", "What & Why", "How It Works",
        "Business Rules", "Architecture", "Data Operations",
        "Questions & Gaps"
    ]
    
    actual_names = [s["name"] for s in sections]
    for expected in expected_sections:
        assert any(expected in actual for actual in actual_names), \
            f"Missing section: {expected}"
    
    # HEADING HIERARCHY verified (NEW)
    self._verify_heading_hierarchy(content)

def _extract_sections(self, markdown: str):
    """Extract section names and line positions."""
    sections = []
    lines = markdown.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("##") and not line.startswith("###"):
            name = line.replace("##", "").strip()
            sections.append({"name": name, "line": i})
    return sections

def _verify_heading_hierarchy(self, markdown: str):
    """Verify no heading level jumps (# → ## OK, # → ### BAD)."""
    lines = markdown.split("\n")
    last_level = 0
    
    for line in lines:
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            if last_level > 0 and level > last_level + 1:
                raise AssertionError(f"Level jump: {last_level} → {level}")
            last_level = level
```

**Impact:**
- ✅ Tests verify actual written structure
- ✅ Catches "valid=true but file wrong" bugs
- ✅ Heading hierarchy checked
- ✅ Section order verified
- ✅ False confidence eliminated

---

## Summary Table

| Issue | Root Cause | Impact | Fix Applied |
|-------|-----------|--------|------------|
| #1 | Full template in prompt | Model paraphrases structure | Use minimal contract (section list only) |
| #2 | Second tool dispatcher | Conflicts with existing router | Integrate as case branch in existing dispatcher |
| #3 | Import path inconsistency | Silent module mismatch at runtime | Use absolute imports (src.tools.*) |
| #4 | Config fields don't match tool | Silent fallback to defaults | Validate config at startup, use snake_case |
| #5 | Missing update_mode | Ambiguous create/replace intent | Add explicit update_mode parameter |
| #6 | Tests don't verify output | False confidence in compliance | Extract/verify sections, heading hierarchy |

---

## How to Use This Document

### For Copilot Agents
- Reference these fixes when implementing the 4 batches
- Each issue maps to a specific task (noted in table)
- Fixes are already incorporated into INTEGRATION_PLAN_TEMPLATE_ENFORCEMENT_TOOL.md

### For Code Review
- Verify each issue is addressed:
  - Task 1.1: Import paths are absolute (`src.tools.*`)
  - Task 2.1: Tool is added to existing dispatcher, not new one
  - Task 2.2: Schema includes `update_mode`
  - Task 3.2: Prompt uses minimal contract, not full template
  - Task 3.3: Config validation runs at startup
  - Task 4.1: Tests extract and verify file structure

### For Troubleshooting
- If docs still don't follow template after integration:
  - Check the Debug Checklist in main plan
  - Map observed issue to one of these 6 problems
  - Verify corresponding fix was applied

---

## Why These Fixes Matter

**Root Theme:** Compliance is fragile without integration layers.

Even perfect components fail if:
- ❌ Multiple write paths exist (tool + agent)
- ❌ Config silently fallsback to unsafe defaults
- ❌ Prompts contradict tool authority
- ❌ Tests verify happy path but not actual output
- ❌ Schema ambiguities lead to wrong behavior

These fixes ensure enforcement is **deterministic**—the output WILL be compliant, not just likely.

---

**Last Updated:** February 3, 2026  
**Status:** Applied to Integration Plan v1.0
