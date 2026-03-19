# Phase 2.5: Copilot Coding Agent Spike — Implementation Plan

**Duration:** 1 week  
**Team:** Standards team (0.5 FTE) + 1 developer for validation  
**Prerequisite:** Phase 2 complete; pilot retrospective shows positive metrics  
**Target:** Binary PASS/FAIL decision with documented recommendation

---

## Overview

Phase 2.5 tests whether the GitHub Copilot coding agent (issue-to-PR automation) meets all acceptance criteria for module documentation generation **without custom infrastructure**. This is a binary gate: if the coding agent passes, Phase 3 custom automation is unnecessary; if it fails with documented shortcomings, Phase 3 is authorized to address only those specific failure modes.

**Critical Decision:** This phase determines whether Phase 3 happens at all.

---

## Acceptance Criteria

Phase 2.5 is complete when:

1. ✅ GitHub Issue template created for module documentation requests
2. ✅ 3 test issues assigned to Copilot coding agent
3. ✅ All acceptance criteria tested (from `test_pipeline_e2e.py`)
4. ✅ Results documented: PASS/FAIL per criterion
5. ✅ Context ceiling tested (8-file module with 2,000+ LOC)
6. ✅ Premium request consumption measured
7. ✅ Go/no-go recommendation documented
8. ✅ Phase 3 authorization (if FAIL) or Phase 3 skip (if PASS)
9. ✅ `<!-- akr-generated -->` metadata header present in all coding agent PR outputs (confirms skill ran to completion in async context)
10. ✅ `.akr/logs/session-*.jsonl` hook log handling follows: "Hard gate only when Copilot hook support is confirmed in Phase 1; otherwise record as known gap with evidence and continue."
11. ✅ SSG pass sequence completes in background execution context:
   - All 7 (or 8 if split) passes complete without manual developer intervention
   - `passes-completed` field in PR output `<!-- akr-generated -->` header contains all expected pass numbers
   - If `pass-timings-seconds` is unavailable in the coding agent surface, this is recorded as a KNOWN-GAP (not a FAIL); wall-clock time is estimated from PR open timestamp minus issue assignment timestamp
   - Total estimated generation time recorded in test results
   - Slow-generation events (>45 min) documented if they occur

**Exit Gate:** Binary decision documented; management approves recommendation; proceed to Phase 3 (if authorized) or Phase 4 (if skipped).

---

## Why Phase 2.5 Exists

**From analysis:**
> "The Copilot coding agent has a context window advantage (multi-step task, not single load) and zero infrastructure cost. It must be tested before investing in Azure Function infrastructure. Phase 3 is authorized **only** if Phase 2.5 documents specific failure modes."

**Strategic rationale:**
- Coding agent is **free** (included in Copilot Business/Enterprise)
- No infrastructure to maintain
- Can follow `akr-docs` skill workflow instructions embedded in issue templates and repository skill files
- Multi-turn conversation model may handle large modules better than single-shot agent mode
- If it works, Phase 3 is unnecessary

---

## Deliverable 1: GitHub Issue Template

### Objective

Create issue template that provides all context needed for coding agent to generate module documentation.

### Template Structure

```markdown
---
name: Generate Module Documentation
about: Request documentation for a module using AKR standards
title: 'docs: [ModuleName] module documentation'
labels: documentation, akr-docs, copilot-task
assignees: ''
---

## Module Information

- **Module Name:** [e.g., CourseDomain]
- **Project Type:** [api-backend | ui-component | microservice | general]
- **Business Capability:** [e.g., CourseCatalogManagement] (PascalCase from tag-registry.json)
- **Files in Module:** [List all files, or reference modules.yaml entry]

## Documentation Mode

- **Generation mode:** [Full - first-time generation | Incremental - update after code change]
   Default: Full for new modules; Incremental for modules with existing committed draft at docs/modules/.akr/.
- **Changed files (Incremental only):** [List files changed since last Mode B run]

## Documentation Requirements

This module must be documented following AKR module documentation standards:

1. **Load context:**
   - Read `modules.yaml` to identify module files and metadata
   - Mapping rule: use `modules.yaml.modules[].businessCapability` directly for YAML front matter `businessCapability`; do not remap from legacy `feature` fields in older docs
   - Load condensed charter from `copilot-instructions/[project_type].instructions.md`
   
2. **Generate documentation:**
   - Use Agent Skill Mode B workflow
   - Apply `lean_baseline_service_template.md` (module variant) for api-backend
   - Or `ui_component_template.md` (module variant) for ui-component
   
3. **Required sections (MODULE docs):**
   - Module Files (list all files with roles)
   - Operations Map (all operations across all files)
   - Architecture Overview (full-stack text diagram)
   - Business Rules (with "Why It Exists" + "Since When" columns)
   - Data Operations (all reads and writes)
   - Questions & Gaps (populated with open items)
   - YAML front matter: businessCapability, feature, layer, project_type, status

### Example YAML front matter (MODULE docs)

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
   
4. **Transparency markers:**
   - Mark AI-inferred content with 🤖
   - Mark sections requiring human input with ❓
   - Provide DEFERRED placeholders where information is not available
   
5. **Validation:**
   - Run `validate_documentation.py --file [output] --fail-on needs`
   - Resolve or mark DEFERRED any validation failures

**Validator output contract (v1.x):**
- `.summary.total_errors` (number)
- `.summary.total_warnings` (number)
- `.summary.average_completeness` (0..1)

A CI smoke step should assert these fields exist on every run.
   
6. **Output:**
   - Write to `docs/modules/[ModuleName]_doc.md`
   - Open draft PR with title: "docs: [ModuleName] module documentation"
   - Include PR checklist from Agent Skill Mode B

## Acceptance Criteria

- [ ] All MODULE-required sections present
- [ ] Module Files section lists all files with correct roles
- [ ] Operations Map covers all operations in all files
- [ ] Architecture diagram shows full stack
- [ ] Business Rules table includes "Why It Exists" column
- [ ] Data Operations covers all reads and writes
- [ ] validate_documentation.py passes with zero errors
- [ ] No section truncation or omission

---

**Note for Copilot Coding Agent:**
Use Agent Skill `akr-docs` Mode B workflow. Load condensed charter for [project_type]. Read all files listed in `modules.yaml` for this module. Generate complete documentation with all required sections.
```

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Draft issue template | Standards author | All required fields and acceptance criteria included | 1 hour |
| Add to `.github/ISSUE_TEMPLATE/` | Standards author | Template available when creating new issue | 15 min |
| Test template clarity | Developer | All fields understood; no ambiguity | 30 min |
| Document invocation pattern | Standards author | README explains how to assign issue to coding agent | 30 min |

---

## Deliverable 2: Test Issue Execution

### Objective

Create 3 test issues covering different module types and complexity levels; assign to Copilot coding agent; measure results.

### Test Cases

**IMPORTANT:** Reuse modules from Phase 2 pilot (CourseDomain, CourseManagementUI, EnrollmentDomain) rather than creating new fixtures. This tests real-world pilot results and validates consistency with Phase 2 baseline across both backend and UI workflows.

#### Test Case 1: Standard Backend Module (Baseline)

**Module:** `CourseDomain` (5 files, ~800 LOC total) — **reused from Phase 2 Deliverable 2**  
**Project Type:** `api-backend`  
**Expected Behavior:** Agent generates complete documentation with all sections; passes validation  
**Acceptance Criteria:** Criteria 1-9 and 11 pass; Criterion 10 handling follows: "Hard gate only when Copilot hook support is confirmed in Phase 1; otherwise record as known gap with evidence and continue."

#### Test Case 2: UI Component Module

**Module:** `CourseManagementUI` (Page + components + hook + types) — **reused from Phase 2 UI pilot**  
**Project Type:** `ui-component`  
**Expected Behavior:** Agent generates complete documentation using the UI module variant; passes validation  
**Acceptance Criteria:** Criteria 1-9 and 11 pass; Criterion 10 handling follows: "Hard gate only when Copilot hook support is confirmed in Phase 1; otherwise record as known gap with evidence and continue." (UI path)

#### Test Case 3: Large Backend Module (Stress Test)

**Module:** `EnrollmentDomain` (5 files, ~1,000 LOC total) — **reused from Phase 2 Deliverable 6**  
**Project Type:** `api-backend`  
**Expected Behavior:** Agent handles larger module; no section truncation  
**Acceptance Criteria:** Criteria 1-9 and 11 pass + no truncation; Criterion 10 handling follows: "Hard gate only when Copilot hook support is confirmed in Phase 1; otherwise record as known gap with evidence and continue."

### Execution Process

1. **Create issue** using template
2. **Assign to `@copilot`** (GitHub Copilot coding agent)
3. **Wait for draft PR** (autonomous generation)
4. **Validate output** against acceptance criteria
5. **Measure time** from issue creation to draft PR
6. **Measure premium requests** consumed (GitHub billing dashboard → Copilot usage)
7. **Document failures** with specific section/criterion that failed

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Create Test Case 1 issue | Standards author | Issue created with all fields | 15 min |
| Assign to coding agent | Standards author | Agent accepts issue; begins work | 5 min |
| Wait for draft PR | N/A | Agent opens PR autonomously | Variable (agent) |
| Validate Test Case 1 output | Developer | All acceptance criteria checked | 30 min |
| Create Test Case 2 issue | Standards author | Issue created with all fields | 15 min |
| Assign to coding agent | Standards author | Agent accepts issue; begins work | 5 min |
| Validate Test Case 2 output | Developer | All acceptance criteria checked | 30 min |
| Create Test Case 3 issue | Standards author | Issue created with all fields | 15 min |
| Assign to coding agent | Standards author | Agent accepts issue; begins work | 5 min |
| Validate Test Case 3 output | Developer | All acceptance criteria checked | 30 min |
| Document results | Standards author | PASS/FAIL table with evidence | 2 hours |

---

## Deliverable 3: Acceptance Criteria Testing

### Objective

Test all acceptance criteria from `test_pipeline_e2e.py` against coding agent output.

### Acceptance Criteria (From Analysis)

**Ported from `akr-mcp-server/tests/test_pipeline_e2e.py`:**

| Criterion | What to Check | Pass Threshold |
|---|---|---|
| 1. **All MODULE sections present** | Module Files, Operations Map, Architecture Overview, Business Rules, Data Operations, Questions & Gaps, YAML front matter | 7/7 sections present |
| 2. **Module Files completeness** | All files listed with correct roles (Controller, Service, Repository, DTO) | 100% of module files listed |
| 3. **Operations Map coverage** | All public methods across all files covered | ≥95% of operations listed |
| 4. **Architecture diagram correctness** | Full-stack flow shown (Controller → Service → Repository → DB) | Text diagram present and accurate |
| 5. **Business Rules table format** | "Why It Exists" and "Since When" columns present | Both columns present |
| 6. **Data Operations coverage** | All reads and writes across all files covered | ≥95% of data operations listed |
| 7. **Validation passes** | `validate_documentation.py --fail-on needs` exits 0 | Exit code 0 |
| 8. **No truncation** | No "..." or "[content omitted]" artifacts in output | Zero truncation markers |
| 9. **Metadata header and final-doc cleanliness** | `<!-- akr-generated -->` block present with correct review_mode context; final doc free of draft-only front matter fields | Header present with all required fields and no draft-only fields in final doc |
| 10. **Hook log present** | `.akr/logs/session-*.jsonl` contains file write entry for the output doc path | Hard gate only when Copilot hook support is confirmed in Phase 1; otherwise record as known gap with evidence and continue |
| 11. **SSG background completion** | `passes-completed` present and complete; split info consistent; timing availability captured | All expected passes present; timing known-gap documented if unavailable |
| 12. **Committed draft/review sheet handling in async context** | Mode A review sheet committed at `docs/modules/.akr/{project}_review.md`; Mode B draft committed at `docs/modules/.akr/{ModuleName}_draft.md`; final doc contains no draft-only fields | Present in PR Files Changed and issue comments; if async review gate unsupported, record `ASYNC-REVIEW-GATE` known gap |

### Testing Matrix

|  | Test Case 1 (Baseline) | Test Case 2 (UI Component) | Test Case 3 (Large) |
|---|---|---|---|
| Criterion 1: All sections | ⬜ | ⬜ | ⬜ |
| Criterion 2: Module Files | ⬜ | ⬜ | ⬜ |
| Criterion 3: Operations Map | ⬜ | ⬜ | ⬜ |
| Criterion 4: Architecture | ⬜ | ⬜ | ⬜ |
| Criterion 5: Business Rules | ⬜ | ⬜ | ⬜ |
| Criterion 6: Data Operations | ⬜ | ⬜ | ⬜ |
| Criterion 7: Validation | ⬜ | ⬜ | ⬜ |
| Criterion 8: No truncation | ⬜ | ⬜ | ⬜ |
| Criterion 9: Metadata header | ⬜ | ⬜ | ⬜ |
| Criterion 10: Hook log | ⬜ | ⬜ | ⬜ |
| Criterion 11: SSG completion | ⬜ | ⬜ | ⬜ |
| Criterion 12: Committed draft + review sheet handling | ⬜ | ⬜ | ⬜ |
| **Overall** | ⬜ PASS / ❌ FAIL | ⬜ PASS / ❌ FAIL | ⬜ PASS / ❌ FAIL |

### Pass/Fail Decision Logic

**PASS:** All 3 test cases meet Criteria 1-9 and 11 and Criterion 10 handling follows: "Hard gate only when Copilot hook support is confirmed in Phase 1; otherwise record as known gap with evidence and continue."  
**FAIL:** Any test case fails Criteria 1-9 or 11, or Criterion 10 fails when Copilot hook support is confirmed in Phase 1

**Partial failures are still FAIL:** If Test Case 1 and 2 pass but Test Case 3 (large module) fails due to truncation, Phase 2.5 result is FAIL. Classify root cause as context overflow only if Pass 2 split was not attempted; if Pass 2 split executed correctly and incompleteness remains, classify as AST comprehension failure.

### Decision Rule (Reviewer PR Checklist)

Apply this rule exactly in PR review to avoid interpretation drift:

1. Verify Criteria 1-9 and 11 for each test case.
2. If any Criterion 1-9 or 11 fails in any test case, mark Phase 2.5 as FAIL.
3. Check whether Copilot hook support was confirmed in Phase 1 Deliverable 7A.
4. Criterion 10 handling follows: "Hard gate only when Copilot hook support is confirmed in Phase 1; otherwise record as known gap with evidence and continue."
5. If a known gap is recorded, include evidence in `SKILL-COMPAT.md` before final decision.
6. Final PASS requires all three test cases passing Criteria 1-9 and 11 and cost/recommendation sections completed.

Reviewer output format:
- `Phase 2.5 Decision: PASS|FAIL`
- `Criteria 1-9: PASS|FAIL`
- `Criterion 11: PASS|FAIL`
- `Criterion 10 Mode: HARD-GATE|KNOWN-GAP`
- `Criterion 10 Result: PASS|FAIL|N/A`
- `Evidence Links: [PRs, logs, SKILL-COMPAT.md entry]`

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Test Criterion 1-11 on Test Case 1 | Developer | All checks completed; results in matrix | 30 min |
| Test Criterion 1-11 on Test Case 2 | Developer | All checks completed; results in matrix | 30 min |
| Test Criterion 1-11 on Test Case 3 | Developer | All checks completed; results in matrix | 30 min |
| Document specific failures | Standards author | For each FAIL, note which section/criterion | 1 hour |
| Analyze failure patterns | Standards author | Identify root cause (e.g., context limit, template parsing) | 1 hour |
| Classify failures against `SKILL-COMPAT.md` model-specific failure modes | Standards author | For each FAIL, determine if root cause matches a known GPT-4o pattern (e.g., truncation at 8 files) or is a new fixable skill instruction gap; classification documented | 1 hour |

---

## Deliverable 4: Premium Request Measurement

### Objective

Measure premium request consumption per module to model monthly cost at team scale.

### Data to Collect

| Metric | Test Case 1 | Test Case 2 | Test Case 3 |
|---|---|---|---|
| **Premium requests consumed** | [from GitHub billing dashboard Copilot usage] | [from GitHub billing dashboard Copilot usage] | [from GitHub billing dashboard Copilot usage] |
| **Time to generate** | [minutes] | [minutes] | [minutes] |
| **Number of agent turns** | [count] | [count] | [count] |
| **Final PR quality** | [PASS/FAIL] | [PASS/FAIL] | [PASS/FAIL] |
| **Criteria 9 & 10 result** | [metadata header: ✅/❌, hook log: ✅/❌] | [metadata header: ✅/❌, hook log: ✅/❌] | [metadata header: ✅/❌, hook log: ✅/❌] |

### Cost Model

**Monthly cost projection:**
```
Modules per developer per month: X
Premium requests per module: Y (average from test cases)
Developers on team: Z
Monthly cost = (X * Y * Z) * premium request rate
```

**Example:**
- 3 modules per developer per month
- 50 premium requests per module (average)
- 10 developers
- $0.08 per premium request (example rate)
- Monthly cost = (3 * 50 * 10) * $0.08 = **$120/month**

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Query GitHub billing dashboard | Standards author | Request counts per test case documented from Copilot usage view | 30 min |
| Capture billing evidence artifacts | Standards author | CSV export or screenshots stored under `docs/pilot/phase-2.5/evidence/<test-case>/billing/` | 30 min |
| Calculate average requests per module | Standards author | Mean across 3 test cases | 15 min |
| Project monthly cost at team scale | Standards author | Cost model with team size variable | 30 min |
| Compare to Phase 3 infrastructure cost | Standards author | Azure Function hosting cost vs. coding agent premium requests | 1 hour |
| Document cost recommendation | Standards author | Which option is more cost-effective? | 30 min |

---

## Deliverable 5: Go/No-Go Recommendation

### Objective

Document binary decision: proceed to Phase 3 (if FAIL) or skip to Phase 4 (if PASS).

### Decision Tree

```
Phase 2.5 Result: PASS
   ├─ All 3 test cases passed Criteria 1-9 and 11
   ├─ Criterion 10 handling follows: "Hard gate only when Copilot hook support is confirmed in Phase 1; otherwise record as known gap with evidence and continue."
  ├─ Premium request cost acceptable at team scale
  ├─ Recommendation: SKIP Phase 3
  └─ Next: Proceed directly to Phase 4

Phase 2.5 Result: FAIL
  ├─ One or more test cases failed one or more acceptance criteria
  ├─ Document specific failure modes
  ├─ Recommendation: AUTHORIZE Phase 3 for documented failure modes only
  └─ Next: Build custom agent to address specific shortcomings
```

### Recommendation Document Template

```markdown
# Phase 2.5 — Coding Agent Spike Results

## Executive Summary

**Result:** [PASS | FAIL]  
**Recommendation:** [SKIP Phase 3 | AUTHORIZE Phase 3 for specific failure modes]  
**Cost Impact:** [premium requests vs. Azure Function hosting]

## Test Results

| Test Case | Result | Acceptance Criteria Met | Notes |
|---|---|---|---|
| 1: Standard Backend | [PASS/FAIL] | [X/11] | [specific failures if any] |
| 2: UI Component | [PASS/FAIL] | [X/11] | [specific failures if any] |
| 3: Large Module | [PASS/FAIL] | [X/11] | [specific failures if any] |

## Failure Modes (if FAIL)

[For each acceptance criterion that failed:]
- **Criterion:** [e.g., Operations Map coverage]
- **Failure:** [e.g., Only 60% of operations listed; missing private methods]
- **Root Cause:** [e.g., Agent did not read all files in module]
- **Frequency:** [X/3 test cases affected]
- **Impact:** [Blocks production use]

## Skill Reliability Results

| Check | Test Case 1 | Test Case 2 | Test Case 3 |
|---|---|---|---|
| `<!-- akr-generated -->` header present | ✅/❌ | ✅/❌ | ✅/❌ |
| Hook log `.akr/logs/session-*.jsonl` present | ✅/❌ | ✅/❌ | ✅/❌ |
| `passes-completed` field present | ✅/❌ | ✅/❌ | ✅/❌ |
| `pass-timings-seconds` available | ✅/KNOWN-GAP | ✅/KNOWN-GAP | ✅/KNOWN-GAP |
| SSG total wall-clock time ≤30 min | ✅/❌ | ✅/❌ | ✅/❌ |
| Pass 2 split handled correctly (large module only) | N/A | N/A | ✅/❌ |
| Self-reporting block in Copilot Chat | N/A (async) | N/A (async) | N/A (async) |

**Interpretation:**
- Metadata header absent → skill did not complete Mode B; document as FAIL on Criterion 9
- Hook log absent → coding agent does not trigger hooks in async context; document as known gap; does not cause Phase 3 authorization unless metadata header also absent

## Cost Analysis

- **Premium requests per module:** [average across test cases]
- **Projected monthly cost (10 developers):** [$X]
- **Azure Function alternative (Phase 3):** [$Y hosting + development cost]
- **Cost comparison:** [which is more economical?]

## Recommendation

### If PASS:
"The GitHub Copilot coding agent meets all acceptance criteria and is cost-effective at team scale. Phase 3 custom automation is unnecessary. Recommend proceeding directly to Phase 4 (feature consolidation)."

### If FAIL:
"The GitHub Copilot coding agent fails [X] acceptance criteria across [Y] test cases. Specific failure modes: [list]. Phase 3 is authorized to build custom agent addressing only these documented shortcomings. Custom agent scope: [specific functionality needed]."

## Next Steps

[Based on PASS/FAIL decision]

## Phase 2.6 Governance Stability Assessment Handoff

Regardless of Phase 2.5 PASS or FAIL verdict, the following data must be explicitly handed off to Phase 2.6:

| Data item | Source | Status |
|---|---|---|
| First-run CI pass rate across 3 test cases | Phase 2.5 acceptance matrix CI results | Required |
| Operations Map completeness on GPT-4o (% of public + private + async methods correctly enumerated) | Manual review of Test Cases 1-3 Operations Map sections | Required |
| Self-reporting block absent rate across all Mode B runs | Phase 2 retrospective + Phase 2.5 test runs | Required |
| benchmark.json actual vs. target pass rates | Phase 2.5 benchmark recording | Required |
| Any new GPT-4o failure modes documented in SKILL-COMPAT.md | SKILL-COMPAT.md v1.1 | Required |

Phase 2.6 cannot begin until all five items are provided in writing to the standards lead.

---

**Approved by:** [Standards Lead]  
**Date:** [Date]
```

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Draft recommendation document | Standards author | All sections completed with evidence | 3 hours |
| Present to management | Standards lead | Decision approved or feedback provided | 1 hour |
| Document Phase 3 authorization (if FAIL) | Standards author | Specific failure modes define Phase 3 scope | 1 hour |
| Document Phase 3 skip (if PASS) | Standards author | CHANGELOG entry noting decision | 30 min |

---

## Deliverable 6: SSG Background Execution Measurement

### Objective

Determine whether the Copilot coding agent executes SSG passes correctly and completely in async background mode, and collect timing data for `benchmark.json`.

### Measurement Approach

Since the coding agent runs asynchronously, per-pass timing from within the agent's execution context may not be available. Use the following measurement protocol:

| Measurement | Source | Method |
|---|---|---|
| Pass sequence completion | `passes-completed` field in PR output header | Direct read from PR output |
| Pass split occurrence | `passes-split` field in PR output header | Direct read from PR output |
| Pass timing data availability | `pass-timings-seconds` field value | If `unavailable`, record as KNOWN-GAP |
| Total wall-clock time | PR open timestamp - issue assignment timestamp | GitHub API or manual observation |
| Slow-generation events | Total wall-clock time > 45 minutes | Binary: yes/no per test case |
| Premium requests consumed | GitHub billing dashboard Copilot usage view | Match session timestamp to test case; record per test case |
| Required sections present | `validate_documentation.py` output `.summary` | Read from CI run output on coding agent PR |
| ❓ marker count | Count in generated output file | Script or manual count before developer review |
| Operations Map completeness (sampled) | Manual spot-check vs. source files | Standards author reviews 2-3 operations per test case |
| Validator first-pass result | CI check status on coding agent PR | ✅/❌ per test case |

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Record issue assignment timestamp for each test case | Standards author | Timestamp noted to nearest minute | 5 min per test |
| Read `passes-completed` from each PR output | Standards author | All expected passes present; any missing passes documented as FAIL on Criterion 11 | 15 min per test |
| Calculate wall-clock time per test case | Standards author | Time difference computed and recorded | 10 min per test |
| Determine if `pass-timings-seconds` is available | Standards author | Binary determination; if unavailable, classify as KNOWN-GAP | 10 min total |
| Record premium requests per test case | Standards author | Billing view evidence mapped to each test case | 15 min per test |
| Record required sections and validator first-pass result | Standards author | `.summary` fields and CI pass/fail recorded for all test cases | 15 min per test |
| Record ❓ marker count and sampled Operations Map completeness | Standards author | Marker count + sampled completeness captured for each test case | 15 min per test |
| Populate `benchmark.json` coding-agent ssg key | Standards author | `avg-total-seconds` populated; `pass-timings-available` set to true/false | 30 min |
| Populate `benchmark.json` quota-planning key | Standards author | Request averages and quota-derived max modules computed | 20 min |
| Document finding in go/no-go recommendation | Standards author | SSG background execution result included in recommendation | 30 min |

### SSG-Specific Failure Modes

The following SSG-specific failures are distinct from the existing Criteria 1-10 failures and must be classified separately. Note: Phase 3 authorization on Operations Map grounds requires evidence of an AST comprehension failure, not a context overflow - SSG handles context overflow via Pass 2 split.

| SSG Failure | Classification | Phase 3 Authorization |
|---|---|---|
| `passes-completed` field absent from PR output | FAIL Criterion 11 | Only if metadata header is also absent (overlaps Criterion 9) |
| Pass sequence out of order (e.g., Pass 4 before Pass 2) | FAIL Criterion 11 | Authorize Phase 3 for SSG orchestration support only |
| Pass 2 split produces incomplete Operations Map after correct execution | FAIL Criterion 2 (Operations Map coverage) - AST comprehension failure | Authorize Phase 3 deterministic AST extractor (Scope Example 1). Require evidence that SSG Pass 2 split executed correctly before authorizing. Context overflow alone is NOT grounds for Phase 3 (SSG already addresses that). |
| Operations Map incomplete because SSG Pass 2 split was NOT attempted | Not a Phase 3 trigger | Require SSG retry with split before any Phase 3 consideration |
| Total generation time >45 min on standard module | Slow-generation event | Do NOT authorize Phase 3 on time alone; document for future tracking |
| `pass-timings-seconds: unavailable` | KNOWN-GAP telemetry | Does not authorize Phase 3 |
| `generation-strategy: developer-elected-single-pass` with `passes-completed: single-pass` | Valid intentional state — not a failure | No Phase 3 implication; developer chose single-pass mode before generation began. This is not logged as a slow-module event and does not affect Criterion 11. |

### benchmark.json Population

After Phase 2.5, update `benchmark.json` with the following for the `coding-agent` -> `ssg` key:

```json
"coding-agent": {
   "ssg": {
      "mode-b-coursedomain": {
         "avg-total-seconds": "[measured value or null]",
         "pass-timings-available": "[true/false]",
         "avg-pass-seconds": {},
         "slow-module-rate": "[0.0 if no slow events; proportion if events occurred]",
         "premium-requests": {
            "avg-per-module": "[average across 3 test cases or null]",
            "min-observed": "[minimum across test cases]",
            "max-observed": "[maximum across test cases]",
            "with-pass2-split": "[average for large module test case with split]"
         },
         "quality": {
            "avg-required-sections-present": "[proportion 0.0-1.0]",
            "validation-first-pass-rate": "[proportion 0.0-1.0]",
            "avg-cqs": "[calculated or null]",
            "note": "operations-map-completeness and mode-c-resolution-minutes collected manually during Phase 2.5 review"
         }
      },
      "mode-b-large-module": {
         "avg-total-seconds": "[measured value or null]",
         "pass-timings-available": "[true/false]",
         "avg-pass-seconds": {},
         "slow-module-rate": "[proportion]",
         "premium-requests": {
            "avg-per-module": "[average]",
            "min-observed": "[minimum]",
            "max-observed": "[maximum]",
            "with-pass2-split": "[average with split]"
         },
         "quality": {
            "avg-required-sections-present": "[proportion]",
            "validation-first-pass-rate": "[proportion]",
            "avg-cqs": "[calculated or null]"
         }
      }
   }
}
```

Also update the `quota-planning` top-level key:

```json
"quota-planning": {
   "monthly-quota-per-developer": "[confirm from GitHub org settings]",
   "avg-requests-ssg-per-module": "[average from Phase 2.5 test cases]",
   "avg-requests-single-pass-per-module": "[from Phase 2 pilot if available; else null]",
   "max-modules-per-month-ssg": "[floor(quota / avg-requests-ssg)]",
   "max-modules-per-month-single-pass": "[floor(quota / avg-requests-single-pass) or null]",
   "recommended-mix": "[e.g., '3 SSG + 2 single-pass for small modules' or null until Phase 2 data available]",
   "notes": "Populated after Phase 2.5. Combine with Phase 2 pilot data for complete strategy decision table."
}
```

---

## Decision Outcomes

### Outcome A: PASS → Skip Phase 3

**Implications:**
- GitHub Copilot coding agent becomes the automation layer
- Issue templates published for team use
- Onboarding documentation updated with coding agent workflow
- No Phase 3 infrastructure investment
- Proceed directly to Phase 4 (feature consolidation)

**Cost savings:**
- Zero infrastructure maintenance
- Zero custom code to maintain
- Premium requests are pay-per-use (scales with usage)

### Outcome B: FAIL → Authorize Phase 3

**Implications:**
- Phase 3 scope narrowed to documented failure modes only
- Custom agent addresses **only** what coding agent cannot do
- Custom agent still uses Agent Skills for governance
- 350-line review gate; 500-line hard ceiling
- CI enforces line count on custom agent repository

**Phase 3 scope examples (hypothetical):**
- **If failure:** "Operations Map only 60% complete" → Custom extractor for deterministic operation listing
- **If failure:** "Operations Map incomplete after SSG Pass 2 split executed correctly" → AST comprehension failure; authorize deterministic AST extractor (Scope Example 1)
- **If failure:** "Template selection incorrect" → Deterministic `project_type` detector

**What Phase 3 CANNOT do (even if Phase 2.5 fails):**
- Re-implement all of Agent Skill logic
- Create monolithic documentation generator
- Ignore governance contracts in `modules.yaml` or `validate_documentation.py`

---

## Risk Register (Phase 2.5 Specific)

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| Coding agent context cliffs unexpectedly | 🟡 Medium | 🟡 Medium | Test Case 3 validates 8-file boundary; if fails, Phase 3 authorized |
| Premium request cost exceeds budget | 🟡 Medium | 🟠 Low | Model cost before execution; compare to Azure Function hosting |
| Coding agent unavailable or rate-limited | 🟠 Low | 🟠 Low | Test during low-usage period; document rate limits if encountered |
| Test cases not representative of real modules | 🟡 Medium | 🟠 Low | Select test modules from pilot project (real production code) |
| Skill reliability drops in async coding agent context | 🟡 Medium | 🟡 Medium | Criteria 9 (metadata header) and 10 (hook log) explicitly test this. Criterion 10 handling follows: "Hard gate only when Copilot hook support is confirmed in Phase 1; otherwise record as known gap with evidence and continue." |

---

## Success Criteria Summary

Phase 2.5 succeeds when:

✅ GitHub Issue template created and tested  
✅ 3 test issues executed (standard, UI, large)  
✅ All acceptance criteria tested (11 criteria × 3 test cases = 33 checks)  
✅ Results documented: PASS/FAIL per criterion  
✅ Premium request consumption measured and modeled  
✅ Go/no-go recommendation documented  
✅ Management approves recommendation  
✅ Phase 3 authorized (if FAIL) or skipped (if PASS)  
✅ Skill reliability results documented: Criteria 9 (metadata header) and 10 (hook log) recorded for all 3 test cases; `benchmark.json` `coding-agent` key populated  

**Gate rule note:** Criteria 1-9 and 11 are hard gates. Criterion 10 handling follows: "Hard gate only when Copilot hook support is confirmed in Phase 1; otherwise record as known gap with evidence and continue."

**Exit gate:** Binary decision approved by management **in writing** (approval record or email); next phase explicitly authorized before work begins.

---

**Next Phase:** [Phase 3: Automation Extension](PHASE_3_AUTOMATION_EXTENSION.md) (if Phase 2.5 result is FAIL)  
**Or:** [Phase 4: Feature Consolidation](PHASE_4_FEATURE_CONSOLIDATION.md) (if Phase 2.5 result is PASS)

**Related Documents:**
- [Phase 2: Pilot Onboarding](PHASE_2_PILOT_ONBOARDING.md)
- [Implementation Plan Overview](IMPLEMENTATION_PLAN_OVERVIEW.md)
- [Implementation-Ready Analysis](../akr_implementation_ready_analysis.md) — Part 10, Part 13
