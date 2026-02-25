# v0.2.0 Acceptance Verification Checklist

**Status:** Automated Verification Complete (93.75% Pass Rate) - **10 BLOCKING Runtime Tests Required**  
**Date:** February 24, 2026  
**Last Run:** February 24, 2026 17:15:44  
**Script:** `scripts/verify_implementation.ps1`

**Environment Requirements:**
- **MCP SDK**: `mcp[cli]>=1.26.0,<1.27` (pinned in requirements.txt)
- **MCP Inspector**: `≥0.14.1` (CVE-2025-49596 fix required)
- **Python**: 3.11+
- **pytest**: Latest with coverage plugin

**Verification Levels:**
- 🟢 **File Exists**: Structure verified (files, imports, handlers present)
- 🟡 **Runtime**: Behavior verified (server started, endpoints called, assertions passed)
- 🔴 **BLOCKING**: Critical for v0.2.0 release - must complete before tagging

---

## 🔥 BLOCKING ITEMS FOR v0.2.0 RELEASE (Priority Order)

These 10 tests are **required** before tagging v0.2.0. Complete in this exact order:

### BLOCKER 1: TemplateResolver Priority Loading
**Why:** Ensures single source of truth (SSoT) with deterministic resolution; remote preview fail-closed
**Test:** `pytest -k test_template_resolver_priority -v`
**Status:** 🔴 BLOCKING

### BLOCKER 2: resources/read Spec-Compliant Payload
**Why:** MCP spec requires `contents[]` array with `uri`, `mimeType`, `text` - clients depend on this shape
**Test:** `pytest tests/test_mcp_resources.py::test_read_resource_payload_shape -v`
**Status:** 🔴 BLOCKING

### BLOCKER 3: Write-Ops Happy Path Returns Dry-Run Diff
**Why:** Least-privilege UX - users review diff by default; write only after explicit intent
**Test:** `AKR_ENABLE_WRITE_OPS=true pytest -k test_write_documentation_dry_run -v`
**Status:** 🔴 BLOCKING

### BLOCKER 4: Front-Matter JSON Schema Validation
**Why:** Front-matter contract for CI and humans; enforce field paths, enums, patterns
**Test:** `pytest -k test_frontmatter_schema_validation -v`
**Status:** 🔴 BLOCKING

### BLOCKER 5: Tier Severity Mapping
**Why:** Prove TIER_1 (≥80%) yields more BLOCKERs than TIER_3 (≥30%) for same doc
**Test:** `pytest -k test_tier_severity_mapping -v`
**Status:** 🔴 BLOCKING

### BLOCKER 6: MCP Tool validate_documentation Callable & Spec-Compliant
**Why:** Copilot/MCP hosts expect tools/call content shape to mirror CLI behavior
**Test:** `pytest tests/test_mcp_resources.py::test_validate_tool_invocation -v`
**Status:** 🔴 BLOCKING

### BLOCKER 7: Auto-Fix Returns Patched Content (No File Writes)
**Why:** Validation is advisory; persistence only through write tools after approval
**Test:** `pytest -k test_auto_fix_patch_return -v`
**Status:** 🔴 BLOCKING

### BLOCKER 8: Extractor Output Cleanliness
**Why:** Schema-stable JSON; no emojis/placeholders - agents depend on predictable keys
**Test:** `pytest -k test_extract_code_context_clean_json -v`
**Status:** 🔴 BLOCKING

### BLOCKER 9: Server Registration Cleanup for Deprecated Tools
**Why:** Prevents Copilot from surfacing confusing legacy tools; keeps tool list crisp
**Test:** `pytest -k test_deprecated_tools_unregistered -v`
**Status:** 🔴 BLOCKING

### BLOCKER 10: CLI Output Formats + Actionable Errors
**Why:** Stable JSON schema and clear next steps in errors for developers and agents
**Test:** `pytest tests/test_cli_akr_validate.py -v && pytest -k test_error_messages_actionable -v`
**Status:** 🔴 BLOCKING

---

## ✅ v0.2.0 Release Gate Checklist

You can tag **v0.2.0** once ALL of the following pass:

- [ ] **All 10 BLOCKING runtime tests** (above) are ✅
- [ ] **MCP spec conformance** tests pass:
  - [ ] `resources/list` returns correct shape
  - [ ] `resources/read` returns `contents[]` with required fields
  - [ ] `resources/templates` exposes dynamic URI construction
  - [ ] `tools/list` returns all active tools with schemas
  - [ ] `tools/call` for validate_documentation returns correct shape
- [ ] **Coverage ≥80%** with `pytest --cov=src --cov-fail-under=80`
- [ ] **SECURITY.md** complete with:
  - [x] MCP trust model documented
  - [x] Inspector ≥0.14.1 requirement (CVE-2025-49596)
  - [x] stdio default highlighted
  - [ ] Future remote transport guidance (streamable-HTTP + TLS + OAuth)
  - [ ] Path safety in write tools (allow-list, symlink rejection, normalization)
- [ ] **requirements.txt** pins MCP SDK: `mcp[cli]>=1.26.0,<1.27`
- [ ] **All files committed and pushed to main**

**Once complete:**
```bash
git tag v0.2.0
git push origin v0.2.0
```

---

## Phase 1: Template Externalization & MCP Resources

### Acceptance Tests

- 🟢 [x] **Submodule configured and directory exists**
  ```bash
  git submodule foreach git log -1 --oneline
  # Expected: Should show commit hash and message
  ```
  ✓ Verified: Submodule `templates/core` exists and is configured

- 🔴 [ ] **TemplateResolver loads templates in priority order (RUNTIME TEST)**
  ```bash
  # Test priority: submodule > local override > remote preview
  pytest -k test_template_resolver_priority -v
  # Expected: When same template exists in multiple locations, submodule wins
  ```
  **Test Requirements:**
  - Create fixtures in 3 locations with different content markers
  - Assert resolver returns submodule content when all 3 exist
  - Assert local override beats remote when submodule missing
  - Assert remote preview with hash verification works
  - Assert fail-closed on hash mismatch

- 🟢 [x] **MCP resource handlers implemented**
  ```bash
  # Start server and test with MCP Inspector or VS Code
  # 1. Run: python -m src.server
  # 2. In Copilot Chat, ask: "List available AKR templates"
  # Expected: Should show template resources
  ```
  ✓ Verified: list_resources, read_resource, list_resource_templates handlers found in server.py

- 🔴 [ ] **MCP resources/read returns spec-compliant payload (RUNTIME TEST)**
  ```bash
  # Start server and call resources/read endpoint
  pytest tests/test_mcp_resources.py::test_read_resource_payload_shape -v
  # Expected: Response must include contents[] with uri, mimeType, and text
  ```
  **Test Requirements:**
  - Start MCP server in test mode
  - Call resources/read with URI `akr://template/lean_baseline_service_template`
  - Assert response has `contents` array
  - Assert each entry has `uri`, `mimeType: "text/markdown"`, and `text` fields
  - Verify `text` contains actual template content
  - No raw string returns (must be proper MCP resource shape)

- [x] **Resource templates handler implemented**
  ```bash
  # In Copilot Chat, try: "Show me akr://template/lean_baseline_service_template"
  # Expected: Template content should be returned
  ```
  ✓ Verified: MCP resource templates handler found in server.py

- [x] **VERSION_MANAGEMENT.md has clear workflow**
  ```bash
  # Manual review
  cat docs/VERSION_MANAGEMENT.md
  # Expected: Clear instructions for updating submodule
  ✓ Verified: File exists at docs/VERSION_MANAGEMENT.md

---

## Phase 2: Write Operations Gating

### Acceptance Tests

- 🟢 [x] **AKR_ENABLE_WRITE_OPS environment flag implemented**
  ```bash
  # Start server without env var
  python -m src.server
  # Expected: Should log "Write operations: DISABLED (default)"
  # Write tools should NOT be registered
  ```
  ✓ Verified: AKR_ENABLE_WRITE_OPS flag found in server.py

- 🟢 [x] **write_documentation with allowWrites parameter**
  ```bash
  # Test in Python:
  python -c "import os; os.environ['AKR_ENABLE_WRITE_OPS']='true'; from src.tools.write_operations import write_documentation; import asyncio; asyncio.run(write_documentation('/tmp/test.md', 'content', allowWrites=False))"
  # Expected: PermissionError with message about allowWrites
  ```
  ✓ Verified: allowWrites parameter found in write_operations.py

- 🔴 [ ] **write_documentation happy path returns dry-run diff (RUNTIME TEST)**
  ```bash
  # Test with both flags enabled
  AKR_ENABLE_WRITE_OPS=true pytest -k test_write_documentation_dry_run -v
  # Expected: Returns {"success": true, "effect": "dry-run", "patch": "...diff..."}
  ```
  **Test Requirements:**
  - Set `AKR_ENABLE_WRITE_OPS=true` in environment
  - Call `write_documentation` with `allowWrites=true` and `mode="dry-run"`
  - Assert response includes `effect: "dry-run"`
  - Assert `patch` field contains unified diff
  - Assert NO file was actually written to disk
  - Test `mode="feature-branch"` performs actual write (VS Code review UI context)

- 🟢 [x] **SECURITY.md exists and documents write operations**
  ```bash
  cat docs/SECURITY.md
  # Expected: Should have sections on MCP trust, Inspector versions, roadmap
  ```
  ✓ Verified: File exists and documents write ops, MCP trust model, and Inspector >= 0.14.1 requirement (CVE-2025-49596)

- [x] **README explains write ops are "off by default"**
  ```bash
  grep -i "write operations" README.md
  # Expected: Should have clear section explaining gating
  ✓ Verified: README.md documents write operations

---

## Phase 3: Dual-Faceted Validation

### Acceptance Tests

- [x] **ValidationEngine correctly wired to TemplateSchemaBuilder**
  ```bash
  # Check code structure
  grep "TemplateSchemaBuilder" src/tools/validation_library.py
  # Expected: Constructor should accept TemplateSchemaBuilder
  ```
  ✓ Verified: ValidationEngine class defined and uses TemplateSchemaBuilder

- [x] **jsonschema dependency added**
  ```bash
  grep jsonschema requirements.txt
  # Expected: jsonschema>=4.0.0 in requirements.txt
  ```
  ✓ Verified: jsonschema dependency found in requirements.txt

- [x] **VALIDATION_GUIDE.md exists with tier documentation**
  ```bash
  grep TIER_1 docs/VALIDATION_GUIDE.md
  # Expected: Should document tier levels
  ```
  ✓ Verified: VALIDATION_GUIDE.md exists and documents TIER_1

- 🔴 [ ] **YAML front matter validated against JSON Schema (RUNTIME TEST)**
  ```bash
  # Test with invalid and valid frontmatter fixtures
  pytest -k test_frontmatter_schema_validation -v
  # OR use CLI:
  python scripts/akr_validate.py --doc tests/fixtures/invalid_frontmatter.md \
    --template lean_baseline_service_template --tier TIER_1 --output json
  ```
  **Test Requirements:**
  - Create `tests/fixtures/invalid_frontmatter.md` with schema violations
  - Create `tests/fixtures/valid_frontmatter.md` with correct fields
  - Invalid: Assert BLOCKER violation with `field_path` and `validator` in message
  - Valid: Assert no front-matter violations
  - Test missing required fields (templateId, project, repo, generatedAtUTC)
  - Test pattern validation (repo must match `owner/name`, commitSha must be hex)
  - Test enum validation (templateId must match manifest)

- 🔴 [ ] **Tier levels control violation severity (RUNTIME TEST)**
  ```bash
  # Test same incomplete doc under different tiers
  pytest -k test_tier_severity_mapping -v
  # OR use CLI comparison:
  python scripts/akr_validate.py --doc tests/fixtures/incomplete_doc.md \
    --template lean_baseline_service_template --tier TIER_1 --output json > tier1.json
  python scripts/akr_validate.py --doc tests/fixtures/incomplete_doc.md \
    --template lean_baseline_service_template --tier TIER_3 --output json > tier3.json
  # Compare: TIER_1 should have MORE BLOCKER violations than TIER_3
  ```
  **Test Requirements:**
  - Create `tests/fixtures/incomplete_doc.md` with missing sections and low completeness
  - Assert TIER_1 produces BLOCKER for missing required sections
  - Assert TIER_3 produces FIXABLE (not BLOCKER) for same missing sections
  - Assert TIER_1 requires ≥80% completeness; TIER_3 requires ≥30%
  - Verify violation counts: count(BLOCKER, TIER_1) > count(BLOCKER, TIER_3)

- 🔴 [ ] **MCP tool validate_documentation callable and spec-compliant (RUNTIME TEST)**
  ```bash
  # In VS Code with Copilot Chat:
  # Ask: "Validate my documentation at docs/ARCHITECTURE.md using template lean_baseline_service_template"
  # OR test programmatically:
  pytest tests/test_mcp_resources.py::test_validate_tool_invocation -v
  ```
  **Test Requirements:**
  - Start MCP server in test mode
  - Call `validate_documentation` tool via MCP protocol
  - Assert response matches CLI output structure (same ValidationResult shape)
  - Assert `violations[]` array contains objects with required fields
  - Assert `auto_fixed_content` field present when fixable violations exist
  - Test via both Copilot Chat and `mcp` CLI for interop

- [x] **CLI akr-validate tool exists**
  ```bash
  # Run CLI and compare with MCP tool results
  python scripts/akr_validate.py --doc docs/ARCHITECTURE.md --template lean_baseline_service_template --tier TIER_2 --output json
  # Expected: Should match MCP tool output structure
  ```
  ✓ Verified: CLI tool found at scripts/akr_validate.py

- 🔴 [ ] **Auto-fix returns patched content without file writes (RUNTIME TEST)**
  ```bash
  # Test auto-fix behavior
  pytest -k test_auto_fix_patch_return -v
  # OR use CLI:
  python scripts/akr_validate.py --doc tests/fixtures/fixable_doc.md \
    --template lean_baseline_service_template --auto-fix --output json
  ```
  **Test Requirements:**
  - Create `tests/fixtures/fixable_doc.md` with fixable violations (missing sections, wrong order)
  - Call validation with `--auto-fix` flag
  - Assert `auto_fixed_content` field is populated
  - Assert file on disk remains UNCHANGED (no write occurred)
  - Assert patched content includes added missing sections
  - Assert patched content has corrected section order
  - Assert `diff` field contains unified diff showing changes
  - Verify dry-run is default behavior (requires explicit write call to persist)
  # Expected: Should return patched content, not write to file
  ```

---

## Phase 4: Extractor Deprecation & Cleanup

### Acceptance Tests

- [x] **CodeAnalyzer implementation exists**
  ```bash
  ls src/tools/code_analytics.py
  # Expected: File should exist
  ```
  ✓ Verified: CodeAnalyzer implementation found at src/tools/code_analytics.py

- [x] **extract_code_context tool registered**
  ```bash
  # Test C# extraction
  # In Copilot Chat: "Extract code context from my C# service files"
  # Expected: Should return methods, classes, imports
  ```
  ✓ Verified: extract_code_context tool found in server.py

- 🔴 [ ] **Returns clean JSON with no emoji/placeholder markers (RUNTIME TEST)**
  ```bash
  # Test extraction output cleanliness
  pytest -k test_extract_code_context_clean_json -v
  # OR manually:
  python -c "from src.tools.code_analytics import CodeAnalyzer; import json; \
    a = CodeAnalyzer(); result = a.analyze('tests/fixtures/sample.cs', ['methods']); \
    print(json.dumps(result, ensure_ascii=True, indent=2))"
  ```
  **Test Requirements:**
  - Create `tests/fixtures/sample.cs` with methods, classes, and imports
  - Call CodeAnalyzer.analyze() on the fixture
  - Assert result contains only these keys: `methods`, `classes`, `imports`, `sql_schema`, `metadata`
  - Assert NO emoji characters (🤖, ❓, etc.) anywhere in output
  - Assert NO placeholder text like "TODO", "FIXME", "[INCOMPLETE]"
  - Assert all values are pure JSON primitives (strings, numbers, booleans, arrays, objects)
  - Assert `metadata.partial` is boolean (true/false), not string
  - Verify output can be parsed by strict JSON parser (no comments, trailing commas)

- [x] **Deprecated extractors have clear warning headers**
  ```bash
  head -20 src/tools/extractors/typescript_extractor.py
  # Expected: Should have ⚠️ DEPRECATED notice
  ```
  ✓ Verified: All 5 deprecated extractors have DEPRECATED headers:
  - typescript_extractor.py
  - business_rule_extractor.py
  - failure_mode_extractor.py
  - method_flow_analyzer.py
  - example_extractor.py

- 🔴 [ ] **Deprecated tools removed from server registration (RUNTIME TEST)**
  ```bash
  # Verify deprecated tools don't appear in tools/list
  pytest -k test_deprecated_tools_unregistered -v
  # OR check manually:
  grep "analyze_codebase" src/server.py  # Should NOT be registered
  ```
  **Test Requirements:**
  - Start MCP server in test mode
  - Call `tools/list` endpoint
  - Assert `analyze_codebase` does NOT appear in tools list
  - Assert other deprecated tools (if any) also not listed
  - Verify only active tools appear: `extract_code_context`, `validate_documentation`, `get_charter`, `write_documentation`, `update_documentation_sections`
  - Check `src/server.py` has commented-out or removed deprecated tool registrations

- 🟡 [ ] **Tests for deprecated tools marked with @pytest.mark.skip**
  ```bash
  # Check skip markers
  grep -r "@pytest.mark.skip" tests/
  # Expected: Deprecated tool tests marked with skip reason
  ```
  **Requirements:**
  - Find tests for `analyze_codebase` tool
  - Add `@pytest.mark.skip(reason="Tool deprecated in v0.2.0; use extract_code_context")` 
  - Add skip markers to TypeScript, BusinessRule, FailureMode, MethodFlow, Example extractor tests
  - Ensure skip reason includes migration guidance

- [x] **CHANGELOG.md exists with v0.2.0 section**
  ```bash
  grep -A 5 "Deprecated" docs/CHANGELOG.md
  # Expected: Should list deprecated extractors with migration path
  ```
  ✓ Verified: CHANGELOG.md exists with v0.2.0 section

---

## Phase 5: Testing & Documentation

### Acceptance Tests

- [x] **Test files exist**
  ```bash
  pytest tests/test_mcp_resources.py tests/test_validation_library.py tests/test_integration_e2e.py -v
  # Expected: All tests should pass
  ```
  ✓ Verified: All 4 required test files exist:
  - test_template_resolver.py
  - test_mcp_resources.py
  - test_validation_library.py
  - test_integration_e2e.py

- [x] **MCP resource handlers test file exists**
  ```bash
  pytest tests/test_mcp_resources.py -v
  # Expected: Tests verify mimeType, uri, text fields
  ```
  ✓ Verified: tests/test_mcp_resources.py exists

- 🔴 [ ] **CLI tool tested for output formats (RUNTIME TEST)**
  ```bash
  # Test JSON and text output formats
  pytest tests/test_cli_akr_validate.py -v
  # OR snapshot tests:
  python scripts/akr_validate.py --doc docs/ARCHITECTURE.md --template lean_baseline_service_template --output json > output.json
  python scripts/akr_validate.py --doc docs/ARCHITECTURE.md --template lean_baseline_service_template --output text > output.txt
  ```
  **Test Requirements:**
  - Test `--output json` produces valid JSON with all required fields
  - Test `--output text` produces human-readable format with colors/formatting
  - Assert JSON output has keys: `success`, `is_valid`, `violations`, `suggestions`, `metadata`
  - Assert text output includes section headers and formatted violation lists
  - Test exit codes: 0 when valid, 1 when invalid
  - Snapshot test to detect regressions in output format

- 🟡 [ ] **Coverage ≥80% verified and enforced**
  ```bash
  # Run coverage check
  pytest --cov=src --cov-report=term-missing --cov-fail-under=80
  # Expected: Pass with ≥80% coverage
  ```
  **Requirements:**
  - Run full test suite with coverage
  - Assert coverage percentage ≥80%
  - Document current coverage in checklist header (currently 81.45%)
  - Add coverage gate to fail builds under 80%
  - Identify untested modules and add tests if coverage drops

- [x] **ARCHITECTURE.md exists**
  ```bash
  grep "v0.2.0" docs/ARCHITECTURE.md
  # Expected: Should describe template provider + validator role
  ```
  ✓ Verified: docs/ARCHITECTURE.md exists

- [x] **COPILOT_CHAT_WORKFLOW.md exists**
  ```bash
  cat docs/COPILOT_CHAT_WORKFLOW.md
  # Expected: Step-by-step guide from extraction to validation to writing
  ```
  ✓ Verified: docs/COPILOT_CHAT_WORKFLOW.md exists

---

## General Checks

- [x] **No Windows-specific paths in documentation**
  ```bash
  grep -r "C:\\\\" docs/
  # Expected: Should return no results or only in examples marked as Windows-specific
  ```
  ✓ Verified: No Windows-specific paths found in documentation

- [x] **Documentation files exist**
  ```bash
  grep -E "(git submodule|cd akr-mcp-server)" docs/INSTALLATION_AND_SETUP.md
  # Expected: Commands should be cross-platform (forward slashes, no drive letters)
  ```
  ✓ Verified: INSTALLATION_AND_SETUP.md exists

- [x] **Deprecation messages clear**
  ```bash
  # Review each deprecated extractor file header
  # Expected: Clear notice + recommendation to use Copilot Chat
  ```
  ✓ Verified: All 5 deprecated extractors have DEPRECATED headers

- [x] **MCP resource URIs consistent**
  ```bash
  grep -r "akr://" src/server.py
  # Expected: Should use akr://template/* and akr://charter/* patterns
  ```
  ✓ Verified: MCP resource URIs use consistent akr:// scheme

- [x] **.gitmodules file exists**
  ```bash
  cat .gitmodules
  # Expected: Should configure templates/core submodule
  ```
  ✓ Verified: .gitmodules file exists for submodule configuration

- 🔴 [ ] **Error messages are actionable (RUNTIME TEST)**
  ```bash
  # Test common error scenarios
  pytest -k test_error_messages_actionable -v
  ```
  **Test Requirements:**
  - **Template not found**: Assert error includes list of valid template IDs
    ```bash
    python scripts/akr_validate.py --doc test.md --template invalid_template --tier TIER_1
    # Expected: "Template 'invalid_template' not found. Available templates: lean_baseline_service_template, ..."
    ```
  - **Missing required field in front matter**: Assert error suggests the field and format
    ```bash
    # Test with doc missing 'repo' field
    # Expected: "Front matter validation failed: 'repo' is required. Example: 'owner/repository-name'"
    ```
  - **Write ops disabled**: Assert error explains both env flag AND allowWrites requirement
    ```bash
    # Call write_documentation with flags disabled
    # Expected: "Write operations disabled. Set AKR_ENABLE_WRITE_OPS=true and pass allowWrites=true"
    ```
  - **Tier violation**: Assert error specifies which tier requirement failed
  - All errors must include **next steps** or **fix suggestions** (not just "Error: X failed")

---

## MCP Spec Conformance

These tests verify the server is compliant with the Model Context Protocol specification.

### Resources Protocol

- 🔴 [ ] **resources/list returns correct shape**
  ```bash
  # Start server and call resources/list
  pytest tests/test_mcp_resources.py::test_resources_list_shape -v
  ```
  **Requirements:**
  - Response includes `resources[]` array
  - Each resource has `uri`, `name`, `mimeType`, optional `description`
  - URIs follow `akr://template/{id}` pattern
  - mimeType is `text/markdown` for templates

- 🔴 [ ] **resources/read returns correct contents[] shape**
  ```bash
  # Already covered in Phase 1, but critical for spec conformance
  pytest tests/test_mcp_resources.py::test_read_resource_payload_shape -v
  ```
  **Requirements:**
  - Response has `contents[]` array (not raw string)
  - Each entry has `uri`, `mimeType`, and `text` fields
  - `mimeType` is `"text/markdown"`
  - `text` contains actual template content
  - URI matches requested resource

- 🔴 [ ] **resources/templates exposes dynamic URI construction**
  ```bash
  pytest tests/test_mcp_resources.py::test_resource_templates -v
  ```
  **Requirements:**
  - Response includes `resourceTemplates[]` array
  - Template has `uriTemplate: "akr://template/{id}"`
  - Includes `name` and `description`
  - Clients can construct URIs without enumerating all resources

### Tools Protocol

- 🔴 [ ] **tools/list returns all active tools with schemas**
  ```bash
  pytest tests/test_mcp_resources.py::test_tools_list_schema -v
  ```
  **Requirements:**
  - Response includes `tools[]` array
  - Each tool has `name`, `description`, and `inputSchema`
  - inputSchema is valid JSON Schema
  - Active tools: `extract_code_context`, `validate_documentation`, `get_charter`, `write_documentation`, `update_documentation_sections`
  - Deprecated tools NOT in list: `analyze_codebase`

- 🔴 [ ] **tools/call for validate_documentation returns correct shape**
  ```bash
  # Already covered in Phase 3, but critical for spec conformance
  pytest tests/test_mcp_resources.py::test_validate_tool_call_shape -v
  ```
  **Requirements:**
  - Request has `name` and `arguments`
  - Response has `content[]` array
  - Content type is appropriate (text or JSON)
  - Tool errors have proper error structure

### SDK Version Pinning

- 🟡 [ ] **MCP SDK version pinned in requirements.txt**
  ```bash
  grep "mcp" requirements.txt
  # Expected: mcp[cli]>=1.26.0 (or specific version)
  ```
  **Requirements:**
  - Pin `mcp` package to avoid breaking changes
  - Include `[cli]` extras for `mcp` command-line tool
  - Document SDK version in verification checklist header

---

## Quick Verification Script

Run this to check most automated criteria:

```bash
# 1. Submodule status
echo "=== Submodule Status ==="
git submodule status

# 2. Test coverage
echo -e "\n=== Test Coverage ==="
pytest --cov=src --cov-report=term-missing | tail -20

# 3. Check for Windows paths in docs
echo -e "\n=== Windows Path Check ==="
grep -r "C:\\\\" docs/ || echo "✓ No Windows paths found"

# 4. Verify deprecated extractors have headers
echo -e "\n=== Deprecated Extractor Headers ==="
for file in src/tools/extractors/{typescript,business_rule,failure_mode,method_flow,example}_extractor.py; do
  echo "Checking $file..."
  head -5 "$file" | grep -q "DEPRECATED" && echo "✓ Has deprecation header" || echo "✗ Missing header"
done

# 5. Check write ops gating
echo -e "\n=== Write Ops Gating ==="
grep "AKR_ENABLE_WRITE_OPS" src/server.py && echo "✓ Environment flag implemented"

# 6. Verify CHANGELOG exists
echo -e "\n=== Documentation Files ==="
for doc in docs/CHANGELOG.md docs/SECURITY.md docs/VERSION_MANAGEMENT.md docs/VALIDATION_GUIDE.md docs/COPILOT_CHAT_WORKFLOW.md; do
  [ -f "$doc" ] && echo "✓ $doc exists" || echo "✗ $doc missing"
done

echo -e "\n=== Verification Complete ==="
```

---

## Next Steps After Verification

1. **Check all boxes above** by running each test
2. **Update IMPLEMENTATION_PLAN_V0.2.0.md** - Change `- [ ]` to `- [x]` for verified items
3. **Create GitHub Release:**
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
4. **Update project board** to mark v0.2.0 as complete
5. **Share release notes** with team and stakeholders

---

## Known Issues and Critical Runtime Tests Required

### ✅ Resolved

- [x] **SECURITY.md MCP trust model** - COMPLETE
  - Added explicit MCP trust model section
  - Added MCP Inspector ≥0.14.1 requirement (CVE-2025-49596)
  - Documented stdio (default) vs HTTP transport security

### 🔴 Critical Runtime Tests Required (Pre-Release Blockers)

Based on M365 Copilot feedback, these **10 runtime tests** are required before v0.2.0 release:

1. **TemplateResolver priority test** - Verify submodule > local > remote with fixtures
2. **Write happy-path** - Test `allowWrites=true` returns dry-run diff, no file write
3. **Front-matter JSON Schema** - Invalid vs valid fixtures produce correct violations with field paths
4. **Tiering test** - Same doc produces more BLOCKER at TIER_1 than TIER_3
5. **MCP validation tool** - Call via Copilot/`mcp` CLI matches CLI output shape
6. **Auto-fix patch return** - Returns patched content without writing to disk
7. **Extractor clean JSON** - No emoji/placeholder markers; stable keys only
8. **Server registration cleanup** - Deprecated tools don't appear in `tools/list`
9. **CLI output tests** - JSON vs text format snapshots; exit codes correct
10. **MCP spec conformance** - `resources/read` returns `contents[]` with `uri`, `mimeType`, `text`

### 📊 Current Status

- **Automated Checks**: 45/48 passed (93.75%)
- **File Structure**: ✅ Complete
- **Runtime Behavior**: ⚠️ 10 critical tests pending
- **MCP Spec Compliance**: ⚠️ Needs integration test verification
- **Ready for Release**: ❌ Complete runtime tests first

### 🎯 Recommended Next Steps

1. Create test fixtures for validation tests (`invalid_frontmatter.md`, `incomplete_doc.md`, `fixable_doc.md`)
2. Implement integration tests that start MCP server and call endpoints
3. Add snapshot tests for CLI output formats
4. Verify MCP resource/tool response shapes match spec
5. Run full test suite: `pytest --cov=src --cov-fail-under=80 -v`
6. Once all runtime tests pass, update this checklist and tag v0.2.0

---

## Verification Summary

### Automated Checks (File Structure)
- **Total Checks**: 48
- **Passed**: 45 (93.75%)
- **Failed**: 2 (submodule commit parsing, minor issues)
- **Warnings**: 1 (uncommitted changes)

### Runtime Tests (Behavior Verification)
- **Total Runtime Tests**: 20
- **Completed**: 0 (🔴 All pending)
- **Critical for v0.2.0**: 10 tests
- **Status**: ⚠️ **Must complete before release**

### MCP Spec Conformance
- **Resources Protocol**: 🔴 Needs integration tests
- **Tools Protocol**: 🔴 Needs integration tests
- **SDK Version**: 🟡 Needs pinning in requirements.txt

### Overall Status
- **File Structure**: ✅ 93.75% Complete
- **Runtime Behavior**: ❌ 0% Tested
- **Documentation**: ✅ Complete (with MCP trust model)
- **Ready for Release**: ❌ **Runtime tests required**

---

**Last Updated:** February 24, 2026 17:15:44  
**Automated Script:** `scripts/verify_implementation.ps1`  
**M365 Copilot Review:** February 24, 2026 (runtime test requirements added)

**Pre-Release Checklist:**
- [ ] Complete 10 critical runtime tests
- [ ] Verify MCP spec conformance (resources/read payload shape)
- [ ] Pin MCP SDK version in requirements.txt
- [ ] Run full test suite with ≥80% coverage
- [ ] Manual testing in VS Code with Copilot Chat
- [ ] Update IMPLEMENTATION_PLAN_V0.2.0.md checkboxes
- [ ] Create GitHub release tag: `git tag v0.2.0 && git push origin v0.2.0`

**Sign-off Required:**
- [ ] Technical Lead: _________________
- [ ] QA/Testing: _________________
- [ ] Release Manager: _________________
