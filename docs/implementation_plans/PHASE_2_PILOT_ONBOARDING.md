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
| **Verify `businessCapability` tag distribution** | Standards author | Run or confirm `distribute-tag-registry.yml` completed; all tags used in `modules.yaml` are available in pilot project's `.github/depends/tag-registry.json` (or equivalent location) | 20 min |
| Configure hosted MCP context source OR `.github/copilot-instructions.md` | Pilot dev | Context source configured; condensed backend charter accessible | 30 min |
| Copy Agent Skill to project | Pilot dev | `.github/skills/akr-docs/SKILL.md` present; loads in agent mode | 15 min |
| Deploy `validate-documentation.yml` | Pilot dev | Workflow file in `.github/workflows/`; triggered on draft PR | 30 min |
| Create initial `modules.yaml` | Pilot dev | Project section complete; `modules[]` empty; `database_objects[]` empty | 30 min |
| Configure Vale | Pilot dev | Vale rules at `validation/vale-rules/`; `.vale.ini` configured | 30 min |
| Test CI workflow | Pilot dev | Trigger workflow on draft PR; verify it runs without errors | 30 min |
| Create CODEOWNERS file | Pilot dev | Standards team + tech lead as owners for `docs/**` AND `modules.yaml` (e.g., `docs/** @org/standards-team @tech-lead` + `modules.yaml @org/standards-team`) | 20 min |

Recommended CODEOWNERS additions:
- `docs/modules/**  @org/standards-team @tech-lead`
- `modules.yaml     @org/standards-team`

**Critical:** Submodule must reference the v1.0.0 release tag, not `main`. Using `main` will cause instability if breaking changes are merged to `core-akr-templates` after pilot begins.

**Critical:** `modules.yaml` must be in CODEOWNERS to prevent rogue changes to `compliance_mode` or `max_files` limits without standards team review.

### Critical: Submodule Rollback and Patch Strategy

**Why this matters:** `core-akr-templates` will be actively developed after v1.0.0. If a validation bug is discovered mid-pilot, you have three options:

1. **Hotfix release** (Recommended): Standards team authors patch release (v1.0.1), pilot project updates submodule pin
2. **Stay on v1.0.0 + local workaround**: Pilot project applies git patch locally; documents workaround; rolls forward on next release
3. **Fork fix to feature branch**: Pilot project temporarily uses branch pin; merges back when patch released

**Decision:** 
- Primary: Watch for validation errors; escalate to standards team for hotfix release decision
- Escalation criteria: Blocking CI validation (phase can't proceed), affecting >1 module, or required for compliance
- Hotfix SLA: 24 hours to release patch if escalated

**Approval:** Standards lead + infrastructure lead authorize patch release; communication goes out before pin update

---

### Critical: Mode A → Mode B Sequencing (Cannot Skip Mode A)

**Governance rule:** Mode B (documentation generation) **cannot run** without an **approved Mode A** `modules.yaml`. 

**Enforcement:**
- CI check prevents draft PRs with Mode B doc changes if `modules.yaml` status is `draft`
- Error message: "modules.yaml must be approved (status != draft) before generating documentation"
- Developer workaround: Contact standards team to manually approve `modules.yaml`; only for exceptions

**Why:** Skipping Mode A to save time leads to incorrect module groupings, which invalidates all downstream documentation and Phase 4 consolidation.

---

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

**Critical first step: Verify tag distribution (before creating modules.yaml)**

Before creating the pilot project's `modules.yaml`, confirm that business capability tags have been **distributed** to application repos. The tags are added to `tag-registry.json` in Phase 0, but `distribute-tag-registry.yml` is the distribution mechanism. If tags aren't distributed when CI runs `validate_documentation.py`, validation will fail on "unknown `businessCapability`".

**Verification steps:**
1. Confirm `CourseCatalogManagement` (+ others) are committed to `tag-registry.json` in `core-akr-templates`
2. Run `distribute-tag-registry.yml` workflow (manual trigger or verify scheduled run completed)
3. Verify that distribution destination (`.github/depends/tag-registry.json` or equivalent in pilot project) contains the new tags
4. Only then create pilot project's `modules.yaml` with those `businessCapability` values

**Ownership:** Standards author ensures distribution before signaling "ready for modules.yaml authoring"

---

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
| Complete onboarding checklist | Pilot dev | All 8 items checked | 3 hours |
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

### Expected Output

Draft `modules.yaml` with:
- **3-5 module groupings** (e.g., CourseDomain, EnrollmentDomain, UserDomain)
- Each module has `files[]` populated with 3-8 files
- `project_type` assigned based on structure detection
- `businessCapability` field populated (must match `tag-registry.json`)
- `database_objects[]` populated with individual DB tables/procedures
- `unassigned[]` populated with shared infrastructure files

### Developer Validation Tasks

| Validation | What to Check | Time |
|---|---|---|
| **Semantic accuracy** | Do grouped files actually implement the same domain concept? | 3 min |
| **Module naming** | Do module names reflect domain language (not file names)? | 2 min |
| **File count** | Does any module exceed `max_files: 8`? If so, split. | 2 min |
| **Misplaced files** | Are any files in the wrong module? Reassign. | 3 min |
| **Database objects** | Are all DB objects typed correctly (table/view/procedure)? | 2 min |
| **Unassigned rationale** | Do `unassigned[]` reasons make sense? | 2 min |
| **Business capability tags** | Do all `businessCapability` values exist in `tag-registry.json`? | 1 min |

**Total validation time target:** ≤15 minutes

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
| Invoke Mode A | Pilot dev | Agent generates draft `modules.yaml` | 5 min (agent time) |
| Review and validate groupings | Pilot dev | All checklist items reviewed; adjustments made | 15 min |
| Open Mode A PR | Pilot dev | Draft PR with checklist; assigned to tech lead | 5 min |
| Tech lead approval | Tech lead | Groupings approved; PR merged | 5 min |
| Record validation time | Standards author | Actual time vs. 15 min target documented | 2 min |
| Capture workflow timestamps | Standards author | Mode A PR open/merge, Mode B PR open, CI start/end timestamps captured for retrospective | 5 min |

### Success Metrics

- **Grouping accuracy:** ≥90% of proposed groupings accepted without reassignment
- **Validation time:** ≤15 minutes from draft to approval
- **Clarity:** Developer understands what to validate (no confusion)

---

## Deliverable 3: Mode B — Documentation Generation

### Objective

Run Agent Skill Mode B to generate documentation for CourseDomain module; developer reviews and fills `❓` sections.

### Invocation

**In VS Code Copilot Chat:**
```
@workspace generate documentation for CourseDomain module
```

### Expected Output

Draft `docs/modules/CourseDomain_doc.md` with:
- **Module Files section** listing all 5 files with roles
- **Operations Map** covering all public methods across all files
- **Architecture Overview** text diagram (Controller → Service → Repository → DB)
- **Business Rules** table with "Why It Exists" and "Since When" columns (some `❓`)
- **Data Operations** section covering all reads and writes
- **Questions & Gaps** section populated with inferred assumptions
- **Markers:** `🤖` on inferred content; `❓` on sections requiring human input

### Developer Content Review Tasks

| Review | What to Fill/Validate | Time |
|---|---|---|
| **❓ sections** | Fill missing business context or mark DEFERRED with justification | 10 min |
| **Business Rules** | Confirm "Why It Exists" column accuracy; add "Since When" dates | 5 min |
| **Data Operations** | Verify all reads and writes covered; add missing operations | 5 min |
| **Questions & Gaps** | Answer open items or mark as DEFERRED | 5 min |
| **Architecture diagram** | Validate full stack is correct | 2 min |
| **Operations Map** | Spot-check that all public methods listed | 3 min |

**Total content review time target:** ≤30 minutes

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
| Review and fill content | Pilot dev | All checklist items completed | 30 min |
| Run `validate_documentation.py` locally | Pilot dev | Zero errors; all required sections present | 5 min |
| Open Mode B PR | Pilot dev | Draft PR with completed checklist | 5 min |
| Tech lead approval | Tech lead | Content accuracy validated; PR approved | 10 min |
| Record generation time | Standards author | Actual time vs. 30 min target documented | 2 min |

### Success Metrics

- **Section completeness:** 100% required sections present
- **Content review time:** ≤30 minutes from draft to PR ready
- **Validation pass rate:** Zero validator errors on first run
- **❓ fill rate:** ≥95% of `❓` sections filled or marked DEFERRED with justification

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

### Visual Studio Considerations

- **Skill loading:** May require different `.github/` path configuration
- **Copilot Chat integration:** UI differs from VS Code; document invocation patterns
- **MCP context source:** Confirm hosted MCP works in VS (if Test 2 passed)
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

### Retrospective Outputs

- **Quantitative summary:** Metrics table with actuals vs. targets
- **Friction point log:** Issues encountered with priority ratings
- **Template updates required:** Specific sections to add/modify/remove
- **Validator updates required:** Rules that fired false positives or missed errors
- **Onboarding checklist refinement:** Steps that were unclear or redundant
- **v1.1.0 scope:** Features to include in next minor release
- **Phase 2.5 authorization:** Go/no-go for coding agent spike

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
- [ ] Copy Agent Skill to .github/skills/akr-docs/
- [ ] Deploy validate-documentation.yml workflow
- [ ] Create initial modules.yaml (project section only)
- [ ] Configure Vale rules
- [ ] Test CI workflow on draft PR
- [ ] Create CODEOWNERS file

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

---

## Risk Register (Phase 2 Specific)

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| Pilot developer unavailable mid-pilot | 🟡 Medium | 🟠 Low | Assign backup developer before pilot begins |
| Mode A groups files incorrectly | 🟡 Medium | 🟡 Medium | 15-minute validation catches; developer reassigns |
| CI false positives frustrate team | 🔴 High | 🟠 Low | Monitor false positive rate; hot-fix validator if >5% |
| Visual Studio workflow broken | 🟡 Medium | 🟠 Low | Phase 0 Visual Studio validation passed; pilot validates real project integration; document workarounds if issues found |
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

**Exit gate:** Phase 2 retrospective complete; Phase 2.5 authorized if metrics support expanded rollout.

---

**Next Phase:** [Phase 2.5: Coding Agent Spike](PHASE_2.5_CODING_AGENT_SPIKE.md)

**Related Documents:**
- [Phase 1: Foundation](PHASE_1_FOUNDATION.md)
- [Implementation Plan Overview](IMPLEMENTATION_PLAN_OVERVIEW.md)
- [Implementation-Ready Analysis](../akr_implementation_ready_analysis.md) — Part 13
