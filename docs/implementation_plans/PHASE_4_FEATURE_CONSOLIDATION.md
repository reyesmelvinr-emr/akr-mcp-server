# Phase 4: Cross-Repository Feature Consolidation — Implementation Plan

**Duration:** 3-4 weeks  
**Team:** Standards team (1 FTE) + Product Owner (0.25 FTE for testing)  
**Prerequisite:** Phase 2 stable ≥6 weeks; zero bypass events; all pilot docs tagged  
**Target:** Deterministic Python aggregator producing Level 3 feature docs

---

## Overview

Phase 4 aggregates Level 1 (module docs) and Level 2 (database object docs) across multiple repositories into Level 3 feature consolidation documents. This enables Product Owners and QA Leads to understand full-stack features that span UI, API, and database layers owned by different teams.

**Key Design Decision:** `consolidate.py` is **deterministic Python**—no AI invocation from GitHub Actions. The non-deterministic part (synthesizing coherent business narrative) is done by the Product Owner with Copilot agent mode assistance on the structured draft.

> **Phase 4 + Agent Skills SDK:** If `consolidate.py` is ever invoked by a custom agent (not the
> current GitHub Actions path), the `script_approval_required` flag from `.akr-config.json` should
> gate execution before file writes occur. See **Deliverable 2D** in Phase 3 for the reference
> implementation pattern. For the current Phase 4 deterministic GitHub Actions path, no approval
> mechanism is needed — the PR itself is the HITL checkpoint.

---

## Skill Re-Evaluation Prerequisite

### Why Required Before Phase 4

At least 6 weeks will have elapsed since the Phase 1 `benchmark.json` baseline was recorded. Model updates to GitHub Copilot (GPT-4o) or Claude may have occurred silently during this period. Phase 4 documentation runs on multiple repositories - a skill regression discovered mid-Phase 4 is far more disruptive than one caught before it begins.

### Re-Evaluation Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Re-run `evals/cases/` full suite on baseline-pinned model versions | Standards author | All three eval cases run against the same model version strings recorded in Phase 1 `benchmark.json` baseline; results recorded | 4 hours |
| Compare results to Phase 1 `benchmark.json` baseline | Standards author | Pass rate delta documented; any regression >10% flagged for team review | 1 hour |
| Update `benchmark.json` with Phase 4 pre-run results | Standards author | New entries added alongside Phase 1 and pilot entries; `last-updated` field current | 30 min |
| Run supplemental eval on newer model versions (if available) | Standards author | New model versions recorded as separate entries; not used to replace baseline comparison rows | 1 hour |
| Update `SKILL-COMPAT.md` if pass rates changed | Standards author | Matrix rows updated; any new GPT-4o failure modes documented with workaround | 1 hour |
| Communicate regressions before Phase 4 documentation runs begin | Standards lead | If pass rate dropped >10%, team briefed; `SKILL.md` updated and re-distributed before Phase 4 runs | External |
| Review Agent Framework SDK release notes for dynamic resource capabilities | Standards author | Check if `@skill.resource` dynamic resources can replace static `benchmark.json` and `standards_version` reads; document finding in `SKILL-COMPAT.md` | 30 min |

> **Dynamic Resources (future enhancement path):** The Agent Framework SDK supports `@skill.resource`
> decorated functions that execute at read time, returning live data from repos, APIs, or config
> files rather than static snapshots. If charter staleness or stale `benchmark.json` thresholds
> become an observed problem during Phase 4 multi-repo runs, migrating these to dynamic resources
> is the recommended upgrade path. This requires building a custom Python `SkillsProvider` to
> replace the file-based `SKILL.md` delivery mechanism — evaluate scope before committing.
> Track in `SKILL-COMPAT.md` under "Future Enhancement Paths."

### Gate: Phase 4 Documentation Runs Must Not Begin Until

- Re-evaluation complete
- `benchmark.json` updated
- Any regressions >10% resolved or explicitly accepted with documented rationale

---

## Acceptance Criteria

Phase 4 is complete when:

1. ✅ Tag registry assessed: evolve `tag-registry.json` or create new `feature-registry.yaml`
2. ✅ `consolidation-config-schema.json` updated with `modulesManifestPath` field
3. ✅ `consolidate.py` implemented as deterministic aggregator (~300-400 lines); `script_approval_required` flag read from `.akr-config.json` if consolidation is invoked via a custom agent with script execution
4. ✅ Workflow deployed: `.github/workflows/consolidate-feature.yml` in Feature repo
5. ✅ Dual config reading: `akr-config-schema.json` (participation) + `consolidation-config-schema.json` (execution)
6. ✅ Input contract tested: module docs as atomic units for API/UI; individual DB objects
7. ✅ 3-component feature consolidated end-to-end (UI + API + DB)
8. ✅ Consolidation completes in <2 minutes (sparse checkout verified)
9. ✅ Product Owner refinement workflow tested
10. ✅ `warnOnMissingLayers` reads existing config flag (not re-implemented)
11. ✅ Skill re-evaluation complete: `evals/` suite re-run; `benchmark.json` updated; any pass-rate regressions resolved before Phase 4 documentation runs begin

**Exit Gate:** Phase 4 retrospective complete; feature consolidation workflow operational.

---

## Prerequisite: Phase 2 Stability

### Why 6-Week Wait?

Phase 4 depends on **stable, tagged Level 1 and Level 2 documentation** across multiple repositories. Starting too early results in:
- Incomplete module docs (teams still onboarding)
- Inconsistent `feature` tagging
- Churn as teams correct groupings

### Stability Metrics

| Metric | Target | Why |
|---|---|---|
| **Zero bypass events** | 6 consecutive weeks | Proves governance is enforced |
| **Module doc coverage** | ≥80% of services documented | Ensures consolidation has input |
| **Business capability tagging consistency** | All docs have valid `businessCapability` field in YAML metadata | Enables cross-repo matching |
| **Validation pass rate** | ≥95% on first PR | Proves validator accuracy |

**Gate ceiling and override path:** If the zero-bypass threshold is not met within 12 weeks after Phase 2 completion, standards lead may authorize Phase 4 with documented bypass trend analysis, mitigations, and explicit written risk acceptance.

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Track stability metrics | Standards author | 6-week dashboard; all targets met | Ongoing |
| Audit businessCapability tag usage | Standards author | All pilot docs have valid `businessCapability` tags from tag-registry.json | 1 hour |
| Confirm zero bypasses | Standards author | Git logs show no `allowWorkflowBypass` use | 30 min |
| Authorize Phase 4 start | Standards lead | Stability targets met; Phase 4 green-lit | Sign-off |

---

## Prerequisite: Feature Documentation Repository

### Objective

Create and configure the centralized feature documentation repository (`feature-docs`) where Level 3 consolidated documentation will live.

**Critical:** This repository must exist before Phase 4 begins. It is not mentioned in earlier phases and must be created as a Phase 4 prerequisite.

### Repository Setup

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| **Create `feature-docs` repository** | Infrastructure lead | Repository created in org with appropriate visibility (private/internal) | 30 min |
| Initialize with README | Standards author | README explains purpose: "Cross-repository feature documentation consolidation" | 30 min |
| Configure branch protection | Infrastructure lead | `main` branch requires PR reviews; no direct commits  | 15 min |
| Add CODEOWNERS | Standards author | Product Owners + Standards team own `docs/features/**` | 15 min |
| Create directory structure | Standards author | `docs/features/` directory created | 5 min |
| Configure GitHub Actions permissions | Infrastructure lead | Workflow can read from other repos (use PAT), write to this repo | 30 min |
| Define consolidation PAT and SSO requirements | Infrastructure lead | PAT scopes documented (`contents:read` on source repos, `contents:write` + `pull-requests:write` on `feature-docs`, `metadata:read`); SAML/SSO authorization steps documented for org repos | 30 min |

### Directory Structure

```
feature-docs/
  README.md                          # Purpose and usage guide
  docs/
    features/                        # Level 3 consolidated docs live here
      CourseCatalogManagement_doc.md # Example
      EnrollmentWorkflow_doc.md      # Example
  .github/
    workflows/
      consolidate-feature.yml        # Deployed in Deliverable 4
    CODEOWNERS                       # Product Owners + Standards team
```

### Notes

- This repository aggregates read-only from application repos; does not contain source code
- Access control: Read access for all developers; write access via PR approval from Product Owners
- Naming convention: Use organization-specific naming (e.g., `org-feature-docs`, `training-feature-docs`)

---

## Deliverable 1: Feature Registry Architecture

### Objective

Decide whether to evolve `tag-registry.json` or create new `feature-registry.yaml`; avoid duplication.

### Background (From Analysis)

**Existing workflow:** `distribute-tag-registry.yml` already governs `tag-registry.json` distribution:
- Triggers on `tag-registry.json` changes
- Validates against `tag-registry-schema.json`
- Distributes to application repos automatically

**Decision:**
- **Option A:** Extend `tag-registry.json` with cross-repo participation metadata
- **Option B:** Create new `feature-registry.yaml` with explicit cross-repo mappings

### Option A: Evolve `tag-registry.json`

**Add to each feature entry:**
```json
{
  "CourseCatalogManagement": {
    "approved": true,
    "domain": "Training",
    "description": "Course catalog browsing and enrollment",
    "owner": "Product Team A",
    "status": "active",
    
    // NEW: Cross-repo participation
    "repositories": [
      {
        "repo": "training-ui",
        "layer": "UI",
        "modules": ["CourseCatalogPage", "CourseCard"]
      },
      {
        "repo": "training-api",
        "layer": "API",
        "modules": ["CourseDomain"]
      },
      {
        "repo": "training-db",
        "layer": "Database",
        "objects": ["training.Courses", "training.Enrollments"]
      }
    ]
  }
}
```

**Pros:**
- Single source of truth
- Existing distribution workflow reused
- No parallel file to maintain

**Cons:**
- Mixes governance (approved features) with operational (repo participation)
- Schema becomes more complex

### Option B: Create `feature-registry.yaml`

**New file in `core-akr-templates`:**
```yaml
# feature-registry.yaml — Cross-Repository Feature Mapping
# Maps feature_tag keys (from tag-registry.json) to participating repositories

features:
  CourseCatalogManagement:
    display_name: Course Catalog Management
    owner: Product Team A
    repositories:
      - repo: training-ui
        layer: UI
        modules:
          - CourseCatalogPage
          - CourseCard
      
      - repo: training-api
        layer: API
        modules:
          - CourseDomain
      
      - repo: training-db
        layer: Database
        objects:
          - training.Courses
          - training.Enrollments
```

**Pros:**
- Clear separation of concerns
- Easier to validate cross-repo structure
- Does not pollute governance registry

**Cons:**
- Parallel file to maintain
- Must not duplicate `tag-registry.json` keys (validation required)

### Recommendation

**Option A (Evolve)** if:
- `tag-registry.json` is already used for operational data
- Distribution workflow can handle additional fields without breaking

**Option B (New file)** if:
- `tag-registry.json` is strictly governance-only
- Cross-repo mappings are expected to change frequently (independent lifecycle)

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Review `tag-registry.json` current usage | Standards author | Governance vs. operational usage documented | 1 hour |
| Decision: evolve or create new | Standards lead | Option A or B selected with rationale | 1 hour |
| Update `distribute-tag-registry.yml` (if Option A) | Standards author | Workflow validates new fields | 2 hours |
| Create `feature-registry.yaml` + schema (if Option B) | Standards author | Schema defined; validator added | 3 hours |
| Add 3-feature test data | Standards author | CourseCatalogManagement + 2 others populated | 1 hour |

---

## Deliverable 2: Schema Evolution

### Objective

Update `consolidation-config-schema.json` to support `modulesManifestPath`; document dual config split.

### Schema Change

**Add to `consolidation-config-schema.json`:**

```json
{
  "repositories": [
    {
      "url": "https://github.com/org/training-api.git",
      "branch": "main",
      "layer": "API",
      "docsPath": "docs/",
      "modulesManifestPath": "modules.yaml",  // NEW field (default: "modules.yaml")
      "includePatterns": ["**/*_doc.md"]
    }
  ]
}
```

**Behavior:**
- If `modulesManifestPath` present: `consolidate.py` reads `modules.yaml` first; matches by `businessCapability` tag
- If `modulesManifestPath` absent: fallback to `docsPath` glob scan (backward compatibility)

### Dual Config Documentation

**`akr-config-schema.json` (`crossRepository` section):**
- **Purpose:** Per-project participation opt-in
- **Fields:** `consolidationRepo`, `publishFeatureDocs`, `relatedRepositories[]`, `syncSchedule`, `outputs[]`
- **Read by:** `consolidate.py` at participation discovery time
- **Example:**
  ```json
  {
    "crossRepository": {
      "consolidationRepo": "https://github.com/org/feature-docs.git",
      "publishFeatureDocs": true,
      "relatedRepositories": [
        "training-ui",
        "training-db"
      ],
      "syncSchedule": "0 2 * * *",
      "outputs": [
        {
          "template": "feature-consolidated.md",
          "outputPath": "docs/features/{FeatureName}_doc.md"
        }
      ]
    }
  }
  ```

**`consolidation-config-schema.json`:**
- **Purpose:** Job execution configuration
- **Fields:** `repositories[]` to clone, `modulesManifestPath`, `outputDir`, `cacheDir`, `parallelism`, `validation.warnOnMissingLayers`
- **Read by:** `consolidate.py` at job execution time

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Add `modulesManifestPath` to schema | Standards author | Field added with default value and description | 30 min |
| Document dual config split | Standards author | ARCHITECTURE.md explains which config drives which decision | 2 hours |
| Create example configs | Standards author | Both schemas populated with pilot project examples | 1 hour |
| Validate schema changes | Standards author | JSON Schema validation passes | 30 min |
| **Document PAT authentication plan** | Infrastructure lead | Explain `GH_MULTI_REPO_PAT` secret setup for cross-repo sparse checkout; include required permissions (Contents: Read) | 1 hour |
| Document template output scope | Standards author | Phase 4 explicitly states `feature-testing-consolidated.md` is deferred and not generated by `consolidate.py` v1.0 | 15 min |

---

## Deliverable 3: `consolidate.py` Implementation

### Objective

Build deterministic Python aggregator that matches module docs by `businessCapability` (feature tag) and fills `feature-consolidated.md` template.

**Scope lock (v1.0):** `consolidate.py` generates `feature-consolidated.md` only. The
`feature-testing-consolidated.md` variant is deferred to a follow-up enhancement after Phase 4
stabilization.

### Design Principles

1. **Deterministic:** No AI invocation from GitHub Actions
2. **Config-driven:** Reads both config schemas for participation and execution
3. **Module-aware:** Treats module docs as atomic units (not individual component files)
4. **Sparse checkout:** Clones only `docs/` and `modules.yaml` per repo (performance)
5. **Fail-safe:** Warns on missing layers; does not block if one layer absent

### High-Level Algorithm

```python
def consolidate_feature(feature_tag: str):
    """
    Aggregates Level 1 + Level 2 docs across repos into Level 3 feature doc.
    """
    
    # Step 1: Read consolidation-config-schema.json (execution config)
    config = load_consolidation_config()
    
    # Step 2: Clone repositories (sparse checkout: docs/ + modules.yaml only)
    repos = sparse_clone_repositories(config['repositories'])
    
    # Step 3: For each repo, read akr-config-schema.json crossRepository section
    #         Confirm publishFeatureDocs: true (opt-in check)
    participating_repos = filter_participating(repos)
    
    # Step 4: For each participating repo, read modules.yaml
    #         Extract modules[] where businessCapability == feature_tag
    api_modules = []
    ui_modules = []
    db_objects = []
    
    for repo in participating_repos:
        modules_yaml = read_modules_yaml(repo, config['modulesManifestPath'])
        
        for module in modules_yaml['modules']:
          if module.get('businessCapability') == feature_tag:
                if module['project_type'] in ['api-backend', 'microservice']:
                    api_modules.append({
                        'repo': repo,
                        'module': module,
                        'doc_path': module['doc_output']
                    })
                elif module['project_type'] == 'ui-component':
                    ui_modules.append({
                        'repo': repo,
                        'module': module,
                        'doc_path': module['doc_output']
                    })
        
        # Database objects use `businessCapability` field (added in Phase 1 schema)
        for db_obj in modules_yaml.get('database_objects', []):
            # Match on explicit businessCapability field (NOT inference)
            if db_obj.get('businessCapability') == feature_tag:
                db_objects.append({
                    'repo': repo,
                    'object': db_obj,
                    'doc_path': db_obj['doc_output']
                })
    
    # Step 5: Load feature-consolidated.md template
    template = load_template('feature-consolidated.md')
    
    # Step 6: Fill template placeholder syntax
    #         {FOR_EACH_API_COMPONENT} ... {END_FOR_EACH}
    #         {FOR_EACH_UI_COMPONENT} ... {END_FOR_EACH}
    #         {FOR_EACH_DB_COMPONENT} ... {END_FOR_EACH}
    
    consolidated_doc = fill_template(
        template,
        api_modules=api_modules,
        ui_modules=ui_modules,
        db_objects=db_objects
    )
    
    # Step 7: Check warnOnMissingLayers flag (existing config; do not re-implement)
    if config['validation']['warnOnMissingLayers']:
        missing_layers = check_missing_layers(api_modules, ui_modules, db_objects)
        if missing_layers:
            print(f"⚠️ Warning: Feature '{feature_tag}' missing layers: {missing_layers}")
    
    # Step 8: Write output to docs/features/{FeatureName}_doc.md
    output_path = config['outputDir'] + f'/{feature_tag}_doc.md'
    write_file(output_path, consolidated_doc)
    
    return output_path
```

### Input Contract (From Analysis)

| Placeholder | Reads From | Notes |
|---|---|---|
| `{FOR_EACH_API_COMPONENT}` | `modules[]` where `businessCapability == feature_tag` AND `project_type in [api-backend, microservice]` | Module docs as atomic units |
| `{FOR_EACH_UI_COMPONENT}` | `modules[]` where `businessCapability == feature_tag` AND `project_type == ui-component` | Module docs as atomic units |
| `{FOR_EACH_DB_COMPONENT}` | `database_objects[]` where `businessCapability == feature_tag` | Individual DB objects (not grouped); businessCapability field added in Phase 1 schema |

### Implementation Estimate

**Realistic line count:** 300-400 lines

**Breakdown:**
- Config reading: ~50 lines
- Sparse clone + repo filtering: ~80 lines
- `modules.yaml` parsing: ~60 lines
- Template filling: ~80 lines
- Missing layers check: ~30 lines
- File I/O + error handling: ~50 lines

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Implement config reading | Standards author | Reads both schemas; validates required fields | 1 day |
| Implement sparse clone | Standards author | Clones only `docs/` + `modules.yaml` per repo; <2 min for 3 repos | 1 day |
| Implement `modules.yaml` parsing | Standards author | Matches modules by `businessCapability` tag; groups by `project_type` | 1 day |
| Implement template filling | Standards author | Replaces `{FOR_EACH_*}` placeholders with matched content | 2 days |
| Implement missing layers check | Standards author | Reads `warnOnMissingLayers` flag; warns if UI, API, or DB missing | 1 day |
| Write unit tests | Standards author | ≥85% coverage; tests config reading, matching, template filling | 2 days |
| Test on 3-component feature | Standards author | CourseCatalogManagement (UI + API + DB) consolidates correctly | 1 day |

---

## Deliverable 4: CI Workflow Deployment

### Objective

Deploy `.github/workflows/consolidate-feature.yml` in Feature repository (consolidation target repo).

### Workflow Trigger Options

**Option 1: Manual (workflow_dispatch)**
```yaml
on:
  workflow_dispatch:
    inputs:
      feature_tag:
        description: 'Feature tag to consolidate (e.g., CourseCatalogManagement)'
        required: true
```

**Option 2: Scheduled (cron)**
```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
```

**Option 3: On-demand via webhook**
```yaml
on:
  repository_dispatch:
    types: [consolidate-feature]
```

**Recommendation:** Start with **Option 1 (manual)**; add Option 2 (scheduled) after Phase 4 stabilizes.

### Workflow Steps

```yaml
name: Consolidate Feature Documentation

on:
  workflow_dispatch:
    inputs:
      feature_tag:
        description: 'Feature tag to consolidate'
        required: true

jobs:
  consolidate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout feature-docs repo
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install pyyaml requests
      
      - name: Download consolidate.py
        run: |
          curl -o consolidate.py \
            https://raw.githubusercontent.com/org/core-akr-templates/main/scripts/consolidate.py
      
      - name: Download consolidation config
        run: |
          curl -o consolidation-config.json \
            https://raw.githubusercontent.com/org/core-akr-templates/main/config/consolidation-config.json
      
      - name: Run consolidation
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # For clone/push only
          GH_PAT: ${{ secrets.GH_MULTI_REPO_PAT }}  # For cross-repo sparse checkout
        run: |
          python consolidate.py \
            --feature-tag "${{ github.event.inputs.feature_tag }}" \
            --config consolidation-config.json \
            --output docs/features/
      
      - name: Open PR with consolidated doc
        uses: peter-evans/create-pull-request@v5
        with:
          title: 'docs: ${{ github.event.inputs.feature_tag }} feature consolidation'
          body: |
            Automated consolidation of Level 1 + Level 2 docs into Level 3 feature doc.
            
            **Feature:** ${{ github.event.inputs.feature_tag }}
            **Layers included:** [review PR contents]
            
            ## Review Checklist
            - [ ] All participating repositories included
            - [ ] No missing layers (or acceptable if documented)
            - [ ] Business narrative sections marked for Product Owner refinement
            - [ ] Cross-references between layers correct
          branch: 'feature-docs/${{ github.event.inputs.feature_tag }}'
          labels: documentation, feature-consolidation, needs-po-review
```

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Author workflow YAML | Standards author | All steps defined; manual trigger working | 2 hours |
| **Configure PAT secret (`GH_MULTI_REPO_PAT`)** | Infrastructure lead | PAT created with `contents:read` for private repos; secret added to `feature-docs` repo; expiration date documented (90-day rotation recommended) | 1 hour |
| Deploy to feature-docs repo | Infrastructure | Workflow file committed; appears in Actions tab | 30 min |
| Test manual trigger | Standards author | Workflow runs; consolidate.py executes; PR opens | 1 hour |
| Document workflow usage | Standards author | README explains how to trigger consolidation + PAT rotation procedure | 1.5 hours |

**PAT Configuration:**
- **Minimum scopes:** `contents:read` (for sparse checkout of private repos)
- **Expiration:** 90 days recommended; document renewal procedure in `feature-docs` README
- **Rotation strategy:** Automated reminder 7 days before expiration; Infrastructure lead owns renewal

---

## Deliverable 5: End-to-End Testing

### Objective

Consolidate 3-component feature end-to-end; validate output quality and performance.

### Test Feature: CourseCatalogManagement

**Participating repositories:**
- `training-ui` (UI layer): `CourseCatalogPage` module, `CourseCard` module
- `training-api` (API layer): `CourseDomain` module
- `training-db` (Database layer): `training.Courses` object, `training.Enrollments` object

**Expected output:** `docs/features/CourseCatalogManagement_doc.md` with:
- Features Overview section
- UI Components section (2 module docs aggregated)
- API Services section (1 module doc aggregated)
- Database Objects section (2 object docs aggregated)
- End-to-End Flow diagram (Product Owner fills with Copilot assistance; **text-based with → arrows, not Mermaid**)
- Business Value section (Product Owner fills)

**Note:** Architecture diagrams across all templates use text-based formatting (e.g., `Controller → Service → Repository → DB`) rather than Mermaid. This ensures consistent rendering across markdown viewers and reduces token complexity.

### Performance Target

**<2 minutes** from workflow trigger to PR opened

**Breakdown:**
- Sparse clone 3 repos: ~30 seconds
- Parse `modules.yaml` + match by `feature_tag`: ~10 seconds
- Read 5 source docs (2 UI + 1 API + 2 DB): ~20 seconds
- Fill template: ~10 seconds
- Write output + open PR: ~30 seconds

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Prepare test repos | Standards author | training-ui, training-api, training-db all have `modules.yaml` and docs | 2 hours |
| Run consolidation workflow | Standards author | Manual trigger with `CourseCatalogManagement` | 5 min |
| Validate output structure | Developer | All expected sections present; no template errors | 30 min |
| Measure performance | Standards author | Workflow completes in <2 min | 5 min |
| Test sparse checkout | Infrastructure | Cloned only `docs/` + `modules.yaml` (not full repos) | 15 min |
| Document test results | Standards author | Report: structure correct; performance met | 1 hour |

---

## Deliverable 6: Product Owner Refinement Workflow

### Objective

Test workflow where Product Owner uses Copilot agent mode to refine business narrative sections of consolidated doc.

### Sections Requiring PO Refinement

**From `feature-consolidated.md` template:**
- **Features Overview:** High-level business description (AI cannot infer business strategy)
- **Business Value:** Why this feature exists; ROI; customer impact
- **End-to-End Flow:** User journey across UI → API → DB (AI provides structure; PO adds context)
- **Known Limitations:** Business-level constraints (AI cannot know roadmap decisions)

**Sections Auto-Generated:**
- API Components (from module docs)
- UI Components (from module docs)
- Database Objects (from object docs)
- Technical Architecture (synthesized from lower-level diagrams)

### PO Workflow

```
1. Consolidation workflow opens draft PR
   ↓
2. PR labeled: needs-po-review
   ↓
3. Product Owner checks out branch
   ↓
4. In VS Code Copilot Chat: "@workspace refine Business Value section 
   based on available module docs and business context"
   ↓
5. Copilot suggests draft; PO edits for accuracy
   ↓
6. Repeat for Features Overview, End-to-End Flow, Known Limitations
   ↓
7. PO approves PR; merges to main
```

### Testing

| Test | What to Validate | Pass Criteria |
|---|---|---|
| **PO can open draft PR** | GitHub permissions correct | PO sees draft PR; can check out branch |
| **Copilot agent mode assists** | Context from module docs loaded | Copilot suggestions reference actual module content |
| **Sections clearly marked** | `❓ [NEEDS PRODUCT OWNER INPUT]` markers present | All PO sections marked; auto-generated sections not marked |
| **PO satisfaction** | Workflow is faster than writing from scratch | PO reports: "Structured draft saved time" |

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Prepare test PR with PO sections marked | Standards author | All `❓` markers in correct sections | 30 min |
| Conduct PO test session | Product Owner | Completes all 4 sections with Copilot assistance | 2 hours |
| Measure PO time | Standards author | PO reports time-to-complete vs. manual estimate | 15 min |
| Collect PO feedback | Standards author | Friction points and satisfaction documented | 30 min |
| Refine template (if needed) | Standards author | Template updated based on PO feedback | 1 hour |

---

## Deliverable 7: `warnOnMissingLayers` Validation

### Objective

Confirm `consolidate.py` reads existing `warnOnMissingLayers` flag; does not re-implement logic.

### Test Scenarios

| Scenario | Config | Expected Behavior |
|---|---|---|---|
| **All layers present (UI + API + DB)** | `warnOnMissingLayers: true` | No warning; consolidation succeeds |
| **Missing UI layer** | `warnOnMissingLayers: true` | Warning: "Feature 'X' missing UI layer"; continues |
| **Missing DB layer** | `warnOnMissingLayers: true` | Warning: "Feature 'X' missing Database layer"; continues |
| **All layers present** | `warnOnMissingLayers: false` | No validation; consolidation succeeds |
| **Missing layers** | `warnOnMissingLayers: false` | No warning; consolidation succeeds |

### Tasks

| Task | Owner | Acceptance Criteria | Estimated Time |
|---|---|---|---|
| Implement flag reading | Standards author | `consolidate.py` reads flag from config JSON | 30 min |
| Test all 5 scenarios | Developer | Expected warnings appear; no hard failures | 1 hour |
| Document flag behavior | Standards author | README explains when warning appears | 30 min |

---

## Phase 4 Retrospective

### Retrospective Agenda

1. **Consolidation accuracy:** Did output match expectations? Any missing content?
2. **Performance:** Was <2 min target met? Any bottlenecks?
3. **PO workflow:** Was refinement faster than manual? What friction?
4. **Schema design:** Did dual config split work well? Any confusion?
5. **Long-term maintenance:** Is deterministic approach sustainable?

### Retrospective Outputs

- **Phase 4 completion metrics:** Actual vs. estimated time
- **Consolidation effectiveness:** Did feature docs provide cross-team value?
- **Product Owner satisfaction:** Was workflow useful? Adopted?
- **Lessons learned:** Would we design consolidation differently?
- **Post-Phase 4 roadmap:** What governance features come next?

---

## Risk Register (Phase 4 Specific)

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| Sparse clone fails on large repos | 🟡 Medium | 🟠 Low | Test on largest pilot repos; fall back to full clone if needed |
| Feature tagging inconsistent across repos | 🔴 High | 🟡 Medium | Validate all pilot repos have consistent `businessCapability` tags before Phase 4 |
| PO workflow too complex | 🟡 Medium | 🟠 Low | Test with real PO in Deliverable 6; simplify if friction high |
| `modules.yaml` schema drift | 🟡 Medium | 🟠 Low | `minimum_standards_version` enforcement prevents drift |
| `consolidate.py` invoked via future custom agent without approval gate | 🟡 Medium | 🟠 Low | Document in `ARCHITECTURE.md`: if Phase 4 consolidation is ever wired to an agent, `script_approval_required: true` must be set in production `.akr-config.json` before Phase 4 runs begin |

---

## Success Criteria Summary

Phase 4 succeeds when:

✅ Feature registry architecture decided (evolve tag-registry or create new)  
✅ `consolidation-config-schema.json` updated with `modulesManifestPath`  
✅ Dual config split documented (participation vs. execution)  
✅ `consolidate.py` implemented (~300-400 lines; deterministic)  
✅ CI workflow deployed in feature-docs repo  
✅ 3-component feature consolidated end-to-end  
✅ Performance <2 minutes from trigger to PR  
✅ Product Owner refinement workflow tested  
✅ `warnOnMissingLayers` reads existing flag (not re-implemented)  
✅ Phase 4 retrospective complete  

**Exit gate:** Feature consolidation operational; governance system complete end-to-end. Standards lead documents final sign-off **in writing** (GitHub comment, email, or approval record) to formally close the implementation program.

---

**🎉 Congratulations:** All implementation phases complete. The AKR Documentation Governance system is now operational from individual modules through cross-repository feature consolidation.

**Related Documents:**
- [Phase 3: Automation Extension](PHASE_3_AUTOMATION_EXTENSION.md) (if executed)
- [Phase 2: Pilot Onboarding](PHASE_2_PILOT_ONBOARDING.md)
- [Implementation Plan Overview](IMPLEMENTATION_PLAN_OVERVIEW.md)
- [Implementation-Ready Analysis](../akr_implementation_ready_analysis.md) — Part 9
