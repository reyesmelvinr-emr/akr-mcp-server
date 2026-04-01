# Phase 2.6: Governance Stability Assessment - Implementation Plan

**Duration:** 1 week  
**Team:** Standards lead (primary) + standards author (data analysis)  
**Prerequisite:** Phase 2.5 complete (PASS or FAIL); Phase 2 retrospective data available  
**Status:** 🟠 MANDATORY - runs regardless of Phase 2.5 verdict

---

## Overview

Phase 2.5 tests whether the coding agent meets acceptance criteria. Phase 2.6 tests whether the SKILL.md compliance architecture is structurally stable enough for production use, using measured data from Phase 2 and 2.5.

**The question Phase 2.6 answers:** Do LLM variance and model update risk require targeted migration of any governance steps from SKILL.md to code-defined deterministic implementations?

This question is independent of Phase 2.5's binary verdict. A Phase 2.5 PASS means the coding agent works. It does not mean SKILL.md governance is reliable at production scale across model updates.

---

## Why This Phase Exists

SKILL.md governance fidelity is LLM-dependent:
- GPT-4o pass rate: ~75% (Operations Map truncation on large modules documented in SKILL-COMPAT.md)
- Claude Sonnet 4.6 pass rate: >=90%
- GitHub Copilot's underlying model updates without announcement - a skill passing at 90% today may degrade silently

Code-defined Python skills (`@skill.script`) are deterministic for extraction tasks: a Python AST parser enumerates all methods regardless of model version. However, code-defined skills are only appropriate for deterministic tasks - interpretation tasks (business rules, architectural narrative, Q&G sections) still require LLM reasoning.

**Phase 2.6 determines whether the LLM variance problem is acceptable at the measured scale, or whether specific extraction steps should be migrated to deterministic code before the system is declared production-ready.**

---

## Acceptance Criteria

Phase 2.6 is complete when:

1. ✅ All five Phase 2.5 handoff data items received
2. ✅ Assessment criteria evaluated against measured data
3. ✅ Verdict documented: "SKILL.md Acceptable", "Targeted Migration Authorized", or "Full Migration Recommended"
4. ✅ If migration authorized: specific steps identified; SDK verification requirement documented
5. ✅ SKILL-COMPAT.md Governance Stability Assessment Record updated
6. ✅ Standards lead sign-off in writing

**Phase 4 gate:** Phase 4 proceeds unless verdict is "Full Migration Recommended". Targeted migrations run in parallel with Phase 4 and do not block it.

---

## Deliverable 1: Data Collection and Measurement

### Required Inputs (from Phase 2.5 Handoff)

| Data Item | Source | How to Measure |
|---|---|---|
| First-run CI pass rate | Phase 2.5 acceptance matrix + Phase 2 retrospective | Count PRs with zero validator errors on first CI run ÷ total Mode B PRs |
| Operations Map completeness on GPT-4o | Manual review of Phase 2.5 Test Cases 1-3 Mode B output | Count correctly enumerated methods (public + private + async) ÷ total methods present in source files |
| Self-reporting block absent rate | Phase 2 retrospective + Phase 2.5 run logs | Count Mode B responses missing `✅ akr-docs INVOKED` block ÷ total Mode B responses |
| benchmark.json actual pass rates | Phase 2.5 benchmark recording | Read from benchmark.json `gpt-4o` and `claude-sonnet-4-6` keys |
| New GPT-4o failure modes | SKILL-COMPAT.md v1.1 | Review model-specific failure mode entries added during pilot |

### Measurement Procedures (Appendix)

**Friction score (% of reviews completed in-editor without opening GitHub):**
Proxy measurement - not directly instrumentable from logs. Collect via a 3-question retrospective form completed by each pilot developer at the end of Phase 2:
1. "Did you open GitHub to complete the Mode A review?" (Yes/No per module)
2. "Did you open GitHub to complete the Mode B content review?" (Yes/No per module)
3. "If yes, what made you go to GitHub?" (free text)
Friction score = (No + No responses) ÷ total responses × 100. Target: >=80%.

**Operations Map completeness (% of methods correctly enumerated on GPT-4o):**
Manual verification procedure for Phase 2.5 test cases:
1. For each test module, run: `grep -E "^\s+(public|private|protected|async|static)" [source_files]` to produce a ground-truth method list.
2. Count total methods in the ground-truth list.
3. Check each method name against the Operations Map section in the Mode B output for that module.
4. Completeness rate = (matched methods) ÷ (total ground-truth methods) × 100.
Note: this procedure applies to C#/TypeScript. For other languages, adapt the grep pattern to the language's visibility keywords.
A light helper script (`evals/scripts/check_ops_map_completeness.py`) should be created as part of this deliverable - it automates steps 1-3 against the test case source files and the benchmark.json output.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Collect all five data items from Phase 2.5 handoff | Standards author | All items present and measured; no TBD entries | 2 hours |
| Run Operations Map completeness procedure on Phase 2.5 test case outputs | Standards author | Method-level count for all 3 test cases; completeness rate computed | 1 hour |
| Cross-reference benchmark.json pass rates against baseline | Standards author | Delta documented per model per eval case | 30 min |
| Create `evals/scripts/check_ops_map_completeness.py` | Standards author | Script automates ground-truth method extraction and comparison; tested on CourseDomain source files | 1 hour |

---

## Deliverable 2: Governance Stability Assessment

### Assessment Criteria

| Criterion | Acceptable | Requires Targeted Migration |
|---|---|---|
| First-run CI pass rate | >=95% | <90% |
| Operations Map completeness on GPT-4o | >=90% of methods (public + private + async) | Private/async methods consistently missing across test cases |
| Self-reporting block absent rate | <5% of Mode B runs | >=10% of Mode B runs |
| Post-model-update regression potential | Baseline gap <=10 points (GPT-4o vs. Claude Sonnet) | Baseline gap >10 points AND growing trend across Phase 2 -> Phase 2.5 |

### Verdict Definitions

**"SKILL.md Governance Acceptable for Production"**
All four criteria within acceptable range. Continue with SKILL.md as primary governance mechanism. Code-defined skills remain in SKILL-COMPAT.md Future Enhancement Paths. No additional migration authorized. Proceed to Phase 3 (if Phase 2.5 FAIL) or Phase 4 (if Phase 2.5 PASS).

**"Targeted Migration Authorized"**
One or more criteria outside acceptable range. Authorize `@skill.script` migration for the specific failing step only - not a full v2.0 rewrite. SDK verification required before implementation. Migration runs in parallel with Phase 4; does not block it.

Migration targets by failing criterion:
- Operations Map completeness fails -> migrate to deterministic AST-based `@skill.script` (Scope Example 1 in Phase 3)
- Step skipping rate is high -> investigate `disable-model-invocation: true` frontmatter compliance; consider co-registration of a code-defined skill that enforces step sequencing programmatically
- Post-model-update regression is severe -> accelerate migration of all deterministic extraction steps; retain LLM only for interpretation sections

**"Full Migration Recommended"**
Three or more criteria outside acceptable range. Full code-defined skill package recommended as Phase 3 Path D or the next major version increment. Phase 4 must not begin documentation runs until full migration scope and timeline are documented and management signs off.

### Critical Distinction from Phase 3

Phase 3 is authorized by Phase 2.5 FAIL for specific **coding agent** failures.
Phase 2.6 migration is authorized by governance stability assessment criteria for **SKILL.md reliability** failures.
Both can be active simultaneously - they are independent authorizations with separate authorization chains.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Evaluate each criterion against measured data | Standards lead | Pass/fail per criterion with evidence cited | 2 hours |
| Document verdict | Standards lead | One of three verdict definitions selected; evidence attached | 1 hour |
| If migration authorized: identify steps and SDK verification plan | Standards author | Step name, target `@skill.script`, SDK verification test procedure | 2 hours |

---

## Deliverable 3: SKILL-COMPAT.md Governance Stability Record Update

**ADD** the following section to `SKILL-COMPAT.md`:

```markdown
## Governance Stability Assessment Record

| Phase | Assessment Date | CI Pass Rate | Ops Map Completeness (GPT-4o) | Step Skip Rate | GPT-4o Baseline Gap | Verdict | Migration Authorized |
|---|---|---|---|---|---|---|---|
| Phase 2.6 | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Phase 4 Pre-Run | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

**Verdict definitions:**
- `SKILL.md Acceptable`: All four criteria within acceptable range
- `Targeted Migration Authorized`: One or more criteria outside range; steps listed in "Migration Authorized" column
- `Full Migration Recommended`: Three or more criteria outside range; Phase 4 blocked until scope documented

**Migration tracking:**
| Step | Migration Status | v2.0 Implementation Target | SDK Verified | Evidence |
|---|---|---|---|---|
| Operations Map extraction | NOT_STARTED | `akr.module_doc_generation.extract_operations` | NOT_VERIFIED | - |
| Draft writing | NOT_STARTED | `akr.module_doc_generation.build_initial_draft` | NOT_VERIFIED | - |
| Mode A manifest patching | NOT_STARTED | `akr.module_boundary.patch_modules_manifest` | NOT_VERIFIED | - |
| Validation | NOT_STARTED | `akr.validation_skill.validate_file` | NOT_VERIFIED | - |
```

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Update SKILL-COMPAT.md Governance Stability Assessment Record | Standards author | Phase 2.6 row populated with all data; verdict recorded | 30 min |
| Distribute updated SKILL-COMPAT.md via distribute-skill.yml | Standards author | Updated file reaches registered repos via PR | 15 min |

---

## Gate Decision and Sign-Off

**Exit Gate:** Standards lead documents verdict in writing (GitHub comment, email, or approval record) before Phase 3 or Phase 4 begins.

**Blocking rule:** Phase 4 proceeds unless verdict is "Full Migration Recommended". Targeted migrations run in parallel with Phase 4 and do not block it. "Full Migration Recommended" requires management sign-off before Phase 4 documentation runs begin.

---

**Related Documents:**
- [Phase 2.5: Coding Agent Spike](PHASE_2_5_CODING_AGENT_SPIKE.md) - Data source
- [Phase 3: Automation Extension](PHASE_3_AUTOMATION_EXTENSION.md) - Parallel authorization path
- [Phase 4: Feature Consolidation](PHASE_4_FEATURE_CONSOLIDATION.md) - Downstream consumer
- [Implementation-Ready Analysis](../akr_implementation_ready_analysis.md) - Part 16 (reliability), Part 19 (v2.0 reference)
