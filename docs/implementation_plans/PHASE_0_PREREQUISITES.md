# Phase 0: Prerequisites — Implementation Plan

**Duration:** 1-2 weeks  
**Team:** Standards team (1 FTE) + pilot project representative  
**Status:** 🔴 BLOCKING GATE — Phase 1 cannot begin until complete

---

## Overview

Phase 0 establishes the minimal viable prerequisites for the AKR module-based documentation system. Every deliverable in this phase is a proven blocker—charter compression prevents context saturation, pre-pilot tests validate foundational assumptions, and infrastructure audit prevents rework.

**Critical Path:** Charter compression → Pre-pilot Test 1 (code analysis) → Pre-pilot Test 7 (Code Skills availability) → remaining tests in parallel

---

## Acceptance Criteria

Phase 0 is complete when:

1. ✅ All 3 condensed charters created and validated at target token counts
2. ✅ Agent Skill authored and validated with Mode A + Mode B + Mode C
3. ✅ `modules.yaml` schema defined and example created
4. ✅ All 7 pre-pilot tests PASS **or** have documented fallback architectures
5. ✅ Infrastructure audit complete with migration inventory
6. ✅ Cost baseline model established and budget approved
7. ✅ Monitoring enabled in pilot `.akr-config.json`
8. ✅ Pilot project business capability tags added to `tag-registry.json`
9. ✅ Registered repository registry established for downstream skill updates
10. ✅ Archive prerequisites completed (tests and validation baselines copied)

**Exit Gate:** All items above checked; Phase 0 retrospective complete; Phase 1 authorized by standards lead **in writing** (GitHub comment, email, or approval record).

---

## Deliverable 1: Charter Compression

### Objective

Compress full charters (~11,000 tokens each) to condensed "dense summary" versions (~2,500 tokens each) that preserve governance rules while removing explanatory prose.

### Why Blocking

Backend charter at ~11,000 tokens + lean baseline template at ~7,000 tokens = ~18,000 tokens **before any source files load**. With 5 source files in a typical module, total context exceeds 25,000 tokens—guaranteed degradation or failure.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Compress `AKR_CHARTER_BACKEND.md` → `copilot-instructions/backend-service.instructions.md` | Standards author | ≤2,500 tokens; all required sections preserved; all marker syntax preserved; all quality thresholds preserved | 3-4 hours |
| Compress `AKR_CHARTER_UI.md` → `copilot-instructions/ui-component.instructions.md` | Standards author | ≤2,500 tokens; component-specific section requirements preserved | 2-3 hours |
| Compress `AKR_CHARTER_DB.md` → `copilot-instructions/database.instructions.md` | Standards author | ≤1,500 tokens; object-level documentation rules preserved | 1-2 hours |
| Validate compression ratio | Standards author | All 3 charters achieve ≤23% of original token count | 30 min |
| Cross-reference full charters | Standards author | Each condensed charter includes "Full charter: [link]" reference | 15 min |
| Validate compressed charters with tokenizer check | Standards author | Use tiktoken GPT-4 encoder consistently; **also count tokens using a GPT-4o tokenizer** to confirm budgets hold for Copilot (GPT-4o) users, not only Claude users | 30 min |

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

Create `.github/skills/akr-docs/SKILL.md` encoding Mode A (grouping proposal), Mode B (documentation generation), and Mode C (interactive HITL completion for existing drafts with unresolved ❓ markers) workflows.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Author `SKILL.md` with Mode A workflow | Standards author | Full specification from Part 5 of analysis document implemented | 2 hours |
| Author `SKILL.md` with Mode B workflow | Standards author | Loads condensed charter based on `project_type`; references `modules.yaml` | 2 hours |
| Author `SKILL.md` with Mode C workflow | Standards author | Enumerates unresolved `❓` markers; guides interactive in-editor resolution; re-runs validator after each batch | 2 hours |
| Add prerequisite check in Mode B | Standards author | Mode B stops if `modules.yaml` status is `draft` | 30 min |
| Document skill invocation patterns | Standards author | "propose module groupings" → Mode A; "generate documentation for X" → Mode B; "walk me through ❓ sections" → Mode C | 1 hour |
| Validate skill loads in VS Code | Pilot rep | Skill appears in agent mode skill list; all three modes trigger correctly | 15 min |
| Add `SKILL_VERSION` header to `SKILL.md` | Standards author | First line is `<!-- SKILL_VERSION: v1.0.0 -->` matching release tag | 5 min |
| Document version bump requirement | Standards author | CONTRIBUTING or release checklist states version must be updated on every skill change | 10 min |
| Add frontmatter block: `disable-model-invocation`, `optimized-for`, `tested-on` | Standards author | Frontmatter present above `SKILL_VERSION` comment; syntax valid per Agent Skills spec | 30 min |
| Add self-reporting block as first SKILL body instruction | Standards author | SKILL body begins with `CRITICAL: When this skill is loaded, begin EVERY response with: ✅ akr-docs INVOKED AND STEPS EXECUTED — Steps followed: 1. [step] — completed...` | 30 min |
| Add `<!-- akr-generated -->` metadata header before validation/write steps in Mode B | Standards author | Mode B writes metadata header to draft output before validator run and before file write; block includes `skill`, `mode`, `template`, `steps-completed`, `generated-at` fields | 30 min |
| Create `SKILL-COMPAT.md` skeleton | Standards author | File present at `.github/skills/akr-docs/SKILL-COMPAT.md`; contains: (1) model compatibility matrix with columns Model, Pass Rate, Known Issues, Workaround; rows for `claude-sonnet-4-6` and `gpt-4o` populated after Phase 0 eval runs; (2) invocation-surface matrix including `coding-agent`, `custom-agent`, and `code-skills` (`run_skill_script`) rows; (3) "Future Enhancement Paths" section with placeholder row for "Dynamic resource-based skill hydration" (see note below) | 1 hour |

> **`SKILL-COMPAT.md` — Future Enhancement Paths section:** Include a second table in the skeleton
> with columns: Enhancement, Description, Trigger Condition, Estimated Effort. Add one placeholder
> row:
>
> | Enhancement | Description | Trigger Condition | Estimated Effort |
> |---|---|---|---|
> | Dynamic resource-based skill hydration | Replace static condensed charters and `benchmark.json` with `@skill.resource` decorated functions that serve live data at read time; requires custom Python `SkillsProvider` | Static charter staleness observed in pilot OR `benchmark.json` thresholds become stale during Phase 4 multi-repo runs | Medium — new Python agent layer required |
>
> This placeholder requires no action in Phase 0. It documents the upgrade path so it is not
> re-discovered independently if the problem emerges during pilot.

### SKILL.md Header Format

```markdown
---
name: akr-docs
description: >
  Generate AKR module documentation following charters and templates.
  Invoke explicitly via /akr-docs [mode-a | mode-b | mode-c] [target].
disable-model-invocation: true
optimized-for: claude-sonnet-4-6
tested-on:
  - claude-sonnet-4-6   # ✅ pass rate ≥90% (Phase 0 baseline)
  - gpt-4o              # ⚠️ ~75%, Mode B truncation on large modules (Phase 0 baseline)
user-invocable: true
skill-version: 1.0.0
---
<!-- SKILL_VERSION: v1.0.0 -->
<!-- Distribution: Managed by core-akr-templates. Do not edit this file directly in application repos. -->
<!-- Updates: Delivered automatically via PR when core-akr-templates releases a new version. -->

CRITICAL: When this skill is loaded, begin EVERY response with the following confirmation block:
✅ akr-docs INVOKED AND STEPS EXECUTED
Steps followed: 1. [first step] — completed | 2. [second step] — completed | ...
Do not skip this block under any circumstances.

# AKR Documentation Agent Skill
...
```

The version header makes drift visible and gives distribution automation a reliable verification point after merge.

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
6. Write `<!-- akr-generated -->` metadata header block to the top of the draft output
7. Run `validate_documentation.py` against draft
8. Write to `doc_output` path on feature branch
9. Open draft PR with content review checklist

> **Phase 0 execution note:** During pre-pilot tests in this phase, `validate_documentation.py` is not yet implemented (built in Phase 1). Use the manual checklist in Tests 1 and 3 to assess section completeness and metadata/header presence.

### Mode B — Required Metadata Header (Pre-Validation Gate)

Before validation and before writing the final file, Mode B **must** write the following header to the top of the generated draft document. This is checked by `validate_documentation.py` in Phase 1+ and its absence is a validator failure.

```markdown
<!-- akr-generated
skill: akr-docs
skill-version: v1.0.0
mode: B
template: {name of template used}
charter: {condensed charter filename loaded}
modules-yaml-status: approved
steps-completed: 1,2,3,4,5,6,7,8,9
generated-at: {ISO 8601 timestamp}
-->
```

**Validator failure message when absent:** `"AKR metadata header missing — skill may not have been properly invoked. Re-run using /akr-docs mode-b [module]."`

**Distribution note:** This instruction is part of the SKILL.md body and is therefore automatically distributed to all registered repositories via `distribute-skill.yml` when a new skill version is released. No per-project action required.

### Mode C Workflow Summary

Mode C replaces the original `/docs.interview` slash command. It is invoked on existing documents — not during initial generation — to resolve unresolved `❓` markers interactively.

1. Read the existing documentation file; enumerate all unresolved `❓` markers grouped by section
2. Present one `❓` item at a time with local section context
3. Ask targeted clarification questions; propose replacement text grounded in code evidence
4. Apply accepted edits immediately; mark unresolved items as `DEFERRED` with rationale and owner
5. Re-run `validate_documentation.py` after each section or batch
6. Summarize: total `❓` resolved, remaining `DEFERRED` items, any blockers requiring domain-owner input
7. Open/update draft PR with HITL completion checklist

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
  .akr/
    schemas/
      modules-schema.json       (NEW — does not exist yet; authored in Phase 1 Deliverable 5)
  examples/
    modules.yaml              (TrainingTracker.Api reference)
    modules-ui-example.yaml   (UI project reference)
```

> **Path note:** `modules-schema.json` is defined here in Phase 0 as a schema specification but physically created in Phase 1 Deliverable 5 alongside the other existing schemas (`akr-config-schema.json`, `tag-registry-schema.json`, `consolidation-config-schema.json`) in `.akr/schemas/`. The Phase 0 deliverable for this item is the schema field specification document, not the JSON file itself.

---

## Deliverable 4: Pre-Pilot Validation Tests

### Objective

Validate seven foundational assumptions before Phase 1 investment. Each test must PASS or have a documented fallback architecture.

### Test Execution Sequence

**Critical dependencies:**
- **Test 5 (Legal/Compliance):** Start on Day 1 (parallel) — longest lead time (2-6 weeks external dependency)
- **Test 1 → Test 7:** Sequential — Test 1 validates charter compression works; Test 7 validates Code Skills availability before Phase 3 assumptions are relied on
- **Test 2:** Independent — can run parallel with Test 1
- **Test 4:** Requires Tests 1-3 and 7 to pass first (needs functional agent for cost baseline)
- **Test 6 (Visual Studio):** Can run parallel after Test 1 passes

**Execution order:** Start Test 5 immediately → Test 1 → Test 7 → (Test 2 + Test 3 + Test 6 in parallel) → Test 4

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
- Phase 0 completeness assessment recorded using manual checklist (validator integration begins in Phase 1)

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
5. Evaluate whether `@skill.resource` dynamic resource hydration is available in the current SDK/toolchain as a replacement path for static charter distribution

**Pass criteria:**
- Context source visible in settings
- Available in both VS Code and Visual Studio
- Context loads automatically on session start
- Condensed charters accessible without manual file loading
- `@skill.resource` feasibility status documented (available now vs. defer), including constraints and migration effort estimate

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
4. Use manual validation checklist in Phase 0 (script integration deferred to Phase 1)

**Pass criteria:**
- All MODULE-required sections present
- Module Files section lists all 8 files
- Operations Map not truncated
- Business Rules table complete
- Data Operations section covers all reads and writes
- No "..." or "[content omitted]" artifacts
- Metadata header and required YAML front matter fields present (manual check in Phase 0)

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

### Test 7: Code Skills Availability

**What it validates:** Agent Framework Code Skills (`@skill.script` + `run_skill_script`) and script approval surfaces are available in the target VS Code Copilot environment before Phase 3 depends on them.

**Prerequisite:** Test 1 complete (skill baseline available)

**Method:**
1. Install/pin `agent-framework` package in an isolated test environment
2. Create minimal `@skill.script` function (no side effects)
3. Verify invocation via `run_skill_script` from the coding agent flow
4. Enable `require_script_approval=True` and verify whether `user_input_requests` approval prompts are surfaced in VS Code Copilot Chat
5. Reject one request and confirm behavior and logs

**Pass criteria:**
- `@skill.script` registration succeeds using Python SDK
- `run_skill_script` invocation succeeds for the test function
- Approval prompt behavior is confirmed and documented (supported/unsupported + UX surface)
- Rejection behavior documented with evidence (alternative path vs. informative failure)

**Fail fallback:**
- Record Option D as unavailable for current environment
- Default Phase 3 path to Option B/C (GitHub Actions or Azure-hosted approach) for failure modes that require automation
- Keep deterministic Phase 1/2 gates unchanged

**Owner:** Standards author  
**Estimated Time:** 30-45 min

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

## Deliverable 5A: Registered Repos Registry

### Objective

Create `registered-repos.yaml` in `core-akr-templates` as the source of truth for which application repositories receive automated `SKILL.md` updates.

### Why Needed Before Phase 1

Phase 1 distribution cannot target repositories without a maintained registry. Authoring this in Phase 0 ensures the first pilot can be updated immediately after onboarding.

### Schema

```yaml
# core-akr-templates/registered-repos.yaml
schema_version: "1.0"
distribution:
  skill_source_path: ".github/skills/akr-docs/SKILL.md"
  pr_title_template: "chore: update AKR Agent Skill to {version}"
  pr_body_template: "automated-skill-update"
  target_branch: "main"
  auto_assign_reviewers: true

repos:
  - org: reyesmelvinr-emr
    name: TrainingTracker.Api
    skill_path: .github/skills/akr-docs/SKILL.md
    onboarded: 2026-03-01
    standards_version: v1.0.0
    team_contact: "@tech-lead-handle"
    compliance_mode: pilot
```

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Create `registered-repos.yaml` with pilot project entry | Standards author | File present at repo root; schema validates; `TrainingTracker.Api` is first entry | 20 min |
| Create PR body template `automated-skill-update.md` | Standards author | Template present at `.github/pr-templates/`; placeholders documented | 20 min |
| Document registry maintenance procedure | Standards author | CONTRIBUTING updated with "add repo to registry during onboarding" | 15 min |
| Add `registered-repos.yaml` to CODEOWNERS | Standards author | Standards lead approval required for add/remove changes | 10 min |

### CODEOWNERS Addition

```text
# Skill distribution registry — standards lead approval required for all changes
registered-repos.yaml   @org/standards-lead
```

### Output Locations

```
core-akr-templates/
  registered-repos.yaml                            (NEW)
  .github/
    pr-templates/
      automated-skill-update.md                    (NEW)
```

---

## Deliverable 5B: Skill Evaluation Framework

### Objective

Establish a baseline eval suite and benchmark record for `akr-docs` skill performance before Phase 1 authoring begins. Results populate `SKILL-COMPAT.md` and `benchmark.json`; they also define the acceptance thresholds for subsequent phase eval runs.

### Why Phase 0

Pre-pilot Tests 1 and 3 already run the skill against real inputs. Adding structured assertions to those runs costs minimal time and produces the Phase 1 baseline automatically - without requiring a separate eval pass later.

### Eval Directory Structure

Create the following directory and files in `core-akr-templates`:

```
evals/
  cases/
    mode-a-standard.yaml         # Mode A assertions for Test 1 standard run
    mode-b-coursedomain.yaml     # Mode B assertions matching courses_service_doc.md
    mode-b-large-module.yaml     # Mode B stress test: 8-file module, no truncation
  datasets/
    coursedomain-files/          # Input files used in Pre-pilot Test 1
  benchmark.json                 # Pass rates + token counts per model version
```

### `benchmark.json` Schema

```json
{
  "last-updated": "YYYY-MM-DD",
  "schema-version": "1.0",
  "models": {
    "claude-sonnet-4-6": {
      "mode-a-standard":       { "pass-rate": null, "avg-tokens": null },
      "mode-b-coursedomain":   { "pass-rate": null, "avg-tokens": null },
      "mode-b-large-module":   { "pass-rate": null, "avg-tokens": null, "known-issue": null }
    },
    "gpt-4o": {
      "mode-a-standard":       { "pass-rate": null, "avg-tokens": null },
      "mode-b-coursedomain":   { "pass-rate": null, "avg-tokens": null },
      "mode-b-large-module":   { "pass-rate": null, "avg-tokens": null, "known-issue": null }
    },
    "coding-agent": {}
  }
}
```

> `null` values are populated after each phase eval run. Do not publish to `core-akr-templates` main branch until at least one run is complete.

### `mode-b-coursedomain.yaml` Assertions (Sample)

```yaml
case: mode-b-coursedomain
description: Mode B output for CourseDomain must match courses_service_doc.md structure
inputs:
  module: CourseDomain
  project_type: api-backend
  files: [datasets/coursedomain-files/]
assertions:
  - section_present: "Module Files"
  - section_present: "Operations Map"
  - section_present: "Architecture Overview"
  - section_present: "Business Rules"
  - section_present: "Data Operations"
  - yaml_front_matter_field: businessCapability
  - yaml_front_matter_field: project_type
  - metadata_header_present: true
  - no_truncation_markers: true
  - self_reporting_block_in_response: true
pass_threshold: 10/10
```

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Create `evals/` directory structure in `core-akr-templates` | Standards author | All directories and placeholder files present | 30 min |
| Author `mode-a-standard.yaml` assertions | Standards author | Assertions match Pre-pilot Test 1 acceptance criteria exactly | 1 hour |
| Author `mode-b-coursedomain.yaml` assertions | Standards author | Assertions reference `courses_service_doc.md` sections; includes `metadata_header_present` and `self_reporting_block_in_response` assertions | 1 hour |
| Author `mode-b-large-module.yaml` assertions | Standards author | Includes 8-file boundary check and no-truncation assertion | 1 hour |
| Create `benchmark.json` with null baseline | Standards author | File present; schema valid; all `null` values to be populated after Tests 1 and 3 | 30 min |
| Run eval cases during Pre-pilot Test 1 | Standards author | Assertions checked against output; results recorded in `benchmark.json` | Part of Test 1 (no additional time) |
| Run eval cases during Pre-pilot Test 3 | Standards author | Large-module assertions checked; results recorded | Part of Test 3 (no additional time) |
| Populate `SKILL-COMPAT.md` with Phase 0 results | Standards author | Model compatibility matrix rows for `claude-sonnet-4-6` and `gpt-4o` populated with actual pass rates | 1 hour |

### Gate Dependency

`mode-b-coursedomain.yaml` requires the condensed backend charter (Deliverable 1) to exist before it can be written. Complete charter compression before authoring eval cases.

**Execution sequence (required):** charter compression → `SKILL.md` authoring (Mode A/B/C + metadata/self-reporting) → pre-pilot eval runs (Tests 1 and 3) → populate `benchmark.json` and `SKILL-COMPAT.md` with actual results → Phase 0 exit gate sign-off.

`benchmark.json` population is a final exit-gate task, not a parallel prerequisite for earlier Deliverable 5B authoring.

### Output Locations

```
core-akr-templates/
  evals/
    cases/
      mode-a-standard.yaml         (NEW)
      mode-b-coursedomain.yaml     (NEW)
      mode-b-large-module.yaml     (NEW)
    datasets/
      coursedomain-files/          (NEW — copy from pre-pilot test inputs)
    benchmark.json                 (NEW — null baseline)
  .github/
    skills/
      akr-docs/
        SKILL-COMPAT.md            (NEW — populated after Phase 0 eval runs)
```

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

- **Agent mode sessions:** 12-20 premium requests per module (provisional; calibrate with Test 1 and Test 3)
- **Coding agent invocations:** 15-30 premium requests per module (provisional; refine in Phase 2.5)
- **Pilot team size:** 3-5 developers (initial pilot assumption)
- **Estimated modules per month:** 10-20 module runs/month during pilot onboarding
- **Budget method:** Use GitHub Copilot Business dashboard + per-user seat cost + observed premium request usage to produce low/base/high monthly projection for management approval

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
| Document non-portable legacy scripts | Standards author | `validate_traceability.py` and `analyze_doc_impact.py` explicitly marked as legacy-architecture scripts requiring refactor before migration | 20 min |

### Archival Checklist

- [ ] All charter content reconciled (no divergence)
- [ ] Test files copied to `core-akr-templates/tests/`
- [ ] Validation library copied to `core-akr-templates/.akr/scripts/`
- [ ] GitHub Actions secrets audited and revoked
- [ ] README updated with archival notice and redirect
- [ ] Deprecated setup scripts documented in `core-akr-templates`
- [ ] Legacy scripts `validate_traceability.py` and `analyze_doc_impact.py` marked non-portable (old `docs/features` + `docs/testing` assumptions) and excluded from direct migration
- [ ] Repository marked read-only
- [ ] Submodule references in other repos noted (will break; redirect in archived README provides mitigation)

### Notes

- These files are referenced in Phase 1 and Phase 2.5 acceptance criteria.
- Archive must not proceed until all checklist items complete.
- Legal review (Test 5) should be consulted before revoking secrets.
- `validate_traceability.py` and `analyze_doc_impact.py` from `akr-mcp-server` are not migration candidates without refactor to the module/database/feature hierarchy and current YAML front matter semantics.

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
- **Eval baseline published:** `benchmark.json` populated with Phase 0 pass rates for `claude-sonnet-4-6` and `gpt-4o`; `SKILL-COMPAT.md` rows populated; both committed to `core-akr-templates` before Phase 1 begins

---

## Risk Register (Phase 0 Specific)

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| Charter compression loses critical rules | 🔴 High | 🟡 Medium | Validate each condensed charter against `test_pipeline_e2e.py` acceptance test |
| Test 5 (legal sign-off) delays entire timeline | 🔴 High | 🟡 Medium | Start legal request immediately; run Tests 1-4 and 7 in parallel where dependencies allow |
| Test 1 (code analysis) fails multiple runs | 🟡 Medium | 🟠 Low | Fallback to deterministic `CodeAnalyzer` + hosted MCP governance |
| Test 2 (hosted MCP) unavailable at current tier | 🟡 Medium | 🟠 Low | Fallback to `.github/copilot-instructions.md` with condensed charter. Secondary long-term fallback: dynamic `@skill.resource` hydration via custom `SkillsProvider` (tracked in `SKILL-COMPAT.md` Future Enhancement Paths) |
| Test 3 (large module) shows truncation | 🟡 Medium | 🟠 Low | Reduce `max_files` guidance to 5 for large-file modules |
| Test 7 (Code Skills availability) unsupported in current VS Code Copilot environment | 🟡 Medium | 🟠 Low | Mark Option D unavailable; document evidence; use Option B/C if Phase 3 is authorized |

---

## Success Criteria Summary

Phase 0 succeeds when:

✅ 3 condensed charters at ≤2,500 tokens each  
✅ Agent Skill Mode A + Mode B + Mode C authored and validated  
✅ `modules.yaml` schema defined and examples created  
✅ 7/7 pre-pilot tests PASS or have documented fallback  
✅ Infrastructure audit complete with migration inventory  
✅ `registered-repos.yaml` created with pilot repo entry  
✅ Cost model approved by management  
✅ `SKILL.md` frontmatter includes `disable-model-invocation: true`, `optimized-for: claude-sonnet-4-6`, `tested-on` fields, and self-reporting CRITICAL block  
✅ `evals/` directory with 3 eval cases and populated `benchmark.json` baseline committed to `core-akr-templates`  
✅ `SKILL-COMPAT.md` skeleton includes "Future Enhancement Paths" table with dynamic resource upgrade path documented  
✅ Pilot feature tags added to `tag-registry.json`  

**Exit gate:** Phase 0 retrospective complete; Phase 1 work authorized by standards lead **in writing** (GitHub comment, email, or approval record) before Phase 1 begins.

---

**Next Phase:** [Phase 1: Foundation](PHASE_1_FOUNDATION.md)

**Related Documents:**
- [Implementation Plan Overview](IMPLEMENTATION_PLAN_OVERVIEW.md)
- [Implementation-Ready Analysis](../akr_implementation_ready_analysis.md) — Parts 3, 5, 11, 12
