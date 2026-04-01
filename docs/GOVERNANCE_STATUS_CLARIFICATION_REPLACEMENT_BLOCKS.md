# Governance Status Clarification Replacement Blocks

Date: 2026-03-31

Purpose: provide exact replacement text blocks to remove ambiguity between:

- module grouping approval state in `modules.yaml`
- generated document maturity state in `docs/..._doc.md`

This file is a drafting aid only. It does not change schema or code behavior. It aligns governance language first so implementation can follow a single, explicit policy.

---

## Policy Baseline

Use this policy consistently across all updates below:

- `modules.yaml` module `status` governs **Mode A grouping readiness** for a module.
- `modules.yaml` approval means the file grouping, naming, and module boundary were reviewed and accepted.
- `modules.yaml` approval does **not** mean generated documentation content was reviewed or approved.
- First-generation Mode B output is a **draft document** unless an explicit document-content approval step has already occurred and that approval is separately recorded.
- `modules-yaml-status` in the `akr-generated` header is a **traceability field only**. It records the module workflow state used at generation time and must not be interpreted as the document's approval state.

---

## 1. core-akr-templates/copilot-instructions/backend-service.instructions.md

### Replace the current `Rules:` block under `## Required Front Matter` with:

```md
Rules:
- businessCapability: required PascalCase key from tag-registry.
- feature: required work-item tag in FN#####_US##### format.
- layer: required and must match module layer.
- project_type: required, expected api-backend.
- status: governs the generated document's maturity state, not the module grouping approval state.
- for first-generation Mode B output, set status to draft unless document-content approval has already occurred through the documented review flow.
- do not copy `modules.yaml` module status directly into document front matter.
- compliance_mode: pilot or production.
```

### Replace the current `## Metadata Header Requirements` bullet list with:

```md
## Metadata Header Requirements
Before section content, include an AKR metadata header block:

- Header marker: <!-- akr-generated -->
- Required fields: skill, mode, template, steps-completed, generated-at
- Required traceability field: modules-yaml-status
- Interpretation rule: modules-yaml-status records the Mode A grouping state used to authorize generation; it does not define the generated document's front matter status
- For section-scoped generation include: generation-strategy, passes-completed, pass-timings-seconds, total-generation-seconds
```

---

## 1b. core-akr-templates/copilot-instructions/ui-component.instructions.md

### Replace line:

```md
- status and compliance_mode must align with workflow stage.
```

### With:

```md
- status: governs the generated document's maturity state, not the module grouping approval state.
   For first-generation Mode B output, set status to draft unless document-content approval has already occurred through the documented review flow.
   Do not copy modules.yaml module status directly into document front matter.
- compliance_mode: pilot or production.
```

---

## 2. docs/akr_implementation_ready_analysis.md

### Replace the `Mode B — Documentation generation` through `Mode B — Content review` rows in `### 1.3 What the Agent Does vs. What Humans Validate` with:

```md
| Mode B — Documentation generation | Copilot coding agent | Reads a grouping-approved `modules.yaml`; loads condensed charter; reads source files; generates a draft module document; opens draft PR | Automated |
| Mode B — Pre-commit draft (committed) | Copilot agent | Before writing to doc_output, generates draft at `docs/modules/.akr/{ModuleName}_draft.md` and displays validation summary in chat. Developer edits draft in VS Code. Agent writes final doc from confirmed draft. Draft is a permanent committed artifact. | <1 min (agent) |
| Mode B — In-editor content review | Developer + tech lead | Opens draft in VS Code Markdown Preview. Fills ❓ sections, validates business rules, confirms architecture, and reviews document maturity independently from module grouping approval. Replies 'ready to commit'. | 20–30 min |
| Mode B — Incremental update (code change) | Copilot agent + developer | Agent reads committed draft; reads only changed source files; loads only relevant charter sections; patches affected sections. Developer confirms targeted changes only. Does not re-read all files or re-run full SSG unless patch scope expands. | ≤10 min |
| Mode B — Content review | Developer + tech lead | Fills `❓` sections; validates business rules; confirms data operations accuracy; determines whether the document remains draft or is promoted through a separate content-approval decision | 20–30 min per module |
```

### Insert this paragraph immediately after the table in `### 1.3 What the Agent Does vs. What Humans Validate`:

```md
Governance clarification: the module `status` recorded in `modules.yaml` is the approval state for the module boundary produced by Mode A. It authorizes Mode B to run, but it does not certify the generated document content. A generated module document therefore begins life as a draft artifact unless document-content approval is separately completed and explicitly recorded.
```

### Replace the sentence:

```md
This is the correct HITL model: **validate the grouping** (Mode A), **generate and review module content** (Mode B), then **interactively resolve remaining `❓` markers in the editor** (Mode C) before merge.
```

with:

```md
This is the correct HITL model: **validate the grouping** (Mode A), **generate draft module content and review that content** (Mode B), then **interactively resolve remaining `❓` markers in the editor** (Mode C) before merge. Grouping approval and document-content approval are separate governance decisions and must not share a single ambiguous status value.
```

### Replace the line in the front matter requirements list:

```md
- Required YAML front matter fields (`feature`, `layer`, `project_type`, `status`, `compliance_mode`)
```

with:

```md
- Required YAML front matter fields (`feature`, `layer`, `project_type`, `status`, `compliance_mode`), where `status` represents document maturity and must not be inferred from `modules.yaml` grouping approval alone
```

### Replace the heading note:

```md
## Mode B — Generate Module Documentation
## (Run only after modules.yaml is approved — status on target module is not draft)
```

with:

```md
## Mode B — Generate Module Documentation
## (Run only after modules.yaml grouping approval is complete — target module status is not draft)
```

---

## 3. AKR_Tracking.md

### Add this bullet at the top of `### Issues and Clarifications` for Phase 2:

```md
- 2026-03-31: Governance clarification required: `modules.yaml` module status currently records Mode A grouping approval, but generated module docs can be misread as inheriting that status as document approval. Policy intent is that grouping approval authorizes Mode B generation only; it does not approve document content. Governance text across analysis, implementation plans, and condensed instructions must explicitly separate grouping state from document maturity before code/schema remediation proceeds.
```

### Add this task row under `Deliverable 11 - Artifact Normalization`:

```md
| Deliverable 11 - Artifact Normalization | Publish status-semantics clarification across governance docs before code/schema changes | Standards author | NOT_STARTED | Pending | TBD | Clarifies that `modules.yaml` status is Mode A grouping approval only; generated document front matter status remains a document-maturity field and defaults to draft on first generation |
```

---

## 4. docs/implementation_plans/PHASE_0_PREREQUISITES.md

### Replace the bullet:

```md
- Required YAML front matter fields (`businessCapability`, `feature` (work-item tag), `layer`, `project_type`, `status`, `compliance_mode`)
```

with:

```md
- Required YAML front matter fields (`businessCapability`, `feature` (work-item tag), `layer`, `project_type`, `status`, `compliance_mode`)
- Status semantics clarification: document front matter `status` represents document maturity, while `modules.yaml` module `status` represents Mode A grouping approval state
```

### Replace the task row:

```md
| Add prerequisite check in Mode B | Standards author | Mode B stops if `modules.yaml` status is `draft` | 30 min |
```

with:

```md
| Add prerequisite check in Mode B | Standards author | Mode B stops if `modules.yaml` grouping status is `draft`; this check authorizes generation only and does not set the generated document's front matter status | 30 min |
```

### Replace the Mode B workflow summary line:

```md
1. Read `modules.yaml`; find requested module; check `status != draft`
```

with:

```md
1. Read `modules.yaml`; find requested module; check grouping `status != draft`
```

### Replace the metadata header example line:

```md
modules-yaml-status: approved
```

with:

```md
modules-yaml-status: approved
# Traceability only: this records grouping approval state from Mode A and must not be interpreted as final document approval.
```

### Replace the field description:

```md
- `status` (enum: draft, review, approved, deprecated)
```

with:

```md
- `status` (enum: draft, review, approved, deprecated) for Mode A grouping approval state only; do not reuse this field as the generated document's content-approval state without an explicit governance rule
```

---

## 5. docs/implementation_plans/PHASE_1_FOUNDATION.md

### Replace the validator front matter bullet:

```md
  - YAML front matter: `businessCapability`, `feature` (work-item), `layer`, `project_type`, `status`, `compliance_mode`
```

with:

```md
  - YAML front matter: `businessCapability`, `feature` (work-item), `layer`, `project_type`, `status`, `compliance_mode`
  - Status semantics rule: front matter `status` is the generated document's maturity field and must not be auto-derived from `modules.yaml` grouping approval state
```

### Replace the task row:

```md
| Add module-scope YAML front matter | Standards author | `businessCapability`, `feature`, `layer`, `project_type`, `status` fields documented | 1 hour |
```

with:

```md
| Add module-scope YAML front matter | Standards author | `businessCapability`, `feature`, `layer`, `project_type`, `status` fields documented, with explicit separation between document maturity status and `modules.yaml` grouping approval status | 1 hour |
```

### Replace the sample front matter line:

```md
   status: draft
```

with:

```md
   status: draft
   # Draft is the default for first-generation Mode B output. Do not replace with the module's grouping approval state from modules.yaml.
```

### Add this sentence immediately after:

```md
This check applies only to files matching a modules[].doc_output path (not draft_output paths).
```

Add:

```md
The validator's final-doc cleanliness rules must be read alongside this governance rule: a final doc may be structurally final for CI purposes while still carrying `status: draft` until document-content approval is completed through the documented review flow.
```

---

## 6. docs/implementation_plans/PHASE_2_PILOT_ONBOARDING.md

### Replace the success criteria lines:

```md
2. ✅ Mode A (grouping proposal) completed; `modules.yaml` approved in ≤15 minutes
3. ✅ Mode B (documentation generation) completed for 3 modules
```

with:

```md
2. ✅ Mode A (grouping proposal) completed; `modules.yaml` grouping approval completed in ≤15 minutes
3. ✅ Mode B (documentation generation) completed for 3 modules, with document review performed separately from grouping approval
```

### Replace the checklist line:

```md
- [ ] modules.yaml approved before documentation generation begins
```

with:

```md
- [ ] modules.yaml grouping approval completed before documentation generation begins
- [ ] Document front matter status is reviewed as a separate content-maturity decision and is not assumed from modules.yaml approval
```

### Replace the Step 2 block:

```md
**Step 2 - Final doc_output + PR (after developer confirms):**
Final `docs/modules/{ModuleName}_doc.md` written from the confirmed draft.
Draft-only front matter fields stripped; final-doc front matter injected (Step 6a).
PR body notes: "Pre-commit draft reviewed at docs/modules/.akr/{ModuleName}_draft.md before PR open."
CI validates final file. modules.yaml updated with draft_output, last_reviewed_at, review_mode.
```

with:

```md
**Step 2 - Final doc_output + PR (after developer confirms):**
Final `docs/modules/{ModuleName}_doc.md` written from the confirmed draft.
Draft-only front matter fields stripped; final-doc front matter injected (Step 6a).
For first-generation output, final-doc front matter status remains `draft` unless document-content approval has already been explicitly completed and recorded.
PR body notes: "Pre-commit draft reviewed at docs/modules/.akr/{ModuleName}_draft.md before PR open."
CI validates final file. modules.yaml updated with draft_output, last_reviewed_at, review_mode.
`modules.yaml` approval remains the grouping-control record; it is not the document approval record.
```

### Replace the developer review note:

```md
**Note:** Review is done in VS Code. The draft file is both the review surface and the permanent record of the developer's annotations.
```

with:

```md
**Note:** Review is done in VS Code. The draft file is both the review surface and the permanent record of the developer's annotations. This review governs document maturity. It is distinct from the earlier Mode A review that governed module grouping correctness.
```

---

## 7. core-akr-templates/.github/skills/akr-docs/SKILL.md

### Replace ProposeGroupings step 2:

```md
2. If modules exist, proceed only for module targets where grouping status is approved; stop and request grouping approval for draft/review targets.
  Note: grouping approval authorizes generation only. It does not set the generated document front matter status.
```

### Replace GenerateDocumentation step 6:

```md
6. Strip draft-only front matter fields and write final document to module doc_output path.
  Status rule: first-generation output must use `status: draft` in generated document front matter unless document-content approval has already been explicitly completed and recorded.
  Do not copy module grouping status from modules.yaml into generated document front matter.
```

### Replace the `modules-yaml-status` line in `### Required metadata header contract`:

Current line to replace:

```md
modules-yaml-status: approved
```

Replacement line:

```md
modules-yaml-status: {actual module status from modules.yaml at generation time}
```

### Add this interpretation note immediately below the metadata header contract block:

```md
Interpretation note: `modules-yaml-status` is a traceability field only. It records the Mode A grouping state used when Mode B ran. It must not be interpreted as generated document approval state.
```

---

## Optional Terminology Addendum

If you want a short terminology block repeated across documents, use this exact text:

```md
Status terminology:
- `modules.yaml` module `status` = Mode A grouping approval state
- generated document front matter `status` = document maturity state
- `modules-yaml-status` in `<!-- akr-generated -->` = traceability field recording the grouping state used at generation time
```

---

## Implementation Note

These replacement blocks intentionally align governance language before any schema or code change. If governance is updated first, the subsequent implementation task becomes clearer:

- keep `modules.yaml` status for grouping approval
- keep first-generation docs as `status: draft`
- retain `modules-yaml-status` only as traceability metadata
- introduce a separate document-approval mechanism later if needed
Append the following section at the end of GOVERNANCE_STATUS_CLARIFICATION_REPLACEMENT_BLOCKS.md.

### Apply Order and Patch Bundle

Goal: apply governance wording updates first, then skill behavior wording, while keeping schema/code unchanged in this pass.

1. Update instruction semantics in core-akr-templates/copilot-instructions/backend-service.instructions.md and core-akr-templates/copilot-instructions/ui-component.instructions.md.
2. Update skill workflow semantics in core-akr-templates/.github/skills/akr-docs/SKILL.md.
3. Update governance narrative in akr_implementation_ready_analysis.md.
4. Update planning language in PHASE_0_PREREQUISITES.md, PHASE_1_FOUNDATION.md, and PHASE_2_PILOT_ONBOARDING.md.
5. Record tracking entry updates in AKR_Tracking.md.

Patch Bundle by Repository:

1. Repository: core-akr-templates  
   Files:
   - core-akr-templates/copilot-instructions/backend-service.instructions.md  
   - core-akr-templates/copilot-instructions/ui-component.instructions.md  
   - core-akr-templates/.github/skills/akr-docs/SKILL.md  
   Scope:
   - Clarify status semantics separation.
   - Make modules-yaml-status metadata dynamic and traceability-only.
   - Add explicit first-generation document status draft rule.

2. Repository: akr-mcp-server  
   Files:
   - akr_implementation_ready_analysis.md  
   - AKR_Tracking.md  
   - PHASE_0_PREREQUISITES.md  
   - PHASE_1_FOUNDATION.md  
   - PHASE_2_PILOT_ONBOARDING.md  
   Scope:
   - Normalize governance language to separate Mode A grouping approval from document maturity.
   - Align phase-plan wording with skill/instruction semantics.
   - Add explicit tracking note for ambiguity remediation.

3. Repository: training-tracker-backend  
   Files:
   - None in this governance-only pass.  
   Scope:
   - No code/schema/document runtime edits in this pass.
   - Consume updated guidance after upstream docs are merged.

Validation Checklist after applying patches:

1. Confirm no statement implies modules.yaml approval equals document approval.
2. Confirm all modules-yaml-status wording explicitly says traceability-only.
3. Confirm SKILL step language enforces draft as first-generation default for document front matter.
4. Confirm phase docs and tracking language are consistent with instruction and skill updates.
5. Confirm no schema or runtime behavior change was introduced in this governance-only pass.

