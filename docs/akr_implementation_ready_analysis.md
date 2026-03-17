# AKR Documentation Governance — Implementation-Ready Analysis
## Definitive Synthesis: Five Reviews + Module-Based Architecture | March 2026

**Engineering Standards | Confidential | Ready for Implementation Planning**

---

## About This Document

This is the definitive pre-implementation analysis for the AKR Documentation Governance system. It synthesizes five independent reviews and one architectural clarification that materially changed the implementation scope. It is structured to feed directly into an implementation plan — every section ends with a concrete, actionable consequence.

### Source Material

| Source | Access | Key Contribution |
|---|---|---|
| Review 1 — Claude | No repository access | Structural governance; pre-pilot assumptions; version drift risk; Phase 3 infrastructure gap |
| Review 2 — GitHub Copilot Round 1 | Direct repo inspection | Monolith diagnosis confirmed; Copilot coding agent as Phase 2.5; first context saturation identification |
| Review 3 — GitHub Copilot Round 2 | Deeper inspection | Charter sizes quantified; compression elevated to blocking precondition; test infrastructure as migration asset; `force_workflow_bypass` corrected |
| Review 4 — M365 Copilot | README + documentation | Agent Skills as primary workflow primitive; Copilot Studio for non-developer HITL; premium request metering; `TEMPLATE_MANIFEST.json` retention |
| Review 5 — GitHub Copilot (Module Architecture) | Direct repo + module clarification | Three-tier documentation hierarchy defined; two-mode Agent Skill specified; `modules.yaml` full schema; `validate_documentation.py` scope upgraded; `layer` vs. `project_type` distinction corrected |
| Review 6 — GitHub Copilot (Schema Audit) | Full inspection of `akr-config-schema.json` + `consolidation-config-schema.json` | Four corrections: `modules-schema.json` is a new artifact; `consolidation-config-schema.json` needs `modulesManifestPath`; dual cross-repo config overlap; `project_type` not in existing `requiredTags`. Three additions: `humanInput` schema maps to HITL model; `warnOnMissingLayers` already defined; `monitoring` schema feeds cost baseline |
| Review 7 — GitHub Copilot (Final File Inspection) | Direct read of `copilot-instructions.md`, `.akr/workflows/`, `tag-registry.json` | Confirmed `copilot-instructions.md` is a full replacement (not partial edit); confirmed two existing workflows (`validate-documentation.yml` already calls the script); confirmed `tag-registry.json` PascalCase format incompatible with free-text `feature` field examples |
| Module Architecture Clarification | Owner-provided | `courses_service_doc.md` confirmed as Level 1 spec; module grouping rules; database object separation; template adaptation requirements |
| Workflow Clarifications (Owner-provided) | Owner-provided | `/docs.interview` original purpose clarified as HITL completion for `❓` sections in existing docs; Agent Skill Mode C added for interactive HITL; zero-cloud/no-incremental-cost constraint made explicit; original `core-akr-templates` ↔ `akr-mcp-server` design intent documented |
| Review 9 — Skill Optimization Analysis | Post-implementation planning conversation | Three failure modes of Copilot skill non-invocation identified; three-layer reliability stack specified (`disable-model-invocation` frontmatter + session hooks + in-document metadata contract); LLM execution quality variance quantified (Claude Sonnet 4.6 ≥90% vs. GPT-4o ~75%); eval framework and `benchmark.json` schema defined; `SKILL-COMPAT.md` as companion model compatibility matrix introduced; hooks (`postToolUse` + `agentStop`) specified as Layer 2 enforcement |

---

## Part 1: The Foundational Architecture — What We Are Building

Before implementation details, the architecture must be stated precisely. All prior confusion about what a "module" is, what templates apply where, and what the agent does vs. what humans validate is resolved here.

### 1.1 The Three-Tier Documentation Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│  LEVEL 3: Feature Consolidation                             │
│  Template: feature-consolidated.md                          │
│  Output:   docs/features/{FeatureName}_doc.md               │
│  Producer: consolidate.py (deterministic aggregation)       │
│  Audience: Product Owner, QA Lead, Tech Lead                │
│  Input:    Level 1 module docs + Level 2 DB docs            │
│            matched by feature_tag                           │
└────────────────────┬────────────────────────────────────────┘
                     │ reads from
     ┌───────────────┴───────────────┐
     ▼                               ▼
┌──────────────────────┐   ┌────────────────────────────────┐
│  LEVEL 1             │   │  LEVEL 2                       │
│  Module Documentation│   │  Database Object Documentation │
│                      │   │                                │
│  Unit: Logical       │   │  Unit: Individual DB object    │
│  grouping of 3–8     │   │  (table, view, procedure)      │
│  domain files        │   │                                │
│                      │   │  Template: table_doc_template  │
│  Template: adapted   │   │  or embedded_database_template │
│  lean_baseline /     │   │                                │
│  ui_component        │   │  Output:                       │
│                      │   │  docs/database/{Object}_doc.md │
│  Output:             │   │                                │
│  docs/modules/       │   │  Producer: Agent Mode (Mode B) │
│  {Module}_doc.md     │   │  or manual                     │
│                      │   │                                │
│  Producer:           │   │  Source: SSDT project, scripts,│
│  Coding Agent Mode B │   │  or manual extraction          │
└──────────────────────┘   └────────────────────────────────┘
        ▲                               ▲
        │ proposes groupings            │ identifies objects
        └───────────────────────────────┘
              Agent Skill Mode A
              (modules.yaml draft)
```

**The key architectural insight confirmed by the module clarification:** The `courses_service_doc.md` sample already *is* the correct Level 1 output. It covers `CoursesController`, `ICourseService`, `ICourseRepository`, `EfCourseRepository`, and `CourseDtos` in a single document — not because it was manually crafted to be comprehensive, but because the module grouping principle correctly identifies these five files as one logical domain unit. The sample is the acceptance criterion for Level 1 template adaptation.

### 1.2 The Module Grouping Principle

A module is a **logical grouping of source files that together implement a single domain concept**, identified by:

- **Namespace / folder co-location** sharing the same domain noun (e.g., `Course`)
- **Dependency graph** — controller injects service interface; service injects repository interface; EF implementation implements repository interface
- **DTO / Contract alignment** — DTOs serve the same domain noun as the service
- **Interface / implementation pairs** — `ICourseService.cs` + `CourseService.cs`

**Rules that are invariant:**

| Rule | Rationale |
|---|---|
| `max_files: 8` per module | Context token ceiling with condensed charter (~2,500 tokens) + source files |
| Database objects are never grouped with application code | Different template, different documentation unit, different Level |
| One `modules.yaml` per repository | Single manifest; `validate_documentation.py` and `consolidate.py` both read from it |
| `modules[]` for API/UI groupings; `database_objects[]` for DB objects | Schema enforces the separation; validator applies different section rules per type |
| Mode A (grouping proposal) must precede Mode B (documentation generation) | Cannot generate a module doc before the grouping is human-validated |

### 1.3 What the Agent Does vs. What Humans Validate

| Stage | Who/What | What They Do | Time Cost |
|---|---|---|---|
| Mode A — Grouping proposal | Copilot coding agent | Scans project; groups by domain noun; writes draft `modules.yaml`; opens PR | Automated |
| Mode A — Grouping validation | Developer who knows the codebase | Reviews groupings; reassigns misplaced files; names modules correctly; splits over-large groups | 5–10 min per project |
| Mode B — Documentation generation | Copilot coding agent | Reads approved `modules.yaml`; loads condensed charter; reads source files; generates doc; opens draft PR | Automated |
| Mode B — Content review | Developer + tech lead | Fills `❓` sections; validates business rules; confirms data operations accuracy | 20–30 min per module |
| Mode C — Interactive HITL completion | Copilot agent mode + developer | Guides developer through unresolved `❓` one section at a time in existing documents; records accepted edits and deferred items | 10–20 min per document |
| CI gate | `validate_documentation.py` + Vale | Validates required sections, markers, `project_type`, `feature_tag` format | Automated at PR merge |

This is the correct HITL model: **validate the grouping** (Mode A), **generate and review module content** (Mode B), then **interactively resolve remaining `❓` markers in the editor** (Mode C) before merge.

---

## Part 2: Repository Ground Truth — Confirmed Facts

*All code-level findings are from direct repository inspection (Reviews 2, 3, 5). These supersede document-level claims.*

### 2.1 `akr-mcp-server` — Final Verdict

**Archive at current state (v0.2.0). Do not invest in Sprint 2.**

Evidence summary:
- `src/server.py`: 75,082 bytes, ~1,750 lines, single `if/elif` dispatcher (lines 815–1,507)
- Duplicate `except TypeError` at lines 1,468–1,498 — active undocumented bug
- `tests/test_server.py`: 67 lines, 100% `@pytest.mark.skip` — zero server-layer test coverage
- `VSCODE_WORKSPACE_FOLDER` hard dependency (line 1,028) + `setup.ps1` (14,849 bytes Windows PowerShell) — Windows + VS Code by design
- Version drift: `InitializationOptions` reports `0.1.0`; tool handlers report `0.2.0`
- `force_workflow_bypass` is config-gated via `allowWorkflowBypass` — not ungated as earlier reviews stated
- Zero team adoption — zero migration cost

**What to carry forward (do not discard):**
- `validation_library.py` — standalone validation logic, CI-reusable
- `test_pipeline_e2e.py` + `ServiceTemplateContext`/`ComponentTemplateContext` type definitions — Phase 2.5 acceptance criteria
- `generate_lean_backend_doc` MCP Prompt pattern (lines 1,550–1,700) — the pre-loading approach is the reference design for the condensed charter + Agent Skill architecture
- Tool-layer tests: `test_context_builder.py`, `test_validation_library.py`, `test_workflow_enforcement.py` — define the quality bar for generated documentation

**M365 analysis conflict resolved:** The M365 recommendation to "complete Sprint 2 first" was based on README-only analysis. Repository-grounded evidence overrules it. Archive immediately.

### 2.1A Original Design Intent: `core-akr-templates` and `akr-mcp-server` Relationship

The historical relationship between the two repositories was under-documented and should be explicit for decision traceability.

- `core-akr-templates` was intended as the remote canonical standards source on GitHub, not as a local developer dependency.
- The original PoC flow was: `core-akr-templates` (remote authority) → startup/CI sync pull → local `akr-mcp-server` context → slash-command workflow in VS Code.
- That sync mechanism was a planned Sprint 2 deliverable and was never implemented, so the repositories never became operationally connected in production.
- The Hosted MCP Context Source model replaces exactly this planned-but-unbuilt sync layer while preserving the same architectural intent (centralized remote standards, local authoring workflow).

**Consequence:** The current strategy is architectural continuity, not architectural reversal. The intermediary changed; the source-of-truth model did not.

### 2.2 `core-akr-templates` — Asset Inventory

**Templates — 10 confirmed (strategy documents referenced 8):**

| Template | Size | Role in New Architecture |
|---|---|---|
| `lean_baseline_service_template.md` | 28,029 bytes | Level 1 base — needs module variant adaptation |
| `ui_component_template.md` | 25,455 bytes | Level 1 base for UI modules — needs module variant |
| `table_doc_template.md` | 6,700 bytes | Level 2 — use as-is for database tables |
| `embedded_database_template.md` | 16,515 bytes | Level 2 — use as-is for embedded DB services |
| `feature-consolidated.md` | 7,204 bytes | Level 3 — already designed for consolidation; `FOR_EACH_*` placeholder syntax is `consolidate.py`'s data contract |
| `feature-testing-consolidated.md` | 11,729 bytes | Level 3 testing variant — parallel output for QA |
| `comprehensive_service_template.md` | 41,880 bytes | Reference only — too large for active context |
| `standard_service_template.md` | 20,608 bytes | Consolidate into lean_baseline via tier validation |
| `legacy_inventory_template.md` | 9,897 bytes | Retain for legacy system documentation |
| `minimal_service_template.md` | 3,620 bytes | Consolidate into lean_baseline via tier validation |

**Charters — confirmed sizes and token loads:**

| Charter | Size | Tokens | Role |
|---|---|---|---|
| `AKR_CHARTER_BACKEND.md` | 44,629 bytes | ~11,000 | Source for backend condensed charter |
| `AKR_CHARTER_UI.md` | 41,057 bytes | ~10,200 | Source for UI condensed charter |
| `AKR_CHARTER.md` (General) | 25,652 bytes | ~6,400 | Source for general condensed charter |
| `AKR_CHARTER_DB.md` | ~18,000 bytes | ~4,500 | Source for DB condensed charter |

**Context saturation is guaranteed for backend modules without charter compression.** Backend charter (~11,000) + lean baseline template (~7,000) = ~18,000 tokens before any source file loads. Charter compression is a Phase 0 blocking precondition.

**Other confirmed assets:**
- `standards/copilot-instructions.md` — exists; template selection logic is file-centric (must be rewritten to module-centric)
- `.akr/vale-rules/` — 7+ rule files; `RequiredSections.yml` confirms Vale checks for required sections; migration to `validation/vale-rules/` is non-trivial
- `.akr/workflows/` — workflow definitions already exist; audit before rebuilding
- `TEMPLATE_MANIFEST.json` (9,029 bytes) — retain as version registry for skill-template coupling; deprecate all other roles
- `tag-registry.json` — `feature` field in `modules.yaml` must match an approved entry here
- `akr-config-schema.json` — `layer` enum: `["UI", "API", "Database", "Integration", "Infrastructure", "Full-Stack"]` — used at project level in `modules.yaml`
- `consolidation-config-schema.json` — cross-repository configuration contract for `consolidate.py`; valid for repo-level config; document-to-section mapping must account for module docs as atomic units

**Additional assets (newly confirmed):**
- `tag-registry-schema.json` (3,847 bytes) — JSON Schema for `tag-registry.json` validation; enforces structure for feature enumeration
- `COST_MONITORING.md` (8,296 bytes) — GitHub Actions cost baseline and tracking guidance; references Jan 2026 pricing model ($0.005/min Ubuntu); critical for Phase 0 budgeting
- `workflows/distribute-tag-registry.yml` — Automation for syncing tag-registry across repositories
- `workflows/validate-documentation.yml` — CI pipeline for documentation validation; calls `validate_documentation.py`
- `vale-rules/AKR/` — Nested directory structure with organization-specific Vale quality rules (path different from earlier `vale-rules/` reference; no migration needed)

---

## Part 3: The Context Window Saturation Problem — Definitively Resolved

### The Scale of the Problem

| Context Load | Tokens | Verdict |
|---|---|---|
| `AKR_CHARTER_BACKEND.md` (current) | ~11,000 | Exceeds working context alone for structured output |
| + `lean_baseline_service_template.md` | + ~7,000 | **~18,000 tokens before source files load** |
| + 5 source files (typical module) | + ~5,000–8,000 | **~23,000–26,000 tokens** — guaranteed degradation |
| + 10 source files (large module) | + ~12,000–15,000 | **~30,000–33,000 tokens** — guaranteed failure |

This is not a risk to test. It is a guaranteed failure mode under current charter sizes for every backend module. Charter compression must precede all other Phase 0 work.

### The Four-Layer Resolution (Confirmed Across All Reviews)

**Layer 1 — Charter Compression (Phase 0, blocking)**

Produce condensed "dense summary" versions of each charter. Target: ~2,500 tokens each.

What the condensed charter retains:
- All required section headings and minimum content criteria
- Required YAML front matter fields (`feature`, `layer`, `project_type`, `status`, `compliance_mode`)
- `🤖` / `❓` / `NEEDS` / `VERIFY` / `DEFERRED` marker syntax and placement rules
- Quality thresholds (minimum word counts, required structural elements)
- Module-level section requirements (Module Files header, Operations Map, full-stack architecture diagram)
- Cross-references to full charter for deep reference

What gets removed: explanatory prose, rationale text, worked examples, historical context. Full charters stay in `charters/` as reference documentation.

With compressed charters:

| Module Type | Charter | Instructions | Source Files | Total | Verdict |
|---|---|---|---|---|---|
| Typical backend (5 files) | ~2,500 | ~1,500 | ~6,000 | **~10,000** | Comfortable |
| Typical UI (5 files) | ~2,500 | ~1,500 | ~5,000 | **~9,000** | Comfortable |
| Large backend (8 files) | ~2,500 | ~1,500 | ~10,000 | **~14,000** | Workable |
| Max module (8 files, large) | ~2,500 | ~1,500 | ~14,000 | **~18,000** | Stress-test boundary |

**Layer 2 — `max_files: 8` Governance Constraint**

Enforced in `modules.yaml` schema. `validate_documentation.py` fails validation if a module's `files` array exceeds `max_files`. Modules exceeding 8 files must be split by the developer during Mode A validation. This bounds the worst-case token load by governance design.

**Layer 3 — Agent Skills for On-Demand Charter Loading**

Agent Skills load contextually, not as a monolithic pre-load. The condensed charter is queried in Step 2 of Mode B — after `modules.yaml` has been read and `project_type` is known. This means the charter is loaded only when needed, in the correct variant, rather than loading all charters as ambient context.

**Layer 4 — `.github/copilot-instructions.md` as Fallback**

If hosted MCP context source configuration (Assumption 2) fails, the condensed charter (~3,000–4,000 characters) fits within `.github/copilot-instructions.md`'s practical limit. This is simultaneously the Assumption 2 fallback and the primary delivery mechanism for teams that do not configure hosted MCP context sources.

---

## Part 4: The `modules.yaml` Schema — Definitive Specification

This schema is the single most important new artifact in the entire implementation. `validate_documentation.py`, `consolidate.py`, and both Agent Skill modes all read from it.

```yaml
# ─────────────────────────────────────────────────────────────
# modules.yaml — AKR Module Manifest
# Schema version: v1.0.0
# ─────────────────────────────────────────────────────────────

# Project-level metadata
project:
  name: TrainingTracker.Api               # Repository / project display name
  layer: API                              # From akr-config-schema.json enum:
                                          # UI | API | Database | Integration |
                                          # Infrastructure | Full-Stack
  standards_version: v1.0.0              # Pin to core-akr-templates release tag
  minimum_standards_version: v1.0.0      # Enforced by validate_documentation.py
  compliance_mode: pilot                  # pilot | production
                                          # pilot:      --fail-on=never (warn only)
                                          # production: --fail-on=needs (blocks merge)

# Module groupings — API and UI projects
# Each module produces ONE Level 1 document covering all listed files
modules:
  - name: CourseDomain                   # PascalCase; becomes doc filename prefix
    project_type: api-backend            # api-backend | ui-component |
                                         # microservice | general
                                         # Maps to condensed charter selection
    feature: CourseCatalogManagement    # PascalCase key — must exactly match a key in tag-registry.json
                                        # Format enforced by tag-registry-schema.json patternProperties: ^[A-Z][a-zA-Z0-9]*$
                                        # Starts with uppercase letter, contains only letters and digits (no spaces, hyphens, underscores)
                                        # Valid examples: ApplicationEditor, UserAuthentication, DocumentGeneration, CourseCatalogManagement
                                        # Invalid: "Course Catalog Management", "course-catalog-management"
                                        # Schema validated by distribute-tag-registry.yml before distribution
                                        # Add missing entries to tag-registry.json before using in modules.yaml;
                                        # distribute-tag-registry.yml auto-distributes on commit
    domain: Backend                      # Logical domain grouping label
    layer: API                           # Architectural layer for this module
    max_files: 8                         # Override project default; hard ceiling
    files:
      - TrainingTracker.Api/Controllers/CoursesController.cs
      - TrainingTracker.Api/Domain/Services/ICourseService.cs
      - TrainingTracker.Api/Contracts/Courses/CourseDtos.cs
      - TrainingTracker.Api/Domain/Repositories/ICourseRepository.cs
      - TrainingTracker.Api/Infrastructure/Persistence/EfCourseRepository.cs
    doc_output: docs/modules/CourseDomain_doc.md
    status: draft                        # draft | review | approved | deprecated
    compliance_mode: pilot               # Module-level override; inherits project default

# Unassigned files — output of Mode A when agent cannot confidently group
unassigned:
  - path: TrainingTracker.Api/Infrastructure/Middleware/ExceptionHandler.cs
    reason: "Shared infrastructure — does not belong to a single domain module"

# Database objects — individual documentation units; never grouped with app code
database_objects:
  - name: training.Courses               # Schema-qualified object name
    type: table                          # table | view | procedure | function
    source: ssdt                         # ssdt | script | manual
    doc_output: docs/database/training_Courses_doc.md
    status: draft
```

### Schema Validation Rules for `validate_documentation.py` v1.0

> **Schema note (Review 6):** `modules-schema.json` does not yet exist in the repository. It is a Phase 1 deliverable. Until it exists, `validate_documentation.py` enforces the rules below programmatically. Once `modules-schema.json` is authored, the script can reference it directly for enum validation.

| Field | Rule | Error Behavior |
|---|---|---|
| `project.layer` | Must be in `["UI", "API", "Database", "Integration", "Infrastructure", "Full-Stack"]` (mirrors `akr-config-schema.json` `projectInfo.layer` enum; validated against `modules-schema.json` at runtime) | Fail with enum error |
| `project.standards_version` | Must be ≥ `minimum_standards_version` | Fail with version lag error |
| `modules[].project_type` | Must be in `[api-backend, ui-component, microservice, general]` | Fail with unknown type error |
| `modules[].feature` | Must exactly match a PascalCase key in `tag-registry.json` (e.g., `CourseCatalogManagement`). Synonym lookup optional but adds complexity. Missing entries must be added to `tag-registry.json` before use. | Fail with unregistered feature error |
| `modules[].files` length | Must not exceed `max_files` (default: 8) | Fail with module size error |
| `modules[].doc_output` | Must not be used by more than one module | Fail with duplicate output error |
| `database_objects[].type` | Must be in `[table, view, procedure, function]` | Fail with unknown type error |
| `project.compliance_mode` | Must be `pilot` or `production` | Fail with invalid mode error |

**`project_type` in YAML front matter (Review 6 addition):** The existing `akr-config-schema.json` `validation.tagValidation.requiredTags` defaults to `["feature", "domain", "layer"]`. It does **not** include `project_type`. Adding `project_type` as a required front matter field in module docs is a new requirement that extends the existing tag validation contract. Phase 1 must update `akr-config-schema.json` to add `project_type` to `requiredTags` for MODULE-type documents (as a conditional requirement based on doc type).

---

## Part 5: The Agent Skill — Three-Mode Specification

The Agent Skill is the primary workflow encoding mechanism. A single `SKILL.md` works across VS Code agent mode, the Copilot coding agent, and the Copilot CLI. Mode A (also referred to as the **DocumentPlanner** step) must precede Mode B, and Mode C handles interactive HITL completion for unresolved `❓` sections in existing drafts.

**Reliability context (Review 9):** Agent Skills are invoked by the LLM on an intent-matching basis. Copilot (GPT-4o) can respond to a documentation request *without* loading the skill, and can execute the skill *without* completing all steps - both silently, with no error. The three-layer reliability stack documented in Part 16 addresses this directly. The `SKILL.md` specification in this section should be read alongside Part 16, which defines the required frontmatter properties, invocation contract, and in-document proof-of-execution that together make the skill enforceable rather than advisory.

**LLM-dependent execution quality (Review 9):** Skill execution quality varies by underlying model. The `akr-docs` skill is optimized for and benchmarked against **Claude Sonnet 4.6**. When running through GitHub Copilot (GPT-4o default), expect lower first-run pass rates, particularly for Mode B on large modules (>6 files). See `SKILL-COMPAT.md` for the full model compatibility matrix and per-model workarounds. The CI gate (`validate_documentation.py`) validates output regardless of which model ran the skill - it is the model-agnostic enforcement layer.

```markdown
# .github/skills/akr-docs/SKILL.md

---
name: akr-docs
description: Propose module groupings and generate module documentation following
             AKR templates, charters, and validation rules. Three modes: Mode A
             (DocumentPlanner grouping proposal), Mode B (documentation generation),
             and Mode C (interactive HITL completion for unresolved ❓ sections).
---

# AKR Documentation Workflow

## Mode A — Propose Module Groupings
## (Run first on any project that does not yet have an approved modules.yaml)

When asked to "propose module groupings", "initialize modules.yaml", or
"scan project for documentation modules":

1. Check whether modules.yaml exists in the project root.
   If it exists and has no modules with status: draft → redirect to Mode B.

2. Scan all source files by directory path and filename.
   Group files by the dominant domain noun in their path/name
   (e.g., Course, Enrollment, User, Training).

3. For each domain group, identify the following file roles:
   - Controller (HTTP entry point)
   - Service interface (IXxxService.cs)
   - Service implementation (XxxService.cs, if present)
   - Repository interface (IXxxRepository.cs)
   - Repository implementation (EfXxxRepository.cs, etc.)
   - DTOs / Contracts (XxxDtos.cs, XxxRequests.cs, XxxResponses.cs)
   For UI projects, identify:
   - Page component (XxxPage.tsx)
   - Sub-components (XxxList.tsx, XxxForm.tsx, XxxCard.tsx)
   - Custom hooks (useXxx.ts)
   - Type definitions (xxxTypes.ts, xxxInterfaces.ts)

4. Mark all database files (*.sql, SSDT project files, migration scripts,
   stored procedures) as database_objects — never group with application code.

5. Files that cannot be confidently assigned to a domain group → add to
   unassigned[] with a reason string.

6. Apply project_type based on project structure:
   - .cs Controller + Service + Repository pattern → api-backend
   - .tsx/.ts component + hook + types pattern → ui-component
   - Mixed patterns or orchestration services → microservice
   - No clear pattern → general

7. Write draft modules.yaml to project root.
   Set status: draft on all modules and unassigned items.

8. Open a draft PR titled: "docs: propose module groupings for [project name]"
   Include PR checklist:
   - [ ] All module groupings reviewed for semantic accuracy
   - [ ] Module names reflect domain language (not file names)
   - [ ] No module exceeds max_files: 8
   - [ ] Misplaced files reassigned to correct module
   - [ ] Shared/infrastructure files correctly placed in unassigned[]
   - [ ] All database objects identified and typed correctly
   - [ ] modules.yaml approved before documentation generation begins

---

## Mode B — Generate Module Documentation
## (Run only after modules.yaml is approved — status on target module is not draft)

When asked to "generate documentation for [ModuleName]" or
"document the [ModuleName] module":

1. Read modules.yaml from the project root.
   Find the module matching the requested name.
   If status is draft → stop and instruct developer to complete Mode A first.
   Load: file list, project_type, feature, doc_output path.

2. Load the condensed charter from copilot-instructions/ based on project_type:
   - api-backend     → copilot-instructions/backend-service.instructions.md
   - ui-component    → copilot-instructions/ui-component.instructions.md
   - microservice    → copilot-instructions/backend-service.instructions.md
   - general         → copilot-instructions/backend-service.instructions.md
   Do not load the full charter from charters/ — condensed only.

3. Read all source files listed in the module's files[] array.
   Do not read files outside the files[] list.

4. Generate the module documentation using the appropriate base template:
   - api-backend / microservice → lean_baseline_service_template.md (module variant)
   - ui-component               → ui_component_template.md (module variant)
   Apply these rules during generation:
   - Mark AI-inferred content: 🤖
   - Mark sections requiring human input: ❓
   - Module Files section: list all files with their role
   - Operations Map: cover ALL operations across all files in the module
   - Architecture diagram: text-based (no Mermaid); show full stack
     Controller → Service → Repository → DB table
   - Business Rules: include Why It Exists and Since When columns
   - Data Operations: cover all reads and writes across all files
   - Questions & Gaps: list all inferred assumptions needing confirmation

5. Run validate_documentation.py against the generated draft.
   Pass the --module-name flag so the script applies module-level section rules.
   Resolve or mark DEFERRED any validation failures before continuing.

6. Write the draft to the doc_output path on a new feature branch.
   Branch name: docs/{module-name}-documentation

7. Open a draft PR titled: "docs: [ModuleName] module documentation"
   Include PR checklist:
   - [ ] Module Files section lists all files with correct roles
   - [ ] All ❓ sections reviewed; filled or marked DEFERRED with justification
   - [ ] Business Rules table complete including Why It Exists column
   - [ ] Data Operations section covers all reads and writes
   - [ ] Questions & Gaps populated with open items
   - [ ] validate_documentation.py passes with zero errors
  - [ ] akr-generated metadata header present at top of document
   - [ ] CODEOWNERS notified for review

8. Write the akr-generated metadata header block to the TOP of the output file
  (this step is required - do not skip; validate_documentation.py checks for it):
  <!-- akr-generated
  skill: akr-docs
  skill-version: {SKILL_VERSION from header}
  mode: B
  template: {template used}
  charter: {condensed charter filename}
  modules-yaml-status: approved
  steps-completed: 1,2,3,4,5,6,7,8
  generated-at: {ISO 8601 timestamp}
  -->

---

## Mode C — Interactive HITL Completion for Existing Drafts
## (Run when a document already exists and has unresolved ❓ sections)

When asked to "review unresolved questions", "walk me through ❓ sections", or
"finish HITL review for [DocName]":

1. Read the existing documentation file and enumerate unresolved `❓` markers.
  Group them by section and priority (critical first when in `production` mode).

2. Start an interactive pass in-editor:
  - Present one `❓` item at a time with local section context
  - Ask targeted clarification questions
  - Propose replacement text options grounded in code evidence

3. Apply accepted edits immediately to the document.
  - Replace resolved `❓` markers with finalized content
  - Keep unresolved items marked as `DEFERRED` with rationale and owner

4. Re-run validation checks after each section or batch:
  - `validate_documentation.py` for structural and marker policy
  - Vale checks for prose quality (if configured in repo)

5. Summarize completion status at the end:
  - Total `❓` resolved
  - Remaining `DEFERRED` items
  - Any blockers requiring domain-owner input

6. Open/update draft PR with a HITL completion checklist:
  - [ ] All critical `❓` resolved or explicitly `DEFERRED`
  - [ ] Deferred items have owner + follow-up trigger
  - [ ] Validator passes for current compliance mode
  - [ ] Reviewer sign-off requested
```

### Skill Reliability Requirements (Review 9)

The SKILL.md specification above encodes the *workflow*. The following requirements ensure the workflow is **actually executed** - not silently bypassed or incompletely run. These requirements are Part 16 items translated into authoring obligations.

#### Required SKILL.md Frontmatter

The frontmatter block must appear *above* the `<!-- SKILL_VERSION -->` comment as the first content in the file:

```yaml
---
name: akr-docs
description: >
  Generate AKR module documentation following charters and templates.
  Invoke explicitly via /akr-docs [mode-a | mode-b | mode-c] [target].
disable-model-invocation: true
optimized-for: claude-sonnet-4-6
tested-on:
  - claude-sonnet-4-6   # ✅ pass rate ≥90%
  - gpt-4o              # ⚠️ ~75%, Mode B truncation on large modules
user-invocable: true
skill-version: 1.0.0
---
```

**`disable-model-invocation: true`** prevents Copilot from auto-loading the skill based on intent matching. Without this, the skill may not load at all on ambiguous requests, producing responses that look correct but were generated entirely from the model's training data - with no charter, no template, and no compliance with the AKR governance contract.

#### Required Self-Reporting Block (First SKILL Body Instruction)

The first instruction in the SKILL body (after the frontmatter and version comment) must be:

```
CRITICAL: When this skill is loaded, begin EVERY response with the following
confirmation block. Do not skip this under any circumstances.

✅ akr-docs INVOKED AND STEPS EXECUTED
Steps followed: 1. [first step description] — completed | 2. [second step] — completed | ...
```

This gives the developer immediate in-session confirmation that the skill loaded and ran. Its absence in a response is an early warning that the skill was not invoked - allowing the developer to retry with an explicit `/akr-docs` command before a PR is opened.

#### Companion File: `SKILL-COMPAT.md`

A companion `SKILL-COMPAT.md` must be maintained alongside `SKILL.md` at `.github/skills/akr-docs/SKILL-COMPAT.md`. It records:

- Model compatibility matrix (pass rates per eval case per model, updated from `evals/benchmark.json` after each eval run)
- Known model-specific failure modes with descriptions
- Recommended workaround prompts per model
- Re-evaluation policy: *"Re-run evals after any SKILL.md change or Copilot model update."*

This file is distributed to registered repositories alongside `SKILL.md` via `distribute-skill.yml`.

---

## Part 6: `validate_documentation.py` — Definitive v1.0 Scope

This is the most consequential scoping decision in Phase 1. The module architecture materially expanded v1.0 scope beyond what earlier analyses estimated.

### What v1.0 Must Do (Non-Negotiable)

The script must distinguish module documents from database object documents before applying any section rules. Without this distinction, Vale and section-presence checks fire false positives on module docs that correctly omit single-service sections.

```
validate_documentation.py --file <path> [--module-name <name>] [--fail-on never|needs|all]

Execution flow:
1. Check whether modules.yaml exists in project root.
   If absent → warn and skip module-type-aware validation; apply generic rules only.
   (Fallback behavior: do not fail hard on missing modules.yaml in v1.0)

2. If modules.yaml exists → load it (pyyaml, declared dependency).
   Determine doc type for the file being validated:
   - If file path matches a modules[].doc_output → type = MODULE, load module metadata
   - If file path matches database_objects[].doc_output → type = DB_OBJECT
   - If no match → type = UNKNOWN, apply generic rules

3. Validate modules.yaml itself (separate validation pass):
   - project.layer in akr-config-schema.json enum
   - project.standards_version >= minimum_standards_version
   - Each module: project_type in allowed values
   - Each module: feature exists in tag-registry.json
   - Each module: files count <= max_files
   - No duplicate doc_output paths

4. Apply section rules based on doc type:
   MODULE docs require:
     - Module Files (list of all files with roles)
     - Operations Map (all operations across all files)
     - Architecture Overview (full-stack text diagram)
     - Business Rules (with Why It Exists + Since When columns)
     - Data Operations (all reads and writes)
     - YAML front matter with: feature, layer, project_type, status
     - <!-- akr-generated --> metadata header block at document top
       (absence → FAIL with: "AKR metadata header missing — skill may not
       have been properly invoked. Re-run using /akr-docs mode-b [module].")

   DB_OBJECT docs require:
     - Object Definition (schema, columns/parameters)
     - Relationships and Dependencies
     - Usage Patterns
     - YAML front matter with: object_type, source

   UNKNOWN docs:
     - Apply generic required sections from lean_baseline_service_template.md
     - Warn that doc is not registered in modules.yaml

5. Check transparency markers:
   - Count unresolved ❓ markers
   - Fail on ❓ if compliance_mode = production
   - Warn on ❓ if compliance_mode = pilot
   - DEFERRED markers with justification text → always pass
   - 🤖 markers → informational only, do not fail

6. Apply --fail-on logic:
   --fail-on=never:  exit 0 always; emit warnings to stdout
   --fail-on=needs:  exit 1 on unresolved ❓ in production mode; else exit 0
   --fail-on=all:    exit 1 on any validation failure

7. Emit structured output:
   PASS/FAIL/WARN per check; summary count; list of specific failures with line refs
```

### Explicit Dependencies

- `pyyaml` — YAML front matter and `modules.yaml` parsing (explicit; not optional)
- `Vale` — prose quality rules (subprocess call; installed separately)
- Python 3.9+ — standard library only beyond `pyyaml` and Vale

### What Defers to v1.1

| Feature | Reason for Deferral |
|---|---|
| `--auto-fix` mode (insert missing sections) | Requires template-aware content generation; too complex for v1.0 |
| `--check-sync` mode (detect code changes without doc updates) | Requires file diff integration; Phase 2 feature |
| `--tier` completeness scoring | Threshold logic can be added after v1.0 section checks are stable |
| `feature-registry.yaml` cross-repo validation | Phase 4 dependency; `tag-registry.json` local validation is sufficient for v1.0 |
| Full Vale subprocess integration | Vale can run as a separate CI step in v1.0; tight integration in v1.1 |
| Model-specific pass-rate adaptive logic | Detecting which model ran the skill and adjusting validation thresholds accordingly - `benchmark.json` data provides the inputs but the logic is v1.1 scope; v1.0 applies uniform rules regardless of model |

The `<!-- akr-generated -->` metadata header check is explicitly **v1.0 scope** - it is not deferred. It is the in-document enforcement contract for the three-layer reliability stack and must be present before the pilot begins.

### Realistic Scope

Based on the full v1.0 feature set: **500–650 lines** with `pyyaml` as an explicit dependency. The prior "~300 lines, no dependencies" estimate was based on a pre-module-architecture scope. Plan Phase 1 accordingly — this is 1–2 weeks of focused development and testing, not a side deliverable.

### Testing Requirements

Port structural assertions from `akr-mcp-server/tests/test_validation_library.py` as the test baseline. `validate_documentation.py` should pass analogous tests for:
- Module doc with all required sections → PASS
- Module doc missing Operations Map → FAIL with correct message
- Module doc with unresolved `❓` in production mode → FAIL
- DB object doc missing Relationships section → FAIL
- `modules.yaml` with module exceeding `max_files` → FAIL
- `modules.yaml` with unknown `project_type` → FAIL
- `modules.yaml` absent from project → WARN, do not fail

---

## Part 7: `copilot-instructions.md` — Required Full Replacement

The existing `.akr/standards/copilot-instructions.md` is not a partial update. Direct file inspection (Review 7) confirms it is approximately 90%+ MCP-server-specific content that is broken by design after the archive. The rewrite is effectively a full document replacement. Estimate: **3–4 hours of focused authoring**, not a quick edit.

### What Must Be Removed Entirely (Six Sections)

**1. Slash-Commands section (~52 lines):** Every slash command is an MCP server invocation:
`/docs.generate`, `/docs.interview`, `/docs.update`, `/docs.update.api`, `/docs.update.architecture`, `/docs.my-role`, `/docs.set-role`, `/docs.health-check`, `/docs.update-templates`. All broken after archive. Remove the entire section.

**Purpose correction for `/docs.interview`:** its intended purpose was not pre-generation module confirmation. It was an interactive HITL flow to guide developers through filling `❓` sections in existing documents. In the new architecture, that capability is replaced by Agent Skill **Mode C**.

**2. Code Analysis Capabilities section (lines 183–205):** Explicitly instructs Copilot to "leverage Tree-sitter AST parsing" for all project types. Replace wholesale with Copilot-native code analysis guidance (read source files, follow dependency graph, infer from naming conventions).

**3. Repository Structure Requirements section (lines 104–121):**
- Vale installation path `.vale/styles/AKR/` conflicts with the new `validation/vale-rules/` migration target — must update
- Output directories `docs/components/`, `docs/services/`, `docs/architecture/` must become `docs/modules/`, `docs/database/`, `docs/features/` per the three-tier hierarchy

**4. YAML front matter example (lines 128–144):** Uses `component_type`, `technologies`, `business_domain`, `priority`, `last_updated` — none of which are in the `modules.yaml` schema's required fields (`feature`, `layer`, `project_type`, `status`, `compliance_mode`). Replace with module-level front matter example.

**5. Template selection logic:** Current logic selects templates based on a single file's complexity. This is structurally wrong under the module architecture. See new template selection table below.

**6. Support and Troubleshooting section (lines 300–318):** References `.vscode/mcp.json`, `~/.akr/templates/`, and `python scripts/validate-docs.py` (old script name — not `validate_documentation.py`). All three reference the archived MCP server. Remove entirely.

### What Must Be Retained (Three Elements Only)

- **Core Principles section** — transparency markers (`🤖`, `❓`, `DEFERRED`), HITL principles — retain with modifications to align marker semantics with `modules.yaml` `compliance_mode` behavior
- **Completeness scoring formula** — retain as-is
- **Vale quality gates reference** — retain, updating the Vale config path from `.akr/.vale.ini` to `validation/.vale.ini`

### New Template Selection Table (Replacement Content)

### New Template Selection Table

| `project_type` | Base Template | Condensed Charter | Notes |
|---|---|---|---|
| `api-backend` | `lean_baseline_service_template.md` (module variant) | `backend-service.instructions.md` | Covers Controller + Service + Repository + DTOs |
| `ui-component` | `ui_component_template.md` (module variant) | `ui-component.instructions.md` | Covers Page + sub-components + hooks + types |
| `microservice` | `lean_baseline_service_template.md` (module variant) | `backend-service.instructions.md` | Service-to-service pattern; no controller layer |
| `general` | `lean_baseline_service_template.md` | `backend-service.instructions.md` | Fallback; apply judgment |
| `table` (DB object) | `table_doc_template.md` | `database.instructions.md` | Individual object; no grouping |
| `view` (DB object) | `table_doc_template.md` | `database.instructions.md` | Individual object |
| `procedure` (DB object) | `embedded_database_template.md` | `database.instructions.md` | Individual object |

### What Else Must Be Added (New Content)

- Module grouping principles (domain noun, dependency graph, DTO alignment, interface/implementation pairs)
- `project_type` → condensed charter → template mapping table (below)
- `modules.yaml` front matter field reference
- Three-mode Agent Skill invocation guidance (when to use Mode A, Mode B, and Mode C)

### Authoring Note

The replacement document should be approximately 150–200 lines. The current file is considerably longer because of MCP-server-specific verbosity. The goal is a concise, Copilot-native reference that a developer reads once during onboarding — not an exhaustive manual.

---

## Part 8: `layer` vs. `project_type` — Definitive Distinction

This was conflated in prior analyses and is now definitively clarified. An important schema correction from Review 6 also applies here.

| Field | Level | Values | Source | Purpose |
|---|---|---|---|---|
| `layer` | **Project-level** in `modules.yaml project:` section | `UI`, `API`, `Database`, `Integration`, `Infrastructure`, `Full-Stack` | Enum values sourced from `akr-config-schema.json`'s `projectInfo.layer` — **but `modules.yaml` is a new artifact validated by `modules-schema.json`, not by `akr-config-schema.json` directly** | Describes the architectural tier of the whole repository |
| `project_type` | **Module-level** in `modules.yaml modules[]:` entries | `api-backend`, `ui-component`, `microservice`, `general` | Defined in new `modules-schema.json` | Drives charter selection and template selection for each documentation unit |

A repository with `layer: API` (the whole project is an API) can contain modules of `project_type: api-backend` (standard CRUD modules) and `project_type: microservice` (lightweight orchestration services). A repository with `layer: UI` contains modules of `project_type: ui-component`.

**Critical schema correction (Review 6):** `akr-config-schema.json` is the schema for `.akr-config.json` — a separate project-level configuration object covering `projectInfo`, `documentation`, `crossRepository`, `tags`, `validation`, `humanInput`, and `monitoring`. It is **not** a schema for `modules.yaml`. The `layer` enum lives inside `projectInfo.layer` within that config schema and is the source of valid values, but `modules.yaml` validation must reference the new `modules-schema.json`, not `akr-config-schema.json` directly.

**Consequence for implementation:** `modules-schema.json` does not yet exist in the repository. It is a Phase 1 deliverable. `validate_documentation.py` validates `layer` against the enum values defined in `modules-schema.json` (which mirrors `akr-config-schema.json`'s `projectInfo.layer` enum) and `project_type` against the separate allowed values list in that same new schema. They are not the same validation rule, and neither references `akr-config-schema.json` at runtime.

---

## Part 9: Phase 4 `consolidate.py` — Revised Data Contract

The module architecture changes how `consolidate.py` reads its inputs. Review 6's schema inspection also reveals that the cross-repository configuration is split across two schemas with overlapping responsibilities — both must be understood before Phase 4 implementation begins.

### What Changes From Prior Analysis

**Before module architecture:** `consolidate.py` was expected to read individual component docs (`CourseService_doc.md`, `CoursesController_doc.md`) as separate inputs for the `FOR_EACH_API_COMPONENT` loop.

**After module architecture:** `consolidate.py` reads module docs (`CourseDomain_doc.md`) as atomic units. `CourseDomain_doc.md` already covers the controller, service, repository, and DTOs — iterating over individual component files is no longer correct.

### The Dual Cross-Repository Configuration — Schema Correction (Review 6)

`consolidation-config-schema.json` defines the **job runner** configuration: which repositories to clone (Git URLs, branches, credentials), caching, parallel processing limits, webhook triggers, and output format. Its current `docsPath` + `includePatterns` glob assumes individual component docs, not `modules.yaml`-driven module docs. It has **no concept of `modules.yaml`**.

`akr-config-schema.json` defines **per-project participation**: the `crossRepository` section (lines 155–316) specifies `consolidationRepo`, `registryUrl`, `publishFeatureDocs`, `relatedRepositories[]`, `syncSchedule`, and a dual `outputs[]` array referencing both `feature-consolidated.md` and `feature-testing-consolidated.md`. This is the per-project opt-in contract.

**Which config drives which decision:**

| Config File | Drives | Read By |
|---|---|---|
| `akr-config-schema.json` (`crossRepository` section) | **Participation**: does this repo contribute? Which consolidation repo? Which related repos? | `consolidate.py` at participation discovery time |
| `consolidation-config-schema.json` | **Execution**: which repos to clone, how to discover docs, output format, parallelism | `consolidate.py` at job execution time |

**Phase 4 schema evolution:** `consolidation-config-schema.json` already defines top-level path fields (`tagRegistryPath`, `templatePath`, `outputDir`, `cacheDir`). Adding `modulesManifestPath` (defaulting to `modules.yaml`) follows this existing pattern exactly — it is a single additional field consistent with the established design, not a structural change. `consolidate.py` reads `modules.yaml` first when `modulesManifestPath` is present; falls back to `docs/**/*.md` glob scan when absent (backward compatibility for repositories not yet onboarded).

**Note on `repositories[].layer` enum:** The current `consolidation-config-schema.json` `repositories[].layer` enum is `["UI", "API", "Database", "Integration", "Infrastructure"]` — it does **not** include `"Full-Stack"`. This differs from `akr-config-schema.json`'s `projectInfo.layer` which does include `"Full-Stack"`. Either add `"Full-Stack"` to the consolidation schema's layer enum in Phase 4, or document that `Full-Stack` repositories must self-identify a primary layer for consolidation participation. The `modules.yaml` schema's `project.layer` should match `akr-config-schema.json` (includes `Full-Stack`) since it describes a single repository's architectural tier, not a repository's participation role in a consolidation job.

### `warnOnMissingLayers` — Already Defined, Not New Logic (Review 6)

`consolidation-config-schema.json` already defines `validation.warnOnMissingLayers: true` — it warns when a feature doc is missing UI, API, or DB layer representation. `consolidate.py` reads this existing flag; the missing-layer warning is **not new logic to implement** from scratch.

### Revised Input Contract

```python
# consolidate.py execution sequence:
# 1. Read consolidation-config-schema.json for job execution config
#    - repositories[] to clone
#    - modulesManifestPath (default: modules.yaml) — NEW field
#    - docsPath fallback if modules.yaml absent
#    - validation.warnOnMissingLayers (existing flag — read, don't implement)
#
# 2. For each repository, read akr-config-schema.json crossRepository section
#    - Confirm publishFeatureDocs: true (opt-in)
#    - Read relatedRepositories[] for cross-repo dependency mapping
#
# 3. Read modules.yaml from each participating repository
#    Input sources per feature_tag:
#    FOR_EACH_API_COMPONENT  → modules[] where feature matches feature_tag
#                              AND project_type in [api-backend, microservice]
#    FOR_EACH_UI_COMPONENT   → modules[] where feature matches feature_tag
#                              AND project_type = ui-component
#    FOR_EACH_DB_COMPONENT   → database_objects[] where feature matches feature_tag
#                              (database objects are still individual units)
#
# 4. Fill feature-consolidated.md template {FOR_EACH_X}...{END_FOR_EACH} syntax
#    No AI invocation from Actions
```

### Design Principle Confirmed

`consolidate.py` is deterministic Python — no AI invocation from GitHub Actions. The non-deterministic part (synthesizing a coherent business narrative) is done by the Product Owner with Copilot agent mode assistance on the structured draft. This eliminates Assumption 4 (Copilot-from-Actions) entirely.

---

## Part 10: AI Tooling — Final Consolidated Evaluation

### Architecture Diagram & Narrative: Ideal End-State Architecture

**[View Interactive Architecture Diagram](akr_architecture_diagram.html)** 

The diagram above illustrates how all components connect in the fully realised system. Five conceptual zones are shown, each with a distinct responsibility boundary.

**Standards Layer — `core-akr-templates` as GitHub Hosted MCP Context Source**

The repository serves as the single source of truth for all governance artefacts. When configured as a GitHub Hosted MCP Context Source (subject to pre-pilot Test 2 validation at your Copilot Business plan tier), its contents — condensed charters, templates, the validation script, and `TEMPLATE_MANIFEST.json` — are made available to Copilot Chat and the coding agent without any local server or custom infrastructure. Full charters remain in `charters/` as reference documentation; only the condensed versions (~2,500 tokens each) are loaded as active context. This is the architectural answer to the context saturation problem: the governance layer is in the repository, not in a running process.

**Developer Workflow Layer — Agent Skills + Copilot Surfaces**

The Agent Skill (`SKILL.md`) is authored once and auto-loads across three surfaces simultaneously: VS Code agent mode (developer-present, interactive), the Copilot coding agent (asynchronous, issue-to-PR), and the Copilot CLI. Mode A proposes module groupings and writes a draft `modules.yaml`; Mode B generates module documentation after groupings are human-validated. The `project_type` field in `modules.yaml` drives charter selection — the skill reads it and loads the correct condensed charter in step 2 of Mode B. `.github/copilot-instructions.md` carries global style rules and acts as the Assumption 2 fallback if hosted MCP context sources are unavailable at the current plan tier.

**CI / Governance Layer — GitHub Actions**

`validate_documentation.py` runs in GitHub Actions on every PR that touches `docs/**/*.md`. It reads `modules.yaml` to determine document type (module doc vs. database object doc) and applies the correct required section rules accordingly — this module-type awareness is what prevents false positives on Level 1 documents. Vale prose rules enforce language quality independently. `consolidate.py` runs as a deterministic Python aggregator in Phase 4, matching module docs by `feature_tag` to produce Level 3 feature consolidations with no AI invocation from Actions.

**Cross-Functional Review Layer — Copilot Studio in Teams (Phase 3+)**

When a PR is labelled `docs-review-required`, a Copilot Studio agent in Microsoft Teams surfaces the PR summary to the relevant non-developer stakeholders — product owner, QA lead, security reviewer — and gates merge on their approval. This layer exists specifically for contributors who do not work in GitHub or VS Code. It is conditional on confirmed Microsoft 365 Copilot licensing and a modelled credit budget, and should not be planned before those prerequisites are met.

**Three-Tier Documentation Output**

The diagram also shows the three documentation levels as outputs, not as system components. Level 1 (module docs) is produced by the coding agent or agent mode via the Agent Skill. Level 2 (database object docs) follows the same workflow but uses individual object templates without grouping. Level 3 (feature consolidation docs) is produced by `consolidate.py` after Levels 1 and 2 are complete and tagged. No Level 3 output is possible until the lower levels are stable — the dependency direction is one-way.

**What Is Not in the Diagram**

The diagram shows the ideal end-state. Two components are conditional and explicitly noted in the footer: hosted MCP context source availability is subject to pre-pilot Test 2 validation, and the Copilot Studio layer requires M365 licensing confirmation. If hosted MCP is unavailable, `.github/copilot-instructions.md` with the condensed charter substitutes at zero additional cost. If Copilot Studio is unavailable, the HITL model operates with three levels rather than four — the CI gate and PR review remain fully effective without the Teams layer.

**Named Architectural Constraint: Zero Cloud Infrastructure, No Incremental Cost**

This program assumes no new cloud infrastructure and no incremental platform cost beyond existing Copilot seat entitlements and premium request consumption. Architecture decisions in all phases must be evaluated against this constraint; any proposal that introduces net-new cloud runtime must be justified by a documented failure at Phase 2.5.


### Tooling Architecture (Confirmed Across All Five Reviews)

```
┌───────────────────────────────────────────────────────────────┐
│  DEVELOPER WORKFLOW (IDE surface)                             │
│                                                               │
│  Agent Skills (SKILL.md)                                      │
│  → Encodes AKR procedure (Mode A + Mode B + Mode C)           │
│  → Invoked via /akr-docs slash command (not auto-discovery)   │
│  → disable-model-invocation: true in frontmatter (Review 9)   │
│  → Self-reporting block confirms invocation per response       │
│  → Mode B writes akr-generated metadata header (proof of       │
│    execution; checked by validate_documentation.py)            │
│  → Optimized for Claude Sonnet 4.6; GPT-4o ~75% pass rate     │
│  → SKILL-COMPAT.md tracks model compatibility matrix           │
│  → Free; no infrastructure; runs on existing Copilot seats   │
│                                                               │
│  Agent Session Hooks (.github/hooks/)                         │
│  → postToolUse: logs file writes to .akr/logs/ (audit trail)  │
│  → agentStop: auto-runs validate_documentation.py at end      │
│  → Layer 2 of three-layer reliability stack (Review 9)        │
│                                                               │
│  Copilot Agent Mode (interactive)                             │
│  → Developer-present confirm → generate flow                  │
│  → Uses Agent Skill automatically                             │
│                                                               │
│  Copilot Coding Agent (asynchronous)                          │
│  → Issue template → autonomous execution → draft PR           │
│  → Uses Agent Skill automatically                             │
│  → Context window advantage: multi-step task, not single load │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│  CI / GOVERNANCE (automated surface)                          │
│                                                               │
│  validate_documentation.py + Vale                             │
│  → Runs in GitHub Actions on docs/**/*.md PRs                 │
│  → Module-aware section validation                            │
│  → Hosted in core-akr-templates/scripts/                      │
│                                                               │
│  .akr/workflows/ (existing — migrate, not rebuild)            │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│  CROSS-FUNCTIONAL REVIEW (Teams surface — Phase 3+)           │
│                                                               │
│  Copilot Studio Doc Review Agent                              │
│  → Triggers on PR label only (not every PR)                   │
│  → Routes to: PM, QA lead, security reviewer                  │
│  → Prerequisite: M365 Copilot license confirmed               │
│  → Credit model: model before committing                      │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│  CONTEXT DELIVERY (standards surface)                         │
│                                                               │
│  Condensed charters in copilot-instructions/                  │
│  → ~2,500 tokens each (from ~11,000 token originals)          │
│  → Agent Skill loads per project_type on demand               │
│                                                               │
│  .github/copilot-instructions.md (per repository)             │
│  → Global style rules only (not procedures)                   │
│  → Carries condensed charter if hosted MCP unavailable        │
│  → Assumption 2 fallback                                      │
│                                                               │
│  GitHub Hosted MCP Context Sources                            │
│  → Loads core-akr-templates as ambient context                │
│  → Assumption 2: must be validated in Phase 0                 │
└───────────────────────────────────────────────────────────────┘
```

### Tooling Decisions Requiring No Further Analysis

| Decision | Verdict | Rationale |
|---|---|---|
| Archive `akr-mcp-server` immediately | ✅ Final | Zero server tests, zero adoption, Windows-only, version drift |
| Agent Skills as primary workflow encoding | ✅ Final | Cross-surface, free, single authoring effort |
| Copilot coding agent as Phase 2.5 | ✅ Final | Zero infrastructure; test-based acceptance criteria available |
| Zero cloud infrastructure / no incremental cost is a design constraint | ✅ Final | Existing tooling surfaces are sufficient for pilot and foundation phases; net-new cloud runtime requires explicit Phase 2.5 failure evidence |
| Charter compression before pre-pilot spike | ✅ Final | Guaranteed failure without it; not a risk to test |
| Phase 4 as deterministic Python + human refinement | ✅ Final | Eliminates unverified Assumption 4 |
| `project_type` and `layer` as separate fields | ✅ Final | Different concepts; different validation rules |
| `TEMPLATE_MANIFEST.json` narrowed to version registry | ✅ Final | Skill-template version coupling requires it; other roles deprecated |
| Phase 3 conditional on Phase 2.5 failure | ✅ Final | Cannot justify Azure Function without evidence coding agent is insufficient |
| Agent Skill reliability requires explicit enforcement, not intent-matching alone | ✅ Final (Review 9) | Three failure modes confirmed: silent non-invocation, partial execution, context saturation. Three-layer stack (frontmatter gate + session hooks + metadata header contract) is the resolution. CI gate is the model-agnostic backstop regardless of which surface ran the skill |

### Tooling Decisions Still Requiring Input

| Decision | Open Question | How to Resolve |
|---|---|---|
| Copilot Studio Doc Review agent | Does the org have M365 Copilot licenses? | Check licensing before Phase 3 planning |
| Premium request metering | What is the monthly allowance and overage rate? | Model before Phase 2.5; use GitHub billing dashboard |
| Copilot Enterprise Knowledge Base | Is tier upgrade planned or under consideration? | Strategic roadmap question; log for future |
| Remote MCP (HTTP + OAuth) | Is shared team access a Phase 3+ requirement? | Validate after pilot proves governance value |

---

## Part 11: Five Pre-Pilot Validation Tests — With Module-Architecture Updates

All five tests must pass (or have documented fallback architectures) before Phase 1 delivery work begins. Tests 1 and 3 now have updated acceptance criteria reflecting the module architecture.

| Test | What It Validates | Updated Acceptance Criteria | Fail Fallback |
|---|---|---|---|
| 1 — Code Analysis Capability | Copilot + condensed charter extracts module-level content correctly; skill invocation confirmed | Agent correctly groups 5 files into one CourseDomain doc; covers Controller + Service + Repository + DTOs in a single output; ≥90% section match across 3 runs; **self-reporting block present in all 3 runs**; **`<!-- akr-generated -->` metadata header present in output** (Review 9 additions — these are now required pass criteria, not optional observations) | Hybrid: retain `CodeAnalyzer` from `akr-mcp-server` for deterministic extraction; hosted MCP for governance |
| 2 — Context Source Configuration | `core-akr-templates` available as hosted MCP context source at current plan tier | Context source appears in Settings → Copilot → MCP; available in VS Code + Visual Studio; context pulled on new sessions | Use `.github/copilot-instructions.md` with condensed charter as primary delivery |
| 3 — Large Module Stress Test | Module with 8 files, 2,000+ LOC: no section truncation | All module-required sections present (Module Files, Operations Map, full-stack diagram, Business Rules, Data Operations); validate_documentation.py passes | `max_files: 8` enforced as governance ceiling; provide `max_files: 5` guidance for large-file modules |
| 4 — GitHub Actions Invocability | Whether Copilot can be invoked from Actions (Phase 4 automation) | Either: working Copilot-from-Actions mechanism documented, or Phase 4 deterministic aggregation design confirmed as sufficient | Phase 4 deterministic aggregation (already designed; this test confirms the fallback is the plan) |
| 5 — Data Governance / Compliance | Legal and security sign-off on Copilot processing org code | Written approval from governance and legal; Copilot data handling confirmed against org data residency requirements | Manual documentation with templates only; no AI generation assistance |

**Prerequisite before Test 1:** Backend condensed charter (`backend-service.instructions.md`) must exist at ~2,500 tokens. Test 1 is not interpretable without it.

---

## Part 12A: Schema Audit Findings — Four Corrections and Three Additions (Review 6)

Full inspection of `akr-config-schema.json` and `consolidation-config-schema.json` reveals seven items that affect implementation plan accuracy. None change the strategy; they change the accuracy of specific Phase 1 and Phase 4 tasks.

### Correction Summary

**C1 — `modules-schema.json` does not exist and must be authored in Phase 1.**
`akr-config-schema.json` is the schema for `.akr-config.json`, not for `modules.yaml`. `modules.yaml` is a new artifact with no existing schema. `validate_documentation.py` cannot reference an existing schema file for `layer` enum validation at runtime — it must reference the new `modules-schema.json` once that file is authored. Until then, enum values are enforced programmatically. Add "author `core-akr-templates/schemas/modules-schema.json`" as an explicit Phase 1 deliverable.

**C2 — `consolidation-config-schema.json` has no `modules.yaml` awareness and must be evolved in Phase 4.**
The current schema assumes `consolidate.py` scans `docs/**/*.md` by glob. `consolidate.py` now needs to read `modules.yaml` first. Phase 4 must add a `modulesManifestPath` field (defaulting to `modules.yaml`) to `consolidation-config-schema.json`. The existing `docsPath` + `includePatterns` remains as the fallback for repositories not yet onboarded to the module architecture.

**C3 — Cross-repository configuration is split across two schemas with overlapping responsibilities.**
`akr-config-schema.json`'s `crossRepository` section (lines 155–316) handles participation: which consolidation repo to publish to, which related repos contribute, sync schedule, and dual `outputs[]` referencing both `feature-consolidated.md` and `feature-testing-consolidated.md` with `sectionMapping`. `consolidation-config-schema.json` handles execution: repo cloning, auth, parallelism, output format. `consolidate.py` must read both. The implementation plan must document this split explicitly so the Phase 4 builder does not re-implement logic that already exists in `akr-config-schema.json`'s `sectionMapping`.

**C4 — `project_type` is not in the existing `requiredTags` contract.**
`akr-config-schema.json`'s `validation.tagValidation.requiredTags` defaults to `["feature", "domain", "layer"]`. It does not include `project_type`. Phase 1 must update this array to include `project_type` as a conditional required tag for MODULE-type documents.

### Addition Summary

**A1 — `humanInput` schema (lines 480–516 of `akr-config-schema.json`) maps directly to the ❓ marker HITL model.**
The schema defines `triggerMode` (`always`, `on-new-file`, `manual`), `priorityFilter` (`critical`, `important`, `optional`), and `defaultRole` with values `developer`, `technical_lead`, `product_owner`, `qa_tester`, `scrum_master`, `general`. These map cleanly to the four-level HITL model:

| `defaultRole` | Maps To |
|---|---|
| `technical_lead` | Level 1 grouping validation + Level 2 architecture review |
| `developer` | Level 2 content review (fills ❓ sections) |
| `product_owner` | Phase 4 narrative refinement |
| `qa_tester` | Copilot Studio Teams approval gate (Phase 3+) |

Phase 1 should cross-reference `humanInput.defaultRole` against the "who provides it" column in the adapted templates, so the two systems use consistent role vocabulary. `validate_documentation.py` can eventually read `humanInput.priorityFilter` to determine which ❓ markers are blocking (`critical`) vs. advisory (`optional`).

**A2 — `warnOnMissingLayers` is already defined in `consolidation-config-schema.json`.**
`consolidation-config-schema.json` at line 220 defines `validation.warnOnMissingLayers: true`. This is already the missing-layer governance rule. `consolidate.py` reads this existing flag and emits the warning based on it — this is not new logic to implement from scratch. Document it as reading an existing config field.

**A3 — `monitoring` schema feeds the Phase 0 cost baseline requirement.**
`akr-config-schema.json` at lines 518–545 defines a `monitoring` object with `trackMetrics: ["generation-time", "validation-results", "human-input-completion", "cross-repo-sync"]` and a `reportingEndpoint` URI. Enabling `monitoring: { enabled: true, trackMetrics: ["generation-time", "validation-results"] }` in the per-project `.akr-config.json` during Phase 0/2 pilot provides a documentation-layer signal of generation workflow usage. This is not a substitute for GitHub billing dashboard monitoring, but it provides a usage baseline that costs nothing to collect. Add to Phase 0: "Enable `monitoring` in pilot project's `.akr-config.json`; collect generation-time baseline across first 10 module documentation runs."

### Complete Schema Audit Impact Table

| Item | Type | Phase Affected | Implementation Plan Action |
|---|---|---|---|
| `modules-schema.json` does not exist | Correction | Phase 1 | Add "author `schemas/modules-schema.json`" as explicit deliverable |
| `consolidation-config-schema.json` has no `modules.yaml` awareness | Correction | Phase 4 | Add `modulesManifestPath` field; `consolidate.py` reads it first |
| Dual cross-repo config schemas overlap | Correction | Phase 4 design | Document: `akr-config-schema.json` drives participation; `consolidation-config-schema.json` drives execution |
| `project_type` not in existing `requiredTags` | Correction | Phase 1 | Update `akr-config-schema.json` `requiredTags` to include `project_type` (conditional) |
| `humanInput` schema maps to ❓ HITL model | Addition | Phase 1 alignment | Cross-reference `defaultRole` enum against template "who provides it" column |
| `warnOnMissingLayers` already defined | Addition | Phase 4 scope | `consolidate.py` reads existing flag; not new logic |
| `monitoring` schema exists for cost baseline | Addition | Phase 0 | Enable in pilot `.akr-config.json`; collect generation-time baseline |
| `tag-registry.json` uses PascalCase keys; `modules.yaml` example used free text | Correction (Review 7) | Phase 0 + Phase 1 | Update `feature` field to PascalCase; add `CourseCatalogManagement` entry to `tag-registry.json` in Phase 0 |

---

## Part 12B: Complete Gap Inventory — All Reviews Consolidated

**🔴 CRITICAL FINDING — Added After Schema Audit:**
**`validate_documentation.py` does not exist in the repository.** The workflow at `.akr/workflows/validate-documentation.yml` attempts to download the script from `https://raw.githubusercontent.com/reyesmelvinr-emr/core-akr-templates/main/scripts/validate_documentation.py`, but this path does not exist and the download returns a 404. The script must be **created from scratch** as a Phase 1 deliverable, separate from the workflow adaptation task. The script location shall be `.akr/scripts/validate_documentation.py` in `core-akr-templates`, keeping it inside the `.akr/` governance subtree. During workflow adaptation, the download URL must be corrected from the broken path to: `https://raw.githubusercontent.com/reyesmelvinr-emr/core-akr-templates/main/.akr/scripts/validate_documentation.py`. This is two Phase 1 deliverables: (1) **Build new** `validate_documentation.py` (~500–650 lines) + (2) **Adapt existing** `validate-documentation.yml` (five targeted changes, including fixing the URL).

| Gap | Source | Severity | Resolution |
|---|---|---|---|
| Charter compression not done | Review 3 (quantified) | 🔴 Blocking | Phase 0 first deliverable |
| `validate_documentation.py` does not exist; must be created from scratch | Final file inspection | 🔴 Blocking for Phase 1 | Author `.akr/scripts/validate_documentation.py` in core-akr-templates (~500–650 lines); correct workflow download URL from broken path to `https://raw.githubusercontent.com/reyesmelvinr-emr/core-akr-templates/main/.akr/scripts/validate_documentation.py` |
| Module-type awareness in validator | Module architecture | 🔴 Blocking for v1.0 | Read `modules.yaml`; apply different section rules per doc type |
| `copilot-instructions.md` needs module-centric rewrite | Module architecture | 🔴 Blocking | Not a text update — conceptual rewrite of template selection logic |
| `layer` vs. `project_type` conflation | Module architecture | 🟡 High | Separate fields; separate validation rules |
| `consolidate.py` input contract change | Module architecture | 🟡 High | Module docs as atomic units for API/UI layers |
| Agent Skill has three modes (not one) | Workflow clarification + module architecture | 🟡 High | Mode A (DocumentPlanner grouping) must precede Mode B (generation); Mode C handles interactive `❓` completion for existing drafts |
| Mode A sequencing not enforced | Module architecture | 🟡 High | Skill checks `modules.yaml` status before Mode B |
| Pre-pilot assumptions are load-bearing | Review 1 + all | 🟡 High | Blocking gate before Phase 1 |
| Charter selection logic undefined | Review 3 + Module arch | 🟡 High | `project_type` field + Agent Skill step 2 |
| `TEMPLATE_MANIFEST.json` disposition unresolved | Review 3 / M365 | 🟡 High | Narrow to version registry; deprecate other roles |
| `--fail-on` graduation criteria undefined | Review 1 + 2 | 🟡 High | `compliance_mode` field in `modules.yaml`; formal approval process |
| Premium request metering unmodeled | Review 4 (M365) | 🟡 High | Model before Phase 2.5; use GitHub billing dashboard |
| `validate_doc.py` cross-platform untested | Review 1 + 3 | 🟡 High | Test Ubuntu + macOS + Windows in Phase 1 |
| Standards version drift unmitigated | Review 1 | 🟡 High | `minimum_standards_version` in validator |
| Azure Function breaks zero-infra premise | Review 1 + 2 | 🟡 Medium | Phase 3 conditional on Phase 2.5 failure |
| Phase 4 Assumption 4 (Copilot from Actions) | All reviews | 🟡 Medium | Deterministic aggregation design resolves |
| `.akr/workflows/` not audited | Review 3 | 🟡 Medium | Audit in Phase 0; migrate rather than rebuild |
| Gitmodule paths invisible to `git grep` | Review 3 | 🟡 Medium | Extended inventory in Phase 0 |
| `modules.yaml` absent: fallback behavior | Module architecture | 🟡 Medium | Warn + skip module-type rules; do not fail hard |
| `test_pipeline_e2e.py` not reused as criteria | Review 3 | 🟠 Medium | Port as Phase 2.5 acceptance criteria |
| `unassigned[]` handling in validator | Module architecture | 🟠 Medium | Warn only; human reviews during Mode A PR |
| Copilot Studio licensing not confirmed | Review 4 (M365) | 🟠 Medium | Check M365 licenses before Phase 3 planning |
| `feature-consolidated.md` `FOR_EACH_*` contract | Module architecture | 🟠 Medium | Document mapping: module docs as loop inputs for API/UI |
| Vale migration complexity understated | Review 2 + 3 | 🟠 Medium | Audit `.akr/vale-rules/` depth; run Vale separately in v1.0 CI |
| `generate_lean_backend_doc` pattern not preserved | Review 2 | 🟠 Low | Archive notes; reference design for condensed charter |
| `modules-schema.json` does not exist | Review 6 (Schema Audit) | 🔴 Blocking for Phase 1 | Author `core-akr-templates/schemas/modules-schema.json` as Phase 1 deliverable |
| `consolidation-config-schema.json` has no `modules.yaml` awareness | Review 6 (Schema Audit) | 🟡 High | Add `modulesManifestPath` field to schema; `consolidate.py` reads it in Phase 4 |
| Dual cross-repo config schemas not documented | Review 6 (Schema Audit) | 🟡 High | Document split: `akr-config-schema.json` = participation; `consolidation-config-schema.json` = execution |
| `project_type` not in existing `requiredTags` | Review 6 (Schema Audit) | 🟡 High | Update `akr-config-schema.json` `validation.tagValidation.requiredTags` in Phase 1 |
| `humanInput` schema not aligned with ❓ HITL model | Review 6 (Schema Audit) | 🟠 Medium | Cross-reference `defaultRole` enum against template "who provides it" column in Phase 1 |
| `warnOnMissingLayers` not recognized as existing logic | Review 6 (Schema Audit) | 🟠 Medium | `consolidate.py` reads existing flag; document as read-not-implement |
| `monitoring` schema unused during pilot | Review 6 (Schema Audit) | 🟠 Medium | Enable in pilot `.akr-config.json` for Phase 0 generation-time baseline |
| `/docs.interview` original purpose not preserved in migration narrative | Workflow clarification | 🟠 Medium | Document as historical HITL command for unresolved `❓`; map replacement to Agent Skill Mode C |
| `copilot-instructions.md` rewrite scope underestimated | Review 7 (File Inspection) | 🔴 Blocking for Phase 1 | Full document replacement (~3–4 hours); only Core Principles, completeness scoring, and Vale gate reference are retained |
| `validate-documentation.yml` already exists and calls `validate_documentation.py` | Review 7 (File Inspection) | 🟡 High | Phase 1 CI task is ADAPT not BUILD; four targeted changes only |
| `tag-registry.json` PascalCase vs. free-text `feature` field mismatch | Review 7 (File Inspection) | 🔴 Blocking for pilot | Fix `feature` field to PascalCase in `modules.yaml`; add `CourseCatalogManagement` entry in Phase 0 |
| Agent Skill may not invoke in Copilot (GPT-4o): silent non-invocation, partial execution, context bypass | Review 9 (Skill Optimization) | 🔴 Blocking — skill is the primary workflow encoding; ungoverned invocation means governance contracts are unenforced | Three-layer stack: (1) `disable-model-invocation: true` frontmatter + `/akr-docs` slash-command only; (2) session hooks (`postToolUse` + `agentStop`); (3) `<!-- akr-generated -->` metadata header as in-document proof-of-execution checked by validator |
| Agent Skill execution quality varies by LLM: GPT-4o ~75% pass rate vs. Claude Sonnet ≥90%; Mode B truncation on large modules under GPT-4o | Review 9 (Skill Optimization) | 🟡 High — affects output completeness; CI gate catches gaps but developers need early warning | `SKILL-COMPAT.md` companion file documents model-specific failure modes; `evals/benchmark.json` tracks pass rates; `copilot-instructions.md` includes model compat note; CI gate is model-agnostic backstop |
| No pre-production skill eval framework: no baseline pass rates, no regression detection after model updates | Review 9 (Skill Optimization) | 🟡 High — without baseline, model updates silently degrade skill performance between phases | `evals/` directory with `cases/` (3 YAML assertion files) + `benchmark.json`; eval cases run during pre-pilot Tests 1 and 3; results populate Phase 1 baseline; re-run before Phase 4 |

---

## Part 13: The Optimal Implementation Path — Final

```
═══════════════════════════════════════════════════════════════
PHASE 0 — Prerequisites (1–2 weeks) BLOCKING GATE
Everything in Phase 0 must complete before Phase 1 begins.
═══════════════════════════════════════════════════════════════

Charter Compression (prerequisite for Pre-Pilot Test 1):
  □ Create copilot-instructions/backend-service.instructions.md
    Target: ~2,500 tokens. Source: AKR_CHARTER_BACKEND.md.
    Preserve: required sections, YAML fields, marker syntax,
    module-level section requirements, quality thresholds.
  □ Create copilot-instructions/ui-component.instructions.md
    Target: ~2,500 tokens. Source: AKR_CHARTER_UI.md.
  □ Create copilot-instructions/database.instructions.md
    Target: ~1,500 tokens. Source: AKR_CHARTER_DB.md.
  □ Full charters remain in charters/ — reference only.

Agent Skill Authoring (prerequisite for Phase 2.5):
  □ Create .github/skills/akr-docs/SKILL.md with Mode A + Mode B + Mode C.
    Use the three-mode specification from Part 5 of this document.
    Reference condensed charters (not full charters) in Mode B step 2.
  □ Add YAML frontmatter block above <!-- SKILL_VERSION --> comment:
    - disable-model-invocation: true (prevents silent auto-invocation)
    - optimized-for: claude-sonnet-4-6
    - tested-on: [claude-sonnet-4-6, gpt-4o] with pass-rate annotations
    (See Part 16 for rationale and failure modes this prevents.)
  □ Add self-reporting CRITICAL block as first SKILL body instruction.
    Required text: "CRITICAL: When this skill is loaded, begin EVERY response
    with: ✅ akr-docs INVOKED AND STEPS EXECUTED — Steps followed: ..."
  □ Add <!-- akr-generated --> metadata header write as final step of Mode B.
    See Part 5 Mode B step 8 for required field list.
  □ Create SKILL-COMPAT.md skeleton at .github/skills/akr-docs/SKILL-COMPAT.md.
    Model compatibility matrix rows; populate with Phase 0 eval results.

Skill Evaluation Framework (prerequisite for Phase 1 baseline):
  □ Create evals/ directory structure in core-akr-templates:
    evals/cases/mode-a-standard.yaml      (assertions matching Test 1 criteria)
    evals/cases/mode-b-coursedomain.yaml  (assertions vs. courses_service_doc.md)
    evals/cases/mode-b-large-module.yaml  (8-file stress test; no truncation)
    evals/datasets/coursedomain-files/    (input files for eval cases)
    evals/benchmark.json                  (null baseline; populated after Tests 1+3)
  □ Run eval cases during Pre-pilot Tests 1 and 3 (no additional time cost).
    Record pass rates and token counts for claude-sonnet-4-6 and gpt-4o.
  □ Populate SKILL-COMPAT.md v1.0 skeleton with Phase 0 eval results.
  Gate: mode-b-coursedomain.yaml requires condensed backend charter first.

modules.yaml Schema Definition:
  □ Define complete schema per Part 4 of this document.
  □ Create core-akr-templates/examples/modules.yaml with:
    - TrainingTracker.Api example (CourseDomain + training.Courses)
    - UI project example (CourseManagementUI)
    - Both modules[] and database_objects[] sections shown

Infrastructure Audit:
  □ Audit .akr/workflows/ — two workflows confirmed (Review 7):
    1. validate-documentation.yml — PRIMARY MIGRATION TARGET
       Already calls validate_documentation.py at core-akr-templates/main/scripts/
       Already runs Vale with .akr/.vale.ini config
       Already uses tj-actions/changed-files@v41 for diff
       Already has Checks API permissions
       → Phase 1 task: ADAPT this workflow; do not rebuild from scratch
    2. distribute-tag-registry.yml — RETAIN AND LEVERAGE
       Triggers on tag-registry.json changes; validates against tag-registry-schema.json;
       distributes to application repos automatically
       → Phase 4 task: assess whether tag-registry.json can be evolved into
         feature-registry.yaml rather than creating a parallel file
  □ Add CourseCatalogManagement (and other pilot feature tags) to tag-registry.json.
    distribute-tag-registry.yml will auto-distribute on commit.
    Do this before pilot modules.yaml is authored.
  □ Extended migration inventory:
    - git grep -l '\.akr/' (repository paths)
    - CI/CD pipeline configs (Azure DevOps / GitHub Actions)
    - Deployment scripts (*.ps1, *.sh) referencing .akr/ or old script names
    - External config management tools
    - .gitmodules references
  □ Narrow TEMPLATE_MANIFEST.json to templateId→version registry only.
    Document deprecated roles in CHANGELOG.

Cost Modeling:
  □ Model premium request consumption for Copilot agent mode + coding agent.
    Use GitHub billing dashboard + M365 Agent Usage Estimator.
    Establish monthly budget baseline and alert threshold.
  □ Enable monitoring in pilot project's .akr-config.json:
    monitoring: { enabled: true, trackMetrics: ["generation-time", "validation-results"] }
    This provides a documentation-layer usage baseline at zero additional cost.
    Collect generation-time data across first 10 module documentation runs.

Pre-Pilot Validation Spike (5 tests — see Part 11):
  □ Test 1: Module-level code analysis with condensed backend charter.
  □ Test 2: Hosted MCP context source configuration at current plan tier.
  □ Test 3: Large-module stress test (8 files, 2,000+ LOC).
  □ Test 4: GitHub Actions invocability (or confirm deterministic fallback).
  □ Test 5: Data governance and legal compliance sign-off.
  GATE: All 5 tests pass or have documented fallback architectures.

═══════════════════════════════════════════════════════════════
PHASE 1 — Foundation (3–5 weeks)
Target: core-akr-templates v1.0.0 release tag.
═══════════════════════════════════════════════════════════════

Template Adaptation:
  □ Adapt lean_baseline_service_template.md → module variant.
    Add: Module Files section, Operations Map, full-stack architecture
    diagram instructions, module-scope YAML front matter.
    Acceptance criterion: output matches courses_service_doc.md structure.
  □ Adapt ui_component_template.md → module variant.
    Add: Module Files section, component hierarchy diagram.
  □ Retain table_doc_template.md and embedded_database_template.md as-is.
    These are Level 2 templates; no module-scope changes needed.

copilot-instructions.md Rewrite:
  □ Remove: MCP server tool invocations, Tree-sitter references,
    VSCODE_WORKSPACE_FOLDER references, file-centric template selection.
  □ Replace with: module-centric template selection table (Part 7).
    project_type → charter → template mapping.
  □ Add: module grouping principles (domain noun, dependency graph,
    DTO alignment, interface/implementation pairs).

validate_documentation.py v1.0:
  □ Implement full v1.0 scope per Part 6 of this document.
    Realistic estimate: 500–650 lines.
    Declared dependency: pyyaml.
  □ Add <!-- akr-generated --> metadata header check to validate_documentation.py.
    MODULE docs fail with: "AKR metadata header missing — skill may not have
    been properly invoked. Re-run using /akr-docs mode-b [module]."
    (Part 6 addition — this is v1.0 scope, not deferred.)
  □ Module-type-aware validation (reads modules.yaml).
  □ modules.yaml schema validation (9 validation rules).
  □ MODULE vs. DB_OBJECT vs. UNKNOWN doc classification.
  □ Transparency marker checks (🤖, ❓, DEFERRED).
  □ compliance_mode enforcement (pilot/production).
  □ minimum_standards_version check.
  □ --fail-on=never|needs|all flag.
  □ Fallback: modules.yaml absent → warn + generic rules only.
  □ Port test assertions from test_validation_library.py as unit tests.
  □ Cross-platform testing: Ubuntu (Actions), macOS, Windows.
  □ Author .github/hooks/postToolUse.json (audit logger).
    Logs file writes to .akr/logs/session-YYYYMMDD.jsonl during agent sessions.
  □ Author .github/hooks/agentStop.json (auto-validation gate).
    Runs validate_documentation.py automatically when agent session ends.
    Handles missing modules.yaml gracefully (skip, do not fail).
  □ Add .akr/logs/ to .gitignore.
  □ Include .github/hooks/ in distribute-skill.yml distribution bundle
    alongside SKILL.md and SKILL-COMPAT.md.
  □ Run Phase 1 eval suite after SKILL.md is authored:
    Execute evals/cases/ against current model versions.
    Populate benchmark.json v1.0 baseline.
    Update SKILL-COMPAT.md v1.0 with model matrix values.

CI Workflow (adapt existing — do not rebuild the workflow; create the missing script):
  □ Author .akr/scripts/validate_documentation.py in core-akr-templates (Phase 1 deliverable).
    Location: `.akr/scripts/validate_documentation.py` (canonical location in governance subtree).
    Scope: ~500–650 lines; full implementation per Part 6 requirements.
    Implementation: Days 2–4 of Phase 1; unblocked after charter compression begins.
    Acceptance criteria: All tests in test_pipeline_e2e.py pass; all MODULE-required sections detected;
    database_objects[] type detection working; modules.yaml validation working.
  □ Migrate .akr/workflows/validate-documentation.yml to validation/workflows/.
    This workflow already:
    - Attempts to download validate_documentation.py from a broken URL (404 — will be fixed below)
    - Installs Vale v2.29.0
    - Runs changed-files detection (tj-actions/changed-files@v41)
    - Has Checks API permissions configured
  □ Adaptations required (five changes total):
    1. Add pyyaml to pip install step
       (current: pip install --no-cache-dir requests)
       (new:     pip install --no-cache-dir requests pyyaml)
    2. **Fix the script download URL** (currently 404)
       (current: https://raw.githubusercontent.com/reyesmelvinr-emr/core-akr-templates/main/scripts/validate_documentation.py)
       (new:     https://raw.githubusercontent.com/reyesmelvinr-emr/core-akr-templates/main/.akr/scripts/validate_documentation.py)
    3. Add modules.yaml to paths: trigger
       (current: docs/**, src/**, .akr-config.json)
       (new:     docs/**, src/**, .akr-config.json, modules.yaml)
    4. Add --module-name flag support to the Run AKR validation step
       (pass project root so script can locate modules.yaml)
    5. Update Vale config path from .akr/.vale.ini to validation/.vale.ini
       (after .akr/ → validation/ directory migration)
    6. Verify that validate_documentation.py v1.0's JSON output structure matches
       the field names expected by the existing jq queries in the workflow's
       downstream steps (.summary.total_errors, .summary.total_warnings,
       .summary.average_completeness). Preserve these exact field names in v1.0's
       --output json schema to ensure compatibility with existing CI logic.

Governance Policies:
  □ compliance_mode graduation criteria documented:
    Trigger: zero ❓ markers in production for 4 consecutive weeks.
    Approval: standards team lead sign-off.
    Artifact: CHANGELOG entry with date and approver.
  □ TEMPLATE_MANIFEST.json narrowed and CI check implemented:
    CI validates that Agent Skill references valid templateId values.
  □ Tag Registry Feature Entry Requirements:
    Document that new entries to tag-registry.json require the following
    fields in the governance section: approved, domain, description, owner,
    status (all required). Optional but recommended: synonyms, relatedFeatures,
    addedDate. Validate entries against tag-registry-schema.json patternProperties
    regex (^[A-Z][a-zA-Z0-9]*$) before distribution.

Schema Deliverables (new — required before validate_documentation.py can reference schemas):
  □ Author .akr/schemas/modules-schema.json (alongside existing akr-config-schema.json,
    tag-registry-schema.json, and consolidation-config-schema.json).
    Define complete modules.yaml schema per Part 4 of this document.
    Include: project section, modules[] array, database_objects[] array,
    unassigned[] array. Layer enum mirrors akr-config-schema.json projectInfo.layer.
  □ Update akr-config-schema.json validation.tagValidation.requiredTags:
    Add project_type as a conditional required tag for MODULE-type documents.
    Document the conditionality: required when doc_type = MODULE; not required
    for DB_OBJECT or UNKNOWN docs.

HITL Alignment:
  □ Cross-reference akr-config-schema.json humanInput.defaultRole enum against
    the "who provides it" column in adapted templates:
    - technical_lead → Level 1 grouping validation + architecture review
    - developer      → Level 2 content review (fills ❓ sections)
    - product_owner  → Phase 4 narrative refinement
    - qa_tester      → Copilot Studio approval gate (Phase 3+)
    This ensures validate_documentation.py can eventually read humanInput.priorityFilter
    to distinguish blocking (critical) from advisory (optional) ❓ markers.

Release:
  □ Tag core-akr-templates v1.0.0.
  □ Publish release notes documenting scope and migration from .akr/ paths.

═══════════════════════════════════════════════════════════════
PHASE 2 — Pilot Project Onboarding (1–2 weeks per project)
Target: One project end-to-end; CI gate live; retrospective complete.
═══════════════════════════════════════════════════════════════

  □ Select pilot project (recommended: TrainingTracker.Api).
  □ Per-project onboarding checklist:
    - Add core-akr-templates as submodule at v1.0.0
    - Configure hosted MCP context source (or .github/copilot-instructions.md)
    - Copy .github/skills/akr-docs/SKILL.md from core-akr-templates
    - Deploy validate-documentation.yml from examples/
    - Create initial modules.yaml (project section only; modules[] empty)
  □ Run Mode A (grouping proposal) on pilot project.
    Review draft modules.yaml PR with developer who knows the codebase.
    Time the grouping validation: target <15 minutes.
  □ Run Mode B (documentation generation) on CourseDomain module.
    Developer present; record time-to-draft.
  □ Open first documented PR; verify CI validation runs correctly.
  □ Test full workflow in Visual Studio (not just VS Code).
  □ Run Mode B on two additional modules independently (unassisted).
  □ Conduct 2–4 week pilot period.
  □ Run pilot retrospective:
    - Time-to-doc per module
    - ❓ section fill rate
    - Validation pass rate on first PR
    - Grouping proposal accuracy (% of groups requiring reassignment)
    - Specific friction points
    - Self-reporting block present rate (target: 100% of Mode B responses)
    - akr-generated metadata header present rate (target: 100% of merged docs)
  □ Document GPT-4o-specific failure modes observed during pilot in SKILL-COMPAT.md v1.1.
    Classify per Part 16 failure mode taxonomy before Phase 2.5 begins.
  □ Update benchmark.json with pilot real-world pass rates alongside Phase 1 baseline.
  □ Update templates and validate_documentation.py based on findings.
  □ Tag v1.1.0 if breaking changes; update pilot project's standards_version pin.
  □ Expand to second project using updated onboarding checklist.

═══════════════════════════════════════════════════════════════
PHASE 2.5 — Copilot Coding Agent Spike (1 week)
Gate: Run after Phase 2 retrospective. Go/no-go for Phase 3.
═══════════════════════════════════════════════════════════════

  □ Create GitHub Issue template: "Generate Module Documentation"
    Fields: module name, project name, project_type.
  □ Assign issue to Copilot coding agent.
  □ Agent uses akr-docs SKILL.md + condensed charter from project_type.
  □ Acceptance criteria (from test_pipeline_e2e.py):
    - All MODULE required sections present
    - Module Files section lists all files with correct roles
    - Operations Map covers all operations in all files
    - validate_documentation.py passes with zero errors
    - No section truncation or omission
    - Criterion 9: <!-- akr-generated --> metadata header present in PR output
      (confirms skill completed Mode B in async coding agent context)
    - Criterion 10: .akr/logs/session-*.jsonl hook log present in PR
      (hard gate only if Copilot hook support is confirmed in Phase 1;
      otherwise classify as KNOWN-GAP telemetry, document evidence in
      SKILL-COMPAT.md, and do not authorize Phase 3 on Criterion 10 alone)
  □ Classify Phase 2.5 failures against SKILL-COMPAT.md model-specific failure modes.
    Distinguish: GPT-4o model limitation (cannot fix with SKILL.md edits) vs.
    fixable skill instruction gap (can address with SKILL.md update).
    Only model-limitation failures authorize Phase 3 scope.
  □ Populate benchmark.json coding-agent key with Phase 2.5 pass rates.
  □ Pass → coding agent is the Phase 3 automation layer.
            Document: "Phase 3 custom agent not required."
  □ Fail → Document specific failure modes by section and module type.
            Phase 3 authorized only for the documented failure cases.

═══════════════════════════════════════════════════════════════
PHASE 3 — Automation Extension (conditional on Phase 2.5 outcome)
═══════════════════════════════════════════════════════════════

If Phase 2.5 passes:
  □ Coding agent + Agent Skill is the automation layer. Phase 3 complete.
  □ Optionally: Copilot Studio Doc Review agent in Teams (if M365 licenses
    confirmed and credit budget approved).

If Phase 2.5 fails (specific documented cases only):
  □ Survey Copilot Marketplace extensions (2–3 days) before building.
  □ Evaluate GitHub Actions + coding agent composition before Azure Functions.
  □ If building custom @doc-agent:
    - 350-line review gate; 500-line hard ceiling
    - CI enforces line count on agent repository
    - No logic embedded in agent; all governance logic in core-akr-templates

Copilot Studio Doc Review Agent (if M365 licensing confirmed):
  □ Trigger on PR label: docs-review-required (not every PR)
  □ Approval routing: tech lead, QA lead, product owner, security reviewer
  □ Compliance artifact: approval chain logged per PR
  □ Credit model confirmed via Agent Usage Estimator before deployment

═══════════════════════════════════════════════════════════════
PHASE 4 — Cross-Repository Feature Consolidation
Gate: Phase 2 stable ≥6 weeks; zero bypass events; all docs tagged.
═══════════════════════════════════════════════════════════════

  □ Assess tag-registry.json vs. feature-registry.yaml:
    distribute-tag-registry.yml already governs tag-registry.json distribution.
    Before creating a new feature-registry.yaml, evaluate whether tag-registry.json
    can be extended with cross-repository participation metadata.
    If tag-registry.json is evolved: update distribute-tag-registry.yml validation rules.
    If a new feature-registry.yaml is needed: it must not duplicate tag-registry.json keys.
  □ Author feature-registry.yaml (or extend tag-registry.json) in core-akr-templates.
    Maps PascalCase feature_tag keys to display names and participating repositories.
  □ Update consolidation-config-schema.json:
    Add modulesManifestPath field (default: "modules.yaml").
    consolidate.py reads modules.yaml first when this field is present;
    falls back to docsPath glob scan for repos not yet onboarded.
  □ Implement consolidate.py as deterministic Python aggregator.
    Config reading split (both configs must be read):
    - akr-config-schema.json crossRepository section: drives participation
      (publishFeatureDocs, relatedRepositories[], sectionMapping)
    - consolidation-config-schema.json: drives execution
      (which repos to clone, modulesManifestPath, output format)
    Document input contract:
    - FOR_EACH_API_COMPONENT: module docs where project_type in [api-backend, microservice]
    - FOR_EACH_UI_COMPONENT: module docs where project_type = ui-component
    - FOR_EACH_DB_COMPONENT: database_objects[] entries
    - Fills feature-consolidated.md template placeholder syntax
    - No AI invocation from Actions
    warnOnMissingLayers: read from consolidation-config-schema.json
    validation.warnOnMissingLayers (existing field — do not re-implement).
  □ Deploy .github/workflows/consolidate-feature.yml in Feature repo.
    Trigger: workflow_dispatch (manual) or schedule.
    Output: structured draft in docs/features/{FeatureName}_doc.md.
  □ Product Owner refines narrative sections with Copilot agent mode.
  □ Test consolidation on 3-component feature end-to-end.
  □ Verify consolidation completes in under 2 minutes (sparse checkout).
  □ Test with real Product Owner and QA lead.
```

---

## Part 14: Decisions Locked vs. Decisions Still Open

### Locked — No Further Analysis Needed

| Decision | Evidence |
|---|---|
| `validate_documentation.py` must be authored from scratch; download URL must be corrected | Final file inspection: script does not exist; workflow attempts 404 download. New canonical location: `.akr/scripts/validate_documentation.py` in core-akr-templates |
| Charter compression is Phase 0 blocking precondition | AKR_CHARTER_BACKEND.md at ~11,000 tokens; math is unambiguous |
| `modules.yaml` separates `modules[]` from `database_objects[]` | Module architecture clarification; required for validator and consolidate.py |
| Agent Skill has Mode A (DocumentPlanner grouping) + Mode B (generation) + Mode C (interactive HITL completion) | Workflow clarification + module architecture; sequencing enforced by skill |
| `validate_documentation.py` must be module-type-aware in v1.0 | Module architecture; cannot defer without false positives on module docs |
| `copilot-instructions.md` requires module-centric rewrite | Module architecture; file-centric logic is structurally wrong |
| `layer` (project-level) ≠ `project_type` (module-level) | Module architecture; separate fields, separate validation |
| `consolidate.py` reads module docs as atomic inputs for API/UI | Module architecture; individual component iteration is no longer correct |
| Phase 2.5 before Phase 3 authorization | All reviews; coding agent must be tested before Azure Function is justified |
| Tag-registry and consolidation schemas both exclude `Full-Stack` intentionally | Final audit: both omit `Full-Stack` from their layer enums. `modules-schema.json` will include `Full-Stack` (parity with `akr-config-schema.json`), but tag-registry and consolidation remain as separate governance layers |
| `TEMPLATE_MANIFEST.json` narrowed to version registry | M365 + prior review reconciliation |
| `courses_service_doc.md` is the Level 1 acceptance criterion | Module architecture clarification |
| `modules-schema.json` is a new Phase 1 deliverable (does not exist yet) | Review 6 schema audit |
| `consolidation-config-schema.json` needs `modulesManifestPath` evolution in Phase 4 | Review 6 schema audit |
| Cross-repo config split: participation (`akr-config-schema.json`) vs. execution (`consolidation-config-schema.json`) | Review 6 schema audit |
| `warnOnMissingLayers` is an existing config flag — read, do not re-implement | Review 6 schema audit |
| Agent Skill must use `disable-model-invocation: true` frontmatter; explicit `/akr-docs` slash command is the supported path for interactive use, while coding-agent runs are initiated through issue assignment with Mode B instructions and validated via metadata header checks | Review 9 (Skill Optimization) — three failure modes of auto-invocation confirmed |
| Mode B final step must write `<!-- akr-generated -->` metadata header; `validate_documentation.py` must check for its presence; absence is a CI failure | Review 9 (Skill Optimization) — in-document proof-of-execution contract |
| Agent Skill execution quality is LLM-dependent; `SKILL-COMPAT.md` and `evals/benchmark.json` are required governance artifacts, not optional tooling | Review 9 (Skill Optimization) — GPT-4o vs. Claude Sonnet variance confirmed; eval framework required before pilot |

### Still Open — Requires Input or Testing

| Decision | Open Question | How to Resolve |
|---|---|---|
| Hosted MCP context source availability | Available at current GitHub Copilot Business tier? | Pre-pilot Test 2 |
| Copilot coding agent premium request rate | What is the per-session cost at team scale? | GitHub billing dashboard + M365 estimator |
| Copilot Studio Doc Review agent | Are M365 Copilot licenses available? | Check licensing |
| `allowWorkflowBypass` default value in `config.json` | Does the dev config ship with bypass enabled? | Code inspection; confirms whether config gate is nominal |
| `copilot-instructions.md` character limit | Is ~4,000 characters sufficient for condensed backend charter? | Test during charter compression |
| Template adaptation acceptance | Does adapted `lean_baseline_service_template.md` produce output matching `courses_service_doc.md`? | Phase 1 deliverable; `courses_service_doc.md` is the spec |
| Agent Skills hooks support in GitHub Copilot | Do `.github/hooks/postToolUse.json` and `.github/hooks/agentStop.json` trigger in Copilot agent mode (not just Claude Code)? | Test during Phase 1 Deliverable 7A; if not supported, document as known gap in `SKILL-COMPAT.md`; CI gate remains the enforcement backstop |

---

## Part 15: Summary of What Each Major Input Contributed

| Input | What It Permanently Changed |
|---|---|
| Review 1 (Claude) | Pre-pilot assumptions as blocking gate; version drift policy; Phase 3 infrastructure concern; `max_files_per_module` governance constraint |
| Review 2 (GH Copilot R1) | Context saturation identified; coding agent as Phase 2.5; `test_pipeline_e2e.py` as acceptance criteria baseline |
| Review 3 (GH Copilot R2) | Charter sizes quantified → compression becomes Phase 0 blocking; `force_workflow_bypass` corrected; template count corrected to 10; `.akr/workflows/` asset identified |
| Review 4 (M365 Copilot) | Agent Skills as primary cross-surface workflow primitive; Copilot Studio for non-developer HITL; premium request metering; `TEMPLATE_MANIFEST.json` retention (narrowed) |
| Review 5 (Module Architecture) | Three-tier hierarchy defined; Agent Skill baseline specified (Mode A + Mode B); `modules.yaml` full schema; `validate_documentation.py` scope upgraded; `layer` vs. `project_type` distinction; `consolidate.py` input contract revised; `copilot-instructions.md` rewrite scope elevated |
| Workflow Clarifications (Owner-provided) | Corrected `/docs.interview` purpose as HITL completion for `❓` markers; added Agent Skill Mode C for interactive in-editor completion; made zero-cloud/no-incremental-cost a named architectural constraint; documented original `core-akr-templates` → sync → `akr-mcp-server` design intent continuity |
| Review 6 (Schema Audit) | Four corrections: `modules-schema.json` is new; `consolidation-config-schema.json` needs `modulesManifestPath`; dual cross-repo config split documented; `project_type` not in existing `requiredTags`. Three additions: `humanInput` schema aligns with HITL model; `warnOnMissingLayers` is existing logic; `monitoring` schema enables Phase 0 cost baseline |
| Review 7 (Final File Inspection) | `copilot-instructions.md` is a full replacement (52-line slash-commands section, Tree-sitter section, YAML front matter, directory structure, troubleshooting — all removed); `validate-documentation.yml` already exists and calls the script (Phase 1 CI = adapt, not build; five adaptations including URL fix); `tag-registry.json` uses PascalCase keys incompatible with free-text `feature` field examples |
| Review 8 (Final File Inspection 2) | CRITICAL: `validate_documentation.py` does not exist anywhere; must be created from scratch as Phase 1 deliverable at `.akr/scripts/validate_documentation.py`. Workflow download URL currently 404 and must be corrected. This is separate from workflow adaptation task. Also confirmed: `tag-registry-schema.json` `layers` array and `consolidation-config-schema.json` `repositories[].layer` both omit `Full-Stack` intentionally (separate from `modules-schema.json` which will include it) |
| Module Architecture Clarification | `courses_service_doc.md` confirmed as Level 1 acceptance criterion; module grouping rules; database object separation invariant; template adaptation is multi-file scope, not new sections |
| Review 9 (Skill Optimization) | Three Agent Skill failure modes confirmed and resolved: (1) silent non-invocation → `disable-model-invocation: true` + `/akr-docs` slash command only; (2) partial execution → self-reporting block + `<!-- akr-generated -->` metadata header contract; (3) LLM execution variance → `SKILL-COMPAT.md` + `evals/benchmark.json` eval framework. Hooks (`postToolUse` + `agentStop`) specified as Layer 2 enforcement. GPT-4o vs. Claude Sonnet 4.6 pass rate delta quantified (~75% vs. ≥90%). Phase plan impact: Phase 0 adds eval framework + SKILL.md frontmatter; Phase 1 adds metadata header validator check + hooks + `SKILL-COMPAT.md` v1.0; Phase 2 adds reliability retrospective metrics; Phase 2.5 adds Criteria 9 and 10 |

---

## Part 16: Agent Skill Reliability — Three-Layer Enforcement Stack

*Source: Review 9 (Post-implementation planning conversation, March 2026)*

This part documents the rationale, failure modes, and resolution for a class of reliability risk that was not visible during the initial seven-review synthesis: **Agent Skills can be invoked without executing, and executed without completing.** Both failures are silent. This section is the authoritative reference for all skill reliability decisions in the phase plan files.

---

### 16.1 The Problem: Three Failure Modes of Skill Non-Invocation

Agent Skills are not enforced execution contracts - they are suggestions the LLM follows when it chooses to. Copilot (GPT-4o) can respond to a documentation request *without* loading `SKILL.md`. Even when loaded, it can skip or compress steps under context pressure. Four failure modes are confirmed:

| Failure Mode | What Happens | Governance Impact |
|---|---|---|
| **Silent non-invocation** | Copilot's intent matcher does not load the skill; Copilot responds from general training data | Full AKR workflow bypassed; output looks plausible but has no charter, no template, no compliance markers |
| **Partial execution** | Skill loads but steps are skipped or compressed, especially on large modules | Missing sections; CI gate catches it, but only after PR submission - no local warning |
| **Context saturation skip** | Skill instructions deprioritised when context window is near capacity with source files | Unpredictable step omissions; worsens above 6 files per module on GPT-4o |
| **Bypass gate risk** | `allowWorkflowBypass` configuration allows workflow circumvention without notification | Skill pipeline bypassed entirely; confirmed in `akr-mcp-server` `force_workflow_bypass` config gate |

**Why this matters for AKR governance specifically:** The charter, template, transparency marker rules, and `modules.yaml` status checks are all encoded in the skill. If the skill does not run, none of these governance contracts are applied. A developer or coding agent can produce a complete-looking document that passes a casual review but violates every AKR standard. The CI gate catches this - but only if `validate_documentation.py` knows what to look for.

---

### 16.2 LLM-Dependent Execution Quality

The same `SKILL.md` file is portable across Claude Code, GitHub Copilot, Cursor, and Codex CLI (open standard, December 2025). However, **execution quality varies significantly by underlying model**.

| Model | Expected Pass Rate | Primary Failure Pattern | Notes |
|---|---|---|---|
| Claude Sonnet 4.6 | ≥90% | None confirmed | Primary benchmark model; skill optimized and tested against this model |
| GPT-4o (Copilot default) | ~75% | Mode B truncation on large modules (>6 files); Operations Map most affected | Context window budget handled less efficiently; charter compression critical |
| Coding agent (async) | TBD - Phase 2.5 | Hooks may not trigger in async context | `benchmark.json` `coding-agent` key populated in Phase 2.5 |

**Pass rate source:** Phase 0 eval baseline (see section 16.4). Values are populated after pre-pilot Tests 1 and 3; the figures above are initial targets, not confirmed measurements.

**Consequence for teams:** Most AKR developers will use GitHub Copilot (GPT-4o). The ~75% pass rate means approximately 1 in 4 Mode B runs will require re-invocation or CI-guided correction. This is acceptable for an interactive workflow - it is not acceptable for an unattended coding agent workflow where the failure is not discovered until PR review. Criteria 9 and 10 in Phase 2.5 directly test this distinction.

**Model updates:** GitHub Copilot's underlying model is updated by Microsoft without announcement. A skill that passes at 90% today may degrade silently after a model update. The re-evaluation requirement before Phase 4 (PHASE_4_FEATURE_CONSOLIDATION.md, Skill Re-Evaluation Prerequisite section) exists specifically for this risk.

---

### 16.3 The Three-Layer Reliability Stack

The resolution is three complementary enforcement layers. Each layer catches failures the previous layer misses:

| Layer | Mechanism | What It Catches | Where Configured |
|---|---|---|---|
| **Layer 1 - Force Invocation** | `disable-model-invocation: true` in SKILL.md frontmatter; interactive runs use explicit `/akr-docs mode-b [module]`, while coding-agent runs use explicit Mode B instructions in issue templates and are verified by metadata headers | Silent non-invocation; Copilot acting without loading skill | SKILL.md frontmatter + issue template contract |
| **Layer 2 - Enforce Execution** | `agentStop` hook auto-runs `validate_documentation.py` at session end; `postToolUse` hook logs file writes to `.akr/logs/` | Silent step skipping; no local feedback before PR opens | `.github/hooks/*.json` - distributed to all registered repos |
| **Layer 3 - In-Document Contract** | `<!-- akr-generated -->` metadata header as Mode B final step; `validate_documentation.py` checks for presence | No proof that skill ran; unclear which mode/version/steps completed | SKILL.md Mode B step 8; `validate_documentation.py` MODULE check |

**Layer 1 alone** prevents the most common failure mode (auto-invocation mismatch) but does not help if the skill loads and then skips steps under context pressure.

**Layer 2 alone** provides a local feedback loop but depends on hook support in the execution surface (confirmed in Claude Code; Copilot hook support subject to Phase 1 verification - see Part 14 Still Open).

**Layer 3 alone** is the CI backstop - model-agnostic, surface-agnostic, always runs. But it catches failures *after* PR submission. Layers 1 and 2 move this detection earlier.

**The CI gate is the guarantee. Layers 1 and 2 are early warning.**

---

### 16.4 Skill Evaluation Framework

Before Phase 1 pilot begins, a baseline eval suite must establish what "passing" looks like for both supported models. Without a baseline, there is no way to detect regressions after model updates or SKILL.md changes.

#### Directory Structure

```
core-akr-templates/
  evals/
    cases/
      mode-a-standard.yaml         # Mode A grouping assertions
      mode-b-coursedomain.yaml     # Mode B vs. courses_service_doc.md structure
      mode-b-large-module.yaml     # Mode B 8-file stress test; no truncation
    datasets/
      coursedomain-files/          # Real input files; reuse from pre-pilot Test 1
    benchmark.json                 # Pass rates + token counts per model version
  .github/
    skills/
      akr-docs/
        SKILL.md
        SKILL-COMPAT.md            # Model compatibility matrix
```

#### `benchmark.json` Schema

```json
{
  "last-updated": "YYYY-MM-DD",
  "schema-version": "1.0",
  "models": {
    "claude-sonnet-4-6": {
      "mode-a-standard":     { "pass-rate": null, "avg-tokens": null },
      "mode-b-coursedomain": { "pass-rate": null, "avg-tokens": null },
      "mode-b-large-module": { "pass-rate": null, "avg-tokens": null, "known-issue": null }
    },
    "gpt-4o": {
      "mode-a-standard":     { "pass-rate": null, "avg-tokens": null },
      "mode-b-coursedomain": { "pass-rate": null, "avg-tokens": null },
      "mode-b-large-module": { "pass-rate": null, "avg-tokens": null, "known-issue": null }
    },
    "coding-agent": {}
  }
}
```

`null` values are populated after each eval run. The `coding-agent` key is populated in Phase 2.5.

#### Eval Cadence

| When | Action |
|---|---|
| Phase 0 (during pre-pilot Tests 1 and 3) | Run eval cases; populate baseline; no additional time cost |
| Phase 1 (after SKILL.md is authored) | Re-run suite; confirm baseline holds with new frontmatter |
| Phase 2 (after pilot retrospective) | Update with real-world pilot pass rates; note delta from synthetic baseline |
| Phase 2.5 (after coding agent test cases) | Populate `coding-agent` key |
| Phase 4 (before documentation runs begin) | Re-run full suite; check for model update regressions |

---

### 16.5 `SKILL-COMPAT.md` - Model Compatibility Matrix

`SKILL-COMPAT.md` is a companion governance file maintained alongside `SKILL.md`. It is distributed to all registered repositories via `distribute-skill.yml`. Its purpose is to give developers the information they need to invoke the skill correctly and to diagnose failures without filing support tickets.

#### Content Requirements

- **Model compatibility matrix:** Pass rates per eval case per model; sourced from `benchmark.json`
- **Known failure modes per model:** Specific failure patterns with descriptions (e.g., "GPT-4o truncates Operations Map on modules with >6 files")
- **Recommended workarounds:** Per-model prompt adjustments (e.g., "For large modules on Copilot, invoke Mode B twice - first for Module Files + Operations Map, second for Business Rules + Data Operations")
- **Re-evaluation policy:** *"Re-run evals/cases/ after any SKILL.md change or after a GitHub Copilot model update notification."*

#### Version Correspondence

`SKILL-COMPAT.md` version must correspond to the `SKILL_VERSION` in `SKILL.md`. When a new skill version is distributed, `SKILL-COMPAT.md` is also updated (or noted as unchanged if no model compatibility changes occurred).

---

### 16.6 Developer Quick Reference - Correct Invocation in Copilot

| Action | Command | Notes |
|---|---|---|
| Start Mode A (grouping proposal) | `/akr-docs mode-a [project path]` | Always use explicit command; never rely on natural language auto-discovery |
| Start Mode B (doc generation) | `/akr-docs mode-b [module name]` | Same |
| Start Mode C (HITL completion) | `/akr-docs mode-c [doc path]` | Same |
| Verify skill is discovered | `/skills` in Copilot Chat | Confirms `akr-docs` is in the Configure Skills menu |
| Confirm invocation | First response line: `✅ akr-docs INVOKED AND STEPS EXECUTED` | If missing, retry with explicit `/akr-docs` command before proceeding |
| Check local validation | `.akr/logs/last-validation.json` | Written by `agentStop` hook at session end; check before opening PR |
| Confirm proof-of-execution | `<!-- akr-generated -->` block at top of output document | Required; CI fails if absent |

**If the self-reporting block is absent from a response:**
1. Check `/skills` to confirm `akr-docs` is enabled and not disabled
2. Retry with explicit: `/akr-docs mode-b [module name]`
3. If still absent: note as skill reliability event; check `SKILL-COMPAT.md` for known model-specific workarounds
4. CI `validate_documentation.py` will catch any output structure gaps regardless - do not merge without CI passing

---

### 16.7 Relationship to Existing Architecture Decisions

This part does not change any existing architecture decision. It adds an enforcement layer *on top of* the existing design:

| Existing Decision | Review 9 Addition |
|---|---|
| Agent Skills as primary workflow encoding (Part 10) | Three-layer enforcement stack ensures the encoding is *actually executed* |
| `validate_documentation.py` as CI gate (Part 6) | Metadata header check added to MODULE doc rules; catches skill non-completion |
| Charter compression as Phase 0 blocking precondition (Part 3) | GPT-4o context budget is the reason this is even more critical - less context headroom means more truncation risk |
| Pre-pilot Tests 1 and 3 (Part 11) | Eval cases run during these tests; self-reporting block and metadata header are now pass criteria |
| Phase 2.5 binary coding agent test (PHASE_2_5) | Criteria 9 and 10 added; async context is where Layer 2 (hooks) may not function |
| Zero cloud infrastructure constraint (Part 10) | Hooks are JSON config files in `.github/`; eval cases are YAML files; `benchmark.json` is a text file - zero infrastructure cost |

---

## Part 17: Agent Skills SDK Update - Validated Addendum (March 2026)

**Date reviewed:** March 2026  
**Source reviewed:** *What's New in Agent Skills: Code Skills, Script Execution, and Approval for Python* (March 13, 2026)  
**Review type:** Post-initial-analysis addendum, validated against current repository state

### 17.1 Why This Was Reviewed Now

This SDK release introduced primitives that align directly with Phase 3 conditional design decisions (custom `@doc-agent` path) and Phase 4 governance concerns (side-effect gating). Because these phases are decision-gated and not yet locked by infrastructure deployment, evaluating this release now has low cost and high downside prevention value.

### 17.2 Relevance to AKR (Validated)

| SDK Capability | AKR Relevance | Validated Impact |
|---|---|---|
| Code-defined scripts via `@skill.script` + `run_skill_script` | High (Phase 3 Path B) | Adds a no-hosting execution option for deterministic handlers (operation extraction, chunked generation, project type detection) before committing to Azure Functions |
| Script approval via `require_script_approval` | High (Phase 3/4 compliance) | Adds pre-side-effect HITL gate that complements existing PR-level review; maps naturally to `pilot` vs `production` compliance behavior |
| Code-defined skills + `@skill.resource` dynamic resources | Medium (future path) | Strong option for live standards/version hydration if static charter snapshots prove stale in production |
| File-based + code-defined mixed provider model | Conditional only | Relevant only if a custom Python SkillsProvider is authorized in Phase 3 Path B |

### 17.3 What This Changes in This Analysis (and What It Does Not)

**Changes adopted here:**

1. Phase 3 option space is formally expanded to include code-defined script execution as a first-class candidate (not just Azure Functions/GitHub Actions).
2. Script-level approval is recognized as an additional HITL checkpoint for write-side effects, especially for production mode.
3. Dynamic resources are documented as an intentional future enhancement path, not an immediate architecture pivot.

**No change to locked decisions:**

- Phases 0-2.5 remain valid as written.
- File-based `SKILL.md` remains the primary delivery mechanism for GitHub Copilot built-in agent mode.
- Phase 3 remains conditional on Phase 2.5 FAIL.

### 17.4 Validation Outcome Against Current Plan Files

The addendum recommendation set is directionally correct, but one statement required correction after repository validation:

| Addendum Claim | Validation Result |
|---|---|
| "Four targeted updates were made to phase documents" | **Not yet fully reflected in current phase-plan files** at time of this analysis update; treat as a recommended update set pending explicit implementation in those files |
| Add `@skill.script` to Phase 3 decision options | **Validated as needed** |
| Add script-approval configuration alignment with compliance mode | **Validated as needed** |
| Track dynamic resources in compatibility planning (`SKILL-COMPAT.md`) | **Validated as needed** |

### 17.5 Recommended Plan-Level Follow-Through (Next Editing Pass)

When phase-plan files are next revised, apply the following in order:

1. `PHASE_3_AUTOMATION_EXTENSION.md`: add a deployment option for code-defined `@skill.script` and evaluate it before Azure Functions.
2. `PHASE_3_AUTOMATION_EXTENSION.md`: add configurable script-approval wiring (`script_approval_required`) tied to compliance mode.
3. `PHASE_0_PREREQUISITES.md`: extend `SKILL-COMPAT.md` skeleton with a "Future Enhancement Paths" table including dynamic-resource hydration.
4. `IMPLEMENTATION_PLAN_OVERVIEW.md` and `PHASE_4_FEATURE_CONSOLIDATION.md`: align risk/stack language with the above additions.

### 17.6 Bottom Line

This SDK update does not invalidate current AKR architecture. It improves the conditional Phase 3 decision tree and strengthens the compliance model with a low-effort, high-leverage addition: script-level approval for side effects. Capturing it now preserves optionality and reduces the risk of committing infrastructure before evaluating lower-cost in-process alternatives.

*Implementation-Ready Analysis — March 2026 — Engineering Standards — Confidential*

*Synthesizes: Review 1 (Claude, structural); Review 2 (GH Copilot Round 1, repository inspection); Review 3 (GH Copilot Round 2, charter size quantification); Review 4 (M365 Copilot, tooling evaluation); Review 5 (GH Copilot, module architecture response); Review 6 (GH Copilot, full schema audit of `akr-config-schema.json` and `consolidation-config-schema.json`); Review 7 (GH Copilot, final file inspection of `copilot-instructions.md`, `.akr/workflows/`, `tag-registry.json`); Module-Based Documentation Architecture clarification and `courses_service_doc.md` sample; Review 9 (Skill Optimization — three-layer reliability stack; LLM execution quality variance; `SKILL-COMPAT.md` + eval framework; `postToolUse` + `agentStop` hooks; `<!-- akr-generated -->` in-document contract); Review 10 (Agent Skills SDK update validation — `@skill.script`, script approval gating, dynamic resource enhancement path).*

---

# Part 18: Section-Scoped Generation (SSG) — Multi-Turn / Multi-Pass Architecture

**Date reviewed:** March 2026
**Review type:** Context window strategy — bridge architecture for charter fidelity under current token constraints
**Appends:** `akr_implementation_ready_analysis.md` as Part 18 (after Part 17: Agent Skills SDK Update)

---

## 18.1 Why SSG Is Being Adopted

The context window saturation problem (Part 3) is currently resolved by charter compression — reducing each charter from ~11,000 tokens to ~2,500 tokens before any source files load. This approach works but introduces a trade-off: condensed charters can lose the nuance and worked guidance that makes them effective generation guides, even when all required rules are preserved.

SSG is adopted as a complementary strategy to charter compression with three goals:

1. **Restore charter fidelity per section** — each generation pass loads only the charter guidance relevant to the section being written, not the full condensed charter for the entire document at once. This enables loading more complete section guidance without increasing total context load.

2. **Provide a defined path to full charter use** — as context windows grow, SSG passes can progressively load larger charter sections, and eventually the full charter per pass, without restructuring the generation pipeline.

3. **Enable background execution** — SSG's sequential pass structure maps naturally to the Copilot coding agent's multi-step task model, allowing generation to run in the background while developers work on other tasks.

SSG does **not** replace charter compression. Both strategies operate together: compression reduces the standing overhead of the charter; SSG reduces the per-section context load by loading only what each pass needs.

---

## 18.2 SSG Architecture — Pass Sequence for Backend Module Docs

The following pass sequence applies to `api-backend` and `microservice` project types. A parallel sequence for `ui-component` follows in section 18.3.

Each pass has:
- A **context budget** (what gets loaded)
- A **charter slice** (which section rules are loaded from the condensed charter)
- An **output** (what the pass produces)
- A **forward payload** (what gets passed to the next pass — summaries only, never raw files re-loaded)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PASS 1 — Module Inventory                                               │
│                                                                         │
│ Context loaded:  modules.yaml (file list + metadata only)               │
│ Charter slice:   Module Files section rules only                        │
│ Source files:    NOT loaded yet                                         │
│                                                                         │
│ Output:          Module Files section                                   │
│                  (each file with its role: Controller, Service, etc.)   │
│                                                                         │
│ Forward payload: File list with roles (compact — not full source)       │
│ Timing target:   ≤3 minutes                                             │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PASS 2 — Operations Map                                                 │
│                                                                         │
│ Context loaded:  All source files (read in full) + Pass 1 forward       │
│ Charter slice:   Operations Map section rules only                      │
│ Note:            This is the heaviest pass. For modules at the 8-file   │
│                  ceiling with large files, this pass may be split into  │
│                  2A (public operations) + 2B (private/internal) if the  │
│                  combined source load exceeds the per-pass token budget. │
│                                                                         │
│ Output:          Operations Map (all operations across all files)       │
│                                                                         │
│ Forward payload: Operations table (condensed — operation names,         │
│                  signatures, file origin; not full implementation)      │
│ Timing target:   ≤8 minutes (≤12 minutes for 8-file modules)           │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PASS 3 — Architecture Overview                                          │
│                                                                         │
│ Context loaded:  Pass 1 forward + Pass 2 forward (no raw files)         │
│ Charter slice:   Architecture diagram rules only                        │
│                                                                         │
│ Output:          Full-stack text diagram                                │
│                  (Controller → Service → Repository → DB table)         │
│                  No Mermaid; text-based only.                           │
│                                                                         │
│ Forward payload: Architecture summary (one paragraph)                  │
│ Timing target:   ≤3 minutes                                             │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PASS 4 — Business Rules                                                 │
│                                                                         │
│ Context loaded:  Pass 2 forward (operations table — method signatures   │
│                  and file origins are sufficient anchor for business    │
│                  rule extraction) + Pass 3 forward (architecture        │
│                  summary for layer context)                             │
│ Source files:    NOT re-read. The Pass 2 operations table contains the  │
│                  method signatures needed to identify rule extraction   │
│                  points. "Why It Exists" + "Since When" columns are     │
│                  human-supplied (❓ markers); no source re-read needed. │
│ Charter slice:   Business Rules section rules only                      │
│                  (Why It Exists + Since When columns)                   │
│                                                                         │
│ Output:          Business Rules table                                   │
│                  (AI-populated Name + Description columns from Pass 2   │
│                  signatures; ❓ markers on Why It Exists + Since When)  │
│                                                                         │
│ Forward payload: Business rules summary (rule names + brief rationale)  │
│ Timing target:   ≤5 minutes                                             │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PASS 5 — Data Operations                                                │
│                                                                         │
│ Context loaded:  Pass 2 forward (operations table already lists all     │
│                  DB-touching operations with file origins) + Pass 4     │
│                  forward (business rules as context for data patterns)  │
│ Source files:    NOT re-read. The operations table from Pass 2 already  │
│                  contains repository method signatures and their file   │
│                  origins, which is sufficient to map reads/writes.      │
│                  If a specific DB call pattern cannot be resolved from  │
│                  the operations table, mark as ❓ for Mode C review.    │
│ Charter slice:   Data Operations section rules only                     │
│                                                                         │
│ Output:          Reads/Writes table                                     │
│                                                                         │
│ Forward payload: Data operations summary (tables touched, patterns)     │
│ Timing target:   ≤3 minutes                                             │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PASS 6 — Questions & Gaps + YAML Front Matter + Transparency Markers    │
│                                                                         │
│ Context loaded:  All prior pass outputs assembled (no raw files)        │
│ Charter slice:   Marker syntax rules + frontmatter field requirements   │
│                                                                         │
│ Output:          ❓ markers, 🤖 markers, DEFERRED placeholders,         │
│                  YAML frontmatter (businessCapability, feature, layer,  │
│                  project_type, status, compliance_mode)                 │
│                  Questions & Gaps section                               │
│                                                                         │
│ Forward payload: Complete draft assembled from Pass 1–6 outputs         │
│ Timing target:   ≤3 minutes                                             │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PASS 7 — Assembly + Validation                                          │
│                                                                         │
│ Context loaded:  Complete draft from Pass 6 forward                     │
│ Actions:         Write <!-- akr-generated --> metadata header           │
│                  Run validate_documentation.py                          │
│                  Surface any failures as additional ❓ markers           │
│                  Write to doc_output path                               │
│                  Open draft PR                                          │
│                                                                         │
│ Output:          Final draft file + PR                                  │
│ Timing target:   ≤3 minutes                                             │
└─────────────────────────────────────────────────────────────────────────┘

Total target: ≤28 minutes (within the ≤30-minute system-level success criterion)
```

---

## 18.3 SSG Pass Sequence for UI Component Module Docs

The `ui-component` pass sequence follows the same forward-payload-only discipline as the backend sequence. Pass 2 reads all UI source files; Passes 3–5 operate exclusively on forward payloads.

| Pass | Section | Charter Slice | Source Files Loaded | Forward Payload Source |
|---|---|---|---|---|
| 1 | Module Files | Module Files rules | None (modules.yaml only) | — |
| 2 | Component Hierarchy + Hook Dependency Graph | Component hierarchy rules + hook graph rules | All UI source files | Component tree + hook dependency map (~500 tokens) |
| 3 | Type Definition Cross-Reference | Type definition rules | **None** — derived from Pass 2 component hierarchy output. Type relationships unresolvable from the hierarchy are marked ❓. | Pass 2 forward |
| 4 | State Management + Props Flow | State/props rules | **None** — props flows and state shapes are mapped from the component hierarchy and hook dependency graph in Pass 2 forward. | Pass 2 + Pass 3 forwards |
| 5 | Rendering Patterns + Side Effects | Rendering rules | **None** — rendering patterns are inferred from component hierarchy. Side-effect sources (useEffect triggers, API calls) are present in the hook dependency graph. Mark unresolvable patterns ❓. | Pass 2 + Pass 4 forwards |
| 6 | Questions & Gaps + Front Matter + Markers | Marker syntax + frontmatter rules | None (pass forwards only) | All prior pass forwards |
| 7 | Assembly + Validation | — | None (assembled draft) | Pass 6 assembled draft |

Timing targets mirror the backend sequence. Pass 2 is the heaviest for UI modules (component hierarchy + hook dependency graph is the equivalent of the Operations Map).

**UI source re-read override:** If a UI module has heavily type-annotated components where the type definitions are the primary structural guide (e.g., complex generic types that are not representable in a component hierarchy summary), a project-level override is available in `modules.yaml`:

```yaml
- name: CourseManagementUI
  ssg_pass3_source_reread: true   # Authorizes targeted type file re-read in Pass 3
```

The same schema and validator treatment applies as `ssg_pass4_source_reread` for backend modules (see NEW-2 resolution in section 18.8A).

**UI forward payload size targets:**

| Pass | Maximum Forward Payload Size |
|---|---|
| Pass 1 → Pass 2 | File list with roles (~200 tokens) |
| Pass 2 → Pass 3 | Component tree + hook graph: component names, props interfaces, hook names, dependency edges (~500 tokens) |
| Pass 3 → Pass 4 | Type summary: exported type names + shapes (~200 tokens) |
| Pass 4 → Pass 5 | State/props summary: state shapes, prop drilling paths (~250 tokens) |
| Pass 5 → Pass 6 | Rendering summary: render patterns, side-effect sources (~200 tokens) |
| Pass 6 → Pass 7 | Full assembled draft (no token limit — this is the document) |

---

## 18.4 Forward Payload Design — Preventing Context Re-Expansion

The most critical SSG discipline is the **forward payload rule**: each pass hands off a **condensed summary** of its output to the next pass — never the raw source files, never the full output text.

This rule prevents context re-expansion, where earlier passes accumulate in later context windows and recreate the saturation problem SSG is meant to solve.

**Forward payload size targets:**

| Pass | Maximum Forward Payload Size |
|---|---|
| Pass 1 → Pass 2 | File list with roles only (~200 tokens) |
| Pass 2 → Pass 3 | Operations table: names, signatures, file origins (~500 tokens) |
| Pass 3 → Pass 4 | Architecture summary: one paragraph (~150 tokens) |
| Pass 4 → Pass 5 | Business rules: rule names + brief rationale (~300 tokens) |
| Pass 5 → Pass 6 | Data operations: tables touched, read/write pattern names (~200 tokens) |
| Pass 6 → Pass 7 | Full assembled draft (all sections joined; no token limit — this is the document) |

The Pass 6 → Pass 7 handoff carries the complete draft because Pass 7's only job is final assembly, metadata header writing, and validation. No source files are re-read in Pass 7.

---

## 18.5 SSG and the `<!-- akr-generated -->` Metadata Header

The existing `<!-- akr-generated -->` metadata header (Part 5, Mode B Step 8) must be extended to record SSG pass execution evidence. This gives the CI gate visibility into which passes completed and whether any were skipped or split.

**Extended header format (no split):**

```markdown
<!-- akr-generated
skill: akr-docs
skill-version: v1.0.0
mode: B
steps-completed: 1,2,3,4,5,6,7,8,9
generation-strategy: section-scoped
template: lean_baseline_service_template.md
charter: backend-service.instructions.md
modules-yaml-status: approved
passes-completed: 1,2,3,4,5,6,7
passes-split:
pass-timings-seconds: pass1=142,pass2=597,pass3=98,pass4=213,pass5=117,pass6=134,pass7=89
total-generation-seconds: 1390
generated-at: 2026-03-17T09:23:41Z
-->
```

**Extended header format (Pass 2 split):**

```markdown
<!-- akr-generated
skill: akr-docs
skill-version: v1.0.0
mode: B
steps-completed: 1,2,3,4,5,6,7,8,9
generation-strategy: section-scoped
template: lean_baseline_service_template.md
charter: backend-service.instructions.md
modules-yaml-status: approved
passes-completed: 1,2A,2B,3,4,5,6,7
passes-split: 2A,2B
pass-timings-seconds: pass1=142,pass2a=287,pass2b=310,pass3=98,pass4=213,pass5=117,pass6=134,pass7=89
total-generation-seconds: 1390
generated-at: 2026-03-17T09:23:41Z
-->
```

**Field definitions:**

| Field | Description | Required |
|---|---|---|
| `generation-strategy` | `section-scoped`, `single-pass`, or `single-pass-fallback` | Yes |
| `passes-completed` | Comma-separated list of passes that completed. When Pass 2 is split, records `1,2A,2B,3,4,5,6,7` — not `1,2,3,...`. When `single-pass-fallback` occurred mid-run, records only the passes that completed before fallback (e.g., `1,2A,2B,3`). This allows the validator to confirm both sub-passes completed, not just that a split was attempted. | Yes |
| `passes-split` | Records the split type when a pass was divided (e.g., `2A,2B`). Serves as a flag for the split pattern in case future versions support other split types. Empty string if no split occurred. | No |
| `pass-timings-seconds` | Per-pass wall-clock time. Keys must match the actual pass IDs in `passes-completed` (e.g., `pass2a`, `pass2b` when split; `pass2` when not split). Value `unavailable` if the surface does not expose timing. | Yes |
| `total-generation-seconds` | Sum of all pass timings. Value `unavailable` if timing not available. | Yes |

`validate_documentation.py` must check:
- `generation-strategy` is present and has a valid value
- `passes-completed` contains all expected pass IDs: `1,2,3,4,5,6,7` (no split) or `1,2A,2B,3,4,5,6,7` (split). Both `2` and `2A,2B` are valid representations of pass 2 completion — the validator accepts either form.
- `passes-split` and `passes-completed` are consistent: if `passes-split: 2A,2B`, then `passes-completed` must contain `2A` and `2B`, not `2`
- `pass-timings-seconds` is present (value may be `unavailable`)
- `total-generation-seconds` is present (value may be `unavailable`)

---

## 18.6 Generation Time Metrics Framework

### Why Timing Data Matters

Per-pass and total generation time data serves three future planning purposes:

1. **Threshold-based routing** — if a module's generation time exceeds the slow-generation threshold (see section 18.8), it triggers the fallback escalation path rather than silently stalling.

2. **AI tooling evolution tracking** — as model speed and context window capacity improve, timing data from earlier periods allows quantitative comparison. A module that takes 28 minutes in 2026 may take 8 minutes in 2027; the historical record makes this improvement visible and guides decisions about whether SSG can be simplified or consolidated.

3. **Phase 3 authorization evidence** — if Phase 2.5 shows the coding agent is slow on large modules specifically at Pass 2 (the heaviest pass), that is targeted Phase 3 automation evidence for the Operations Map extraction step only, not a reason to replace the whole pipeline.

### Metrics to Collect

The following metrics must be collected during every Mode B generation run and stored in `.akr-config.json` monitoring output and `benchmark.json`:

| Metric | Where Collected | Granularity | Target Value |
|---|---|---|---|
| `pass_wall_clock_seconds` | `akr-generated` header + `session-*.jsonl` hook log | Per pass | See pass targets in 18.2 |
| `total_generation_seconds` | `akr-generated` header | Per module | ≤1,800 (30 minutes) |
| `pass2_split_occurred` | `passes-split` field | Boolean | False for modules ≤5 files |
| `source_file_token_count` | Logged by skill before Pass 2 | Per module | Informational |
| `charter_slice_token_count` | Logged by skill per pass | Per pass | Informational |
| `passes_completed_count` | Count of `passes-completed` | Per run | 7 (or 8 if Pass 2 split) |
| `validation_pass_on_first_run` | `validate_documentation.py` exit code | Per run | ≥95% of runs |
| `slow_pass_count` | Passes exceeding their individual target | Per run | 0 |

### `benchmark.json` SSG Schema Extension

The existing `benchmark.json` schema (Part 16.4) must be extended with an `ssg` key per model:

```json
{
  "last-updated": "YYYY-MM-DD",
  "schema-version": "1.1",
  "models": {
    "claude-sonnet-4-6": {
      "mode-a-standard":     { "pass-rate": null, "avg-tokens": null },
      "mode-b-coursedomain": { "pass-rate": null, "avg-tokens": null },
      "mode-b-large-module": { "pass-rate": null, "avg-tokens": null, "known-issue": null },
      "ssg": {
        "mode-b-coursedomain": {
          "avg-total-seconds": null,
          "avg-pass-seconds": {
            "pass1": null, "pass2": null, "pass3": null,
            "pass4": null, "pass5": null, "pass6": null, "pass7": null
          },
          "pass2-split-rate": null,
          "slow-module-rate": null
        },
        "mode-b-large-module": {
          "avg-total-seconds": null,
          "avg-pass-seconds": {
            "pass1": null, "pass2a": null, "pass2b": null, "pass3": null,
            "pass4": null, "pass5": null, "pass6": null, "pass7": null
          },
          "pass2-split-rate": null,
          "slow-module-rate": null
        }
      }
    },
    "gpt-4o": {
      "ssg": {
        "mode-b-coursedomain": {
          "avg-total-seconds": null,
          "avg-pass-seconds": { "pass1": null, "pass2": null, "pass3": null,
                                "pass4": null, "pass5": null, "pass6": null, "pass7": null },
          "pass2-split-rate": null,
          "slow-module-rate": null
        },
        "mode-b-large-module": {
          "avg-total-seconds": null,
          "avg-pass-seconds": { "pass1": null, "pass2a": null, "pass2b": null, "pass3": null,
                                "pass4": null, "pass5": null, "pass6": null, "pass7": null },
          "pass2-split-rate": null,
          "slow-module-rate": null
        }
      }
    },
    "coding-agent": {
      "ssg": {
        "mode-b-coursedomain": {
          "avg-total-seconds": null,
          "pass-timings-available": null,
          "avg-pass-seconds": {},
          "slow-module-rate": null
        }
      }
    }
  }
}
```

`null` values are populated after each eval run. `pass-timings-available` in the `coding-agent` block is a boolean populated in Phase 2.5 based on whether the coding agent surface exposes per-pass timing.

### `.akr-config.json` Monitoring Extension

The existing monitoring config (Part 12A, Addition A3) must include SSG timing metrics:

```json
"monitoring": {
  "enabled": true,
  "trackMetrics": [
    "generation-time",
    "validation-results",
    "human-input-completion",
    "cross-repo-sync",
    "ssg-pass-timings",
    "ssg-slow-module-events"
  ]
}
```

`ssg-pass-timings` records per-pass wall-clock times for every Mode B run.
`ssg-slow-module-events` records any module that exceeded the total or per-pass timing threshold, for later review.

---

## 18.7 SSG as a Long-Term Strategy — Assessment

### Where SSG Holds Up Long-Term

SSG's sequential pass structure mirrors how documentation is actually organized. The Operations Map does not depend on the Business Rules being written simultaneously; the Architecture Overview depends only on having the file list and operations already established. This decomposition reflects sound editorial process, not a workaround.

As context windows grow, SSG remains valuable for a different reason: focused, scoped generation produces more consistent output per section than loading everything at once. A model working on one section at a time is less prone to cross-section inconsistency, hallucinated relationships between sections, and token-budget-driven truncation of specific areas.

**SSG is durable as a pattern. The manual orchestration of passes is what gets replaced as AI tooling matures.**

### Where SSG Is Superseded

The following conditions would reduce or eliminate the need for SSG as a context management strategy (though not necessarily as a quality strategy):

| Condition | Impact on SSG |
|---|---|
| Context window reliably supports full charter + full module in one pass (~50K+ tokens effectively) | SSG becomes optional for small/medium modules; remains valuable for quality |
| Copilot coding agent supports native multi-step task decomposition with charter-section routing | SSG passes are automated by the platform rather than encoded in SKILL.md |
| `@skill.resource` dynamic hydration serves per-section charter content | SSG's charter-slice logic is offloaded to the resource layer |
| RAG/retrieval layer over charters is implemented (Phase 3+ Future Enhancement) | Retrieval replaces manual pass-level charter slicing |

These conditions are tracked in `SKILL-COMPAT.md` under "Future Enhancement Paths." When any condition is met, a `SKILL.md` revision is evaluated to simplify or consolidate SSG passes.

### Progressive Restoration Plan

As context windows grow, SSG passes can progressively load larger charter sections according to this restoration order:

1. **First to restore:** Worked examples back into charter slices (currently removed in compression; highest fidelity gain per token restored)
2. **Second:** Explanatory rationale for rules (helps model apply rules correctly in edge cases)
3. **Third:** Full charter section consolidation — multiple related sections merged into one pass (e.g., Business Rules + Data Operations in a single pass)
4. **Final state:** Single-pass generation with the full charter loaded — SSG collapses to the current Mode B single-shot approach, but now with full charter fidelity

This restoration order is documented in `CHARTER-RESTORATION-PLAN.md` (see Phase 0 addition in section 18.9 below).

---

## 18.8 Slow-Generation Fallback — Alternative for Long-Running Modules

### Threshold Definition

A module generation run is classified as **slow** if any of the following are true:

| Condition | Classification | Action |
|---|---|---|
| Any individual pass exceeds 2× its per-pass target | Slow pass | Log as `ssg-slow-module-event`; no automatic action |
| Total generation exceeds 45 minutes | Slow module | Trigger fallback escalation path |
| Pass 2 requires more than 2 splits (i.e., 3+ sub-passes) | Oversized module | Developer review required; consider splitting module |

The 45-minute threshold is set above the ≤30-minute target to distinguish degraded-but-acceptable performance from genuinely blocked generation.

### Fallback Escalation Path

When total generation exceeds 45 minutes:

```
SLOW GENERATION DETECTED
Total elapsed: [X] minutes — exceeds 45-minute threshold

Option 1: Continue with current pass sequence
  → Agent waits for current pass to complete before proceeding
  → No action required from developer
  → Recommended if background execution (coding agent) is running

Option 2: Use module splitting to reduce per-pass load
  → Developer reviews modules.yaml and splits the module into two smaller modules
  → Each sub-module is documented separately; docs are linked in a module-group header
  → Requires: re-running Mode A validation for the split; both modules ≤8 files
  → Add `module_group: [ParentModuleName]` field to modules.yaml for both sub-modules

Option 3: Use single-pass fallback for remaining sections
  → Remaining incomplete sections are generated in a single consolidated pass
  → Charter slice for this pass is the full condensed charter (not section-specific slices)
  → Lower fidelity than SSG; more ❓ markers expected
  → Validator will flag this via `generation-strategy: single-pass-fallback` in the header
  → Developer resolves additional ❓ markers in Mode C review
```

**The fallback is not a failure.** A document generated via `single-pass-fallback` for remaining sections is still a valid draft. The `generation-strategy` field in the metadata header communicates to the CI validator and the developer which sections were generated under which strategy, so review effort can be calibrated accordingly.

### Module Splitting Rules

If a module is consistently slow across multiple runs (recorded in `ssg-slow-module-events`), the recommended path is module splitting rather than repeated fallback generation:

- The module must be split into two sub-modules, each with ≤8 files
- Both sub-modules must share the same `businessCapability` tag
- A `module_group` field is added to both entries in `modules.yaml`:
  ```yaml
  - name: CourseDomainCore
    module_group: CourseDomain
    ...
  - name: CourseDomainInfrastructure
    module_group: CourseDomain
    ...
  ```
- `validate_documentation.py` recognizes `module_group` and links the two docs in output
- `consolidate.py` treats module_group members as a single logical unit for Level 3 feature consolidation

---

## 18.8A Review Findings — Resolved Issues

The following issues were identified during peer review of this document and are resolved here as binding clarifications.

---

### Risk 1 (Blocking): Phase 3 Scope Example 2 Reclassification

**Finding:** Phase 3 currently documents a "Scope Example 2: Chunked Context Processor" defined as:

> *"Failure mode: 'Large modules (8 files) truncate sections.' Root cause: Context window ceiling at ~25,000 tokens. Solution: Multi-pass processing: (1) extract structure, (2) generate per-section, (3) assemble. Lines: ~200 lines."*

SSG's Pass 1–7 sequence is exactly this solution, implemented in SKILL.md rather than a Python code-skill. Since SSG is baked into SKILL.md from Phase 1, "context window ceiling at 8 files" is **no longer a valid Phase 2.5 FAIL condition that authorizes Phase 3's chunked processor**. Leaving both creates two parallel chunking solutions with no decision rule for which applies.

**Resolution:**

Phase 3 Scope Example 2 ("Chunked Context Processor") is **reclassified** as follows when SSG is adopted:

| Condition | Old classification | New classification |
|---|---|---|
| Large module (8 files) produces truncated sections | Phase 2.5 FAIL → Phase 3 chunked processor | SSG handles via Pass 2 split; NOT a Phase 3 authorization condition |
| Operations Map incomplete due to **context overflow** | Phase 2.5 FAIL → Phase 3 chunked processor | SSG handles; not a Phase 3 trigger |
| Operations Map incomplete due to **AST comprehension failure** (model misses private/async methods regardless of context load) | No prior classification | Phase 2.5 FAIL → Phase 3 deterministic AST extractor (Scope Example 1 remains valid) |

**Required edit to `PHASE_3_AUTOMATION_EXTENSION.md`:** Remove "Context window ceiling at 8 files" from the authorization failure modes. Retain Scope Example 1 (deterministic operation extraction for AST comprehension failures) unchanged. Add a note:

> *"Note: Multi-pass chunking for context overflow (formerly Scope Example 2) is handled by SSG in SKILL.md. Phase 3 authorization on context grounds requires evidence that SSG Pass 2 split produces structurally incomplete output even when executed correctly — i.e., the model comprehends the content but cannot produce a complete Operations Map from correct method signatures. This is an AST comprehension failure, not a context failure, and is addressed by Scope Example 1's deterministic extractor."*

**Phase 2.5 FAIL conditions update:** In `PHASE_2_5_CODING_AGENT_SPIKE.md` Deliverable 5 failure mode table, replace:

> *"'Operations Map only 60% complete' → Context window ceiling at ~25,000 tokens → Authorize Phase 3 chunked processor"*

With:

> *"'Operations Map incomplete after SSG Pass 2 split executed correctly' → AST comprehension failure (model misses private/async methods) → Authorize Phase 3 deterministic AST extractor (Scope Example 1)"*

---

### Risk 2 (Blocking): Pass 4 and Pass 5 Source Re-Read Contradiction — Resolved

**Finding:** The original Pass 4 loaded "domain-logic files only (Service + Repository)" and Pass 5 loaded "DB-touching files only (Repository implementation)" — both direct source re-reads after Pass 2 had already read all files. This contradicts the forward payload discipline stated in section 18.4.

**Resolution:** Applied directly to Pass 4 and Pass 5 definitions in section 18.2. Both passes now operate exclusively on forward payloads from prior passes:

- **Pass 4** uses the Pass 2 operations table (method signatures and file origins) as the anchor for business rule name and description extraction. "Why It Exists" and "Since When" columns are inherently human-supplied and carry ❓ markers — no source re-read is required for those columns.
- **Pass 5** uses the Pass 2 operations table to map database operations (repository method signatures already identify the read/write patterns). Specific DB call details that cannot be resolved from signatures are marked ❓ for Mode C resolution.

If a team finds that business rules extraction from the operations table is insufficient for a particular codebase (e.g., heavily commented service files where the comments are the primary business rule source), they may authorize a targeted source re-read for Pass 4 only, documented as a project-level override in `modules.yaml` with `ssg_pass4_source_reread: true`. This override is not the default.

---

### Risk 3: SSG SKILL.md Authoring Time — Scope Assessment

**Finding:** The Phase 0 SKILL.md task table provides no time estimate for adding the SSG pass sequence to Mode B. INSERT 3B replaces ~10 lines of Steps 3–4 with an ~80-line structured pass sequence including timing enforcement, forward payload caps, split logic, and fallback escalation.

**Resolution:** The following time estimates are added to the Phase 0 SKILL.md authoring task table (see PHASE_UPDATES.md INSERT 2E for the full task row additions):

| Task | Estimated Time |
|---|---|
| Author SSG pass sequence (Pass 1–7) in SKILL.md Mode B | 4 hours |
| Author slow-generation escalation handler in SKILL.md | 1 hour |
| Author 4 new SSG eval cases (`evals/cases/ssg-*.yaml`) | 3 hours |
| Validate SSG pass sequence against eval cases (3 runs each) | 2 hours |
| **SSG SKILL.md total addition to Phase 0** | **~10 hours (1.5 days)** |

**Assessment:** If Phase 0 is already committed to a 1-2 week timeline, SSG SKILL.md authoring is additive scope. Two options:

- **Option A (Recommended):** Keep SSG SKILL.md authoring in Phase 0, extend Phase 0 timeline by 2 days. SSG eval cases provide coverage that also validates the non-SSG skill flow, so there is partial test consolidation value.
- **Option B:** Defer SSG pass sequence to Phase 1 Deliverable 2 (SKILL.md authoring). Phase 0 establishes charter section heading structure (INSERT 2A) and `benchmark.json` schema 1.1 (OBS-3 below), but does not implement SSG in the skill yet. Phase 1 SKILL.md authoring then includes the full SSG sequence. Phase 0 eval cases are reduced to the non-SSG baseline.

The standards lead must decide between Options A and B before Phase 0 begins. This document does not pre-commit to either.

---

### OBS-1: Success Metric Clarification — SSG 30-Minute Target vs. Full-Cycle 45-Minute Target

**Finding:** INSERT 1B adds "SSG total generation time per module: ≤30 minutes" alongside the existing "Time-to-first-documented-PR: ≤45 minutes (grouping + generation + review)." These can appear contradictory since Mode A alone can take 10–15 minutes.

**Resolution:** Add the following clarifying note to INSERT 1B immediately after the 30-minute bullet:

> *Note: The 30-minute SSG target covers Mode B generation only (SSG Passes 1–7). It is not the full Mode A → Mode B → review cycle. The existing 45-minute Phase 2 success metric covers the full cycle and remains unchanged. A compliant workflow could be: Mode A grouping validation (10 min) + Mode B SSG generation (≤30 min) + developer review setup (5 min) = 45 minutes total.*

---

### OBS-2: `passes-completed` vs. `steps-completed` Field Name Resolution

**Finding:** The existing `<!-- akr-generated -->` header uses `steps-completed: 1,2,3,4,5,6,7,8,9` (the 9 Mode B workflow steps). SSG introduces `passes-completed: 1,2,3,4,5,6,7` (SSG generation passes — a sub-sequence within workflow Steps 3–4). These are semantically different and the validator checks both.

**Resolution:** Both fields coexist with distinct semantics. The header format is:

```markdown
<!-- akr-generated
...
steps-completed: 1,2,3,4,5,6,7,8,9
generation-strategy: section-scoped
passes-completed: 1,2,3,4,5,6,7
passes-split: (empty if no split; 2A,2B if Pass 2 was split)
pass-timings-seconds: pass1=142,...
total-generation-seconds: 1390
...
-->
```

- `steps-completed` = Mode B workflow steps (reading modules.yaml, loading charter, generating, writing, validating, opening PR). This field pre-exists SSG and its validator check is unchanged.
- `passes-completed` = SSG generation passes. This is a new field, only present when `generation-strategy: section-scoped`. The validator checks it only when `generation-strategy` is set to `section-scoped` or `single-pass-fallback`.
- When `generation-strategy: single-pass-fallback`, `passes-completed` records which passes ran before fallback triggered (e.g., `passes-completed: 1,2,3`; remaining sections completed via fallback).

This resolution must be reflected in INSERT 3A's validator rules and in the SKILL.md header format block in INSERT 3B.

---

### OBS-3: `benchmark.json` Schema Version at Phase 0 vs. Phase 1

**Finding:** Part 18.6 changes schema-version from `"1.0"` to `"1.1"` but does not specify which phase establishes `1.1`. If SSG eval cases are committed in Phase 0 (INSERT 2C), the schema must be `1.1` from the start.

**Resolution:** The schema version at each phase exit gate is:

| Phase | `benchmark.json` schema-version | Notes |
|---|---|---|
| Phase 0 exit | `1.1` | SSG `ssg` key present with null values; established at Phase 0 even if SSG SKILL.md is deferred to Phase 1 (Option B above). The schema is a Phase 0 artifact; the data is populated later. |
| Phase 1 exit | `1.1` | SSG baseline pass rates populated from Phase 1 SKILL.md authoring validation runs |
| Phase 2.5 exit | `1.1` | `coding-agent` → `ssg` key populated |

The `1.0` → `1.1` bump is a Phase 0 deliverable regardless of whether SSG SKILL.md authoring is in Phase 0 or Phase 1.

---

### NEW-1: UI Pass Sequence Source Re-Reads — Resolved

**Finding:** The original UI pass sequence table in section 18.3 listed source file re-reads in Passes 3 (Type files), 4 (Component + hook files), and 5 (Component files) — the same structural violation as the backend Risk 2.

**Resolution:** Applied directly to section 18.3. The UI pass sequence now follows identical forward-payload-only discipline:

- **Pass 3 (Type Definitions):** Derived from Pass 2 component hierarchy output. Type relationships unresolvable from the hierarchy receive ❓ markers.
- **Pass 4 (State/Props):** Props flows and state shapes mapped from the component hierarchy and hook dependency graph in Pass 2 forward.
- **Pass 5 (Rendering Patterns):** Rendering patterns inferred from component hierarchy; side-effect sources present in hook dependency graph.

The same project-level override pattern (`ssg_pass3_source_reread: true` in `modules.yaml`) is available for heavily type-annotated UI modules, subject to the same schema/validator treatment as `ssg_pass4_source_reread`.

---

### NEW-2: `ssg_pass4_source_reread` / `ssg_pass3_source_reread` Schema Fields Not in Task Tables — Resolved

**Finding:** The override fields added in the Pass 4 fix (backend) and Pass 3 fix (UI) are undocumented schema additions with no task rows to add them to `modules-schema.json`, `validate_documentation.py`, or the `modules.yaml` example.

**Resolution:** The following task rows must be added to Phase 1 Deliverable 3 (schema updates task table). See PHASE_UPDATES.md INSERT 3E for the exact table rows.

Fields to add to `modules-schema.json`:

```json
"ssg_pass4_source_reread": {
  "type": "boolean",
  "default": false,
  "description": "Authorizes targeted Service file re-read in SSG Pass 4 for modules where service-file comments are the primary business rule source. Not recommended as a default. Document rationale in modules.yaml notes field."
},
"ssg_pass3_source_reread": {
  "type": "boolean",
  "default": false,
  "description": "Authorizes targeted type file re-read in SSG Pass 3 for UI modules where complex generic type annotations are not representable in component hierarchy summaries."
}
```

`validate_documentation.py` reads these fields during modules.yaml schema validation and records the override in the validation output summary. The `passes-completed` field in the metadata header records the override as `pass4-override` or `pass3-override` when triggered.

---

### NEW-3: Slow-Generation Fallback Agent Autonomy Clarification — Resolved

**Finding:** INSERT 3C presented Option A (module splitting) as a choice the agent offers, implying it might execute it. Module splitting requires a `modules.yaml` PR through the standards team — the agent cannot do this unilaterally.

**Resolution:** The SKILL.md slow-generation handler is clarified as follows (also reflected in INSERT 3C update in PHASE_UPDATES.md):

- **Option A (module splitting)** is presented as a recommendation for the developer to pursue **after the PR is merged**, not as an agent-executable action. The agent documents the slow-module event and proceeds to Option B automatically in background mode.
- **Option B (single-pass fallback)** is the agent's autonomous path. The agent never waits for a developer decision in background mode — it records `generation-strategy: single-pass-fallback` and opens the PR with a PR checklist note flagging the slow-module event.
- In interactive VS Code mode, the agent notifies the developer before proceeding to Option B, giving them the opportunity to interrupt and manually execute Option A instead.

---

### NEW-4: `passes-completed` Split Encoding — Resolved

**Finding:** When Pass 2 was split, `passes-completed: 1,2,3,4,5,6,7` did not distinguish whether both 2A and 2B completed — the split was only indicated by `passes-split`. The validator could not confirm both sub-passes ran.

**Resolution:** Applied directly to section 18.5:

- When a split occurs, `passes-completed` records the actual execution sequence: `1,2A,2B,3,4,5,6,7`
- `passes-split` remains as a flag for the split type (to support future split patterns beyond 2A/2B)
- The validator accepts both `2` (no split) and `2A,2B` appearing in `passes-completed` as valid pass 2 completions, and checks that `passes-split` and `passes-completed` are consistent
- When `single-pass-fallback` occurs, `passes-completed` records only the passes that completed before fallback (e.g., `1,2A,2B,3`)

---

### NEW-5: `ssg-forward-payload.yaml` Eval Case Verifiability — Resolved

**Finding:** The assertion "Passes 3–7 context does not include source file content (tested by token count comparison)" is not mechanically verifiable in the Agent Skills eval framework, which tests output artifacts — not model execution context.

**Resolution:** `ssg-forward-payload.yaml` is reclassified from an automated eval assertion to a **manual observation checklist item**. See PHASE_UPDATES.md INSERT 2C update for the revised eval case table.

The verifiability proxy used is behavioral: the standards author runs a Mode B eval on a known 5-file module, observes the SKILL.md self-reporting block output for each pass (which lists "Steps followed: …"), and records whether any pass beyond Pass 2 reports loading source files. This is recorded as a binary YES/NO observation in `benchmark.json` rather than an automated assertion. The `pass-timings-seconds` data provides a secondary proxy: if Pass 3 timing is unexpectedly close to Pass 2 timing, it warrants manual inspection.

---

## 18.9 SSG — Additions Required in Other Parts of This Analysis

The following table summarizes where existing parts of this analysis require additions or cross-references due to SSG adoption. These are the source of the targeted updates in the phase plan files.

| Part | Required Addition |
|---|---|
| Part 3 (Context Resolution) | Add Layer 5: SSG as a fifth resolution layer (after Layers 1–4) |
| Part 5 (Agent Skill Specification) | Add SSG pass sequence to Mode B steps 3–4; add forward payload discipline; add `passes-completed` + `pass-timings-seconds` to the `akr-generated` header |
| Part 6 (validate_documentation.py) | Add SSG header field validation; add slow-generation warning; add `passes-split` handling; add `single-pass-fallback` detection |
| Part 11 (Pre-Pilot Tests) | Add SSG timing measurement to Test 1 and Test 3 acceptance criteria |
| Part 12A (Schema Audit) | Add `ssg-pass-timings` and `ssg-slow-module-events` to monitoring trackMetrics list |
| Part 16 (Skill Reliability) | Add SSG execution quality note to LLM-dependent execution quality table; add `ssg-avg-total-seconds` to benchmark.json schema |

---

## 18.10 Relationship to Existing Architecture Decisions

SSG does not change any locked decision. It adds a generation strategy layer on top of the existing Mode B workflow:

| Existing Decision | SSG Addition |
|---|---|
| Charter compression as Phase 0 blocking precondition (Part 3) | SSG reduces per-pass context load; compression still required to keep each pass within budget |
| Agent Skill Mode B as primary generation workflow (Part 5) | SSG is implemented as a structured Mode B pass sequence, not a separate mode |
| `validate_documentation.py` as CI gate (Part 6) | Extended with SSG header field validation and slow-generation warning |
| Three-layer reliability stack (Part 16) | Unchanged; `passes-completed` field in metadata header is an addition to Layer 3 evidence |
| Phase 2.5 coding agent test (Phase 2.5) | New Criterion 11 tests SSG pass sequence completion in async context |
| `benchmark.json` eval framework (Part 16.4) | Extended with `ssg` key per model for timing data |

---

*Part 18 — Section-Scoped Generation (SSG) Architecture — March 2026 — Engineering Standards — Confidential*
