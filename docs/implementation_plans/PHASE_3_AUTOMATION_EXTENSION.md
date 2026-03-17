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

**Decision deadline after Phase 2.5 FAIL:** Path selection (A, B, or C) must be documented within 2 weeks of the published Phase 2.5 retrospective. If no path is selected within that window, default to Path C (no custom automation) with written rationale by standards lead.

---

> **📖 Agent Skills SDK Update (March 2026):** The Microsoft Agent Framework Python SDK now supports
> code-defined skills (`@skill.script` decorator) that run **in-process** with zero external hosting.
> This directly impacts the Phase 3 Path B deployment decision. See the updated
> **Deployment Options** table in Deliverable 2B and the new **Deployment Option D** below before
> committing to Azure Functions or GitHub Actions.

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
| Import `evals/copilot-studio/eval-set.xlsx` into Agent Evaluation | Standards author | Test set imported into Agent Evaluation (public preview) before deployment; test cases cover: document completeness summary, section presence check, reviewer routing logic; at least 10 test cases with expected outputs defined | 1 day |

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

#### Scope Example 2: Reclassified (SSG Adoption)

Context overflow chunking (formerly Scope Example 2) is now handled by SSG in SKILL.md. SSG's Pass 2 split (2A + 2B) is the production solution for large-module context management. This path no longer authorizes Phase 3.

Phase 3 authorization on Operations Map grounds requires evidence of an AST comprehension failure - the model produces an incomplete Operations Map even when the SSG pass executes correctly and context is not overflowing. This is a model-level failure to extract private/async/internal methods from correct method signatures, not a context overflow. This failure is addressed by Scope Example 1's deterministic AST extractor (unchanged).

Evidence required to distinguish the two: Operations Map completeness must be measured with and without SSG. If SSG Pass 2 split produces the same incompleteness as single-pass, the failure is AST comprehension. If SSG Pass 2 split resolves the incompleteness, the failure was context overflow and Phase 3 is not needed.

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
| **Minimal dependencies** | Python stdlib + `pyyaml` + GitHub API only; no ML frameworks. **If code-defined scripts (`@skill.script`):** `agent-framework` Python package required. **If Azure Function:** May include `flask`/`fastapi` for HTTP trigger |
| **Prefer in-process scripts** | Evaluate `@skill.script` code-defined scripts before committing to external hosting; see Deployment Options |

### Implementation Pattern

**Option A — Code-Defined Scripts via `@skill.script` (Preferred; evaluate first)**

**Compatibility constraints (required):**
- Code-defined skills via `@skill.script` are currently available in the **Python SDK path only**.
- Pin the SDK dependency during implementation and pilot, then re-validate on upgrades.
  - Recommended baseline: `agent-framework>=X.Y.Z,<X+1.0.0` (replace `X.Y.Z` with the current tested release at implementation start)
- If implementation stack is TypeScript/Node-only, Option A is not available; use Option B/C.

```python
"""
Custom @doc-agent — Failure mode handlers as code-defined Agent Skills
Design: Register each failure mode handler as an @skill.script; agent calls run_skill_script.
No external hosting required — scripts run in-process.
"""

from agent_framework import Skill, SkillsProvider

doc_agent_skill = Skill(
  name="akr-doc-agent",
  description="Handles AKR documentation failure modes not addressed by the coding agent.",
  content="Use this skill for deterministic extraction and chunked processing tasks.",
)

# ── Failure Mode 1: Deterministic Operation Extraction (if authorized) ──
@doc_agent_skill.script(
  name="extract-operations",
  description="Extracts ALL operations (public + private + async) via AST parsing."
)
def extract_operations(file_paths: str) -> str:
  """Run AST-based operation extraction; returns JSON list of operations."""
  import ast, json
  # Reuse CodeAnalyzer logic from akr-mcp-server/src/tools/
  # ~150 lines
  return json.dumps({"operations": []})  # placeholder

# ── Failure Mode 2: Chunked Context Processing (if authorized) ──
# WARNING - SSG RECLASSIFICATION NOTE:
# Context overflow chunking is handled by SSG Pass 2 split in SKILL.md
# (Scope Example 2 reclassified). This script is retained as a placeholder only if:
#   (a) Phase 2.5 shows SSG Pass 2 split executed correctly but the model still
#       cannot assemble coherent output from forward payloads, or
#   (b) The active execution surface cannot reliably support multi-turn flow.
# Authorization requires explicit Phase 2.5 FAIL evidence with SSG split confirmed.
# Do NOT build this script based on context overflow alone.
@doc_agent_skill.script(
  name="generate-chunked",
  description="Multi-pass doc generation for large modules (>6 files or >15,000 tokens)."
)
def generate_chunked(module_path: str, output_path: str) -> str:
  """Pass 1: extract structure. Pass 2: generate per-section. Pass 3: assemble."""
  # ~200 lines
  return '{"status": "assembled"}'  # placeholder

# ── Failure Mode 3: Project Type Detection (if authorized) ──
@doc_agent_skill.script(
  name="detect-project-type",
  description="Deterministic project_type assignment: api-backend / ui-component / microservice."
)
def detect_project_type(file_tree_json: str) -> str:
  """Pattern-match file tree to project type."""
  import json
  # Controller + Service + Repository → api-backend
  # Page + Components + Hooks → ui-component
  # Service-to-service calls, no controllers → microservice
  # ~100 lines
  return json.dumps({"project_type": "api-backend"})  # placeholder

skills_provider = SkillsProvider(
  skills=[doc_agent_skill],
  require_script_approval=True,   # See Script Approval section below
)
```

**Required custom-agent instruction extension (`SKILL.md` or equivalent):**

```markdown
When deterministic extraction or chunked assembly is required, call `run_skill_script` explicitly:

1. Operation extraction failure mode:
  - `run_skill_script("extract-operations", {"file_paths": "<space-separated paths>"})`
2. Large module/chunking failure mode (only if authorized per Scope Example 2 reclassification criteria):
  - `run_skill_script("generate-chunked", {"module_path": "<path>", "output_path": "<path>"})`
3. Project type ambiguity failure mode:
  - `run_skill_script("detect-project-type", {"file_tree_json": "<json>"})`

Do not assume scripts run automatically based only on registration.
```

**Option B — Webhook Handler (Azure Functions / GitHub Actions; fallback if in-process insufficient)**

```python
"""
Custom @doc-agent — Minimal automation for Phase 2.5 failure modes
Use this pattern only if code-defined @skill.script cannot handle the failure mode
(e.g., failure mode requires subprocess isolation or external system access).
"""

# ── GitHub Issue Webhook Handler ──
@app.route('/webhook/issue', methods=['POST'])
def handle_issue_assignment():
  """Invoked when issue assigned to @doc-agent"""
  issue_data = request.json

  if requires_operation_extraction(issue_data):
    extractor = OperationExtractor()
    operations = extractor.extract_operations(...)
    # Invoke coding agent with pre-extracted operations as context

  elif requires_chunked_processing(issue_data):
    generator = ChunkedDocGenerator()
    doc = generator.generate_chunked(...)
    # Open PR directly (coding agent bypassed for this case)

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
      - uses: actions/checkout@v4
      
      - name: Count lines (exclude comments and blank lines)
        id: count
        run: |
          python - << 'PY'
          import os

          total = 0
          for root, _, files in os.walk('src'):
            for name in files:
              if name.endswith(('.py', '.ts', '.js', '.cs')):
                path = os.path.join(root, name)
                with open(path, 'r', encoding='utf-8', errors='ignore') as handle:
                  for line in handle:
                    stripped = line.strip()
                    if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                      continue
                    total += 1

          with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
            output.write(f"lines={total}\n")
          PY
      
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

---

## Deliverable 2C: Skill Reliability in Custom Agent Context

### Objective

Ensure that any custom agent built in Phase 3 (Path A or Path B) preserves the three-layer reliability contract established in Phase 1.

### Requirements

These requirements apply to **all custom agents** built in Phase 3, regardless of path (Copilot Studio or custom `@doc-agent`):

| Requirement | How to Implement | Verification |
|---|---|---|
| **Metadata header in output** | Custom agent must include `<!-- akr-generated -->` block as final step of document generation — same as Mode B | CI `validate_documentation.py` check; any PR from the custom agent without the header fails CI |
| **Model compatibility note in agent instructions** | Custom agent instructions must note: "This agent calls Agent Skill `akr-docs`. Output quality depends on the underlying model. Refer to `SKILL-COMPAT.md` for known failure modes." | Code review of agent instructions |
| **`SKILL-COMPAT.md` updated for custom agent** | After Phase 3 deployment, add a `custom-agent` row to `SKILL-COMPAT.md` with observed pass rates | Standards author post-deployment review |
| **`benchmark.json` `custom-agent` key** | Record custom agent pass rates in `benchmark.json` alongside `coding-agent` from Phase 2.5 | Same benchmark format as Phase 2.5 |

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Embed `<!-- akr-generated -->` header requirement in custom agent instructions | Standards author | Agent instructions include final step writing metadata header; same fields as Mode B definition | 30 min |
| Add CI assertion: custom agent PRs must contain metadata header | Standards author | `validate_documentation.py` already enforces this; confirm no exemption was added for custom agent PRs | 15 min |
| Add `custom-agent` row to `SKILL-COMPAT.md` post-deployment | Standards author | Row populated with observed pass rate after first 5 real-world runs | 1 hour |
| Populate `benchmark.json` `custom-agent` key | Standards author | Pass rates and average token counts recorded for at least 3 test cases | 1 hour |

---

### Deployment Options

| Option | Pros | Cons | Est. Cost |
|---|---|---|---|
| **D — Code-defined `@skill.script`** ⭐ | No external hosting; in-process; no cold starts; no infra; maps directly to Agent Skills `run_skill_script` tool | Scripts share agent process permissions; requires `agent-framework` Python package; not suitable if subprocess isolation is required | **Zero** (no infra) |
| **A — Azure Functions** | Serverless; pay-per-use; auto-scale | Requires Azure subscription; cold start latency | ~$5-10/month pilot scale |
| **B — GitHub Actions** | No external hosting; native CI/CD | Consumes Actions minutes; no persistent state | Free tier sufficient for pilot |
| **C — Fly.io / Render** | Simple deployment; free tier | External dependency; less enterprise-friendly | Free tier for pilot |

**Evaluation order (required):** Evaluate **Option D first**. Only proceed to Azure Functions (Option A) if the failure mode requires subprocess isolation, external network access, or is incompatible with in-process execution.

**Decision gate:** Standards author must document in writing why Option D is insufficient before Option A is authorized. This decision is recorded in `ARCHITECTURE.md` (Deliverable 4).

---

## Deliverable 2D: Script Approval Configuration

### Objective

Wire the `require_script_approval` flag from the Microsoft Agent Framework Python SDK into the AKR
compliance mode model so script execution in the custom `@doc-agent` is gated by human approval
in production environments, consistent with the HITL contract established in Phases 0-2.

### Background

The Agent Framework `SkillsProvider` now supports `require_script_approval=True`, which pauses
script execution and returns an approval request to the calling application before any side effects
occur. This maps directly onto the AKR compliance mode progression:

| AKR `compliance_mode` | `require_script_approval` | Rationale |
|---|---|---|
| `pilot` | `False` (default) | Fast iteration; PR-level review is sufficient HITL gate |
| `production` | `True` | Script side effects (file writes, extractions) require explicit human sign-off before they occur |

### Implementation

**1. Use `script_approval_required` from the Phase 1 schema baseline:**

```json
{
  "compliance_mode": "production",
  "script_approval_required": true
}
```

**2. Wire field value to `SkillsProvider` in the custom agent:**

```python
from agent_framework import SkillsProvider
import json

with open('.akr-config.json') as f:
  akr_config = json.load(f)

skills_provider = SkillsProvider(
  skills=[doc_agent_skill],
  require_script_approval=akr_config.get("script_approval_required", False),
)
```

**3. Handle approval requests in the agent invocation loop:**

```python
result = await agent.run("Generate documentation for CourseDomain module", session=session)

while result.user_input_requests:
  for request in result.user_input_requests:
    script_name = request.function_call.name
    script_args = request.function_call.arguments

    # Log for audit trail
    print(f"[AKR APPROVAL REQUIRED] Script: {script_name}")
    print(f"  Args: {script_args}")

    # Present request to the host UI surface.
    # In Copilot-hosted contexts this may be surfaced by the platform, not terminal I/O.
    approved = get_approval_from_host_ui(script_name, script_args)

    approval_response = request.to_function_approval_response(approved=approved)
    result = await agent.run(approval_response, session=session)
```

### Audit Trail Requirement

When `script_approval_required: true`, the agent **must** log the following for each script
execution attempt:

- Script name
- Arguments passed
- Approved / rejected (with reviewer identity if available)
- ISO 8601 timestamp
- `alternative_approach_used` flag when a script is rejected and the agent continues via a non-script path

Log format (append to `.akr/logs/script-approvals.jsonl`):

```json
{"timestamp": "2026-03-16T10:00:00Z", "script": "extract-operations", "args": {"file_paths": "..."}, "approved": true, "reviewer": "developer@org.com", "alternative_approach_used": false}
```

**Implementation risk (must validate before production):** Approval UI/event wiring (`user_input_requests`
and response submission) is platform-dependent in VS Code Copilot Chat and may not behave like standalone
SDK sample loops. Confirm host behavior in Phase 0 Test 7 and again in a Phase 3 pre-production run.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Verify Phase 1 `script_approval_required` schema field exists in target repo | Standards author | Field present; type `boolean`; default `false`; schema version includes update | 15 min |
| Implement `SkillsProvider` wiring from `.akr-config.json` | Standards author | `require_script_approval` reads from config; not hardcoded | 1 hour |
| Implement approval loop in agent invocation | Standards author | Loop handles all `user_input_requests`; rejected scripts produce informational message; host UI integration point documented | 2 hours |
| Implement audit log writer | Standards author | `.akr/logs/script-approvals.jsonl` created; each approval/rejection appended | 1 hour |
| Test: pilot mode — no approval prompt | Developer | `compliance_mode: pilot` + `script_approval_required: false` → scripts run without prompt | 30 min |
| Test: production mode — approval required | Developer | `compliance_mode: production` + `script_approval_required: true` → prompt appears before script runs | 30 min |
| Test: rejection path | Developer | Rejected script → agent reports limitation and suggests alternative approach; log includes `alternative_approach_used` | 30 min |
| Document in `VALIDATION_GUIDE.md` | Standards author | Section added: "Script Approval in Production Mode" | 1 hour |

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
| **Script Approval: pilot mode** | `compliance_mode: pilot` → no approval prompt | Scripts run immediately without prompt |
| **Script Approval: production mode** | `compliance_mode: production` → approval prompt before script execution | Prompt shown; audit log entry written |
| **Script Approval: rejection behavior** | Rejected script request path | Agent either exits safely or uses fallback; audit log includes `alternative_approach_used` |

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
| `@skill.script` in-process permission scope too broad | 🟡 Medium | 🟠 Low | Review script function permissions; use `require_script_approval=True` in production; document accepted scope in `ARCHITECTURE.md` |
| `user_input_requests` approval UI surface behaves differently in Copilot-hosted sessions | 🔴 High | 🟡 Medium | Validate host UI behavior in Phase 0 Test 7 and Phase 3 pre-prod smoke test; if unsupported, keep `script_approval_required=false` and use PR review as HITL fallback |
| Agent Framework SDK API drift changes `@skill.script` contract | 🟡 Medium | 🟠 Low | Pin `agent-framework` version during rollout; require release-note review before upgrades |

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
✅ Deployment option evaluated in required order (D → A → B → C); rationale documented if D rejected
✅ `script_approval_required` flag from Phase 1 schema baseline is wired to `SkillsProvider`; pilot=false / production=true
✅ Token budget re-validated for Phase 3 path: condensed charter + SKILL instructions + code-skill tool definitions + source files remains within operational context limits for max-size module

**Exit gate:** Custom automation deployed and validated; Phase 4 work authorized by standards lead **in writing** (GitHub comment, email, or approval record) before Phase 4 begins.

---

**Next Phase:** [Phase 4: Feature Consolidation](PHASE_4_FEATURE_CONSOLIDATION.md)

**Related Documents:**
- [Phase 2.5: Coding Agent Spike](PHASE_2_5_CODING_AGENT_SPIKE.md) — Authorization criteria
- [Implementation Plan Overview](IMPLEMENTATION_PLAN_OVERVIEW.md)
- [Implementation-Ready Analysis](../akr_implementation_ready_analysis.md) — Part 10, Part 13
