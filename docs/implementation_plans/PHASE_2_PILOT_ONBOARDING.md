# Phase 2: Pilot Project Onboarding — Implementation Plan

**Duration:** 1-2 weeks per project  
**Team:** Standards team (0.5 FTE) + pilot project team (1-2 developers)  
**Prerequisite:** Phase 1 complete; `core-akr-templates` v1.0.0 tagged  
**Target:** One complete end-to-end pilot with retrospective

---

## Overview

Phase 2 validates the entire documentation workflow on a real project from grouping proposal through CI validation. The pilot proves that module-based documentation is faster than manual documentation, that validation catches errors before merge, and that the governance model works at team scale.

**Critical Path:** Project onboarding → Mode A grouping → Mode B generation → PR validation → Retrospective

---

## Acceptance Criteria

Phase 2 is complete when:

1. ✅ Pilot project selected and onboarded (recommended: TrainingTracker.Api)
2. ✅ Mode A (grouping proposal) completed; `modules.yaml` approved in ≤15 minutes
3. ✅ Mode B (documentation generation) completed for 3 modules
4. ✅ First documented PR opened; CI validation passes
5. ✅ Workflow tested in Visual Studio (or documented fallback if skills unavailable)
6. ✅ Two additional modules documented independently (unassisted)
7. ✅ 2-4 week pilot period completed
8. ✅ Pilot retrospective conducted with quantitative metrics
9. ✅ Templates and validator updated based on findings (if needed)
10. ✅ Onboarding checklist finalized
11. ✅ Second project onboarded using updated checklist

**Exit Gate:** Pilot retrospective complete; lessons learned documented; Phase 2.5 authorized if metrics support expanded rollout.

---

## Pilot Project Selection Criteria

### Recommended: TrainingTracker.Api

**Why ideal:**
- Pure API layer (clear `project.layer: API`)
- 3-5 well-defined domain modules (Courses, Enrollments, Users)
- Standard Controller → Service → Repository pattern
- Database objects clearly separable
- Team familiar with codebase (fast grouping validation)
- Active development (real PRs to test validation)

### Alternative Considerations

| Project | Pros | Cons |
|---|---|---|
| Frontend UI project | Tests `ui-component` workflow | May have fewer clear module boundaries |
| Microservice | Tests lightweight service pattern | May be too simple to stress-test |
| Full-stack monolith | Tests both UI and API simultaneously | Complexity may obscure pilot signal |

### Selection Decision

**Owner:** Standards lead + management  
**Deadline:** Before Phase 2 begins  
**Deliverable:** Pilot project identified; team assigned; kickoff scheduled

---

## Deliverable 1: Per-Project Onboarding

### Objective

Onboard pilot project with all Phase 1 deliverables; configure tooling end-to-end.

### Onboarding Checklist

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Add `core-akr-templates` as submodule | Pilot dev | Submodule pinned to **v1.0.0 release tag** (not `main`); `.gitmodules` configured | 15 min |
| Initialize submodule for local hook/runtime use | Pilot dev | `git submodule update --init --recursive` executed; `.akr/templates/.akr/scripts/validate_documentation.py` resolvable in local working tree | 5 min |
| Step 1a: Confirm GitHub MCP Server (`@github`) available in VS Code | Pilot dev | GitHub MCP extension installed and authenticated; `@github get files with names like CHARTER.md` returns charter files | 10 min |
| Step 1b: Configure hosted MCP context source OR `.github/copilot-instructions.md` as primary charter delivery fallback | Pilot dev | Context source configured; condensed backend charter accessible | 30 min |
| Confirm initial skill copy from submodule | Pilot dev | `.github/skills/akr-docs/SKILL.md` copied from `.akr/templates/.github/skills/akr-docs/SKILL.md`; `SKILL_VERSION` matches current release | 10 min |
| Deploy `validate-documentation.yml` | Pilot dev | Workflow file in `.github/workflows/`; triggered on draft PR | 30 min |
| Create initial `modules.yaml` | Pilot dev | Project section complete; `modules[]` empty; `database_objects[]` empty | 30 min |
| Copy Vale rules bundle into application repo | Pilot dev | `validation/vale-rules/AKR/` and `validation/.vale.ini` present; files copied from `core-akr-templates` submodule path or delivered via distribution PR - not manually authored | 20 min |
| Add Vale files to CODEOWNERS | Pilot dev | `validation/vale-rules/    @org/standards-team` and `validation/.vale.ini    @org/standards-team` present in CODEOWNERS; prevents local rule edits without standards-team review | 10 min |
| Test CI workflow | Pilot dev | Trigger workflow on draft PR; verify it runs without errors | 30 min |
| Create CODEOWNERS file | Pilot dev | Standards team + tech lead as owners for `docs/**`, `modules.yaml`, and `.github/skills/akr-docs/SKILL.md` | 20 min |
| Register repo in `core-akr-templates` | Standards author | Entry added to `registered-repos.yaml`; registration PR merged | 15 min |
| Verify distribution workflow reaches this repo | Pilot dev | `workflow_dispatch` targeting this repo opens an update PR | 15 min |
| Confirm `.github/hooks/` directory present | Pilot dev | Both `postToolUse.json` and `agentStop.json` present in application repo (distributed by `distribute-skill.yml`); run a Mode B session and confirm both `.akr/logs/session-YYYYMMDD.jsonl` and `.akr/logs/last-validation.json` are created | 15 min |

Recommended CODEOWNERS additions:
- `docs/modules/**  @org/standards-team @tech-lead`
- `modules.yaml     @org/standards-team`
- `.github/skills/akr-docs/SKILL.md  @org/standards-team`
- `validation/vale-rules/    @org/standards-team`
- `validation/.vale.ini       @org/standards-team`

**Critical:** Submodule must reference the v1.0.0 release tag, not `main`. Using `main` will cause instability if breaking changes are merged to `core-akr-templates` after pilot begins.

**Note on skill maintenance:** After onboarding, developers should never manually edit `.github/skills/akr-docs/SKILL.md` in application repositories. All updates originate in `core-akr-templates` and are delivered automatically via pull request.

**Critical:** `modules.yaml` must be in CODEOWNERS to prevent rogue changes to `compliance_mode` or `max_files` limits without standards team review.

**Critical:** `.github/skills/akr-docs/SKILL.md` must be in CODEOWNERS so manual edits cannot bypass standards-team review.

**Critical:** `validation/vale-rules/` and `validation/.vale.ini` must be in CODEOWNERS. Application teams must never edit these files directly. Rule updates arrive via distribution PRs from `core-akr-templates`.

### Initial `modules.yaml` Template

```yaml
# modules.yaml — TrainingTracker.Api Pilot
project:
  name: TrainingTracker.Api
  layer: API
  standards_version: v1.0.0
  minimum_standards_version: v1.0.0
  compliance_mode: pilot

# Modules section initially empty — populated by Mode A
modules: []

# Database objects section initially empty — populated by Mode A or manually
database_objects: []

# Unassigned files — populated by Mode A when files cannot be confidently grouped
unassigned: []
```

### Hosted MCP Context Source Configuration

**If Test 2 passed (Pre-pilot):**

1. Open VS Code Settings → Copilot → MCP
2. Add `core-akr-templates` repository as context source
3. Verify condensed charter loads on new session
4. Test in Visual Studio as well

**If Test 2 failed (Pre-pilot fallback):**

1. Copy the **condensed backend charter** to `.github/copilot-instructions.md` (must be ≤ **2,500 tokens**; enforced by our tokenizer check)
2. Document: this is per-repository distribution until hosted MCP available
3. Future migration path: when hosted MCP becomes available, remove from `.github/copilot-instructions.md`

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Complete onboarding checklist | Pilot dev | All 10 items checked | 3 hours |
| Document onboarding friction points | Pilot dev | Notes on unclear steps or missing instructions | 30 min |
| Validate tooling end-to-end | Standards author | Agent Skill loads; CI triggers; Vale runs | 1 hour |
| Schedule Mode A session | Standards author + pilot dev | 1-hour pairing session on calendar | 5 min |

---

## Deliverable 2: Mode A — Grouping Proposal

### Objective

Run Agent Skill Mode A to propose module groupings; developer validates and approves in ≤15 minutes.

### Invocation

**In VS Code Copilot Chat:**
```
@workspace propose module groupings for TrainingTracker.Api
```

**Or GitHub Copilot CLI:**
```bash
gh copilot suggest "propose module groupings for TrainingTracker.Api"
```

### Expected Output - Two committed artifacts, in sequence

**Step 1 - Semantic Review Sheet (immediate, before PR):**
`docs/modules/.akr/{project}_review.md` committed to the PR branch and displayed in Copilot Chat.
Contains: YAML front matter with last-reviewed-at, per-module file-role tables, unassigned rationale,
reviewer checkboxes, reassignment summary, pre-filled tracker update blocks.
The developer validates this document in VS Code - not a GitHub PR diff.
This file is a permanent artifact and the starting context for all future Mode A incremental updates.

**Step 2 - Final modules.yaml + PR (after review sheet approval):**
modules.yaml patched with any reassignments; review_sheet and last_reviewed_at fields added.
PR opened; review sheet visible in PR Files Changed tab under docs/modules/.akr/.
CI validates modules.yaml schema, enum values, and businessCapability tags.

### Developer Validation Tasks - Using the Committed Review Sheet

| Validation | Where to Do It | What to Check | Time |
|---|---|---|---|
| **Semantic accuracy** | `docs/modules/.akr/{project}_review.md` in VS Code | Does each file's assigned role match what it actually does? | 3 min |
| **Module naming** | Review sheet, module header | Do module names reflect domain language, not file names? | 2 min |
| **File count** | Review sheet, max_files status | Any module over limit? Record split recommendation. | 1 min |
| **Misplaced files** | Review sheet, "Belongs Here?" column | Mark ☐ No; fill "Files to move out" table. | 3 min |
| **Unassigned rationale** | Review sheet, unassigned section | Is each reason correct? | 2 min |
| **Business capability tags** | Review sheet, module headers | Does each `businessCapability` value exist in `tag-registry.json`? | 2 min |
| **Reply to agent** | Copilot Chat | Reply 'approved' or 'N reassignments made'. | 1 min |

**Total validation time target: ≤15 minutes**
**Note:** Review is done in VS Code, not GitHub. The PR is a merge/CI artifact - all semantic decisions are made before it opens.

### Mode A PR Checklist (Auto-Generated by Agent Skill)

```markdown
## Mode A — Grouping Proposal Review

- [ ] All module groupings reviewed for semantic accuracy
- [ ] Module names reflect domain language (not file names)
- [ ] No module exceeds max_files: 8
- [ ] Misplaced files reassigned to correct module
- [ ] Shared/infrastructure files correctly placed in unassigned[]
- [ ] All database objects identified and typed correctly
- [ ] All `businessCapability` tags exist in tag-registry.json
- [ ] modules.yaml approved before documentation generation begins
```

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Invoke Mode A | Pilot dev | Agent generates and commits review sheet at `docs/modules/.akr/` AND displays in chat | 5 min (agent) |
| Review and validate groupings | Pilot dev | Review sheet annotations complete; reassignment count recorded | 15 min |
| Confirm to agent | Pilot dev | Reply 'approved' or 'N reassignments' | 1 min |
| Agent applies reassignments, updates modules.yaml, opens PR | Agent | modules.yaml patched with review_sheet + last_reviewed_at; review sheet committed; PR opened | 3 min (agent) |
| Tech lead spot-check | Tech lead | Confirms review sheet in PR Files Changed; approves | 3 min |
| Record validation time | Standards author | Time from review sheet display → agent reply vs. 15 min target; recorded in AKR_Tracking.md | 2 min |

### Success Metrics

- **Grouping accuracy:** ≥90% of proposed groupings accepted without reassignment
- **Validation time:** ≤15 minutes from review sheet display to developer reply
- **Friction score:** Developer completes review in VS Code without opening GitHub
- **Reassignment churn:** Zero PR comments requesting reassignment
- **Future update speed:** Second Mode A invocation (after code change) completes in ≤5 min

---

## Deliverable 3: Mode B — Documentation Generation

### Objective

Run Agent Skill Mode B to generate documentation for CourseDomain module; developer reviews and fills `❓` sections.

### Reusable Section Guidance Block Reference

Use the draft section-guidance standard at:
`docs/implementation_plans/SECTION_GUIDANCE_BLOCK_DRAFT.md`

Phase 2 application scope:
- Apply the TL;DR guidance block in pilot module template runs so TL;DR output remains business-readable for Product Owner and QA audiences.
- Collect reviewer feedback on clarity and usefulness during Deliverable 7 retrospective inputs.
- Promote to normalized template pattern only after pilot validation confirms value and low context overhead.

### Invocation

**In VS Code Copilot Chat:**
```
@workspace generate documentation for CourseDomain module
```

### Expected Output - Two committed artifacts, in sequence

**Step 1 - Committed draft (immediate, before PR):**
`docs/modules/.akr/{ModuleName}_draft.md` written and committed to the branch.
Displayed in Copilot Chat with validation summary block.
Developer edits draft in VS Code Markdown Preview.
This file is a permanent artifact and the starting context for all future Mode B incremental updates.

**Step 2 - Final doc_output + PR (after developer confirms):**
Final `docs/modules/{ModuleName}_doc.md` written from the confirmed draft.
Draft-only front matter fields stripped; final-doc front matter injected (Step 6a).
PR opened with validation summary block in PR description.
PR body notes: "Pre-commit draft reviewed at docs/modules/.akr/{ModuleName}_draft.md before PR open."
CI validates final file. modules.yaml updated with draft_output, last_reviewed_at, review_mode.

### Developer Content Review Tasks - Using the Committed Draft

| Review | Where to Do It | What to Fill/Validate | Time |
|---|---|---|---|
| **Read validation summary** | Copilot Chat | Check section completeness, ❓ count, validator result. If errors: ask agent to fix. | 2 min |
| **❓ sections** | `docs/modules/.akr/{ModuleName}_draft.md` in VS Code Markdown Preview | Fill ❓ sections or add `DEFERRED: [reason]` with owner. | 10 min |
| **Business Rules** | Draft file | Confirm "Why It Exists" accuracy; add "Since When" dates. | 5 min |
| **Data Operations** | Draft file | Verify all reads and writes covered. | 5 min |
| **Architecture diagram** | Draft file | Validate full stack is correct. | 2 min |
| **Operations Map** | Draft file | Spot-check all public methods listed. | 3 min |
| **Reply to agent** | Copilot Chat | Reply 'ready to commit'. | 1 min |

**Total content review time target: ≤30 minutes**
**Note:** Review is done in VS Code. The draft file is both the review surface and the permanent record of the developer's annotations.

### Mode B PR Checklist (Auto-Generated by Agent Skill)

```markdown
## Mode B — CourseDomain Documentation Review

- [ ] Module Files section lists all files with correct roles
- [ ] All ❓ sections reviewed; filled or marked DEFERRED with justification
- [ ] Business Rules table complete including "Why It Exists" column
- [ ] Data Operations section covers all reads and writes
- [ ] Questions & Gaps populated with open items
- [ ] validate_documentation.py passes with zero errors
- [ ] CODEOWNERS notified for review
```

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Invoke Mode B for CourseDomain | Pilot dev | Agent generates draft documentation | 10 min (agent time) |
| Apply reusable TL;DR section guidance block in draft review | Pilot dev | TL;DR section aligns with `SECTION_GUIDANCE_BLOCK_DRAFT.md` and is readable by non-implementing stakeholders | 5 min |
| Review and fill content | Pilot dev | All checklist items completed | 30 min |
| Run `validate_documentation.py` locally | Pilot dev | Zero errors; all required sections present | 5 min |
| Open Mode B PR | Pilot dev | Draft PR with completed checklist | 5 min |
| Tech lead approval | Tech lead | Content accuracy validated; PR approved | 10 min |
| Record generation time | Standards author | Actual time vs. 30 min target documented | 2 min |
| Record section-guidance feedback | Standards author | Feedback captured for TL;DR clarity and recommendation status for template normalization | 3 min |

### Incremental Update Procedure (subsequent Mode B runs after code changes)

Invocation: `@workspace update {ModuleName} documentation for recent changes to [file(s)]`

Agent behavior:
- Reads committed draft at docs/modules/.akr/{ModuleName}_draft.md (primary context)
- Does not re-read all files or re-run full SSG unless patch scope expands beyond identified changed files
- Reads only changed source file(s); loads only relevant charter section(s)
- Patches affected sections in-place; updates front matter timestamps
- Displays incremental summary (patched vs. unchanged sections; new ❓ markers)
- Developer confirms; agent strips draft-only front matter, writes final doc, opens PR

Target time: ≤10 minutes (developer time)

### SSG Timing Data Collection

During Mode B runs in the pilot, the following data must be recorded for every module documented. This feeds `benchmark.json`, the strategy decision benchmark table, and quota planning guidance.

Collection method: Timing and strategy fields are read from the `<!-- akr-generated -->` metadata header in each PR output. Premium requests are read from the GitHub billing dashboard Copilot usage view (per-session or per-day export, matched to documentation PR timestamps). Quality metrics are derived from the validator output and a manual spot-check.

| Module | Files | LOC Est. | Strategy | Premium Requests | Total Time (s) | Pass 2 Split? | Sections Present | ❓ Marker Count | Ops Map Complete (%) | Validator Pass? | Mode C Time (min) | CQS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [CourseDomain] | 5 | ~800 | SSG | | | No | | | | | | |
| [EnrollmentDomain] | | | SSG | | | | | | | | | |
| [UserDomain] | | | SSG | | | | | | | | | |
| [SmallModule] | <=3 | <600 | Single-pass | | | N/A | | | | | | |

Notes on collection:
- "Ops Map Complete (%)" requires a 5-minute manual spot-check: open the source file, count public methods, compare to Operations Map entries. Record as a rough percentage (not exact).
- "Mode C Time" is recorded by the developer using a stopwatch during their ❓ review session, starting when Mode C is invoked and ending when all items are resolved or DEFERRED.
- Premium requests: if the billing dashboard does not provide per-module granularity, record the session-level count and note the session included this module only.
- CQS is calculated post-collection using the formula in Part 18.6.3. Standards author calculates after all other fields are populated.

After at least 3 SSG modules and 1 single-pass module are documented, calculate:
- Average premium requests per strategy per module profile
- Average CQS per strategy per module profile
- Record in `benchmark.json` under the `ssg` -> `premium-requests` and `quality` keys
- Record in `benchmark.json` -> `quota-planning` block

### Success Metrics

- **Section completeness:** 100% required sections present (validated in draft before PR)
- **Content review time (first-run):** ≤30 minutes from draft display to 'ready to commit'
- **Incremental update time:** ≤10 minutes from invocation to developer confirmation
- **Validation pass rate:** Zero validator errors on PR open
- **❓ fill rate:** ≥95% of ❓ sections filled or marked DEFERRED
- **PR comment volume:** Zero tech lead comments requesting content changes
- **Friction score:** Developer does not open GitHub to complete content review

### Slow Module Escalation

If a module's total generation time exceeds 45 minutes during the pilot, follow this process:

1. Record the event. Log to `.akr/logs/session-*.jsonl` (via `agentStop` hook). Note which pass was slowest and approximately how many source file tokens were loaded in Pass 2.
2. Do not re-run immediately. Re-running the same configuration will produce the same timing result. First evaluate whether module splitting is appropriate.
3. Evaluate module splitting. If the module has 7-8 files and large file sizes, splitting into two sub-modules (<=5 files each) is the preferred resolution. This requires a modules.yaml update (PR through standards team) and a Mode A re-validation step.
4. If splitting is not feasible (e.g., the files are tightly coupled and cannot be logically separated), document the module as a "large module exception" in modules.yaml with `notes: "SSG slow module - single-pass fallback authorized"` and proceed with single-pass fallback. Expect additional ❓ markers.
5. Report in retrospective. Include the module name, total time, slowest pass, and resolution chosen. This feeds the `ssg-slow-module-rate` metric in `benchmark.json`.

---

## Deliverable 4: CI Validation Testing

### Objective

Verify that CI workflow runs successfully on Mode B PR; catches validation errors; provides actionable feedback.

### Test Scenarios

| Scenario | Expected Behavior | Validation |
|---|---|---|
| **Happy path:** All sections present, no `❓` | Workflow passes; PR checks green | CI status: ✅ |
| **Missing section:** Operations Map omitted | Workflow fails; error message identifies missing section | CI status: ❌ with clear error |
| **Unresolved `❓` in pilot mode** | Workflow warns but passes (compliance_mode: pilot) | CI status: ⚠️ with warning |
| **File not in modules.yaml** | Workflow warns doc not registered; applies generic rules | CI status: ⚠️ |
| **Vale prose quality issue** | Vale reports style violations; does not block merge | CI status: ⚠️ |

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Test happy path scenario | Pilot dev | PR checks pass; no false positives | 30 min |
| Test missing section scenario | Pilot dev | Error message clear; identifies specific missing section | 30 min |
| Test unresolved `❓` in pilot mode | Pilot dev | Warning displayed; PR not blocked | 15 min |
| Test Vale prose check | Pilot dev | Vale runs; reports style issues; does not block | 15 min |
| Document CI feedback clarity | Standards author | Errors are actionable; no developer confusion | 30 min |

### Success Metrics

- **Zero false positives:** CI does not report errors on valid module docs
- **Error clarity:** All error messages identify specific issue and line number
- **Performance:** CI completes in <2 minutes for typical PR

---

## Deliverable 5: Visual Studio Testing

### Objective

Validate that workflow functions correctly in Visual Studio (not just VS Code).

**Why critical:** Enterprise teams may use Visual Studio for .NET projects; VS Code-only workflows create adoption friction.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Configure Agent Skill in Visual Studio | Pilot dev | Skill loads in Copilot Chat window OR fallback documented | 30 min |
| Run Mode A in Visual Studio | Pilot dev | Grouping proposal generated successfully OR fallback documented | 30 min |
| Run Mode B in Visual Studio | Pilot dev | Documentation generated successfully OR fallback documented | 30 min |
| Document Visual Studio-specific steps | Standards author | README includes VS-specific configuration AND fallback workflow | 2 hours |
| Verify `@github` MCP tool call availability in Visual Studio Copilot Chat | Pilot dev | `@github get files with names like CHARTER.md` returns charter files OR limitation documented; VS parity vs VS Code recorded before Mode A/B VS runs begin | 15 min |

### Visual Studio Considerations

- **Skill loading:** May require different `.github/` path configuration
- **Copilot Chat integration:** UI differs from VS Code; document invocation patterns
- **MCP context source:** Confirm hosted MCP works in VS (if Test 2 passed). Also verify `@github` tool call availability: run `@github get files with names like CHARTER.md` in VS Copilot Chat. If `@github` is unavailable in VS, PATH B (local file fallback) in SKILL.md Mode B Step 2 applies for all VS sessions.
- **Terminal commands:** `validate_documentation.py` runs from Developer PowerShell
- **Fallback plan:** If Agent Skills are unavailable in VS, document workaround using VS Code for Mode A/B invocations + VS for code editing + CI validation

---

## Deliverable 6: Independent Module Documentation

### Objective

Developer documents two additional modules independently (unassisted) to validate that workflow is self-service.

### Modules

- **EnrollmentDomain** (5 files)
- **UserDomain** (4 files)

### Success Criteria

- Developer completes both modules without asking for help
- Each module takes ≤45 minutes (Mode B invocation + content review + PR)
- CI validation passes on first PR for both
- Developer reports: "Faster than writing docs manually"

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Document EnrollmentDomain | Pilot dev (unassisted) | PR opened with all sections complete | 45 min |
| Document UserDomain | Pilot dev (unassisted) | PR opened with all sections complete | 45 min |
| Record time per module | Pilot dev | Self-reported time tracked | 2 min each |
| Collect friction points | Pilot dev | Notes on unclear steps or errors encountered | 10 min |

---

## Deliverable 7: 2-4 Week Pilot Period

### Objective

Run pilot for 2-4 weeks to accumulate real-world usage data; iterate on templates and validator based on findings.

### Pilot Activities

**Week 1:**
- Mode A + Mode B for 3 modules (CourseDomain, EnrollmentDomain, UserDomain)
- Daily check-in: standards author available for questions
- Collect: time-to-doc, ❓ fill rate, validation pass rate

**Week 2:**
- Document 2 additional modules independently
- First production use: real feature development uses docs
- Collect: developer satisfaction feedback

**Week 3-4 (if needed):**
- Iterate on templates based on Week 1-2 findings
- Test updated templates on 1-2 modules
- Collect: improvement delta

### Metrics to Track

| Metric | Collection Method | Target |
|---|---|---|
| **Time-to-doc per module** | Self-reported by developer | ≤30 minutes |
| **Grouping validation time** | Timer during Mode A review | ≤15 minutes |
| **❓ section fill rate** | Count unresolved `❓` in merged docs | ≥95% filled or DEFERRED |
| **Validation pass rate on first PR** | CI logs | ≥95% pass without errors |
| **Grouping proposal accuracy** | % of groups needing reassignment | ≥90% accepted as-is |
| **Developer satisfaction** | Post-pilot survey | "Faster than manual" consensus |
| **Self-reporting block present rate** | Manual spot-check of Copilot Chat responses | 100% of skill responses begin with `✅ akr-docs INVOKED` block |
| **`<!-- akr-generated -->` header present rate** | `grep` over merged module docs | 100% of merged module docs contain metadata header |

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Conduct daily check-ins (Week 1) | Standards author | Developer questions answered same-day | 30 min/day |
| Collect metrics | Standards author | Spreadsheet with all metrics tracked | Ongoing |
| Identify friction points | Standards author | List of unclear steps or errors | Ongoing |
| Iterate templates (if needed) | Standards author | Updates deployed mid-pilot | 1-2 days |
| Document iteration rationale | Standards author | CHANGELOG entries for mid-pilot updates | 1 hour |

---

## Deliverable 8: Pilot Retrospective

### Objective

Conduct retrospective with quantitative metrics and qualitative feedback; decide on v1.1 updates.

### Retrospective Agenda

1. **Metrics review:** Present all tracked metrics vs. targets
2. **Friction points:** What took longer than expected? What was confusing?
3. **Template accuracy:** Did templates capture the right information?
4. **Validator effectiveness:** Did CI catch real errors? Any false positives?
5. **Developer experience:** Was workflow faster than manual documentation?
6. **Visual Studio parity:** Did VS workflow work as well as VS Code?
7. **Phase 2.5 readiness:** Do metrics support expanding to coding agent?
8. **Skill reliability:** Was the self-reporting block present in 100% of sessions? If not, when was it absent - and did the metadata header check in CI catch the gap?
9. **Model compatibility:** Did any GPT-4o-specific failure modes emerge (e.g., Mode B truncation on large modules)? Document specific module/file-count where truncation first occurred, if any.
10. **Review surface effectiveness:** Did committed review sheets reduce reassignment PR comments to zero? Did committed drafts eliminate first-run CI failures? Were developers able to complete reviews without opening GitHub?
11. **Incremental update scenario:** Were any committed drafts used as starting context for an update-scenario Mode B run? Was the incremental path faster than full re-generation?
12. **Staleness management:** Were any committed drafts found stale relative to code changes? How were they detected?
13. **Governance stability baseline (feeds Phase 2.6):** Record first-run CI pass rate AND Operations Map completeness rate now, before Phase 2.5. These are the baseline measurements Phase 2.6 requires.

### Retrospective Outputs

- **Quantitative summary:** Metrics table with actuals vs. targets
- **SSG retrospective metrics:**

| Metric | Target | Actual (to fill in) |
|---|---|---|
| Average SSG total generation time per module | ≤30 minutes | |
| Slowest individual pass across all modules | Pass 2 expected | |
| Modules triggering slow-generation fallback (>45 min) | <10% | |
| Modules requiring Pass 2 split (2A+2B) | <50% of modules | |
| Average Pass 2 time (seconds) | ≤480 seconds (8 min) | |
| Timing data availability (% of runs with pass-timings-seconds populated) | ≥80% | |
| Average premium requests - SSG multi-pass, standard module | Informational | |
| Average premium requests - SSG multi-pass, large module | Informational | |
| Average premium requests - single-pass (if any runs observed) | Informational | |
| Average CQS - SSG multi-pass | ≥0.80 | |
| Average CQS - single-pass (if any runs observed) | Informational | |
| Average ❓ marker count at generation - SSG | ≤5 per document | |
| Average ❓ marker count at generation - single-pass | Informational | |
| Average Mode C resolution time - SSG | ≤10 minutes | |
| Average Mode C resolution time - single-pass | Informational | |
| Validator first-pass rate - SSG | ≥95% | |
| Validator first-pass rate - single-pass | Informational | |
| Modules documented via developer-elected single-pass | Informational (track proportion) | |
| Monthly quota consumed by documentation (% of individual quota) | <25% of monthly quota | |

- **Retrospective questions to add:**
  "For modules where generation took >20 minutes, did developers use the coding agent background execution model or wait interactively? What was the impact on developer experience?"
  "For any single-pass runs: did the Mode C resolution time offset the premium request savings? Would the developer use single-pass again for that module profile?"
  "At the current average premium request rate per module, how many modules can a developer document before exhausting their monthly quota? Is this sufficient for the team's documentation cadence?"
- **Friction point log:** Issues encountered with priority ratings
- **Template updates required:** Specific sections to add/modify/remove
- **Validator updates required:** Rules that fired false positives or missed errors
- **Onboarding checklist refinement:** Steps that were unclear or redundant
- **v1.1.0 scope:** Features to include in next minor release
- **Phase 2.5 authorization:** Go/no-go for coding agent spike
- **Skill reliability report:** Self-reporting block presence rate + metadata header presence rate across all pilot Mode B sessions; root cause noted for any absence events
- **`SKILL-COMPAT.md` v1.1 update:** GPT-4o failure modes observed during pilot (if any) documented before Phase 2.5 begins; pass rates in `benchmark.json` updated with pilot real-world data
- `preview-friction-score`: % of reviews completed in-editor without opening GitHub (target: ≥80%)
- `reassignment-churn-rate`: avg PR comments requesting reassignment (target: 0 after first two modules)
- `first-run-CI-pass-rate`: % of PRs with zero validator errors (target: ≥98%)
- `operations-map-completeness-gpt4o`: % of methods correctly enumerated on GPT-4o runs (feeds Phase 2.6)
- `self-reporting-block-absent-rate`: % of Mode B runs missing self-reporting block (feeds Phase 2.6)
- `incremental-update-count`: number of Mode B incremental runs observed
- `incremental-update-time`: avg developer time for incremental runs (target: ≤10 min)
- `staleness-incidents`: number of times committed draft was stale relative to code changes

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Prepare retrospective deck | Standards author | Metrics + friction points + recommendations | 3 hours |
| Conduct retrospective meeting | Standards lead + pilot team | All agenda items covered; outputs documented | 2 hours |
| Document recommendations | Standards author | Retrospective report published | 2 hours |
| Update templates (if needed) | Standards author | Changes implemented based on findings | 1-2 days |
| Tag v1.1.0 (if breaking changes) | Standards lead | Release notes published | 1 hour |

---

## Deliverable 9: Onboarding Checklist Finalization

### Objective

Finalize onboarding checklist based on pilot learnings; prepare for second project rollout.

### Checklist Refinements

- **Step ordering:** Was sequence logical? Any prerequisite missed?
- **Clarity:** Were instructions clear? Any ambiguous steps?
- **Tooling:** Did all configuration steps work? Any platform-specific issues?
- **Timing:** Were time estimates accurate? Any steps take longer than expected?

### Finalized Checklist Template

```markdown
# AKR Documentation Onboarding Checklist

## Prerequisites
- [ ] GitHub Copilot Business or Enterprise license confirmed
- [ ] Project identified and team assigned
- [ ] core-akr-templates v1.0.0+ available

## Setup (estimated: 3 hours)
- [ ] Add core-akr-templates as submodule at v1.0.0
- [ ] Configure hosted MCP context source (or .github/copilot-instructions.md)
- [ ] Confirm initial SKILL.md copy from submodule and verify `SKILL_VERSION` header
- [ ] Confirm `.github/hooks/postToolUse.json` and `.github/hooks/agentStop.json` present (distributed with SKILL.md); run Mode B session to verify `.akr/logs/` is created
- [ ] Deploy validate-documentation.yml workflow
- [ ] Create initial modules.yaml (project section only)
- [ ] Copy Vale rules bundle from submodule or distribution PR (do not manually author)
- [ ] Add `validation/vale-rules/` and `validation/.vale.ini` to CODEOWNERS under @org/standards-team
- [ ] Test CI workflow on draft PR
- [ ] Create CODEOWNERS file

## Skill Distribution Registration (estimated: 30 min)
- [ ] Confirm `SKILL_VERSION` header in .github/skills/akr-docs/SKILL.md
- [ ] Add .github/skills/akr-docs/SKILL.md to CODEOWNERS: @org/standards-team
- [ ] Standards author adds repo to registered-repos.yaml in core-akr-templates
- [ ] Test distribution workflow: workflow_dispatch targeting this repo opens a PR
- [ ] Merge test PR to confirm end-to-end flow works

## Mode A — Grouping Proposal (estimated: 1 hour)
- [ ] Invoke Agent Skill Mode A: "propose module groupings"
- [ ] Review draft modules.yaml (15 minutes)
- [ ] Validate groupings per checklist
- [ ] Open Mode A PR
- [ ] Tech lead approves groupings

## Mode B — Documentation Generation (per module, estimated: 45 minutes)
- [ ] Invoke Agent Skill Mode B: "generate documentation for [Module]"
- [ ] Review and fill ❓ sections (30 minutes)
- [ ] Run validate_documentation.py locally
- [ ] Open Mode B PR
- [ ] CI validation passes
- [ ] Tech lead approves content

## Pilot Period (2-4 weeks)
- [ ] Document 3+ modules independently
- [ ] Collect metrics (time, pass rate, satisfaction)
- [ ] Identify friction points
- [ ] Iterate templates if needed

## Retrospective
- [ ] Conduct pilot retrospective
- [ ] Document lessons learned
- [ ] Update onboarding checklist for next project
```

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Incorporate pilot feedback | Standards author | Checklist updated with clarifications | 2 hours |
| Validate time estimates | Standards author | All estimates reflect pilot actuals | 30 min |
| Add platform-specific notes | Standards author | Windows/macOS/Linux considerations documented | 1 hour |
| Publish final checklist | Standards author | Available in core-akr-templates/docs/ | 15 min |

---

## Deliverable 10: Second Project Onboarding

### Objective

Validate that updated onboarding checklist works on a second project; prove repeatability.

### Second Project Selection

**Criteria:**
- Different `project.layer` than pilot (if pilot was API, choose UI or Database)
- Different team (validates knowledge transfer)
- Active development (real documentation needs)

**Recommended:** UI project using React/TypeScript to test `ui-component` workflow

### Success Criteria

- Onboarding completed in ≤4 hours using finalized checklist
- Zero questions that should have been answered by checklist
- Mode A + Mode B workflows successful on first attempt
- Developer reports: "Checklist was clear and complete"

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Select second project | Standards lead | Project identified; team assigned | External |
| Run onboarding using finalized checklist | Second project dev | All steps completed | 4 hours |
| Document any missing steps | Second project dev | Feedback provided to standards team | 30 min |
| Update checklist (if needed) | Standards author | Final refinements incorporated | 1 hour |

---

## Phase 2 Retrospective

### Retrospective Agenda

1. **Pilot success:** Did metrics meet targets? What exceeded expectations?
2. **Onboarding effectiveness:** Was checklist complete? Any missing steps?
3. **Template accuracy:** Did module groupings produce correct documentation?
4. **Validator effectiveness:** Did CI catch real errors? Any false positives?
5. **Developer adoption:** Is team excited about workflow? Any resistance?
6. **Visual Studio parity:** Was VS experience equivalent to VS Code?
7. **Phase 2.5 decision:** Should we proceed with coding agent spike?

### Retrospective Outputs

- **Phase 2 completion metrics:** Pilot vs. second project comparison
- **Deterministic timing metrics:** Event-derived grouping validation time and time-to-doc from PR/CI timestamps
- **v1.1.0 backlog:** Features deferred or identified during pilot
- **Onboarding playbook:** Final checklist + lessons learned
- **Phase 2.5 authorization:** Standards lead go/no-go decision
- **`benchmark.json` update:** Real-world pilot pass rates added alongside Phase 1 synthetic baseline; delta between synthetic and real-world documented if significant

---

## Risk Register (Phase 2 Specific)

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| Pilot developer unavailable mid-pilot | 🟡 Medium | 🟠 Low | Assign backup developer before pilot begins |
| Mode A groups files incorrectly | 🟡 Medium | 🟡 Medium | 15-minute validation catches; developer reassigns |
| CI false positives frustrate team | 🔴 High | 🟠 Low | Monitor false positive rate; hot-fix validator if >5% |
| Visual Studio workflow broken | 🟡 Medium | 🟠 Low | Phase 0 Test 6 baseline passed; pilot validates real project integration; document workarounds if issues found |
| Pilot metrics don't support Phase 2.5 | 🟡 Medium | 🟠 Low | Retrospective determines if manual workflow sufficient |

---

## Success Criteria Summary

Phase 2 succeeds when:

✅ Pilot project onboarding complete (3 hours)  
✅ Mode A grouping validated in ≤15 minutes  
✅ Mode B documentation for 3 modules in ≤30 minutes each  
✅ First documented PR CI validation passes  
✅ Visual Studio workflow tested and documented  
✅ Two additional modules documented independently  
✅ 2-4 week pilot period completed with metrics  
✅ Pilot retrospective conducted; lessons documented  
✅ Onboarding checklist finalized  
✅ Second project onboarded successfully  
✅ Self-reporting block present in 100% of observed pilot Mode B sessions (or absence events documented with root cause)  
✅ `<!-- akr-generated -->` metadata header present in 100% of merged module docs (validated by CI)  

**Exit gate:** Phase 2 retrospective complete; Phase 2.5 authorized by standards lead **in writing** (GitHub comment, email, or approval record) before Phase 2.5 begins.

---

**Next Phase:** [Phase 2.5: Coding Agent Spike](PHASE_2_5_CODING_AGENT_SPIKE.md)

**Related Documents:**
- [Phase 1: Foundation](PHASE_1_FOUNDATION.md)
- [Implementation Plan Overview](IMPLEMENTATION_PLAN_OVERVIEW.md)
- [Implementation-Ready Analysis](../akr_implementation_ready_analysis.md) — Part 13
