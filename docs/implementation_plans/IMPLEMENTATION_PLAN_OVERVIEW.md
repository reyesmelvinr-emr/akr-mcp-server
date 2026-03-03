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
| **Phase 4: Feature Consolidation** | 3-4 weeks | consolidate.py, feature-registry, cross-repo workflows | 3-component feature consolidated in <2 min |

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
| **Hosted MCP context unavailable** | 🟡 Medium | Pre-pilot Test 2 validates availability | Use `.github/copilot-instructions.md` with condensed charter (fits in ~4,000 chars) |
| **Coding agent fails acceptance criteria** | 🟡 Medium | Phase 2.5 binary test with fallback | Phase 3 custom agent authorized only for documented failure modes |
| **Premium request overage** | 🟡 Medium | Model cost in Phase 0; establish budget baseline | Set billing alerts; monthly review with management |
| **Legal/compliance blocks AI processing** | 🔴 High | Pre-pilot Test 5 (legal sign-off) | Manual documentation with templates only; no AI generation |
| **Cross-platform validator failures** | 🟠 Low | Test Ubuntu + macOS + Windows in Phase 1 | Fix platform-specific file path or YAML parsing issues |

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
