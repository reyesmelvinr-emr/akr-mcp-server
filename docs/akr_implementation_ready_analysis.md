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
| CI gate | `validate_documentation.py` + Vale | Validates required sections, markers, `project_type`, `feature_tag` format | Automated at PR merge |

This is the correct HITL model: **validate the grouping** (fast, developer-present, before generation), then **validate the content** (PR review, before merge).

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

## Part 5: The Agent Skill — Two-Mode Specification

The Agent Skill is the primary workflow encoding mechanism. A single `SKILL.md` works across VS Code agent mode, the Copilot coding agent, and the Copilot CLI. Mode A must precede Mode B — this sequencing is enforced by the skill's explicit prerequisite check.

```markdown
# .github/skills/akr-docs/SKILL.md

---
name: akr-docs
description: Propose module groupings and generate module documentation following
             AKR templates, charters, and validation rules. Two modes: Mode A
             (grouping proposal) must complete before Mode B (documentation generation).
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
   - [ ] CODEOWNERS notified for review
```

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
- Two-mode Agent Skill invocation guidance (when to use Mode A vs. Mode B)

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


### Tooling Architecture (Confirmed Across All Five Reviews)

```
┌───────────────────────────────────────────────────────────────┐
│  DEVELOPER WORKFLOW (IDE surface)                             │
│                                                               │
│  Agent Skills (SKILL.md)                                      │
│  → Encodes AKR procedure (Mode A + Mode B)                    │
│  → Auto-loads across: VS Code agent mode +                    │
│    Copilot coding agent + Copilot CLI                         │
│  → Free; no infrastructure; runs on existing Copilot seats   │
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
| Charter compression before pre-pilot spike | ✅ Final | Guaranteed failure without it; not a risk to test |
| Phase 4 as deterministic Python + human refinement | ✅ Final | Eliminates unverified Assumption 4 |
| `project_type` and `layer` as separate fields | ✅ Final | Different concepts; different validation rules |
| `TEMPLATE_MANIFEST.json` narrowed to version registry | ✅ Final | Skill-template version coupling requires it; other roles deprecated |
| Phase 3 conditional on Phase 2.5 failure | ✅ Final | Cannot justify Azure Function without evidence coding agent is insufficient |

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
| 1 — Code Analysis Capability | Copilot + condensed charter extracts module-level content correctly | Agent correctly groups 5 files into one CourseDomain doc; covers Controller + Service + Repository + DTOs in a single output; ≥90% section match across 3 runs | Hybrid: retain `CodeAnalyzer` from `akr-mcp-server` for deterministic extraction; hosted MCP for governance |
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
| Agent Skill has two modes (not one) | Module architecture | 🟡 High | Mode A (grouping) must precede Mode B (generation) |
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
| `copilot-instructions.md` rewrite scope underestimated | Review 7 (File Inspection) | 🔴 Blocking for Phase 1 | Full document replacement (~3–4 hours); only Core Principles, completeness scoring, and Vale gate reference are retained |
| `validate-documentation.yml` already exists and calls `validate_documentation.py` | Review 7 (File Inspection) | 🟡 High | Phase 1 CI task is ADAPT not BUILD; four targeted changes only |
| `tag-registry.json` PascalCase vs. free-text `feature` field mismatch | Review 7 (File Inspection) | 🔴 Blocking for pilot | Fix `feature` field to PascalCase in `modules.yaml`; add `CourseCatalogManagement` entry in Phase 0 |

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
  □ Create .github/skills/akr-docs/SKILL.md with Mode A + Mode B.
    Use the two-mode specification from Part 5 of this document.
    Reference condensed charters (not full charters) in Mode B step 2.

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
| Agent Skill has Mode A (grouping) + Mode B (generation) | Module architecture; sequencing enforced by skill |
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

### Still Open — Requires Input or Testing

| Decision | Open Question | How to Resolve |
|---|---|---|
| Hosted MCP context source availability | Available at current GitHub Copilot Business tier? | Pre-pilot Test 2 |
| Copilot coding agent premium request rate | What is the per-session cost at team scale? | GitHub billing dashboard + M365 estimator |
| Copilot Studio Doc Review agent | Are M365 Copilot licenses available? | Check licensing |
| `allowWorkflowBypass` default value in `config.json` | Does the dev config ship with bypass enabled? | Code inspection; confirms whether config gate is nominal |
| `copilot-instructions.md` character limit | Is ~4,000 characters sufficient for condensed backend charter? | Test during charter compression |
| Template adaptation acceptance | Does adapted `lean_baseline_service_template.md` produce output matching `courses_service_doc.md`? | Phase 1 deliverable; `courses_service_doc.md` is the spec |

---

## Part 15: Summary of What Each Major Input Contributed

| Input | What It Permanently Changed |
|---|---|
| Review 1 (Claude) | Pre-pilot assumptions as blocking gate; version drift policy; Phase 3 infrastructure concern; `max_files_per_module` governance constraint |
| Review 2 (GH Copilot R1) | Context saturation identified; coding agent as Phase 2.5; `test_pipeline_e2e.py` as acceptance criteria baseline |
| Review 3 (GH Copilot R2) | Charter sizes quantified → compression becomes Phase 0 blocking; `force_workflow_bypass` corrected; template count corrected to 10; `.akr/workflows/` asset identified |
| Review 4 (M365 Copilot) | Agent Skills as primary cross-surface workflow primitive; Copilot Studio for non-developer HITL; premium request metering; `TEMPLATE_MANIFEST.json` retention (narrowed) |
| Review 5 (Module Architecture) | Three-tier hierarchy defined; two-mode Agent Skill specified; `modules.yaml` full schema; `validate_documentation.py` scope upgraded; `layer` vs. `project_type` distinction; `consolidate.py` input contract revised; `copilot-instructions.md` rewrite scope elevated |
| Review 6 (Schema Audit) | Four corrections: `modules-schema.json` is new; `consolidation-config-schema.json` needs `modulesManifestPath`; dual cross-repo config split documented; `project_type` not in existing `requiredTags`. Three additions: `humanInput` schema aligns with HITL model; `warnOnMissingLayers` is existing logic; `monitoring` schema enables Phase 0 cost baseline |
| Review 7 (Final File Inspection) | `copilot-instructions.md` is a full replacement (52-line slash-commands section, Tree-sitter section, YAML front matter, directory structure, troubleshooting — all removed); `validate-documentation.yml` already exists and calls the script (Phase 1 CI = adapt, not build; five adaptations including URL fix); `tag-registry.json` uses PascalCase keys incompatible with free-text `feature` field examples |
| Review 8 (Final File Inspection 2) | CRITICAL: `validate_documentation.py` does not exist anywhere; must be created from scratch as Phase 1 deliverable at `.akr/scripts/validate_documentation.py`. Workflow download URL currently 404 and must be corrected. This is separate from workflow adaptation task. Also confirmed: `tag-registry-schema.json` `layers` array and `consolidation-config-schema.json` `repositories[].layer` both omit `Full-Stack` intentionally (separate from `modules-schema.json` which will include it) |
| Module Architecture Clarification | `courses_service_doc.md` confirmed as Level 1 acceptance criterion; module grouping rules; database object separation invariant; template adaptation is multi-file scope, not new sections |

---

*Implementation-Ready Analysis — March 2026 — Engineering Standards — Confidential*

*Synthesizes: Review 1 (Claude, structural); Review 2 (GH Copilot Round 1, repository inspection); Review 3 (GH Copilot Round 2, charter size quantification); Review 4 (M365 Copilot, tooling evaluation); Review 5 (GH Copilot, module architecture response); Review 6 (GH Copilot, full schema audit of `akr-config-schema.json` and `consolidation-config-schema.json`); Review 7 (GH Copilot, final file inspection of `copilot-instructions.md`, `.akr/workflows/`, `tag-registry.json`); Module-Based Documentation Architecture clarification and `courses_service_doc.md` sample.*
