# Phase 1: Foundation — Implementation Plan

**Duration:** 3-5 weeks  
**Team:** Standards team (1-2 FTE)  
**Prerequisite:** Phase 0 complete; all pre-pilot tests PASS or have fallback  
**Target:** `core-akr-templates` v1.0.0 release tag

---

## Overview

Phase 1 delivers production-ready infrastructure: module-aware templates, a complete validation script, CI workflows, and schema definitions. This phase establishes the foundation that all subsequent phases depend on—no pilot onboarding can begin until v1.0.0 is tagged and released.

**Critical Path:** `validate_documentation.py` → CI workflow adaptation → skill distribution workflow → template adaptation → v1.0.0 release

---

## Acceptance Criteria

Phase 1 is complete when:

1. ✅ `validate_documentation.py` v1.0 authored (~500-650 lines); all tests passing
2. ✅ CI workflow adapted (9 targeted changes); validates module docs without false positives
3. ✅ 2 templates adapted for module architecture; acceptance criterion passed
4. ✅ `copilot-instructions.md` rewritten with module-centric logic
5. ✅ `modules-schema.json` authored with complete validation rules
6. ✅ `akr-config-schema.json` updated with `project_type` in required tags and `businessCapability` support
7. ✅ HITL alignment documented; `humanInput` role mapping complete
8. ✅ Governance policies documented (compliance mode graduation, TEMPLATE_MANIFEST narrowing)
9. ✅ Cross-platform testing passed (Ubuntu, macOS, Windows)
10. ✅ `core-akr-templates` v1.0.0 tagged and release notes published
11. ✅ Skill distribution workflow (`distribute-skill.yml`) operational for registered repos
12. ✅ `DEVELOPER_REFERENCE.md` created/updated with HITL alignment, role mapping, and three-mode skill guidance
13. ✅ `VALIDATION_GUIDE.md` created/updated with compliance mode graduation and emergency rollback procedure

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
  - YAML front matter: `businessCapability`, `feature` (work-item), `layer`, `project_type`, `status`, `compliance_mode`
  - `<!-- akr-generated -->` metadata header block (presence check; fail with `"AKR metadata header missing — skill may not have been properly invoked"` if absent)
  - SSG metadata validation (when `generation-strategy = section-scoped`):
    - `passes-completed` field present; contains expected pass numbers
      (Note: this is distinct from `steps-completed`, which counts the 9 Mode B workflow steps and remains checked independently. `passes-completed` counts SSG generation passes within Steps 3-4. Both fields must be present when generation-strategy is section-scoped.)
    - `passes-completed` may include override annotations alongside standard pass IDs
      (e.g., `pass4-override`, `pass3-override`). Validator must accept these as valid
      entries and not reject them as non-numeric. Emit INFO:
      "Pass N source re-read override was applied. Verify override is documented
       in modules.yaml notes field."
    - `pass-timings-seconds` field present (value may be "unavailable")
    - `total-generation-seconds` present (value may be "unavailable")
    - `passes-split` field: if present, value must be a valid sub-pass designation
    - `passes-split` and `passes-completed` must be consistent: if `passes-split: 2A,2B`
      then `passes-completed` must contain `2A` and `2B`, not `2`
    - If `generation-strategy: single-pass-fallback`, `passes-completed` records
      passes that ran before fallback (e.g., `passes-completed: 1,2,3`); emit WARNING:
      "Sections generated via fallback strategy. Additional ❓ markers expected.
       Run Mode C to resolve remaining gaps before production compliance."
    - If `generation-strategy: developer-elected-single-pass`, `passes-completed`
      value is `single-pass`; emit INFO (not WARNING):
      "Document generated via developer-elected single-pass. Review thoroughly,
       especially Operations Map and Business Rules on large modules. Consider
       re-running with SSG if module has 5+ files or any file >500 LOC."
      Do NOT count this as a `fallback_strategy_count` event - it is an intentional
      developer choice, not a generation failure.
    - If `total-generation-seconds` > 2700 (45 minutes) and not "unavailable",
      emit WARNING: "Module generation exceeded slow threshold. Consider module
      splitting if this recurs. See CHARTER-RESTORATION-PLAN.md."
    - `steps-completed` check: unchanged from existing validator logic; checked
      independently of SSG fields.
   
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
  - Extended output contract fields for SSG:
    - `.summary.ssg_slow_modules` (array of module names that exceeded threshold)
    - `.summary.ssg_avg_total_seconds` (average across all validated docs in run)
    - `.summary.fallback_strategy_count` (count of docs using single-pass-fallback - system-triggered)
    - `.summary.developer_single_pass_count` (count of docs using developer-elected-single-pass - intentional)
    - `.summary.ssg_pass_overrides` (array of `{module_name, override_field, value}` for any module with non-default override)

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
| Add `pyyaml` to `requirements.txt` | Standards author | `pyyaml` listed as explicit dependency; `pip install -r requirements.txt` installs cleanly on all platforms | 15 min |
| Implement `<!-- akr-generated -->` metadata header check | Standards author | Validator checks for header presence in MODULE docs; fails with exact message: `"AKR metadata header missing — skill may not have been properly invoked"` | 2 hours |

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

Adapt existing `.akr/workflows/validate-documentation.yml` to work with new `validate_documentation.py` script; fix broken download URL.

### Context

**From analysis:** This workflow already exists and already attempts to call `validate_documentation.py`. It is not a rebuild—it is an adaptation with 8 targeted changes plus compatibility verification.

**Current workflow capabilities:**
- Downloads `validate_documentation.py` from remote URL (currently 404—must fix)
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
| **Change 9:** Add SKILL file CODEOWNERS guidance | Standards author | Workflow example/docs include `.github/skills/akr-docs/SKILL.md @org/standards-team` | 10 min |
| **Verification:** Confirm JSON output compatibility | Standards author | Workflow's `jq` queries work with v1.0 output schema | 30 min |
| **Verification:** Update action versions and changed-files action | Standards author | `actions/checkout@v4`, `actions/setup-python@v5`, `tj-actions/changed-files@v44` or latest | 15 min |
| **Verification:** Confirm/deny Copilot hook execution in VS Code agent mode | Standards author | Hook support status documented in `SKILL-COMPAT.md` with evidence (`postToolUse`/`agentStop` logs or absence); if unsupported, Phase 2 onboarding checklist explicitly marks `.akr/logs/session-*.jsonl` as non-gating known gap | 45 min |
| Test workflow on draft PR | Standards author | Workflow runs successfully; validation results appear in PR checks | 1 hour |
| Document workflow customization | Standards author | README explains how projects adapt workflow for their structure | 1 hour |
| Copy adapted workflow to `examples/workflows/` | Standards author | `examples/workflows/validate-documentation.yml` present; matches production workflow; referenced in onboarding docs | 15 min |
| Add `agentStop` hook invocation documentation to workflow README | Standards author | README section explains that `.github/hooks/` directory should also be copied to application repos; notes that `agentStop` hook auto-runs `validate_documentation.py` at session end as local enforcement before CI | 30 min |

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

> **Compatibility note (required):** The legacy `akr-mcp-server/scripts/validation/validate_documentation.py`
> implementation used `git diff --name-only` when `--changed-files` was set. Phase 1 v1.0 must
> **not** reuse that behavior. In v1.0, `--changed-files` means explicit file list input from
> workflow outputs/environment so CI scope is deterministic and PR-accurate.

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

#### Change 9: Add SKILL.md to CODEOWNERS in Application Repos

Include this guidance in onboarding and workflow examples so automated skill update PRs always require standards-team review:

```text
# Add to CODEOWNERS in application repos during onboarding
.github/skills/akr-docs/SKILL.md   @org/standards-team
```

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
      validate-documentation.yml   (ADAPTED; 9 changes)
  examples/
    workflows/
      validate-documentation.yml   (Copy for projects to deploy)
```

---

## Deliverable 2A: Skill Distribution Workflow

### Objective

Build `.github/workflows/distribute-skill.yml` in `core-akr-templates` to open PRs in all registered application repositories whenever `SKILL.md` is released via tag.

### Why in Phase 1

Phase 2 begins copying skill files into application repositories. Without distribution in place before onboarding, those copies drift as soon as the next skill release occurs.

### Trigger Conditions

1. Tag push matching `v*` (primary release trigger)
2. `workflow_dispatch` (manual re-run or single-repo targeting)

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Author `distribute-skill.yml` | Standards author | Workflow present; syntax valid; tag and manual triggers configured | 3 hours |
| Create `AKR_DISTRIBUTION_PAT` secret | Infrastructure lead | Fine-grained PAT configured in repo secrets | 1 hour |
| Document PAT scope requirements | Infrastructure lead | Security/deployment docs list minimum required permissions | 30 min |
| Test workflow on `TrainingTracker.Api` | Standards author + infrastructure | PR opens with expected skill diff and title | 1 hour |
| Test `workflow_dispatch` with `target_repo` | Standards author | Only selected repo is updated | 30 min |
| Test `fail-fast: false` matrix behavior | Standards author | One failing repo does not block successful repos | 30 min |
| Add per-repo distribution status summary and failure follow-up | Standards author | Workflow summary lists success/failure for each repo; failures create or link tracking issue for stale-skill follow-up | 45 min |
| Add distribution checks to release checklist | Standards author | v1.0.0 release checklist includes distribution validation | 10 min |
| Include `.github/hooks/` in distribution bundle | Standards author | `distribute-skill.yml` copies `.github/hooks/postToolUse.json` and `.github/hooks/agentStop.json` to registered repos alongside `SKILL.md`; PR body notes that hook files must be merged to activate local validation | 1 hour |

### Required Secret

`AKR_DISTRIBUTION_PAT` (fine-grained PAT)

- `contents: write`
- `pull-requests: write`
- `metadata: read`

### Output Locations

```
core-akr-templates/
  .github/
    workflows/
      distribute-skill.yml                         (NEW)
    skills/
      akr-docs/
        SKILL.md                                   (EXISTING — source of truth)
        SKILL-COMPAT.md                            (NEW — model compatibility matrix)
    hooks/
      postToolUse.json                             (NEW — logs file writes to .akr/logs/)
      agentStop.json                               (NEW — auto-runs validate_documentation.py)
```

### SKILL.md Mode B SSG Pass Sequence

Replace the original Mode B generation core with this SSG sequence:

```text
3. Determine generation strategy.

   DEFAULT: Section-Scoped Generation (SSG) - multi-pass sequence (Passes 1-7).
   OVERRIDE: Developer-elected single-pass - skip SSG passes; generate entire
             document in one consolidated pass using the full condensed charter.

   Developer may elect single-pass by invoking Mode B with the --single-pass flag
   or by including "single-pass" in the issue template request:
     /akr-docs mode-b [ModuleName] --single-pass
     Issue template field: "Generation mode: single-pass"

   When to use single-pass (developer's discretion):
   - Module files are known to be small (e.g., <=3 files, each <200 LOC)
   - A quick draft is needed for orientation or planning purposes, with the
     developer explicitly accepting that the output will need thorough review
   - Time constraints require a faster turnaround and the developer understands
     the trade-off

   Single-pass is NOT recommended when:
   - Module has 5+ files or any file >500 LOC
   - Documentation will be used as a production reference without Mode C review
   - The module is at or near the max_files: 8 ceiling

   If single-pass is elected:
   - Load: All source files + full condensed charter in one context load
   - Generate: Complete document in one pass using the appropriate base template
   - Set in metadata header:
       generation-strategy: developer-elected-single-pass
       passes-completed: single-pass
       pass-timings-seconds: [total time or "unavailable"]
    - validate_documentation.py emits INFO (not WARNING) when this strategy is present:
       "Document generated via developer-elected single-pass. Review thoroughly,
        especially Operations Map and Business Rules on large modules."
   - Proceed directly to Pass 7 (Assembly + Validation) after generation.
   - No `ssg_slow_modules` event is logged for single-pass runs.

   If single-pass is NOT elected (default), begin SSG:

   Initialize forward payload as an empty object.
   Record pass start time before each pass (if surface supports timing).

   PASS 1 — Module Inventory
   - Load: modules.yaml file list + module metadata only
   - Charter slice: Load ONLY the "Module Files Rules" section of the condensed charter
   - Do NOT load source files in this pass
   - Generate: Module Files section (each file with its role)
   - Forward payload -> Pass 2: file list with roles (~200 tokens maximum)

   PASS 2 — Operations Map
   - Load: All source files from the module's files[] array
   - Charter slice: Load ONLY the "Operations Map Rules" section of the condensed charter
   - If source file total exceeds per-pass token budget:
       Split into Pass 2A (public operations) + Pass 2B (private/internal operations)
       Record split in passes-split field of the metadata header
   - Generate: Operations Map covering ALL operations across all files
   - Forward payload -> Pass 3: operations table (names, signatures, file origins)
     Maximum size: ~500 tokens. Do NOT pass raw source file content forward.

   PASS 3 — Architecture Overview
   - Load: Pass 1 forward + Pass 2 forward ONLY (no source files re-loaded)
   - Charter slice: Load ONLY the "Architecture Diagram Rules" section
   - Generate: Full-stack text diagram (Controller -> Service -> Repository -> DB)
     No Mermaid. Text-based only.
   - Forward payload -> Pass 4: architecture summary (one paragraph, ~150 tokens)

   PASS 4 — Business Rules
   - Load: Pass 2 forward (operations table — method signatures and file origins
             are the anchor for business rule extraction) + Pass 3 forward
             (architecture summary for layer context)
   - Source files: NOT re-read. "Why It Exists" + "Since When" columns are
     human-supplied — apply ❓ markers. Name + Description columns are derived
     from the Pass 2 operations table (method signatures). No source re-read needed.
   - Charter slice: Load ONLY the "Business Rules Requirements" section
                    (Why It Exists + Since When columns)
   - Generate: Business Rules table (Name + Description from operations table;
     ❓ on Why It Exists + Since When for human completion in Mode C)
   - Forward payload -> Pass 5: rule names + brief rationale (~300 tokens maximum)
   - Project-level override: if `ssg_pass4_source_reread: true` is set in
     modules.yaml for this module (e.g., heavily commented service files),
     targeted re-read of Service files is authorized. Document override in
     passes-completed as pass4-override.

   PASS 5 — Data Operations
   - Load: Pass 2 forward (operations table already contains repository method
             signatures and file origins, sufficient to map reads/writes)
             + Pass 4 forward (business rules for data pattern context)
   - Source files: NOT re-read. If a specific DB call pattern cannot be resolved
     from the operations table, mark as ❓ for Mode C resolution.
   - Charter slice: Load ONLY the "Data Operations Rules" section
   - Generate: Reads/Writes table
   - Forward payload -> Pass 6: table operations summary (~200 tokens maximum)

   PASS 6 — Questions & Gaps + Front Matter + Transparency Markers
   - Load: All prior pass forwards assembled (no source files)
   - Charter slice: Load ONLY the "Marker Syntax Rules" + "Front Matter Requirements"
   - Generate:
       ❓ markers on sections requiring human input
       🤖 markers on AI-inferred content
       DEFERRED placeholders where information is unavailable
       YAML front matter (businessCapability, feature, layer, project_type,
                          status, compliance_mode)
       Questions & Gaps section
   - Forward payload -> Pass 7: complete assembled draft (all sections joined)

   For ui-component project types, substitute the following pass 2-5 sections:

   PASS 2 (UI) — Component Hierarchy + Hook Dependency Graph
   - Load: All UI source files from the module's files[] array
   - Charter slice: Load ONLY the "Component Hierarchy Rules" + "Hook Graph Rules"
   - If source file total exceeds per-pass token budget: split into Pass 2A + Pass 2B
   - Generate: Component tree with props interfaces + hook dependency graph
   - Forward payload -> Pass 3: component tree + hook graph (~500 tokens maximum)
     Do NOT pass raw source file content forward.

   PASS 3 (UI) — Type Definition Cross-Reference
   - Load: Pass 2 forward ONLY (no source files re-read)
   - Charter slice: Load ONLY the "Type Definition Rules"
   - Generate: Type cross-reference from component hierarchy output
     Mark unresolvable type relationships as ❓
   - Override: if ssg_pass3_source_reread: true in modules.yaml, targeted type
     file re-read is authorized; record pass3-override in passes-completed
   - Forward payload -> Pass 4: type summary (~200 tokens maximum)

   PASS 4 (UI) — State Management + Props Flow
   - Load: Pass 2 forward + Pass 3 forward ONLY (no source files re-read)
   - Charter slice: Load ONLY the "State/Props Rules"
   - Generate: State shapes and prop drilling paths from component hierarchy
   - Forward payload -> Pass 5: state/props summary (~250 tokens maximum)

   PASS 5 (UI) — Rendering Patterns + Side Effects
   - Load: Pass 2 forward + Pass 4 forward ONLY (no source files re-read)
   - Charter slice: Load ONLY the "Rendering Rules"
   - Generate: Rendering patterns and side-effect sources from component hierarchy
     and hook dependency graph
   - Forward payload -> Pass 6: rendering summary (~200 tokens maximum)

4. PASS 7 — Assembly + Validation
   - Assemble complete draft from Pass 6 forward payload
   - Write <!-- akr-generated --> metadata header (see header format in Step 8)
     Populate fields:
       passes-completed: record actual execution IDs (e.g., 1,2,3,4,5,6,7 if no split;
                         1,2A,2B,3,4,5,6,7 if Pass 2 was split)
       passes-split: record split type if split occurred (e.g., 2A,2B); empty string if not
       pass-timings-seconds: use pass IDs matching passes-completed
                             (e.g., pass2a=Xs,pass2b=Ys when split; pass2=Xs when not split)
       generation-strategy: section-scoped (or single-pass-fallback if fallback occurred)
     Override annotation examples:
       Backend with pass4 override: passes-completed: 1,2,3,pass4-override,5,6,7
       UI with pass3 override:      passes-completed: 1,2,pass3-override,4,5,6,7
       UI with pass3 override + split: passes-completed: 1,2A,2B,pass3-override,4,5,6,7
   - Run validate_documentation.py against assembled draft
   - Resolve or mark DEFERRED any validation failures
   - Proceed to file write and PR steps
```

### Slow-Generation Handling in Mode B

```text
SLOW GENERATION HANDLING

If total elapsed time across all passes exceeds 45 minutes:
  1. If running in coding agent background mode:
     - Continue and complete the current pass.
     - Proceed automatically to single-pass-fallback (Option B below) for any
       remaining incomplete sections. Do NOT wait for developer input.
     - Set generation-strategy: single-pass-fallback in metadata header.
     - Log ssg-slow-module-event to .akr/logs/session-*.jsonl.
     - Add PR checklist note: "⚠️ Generation exceeded 45-minute threshold.
       Single-pass fallback used for remaining sections. Consider module
       splitting (requires standards team PR) if this recurs."
     - Option A (module splitting) is a POST-PR developer action — the agent
       cannot modify modules.yaml without a standards team PR. The developer
       evaluates module splitting after reviewing this PR.

  2. If running in interactive VS Code mode:
     - Notify developer before proceeding: "Generation is taking longer than
       expected ([X] minutes elapsed). Remaining sections will be completed
       using single-pass fallback unless you choose to stop and split the module.
       A) Stop now — split module in modules.yaml (requires standards team PR)
       B) Continue — use single-pass fallback for remaining sections (more ❓
          markers; Mode C review recommended before merge)"
     - If developer does not respond within the current session, proceed with
       Option B and note the lack of explicit response.

  3. If Pass 2 requires more than 2 splits (>2 sub-passes):
     - Do NOT attempt a third sub-pass.
     - Record passes-completed up to the last completed sub-pass.
     - Proceed to single-pass-fallback for the Operations Map remainder and all
       subsequent sections.
     - Add PR checklist note: "⚠️ Module required >2 Pass 2 sub-passes. Module
       splitting is strongly recommended. See modules.yaml module_group field."

  Option B — Single-pass fallback:
     Load full condensed charter (not section-specific slices)
     Generate remaining incomplete sections in one consolidated pass
     Set generation-strategy: single-pass-fallback in metadata header
     Expect additional ❓ markers — Mode C review is recommended before PR merge
```

### Mode B PR Checklist Additions

- [ ] `<!-- akr-generated -->` header includes `passes-completed` field
- [ ] `pass-timings-seconds` field present (or `unavailable` with justification)
- [ ] If `generation-strategy` is `single-pass-fallback`: Mode C review scheduled
- [ ] If `generation-strategy` is `developer-elected-single-pass`: reviewer is aware output may have more `❓` markers than SSG-generated docs, especially on large modules; Mode C review recommended before production compliance mode
- [ ] If `passes-split` is populated: Operations Map reviewed for completeness across sub-passes

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
| Update existing `lean_baseline_service_template.md` front matter block | Standards author | Existing front matter includes both `businessCapability` (PascalCase) and `feature` (work-item ID format) to match Phase 1 validation contract | 30 min |
| Adapt `ui_component_template.md` | Standards author | Module Files, component hierarchy diagram sections added | 3 hours |
| Add module-scope YAML front matter | Standards author | `businessCapability`, `feature`, `layer`, `project_type`, `status` fields documented | 1 hour |
| **Update all YAML front matter examples to PascalCase** | Standards author | All `businessCapability` examples use PascalCase matching `tag-registry.json` (e.g., `CourseCatalogManagement` not `course-catalogmanagement`) | 1 hour |
| Test backend template on CourseDomain | Standards author | Output matches `courses_service_doc.md` structure | 2 hours |
| Test UI template on sample UI module | Standards author | Component grouping logic works; hierarchy clear | 2 hours |
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

4. **Three-mode Agent Skill invocation guidance**
   - When to use Mode A (grouping proposal)
   - When to use Mode B (documentation generation)
   - When to use Mode C (interactive HITL completion for existing drafts with unresolved `❓` markers — replaces `/docs.interview`)
   
5. **`modules.yaml` front matter field reference**

6. **Copilot-specific invocation guidance and model compatibility note**
  - Instruction to always use `/akr-docs mode-a`, `/akr-docs mode-b`, `/akr-docs mode-c` explicitly (never rely on auto-discovery)
  - What to expect at the start of every response: `✅ akr-docs INVOKED AND STEPS EXECUTED` self-reporting block
  - What to do if the self-reporting block is absent: check `/skills` to confirm `akr-docs` is enabled; retry with explicit slash command
  - Note: skill is optimised for Claude Sonnet 4.6; Copilot (GPT-4o) users should expect ~75% first-run pass rate on large modules; CI gate validates output regardless of model

### Target Document Length

**150-200 lines** (vs. current verbose file)

Goal: concise Copilot-native reference that a developer reads once during onboarding

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Remove MCP-specific sections | Standards author | 6 sections removed cleanly | 1 hour |
| Author module grouping principles | Standards author | Domain noun, dependency graph, DTO alignment, interface/impl pairs documented | 1 hour |
| Add template selection table | Standards author | All 7 `project_type` values mapped to templates | 30 min |
| Add Agent Skill invocation guidance | Standards author | Mode A, Mode B, and Mode C triggers clear; Mode C noted as `/docs.interview` replacement | 1 hour |
| Add `modules.yaml` front matter reference | Standards author | Required fields per doc type documented | 30 min |
| Validate document length | Standards author | ≤200 lines; concise and scannable | 15 min |
| Test with Copilot in VS Code | Pilot rep | Instructions load correctly; no broken references | 30 min |
| Add Copilot-specific invocation and model compat note | Standards author | Section present covering: (a) always use `/akr-docs` slash command, (b) self-reporting confirmation block, (c) what to do if block is absent, (d) model compatibility note referencing `SKILL-COMPAT.md` for full detail | 45 min |

### Output Location

```
core-akr-templates/
  .akr/
    standards/
      copilot-instructions.md   (REPLACED; canonical source)

Per-project deployment:
  .github/
    copilot-instructions.md     (copy of canonical source or condensed charter fallback)

Documentation outputs:
  docs/
    DEVELOPER_REFERENCE.md      (UPDATED in Phase 1 — HITL alignment + role mapping)
    VALIDATION_GUIDE.md         (UPDATED in Phase 1 — compliance mode graduation + rollback)
```

---

## Deliverable 5: Schema Deliverables

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
          },
          "ssg_pass4_source_reread": {
            "type": "boolean",
            "default": false,
            "description": "Authorizes targeted Service file re-read in SSG Pass 4 for modules where service-file comments are the primary business rule source. Not recommended as a default. Document rationale in the notes field."
          },
          "ssg_pass3_source_reread": {
            "type": "boolean",
            "default": false,
            "description": "Authorizes targeted type file re-read in SSG Pass 3 for UI modules where complex generic type annotations are not representable in component hierarchy summaries."
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

**Additional Phase 1 schema field (for Phase 3/4 compatibility):**

```json
"script_approval_required": {
  "type": "boolean",
  "default": false,
  "description": "When true, custom-agent script execution must require explicit user approval before running side-effecting script skills"
}
```

This field is introduced in Phase 1 so downstream phases can rely on a stable schema even if
Phase 3 automation is skipped after a successful Phase 2.5 outcome.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Author `modules-schema.json` | Standards author | Complete schema per Part 4 specification | 3 hours |
| Update `akr-config-schema.json` | Standards author | `project_type` added to `requiredTags`; conditionality documented | 1 hour |
| Add `script_approval_required` to `akr-config-schema.json` | Standards author | Boolean field present with default `false`; description references custom-agent script gating | 30 min |
| Update `tag-registry-schema.json` layers | Standards author | Decide whether to add `Full-Stack` or document exclusion | 1 hour |
| Validate schemas with test YAML | Standards author | Example `modules.yaml` validates without errors | 1 hour |
| Document schema versioning | Standards author | Schema version tied to `core-akr-templates` release tag | 30 min |
| Add `ssg_pass4_source_reread` optional boolean field to `modules-schema.json` | Standards author | Field present with type `boolean`, default `false`, description: "Authorizes targeted Service file re-read in SSG Pass 4 for modules where service-file comments are the primary business rule source. Requires rationale in notes field." | 30 min |
| Add `ssg_pass3_source_reread` optional boolean field to `modules-schema.json` | Standards author | Field present with type `boolean`, default `false`, description: "Authorizes targeted type file re-read in SSG Pass 3 for UI modules where complex generic types are not representable in the component hierarchy summary." | 30 min |
| Add validator support for both override fields in `validate_documentation.py` | Standards author | Validator reads both fields from modules.yaml; records `pass4-override` or `pass3-override` in validation output when either is `true`; emits INFO log (not warning) noting the override | 1 hour |
| Add both fields to `modules.yaml` example file | Standards author | Fields present with `false` values and inline comment: "# Set true only with documented rationale - see CHARTER-RESTORATION-PLAN.md override guidance" | 20 min |

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

## Deliverable 7A: Agent Session Hooks

### Objective

Create two hook configuration files that provide local enforcement of the skill execution contract before CI runs. These hooks are distributed to all registered application repositories via `distribute-skill.yml`.

### Why Phase 1

Hooks enforce the in-session contract (Layer 2 of the three-layer reliability stack). Without hooks, the developer has no local feedback if a skill step was skipped - they discover this only when CI fails after PR submission. Hooks close this gap by running `validate_documentation.py` automatically at session end.

### Hook Files

**`.github/hooks/postToolUse.json` - Audit Logger**

Logs every file write during the session to a local JSONL file, providing a session-level audit trail. CI can reference this log to confirm expected output files were written.

```json
{
  "version": 1,
  "hooks": {
    "postToolUse": [
      {
        "type": "command",
        "bash": "mkdir -p .akr/logs; if [ \"$TOOL_NAME\" = \"write_file\" ] || [ \"$TOOL_NAME\" = \"create_file\" ] || [ \"$TOOL_NAME\" = \"run_skill_script\" ]; then echo \"{\\\"timestamp\\\": \\\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\\\", \\\"tool\\\": \\\"$TOOL_NAME\\\", \\\"file\\\": \\\"$TOOL_INPUT_FILE_PATH\\\"}\" >> .akr/logs/session-$(date +%Y%m%d).jsonl; fi",
        "timeoutSec": 5
      }
    ]
  }
}
```

`run_skill_script` is included so Phase 3 code-skill executions are visible in the same session
audit trail as file write operations.

**`.github/hooks/agentStop.json` - Auto-Validation Gate**

Runs `validate_documentation.py` automatically when the agent session ends. Results written to `.akr/logs/last-validation.json`. If validation fails, the developer sees the error immediately in their terminal before opening a PR.

Because local hooks do not run inside GitHub Actions, no `tj-actions` outputs exist at hook time.
The hook must derive a local changed-file list and pass it explicitly to `--changed-files`.

```json
{
  "version": 1,
  "hooks": {
    "agentStop": [
      {
        "type": "command",
        "bash": "if [ -f modules.yaml ]; then CHANGED_FILES=$(git diff --name-only --diff-filter=AM HEAD -- docs); if [ -n \"$CHANGED_FILES\" ]; then python .akr/scripts/validate_documentation.py --changed-files \"$CHANGED_FILES\" --output json --fail-on needs | tee .akr/logs/last-validation.json; else python .akr/scripts/validate_documentation.py --all docs/modules --output json --fail-on needs | tee .akr/logs/last-validation.json; fi; else echo '{\"summary\": {\"note\": \"modules.yaml not found — skipping module-aware validation\"}}'; fi",
        "timeoutSec": 60
      }
    ]
  }
}
```

### Scope and Limitations

- Hooks run in Claude Code sessions. Availability in GitHub Copilot depends on Copilot's hook support at the time of Phase 1 execution.
- If hooks are not supported by Copilot at Phase 1 time, document this as a known gap and surface the issue in `SKILL-COMPAT.md`. The CI gate (`agentStop` equivalent) remains the enforcement fallback.
- Local hook `git diff` usage is limited to producing an explicit file list input for `--changed-files`; validator semantics remain explicit-list based.
- Hook files are in `.github/hooks/` to keep them with other GitHub-managed skill files and to allow CODEOWNERS control.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Author `postToolUse.json` audit logger hook | Standards author | File present at `.github/hooks/postToolUse.json`; bash command writes valid JSONL to `.akr/logs/session-YYYYMMDD.jsonl`; monitored tools include `write_file`, `create_file`, `run_skill_script` | 1 hour |
| Author `agentStop.json` auto-validation hook | Standards author | File present at `.github/hooks/agentStop.json`; hook derives local changed files and passes explicit list to `--changed-files` (fallback `--all docs/modules` when no local changes); writes output to `.akr/logs/last-validation.json`; handles missing `modules.yaml` gracefully | 1 hour |
| Add `.akr/logs/` to `.gitignore` | Standards author | Log files not committed; `session-*.jsonl` pattern in `.gitignore` | 10 min |
| Test `postToolUse` hook in Claude Code session | Standards author | File write events appear in `.akr/logs/session-YYYYMMDD.jsonl` after Mode B run | 30 min |
| Test `agentStop` hook in Claude Code session | Standards author | Validation output appears in `.akr/logs/last-validation.json`; errors surfaced before PR opened | 30 min |
| Verify hook JSON syntax against Agent Skills spec | Standards author | Both JSON files validate without errors | 15 min |
| Add hooks note to onboarding checklist | Standards author | Onboarding checklist (Phase 2 Deliverable 9) includes step to confirm `.github/hooks/` directory present and both files present | 10 min |
| Document hook unavailability fallback | Standards author | `SKILL-COMPAT.md` includes row noting if hooks are unsupported in Copilot at time of Phase 1; workaround = run `validate_documentation.py --changed-files "<space-separated file list>" --fail-on needs` manually before opening PR (or `--all docs/modules` when no file list available) | 30 min |

### Output Locations

```
core-akr-templates/
  .github/
    hooks/
      postToolUse.json     (NEW)
      agentStop.json       (NEW)
```

Per-project (delivered via `distribute-skill.yml`):

```
[application-repo]/
  .github/
    hooks/
      postToolUse.json     (distributed copy)
      agentStop.json       (distributed copy)
  .akr/
    logs/                  (created at first hook run; gitignored)
```

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
- [ ] `SKILL_VERSION: v1.0.0` header present in `.github/skills/akr-docs/SKILL.md`
- [ ] `registered-repos.yaml` present with pilot project entry
- [ ] `distribute-skill.yml` present and tested against pilot project
- [ ] `SKILL.md` frontmatter includes `disable-model-invocation: true`, `optimized-for: claude-sonnet-4-6`, `tested-on` fields, and self-reporting CRITICAL block
- [ ] `.github/hooks/postToolUse.json` and `.github/hooks/agentStop.json` present and tested
- [ ] `evals/benchmark.json` Phase 1 baseline populated; `SKILL-COMPAT.md` v1.0 complete with model matrix values
- [ ] `AKR_DISTRIBUTION_PAT` secret configured by infrastructure lead
- [ ] PR body template `automated-skill-update.md` present
- [ ] Distribution workflow fires successfully on v1.0.0 tag push
- [ ] `docs/DEVELOPER_REFERENCE.md` updated with HITL alignment and role mapping
- [ ] `docs/VALIDATION_GUIDE.md` updated with compliance mode graduation and rollback procedure
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
- **Agent Skill three-mode:** Mode A (grouping proposal) + Mode B (documentation generation) + Mode C (interactive HITL completion for existing drafts)
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
✅ `pyyaml` added to `requirements.txt` as explicit dependency  
✅ CI workflow: 9 changes applied; validates module docs without false positives; `examples/workflows/` copy published  
✅ Skill distribution workflow: `distribute-skill.yml` operational with PAT and registered repo targets  
✅ Templates: 2 adapted; acceptance criterion passed (CourseDomain output matches `courses_service_doc.md`)  
✅ `copilot-instructions.md`: Full rewrite complete (~150-200 lines); module-centric logic; three-mode Agent Skill guidance included  
✅ `modules-schema.json`: Complete schema authored at `.akr/schemas/`; validates example YAML  
✅ `akr-config-schema.json`: `project_type` added to required tags  
✅ HITL alignment: Role mapping documented; templates updated  
✅ Governance policies: Compliance graduation + TEMPLATE_MANIFEST narrowing documented  
✅ Cross-platform: Ubuntu + macOS + Windows all passing  
✅ v1.0.0 release: Tagged, release notes published, team announced  
✅ `SKILL.md` frontmatter: `disable-model-invocation: true` + self-reporting CRITICAL block + `<!-- akr-generated -->` Mode B final step all present  
✅ `.github/hooks/`: `postToolUse.json` and `agentStop.json` distributed to pilot repo via `distribute-skill.yml`  
✅ `evals/benchmark.json` v1.0 baseline and `SKILL-COMPAT.md` v1.0 both committed before pilot begins  
✅ `docs/DEVELOPER_REFERENCE.md` updated with HITL alignment and role mapping  
✅ `docs/VALIDATION_GUIDE.md` updated with compliance mode graduation and rollback procedure  

**Exit gate:** Phase 1 retrospective complete; Phase 2 pilot onboarding authorized by standards lead **in writing** (GitHub comment, email, or approval record) before Phase 2 begins.

---

**Next Phase:** [Phase 2: Pilot Onboarding](PHASE_2_PILOT_ONBOARDING.md)

**Related Documents:**
- [Phase 0: Prerequisites](PHASE_0_PREREQUISITES.md)
- [Implementation Plan Overview](IMPLEMENTATION_PLAN_OVERVIEW.md)
- [Developer Reference](../DEVELOPER_REFERENCE.md)
- [Validation Guide](../VALIDATION_GUIDE.md)
- [Implementation-Ready Analysis](../akr_implementation_ready_analysis.md) — Parts 2, 6, 7, 12
