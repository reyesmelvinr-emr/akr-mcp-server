# AKR Mode Rename Plan: Full Replacement Tracking

**Status:** COMPLETED  
**Created:** March 31, 2026  
**Target Completion:** Phase 0 (concurrent with other Phase 0 tasks)  
**Owner:** Standards Author

---

## Executive Summary

Replace Mode A/B/C with verb-first functional names across active AKR runtime artifacts:

| Current | New | Shorthand Command | Purpose |
|---|---|---|---|
| Mode A | ProposeGroupings | `/akr-docs groupings` | Propose and review module grouping boundaries |
| Mode B | GenerateDocumentation | `/akr-docs generate` | Generate and validate module docs |
| Mode C | ResolveUnknowns | `/akr-docs resolve` | HITL resolution of unresolved markers |

### Locked Decisions
- `mode:` metadata header value for Generation is exactly `generation` (not `generate`).
- Historical planning records are immutable and intentionally out of scope for this rename.
- Slash-command syntax is updated in active docs and runtime instructions.
- Eval YAML `description:` fields use plain English prose (for example, "generation output completeness") rather than functional labels.

### Scope and Risk
- Scope includes: SKILL files, compatibility matrix, validator strings/tests, workspace instructions, README, eval fixtures, benchmark keys, distribution-dependent artifacts, and changelog.
- Out of scope: archived/historical planning docs and prior decision records.
- Risk remains low: no `modules.yaml` schema enum migration is required.

---

## Validation of GH28 Recommendations

Validated and included:
- SKILL-COMPAT inclusion and date bump.
- `.akr/standards/copilot-instructions.md` inclusion.
- Dual validator test paths coverage.
- Validator line-number pre-check before edits.
- Explicit README hotspot checklist.
- Explicit Audience header checklist for charter instruction files.
- Explicit CHANGELOG entry template.
- `ssg-pass-sequence.yaml` command check.
- Re-evaluation-policy handling documented as explicit deferral note.

Updated plan decision:
- Implementation-plans rename step removed to honor immutable historical-doc decision.

---

## Phase 1: Naming and Checklist Baseline

### Step 1: Confirm naming contract (30 min)
- [x] Confirm functional names: ProposeGroupings, GenerateDocumentation, ResolveUnknowns.
- [x] Confirm command aliases: `groupings`, `generate`, `resolve`.
- [x] Confirm metadata contract: `mode: generation` for GenerateDocumentation outputs.

### Step 2: Build migration checklist (30 min)
- [x] Runtime skill files and distributed copies.
- [x] Compatibility matrix and policy notes.
- [x] Validator script and both test files.
- [x] Workspace instruction surfaces (global + condensed charters + fallback copy).
- [x] Eval cases, benchmark keys, and non-renamed eval command fields.
- [x] README hotspots and support snippets.
- [x] CHANGELOG entry.

---

## Phase 2: Core Artifact Updates

### Step 3: Update skill bundle (2.25 hours)

Files:
- `core-akr-templates/.github/skills/akr-docs/SKILL.md`
- `core-akr-templates/.github/skills/akr-docs/SKILL-COMPAT.md`

Checklist:
- [x] Rename Mode section headers and command examples in SKILL.md.
- [x] Update any step references that call out Mode A/B/C.
- [x] Keep metadata header requirement and set Generation mode value to `generation`.
- [x] Update SKILL-COMPAT references: known issues, role mapping, governance stability seed rows.
- [x] Bump `Last updated` in SKILL-COMPAT.
- [x] Add explicit note in SKILL-COMPAT: eval re-run deferred for rename-only change (no behavior logic change) and to be run at next behavioral change.

Acceptance:
- [x] SKILL.md and SKILL-COMPAT terminology is fully aligned.

### Step 4: Update validator messaging and tests (1.75 hours)

Files:
- `core-akr-templates/.akr/scripts/validate_documentation.py`
- `core-akr-templates/.akr/scripts/tests/test_validate_documentation.py`
- `core-akr-templates/.akr/scripts/test_validate_documentation.py` (verify impact; update if assertions/messages reference mode labels)

Precondition:
- [x] Run exact-string inventory before editing: `grep -n "Mode [ABC]\|mode-[abc]\|Mode B Preview" .akr/scripts/validate_documentation.py`

Checklist:
- [x] Update declared-artifact warnings currently mentioning Mode A/Mode B.
- [x] Update final-doc cleanliness message currently referencing Mode B Step 6a.
- [x] Update preview header currently rendered as `Mode B Preview:`.
- [x] Update subprocess test assertions in `.akr/scripts/tests/test_validate_documentation.py`.
- [x] Verify whether `.akr/scripts/test_validate_documentation.py` checks user-visible mode text; patch if needed.

Acceptance:
- [x] `pytest .akr/scripts/tests/test_validate_documentation.py -v` passes.
- [x] Secondary test file is either updated or explicitly confirmed unaffected.

### Step 5: Update instruction surfaces (1.25 hours)

Files:
- `core-akr-templates/.akr/standards/copilot-instructions.md`
- `core-akr-templates/copilot-instructions/backend-service.instructions.md`
- `core-akr-templates/copilot-instructions/ui-component.instructions.md`
- `core-akr-templates/copilot-instructions/database.instructions.md`
- `training-tracker-backend/.github/copilot-instructions.md`

Checklist:
- [x] Replace `/akr-docs mode-a|mode-b|mode-c` invocation references.
- [x] Replace Mode A/B/C heading language with functional naming.
- [x] Update all `Audience: Agent Skill Mode B ...` headers.
- [x] Confirm fallback copy in training tracker matches updated guidance.

Acceptance:
- [x] No active instruction surface still prescribes old slash commands.

### Step 6: Update eval fixtures and benchmark keys (1.75 hours)

Files:
- `core-akr-templates/evals/cases/mode-a-standard.yaml` -> `groupings-standard.yaml`
- `core-akr-templates/evals/cases/mode-b-coursedomain.yaml` -> `generate-coursedomain.yaml`
- `core-akr-templates/evals/cases/mode-b-large-module.yaml` -> `generate-large-module.yaml`
- `core-akr-templates/evals/cases/ssg-pass-sequence.yaml` (no rename required; command field check required)
- `core-akr-templates/evals/benchmark.json`

Checklist:
- [x] Rename the three `mode-*` files and internal `id` values.
- [x] Update `command` fields to new slash command syntax.
- [x] Update `description` fields to plain English prose (remove "Mode A/B/C" wording).
- [x] Update benchmark key names to match new fixture names.
- [x] Update benchmark prose references (`Mode C resolution` -> `ResolveUnknowns resolution`).
- [x] Verify `ssg-pass-sequence.yaml` command field no longer uses `/akr-docs mode-b`.

Acceptance:
- [x] Fixture names, IDs, commands, and benchmark keys are consistent.

### Step 7: Update README and support text (1.25 hours)

Files:
- `core-akr-templates/README.md`
- `akr-mcp-server/templates/core/README.md` (if present and currently used)

Explicit README hotspots in `core-akr-templates/README.md`:
- [x] Overview bullet describing three-mode workflow.
- [x] Key Architecture bullets listing Mode A/B/C.
- [x] Repository tree comment (`Three-mode workflow (A, B, C)`).
- [x] Eval fixture list in repository tree (`mode-*` filenames).
- [x] Agent Skill documentation link text (`Mode A/B/C workflow definition`).
- [x] Support command snippet `/akr-docs mode-a`.
- [x] Support command snippet `/akr-docs mode-c ...`.

Acceptance:
- [x] README references and command examples all use new naming.

### Step 8: Add changelog entry (20 min)

File:
- `core-akr-templates/CHANGELOG.md`

Checklist:
- [x] Add dated entry `2026-03-31 - Skill Command Rename (Phase 0)`.
- [x] Mark command rename as breaking for command consumers.
- [x] Include metadata field update (`mode: B` -> `mode: generation`).
- [x] Include eval fixture rename mapping.

Acceptance:
- [x] Changelog records command migration and rationale.

---

## Phase 3: Validation, Distribution, and Cleanup

### Step 9: Validate and smoke test (1 hour)

Checklist:
- [x] Run validator tests for updated assertion paths.
- [x] Smoke test skill invocation patterns for `groupings`, `generate`, `resolve`.
- [x] Confirm preview output and warnings reflect new terms.

### Step 10: Distribute updated bundle (35 min)

Distribution coupling from workflow:
- `distribute-skill.yml` copies both SKILL.md and SKILL-COMPAT.md.
- Trigger note: distribution is not automatic on commit. Run `workflow_dispatch` manually for `distribute-skill.yml` targeting `reyesmelvinr-emr/training-tracker-backend`, or push a `v*` tag when this change is bundled into a release (preferred audit trail).

Checklist:
- [x] Ensure both files are updated before triggering distribution.
- [x] Verify distributed copy in training tracker for both files.

### Step 11: Final search and classification (40 min)

Checklist:
- [x] Search active surfaces for `Mode [ABC]|mode-[abc]|mode: [ABC]`.
- [x] For any remaining hits, classify as active artifact vs historical record.
- [x] Keep historical references unchanged and document intentional exclusions.

---

## Explicit Exclusions

Intentionally not renamed in this plan:
- `akr-mcp-server/docs/implementation_plans/*.md`
- `akr-mcp-server/docs/akr_implementation_ready_analysis.md`

Reason:
- These are historical planning and decision-trace artifacts and remain immutable records.

---

## File Inventory (Active Scope)

Core skill bundle:
- `core-akr-templates/.github/skills/akr-docs/SKILL.md`
- `core-akr-templates/.github/skills/akr-docs/SKILL-COMPAT.md`

Validator and tests:
- `core-akr-templates/.akr/scripts/validate_documentation.py`
- `core-akr-templates/.akr/scripts/tests/test_validate_documentation.py`
- `core-akr-templates/.akr/scripts/test_validate_documentation.py` (verify/update as needed)

Instruction surfaces:
- `core-akr-templates/.akr/standards/copilot-instructions.md`
- `core-akr-templates/copilot-instructions/backend-service.instructions.md`
- `core-akr-templates/copilot-instructions/ui-component.instructions.md`
- `core-akr-templates/copilot-instructions/database.instructions.md`
- `training-tracker-backend/.github/copilot-instructions.md`

Eval and metrics:
- `core-akr-templates/evals/cases/groupings-standard.yaml` (renamed)
- `core-akr-templates/evals/cases/generate-coursedomain.yaml` (renamed)
- `core-akr-templates/evals/cases/generate-large-module.yaml` (renamed)
- `core-akr-templates/evals/cases/ssg-pass-sequence.yaml` (command update check)
- `core-akr-templates/evals/benchmark.json`

Docs and release notes:
- `core-akr-templates/README.md`
- `akr-mcp-server/templates/core/README.md` (if active)
- `core-akr-templates/CHANGELOG.md`

---

## Effort Summary

| Phase | Area | Duration |
|---|---|---|
| 1 | Naming + checklist baseline | 1.0h |
| 2 | Core artifact updates | 8.25h |
| 3 | Validation + distribution + cleanup | 2.25h |
| | **Total** | **~11.5h** |

Note:
- Total increased versus earlier draft because validated scope now includes SKILL-COMPAT, global workspace instructions, changelog, secondary test-path verification, and final exclusion audit.

---

## Sign-Off

- [x] Plan reviewed and approved.
- [x] Locked decisions accepted (`mode: generation`, historical-doc exclusions).
- [x] Implementation authorized.

