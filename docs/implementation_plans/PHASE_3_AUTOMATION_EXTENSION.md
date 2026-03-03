# Phase 3: Automation Extension — Implementation Plan

**Duration:** 2-4 weeks (if authorized)  
**Team:** Standards team (1 FTE) + infrastructure (0.5 FTE if Azure deployment needed)  
**Prerequisite:** Phase 2.5 result is FAIL with documented failure modes  
**Status:** 🟡 **CONDITIONAL** — Only authorized if Phase 2.5 documents specific shortcomings

---

## ⚠️ Important: Phase 3 Authorization Criteria

**Phase 3 is NOT authorized unless:**

1. Phase 2.5 executed and resulted in **FAIL**
2. Specific acceptance criteria failures documented with evidence
3. Failure modes are **technical** (not process or training issues)
4. Custom automation is the **only** viable solution (not workarounds)
5. Management approves cost/benefit of custom infrastructure

**If Phase 2.5 result is PASS:** This phase is **skipped entirely**. Proceed directly to Phase 4.

---

## Overview

Phase 3 builds targeted automation **only for documented Phase 2.5 failure modes**. This is not a general-purpose documentation generator—it is a surgical fix for specific shortcomings of the GitHub Copilot coding agent. All governance logic remains in Agent Skills, templates, and `validate_documentation.py`.

**Design Constraints:**
- **350-line review gate; 500-line hard ceiling** (CI-enforced)
- No logic duplication from Agent Skills or validators
- Uses Agent Skills for workflow; adds only missing functionality
- Decomposed: explore Copilot Marketplace extensions before building
- Evaluate GitHub Actions + coding agent composition before Azure Functions

---

## Decision Tree: What to Build

### Path A: Copilot Studio Doc Review Agent (M365 Licensing Available)

**Trigger:** M365 Copilot licenses confirmed; credit budget approved  
**Scope:** Cross-functional review automation for non-developer stakeholders  
**Audience:** Product Owner, QA Lead, Security Reviewer  
**Workflow:** PR label `docs-review-required` → Teams notification → approval gate

### Path B: Custom @doc-agent (Phase 2.5 Technical Failures)

**Trigger:** Coding agent fails specific acceptance criteria; no Marketplace equivalent  
**Scope:** Address **only** documented failure modes from Phase 2.5  
**Audience:** Developers (same as coding agent)  
**Workflow:** Issue assignment → targeted automation → draft PR

### Path C: No Custom Automation (Re-evaluation)

**Trigger:** Re-analysis shows workarounds or process changes sufficient  
**Scope:** Document workarounds; update Agent Skills or templates; skip automation  
**Audience:** N/A  
**Workflow:** N/A

---

## Deliverable 1: Phase 2.5 Failure Analysis

### Objective

Deeply analyze Phase 2.5 failures to determine root cause and whether custom automation is justified.

### Analysis Framework

For each failed acceptance criterion:

| Question | Answer Determines |
|---|---|
| **Is this a technical limitation or user error?** | Technical → automation candidate; User error → training/docs |
| **Can Agent Skills be refined to address it?** | Yes → update skills; No → automation candidate |
| **Is workaround acceptable?** | Yes → document workaround; No → automation candidate |
| **Does Copilot Marketplace have an extension?** | Yes → evaluate extension; No → build custom |
| **Is cost/benefit favorable?** | Yes → authorize build; No → accept limitation |

### Example Failure Mode Analysis

**Failure:** "Operations Map only 60% complete — coding agent missed private methods"

| Analysis Step | Conclusion |
|---|---|
| Technical or user error? | Technical — coding agent filters by public visibility heuristic |
| Can Agent Skills fix it? | No — coding agent's code analysis is upstream of skills |
| Is workaround acceptable? | No — incomplete Operations Map blocks production compliance |
| Marketplace extension available? | No — no AKR-specific extensions exist |
| Cost/benefit favorable? | Build deterministic AST-based extractor (150 lines); reuse from `akr-mcp-server` |
| **Decision** | **Authorize custom extractor module** |

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Analyze each Phase 2.5 failure | Standards author | Root cause documented per failure | 4 hours |
| Survey Copilot Marketplace | Standards author | Extensions evaluated; none match AKR needs (or alternatives identified) | 2 hours |
| Evaluate GitHub Actions + coding agent composition | Standards author | Can orchestration solve failures without new code? | 2 hours |
| Cost/benefit per failure mode | Standards author | Build vs. workaround analysis | 2 hours |
| Document authorization decision | Standards lead | Specific failures authorized for Phase 3; specific failures deferred | 1 hour |

---

## Deliverable 2A: Copilot Studio Doc Review Agent (If M365 Licenses Available)

### Objective

Build Copilot Studio agent in Microsoft Teams for cross-functional documentation review by non-developer stakeholders.

### Prerequisites

✅ M365 Copilot licenses confirmed  
✅ Credit model approved (modeled in Phase 0)  
✅ Teams integration permissions granted  

### Workflow

```
Developer opens PR with docs changes
   ↓
Developer applies label: docs-review-required
   ↓
GitHub webhook triggers Copilot Studio agent
   ↓
Agent posts PR summary to designated Teams channel
   ↓
Agent @mentions: Product Owner + QA Lead + Security Reviewer
   ↓
Each stakeholder reviews in Teams and approves/rejects
   ↓
All approvals received → Agent approves PR via GitHub API
   ↓
PR merge unblocked
```

### Agent Capabilities

- **Summarize PR:** Extract doc changes; generate plain-language summary
- **Route to roles:** Match doc type to reviewer roles (from `humanInput.defaultRole`)
- **Collect approvals:** Track who approved; require all before merging
- **Log compliance:** Record approval chain per PR

### Implementation

| Component | Technology | Estimated Lines |
|---|---|---|
| **Copilot Studio agent** | Power Platform | No-code / low-code |
| **GitHub webhook handler** | Azure Function (HTTP trigger) | ~100 lines |
| **Teams adaptive card** | JSON template | ~50 lines |
| **Approval tracking** | Azure Table Storage | ~50 lines |
| **GitHub API integration** | Octokit.js | ~50 lines |

**Total custom code:** ~250 lines (within 350-line review gate)

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Create Copilot Studio agent | Infrastructure | Agent deployed; responds in Teams | 1 week |
| Build GitHub webhook handler | Infrastructure | Parses PR payload; posts to Teams | 2 days |
| Design adaptive card template | Infrastructure | Summary readable; approve/reject buttons functional | 1 day |
| Implement approval tracking | Infrastructure | Tracks all required approvals; triggers GitHub API | 1 day |
| Test end-to-end workflow | Standards author + pilot team | Label applied → approvals collected → PR unblocked | 1 day |
| Document admin setup | Infrastructure | README for deploying to new Teams channels | 1 day |

### Cost Model

- **M365 Copilot premium requests:** Model in Phase 0 (X requests per PR)
- **Azure Function hosting:** Azure Functions Consumption Plan (~$0.20/million executions)
- **Azure Table Storage:** Negligible (<$1/month for pilot scale)

---

## Deliverable 2B: Custom @doc-agent (If Phase 2.5 Technical Failures)

### Objective

Build minimal custom agent addressing **only** documented Phase 2.5 failure modes.

### Scope Determination (Based on Phase 2.5 Results)

**Example scopes (hypothetical — actual scope TBD by Phase 2.5):**

#### Scope Example 1: Deterministic Operation Extractor

**Failure mode:** "Operations Map only 60% complete"  
**Root cause:** Coding agent misses private methods, async operations, or nested classes  
**Solution:** Reuse AST-based `CodeAnalyzer` from `akr-mcp-server`  
**Lines:** ~150 lines (ported + minimal wrapper)

#### Scope Example 2: Chunked Context Processor

**Failure mode:** "Large modules (8 files) truncate sections"  
**Root cause:** Context window ceiling at ~25,000 tokens  
**Solution:** Multi-pass processing: (1) extract structure, (2) generate per-section, (3) assemble  
**Lines:** ~200 lines (chunking logic + coordination)

#### Scope Example 3: Template-to-Module Mapper

**Failure mode:** "Template selection incorrect for microservices"  
**Root cause:** Coding agent heuristic fails on lightweight service pattern  
**Solution:** Deterministic `project_type` detection based on file structure  
**Lines:** ~100 lines (pattern matching + file tree analysis)

### Design Constraints

| Constraint | Enforcement |
|---|---|
| **Line count:** ≤500 lines total | CI check fails build if exceeded |
| **No Agent Skill duplication** | Agent uses Agent Skills for workflow; adds only missing functionality |
| **No validator duplication** | Agent calls `validate_documentation.py`; does not re-implement checks |
| **No template duplication** | Agent loads templates from `core-akr-templates`; does not embed them |
| **Minimal dependencies** | Python stdlib + `pyyaml` + GitHub API only; no ML frameworks. **If Path B (Azure Function):** May include `flask`/`fastapi` for HTTP trigger |

### Implementation Pattern

```python
"""
Custom @doc-agent — Minimal automation for Phase 2.5 failure modes
Design: Supplement coding agent with deterministic extraction; use Agent Skills for governance
"""

# ── Failure Mode 1: Deterministic Operation Extraction (if authorized) ──
class OperationExtractor:
    """Extracts ALL operations (public + private + async) using AST parsing"""
    def extract_operations(self, file_paths: list) -> dict:
        # Reuse CodeAnalyzer from akr-mcp-server/src/tools/
        pass  # ~150 lines

# ── Failure Mode 2: Chunked Context Processing (if authorized) ──
class ChunkedDocGenerator:
    """Multi-pass doc generation for large modules (>6 files or >15,000 tokens)"""
    def generate_chunked(self, module: dict) -> str:
        # Pass 1: Extract structure (files, operations, data ops)
        # Pass 2: Generate per-section with bounded context
        # Pass 3: Assemble with full-module references
        pass  # ~200 lines

# ── Failure Mode 3: Project Type Detection (if authorized) ──
class ProjectTypeDetector:
    """Deterministic project_type assignment based on file structure patterns"""
    def detect_type(self, file_tree: dict) -> str:
        # Pattern match: Controller + Service + Repository → api-backend
        #                Page + Components + Hooks → ui-component
        #                Service-to-service calls, no controllers → microservice
        pass  # ~100 lines

# ── GitHub Issue Webhook Handler ──
@app.route('/webhook/issue', methods=['POST'])
def handle_issue_assignment():
    """Invoked when issue assigned to @doc-agent"""
    issue_data = request.json
    
    # Determine which failure mode this issue needs
    if requires_operation_extraction(issue_data):
        extractor = OperationExtractor()
        operations = extractor.extract_operations(...)
        # Invoke coding agent with pre-extracted operations as context
    
    elif requires_chunked_processing(issue_data):
        generator = ChunkedDocGenerator()
        doc = generator.generate_chunked(...)
        # Open PR directly (coding agent bypassed for this case)
    
    # ... etc. for other failure modes
    
    return {'status': 'processing'}
```

### Line Count Enforcement (CI Check)

```yaml
# .github/workflows/line-count-check.yml
name: Enforce Line Count Ceiling

on:
  pull_request:
    paths:
      - 'src/**'

jobs:
  check-lines:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Count lines (exclude comments and blank lines)
        id: count
        run: |
          LINES=$(find src -name '*.py' -exec cat {} + | grep -v '^\s*#' | grep -v '^\s*$' | wc -l)
          echo "lines=$LINES" >> $GITHUB_OUTPUT
      
      - name: Enforce 500-line ceiling
        run: |
          if [ ${{ steps.count.outputs.lines }} -gt 500 ]; then
            echo "❌ Line count ceiling exceeded: ${{ steps.count.outputs.lines }} / 500"
            echo "Custom agent must remain under 500 lines. Refactor or decompose."
            exit 1
          else
            echo "✅ Line count OK: ${{ steps.count.outputs.lines }} / 500"
          fi
```

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Port `CodeAnalyzer` (if authorized) | Standards author | Extracts operations from Python/C#/TS files | 2 days |
| Build chunked processor (if authorized) | Standards author | Handles 8-file modules without truncation | 3 days |
| Build project type detector (if authorized) | Standards author | Correctly assigns api-backend / ui-component / microservice | 1 day |
| Implement webhook handler | Infrastructure | Receives GitHub issue assignments; routes to failure mode handlers | 1 day |
| Write unit tests | Standards author | ≥85% coverage; tests per authorized failure mode | 2 days |
| Deploy to Azure Functions (if needed) | Infrastructure | Webhook endpoint live; handles GitHub events | 1 day |
| Test end-to-end | Standards author + pilot team | Issue assigned → agent acts → PR opened | 1 day |
| Document usage | Standards author | README explains when to use @doc-agent vs. coding agent | 1 day |

### Deployment Options

| Option | Pros | Cons | Est. Cost |
|---|---|---|---|
| **Azure Functions** | Serverless; pay-per-use; auto-scale | Requires Azure subscription; cold start latency | ~$5-10/month pilot scale |
| **GitHub Actions** | No external hosting; native CI/CD | Consumes Actions minutes; no persistent state | Free tier sufficient for pilot |
| **Fly.io / Render** | Simple deployment; free tier | External dependency; less enterprise-friendly | Free tier for pilot |

**Recommended:** Azure Functions if infrastructure team available; GitHub Actions otherwise.

---

## Deliverable 3: Testing and Validation

### Objective

Validate that custom automation addresses Phase 2.5 failure modes without introducing new issues.

### Test Matrix

| Test | What to Validate | Pass Criteria |
|---|---|---|
| **Regression:** Test Cases 1-3 from Phase 2.5 | Custom agent PASSES where coding agent FAILED | 3/3 test cases now PASS all acceptance criteria |
| **Line count:** CI enforces 500-line ceiling | Build fails if line count exceeded | CI check passes; line count ≤500 |
| **Agent Skills integration:** Custom agent calls skills | Workflow logic not duplicated | Agent invokes Agent Skills; does not re-implement |
| **Validator integration:** Custom agent calls validator | Validation logic not duplicated | Agent runs `validate_documentation.py`; does not re-check |
| **Template integration:** Custom agent loads templates | Templates not embedded in agent code | Agent reads from `core-akr-templates`; no hardcoded templates |

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Re-run Phase 2.5 Test Cases 1-3 | Developer | Custom agent passes where coding agent failed | 2 hours |
| CI line count check | Standards author | Workflow enforces 500-line ceiling | 1 hour |
| Integration test: Agent Skills | Standards author | Agent invokes skills; no duplication detected | 1 hour |
| Integration test: Validator | Standards author | Agent calls `validate_documentation.py` correctly | 1 hour |
| Integration test: Templates | Standards author | Agent loads templates from repo; no embedded content | 1 hour |
| Document test results | Standards author | Report: all tests passed; agent meets constraints | 2 hours |

---

## Deliverable 4: Documentation and Handoff

### Objective

Document custom agent design, deployment, and maintenance for long-term ownership.

### Documentation Artifacts

| Document | Content | Audience |
|---|---|---|
| **ARCHITECTURE.md** | Design rationale; failure modes addressed; integration points | Future maintainers |
| **DEPLOYMENT.md** | Azure Functions setup; webhook configuration; secrets management | Infrastructure team |
| **USAGE.md** | When to use @doc-agent vs. coding agent; issue template | Developers |
| **MAINTENANCE.md** | Line count enforcement; how to add new failure modes; testing | Standards team |

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Write ARCHITECTURE.md | Standards author | Design decisions documented with rationale | 2 hours |
| Write DEPLOYMENT.md | Infrastructure | Step-by-step deployment instructions | 2 hours |
| Write USAGE.md | Standards author | Clear guidance on agent vs. coding agent | 1 hour |
| Write MAINTENANCE.md | Standards author | Maintenance procedures documented | 1 hour |
| Conduct handoff meeting | Standards lead | Infrastructure and standards teams trained | 1 hour |

---

## Phase 3 Retrospective

### Retrospective Agenda

1. **Was Phase 3 necessary?** In hindsight, could Phase 2.5 failures have been addressed without custom automation?
2. **Line count ceiling:** Was 500 lines sufficient? Did we stay under?
3. **Integration complexity:** How difficult was integrating with Agent Skills and validators?
4. **Cost:** Actual hosting cost vs. estimated; worth it compared to manual workarounds?
5. **Phase 4 readiness:** Is governance layer stable enough for cross-repo consolidation?

### Retrospective Outputs

- **Phase 3 completion metrics:** Actual vs. estimated time and cost
- **Custom agent effectiveness:** Did it solve documented failure modes?
- **Lessons learned:** Would we authorize Phase 3 again given current knowledge?
- **Phase 4 authorization:** Standards lead sign-off to proceed

---

## Risk Register (Phase 3 Specific)

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| Line count ceiling forces incomplete solution | 🟡 Medium | 🟠 Low | 500 lines chosen to force decomposition; expand only with justification |
| Custom agent becomes maintenance burden | 🔴 High | 🟡 Medium | Minimize complexity; document thoroughly; consider sunsetting if coding agent improves |
| Azure Function cold starts cause delays | 🟠 Low | 🟡 Medium | Use Azure Functions Premium Plan if latency critical |
| Custom agent diverges from Agent Skills | 🔴 High | 🟡 Medium | CI checks enforce no logic duplication; integration tests validate |

---

## Success Criteria Summary

Phase 3 succeeds when:

✅ Phase 2.5 failure analysis complete; specific failure modes authorized  
✅ Copilot Marketplace surveyed; no alternatives found (or alternatives evaluated and insufficient)  
✅ Custom automation built addressing **only** authorized failure modes  
✅ Line count ≤500 lines (CI-enforced)  
✅ Regression tests: Phase 2.5 Test Cases 1-3 now PASS  
✅ Integration tests: Agent Skills, validator, templates all called correctly  
✅ Documentation complete: ARCHITECTURE, DEPLOYMENT, USAGE, MAINTENANCE  
✅ Phase 3 retrospective complete; Phase 4 authorized  

**Exit gate:** Custom automation deployed and validated; Phase 4 work authorized by standards lead.

---

**Next Phase:** [Phase 4: Feature Consolidation](PHASE_4_FEATURE_CONSOLIDATION.md)

**Related Documents:**
- [Phase 2.5: Coding Agent Spike](PHASE_2.5_CODING_AGENT_SPIKE.md) — Authorization criteria
- [Implementation Plan Overview](IMPLEMENTATION_PLAN_OVERVIEW.md)
- [Implementation-Ready Analysis](../akr_implementation_ready_analysis.md) — Part 10, Part 13
