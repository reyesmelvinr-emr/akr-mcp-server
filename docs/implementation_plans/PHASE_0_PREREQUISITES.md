# Phase 0: Prerequisites — Implementation Plan

**Duration:** 1-2 weeks  
**Team:** Standards team (1 FTE) + pilot project representative  
**Status:** 🔴 BLOCKING GATE — Phase 1 cannot begin until complete

---

## Overview

Phase 0 establishes the minimal viable prerequisites for the AKR module-based documentation system. Every deliverable in this phase is a proven blocker—charter compression prevents context saturation, pre-pilot tests validate foundational assumptions, and infrastructure audit prevents rework.

**Critical Path:** Charter compression → Pre-pilot Test 1 (code analysis) → remaining tests in parallel

---

## Acceptance Criteria

Phase 0 is complete when:

1. ✅ `akr-mcp-server` archived in GitHub (repo set to archived; team notified)
2. ✅ All 3 condensed charters created and validated at target token counts
3. ✅ Character limit validated for all condensed charters (≤~4,000 chars fallback; ≤2,500 tokens target)
4. ✅ Agent Skill authored and validated with Mode A + Mode B
5. ✅ `modules.yaml` schema defined and example created
6. ✅ All 6 pre-pilot tests PASS **or** have documented fallback architectures (Test 5 legal review initiated in parallel at Phase 0 start)
7. ✅ Infrastructure audit complete with migration inventory; all references documented
8. ✅ Cost baseline model established and budget approved
9. ✅ Monitoring enabled in pilot `.akr-config.json`
10. ✅ Pilot project business capability tags added to `tag-registry.json` and distribution verified
11. ✅ Archive prerequisites completed (tests and validation baselines copied)

**Exit Gate:** All items above checked; Phase 0 retrospective complete; Phase 1 authorized by standards lead.

---
### Deliverable 0: Archive `akr-mcp-server` (First Task)

### Objective

Archive the `akr-mcp-server` repository to prevent ongoing references to a deprecated codebase during pilot.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Set repo to archived | Infrastructure lead | `akr-mcp-server` archived in GitHub settings; access restricted to read-only | 15 min |
| Copy validation baselines and tests | Standards author | `test_validation_library.py`, `test_extraction.py`, `test_pipeline_e2e.py` copied to `core-akr-templates/tests/` | 30 min |
| Update any `.gitmodules` references | Standards author | Confirm no submodule references to `akr-mcp-server` exist in active projects | 15 min |
| Communicate deprecation to team | Standards lead | Team notified of archival; directed to `core-akr-templates` as source of truth | 30 min |

---
## Deliverable 1: Charter Compression

### Objective

Compress full charters (~11,000 tokens each) to condensed "dense summary" versions (~2,500 tokens each) that preserve governance rules while removing explanatory prose.

### Why Blocking

Backend charter at ~11,000 tokens + lean baseline template at ~7,000 tokens = ~18,000 tokens **before any source files load**. With 5 source files in a typical module, total context exceeds 25,000 tokens—guaranteed degradation or failure.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Compress `AKR_CHARTER_BACKEND.md` → `copilot-instructions/backend-service.instructions.md` | Standards author | ≤2,500 tokens; ≤~4,000 characters fallback; all required sections preserved; all marker syntax preserved; all quality thresholds preserved | 3-4 hours |
| Compress `AKR_CHARTER_UI.md` → `copilot-instructions/ui-component.instructions.md` | Standards author | ≤2,500 tokens; ≤~4,000 characters fallback; component-specific section requirements preserved | 2-3 hours |
| Compress `AKR_CHARTER_DB.md` → `copilot-instructions/database.instructions.md` | Standards author | ≤1,500 tokens; ≤~2,500 characters fallback; object-level documentation rules preserved | 1-2 hours |
| **Validate character count (Sub-test)** | Standards author | **Before declaring compression complete:** All 3 charters validated against ~4,000 character practical limit (Markdown format) | 30 min |
| Validate compression ratio | Standards author | All 3 charters achieve ≤23% of original token count | 30 min |
| Cross-reference full charters | Standards author | Each condensed charter includes "Full charter: [link]" reference | 15 min |

### What Must Be Retained

**In all condensed charters:**
- Required section headings and minimum content criteria
- Required YAML front matter fields (`businessCapability`, `feature` (work-item tag), `layer`, `project_type`, `status`, `compliance_mode`)
- Transparency marker syntax: `🤖`, `❓`, `NEEDS`, `VERIFY`, `DEFERRED` with placement rules
- Quality thresholds (minimum word counts, required structural elements)
- Cross-references to full charter location

**Backend-specific:**
- Module Files section requirement
- Operations Map requirement covering ALL operations across ALL files
- Full-stack architecture diagram instruction (text-based, no Mermaid)
- Business Rules table with "Why It Exists" and "Since When" columns

**UI-specific:**
- Component hierarchy diagram requirement
- Hook dependency graph requirement
- Type definition cross-reference requirement

**Database-specific:**
- Object Definition section requirement (schema, columns/parameters)
- Relationships and Dependencies section requirement
- Usage Patterns section requirement

### What Gets Removed

- Explanatory prose and rationale paragraphs
- Worked examples and sample documentation snippets
- Historical context and changelog references
- Redundant restatements of governance rules
- Verbose troubleshooting guides

### Output Format Specification

**Structure:** Plain Markdown with numbered rules for clarity
- Use ATX headings (##, ###) for section hierarchy
- List required fields as bullet points with inline code formatting
- Use blockquotes for critical rules that must not be omitted
- Include code fences only for YAML front matter examples
- NO Mermaid diagrams in condensed charters (text-based only)

**Validation:** Character count must fit `.github/copilot-instructions.md` ~4,000 character practical limit as fallback delivery method

### Output Locations

```
core-akr-templates/
  copilot-instructions/
    backend-service.instructions.md      (~2,500 tokens)
    ui-component.instructions.md         (~2,500 tokens)
    database.instructions.md             (~1,500 tokens)
  charters/
    AKR_CHARTER_BACKEND.md               (full; reference only)
    AKR_CHARTER_UI.md                    (full; reference only)
    AKR_CHARTER_DB.md                    (full; reference only)
```

### Risk Mitigation

| Risk | Mitigation |
|---|---|
| Over-compression loses critical rules | Validate each condensed charter against acceptance test from `test_pipeline_e2e.py` |
| Token count measurement inconsistency | Use consistent tokenizer (tiktoken GPT-4 encoder) for all measurements |
| Condensed charter insufficient for complex modules | Pre-pilot Test 3 (large module stress test) validates boundary case |

---

## Decision Gate: Feature Tag Collision

### Objective

Resolve the collision between legacy `feature` tags (`FN#####_US#####`) and the new business capability taxonomy before any charter compression or modules.yaml examples are authored.

### Decision (Locked)

- Rename the modules manifest field to `businessCapability`.
- Keep `feature` in YAML front matter as the work-item tag in `FN#####_US#####` format.

### Consequences

- All condensed charters must describe **two distinct tags**:
  - `businessCapability`: PascalCase key aligned to `tag-registry.json`
  - `feature`: work-item identifier in `FN#####_US#####` format
- `modules.yaml` examples must use `businessCapability` (PascalCase).
- `validate_documentation.py` must validate `businessCapability` against `tag-registry.json`.
- `feature` format enforcement remains in the charters and templates.

---

## Deliverable 2: Agent Skill Authoring

### Objective

Create `.github/skills/akr-docs/SKILL.md` encoding Mode A (grouping proposal) and Mode B (documentation generation) workflows.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Author `SKILL.md` with Mode A workflow | Standards author | Full specification from Part 5 of analysis document implemented | 2 hours |
| Author `SKILL.md` with Mode B workflow | Standards author | Loads condensed charter based on `project_type`; references `modules.yaml` | 2 hours |
| Add prerequisite check in Mode B | Standards author | Mode B stops if `modules.yaml` status is `draft` | 30 min |
| Document skill invocation patterns | Standards author | "propose module groupings" → Mode A; "generate documentation for X" → Mode B | 1 hour |
| Validate skill loads in VS Code | Pilot rep | Skill appears in agent mode skill list | 15 min |

### Mode A Workflow Summary

1. Check if `modules.yaml` exists; redirect to Mode B if approved modules present
2. Scan source files by directory path and filename
3. Group by dominant domain noun (e.g., Course, Enrollment, User)
4. Identify file roles: Controller, Service, Repository, DTOs (backend) or Page, Components, Hooks, Types (UI)
5. Mark database files as `database_objects[]` — never group with app code
6. Unassignable files → `unassigned[]` with reason
7. Apply `project_type` based on project structure detection
8. Write draft `modules.yaml` with `status: draft` on all modules
9. Open draft PR with grouping validation checklist

### Mode B Workflow Summary

1. Read `modules.yaml`; find requested module; check `status != draft`
2. Load condensed charter from `copilot-instructions/` based on `project_type`
3. Read all source files listed in module's `files[]` array
4. Generate module documentation using appropriate base template
5. Apply transparency markers: `🤖` for inferred, `❓` for required human input
6. Run `validate_documentation.py` against draft
7. Write to `doc_output` path on feature branch
8. Open draft PR with content review checklist

### Output Location

```
core-akr-templates/
  .github/
    skills/
      akr-docs/
        SKILL.md
```

---

## Deliverable 3: `modules.yaml` Schema and Example

### Objective

Define the complete `modules.yaml` schema and create reference examples for API and UI projects.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Define `modules.yaml` schema | Standards author | Full specification from Part 4 of analysis document | 2 hours |
| Create TrainingTracker.Api example | Standards author | CourseDomain module + training.Courses DB object | 1 hour |
| Create UI project example | Standards author | CourseManagementUI module with component grouping | 1 hour |
| Document field semantics | Standards author | `layer` vs. `project_type` distinction clear; `businessCapability` format documented | 1 hour |
| Validate YAML syntax | Standards author | Valid YAML; loads with PyYAML without errors | 15 min |

### Schema Components

**Project-level metadata:**
- `project.name` (string)
- `project.layer` (enum: UI, API, Database, Integration, Infrastructure, Full-Stack)
- `project.standards_version` (semver)
- `project.minimum_standards_version` (semver)
- `project.compliance_mode` (enum: pilot, production)

**Module groupings (`modules[]`):**
- `name` (PascalCase string)
- `project_type` (enum: api-backend, ui-component, microservice, general)
- `businessCapability` (PascalCase key from `tag-registry.json`)
- `domain` (string)
- `layer` (string)
- `max_files` (integer, default: 8, hard ceiling)
- `files[]` (array of workspace-relative paths)
- `doc_output` (workspace-relative output path)
- `status` (enum: draft, review, approved, deprecated)
- `compliance_mode` (optional; overrides project default)

**Database objects (`database_objects[]`):**
- `name` (schema-qualified string)
- `type` (enum: table, view, procedure, function)
- `source` (enum: ssdt, script, manual)
- `businessCapability` (optional; PascalCase key from `tag-registry.json`)
- `doc_output` (workspace-relative output path)
- `status` (enum: draft, review, approved, deprecated)

**Unassigned files (`unassigned[]`):**
- `path` (workspace-relative path)
- `reason` (string; why unassigned)

### Output Locations

```
core-akr-templates/
  schemas/
    modules-schema.json       (NEW — does not exist yet)
  examples/
    modules.yaml              (TrainingTracker.Api reference)
    modules-ui-example.yaml   (UI project reference)
```

---

## Deliverable 4: Pre-Pilot Validation Tests

### Objective

Validate six foundational assumptions before Phase 1 investment. Each test must PASS or have a documented fallback architecture.

### Test Execution Sequence

**Critical dependencies:**
- **Test 5 (Legal/Compliance):** Start on Day 1 (parallel) — longest lead time (2-6 weeks external dependency)
- **Test 1 → Test 3:** Sequential — Test 1 validates charter compression works
- **Test 2:** Independent — can run parallel with Test 1
- **Test 4:** Requires Tests 1-3 to pass first (needs functional agent for cost baseline)
- **Test 6 (Visual Studio):** Can run parallel after Test 1 passes

**Execution order:** Start Test 5 immediately → Test 1 → (Test 2 + Test 3 + Test 6 in parallel) → Test 4

### Test 1: Code Analysis Capability

**What it validates:** Copilot + condensed charter extracts module-level content correctly

**Prerequisite:** Backend condensed charter must exist

**Method:**
1. Create test module: `CourseDomain` (5 files: Controller, Service interface, Service impl, Repository interface, EF repository, DTOs)
2. Invoke Agent Skill Mode B with condensed backend charter loaded
3. Run 3 times independently
4. Measure: section completeness, operations coverage, file role identification

**Pass criteria:**
- Agent correctly groups 5 files into one output
- Module Files section lists all 5 files with correct roles
- Operations Map covers ≥90% of public methods across all files
- Architecture diagram shows full stack (Controller → Service → Repository → DB)
- ≥90% consistency across 3 runs

**Fail fallback:**
- Retain `CodeAnalyzer` from `akr-mcp-server` for deterministic extraction
- Hosted MCP for governance; local deterministic analyzer for structure

**Owner:** Standards author + pilot rep  
**Estimated Time:** 4 hours

---

### Test 2: Context Source Configuration

**What it validates:** `core-akr-templates` available as GitHub Hosted MCP Context Source at current Copilot plan tier

**Method:**
1. Configure `core-akr-templates` repository as Hosted MCP Context Source
2. Check Settings → Copilot → MCP in VS Code
3. Verify context source appears and loads on new sessions
4. Test in Visual Studio (not just VS Code)

**Pass criteria:**
- Context source visible in settings
- Available in both VS Code and Visual Studio
- Context loads automatically on session start
- Condensed charters accessible without manual file loading

**Fail fallback:**
- Use `.github/copilot-instructions.md` with condensed charter as primary delivery
- Fits in ~4,000 character practical limit
- Per-repository distribution instead of centralized

**Owner:** Standards author  
**Estimated Time:** 2 hours

---

### Test 3: Large Module Stress Test

**What it validates:** Module with 8 files and 2,000+ LOC does not truncate sections

**Prerequisite:** Charter compression complete

**Method:**
1. Create test module: 8 files, ~250 lines each, ~2,000 total LOC
2. Invoke Mode B with condensed backend charter
3. Check output for section truncation or omission
4. Run `validate_documentation.py` (mock if not yet available)

**Pass criteria:**
- All MODULE-required sections present
- Module Files section lists all 8 files
- Operations Map not truncated
- Business Rules table complete
- Data Operations section covers all reads and writes
- No "..." or "[content omitted]" artifacts

**Fail fallback:**
- Enforce `max_files: 5` guidance for large-file modules
- Document that 8-file ceiling is for normal-sized files (~150-200 lines)
- Provide split guidance for over-600-line files

**Owner:** Standards author  
**Estimated Time:** 3 hours

---

### Test 4: GitHub Actions Invocability

**What it validates:** Whether Copilot can be invoked from GitHub Actions for automation

**Method:**
1. Research current Copilot-from-Actions APIs
2. Test simple invocation from workflow context
3. Document API availability, rate limits, authentication

**Pass criteria:**
- Working Copilot-from-Actions mechanism documented
- Rate limits acceptable for Phase 4 consolidation frequency
- OR deterministic aggregation design confirmed as sufficient

**Fail fallback:**
- Phase 4 deterministic aggregation design (already designed in analysis)
- `consolidate.py` as deterministic Python aggregator
- Human refinement with Copilot agent mode assistance (not from Actions)

**Owner:** Standards author  
**Estimated Time:** 2 hours

---

### Test 5: Data Governance / Compliance

**What it validates:** Legal and security approval for Copilot processing org code

**Method:**
1. Submit data governance request to legal team
2. Document Copilot data handling model (Microsoft commitment)
3. Confirm against org data residency requirements
4. Obtain written approval

**Pass criteria:**
- Written sign-off from legal and security teams
- Copilot data handling confirmed compliant
- Any restrictions documented (e.g., exclude certain repos)

**Fail fallback:**
- Manual documentation with templates only
- No AI generation assistance
- Templates and validation remain; remove Agent Skills
- Significant productivity reduction; escalate to management

**Owner:** Standards lead + legal liaison  
**Estimated Time:** 1-2 weeks (external dependency)

**CRITICAL:** This test must start on Day 1 of Phase 0, running in parallel with all other work. Legal review is the longest lead-time item and will become the critical path bottleneck if started sequentially after other tests.

---

### Test 6: Visual Studio Parity

**What it validates:** Agent Skills load and function correctly in Visual Studio (not just VS Code)

**Prerequisite:** Test 1 complete (functional Agent Skill)

**Method:**
1. Install GitHub Copilot extension in Visual Studio 2022
2. Configure Agent Skill in `.github/skills/akr-docs/SKILL.md`
3. Test Mode A (grouping proposal) invocation in Visual Studio Copilot Chat
4. Test Mode B (documentation generation) invocation
5. Compare output quality vs. VS Code baseline

**Pass criteria:**
- Agent Skill loads in Visual Studio Copilot Chat window
- Mode A produces grouping proposal matching VS Code output
- Mode B produces module documentation matching VS Code output
- Invocation syntax documented (any VS-specific differences)

**Fail fallback:**
- Document hybrid workflow: VS Code for Mode A/B invocations + Visual Studio for code editing + CI validation
- Provide step-by-step workaround instructions in onboarding checklist
- Add fallback time estimates (+30 min per module for context-switching overhead)

**Owner:** Standards author + pilot .NET developer  
**Estimated Time:** 3 hours

---

## Deliverable 5: Infrastructure Audit

### Objective

Audit existing `.akr/` infrastructure to migrate rather than rebuild; identify hidden dependencies.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Audit `.akr/workflows/` | Standards author | Both workflows documented; migration plan per workflow | 2 hours |
| Add pilot feature tags to `tag-registry.json` | Standards author | `CourseCatalogManagement` and other pilot tags added; `distribute-tag-registry.yml` validates and distributes | 1 hour |
| Extended migration inventory | Standards author | Git grep results, CI/CD pipelines, deployment scripts, .gitmodules references documented | 2 hours |
| Narrow `TEMPLATE_MANIFEST.json` | Standards author | Document deprecated roles; retain only `templateId → version` registry function | 1 hour |
| Document `.akr/` → `validation/` migration plan | Standards author | File-by-file migration checklist; breaking changes identified | 2 hours |

### `.akr/workflows/` Audit Results (From Analysis)

**1. `validate-documentation.yml` — PRIMARY MIGRATION TARGET**
- Already calls `validate_documentation.py` from `core-akr-templates/main/scripts/`
- Already runs Vale with `.akr/.vale.ini` config
- Already uses `tj-actions/changed-files@v41` for diff detection
- Already has Checks API permissions configured
- **Phase 1 action:** ADAPT this workflow (5 changes); do not rebuild from scratch

**2. `distribute-tag-registry.yml` — RETAIN AND LEVERAGE**
- Triggers on `tag-registry.json` changes
- Validates against `tag-registry-schema.json`
- Distributes to application repos automatically
- **Phase 0 action:** Add pilot feature tags; workflow auto-distributes on commit
- **Phase 4 consideration:** Assess whether `tag-registry.json` can evolve into `feature-registry.yaml`

### Extended Inventory Commands

```powershell
# Repository path references
git grep -l '\.akr/'

# CI/CD pipeline configs
Get-ChildItem -Recurse -Include *.yml,*.yaml,azure-pipelines.yml

# Deployment scripts
Get-ChildItem -Recurse -Include *.ps1,*.sh | Select-String -Pattern "\.akr/|akr-mcp-server|validate-docs.py"

# External config management
Get-ChildItem -Recurse -Include appsettings*.json,*.config | Select-String -Pattern "akr|MCP"

# Gitmodule submodule references
git config --file .gitmodules --get-regexp path
```

### `TEMPLATE_MANIFEST.json` Narrowing

**Retain:**
- `templateId → version` mapping for skill-template version coupling
- CI check that Agent Skill references valid `templateId` values

**Deprecate (document in CHANGELOG):**
- Template selection logic (moved to Agent Skill + `copilot-instructions.md`)
- Complexity scoring (replaced by `project_type` field in `modules.yaml`)
- File-centric routing (replaced by module-centric routing)

---

## Deliverable 6: Cost Modeling and Budget Approval

### Objective

Establish monthly premium request budget baseline and monitoring thresholds.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Model premium request consumption | Standards author | Requests per module calculated; monthly cost estimated for pilot team | 2 hours |
| Manual consumption delta measurement | Standards author | Before/after billing dashboard snapshots captured for Tests 1 and 3 | 1 hour |
| Review GitHub billing dashboard | Standards lead | Current usage baseline established; alert thresholds configured | 1 hour |
| Enable monitoring in pilot `.akr-config.json` | Standards author | `monitoring.enabled: true`; `trackMetrics: ["generation-time", "validation-results"]` | 30 min |
| Establish management approval | Standards lead | Monthly budget approved; overage escalation process documented | External |
| Document cost baseline collection | Standards author | Plan to collect generation-time data across first 10 module runs | 30 min |

### Cost Model Inputs

- **Agent mode sessions:** ~X requests per module (to be measured in Test 1)
- **Coding agent invocations:** ~Y requests per module (estimate; refined in Phase 2.5)
- **Pilot team size:** Z developers
- **Estimated modules per month:** Based on pilot project inventory

### Monitoring Configuration

```yaml
# .akr-config.json for pilot project
{
  "monitoring": {
    "enabled": true,
    "trackMetrics": [
      "generation-time",
      "validation-results"
    ],
    "reportingEndpoint": null  # Local collection only in Phase 0
  }
}
```

### Success Metrics

- Monthly cost projection documented
- Billing alert configured at 80% of approved budget
- Generation-time baseline collection plan established

---

## Archive Prerequisites (Before `akr-mcp-server` Archive)

### Objective

Preserve validation baselines and tests currently located in `akr-mcp-server` before archiving. Ensure clean separation with no security or content loss risks.

### Critical Sequencing

**These tasks MUST complete before `akr-mcp-server` is archived.** If archived prematurely:
- Phase 1 cannot port validation logic (test files become read-only)
- Phase 2.5 acceptance criteria become unreferenceable
- Charter divergence risk if `akr_content/` differs from `core-akr-templates` charters

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| **Reconcile `akr_content/` charters** | Standards author | Compare `akr-mcp-server/akr_content/charters/` vs. `core-akr-templates/.akr/charters/`; merge any updates | 2 hours |
| Copy `tests/test_pipeline_e2e.py` | Standards author | File copied to `core-akr-templates/tests/` | 30 min |
| Copy `src/tools/validation_library.py` | Standards author | File copied to `core-akr-templates/.akr/scripts/` | 30 min |
| Copy `tests/test_validation_library.py` | Standards author | File copied to `core-akr-templates/tests/` | 30 min |
| **Audit GitHub Actions secrets** | Infrastructure lead | List all secrets used in `.github/workflows/`; revoke or document post-archive | 1 hour |
| **Add deprecation notice to README** | Standards author | Update `akr-mcp-server` README with redirect to `core-akr-templates` and archival notice | 30 min |
| **Add deprecation notice for setup scripts** | Standards author | Update `core-akr-templates` README noting `setup.ps1`/`setup.sh` are deprecated; remove from docs | 30 min |
| Update workflow download URLs | Standards author | Broken downloads removed or replaced before archive | 30 min |

### Archival Checklist

- [ ] All charter content reconciled (no divergence)
- [ ] Test files copied to `core-akr-templates/tests/`
- [ ] Validation library copied to `core-akr-templates/.akr/scripts/`
- [ ] GitHub Actions secrets audited and revoked
- [ ] README updated with archival notice and redirect
- [ ] Deprecated setup scripts documented in `core-akr-templates`
- [ ] Repository marked read-only
- [ ] Submodule references in other repos noted (will break; redirect in archived README provides mitigation)

### Notes

- These files are referenced in Phase 1 and Phase 2.5 acceptance criteria.
- Archive must not proceed until all checklist items complete.
- Legal review (Test 5) should be consulted before revoking secrets.

---

## Phase 0 Retrospective

### Retrospective Agenda

1. **What went well:** Which deliverables completed faster than estimated?
2. **What took longer:** Which tasks exceeded time estimates and why?
3. **Assumption validation:** Did pre-pilot tests uncover unexpected issues?
4. **Fallback triggers:** Did any test fail, requiring fallback architecture?
5. **Phase 1 readiness:** Are all prerequisites truly complete?

### Retrospective Outputs

- **Phase 0 completion metrics:** Actual time vs. estimated time per deliverable
- **Phase 1 authorization:** Standards lead sign-off to proceed
- **Risk register updates:** Any new risks identified during tests
- **Budget confirmation:** Approved monthly cost baseline documented

---

## Risk Register (Phase 0 Specific)

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| Charter compression loses critical rules | 🔴 High | 🟡 Medium | Validate each condensed charter against `test_pipeline_e2e.py` acceptance test |
| Test 5 (legal sign-off) delays entire timeline | 🔴 High | 🟡 Medium | Start legal request immediately; run Tests 1-4 in parallel |
| Test 1 (code analysis) fails multiple runs | 🟡 Medium | 🟠 Low | Fallback to deterministic `CodeAnalyzer` + hosted MCP governance |
| Test 2 (hosted MCP) unavailable at current tier | 🟡 Medium | 🟠 Low | Fallback to `.github/copilot-instructions.md` with condensed charter |
| Test 3 (large module) shows truncation | 🟡 Medium | 🟠 Low | Reduce `max_files` guidance to 5 for large-file modules |

---

## Success Criteria Summary

Phase 0 succeeds when:

✅ 3 condensed charters at ≤2,500 tokens each  
✅ Agent Skill Mode A + Mode B authored and validated  
✅ `modules.yaml` schema defined and examples created  
✅ 5/5 pre-pilot tests PASS or have documented fallback  
✅ Infrastructure audit complete with migration inventory  
✅ Cost model approved by management  
✅ Pilot feature tags added to `tag-registry.json`  

**Exit gate:** Phase 0 retrospective complete; Phase 1 work authorized by standards lead.

---

**Next Phase:** [Phase 1: Foundation](PHASE_1_FOUNDATION.md)

**Related Documents:**
- [Implementation Plan Overview](IMPLEMENTATION_PLAN_OVERVIEW.md)
- [Implementation-Ready Analysis](../akr_implementation_ready_analysis.md) — Parts 3, 5, 11, 12
