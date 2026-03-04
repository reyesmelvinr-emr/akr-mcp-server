# Phase 1: Foundation — Implementation Plan

**Duration:** 3-5 weeks  
**Team:** Standards team (1-2 FTE)  
**Prerequisite:** Phase 0 complete; all pre-pilot tests PASS or have fallback  
**Target:** `core-akr-templates` v1.0.0 release tag

---

## Overview

Phase 1 delivers production-ready infrastructure: module-aware templates, a complete validation script, CI workflows, and schema definitions. This phase establishes the foundation that all subsequent phases depend on—no pilot onboarding can begin until v1.0.0 is tagged and released.

**Critical Path:** `validate_documentation.py` → CI workflow adaptation → template adaptation → v1.0.0 release

---

## Acceptance Criteria

Phase 1 is complete when:

1. ✅ `validate_documentation.py` v1.0 authored (~500-650 lines); all tests passing
2. ✅ CI workflow adapted (8 targeted changes); **broken download URL fixed and verified working**; validates module docs without false positives
3. ✅ 2 templates adapted for module architecture; acceptance criterion passed
4. ✅ `copilot-instructions.md` rewritten with module-centric logic; **Copilot session test passed against CourseDomain example**
5. ✅ `modules-schema.json` authored with complete validation rules
6. ✅ `akr-config-schema.json` updated with `project_type` in required tags and `businessCapability` support; `priorityFilter` passthrough stub added
7. ✅ HITL alignment documented; `humanInput` role mapping complete
8. ✅ Full-Stack layer enum divergence documented in CHANGELOG/schema README
9. ✅ `standard_service_template.md` and `minimal_service_template.md` consolidated or explicitly deferred (owned)
10. ✅ Governance policies documented (compliance mode graduation, TEMPLATE_MANIFEST narrowing)
11. ✅ Cross-platform testing passed (Ubuntu, macOS, Windows)
12. ✅ Migration inventory from Phase 0 resolved (all `.akr/` path references documented or closed)
13. ✅ `core-akr-templates` v1.0.0 tagged and release notes published

**Exit Gate:** All items above checked; Phase 1 retrospective complete; Phase 2 pilot onboarding authorized.

---

## Deliverable 1: `validate_documentation.py` v1.0

### Objective

Create validation script from scratch that distinguishes module docs from database object docs and applies correct section rules per document type.

### Why "From Scratch"

**Critical finding from analysis:** The script does not exist in the repository. The workflow at `.akr/workflows/validate-documentation.yml` attempts to download it from a URL that returns 404. This is not an adaptation task—it is a net-new build.

### Scope

**Realistic estimate:** 500-650 lines with explicit `pyyaml` dependency

**What v1.0 MUST do:**

1. **Module-type-aware validation**
   - Check if `modules.yaml` exists in project root
   - If absent: warn and apply generic rules only (do not fail hard)
   - If present: load and determine doc type for each file being validated
   
2. **Doc type classification**
   ```
   IF file path matches modules[].doc_output → type = MODULE
   IF file path matches database_objects[].doc_output → type = DB_OBJECT
   ELSE → type = UNKNOWN
   ```

3. **modules.yaml schema validation** (9 rules from Part 6 of analysis)
   - `project.layer` in allowed enum
   - `project.standards_version >= minimum_standards_version`
   - `modules[].project_type` in allowed values
  - `modules[].businessCapability` exists in `tag-registry.json` (PascalCase match)
     **Lookup path:** Check submodule first (`core-akr-templates/tag-registry.json`), fallback to `tag-registry.json` in project root if submodule unavailable, fail if neither exists
   - `modules[].files` count ≤ `max_files`
   - No duplicate `doc_output` paths
   - `database_objects[].type` in allowed enum
   - `project.compliance_mode` in {pilot, production}

4. **Section rules by doc type**
   
   **MODULE docs require:**
   - Module Files (list all files with roles)
   - Operations Map (all operations across all files)
   - Architecture Overview (full-stack text diagram)
   - Business Rules (with "Why It Exists" + "Since When" columns)
   - Data Operations (all reads and writes)
  - YAML front matter: `businessCapability`, `feature` (work-item), `layer`, `project_type`, `status`
   
   **DB_OBJECT docs require:**
   - Object Definition (schema, columns/parameters)
   - Relationships and Dependencies
   - Usage Patterns
   - YAML front matter: `object_type`, `source`
   
   **UNKNOWN docs:**
   - Apply generic required sections from `lean_baseline_service_template.md`
   - Warn that doc is not registered in `modules.yaml`

5. **Transparency marker checks**
   - Count unresolved `❓` markers
   - Fail on `❓` if `compliance_mode = production`
   - Warn on `❓` if `compliance_mode = pilot`
   - `DEFERRED` markers with justification text → always pass
   - `🤖` markers → informational only

6. **--fail-on logic**
   ```
   --fail-on=never  → exit 0 always; emit warnings to stdout
   --fail-on=needs  → exit 1 on unresolved ❓ in production mode; else exit 0
   --fail-on=all    → exit 1 on any validation failure
   ```

7. **Structured output**
   - JSON format with `.summary.total_errors`, `.summary.total_warnings`, `.summary.average_completeness`
  - Results include `.results[].issues[].line` and `.results[].completeness_score`
   - These exact field names required for CI workflow compatibility
   - PASS/FAIL/WARN per check
   - Summary count
  - List of specific failures with line references

8. **--changed-files support (workflow compatibility)**
  - Reads changed files list from environment (compatible with `tj-actions/changed-files`)
  - Applies validation to all changed docs

9. **--output flag**
  - `--output json` writes JSON to stdout with workflow-compatible fields
  - `--output text` writes human-readable summary

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Implement core validation engine | Standards author | Reads `modules.yaml`, classifies doc types, applies section rules | Days 1-2 (16 hours) |
| Implement `modules.yaml` schema validation | Standards author | All 9 validation rules working; enum checks against schema files | Day 2 (4 hours) |
| Implement transparency marker logic | Standards author | `❓` / `🤖` / `DEFERRED` detection; compliance mode enforcement | Day 3 (4 hours) |
| Implement `--fail-on` flag behavior | Standards author | Three modes working as specified | Day 3 (2 hours) |
| Implement JSON output with exact field names | Standards author | `.summary.total_errors`, etc. match existing CI workflow expectations | Day 3 (2 hours) |
| Implement fallback mode (modules.yaml absent) | Standards author | Warns and applies generic rules; does not fail hard | Day 4 (2 hours) |
| Write unit tests | Standards author | Port assertions from `test_validation_library.py`; ≥85% coverage | Day 4-5 (8 hours) |
| Test cross-platform | Standards author | Ubuntu (GitHub Actions), macOS, Windows PowerShell | Day 5 (3 hours) |
| Document CLI usage | Standards author | `--file`, `--changed-files`, `--module-name`, `--fail-on`, `--output` flags documented in README | Day 5 (1 hour) |

### Test Cases (Port from `test_validation_library.py`)

```python
def test_module_doc_all_sections_present():
    # Module doc with all MODULE-required sections → PASS
    
def test_module_doc_missing_operations_map():
    # Module doc missing Operations Map → FAIL with correct message
    
def test_module_doc_unresolved_question_marks_production():
    # Module doc with unresolved ❓ in production mode → FAIL
    
def test_db_object_doc_missing_relationships():
    # DB object doc missing Relationships section → FAIL
    
def test_modules_yaml_exceeds_max_files():
    # modules.yaml with module exceeding max_files → FAIL
    
def test_modules_yaml_unknown_project_type():
    # modules.yaml with unknown project_type → FAIL with enum error
    
def test_modules_yaml_absent():
    # Project without modules.yaml → WARN, do not fail
```

### Dependencies

- **Python 3.9+**
- **pyyaml** (explicit; add to `requirements.txt`)
- **Vale** (subprocess call; installed separately in CI)

### Output Location

```
core-akr-templates/
  .akr/
    scripts/                      (NEW directory — must be created)
      validate_documentation.py   (~500-650 lines; NEW)
```

**Note:** The `.akr/scripts/` directory does not currently exist in `core-akr-templates`. Creating this directory and committing the script is part of this deliverable.

### Risk Mitigation

| Risk | Mitigation |
|---|---|---|
| 500-650 lines exceeds capacity for standards team | Prioritize critical path; defer `--auto-fix` and `--tier` scoring to v1.1 |
| YAML parsing breaks on Windows paths | Test with Windows-style paths in unit tests; use `pathlib.Path` for normalization |
| Vale subprocess integration issues | Run Vale as separate CI step in v1.0; tight integration in v1.1 |

---

## Deliverable 2: CI Workflow Adaptation

### Objective

Adapt existing `.akr/workflows/validate-documentation.yml` to work with new `validate_documentation.py` script; **fix broken download URL as FIRST critical task**.

### ⚠️ CRITICAL: Broken Download URL

**Issue:** The workflow currently attempts to download `validate_documentation.py` from a URL that returns 404. This blocks all Phase 2 pilot CI runs.

**Status:** Current broken URL in `.akr/workflows/validate-documentation.yml`:
```
https://raw.githubusercontent.com/reyesmelvinr-emr/core-akr-templates/main/scripts/validate_documentation.py
```

**Correct URL (after v1.0 implementation):**
```
https://raw.githubusercontent.com/reyesmelvinr-emr/core-akr-templates/main/.akr/scripts/validate_documentation.py
```

**Action:** Change 2 (below) includes this URL fix. It must be completed **immediately after** `validate_documentation.py` is committed to the repository, before any Phase 2 pilot project attempts to run CI.

### Context

**From analysis:** This workflow already exists and already attempts to call `validate_documentation.py`. It is not a rebuild—it is an adaptation with 8 targeted changes plus compatibility verification.

**Current workflow capabilities:**
- Downloads `validate_documentation.py` from remote URL (currently 404—**must fix before Phase 2**)
- Installs Vale v2.29.0
- Runs changed-files detection (`tj-actions/changed-files@v41`)
- Has Checks API permissions configured
- Runs Vale with `.akr/.vale.ini` config

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| **Change 1:** Add `pyyaml` to pip install step | Standards author | `pip install --no-cache-dir requests pyyaml` | 5 min |
| **Change 2:** Fix script download URL | Standards author | URL updated to `.akr/scripts/validate_documentation.py` (not `/scripts/`) | 5 min |
| **Change 3:** Add `modules.yaml` to paths trigger | Standards author | Trigger includes `modules.yaml` alongside `docs/**`, `src/**` | 5 min |
| **Change 4:** Add `--module-name` and `--changed-files` support | Standards author | Workflow passes module name and changed-files mode | 10 min |
| **Change 5:** Update Vale config path | Standards author | Change from `.akr/.vale.ini` to `validation/.vale.ini` (after directory migration) | 5 min |
| **Change 6:** Remove or replace `validate_traceability.py` download | Standards author | No downloads from `akr-mcp-server` remain | 10 min |
| **Change 7:** Remove or replace `analyze_doc_impact.py` download | Standards author | No downloads from `akr-mcp-server` remain | 10 min |
| **Change 8:** Remove MCP branding from PR comment footer | Standards author | Footer does not mention MCP server | 5 min |
| **Verification:** Confirm JSON output compatibility | Standards author | Workflow's `jq` queries work with v1.0 output schema | 30 min |
| **Verification:** Update action versions and changed-files action | Standards author | `actions/checkout@v4`, `actions/setup-python@v5`, `tj-actions/changed-files@v44` or latest | 15 min |
| Test workflow on draft PR | Standards author | Workflow runs successfully; validation results appear in PR checks | 1 hour |
| Document workflow customization | Standards author | README explains how projects adapt workflow for their structure | 1 hour |

### Change Details

#### Change 1: Add pyyaml Dependency

```yaml
# BEFORE
- name: Install dependencies
  run: pip install --no-cache-dir requests

# AFTER
- name: Install dependencies
  run: pip install --no-cache-dir requests pyyaml
```

#### Change 2: Fix Download URL

```yaml
# BEFORE (404 error)
- name: Download validation script
  run: |
    curl -o validate_documentation.py \
      https://raw.githubusercontent.com/reyesmelvinr-emr/core-akr-templates/main/scripts/validate_documentation.py

# AFTER (correct path)
- name: Download validation script
  run: |
    curl -o validate_documentation.py \
      https://raw.githubusercontent.com/reyesmelvinr-emr/core-akr-templates/main/.akr/scripts/validate_documentation.py
```

#### Change 3: Add modules.yaml to Trigger

```yaml
# BEFORE
paths:
  - 'docs/**'
  - 'src/**'
  - '.akr-config.json'

# AFTER
paths:
  - 'docs/**'
  - 'src/**'
  - '.akr-config.json'
  - 'modules.yaml'
```

#### Change 4: Add --module-name and --changed-files Support

```yaml
# NEW step after changed-files detection
- name: Run AKR validation
  run: |
    python validate_documentation.py \
      --changed-files \
      --output json \
      --fail-on needs
```

**`--changed-files` Contract:**  
Reads space-separated file paths compatible with `tj-actions/changed-files@v41` output format. The script must split on whitespace and process each path as workspace-relative. Example workflow integration:

```yaml
- name: Get changed files
  id: changed-files
  uses: tj-actions/changed-files@v41
  with:
    files: 'docs/**/*.md'
    
- name: Validate changed docs
  run: |
    python validate_documentation.py \
      --changed-files "${{ steps.changed-files.outputs.all_changed_files }}" \
      --output json \
      --fail-on needs
```

#### Change 5: Update Vale Config Path

```yaml
# BEFORE
- name: Run Vale
  uses: errata-ai/vale-action@v2
  with:
    config: .akr/.vale.ini

# AFTER
- name: Run Vale
  uses: errata-ai/vale-action@v2
  with:
    config: validation/.vale.ini
```

#### Vale Rules Migration (Required)

- Move `.akr/vale-rules/` to `validation/vale-rules/`.
- Audit all rule files for hardcoded paths.
- Update `.vale.ini` `StylesPath` to `validation/vale-rules`.
- Add a CI check that fails when `StylesPath` is missing.

#### Change 6: Remove Traceability Download

- Remove step that downloads `validate_traceability.py` from `akr-mcp-server`.
- If traceability is required in v1.0, host the script in `core-akr-templates` and update URL.

#### Change 7: Remove Impact Analysis Download

- Remove step that downloads `analyze_doc_impact.py` from `akr-mcp-server`.
- If impact analysis is required, migrate the script to `core-akr-templates` first.

#### Change 8: Remove MCP Branding

- Remove or replace `<sub>Powered by AKR MCP Documentation Server</sub>` in PR comments.

#### Verification: JSON Output Compatibility

**Existing workflow expects these fields:**
```bash
jq -r '.summary.total_errors' validation_results.json
jq -r '.summary.total_warnings' validation_results.json
jq -r '.summary.average_completeness' validation_results.json
```

**v1.0 must output exactly:**
```json
{
  "summary": {
    "total_errors": 0,
    "total_warnings": 2,
    "average_completeness": 0.87
  },
  "results": [ ... ]
}
```

### Output Locations

```
core-akr-templates/
  .akr/
    workflows/
      validate-documentation.yml   (ADAPTED; 8 changes)
  examples/
    workflows/
      validate-documentation.yml   (Copy for projects to deploy)
```

---

## Deliverable 3: Template Adaptation

### Objective

Adapt `lean_baseline_service_template.md` and `ui_component_template.md` for module-scope documentation; retain database templates as-is.

### Acceptance Criterion

**Critical:** Adapted `lean_baseline_service_template.md` must produce output matching `courses_service_doc.md` structure when used on CourseDomain module (Controller + Service + Repository + DTOs).

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Adapt `lean_baseline_service_template.md` | Standards author | Module Files, Operations Map, full-stack diagram sections added | 4 hours |
| Adapt `ui_component_template.md` | Standards author | Module Files, component hierarchy diagram sections added | 3 hours |
| Add module-scope YAML front matter | Standards author | `businessCapability`, `feature`, `layer`, `project_type`, `status` fields documented | 1 hour |
| **Update all YAML front matter examples to PascalCase** | Standards author | All `businessCapability` examples use PascalCase matching `tag-registry.json` (e.g., `CourseCatalogManagement` not `course-catalogmanagement`) | 1 hour |
| Test backend template on CourseDomain | Standards author | Output matches `courses_service_doc.md` structure | 2 hours |
| Test UI template on sample UI module | Standards author | Component grouping logic works; hierarchy clear | 2 hours |
| **Consolidate template variants** | Standards author | `standard_service_template.md` and `minimal_service_template.md` reviewed and consolidated into `lean_baseline` module variant; OR explicitly deferred with owner assigned to a later phase | 2 hours |
| Document template selection logic | Standards author | `project_type` → template mapping table in README | 1 hour |

**Critical:** YAML front matter `businessCapability` values must use PascalCase (e.g., `CourseCatalogManagement`) to match `tag-registry.json` keys. Otherwise Phase 4's `consolidate.py` will fail to match module docs by feature tag.

### Module Variant Additions (Backend)

**New sections for `lean_baseline_service_template.md` module variant:**

1. **Module Files** (after Service Identification)
   ```markdown
   ## Module Files
   
   | File | Role | Primary Responsibilities |
   |------|------|-------------------------|
   | [file path] | Controller / Service / Repository / DTO | [brief description] |
   ```
   
2. **Operations Map** (consolidates all component operations)
   ```markdown
   ## Operations Map
   
   This section covers ALL operations across ALL files in the module.
   
   ### Public Operations
   | Operation | File | Parameters | Returns | Business Purpose |
   |-----------|------|------------|---------|-----------------|
   ```

3. **Architecture Overview** (full-stack text diagram)
   ```markdown
   ## Architecture Overview
   
   Text-based architecture showing full stack:
   Controller → Service (interface) → Service (implementation) → Repository (interface) → EF Repository → Database Table
   
   [No Mermaid; plain text with → arrows and indentation]
   ```

4. **Business Rules** (enhanced table)
   ```markdown
   ## Business Rules
   
   | Rule | Why It Exists | Since When | Where Enforced |
   |------|---------------|------------|----------------|
   ```

5. **Module-scope YAML front matter**
   ```yaml
   ---
  businessCapability: CourseCatalogManagement
  feature: FN12345_US678
   layer: API
   project_type: api-backend
   status: draft
   compliance_mode: pilot
   ---
   ```

### Module Variant Additions (UI)

**New sections for `ui_component_template.md` module variant:**

1. **Module Files** (after Component Identification)
2. **Component Hierarchy Diagram** (text-based)
   ```
   CoursePage (container)
   ├── CourseList (presentation)
   │   └── CourseCard (presentation)
   ├── CourseForm (form)
   └── useCourseData (hook)
   ```
3. **Hook Dependency Graph** (which hooks call which)
4. **Type Definitions Cross-Reference** (interfaces and types)

### Template Selection Table

| `project_type` | Base Template | Notes |
|---|---|---|
| `api-backend` | `lean_baseline_service_template.md` (module variant) | Covers Controller + Service + Repository + DTOs |
| `ui-component` | `ui_component_template.md` (module variant) | Covers Page + sub-components + hooks + types |
| `microservice` | `lean_baseline_service_template.md` (module variant) | Service-to-service; no controller layer |
| `general` | `lean_baseline_service_template.md` | Fallback |
| `table` | `table_doc_template.md` | Individual object; no grouping |
| `view` | `table_doc_template.md` | Individual object |
| `procedure` | `embedded_database_template.md` | Individual object |

### Output Locations

```
core-akr-templates/
  templates/
    lean_baseline_service_template_module.md   (NEW variant)
    ui_component_template_module.md            (NEW variant)
    table_doc_template.md                      (RETAIN as-is)
    embedded_database_template.md              (RETAIN as-is)
```

---

## Deliverable 4: `copilot-instructions.md` Rewrite

### Objective

Full document replacement with module-centric template selection logic; remove all MCP server references.

### Why "Full Replacement"

**From analysis:** Direct file inspection confirms ~90% of current content is MCP-server-specific and broken after archive. This is not a text update—it is a conceptual rewrite.

**Estimated effort:** 3-4 hours of focused authoring

### What Must Be REMOVED Entirely

1. **Slash-Commands section** (~52 lines) — every command is an MCP server invocation
2. **Code Analysis Capabilities section** — instructs Copilot to use Tree-sitter AST parsing
3. **Repository Structure Requirements** — references broken paths
4. **YAML front matter example** — uses fields not in `modules.yaml` schema
5. **Template selection logic** — file-centric (structurally wrong)
6. **Support and Troubleshooting section** — references `.vscode/mcp.json`, old script names

### What Must Be RETAINED (3 Elements)

1. **Core Principles section** — transparency markers with updated semantics
2. **Completeness scoring formula** — retain as-is
3. **Vale quality gates reference** — update path to `validation/.vale.ini`

### What Must Be ADDED (New Content)

1. **Module grouping principles**
   - Domain noun identification
   - Dependency graph following
   - DTO alignment
   - Interface/implementation pairs
   
2. **Template selection table** (from Deliverable 3)
   
3. **`project_type` → condensed charter → template mapping**

4. **Two-mode Agent Skill invocation guidance**
   - When to use Mode A (grouping proposal)
   - When to use Mode B (documentation generation)
   
5. **`modules.yaml` front matter field reference**

### Target Document Length

**150-200 lines** (vs. current verbose file)

Goal: concise Copilot-native reference that a developer reads once during onboarding

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Remove MCP-specific sections | Standards author | 6 sections removed cleanly | 1 hour |
| Author module grouping principles | Standards author | Domain noun, dependency graph, DTO alignment, interface/impl pairs documented | 1 hour |
| Add template selection table | Standards author | All 7 `project_type` values mapped to templates | 30 min |
| Add Agent Skill invocation guidance | Standards author | Mode A vs. Mode B triggers clear | 1 hour |
| Add `modules.yaml` front matter reference | Standards author | Required fields per doc type documented | 30 min |
| Validate document length | Standards author | ≤200 lines; concise and scannable | 15 min |
| **Test copilot-instructions.md with Copilot** | Pilot rep | Run CourseDomain example against rewritten instructions; verify module boundaries identified correctly in Copilot session | 1 hour |
| Test with Copilot in VS Code | Pilot rep | Instructions load correctly; no broken references | 30 min |

### Output Location

```
core-akr-templates/
  .akr/
    standards/
      copilot-instructions.md   (REPLACED; canonical source)

Per-project deployment:
  .github/
    copilot-instructions.md     (copy of canonical source or condensed charter fallback)
```

---

## Deliverable 6.5: Migration Inventory Resolution (From Phase 0)

### Objective

Resolve findings from Phase 0 infrastructure audit: all `.akr/` path references documented or closed.

### Context

Phase 0 included a task: "Run `git grep -l '.akr/'` to find all references across CI/CD configs, scripts, and `.gitmodules`." The inventory was created but no task consumed its findings. Phase 1 must close this loop.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Review migration inventory from Phase 0 | Standards author | List all `.akr/` references found in grep output | 30 min |
| Resolve all external references | Standards author | Each reference either: (a) updated to new `.akr/` structure, (b) documented as no-longer-valid, or (c) deleted | 2 hours |
| Update `.gitmodules` (if present) | Standards author | No references to `akr-mcp-server` submodule; confirm `core-akr-templates` pinned at v1.0.0 | 30 min |
| Document resolution in CHANGELOG | Standards author | Entry listing all path changes and corrections | 1 hour |

### Output

Phase 1 completion checklist: "Migration inventory fully resolved; zero open `.akr/` path questions"

### Objective

Author new `modules-schema.json`; update `akr-config-schema.json` for `project_type` in required tags.

### `modules-schema.json` (NEW)

**Why needed:** Does not exist in repository; `validate_documentation.py` cannot reference schemas until this exists.

**Critical note:** `modules-schema.json` `project_type` enum **MUST include `Full-Stack`** for parity with `akr-config-schema.json` `projectInfo.layer`. This is intentionally different from `tag-registry-schema.json` and `consolidation-config-schema.json` which omit `Full-Stack` for governance reasons. The layer enums serve different purposes:
- `modules-schema.json` (module taxonomy): includes `Full-Stack`
- `tag-registry-schema.json` (business capability governance): excludes `Full-Stack`
- `consolidation-config-schema.json` (cross-repo aggregation): excludes `Full-Stack`

**Scope:** Define complete `modules.yaml` schema per Part 4 of analysis document.

#### Schema Structure

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AKR Module Manifest Schema",
  "description": "Defines module groupings and database objects for AKR documentation",
  "type": "object",
  "required": ["project", "modules"],
  "properties": {
    "project": {
      "type": "object",
      "required": ["name", "layer", "standards_version", "minimum_standards_version", "compliance_mode"],
      "properties": {
        "name": { "type": "string" },
        "layer": {
          "type": "string",
          "enum": ["UI", "API", "Database", "Integration", "Infrastructure", "Full-Stack"]
        },
        "standards_version": { "type": "string", "pattern": "^v\\d+\\.\\d+\\.\\d+$" },
        "minimum_standards_version": { "type": "string", "pattern": "^v\\d+\\.\\d+\\.\\d+$" },
        "compliance_mode": {
          "type": "string",
          "enum": ["pilot", "production"]
        }
      }
    },
    "modules": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "project_type", "businessCapability", "domain", "layer", "files", "doc_output", "status"],
        "properties": {
          "name": { "type": "string", "pattern": "^[A-Z][a-zA-Z0-9]*$" },
          "project_type": {
            "type": "string",
            "enum": ["api-backend", "ui-component", "microservice", "general"]
          },
          "businessCapability": { "type": "string", "pattern": "^[A-Z][a-zA-Z0-9]*$" },
          "domain": { "type": "string" },
          "layer": { "type": "string" },
          "max_files": { "type": "integer", "default": 8, "maximum": 8 },
          "files": {
            "type": "array",
            "items": { "type": "string" },
            "maxItems": 8
          },
          "doc_output": { "type": "string" },
          "status": {
            "type": "string",
            "enum": ["draft", "review", "approved", "deprecated"]
          },
          "compliance_mode": {
            "type": "string",
            "enum": ["pilot", "production"]
          }
        }
      }
    },
    "database_objects": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "type", "source", "doc_output", "status"],
        "properties": {
          "name": { "type": "string" },
          "type": {
            "type": "string",
            "enum": ["table", "view", "procedure", "function"]
          },
          "source": {
            "type": "string",
            "enum": ["ssdt", "script", "manual"]
          },
          "businessCapability": { "type": "string", "pattern": "^[A-Z][a-zA-Z0-9]*$" },
          "doc_output": { "type": "string" },
          "status": {
            "type": "string",
            "enum": ["draft", "review", "approved", "deprecated"]
          }
        }
      }
    },
    "unassigned": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["path", "reason"],
        "properties": {
          "path": { "type": "string" },
          "reason": { "type": "string" }
        }
      }
    }
  }
}
```

### `akr-config-schema.json` Update

**Change:** Add `project_type` and `businessCapability` to `validation.tagValidation.requiredTags`

```json
// BEFORE
"requiredTags": {
  "type": "array",
  "default": ["feature", "domain", "layer"]
}

// AFTER
"requiredTags": {
  "type": "array",
  "default": ["businessCapability", "feature", "domain", "layer", "project_type"],
  "description": "businessCapability and project_type are conditionally required for MODULE-type documents only"
}
```

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Add `modules-schema.json` | Standards author | Complete schema per Part 4 specification | 3 hours |
| Update `akr-config-schema.json` | Standards author | `project_type` added to `requiredTags`; conditionality documented; `priorityFilter` passthrough field added (v1.1 hook) | 1.5 hours |
| **Document Full-Stack layer divergence** | Standards author | CHANGELOG entry explaining intentional exclusion of `Full-Stack` from `tag-registry-schema.json` and retention in `modules-schema.json`; cross-reference in schema README | 1 hour |
| Update `tag-registry-schema.json` layers | Standards author | Decide whether to add `Full-Stack` or document exclusion | 1 hour |
| Validate schemas with test YAML | Standards author | Example `modules.yaml` validates without errors | 1 hour |
| Document schema versioning | Standards author | Schema version tied to `core-akr-templates` release tag | 30 min |

### Output Locations

```
core-akr-templates/
  .akr/
    schemas/
      modules-schema.json         (NEW)
      akr-config-schema.json      (UPDATED)
      tag-registry-schema.json    (UPDATED if `Full-Stack` inclusion decided)
      consolidation-config-schema.json  (existing; Phase 4 changes)
```

---

## Deliverable 6: HITL Alignment

### Objective

Cross-reference `akr-config-schema.json` `humanInput.defaultRole` enum against template "who provides it" columns.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Document role mapping | Standards author | Table mapping `defaultRole` values to HITL levels | 2 hours |
| Update template "who provides it" columns | Standards author | Templates use consistent role vocabulary | 2 hours |
| Plan `priorityFilter` integration | Standards author | Design how `validate_documentation.py` v1.1 reads `priorityFilter` to distinguish blocking vs. advisory `❓` | 1 hour |

### Role Mapping Table

| `humanInput.defaultRole` | HITL Level | Responsibility |
|---|---|---|
| `technical_lead` | Level 1 + Level 2 architecture | Grouping validation; architecture diagram review |
| `developer` | Level 2 content | Fills `❓` sections; validates business rules |
| `product_owner` | Phase 4 consolidation | Narrative refinement on feature docs |
| `qa_tester` | Phase 3+ (conditional) | Copilot Studio Teams approval gate |

### Future Integration (v1.1)

```python
# validate_documentation.py v1.1 (DEFERRED)
def check_question_markers(doc, config):
    priority_filter = config.get("humanInput", {}).get("priorityFilter", "important")
    
    if priority_filter == "critical":
        # Only fail on ❓ markers tagged as [CRITICAL]
    elif priority_filter == "important":
        # Fail on all unresolved ❓ markers (current v1.0 behavior)
    elif priority_filter == "optional":
        # Warn only; do not fail
```

### Output

Documentation in `DEVELOPER_REFERENCE.md` section on HITL model alignment.

---

## Deliverable 7: Governance Policies

### Objective

Document compliance mode graduation criteria and `TEMPLATE_MANIFEST.json` narrowing.

### Compliance Mode Graduation

**Trigger:** Zero unresolved `❓` markers in production for 4 consecutive weeks

**Process:**
1. Standards team reviews validation logs
2. Confirms no bypass events occurred
3. Tech lead sign-off
4. Update project's `modules.yaml`: `compliance_mode: pilot → production`
5. CHANGELOG entry with date and approver

### `TEMPLATE_MANIFEST.json` Narrowing

**Retain:**
- `templateId → version` mapping
- CI check that Agent Skill references valid `templateId` values

**Deprecate (document in CHANGELOG):**
- Template selection logic (moved to Agent Skill)
- Complexity scoring (replaced by `project_type`)
- File-centric routing (replaced by module-centric)

### Tag Registry Feature Entry Requirements

**Document:** New entries to `tag-registry.json` require:
- `approved`: boolean
- `domain`: string
- `description`: string
- `owner`: string
- `status`: enum {active, deprecated}
- **Optional:** `synonyms`, `relatedFeatures`, `addedDate`

**Validation:** Entries must match `tag-registry-schema.json` `patternProperties` regex (`^[A-Z][a-zA-Z0-9]*$`)

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Document compliance mode graduation | Standards author | Process documented in `VALIDATION_GUIDE.md`; includes emergency rollback procedure (--fail-on=never usage, authority requirements, hotfix SLA, org-wide disable mechanism) | 1.5 hours |
| Document `TEMPLATE_MANIFEST.json` narrowing | Standards author | CHANGELOG entry; deprecated roles listed | 1 hour |
| Document tag registry requirements | Standards author | New entry requirements in `TAG_REGISTRY_GUIDE.md` | 1 hour |
| Implement CI check for templateId validity | Standards author | Workflow step validates Agent Skill references | 2 hours |

---

## Deliverable 8: Cross-Platform Testing

### Objective

Validate `validate_documentation.py` works on Ubuntu (GitHub Actions), macOS, Windows PowerShell.

### Test Matrix

| Platform | Python Version | YAML Library | Result |
|---|---|---|---|
| Ubuntu 22.04 (GitHub Actions) | 3.9 | pyyaml 6.0 | PASS |
| macOS Ventura | 3.10 | pyyaml 6.0 | PASS |
| Windows 11 PowerShell 7 | 3.11 | pyyaml 6.0 | PASS |

### Test Cases

1. **Path normalization:** Windows backslashes vs. Unix forward slashes
2. **YAML parsing:** Line endings (CRLF vs. LF)
3. **File encoding:** UTF-8 with BOM (Windows) vs. UTF-8 without BOM
4. **Vale subprocess:** Vale executable location differs per OS
5. **Exit codes:** Consistent 0/1 behavior across platforms

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Test script on Ubuntu | Standards author | All test cases pass; CI workflow successful | 1 hour |
| Test script on macOS | Standards author | All test cases pass | 1 hour |
| Test script on Windows | Standards author | All test cases pass; PowerShell execution clean | 1 hour |
| Document platform-specific notes | Standards author | README includes OS-specific installation/usage | 30 min |

---

## Deliverable 9: v1.0.0 Release

### Objective

Tag `core-akr-templates` v1.0.0 and publish release notes.

### Release Checklist

- [ ] All Phase 1 deliverables complete
- [ ] `validate_documentation.py` tests passing (≥85% coverage)
- [ ] CI workflow validated on draft PR
- [ ] Templates produce expected output (acceptance criterion passed)
- [ ] `copilot-instructions.md` rewrite complete
- [ ] `modules-schema.json` authored and validated
- [ ] Cross-platform testing passed
- [ ] **`minimum_standards_version` initial value decided** (see Critical Decision below)
- [ ] CHANGELOG updated with breaking changes
- [ ] Migration guide written (`.akr/` → `validation/` paths)
- [ ] Migration guide includes old docs path mapping (`docs/components`, `docs/services`, `docs/architecture` → `docs/modules`, `docs/database`, `docs/features`)
- [ ] Release notes drafted

### Critical Decision: `minimum_standards_version` Initial Value

**Decision required before v1.0.0 release:** Set `minimum_standards_version` in pilot project `modules.yaml`.

**Options:**
- **`v0.0.0` (permissive start):** Allows pilot projects created before v1.0.0 tag to pass validation; provides migration window
- **`v1.0.0` (strict from day one):** Enforces v1.0.0 compliance immediately; any project with `standards_version < v1.0.0` will fail validation

**Recommendation:** `v0.0.0` for pilot projects onboarded during Phase 2. Update to `v1.0.0` after 6-week stability period (before Phase 4). Document this decision in release notes and migration guide.

### Release Notes Structure

```markdown
# core-akr-templates v1.0.0

## Breaking Changes

- Module-based documentation architecture replaces file-centric approach
- `.akr/` paths migrated to `validation/` (except schemas and workflows)
- `modules.yaml` now required for module-type-aware validation
- `copilot-instructions.md` fully rewritten; no backward compatibility

## New Features

- **Module-aware validation:** `validate_documentation.py` distinguishes MODULE vs. DB_OBJECT docs
- **Agent Skill dual-mode:** Mode A (grouping) + Mode B (generation)
- **Condensed charters:** ~22% of original token count; prevents context saturation
- **Schema-driven validation:** `modules-schema.json` defines complete module manifest contract

## Migration Guide

[Link to migration documentation]

## Known Limitations

- Vale integration is via separate CI step (tight integration deferred to v1.1)
- `--auto-fix` mode deferred to v1.1
- Large modules (>8 files) require manual splitting

## Contributors

[Team credits]
```

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Draft release notes | Standards author | All breaking changes documented; migration guide linked | 2 hours |
| Update CHANGELOG | Standards author | v1.0.0 section added with date | 30 min |
| Tag v1.0.0 | Standards lead | Git tag created; GitHub release published | 15 min |
| Announce to team | Standards lead | Teams/Slack announcement with migration timeline | 30 min |

---

## Phase 1 Retrospective

### Retrospective Agenda

1. **Deliverable completion:** Which deliverables exceeded or under-ran time estimates?
2. **Scope creep:** Did any "must-haves" emerge during implementation?
3. **Quality:** Did cross-platform testing uncover unexpected issues?
4. **Team feedback:** Was the 3-5 week estimate realistic?
5. **Phase 2 readiness:** Is v1.0.0 truly pilot-ready?

### Retrospective Outputs

- **Phase 1 completion metrics:** Actual vs. estimated time per deliverable
- **v1.1 backlog:** Features deferred from v1.0 (e.g., `--auto-fix`, tight Vale integration)
- **Phase 2 authorization:** Standards lead sign-off to begin pilot onboarding
- **Lessons learned:** What would we do differently in next major version build?

---

## Risk Register (Phase 1 Specific)

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| `validate_documentation.py` scope exceeds 650 lines | 🟡 Medium | 🟡 Medium | Ruthlessly defer v1.1 features; focus on critical path |
| Template adaptation breaks existing docs | 🟡 Medium | 🟠 Low | Test on `courses_service_doc.md` acceptance criterion early |
| Cross-platform path issues on Windows | 🟡 Medium | 🟠 Low | Use `pathlib.Path` for all file operations; test early |
| CI workflow JSON compatibility breaks | 🔴 High | 🟠 Low | Verify field names match existing `jq` queries before merge |
| v1.0.0 ships with critical bug | 🔴 High | 🟠 Low | Require ≥85% test coverage; manual testing on all 3 platforms |

---

## Success Criteria Summary

Phase 1 succeeds when:

✅ `validate_documentation.py` v1.0: 500-650 lines; all tests passing; cross-platform validated  
✅ CI workflow: 8 changes applied; validates module docs without false positives  
✅ Templates: 2 adapted; acceptance criterion passed (CourseDomain output matches `courses_service_doc.md`)  
✅ `copilot-instructions.md`: Full rewrite complete (~150-200 lines); module-centric logic  
✅ `modules-schema.json`: Complete schema authored; validates example YAML  
✅ `akr-config-schema.json`: `project_type` added to required tags  
✅ HITL alignment: Role mapping documented; templates updated  
✅ Governance policies: Compliance graduation + TEMPLATE_MANIFEST narrowing documented  
✅ Cross-platform: Ubuntu + macOS + Windows all passing  
✅ v1.0.0 release: Tagged, release notes published, team announced  

**Exit gate:** Phase 1 retrospective complete; Phase 2 pilot onboarding authorized by standards lead.

---

**Next Phase:** [Phase 2: Pilot Onboarding](PHASE_2_PILOT_ONBOARDING.md)

**Related Documents:**
- [Phase 0: Prerequisites](PHASE_0_PREREQUISITES.md)
- [Implementation Plan Overview](IMPLEMENTATION_PLAN_OVERVIEW.md)
- [Implementation-Ready Analysis](../akr_implementation_ready_analysis.md) — Parts 2, 6, 7, 12
