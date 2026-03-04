# AKR Documentation Governance — Implementation Plan Overview

**Engineering Standards | Confidential | March 2026**

---

## Executive Summary

This implementation plan transforms the AKR Documentation Governance system from an MCP server-based prototype to a production-ready, Copilot-native solution using Agent Skills, GitHub Actions, and module-based documentation architecture. The plan synthesizes findings from seven independent reviews and establishes a phased, risk-mitigated path to deployment.

### Key Strategic Decisions

| Decision | Rationale |
|---|---|
| **Archive `akr-mcp-server`** after preservation steps | Copy validation baselines/tests first; remove workflow dependencies |
| **Module-based architecture** | Groups 3-8 related files per doc; prevents context saturation |
| **Agent Skills as primary workflow** | Cross-surface (VS Code, Copilot CLI, coding agent), zero infrastructure |
| **Charter compression** as Phase 0 blocker | Backend charter at ~11,000 tokens guarantees failure without compression |
| **Binary Phase 2.5 gate** | Coding agent must be tested before custom Azure Function is justified |
| **Deterministic Phase 4** | No AI in GitHub Actions; human-refined structured output |

---

## Implementation Phases

### Phase Dependencies

```
Phase 0 (Prerequisites)
    ↓ BLOCKING GATE
Phase 1 (Foundation)
    ↓ 
Phase 2 (Pilot Onboarding)
    ↓
Phase 2.5 (Coding Agent Spike)
    ↓ GO/NO-GO DECISION
Phase 3 (Automation Extension) [CONDITIONAL]
    ↓
Phase 4 (Feature Consolidation)
```

### Phase Overview

| Phase | Duration | Deliverables | Blocking Criteria |
|---|---|---|---|
| **Phase 0: Prerequisites** | 1-2 weeks | Condensed charters (3), Agent Skill, modules.yaml schema, pre-pilot tests (5) | All 5 pre-pilot tests PASS or have fallback |
| **Phase 1: Foundation** | 3-5 weeks | Templates (2 adapted), validate_documentation.py, CI workflow, schemas (1 new) | CI validation working; pilot-ready release tag v1.0.0 |
| **Phase 2: Pilot Onboarding** | 1-2 weeks per project | Pilot project complete end-to-end, retrospective, onboarding checklist | Zero validation failures; <15 min grouping time |
| **Phase 2.5: Coding Agent Spike** | 1 week | Acceptance test results; go/no-go recommendation | PASS → Phase 3 skipped; FAIL → Phase 3 authorized |
| **Phase 3: Automation Extension** | 2-4 weeks (conditional) | Custom @doc-agent or Copilot Studio agent | Only if Phase 2.5 documents specific failure modes |
| **Phase 4: Feature Consolidation** | 3-4 weeks | consolidate.py, feature-registry, cross-repo workflows | 6 weeks zero bypass + ≥80% module coverage (hard gate) |

---

## Success Criteria

### Phase-Level Success

| Phase | Success Metric | Target |
|---|---|---|
| Phase 0 | Pre-pilot test pass rate | 5/5 or documented fallback for each |
| Phase 1 | validate_documentation.py accuracy | Zero false positives on module docs |
| Phase 2 | Time-to-first-documented-PR | ≤45 minutes (grouping + generation + review) |
| Phase 2.5 | Coding agent section completeness | 100% required sections, zero truncations |
| Phase 3 | Custom agent line count | ≤500 lines; CI-enforced |
| Phase 4 | Cross-repo consolidation time | <2 minutes for 3-component feature |

### System-Level Success

**Quantitative:**
- **Module documentation generation:** ≤30 minutes per module (developer time)
- **Grouping validation:** ≤15 minutes per project (developer time)
- **CI validation pass rate:** ≥95% on first PR
- **Unresolved ❓ marker rate:** <5% after developer review
- **Standards drift incidents:** Zero (enforced by `minimum_standards_version`)

**Qualitative:**
- **Developer satisfaction:** "Faster than writing docs manually" (pilot retrospective)
- **Tech lead confidence:** "Documentation reflects actual system state" (validation accuracy)
- **Product owner value:** "Feature docs enable cross-team coordination" (Phase 4)

---

## Risk Register

### Critical Risks

| Risk | Impact | Mitigation | Contingency |
|---|---|---|---|
| **Context saturation on large modules** | 🔴 High | Charter compression to ~2,500 tokens; `max_files: 8` governance constraint | Provide `max_files: 5` guidance for large-file modules; stress-test boundary is 8 files |
| **Hosted MCP context unavailable** | 🟡 Medium | Pre-pilot Test 2 validates availability | Use `.github/copilot-instructions.md` with condensed charter that stays within the 2,500-token budget |
| **Coding agent fails acceptance criteria** | 🟡 Medium | Phase 2.5 binary test with fallback | Phase 3 custom agent authorized only for documented failure modes |
| **Premium request overage** | 🟡 Medium | Model cost in Phase 0; establish budget baseline | Set billing alerts; monthly review with management |
| **Legal/compliance blocks AI processing** | 🔴 High | Pre-pilot Test 5 (legal sign-off) | Manual documentation with templates only; no AI generation |
| **Cross-platform validator failures** | 🟠 Low | Test Ubuntu + macOS + Windows in Phase 1 | Fix platform-specific file path or YAML parsing issues |
| **Tag-registry distribution lag** | 🟠 Low | Verify `tag-registry.json` is distributed (not just committed) before Phase 2 workflows reference it | Implement pre-flight check in Phase 2 tag verification; use `git lfs` if needed for large registries |

### Deferred Risks (Post-Pilot)

- **Standards version drift across teams:** Mitigated by `minimum_standards_version` validation
- **Business capability tag collision across repos:** Mitigated by centralized `tag-registry.json` + distribution workflow
- **Phase 4 repository permission issues:** Mitigated by sparse checkout + PAT with minimal scopes

---

## Architecture Overview

### Three-Tier Documentation Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│  LEVEL 3: Feature Consolidation                             │
│  Template: feature-consolidated.md                          │
│  Producer: consolidate.py (deterministic Python)            │
│  Audience: Product Owner, QA Lead, Tech Lead                │
└────────────────────┬────────────────────────────────────────┘
                     │ reads from
     ┌───────────────┴───────────────┐
     ▼                               ▼
┌──────────────────────┐   ┌────────────────────────────────┐
│  LEVEL 1             │   │  LEVEL 2                       │
│  Module Docs         │   │  Database Object Docs          │
│  (3-8 files grouped) │   │  (individual objects)          │
│  Producer: Agent Skill│   │  Producer: Agent Skill Mode B │
│  Mode B              │   │  or manual                     │
└──────────────────────┘   └────────────────────────────────┘
        ▲                               ▲
        └───────────────────────────────┘
              Agent Skill Mode A
              (proposes groupings)
```

### Technology Stack

| Layer | Technology | Licensing |
|---|---|---|
| **Workflow encoding** | Agent Skills (SKILL.md) | Free (GitHub Copilot seat) |
| **Interactive generation** | VS Code agent mode | Copilot Business/Enterprise |
| **Autonomous generation** | Copilot coding agent | Copilot Business/Enterprise |
| **CI validation** | Python + GitHub Actions | Free |
| **Prose quality** | Vale | Open source |
| **Standards distribution** | GitHub Hosted MCP Context Sources | Copilot Business (tier-dependent) |
| **Cross-functional review (Phase 3+)** | Copilot Studio (Teams) | M365 Copilot (premium) |

---

## Pre-Implementation Checklist

Before Phase 0 begins, confirm:

- [ ] Legal and security sign-off on Copilot processing organizational code (Pre-pilot Test 5)
- [ ] GitHub Copilot Business or Enterprise license confirmed
- [ ] Management approval for premium request budget allocation
- [ ] Pilot project identified (recommended: TrainingTracker.Api)
- [ ] Standards team capacity allocated (Phase 0: 1 FTE; Phase 1: 1-2 FTE)
- [ ] Development team representative assigned for pilot (grouping validation + retrospective)
- [ ] Default `allowWorkflowBypass: false` verified in all module configs (governance gate)

---

## Phase-Specific Plans

Each phase has a dedicated implementation plan document:

1. [Phase 0: Prerequisites](PHASE_0_PREREQUISITES.md) — Charter compression, Agent Skill, pre-pilot tests
2. [Phase 1: Foundation](PHASE_1_FOUNDATION.md) — Templates, validator, CI, schemas
3. [Phase 2: Pilot Onboarding](PHASE_2_PILOT_ONBOARDING.md) — End-to-end pilot, retrospective, onboarding checklist
4. [Phase 2.5: Coding Agent Spike](PHASE_2.5_CODING_AGENT_SPIKE.md) — Binary test with acceptance criteria
5. [Phase 3: Automation Extension](PHASE_3_AUTOMATION_EXTENSION.md) — Conditional custom agent or Copilot Studio
6. [Phase 4: Feature Consolidation](PHASE_4_FEATURE_CONSOLIDATION.md) — Cross-repository deterministic aggregation

---

## Governance and Compliance

### Version Management

- **Standards version pinning:** Each project pins `standards_version` in `modules.yaml`
- **Minimum version enforcement:** `validate_documentation.py` fails if `standards_version` < `minimum_standards_version`
- **Breaking changes:** Require major version bump (e.g., v1.x → v2.0)
- **Non-breaking additions:** Minor version bump (e.g., v1.0 → v1.1)

### Compliance Mode Progression

| Mode | Behavior | Graduation Trigger |
|---|---|---|
| **pilot** | `--fail-on=never` (warn only) | Pilot retrospective complete |
| **production** | `--fail-on=needs` (blocks on unresolved ❓) | 4 weeks zero ❓ in production |

### Documentation Ownership

- **Level 1 (Module docs):** Development team owns; tech lead approves
- **Level 2 (DB object docs):** DBA or backend lead owns
- **Level 3 (Feature consolidation):** Product owner owns; QA lead + tech lead approve

---

## Realistic Timeline Estimate

### Total Duration

**estimate: 14-20 weeks (3.5-5 months) from Phase 0 start to Phase 4 completion**

### Detailed Breakdown

| Phase | Duration | Real-World Notes | Cumulative |
|---|---|---|---|
| **Phase 0** | 1-2 weeks | Charter compression + pre-pilot tests may take longer if legal review (Test 5) is slow; recommend parallel initiation | Week 2 |
| **Phase 1** | 3-5 weeks | `validate_documentation.py` implementation ~2 weeks; CI workflow + schema updates ~1-2 weeks; contingency for cross-platform issues | Week 7 |
| **Phase 2** | 3-6 weeks | 1-2 week pilot onboarding + 2-4 week pilot execution + 1 week retrospective/analysis = 4-7 weeks minimum. **Note:** Phase 2.5 **cannot start** until retrospective is complete | Week 14 |
| **Phase 2.5** | 1-2 weeks | Depends on Phase 2 completion; binary spike with fixed acceptance criteria | Week 16 |
| **Phase 3** | 2-4 weeks (conditional) | Only if Phase 2.5 FAIL; skipped if PASS | Week 20 (if needed) |
| **Phase 4** | 3-4 weeks | Starts after Phase 2 stability plateau (6+ weeks zero bypass); Phase 3 prereq if FAIL | Week 24 (best case) / Week 28 (with Phase 3) |

### Sequencing Notes

1. **Phase 2 retrospective lag:** The biggest timeline risk is Phase 2 running for 4 weeks, retrospective adding 1 week. Phase 2.5 start is blocked until this completes.
   - **Mitigation:** Run pre-retrospective synthesis weekly; compile final retrospective incrementally
   - **Early start allowance:** If Phase 2 completes faster, Phase 2.5 can start within days

2. **Phase 4 prerequisites:** Requires 6 weeks post-Phase-2 stability (zero bypass events, ≥80% module coverage). This is a **hard gate**, not a duration estimate.
   - **Timing:** If Phase 2 ends week 6, Phase 4 starts week 12 (6-week wait) → ends week 16
   - **Early win:** Stabilit metrics earned Week 3 of Phase 2 → Phase 4 can start Week 9

3. **Phase 3 contingency:** If Phase 2.5 FAIL, adds 2-4 week delay to Phase 4. Plan for this in communication.

### Compressed Timeline (If All Conditions Optimal)

- Phase 0 (2 weeks) + Phase 1 (5 weeks) + Phase 2 (3 weeks + 1 week retro) + 2-week stability wait + Phase 2.5 (1 week) + Phase 4 (3 weeks) = **17 weeks**

### Extended Timeline (With Typical Slowdowns)

- Phase 0 (2 weeks, legal delay +2) + Phase 1 (5 weeks) + Phase 2 (6 weeks pilot + 1 retro) + 6-week stability wait + Phase 2.5 (2 weeks) + Phase 3 (3 weeks if FAIL) + Phase 4 (4 weeks) = **31 weeks**

**Recommended planning baseline: 20-22 weeks (5-5.5 months)**

---

## Monitoring and Reporting

### Phase 0-2 Metrics

- **Charter compression ratio:** Target ~22% of original (11,000 → 2,500 tokens)
- **Pre-pilot test results:** 5/5 pass or documented fallback
- **Pilot time-to-doc:** Track per module; target ≤30 minutes
- **Grouping accuracy:** % of Mode A proposals requiring reassignment
- **CI validation accuracy:** False positive rate on module docs

### Phase 2.5+ Metrics (Conditional)

- **Coding agent success rate:** % of sessions meeting all acceptance criteria
- **Premium request consumption:** Requests per module; monthly cost
- **Validator output contract stability:** `summary.total_errors`, `summary.total_warnings`, `summary.average_completeness` unchanged for v1.x
- **Custom agent invocations:** If Phase 3; track usage + cost
- **Phase 4 consolidation time:** Target <2 min per 3-component feature

### Reporting Cadence

- **Phase 0:** Daily standup during pre-pilot tests
- **Phase 1:** Weekly release note on deliverable completion
- **Phase 2:** Post-pilot retrospective report
- **Phase 2.5:** Binary pass/fail report + go/no-go recommendation
- **Phase 3+:** Monthly usage + cost report

---

## Document Status

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | March 2026 | Standards Team | Initial implementation plan based on seven-review synthesis |

---

**Related Documents:**
- [Implementation-Ready Analysis](../akr_implementation_ready_analysis.md) — Source material for this plan
- [Architecture Diagram](../akr_architecture_diagram.html) — Interactive system architecture
- [Developer Reference](../DEVELOPER_REFERENCE.md) — Technical specifications
- [Validation Guide](../VALIDATION_GUIDE.md) — CI and validation rules

**Status:** 🟢 Ready for Phase 0 execution pending pre-implementation checklist completion
