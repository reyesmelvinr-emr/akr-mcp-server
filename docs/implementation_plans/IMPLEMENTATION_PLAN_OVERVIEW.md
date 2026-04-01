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
| **`@skill.script` before Azure Functions** | Code-defined in-process scripts evaluated first for Phase 3 Path B; Azure Functions authorized only if subprocess isolation required (see Phase 3 Deployment Options) |
| **v2.0 code-defined skills are Phase 3+ scope, not Phase 1-2 replacements** | SKILL.md is the delivery mechanism for GitHub Copilot interactive surfaces; code-defined Python skills require `agent-framework` SDK (currently unconfirmed on target surface) and are authorized only after Phase 2.6 Governance Stability Assessment. Mixing architectures mid-pilot invalidates benchmark data and removes Phase 2.6 assessment evidence. |
| **Section-Scoped Generation (SSG) as Mode B generation strategy** | Loads charter guidance and source files per section rather than all at once; reduces per-pass context load without requiring additional charter condensation; forward payload discipline prevents context re-expansion across passes; maps naturally to Copilot coding agent background execution |

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
    ↓ MANDATORY (regardless of PASS/FAIL)
Phase 2.6 (Governance Stability Assessment)
    ↓
Phase 3 (Automation Extension) [CONDITIONAL - authorized by Phase 2.5 FAIL or Phase 2.6 migration verdict]
    ↓
Phase 4 (Feature Consolidation)

Note: Phase 4 proceeds unless Phase 2.6 returns "Full Migration Recommended".
Targeted migrations authorized by Phase 2.6 run in parallel with Phase 4 and do not block it.
```

### Phase Overview

| Phase | Duration | Deliverables | Blocking Criteria |
|---|---|---|---|
| **Phase 0: Prerequisites** | 1-2 weeks | Condensed charters (3), Agent Skill (3 modes + frontmatter + self-reporting block), `modules.yaml` schema, pre-pilot tests (7), eval framework (`evals/` directory + `benchmark.json` baseline), `SKILL-COMPAT.md` skeleton | All 7 pre-pilot tests PASS or have fallback; `benchmark.json` baseline populated |
| **Phase 1: Foundation** | 3-5 weeks | Templates (2 adapted), `validate_documentation.py` (with metadata header check), CI workflow, schemas (1 new), hooks (`postToolUse` + `agentStop`), `SKILL-COMPAT.md` v1.0 | CI validation working; hooks distributed; pilot-ready release tag v1.0.0 |
| **Phase 2: Pilot Onboarding** | 1-2 weeks per project | Pilot project complete end-to-end, retrospective, onboarding checklist | Zero validation failures; <15 min grouping time |
| **Phase 2.5: Coding Agent Spike** | 1 week | Acceptance test results; go/no-go recommendation | PASS → Phase 3 skipped; FAIL → Phase 3 authorized |
| **Phase 2.6: Governance Stability Assessment** | 1 week | Governance stability verdict (SKILL.md acceptable or targeted migration authorized); `PHASE_2_6_GOVERNANCE_STABILITY.md` plan document | Phase 2.5 complete (PASS or FAIL); Phase 2 retrospective data available |
| **Phase 3: Automation Extension** | 2-4 weeks (conditional) | Custom @doc-agent or Copilot Studio agent | Only if Phase 2.5 documents specific failure modes |
| **Phase 4: Feature Consolidation** | 3-4 weeks | consolidate.py, feature-registry, cross-repo workflows | 3-component feature consolidated in <2 min |

---

## Success Criteria

### Phase-Level Success

| Phase | Success Metric | Target |
|---|---|---|
| Phase 0 | Pre-pilot test pass rate | 7/7 or documented fallback for each |
| Phase 1 | validate_documentation.py accuracy | Zero false positives on module docs |
| Phase 2 | Time-to-first-documented-PR | ≤45 minutes (grouping + generation + review) |
| Phase 2.5 | Coding agent section completeness | 100% required sections, zero truncations |
| Phase 3 | Custom agent line count | ≤500 lines; CI-enforced |
| Phase 4 | Cross-repo consolidation time | <2 minutes for 3-component feature |

### System-Level Success

**Quantitative:**
- **Module documentation generation:** ≤30 minutes per module (developer time)
- **SSG total generation time per module:** ≤30 minutes for Mode B generation only (SSG Passes 1-7). This is not the full Mode A -> Mode B -> review cycle. A compliant full workflow is: Mode A grouping validation (<=15 min) + Mode B SSG generation (<=30 min) + developer review setup (<=5 min) ≈ 50 minutes total. The existing Phase 2 success metric "Time-to-first-documented-PR: <=45 minutes" covers the full cycle and is unchanged - the SSG target is a sub-metric for generation only. Note: the <=45-minute metric measures active developer time (excludes coding agent background generation time). When Mode B runs asynchronously via the coding agent, the developer's active contribution is Mode A grouping (<=15 min) + review setup (<=5 min) = <=20 minutes active, well within the target.
- **SSG per-pass timing data:** Collected from >=80% of Mode B runs by end of Phase 2 pilot (timing unavailable on some surfaces is acceptable; see Part 18.5)
- **Slow-module rate:** <10% of modules trigger the 45-minute fallback threshold (tracked in `ssg-slow-module-events` monitoring metric)
- **Grouping validation:** ≤15 minutes per project (developer time)
- **Mode A update-run time (new file added to existing module):** ≤5 minutes (reads `modules.yaml`; proposes targeted addition; developer confirms) - baseline established in Phase 2 retrospective
- **Mode B update-run time (one file changed in existing module):** ≤10 minutes (reads committed draft; patches affected sections only; developer confirms) - baseline established in Phase 2 retrospective
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
| **Hosted MCP context unavailable** | 🟡 Medium | Pre-pilot Test 2 validates availability | Primary: Use `.github/copilot-instructions.md` with condensed charter within the 2,500-token budget. Secondary (long-term): migrate to dynamic `@skill.resource` hydration via custom `SkillsProvider`; tracked in `SKILL-COMPAT.md` Future Enhancement Paths |
| **Coding agent fails acceptance criteria** | 🟡 Medium | Phase 2.5 binary test with fallback | Phase 3 custom agent authorized only for documented failure modes |
| **Premium request overage** | 🟡 Medium | Model cost in Phase 0; establish budget baseline | Set billing alerts; monthly review with management |
| **Legal/compliance blocks AI processing** | 🔴 High | Pre-pilot Test 5 (legal sign-off) | Manual documentation with templates only; no AI generation |
| **Cross-platform validator failures** | 🟠 Low | Test Ubuntu + macOS + Windows in Phase 1 | Fix platform-specific file path or YAML parsing issues |
| **Copilot (GPT-4o) skill non-invocation** | 🟡 Medium | `disable-model-invocation: true` frontmatter; interactive runs use explicit `/akr-docs` commands, coding-agent runs use issue-template Mode B instructions; CI metadata header check enforces completion | Document in `SKILL-COMPAT.md`; treat as known limitation, not blocker |
| **SSG generation time exceeds developer patience on large modules** | 🟡 Medium | Per-pass timing targets in Part 18.2; slow-generation fallback at 45-minute threshold; coding agent background execution eliminates active wait time | Module splitting into sub-modules (<=8 files each); single-pass fallback for remaining sections with additional `❓` markers expected |
| **Duplicate Mode A review artifacts create reassignment churn** | 🟡 Medium | Review groupings directly in `modules.yaml` and keep committed drafts only for Mode B; incremental update path eliminates full re-generation cost for ongoing changes | Metric: reassignment count per Mode A PR should trend to 0 after first two pilots |
| **Stale committed draft misleads incremental update agent** | 🟡 Medium | `last_reviewed_at` in modules.yaml + v1.1 `--check-sync` WARNING when draft older than most recent file change | v1.0 mitigation: committed drafts older than most recent code change are advisory; v1.1 automates detection |

### Deferred Risks (Post-Pilot)

- **Standards version drift across teams:** Mitigated by `minimum_standards_version` validation
- **Business capability tag collision across repos:** Mitigated by centralized `tag-registry.json` + distribution workflow
- **Phase 4 repository permission issues:** Mitigated by sparse checkout + PAT with minimal scopes
- **SSG pass timing data insufficient to guide AI tooling decisions:** Addressed in Phase 2 retrospective metrics; mitigated by `ssg-slow-module-events` monitoring even when per-pass timing is unavailable on a surface

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

Agent Skill Mode C — Interactive HITL completion for existing
drafts with unresolved ❓ markers (replaces /docs.interview)
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
| **In-process script execution (Phase 3, conditional)** | Agent Framework `@skill.script` (Python SDK) | Included with `agent-framework` package; zero additional infra cost |
| **v2.0 target architecture (Phase 3+ conditional on Phase 2.6 verdict)** | AKR Python skill package (`akr.module_boundary`, `akr.module_doc_generation`, `akr.validation_skill`, `akr.consolidation_skill`) with `@skill.script` + `@skill.resource` + `require_script_approval=True` | `agent-framework` package - requires SDK verification before implementation |
| **Generation strategy** | Section-Scoped Generation (SSG) - structured Mode B pass sequence with forward payload discipline | Zero cost - encoded in SKILL.md; no new infrastructure |

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
4. [Phase 2.5: Coding Agent Spike](PHASE_2_5_CODING_AGENT_SPIKE.md) — Binary test with acceptance criteria
5. [Phase 2.6: Governance Stability Assessment](PHASE_2_6_GOVERNANCE_STABILITY.md) — Mandatory stability verdict after Phase 2.5
6. [Phase 3: Automation Extension](PHASE_3_AUTOMATION_EXTENSION.md) — Conditional custom agent or Copilot Studio
7. [Phase 4: Feature Consolidation](PHASE_4_FEATURE_CONSOLIDATION.md) — Cross-repository deterministic aggregation

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
- **Pre-pilot test results:** 6/6 pass or documented fallback
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

## Cross-Phase Owners Reference

| Role | Phase 0 | Phase 1 | Phase 2 | Phase 2.5 | Phase 3 (conditional) | Phase 4 |
|---|---|---|---|---|---|---|
| **Standards author** | Charter compression, SKILL.md (all 3 modes + frontmatter + self-reporting block + Mode B metadata header), schema, archive copy tasks, `evals/` directory + `benchmark.json` baseline, `SKILL-COMPAT.md` skeleton | `validate_documentation.py` (with metadata header check), templates, CI workflow, `copilot-instructions.md` rewrite, HITL alignment, hooks (`postToolUse` + `agentStop`), `SKILL-COMPAT.md` v1.0 | Onboarding checklist updates, mid-pilot template iterations, `SKILL-COMPAT.md` v1.1 (pilot findings) | Test case execution (Criteria 9 & 10), results documentation, `benchmark.json` `coding-agent` key, `SKILL-COMPAT.md` failure mode classification | Custom agent authoring (if authorized), `evals/copilot-studio/eval-set.xlsx`, `benchmark.json` custom-agent key | `consolidate.py`, feature registry, Phase 4 skill re-evaluation |
| **Standards lead** | Exit gate sign-off, cost model approval, legal coordination | Exit gate sign-off | Retrospective facilitation, Phase 2.5 authorization | go/no-go recommendation approval | Phase 3 scope authorization | Exit gate sign-off |
| **Infrastructure lead** | Secrets audit (`akr-mcp-server`), CI workflow validation | Cross-platform testing (Ubuntu/macOS/Windows) | CI deployment to pilot repos | Billing dashboard monitoring | Azure Function deployment (if authorized) | PAT setup, cross-repo Actions permissions |
| **Pilot developer** | Pre-pilot Test 1 validation (code analysis) | CourseDomain acceptance test, Visual Studio testing | Mode A/B validation, independent module docs, retrospective input | Spike test case participation | — | `businessCapability` tag audit |
| **Management** | Budget approval (P.3) | — | — | go/no-go decision | Phase 3 scope approval | — |
| **Legal/security** | Pre-pilot Test 5 sign-off | — | — | — | — | — |
| **Product owner** | — | — | Stakeholder briefing | — | Copilot Studio approval routing (if licensed) | Feature doc narrative refinement |

> **Exit gate standard:** Each phase exit gate requires the standards lead to document authorization **in writing** (GitHub comment, email, or approval record) before the next phase begins. Verbal sign-off is not sufficient.

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
