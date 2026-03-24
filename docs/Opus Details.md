Let me search both repositories for the current state of the relevant files before generating precise copy-paste updates.Here are all the copy-paste-ready updates, organized by file. Each block is labeled with the exact file, and the line number or section heading it should be inserted at or appended after.

---

## FILE 1 — `AKR_Tracking.md`
**Repo:** `reyesmelvinr-emr/akr-mcp-server`

### UPDATE 1A — Add `Test 2A` row to the Pre-Pilot 7-Test Checklist table
**Location:** After line 72 (after the `Test 7` row) in `### Pre-Pilot 7-Test Checklist`

````markdown name=AKR_Tracking.md url=https://github.com/reyesmelvinr-emr/akr-mcp-server/blob/aca792bfb61e9f77ee420b90be1f3bfa52009eb0/AKR_Tracking.md#L72
| Test 2A | GitHub MCP Server charter access validation (VS Code) | PASS | Confirmed 2026-03-23: `@github get files with names like CHARTER.md` returns `.akr/charters/AKR_CHARTER_BACKEND.md` and compressed charters from `core-akr-templates/copilot-instructions/`; GitHub MCP extension installed and authenticated; no additional licensing required | Test 2A is a supplemental validation, not a replacement for Test 2; Test 2 (Hosted MCP Context Sources) remains FALLBACK and is preserved as-is; Test 2A adds on-demand pull access via `@github` tool; Visual Studio parity deferred to Phase 2 Deliverable 5 |
````

---

### UPDATE 1B — Add clarification note to Phase 0 `### Issues and Clarifications`
**Location:** Append after line 107 (after the last `2026-03-18:` entry, before `### Gate Decision`)

````markdown name=AKR_Tracking.md url=https://github.com/reyesmelvinr-emr/akr-mcp-server/blob/aca792bfb61e9f77ee420b90be1f3bfa52009eb0/AKR_Tracking.md#L107
- 2026-03-24: **Post-gate context clarification (Phase 0 closed — no reopen):** On 2026-03-23, `@github` tool access via the GitHub MCP Server extension was confirmed in VS Code for `core-akr-templates`. This is architecturally distinct from the Hosted MCP Context Sources tested in Test 2; Test 2 tested ambient auto-loading and remains FALLBACK. The GitHub MCP Server enables explicit on-demand `@github get file` calls with no additional licensing. A supplemental Test 2A row has been added to the checklist above to preserve this evidence without altering the Phase 0 gate record. Charter compression completed in Phase 0 remains the standard and required delivery mechanism; GitHub MCP changes delivery mechanics (pull vs. push) but does not replace the compressed charter artifacts. Downstream operational changes (SKILL.md Step 2 update, onboarding checklist addition, distribution bundle refinement) are recorded as Phase 2 issues below.
````

---

### UPDATE 1C — Add entries to Phase 2 `### Issues and Clarifications`
**Location:** Append after line 346 in the Phase 2 Issues and Clarifications section (after the last `2026-03-20:` entry and before `### Gate Decision`)

````markdown name=AKR_Tracking.md url=https://github.com/reyesmelvinr-emr/akr-mcp-server/blob/aca792bfb61e9f77ee420b90be1f3bfa52009eb0/AKR_Tracking.md#L346
- 2026-03-24: **GitHub MCP Server access confirmed — Phase 2 operational impact recorded.** On 2026-03-23, the GitHub MCP Server extension (`@github` command) was confirmed available in VS Code for `core-akr-templates`. Files accessible on demand via `@github get file reyesmelvinr-emr/core-akr-templates <path>` without Hosted MCP Context Sources configuration. This changes charter delivery mechanics but does not replace Phase 0 compressed charters; condensed charter files remain the authoritative reference and their headings are required to match SSG pass sequence references in SKILL.md. Evidence recorded as Test 2A in Phase 0 checklist (supplemental row).
- 2026-03-24: **SKILL.md Mode B Step 2 update required (Phase 2 task — not a Phase 0/1 reopen).** SKILL.md Mode B charter-loading step should be updated to: (1) prefer `@github` fetch of condensed charter in Pass 1 when GitHub MCP is available; (2) carry the full condensed charter in the forward payload from Pass 1; (3) prohibit re-fetching the charter or source files via `@github` in SSG Passes 2–7 (forward payload discipline). Update target: `core-akr-templates/.github/skills/akr-docs/SKILL.md`, Mode B Step 2 and SSG Pass 1 instructions. Condensed charter remains primary charter artifact; `copilot-instructions/` files remain the fetch targets. See GITHUB_MCP_CONTEXT_SOURCE_ASSESSMENT.md Section 4 for full revised instruction text. Distribute updated SKILL.md to registered repos via `distribute-skill.yml` after change.
- 2026-03-24: **Onboarding checklist gap — GitHub MCP verification step missing (Deliverable 1).** The Deliverable 1 onboarding checklist does not include a step to verify GitHub MCP Server availability and `@github` command functionality. This is now a required pre-Mode A onboarding check because SKILL.md will reference `@github` for charter loading. Add the following to Deliverable 1 tracking before marking checklist complete: (1) Install GitHub MCP extension in VS Code; (2) Run `@github get file reyesmelvinr-emr/core-akr-templates copilot-instructions/backend-service.instructions.md` in Copilot Chat and confirm file content is returned; (3) Document result in tracker. If `@github` is unavailable, document surface type and ensure `.github/copilot-instructions.md` in the app repo carries the condensed charter as fallback.
- 2026-03-24: **benchmark.json quota-planning update required — @github tool calls not yet tracked.** The current `benchmark.json` `quota-planning` block does not account for `@github` tool call consumption (2 calls per Mode B run: one for `modules.yaml` in Pass 1, one for the condensed charter in Pass 1). These tool calls consume premium requests alongside generation calls. The `github-mcp-calls-per-run` field should be added to each model's `premium-requests` block under the SSG key. Update target: `core-akr-templates/evals/benchmark.json`. Defer data population to Phase 2 Mode B runs; add field with `null` placeholder now so the schema is consistent before first run.
- 2026-03-24: **distribute-skill.yml distribution bundle — condensed charters now optional for distribution.** With `@github` access confirmed, condensed charter files (`copilot-instructions/` directory) no longer need to be distributed to each application repo as a primary delivery mechanism. They remain in `core-akr-templates` and are accessed on demand. However, distribution is still optional for teams that want offline/Visual Studio fallback access. No immediate change to `distribute-skill.yml` required for Phase 2 pilot (training-tracker-backend). Decision to remove charters from distribution bundle should be made during Phase 2 retrospective based on pilot feedback. Record this as an open option, not an immediate action.
- 2026-03-24: **Visual Studio `@github` availability — unconfirmed, Deliverable 5 scope updated.** The GitHub MCP Server is confirmed for VS Code only. Availability in Visual Studio (full IDE) is unconfirmed. Phase 2 Deliverable 5 scope is updated to include: (1) test whether `@github` command is available in Visual Studio Copilot Chat; (2) if unavailable, confirm `.github/copilot-instructions.md` fallback (with condensed charter) works as substitute; (3) document VS-specific charter loading procedure in tracker notes. This is a blocking item for confirming Mode B surface parity.
````

---

### UPDATE 1D — Add new Deliverable 1 task rows to the Phase 2 Deliverable Tracking table
**Location:** After the last `| Deliverable 1 - Onboarding |` row (after line ~259, before `| Deliverable 2 - Mode A |`)

````markdown name=AKR_Tracking.md url=https://github.com/reyesmelvinr-emr/akr-mcp-server/blob/aca792bfb61e9f77ee420b90be1f3bfa52009eb0/AKR_Tracking.md#L259
| Deliverable 1 - Onboarding | Verify GitHub MCP Server extension installed in VS Code and `@github` command returns files from core-akr-templates | Pilot dev | NOT_STARTED | Pending | TBD | Run: `@github get file reyesmelvinr-emr/core-akr-templates copilot-instructions/backend-service.instructions.md`; confirm content returned; document result; if unavailable, record surface type and activate `.github/copilot-instructions.md` fallback path |
| Deliverable 1 - Onboarding | Update SKILL.md Mode B Step 2 and SSG Pass 1 to use `@github` charter fetch (PATH A) with forward payload carry and `@github` prohibition after Pass 2 | Standards author | NOT_STARTED | Pending | TBD | Target file: `core-akr-templates/.github/skills/akr-docs/SKILL.md`; charter fetch in Pass 1 only; condensed charter carried in forward payload; no @github calls for source files in Passes 2–7; distribute updated SKILL.md via `distribute-skill.yml` after change |
| Deliverable 1 - Onboarding | Add `github-mcp-calls-per-run` null placeholder to benchmark.json `premium-requests` SSG block for each model | Standards author | NOT_STARTED | Pending | TBD | Target file: `core-akr-templates/evals/benchmark.json`; 2 calls per Mode B run (modules.yaml + condensed charter in Pass 1); populate with observed data during Phase 2 Mode B runs |
````

---

### UPDATE 1E — Add entry to the Change Log
**Location:** Append at the end of `## Change Log (Tracking File Updates)` (after the last line in the file, currently line 506)

````markdown name=AKR_Tracking.md url=https://github.com/reyesmelvinr-emr/akr-mcp-server/blob/aca792bfb61e9f77ee420b90be1f3bfa52009eb0/AKR_Tracking.md#L506
- 2026-03-24: Recorded GitHub MCP Server discovery impact: added Test 2A supplemental checklist row to Phase 0 (no gate reopen); added post-gate clarification note to Phase 0 Issues; added five Phase 2 operational impact entries (SKILL.md Step 2, onboarding checklist, benchmark.json schema, distribution bundle, Visual Studio gap); added three new Deliverable 1 task rows for GitHub MCP verification, SKILL.md charter loading update, and benchmark.json field addition. Source: GITHUB_MCP_CONTEXT_SOURCE_ASSESSMENT.md (2026-03-23).
````

---

## FILE 2 — `docs/implementation_plans/PHASE_2_PILOT_ONBOARDING.md`
**Repo:** `reyesmelvinr-emr/akr-mcp-server`

### UPDATE 2A — Update Deliverable 1 Onboarding Checklist
**Location:** Find the step `Configure hosted MCP context source or fallback .github/copilot-instructions.md` in `### Onboarding Checklist`. Replace it with:

````markdown name=PHASE_2_PILOT_ONBOARDING.md url=https://github.com/reyesmelvinr-emr/akr-mcp-server/blob/main/docs/implementation_plans/PHASE_2_PILOT_ONBOARDING.md
**Step: Verify GitHub MCP Server charter access (primary path)**
- Install GitHub MCP Server extension in VS Code if not already present
- Start MCP server via Command Palette: `MCP: List servers`
- In Copilot Chat, run: `@github get file reyesmelvinr-emr/core-akr-templates copilot-instructions/backend-service.instructions.md`
- Confirm file content is returned
- Record result in AKR_Tracking.md Phase 2 Deliverable 1 row
- Owner: Pilot dev | Time estimate: 15 min
- Acceptance criterion: File content returned and charter headings visible; `TEST2A_GITHUB_MCP_AVAILABLE=True` recorded in tracker

**Step: Configure .github/copilot-instructions.md (global rules only)**
- Ensure the file contains: invocation guidance (`/akr-docs mode-a/mode-b/mode-c`), self-reporting block reminder, model compatibility note, module grouping principles
- The file does NOT need to carry the condensed charter if `@github` access is confirmed above
- If `@github` is unavailable on this surface (e.g. Visual Studio), add condensed charter content as fallback
- Owner: Pilot dev | Time estimate: 20 min
- Acceptance criterion: File ≤150 lines; charter not duplicated if `@github` available
````

---

### UPDATE 2B — Update Deliverable 5 Visual Studio Testing scope
**Location:** In `### Deliverable 5: Visual Studio Testing`, update the test scope description block:

````markdown name=PHASE_2_PILOT_ONBOARDING.md url=https://github.com/reyesmelvinr-emr/akr-mcp-server/blob/main/docs/implementation_plans/PHASE_2_PILOT_ONBOARDING.md
**Updated Scope (2026-03-24):** In addition to testing Agent Skill Mode A/B operation in Visual Studio:
1. Test whether `@github` command is available in Visual Studio Copilot Chat
2. If available: confirm condensed charter can be fetched via `@github get file reyesmelvinr-emr/core-akr-templates copilot-instructions/backend-service.instructions.md`
3. If unavailable: confirm `.github/copilot-instructions.md` fallback (with condensed charter appended) provides charter guidance; document character count to confirm within ~4,000-char limit
4. Document VS-specific charter loading procedure in AKR_Tracking.md Phase 2 notes
5. Record `TEST_VS_GITHUB_MCP_AVAILABLE=True/False` in tracker
````

---

## FILE 3 — `docs/akr_implementation_ready_analysis.md`
**Repo:** `reyesmelvinr-emr/akr-mcp-server`

### UPDATE 3A — Add to Part 11: Pre-Pilot Validation Tests
**Location:** Find `### Test 2` (or the equivalent Pre-Pilot Test 2 entry) in `## Part 11`. Append after it:

````markdown name=akr_implementation_ready_analysis.md url=https://github.com/reyesmelvinr-emr/akr-mcp-server/blob/main/docs/akr_implementation_ready_analysis.md
**Test 2A: GitHub MCP Server Charter Access (Supplemental — Added 2026-03-24)**

| Item | Value |
|---|---|
| Status | PASS (confirmed 2026-03-23 in VS Code) |
| Mechanism | GitHub MCP Server extension (`@github` tool); distinct from Hosted MCP Context Sources tested in Test 2 |
| Test command | `@github get file reyesmelvinr-emr/core-akr-templates copilot-instructions/backend-service.instructions.md` |
| Scope | VS Code only; Visual Studio parity unconfirmed — test in Phase 2 Deliverable 5 |
| Relationship to Test 2 | Supplemental. Test 2 (Hosted MCP Context Sources = FALLBACK) is preserved. Test 2A validates on-demand pull access via `@github` tool. |
| Impact on charter compression | Charter compression artifacts remain required and are the fetch targets for `@github`. Compressed charter is ~10% of original — far more efficient than fetching 11,000-token full charter per pass. |
| Impact on SKILL.md | Mode B Step 2 should be updated to prefer `@github` charter fetch in Pass 1 (PATH A); carry full condensed charter in forward payload; prohibit `@github` calls for source files in Passes 2–7 (forward payload discipline). See Section 4 of GITHUB_MCP_CONTEXT_SOURCE_ASSESSMENT.md. |
````

---

### UPDATE 3B — Add to Part 18: SSG Architecture (Part 18.4 — Forward Payload Design)
**Location:** At the end of `## 18.4 Forward Payload Design`, append:

````markdown name=akr_implementation_ready_analysis.md url=https://github.com/reyesmelvinr-emr/akr-mcp-server/blob/main/docs/akr_implementation_ready_analysis.md
**18.4.1 @github Tool Call Discipline (Added 2026-03-24)**

With the GitHub MCP Server confirmed available in VS Code, `@github` tool calls are now a viable charter delivery mechanism. Forward payload discipline must be extended to govern tool call usage:

| Rule | Requirement |
|---|---|
| **Charter fetch** | One `@github` call in Pass 1 to fetch the condensed charter (e.g., `copilot-instructions/backend-service.instructions.md`). Full charter is carried in `charter_content` key of forward payload. |
| **modules.yaml fetch** | One `@github` call in Pass 1 to fetch the module entry from `modules.yaml`. |
| **Total @github calls per Mode B run** | 2 (Pass 1 only). No additional `@github` calls are authorized in Passes 2–7. |
| **Source file prohibition** | `@github` calls for source files listed in `modules[].files[]` are **PROHIBITED** after Pass 2. The forward payload from Pass 2 (operations table, architecture summary) is the only permitted source. Any re-fetch is a skill execution error requiring a retry. |
| **Charter prohibition after Pass 1** | No pass after Pass 1 may issue a `@github` call to reload the charter. Extract the relevant section from `charter_content` in the forward payload instead. |

**Premium request impact:** `@github` tool calls consume premium requests in addition to generation calls. The `benchmark.json` `premium-requests` SSG block must include a `github-mcp-calls-per-run: 2` field to ensure accurate per-module cost accounting in Phase 2. The `quota-planning` block should note that tool calls count toward the monthly premium quota alongside generation calls.
````

---

## FILE 4 — `core-akr-templates/.github/skills/akr-docs/SKILL.md`
**Repo:** `reyesmelvinr-emr/core-akr-templates`

### UPDATE 4A — Replace Mode B Step 2 (charter loading instruction)
**Location:** Find the Mode B Step 2 block (the step that loads the condensed charter). Replace the existing content of that step with:

````markdown name=SKILL.md url=https://github.com/reyesmelvinr-emr/core-akr-templates/blob/main/core-akr-templates/.github/skills/akr-docs/SKILL.md
**Step 2 — Load charter (Pass 1 only)**

Select the loading path based on surface availability:

**PATH A — GitHub MCP available (preferred, VS Code):**
Fetch the full condensed charter ONCE at Pass 1 start using the `@github` tool. Carry the result in the forward payload as `charter_content`. Do NOT issue additional `@github` charter calls in Passes 2–7.

Charter file by project_type:
- `api-backend`, `microservice`, `general`:
  `@github get file reyesmelvinr-emr/core-akr-templates copilot-instructions/backend-service.instructions.md`
- `ui-component`:
  `@github get file reyesmelvinr-emr/core-akr-templates copilot-instructions/ui-component.instructions.md`
- `database`:
  `@github get file reyesmelvinr-emr/core-akr-templates copilot-instructions/database.instructions.md`

Also fetch `modules.yaml` in Pass 1:
  `@github get file {current-workspace-repo} modules.yaml`

Total `@github` calls in Pass 1: **2** (charter + modules.yaml).
Total `@github` calls in Passes 2–7: **0**.

**PATH B — Fallback (GitHub MCP unavailable):**
Use the condensed charter present in the session context via `.github/copilot-instructions.md` (if the team has configured it there). If not available in session context, ask the developer to paste the relevant charter file content before proceeding.

**CRITICAL — @github source file prohibition (all passes):**
After Pass 2, `@github` calls for source files listed in `modules[].files[]` are PROHIBITED.
The forward payload from Pass 2 (operations table, architecture summary) is the only permitted source.
Any re-fetch of source files in Passes 3–7 is a skill execution error — stop, discard the pass output, and retry from the correct forward payload.

**Forward payload charter carry rule:**
In each SSG pass (Passes 2–7), extract only the section relevant to that pass from `charter_content` in the forward payload. Use the section heading that matches the pass (e.g., `## Operations Map Rules` in Pass 2, `## Architecture Diagram Rules` in Pass 3). Do not re-fetch the charter from `@github`.
````

---

## FILE 5 — `core-akr-templates/.github/skills/akr-docs/SKILL-COMPAT.md`
**Repo:** `reyesmelvinr-emr/core-akr-templates`

### UPDATE 5A — Add GitHub MCP failure mode to Model-Specific Failure Modes table
**Location:** In the `## Model-Specific Failure Modes` table (or equivalent section), append after the last GPT-4o row:

````markdown name=SKILL-COMPAT.md url=https://github.com/reyesmelvinr-emr/core-akr-templates/blob/main/core-akr-templates/.github/skills/akr-docs/SKILL-COMPAT.md
| GPT-4o | `@github` source file re-fetch in SSG Passes 3–7 | Model may drift toward issuing additional `@github get file` calls for source files already covered by the Pass 2 forward payload, violating forward payload discipline | Mitigation: SKILL.md Step 2 contains explicit prohibition; SKILL-COMPAT.md model note reminds the user to watch for `@github` calls in later passes; if observed, retry the failing pass without `@github` context | Medium |
| GPT-4o | Charter section mismatch in forward payload | If condensed charter heading in `charter_content` does not exactly match the heading referenced in a pass instruction, the pass may generate without the correct rules rather than failing visibly | Mitigation: Phase 0 condensed charter authoring must use canonical headings; heading names must be agreed in Phase 0 D1 and mirrored exactly in both SKILL.md pass sequence and charter files | Low |
````

---

### UPDATE 5B — Add a new surface availability note for GitHub MCP
**Location:** In the `## Surface Compatibility` or `## Invocation Surfaces` section, append:

````markdown name=SKILL-COMPAT.md url=https://github.com/reyesmelvinr-emr/core-akr-templates/blob/main/core-akr-templates/.github/skills/akr-docs/SKILL-COMPAT.md
| Surface | @github tool available | Charter loading path | Notes |
|---|---|---|---|
| VS Code Copilot Chat (agent mode) | ✅ CONFIRMED (2026-03-23) | PATH A: `@github get file` in Pass 1 | Primary workflow surface |
| Visual Studio 2022 Copilot Chat | ⚠️ UNCONFIRMED | PATH B: `.github/copilot-instructions.md` fallback assumed | Test in Phase 2 Deliverable 5 |
| Copilot CLI / coding agent | ⚠️ UNCONFIRMED | PATH B: issue template must carry charter context explicitly | Test in Phase 2.5 |
````

---

## FILE 6 — `core-akr-templates/evals/benchmark.json`
**Repo:** `reyesmelvinr-emr/core-akr-templates`

### UPDATE 6A — Add `github-mcp-calls-per-run` to SSG premium-requests block
**Location:** In each model's `ssg` → `premium-requests` block (for both `gpt-4o` and `claude-sonnet-4-6`), add the following two fields alongside the existing null fields:

```json name=benchmark.json url=https://github.com/reyesmelvinr-emr/core-akr-templates/blob/main/evals/benchmark.json
"github-mcp-calls-per-run": 2,
"github-mcp-calls-note": "One @github call for condensed charter (Pass 1) + one @github call for modules.yaml (Pass 1). No additional @github calls authorized in Passes 2-7 per forward payload discipline."
```

**Also add to the top-level `quota-planning` block:**

```json name=benchmark.json url=https://github.com/reyesmelvinr-emr/core-akr-templates/blob/main/evals/benchmark.json
"github-mcp-tool-calls-count-toward-quota": true,
"github-mcp-tool-calls-note": "Each @github tool call consumes one premium request in addition to generation calls. Mode B runs budget 2 tool calls per run (charter + modules.yaml). Track separately from generation call counts in Phase 2 pilot data."
```

---

## Summary Table

| File | Update ID | Section | Action Type |
|---|---|---|---|
| `AKR_Tracking.md` | 1A | Phase 0 Pre-Pilot 7-Test Checklist | Add new Test 2A row after Test 7 |
| `AKR_Tracking.md` | 1B | Phase 0 Issues and Clarifications | Append post-gate clarification bullet after line 107 |
| `AKR_Tracking.md` | 1C | Phase 2 Issues and Clarifications | Append 5 new operational impact bullets after line 346 |
| `AKR_Tracking.md` | 1D | Phase 2 Deliverable Tracking table | Add 3 new Deliverable 1 task rows after line ~259 |
| `AKR_Tracking.md` | 1E | Change Log | Append 1 change log entry at end of file |
| `PHASE_2_PILOT_ONBOARDING.md` | 2A | Deliverable 1 Onboarding Checklist | Replace MCP step with 2-step GitHub MCP + fallback structure |
| `PHASE_2_PILOT_ONBOARDING.md` | 2B | Deliverable 5 Visual Studio Testing | Add updated scope block including `@github` availability test |
| `akr_implementation_ready_analysis.md` | 3A | Part 11 Pre-Pilot Validation Tests | Add Test 2A table block after Test 2 entry |
| `akr_implementation_ready_analysis.md` | 3B | Part 18.4 Forward Payload Design | Add Section 18.4.1 `@github` tool call discipline block |
| `SKILL.md` (core-akr-templates) | 4A | Mode B Step 2 | Replace charter loading step with PATH A / PATH B / prohibition block |
| `SKILL-COMPAT.md` (core-akr-templates) | 5A | Model-Specific Failure Modes table | Add 2 new GPT-4o `@github`-related failure mode rows |
| `SKILL-COMPAT.md` (core-akr-templates) | 5B | Surface Compatibility / Invocation Surfaces | Add GitHub MCP availability table |
| `benchmark.json` (core-akr-templates) | 6A | SSG `premium-requests` block + `quota-planning` | Add `github-mcp-calls-per-run: 2` and quota note fields |