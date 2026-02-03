# Implementation Plan: Template Enforcement Tool (MCP)

**Document Version:** 5.3 (M365 Copilot Final Polish Complete)
**Date:** February 3, 2026  
**Status:** Ready for Implementation  
**Owner:** AKR MCP Server Team

---

## 📋 Version History

| Version | Date | Key Changes | Status |
|---------|------|-------------|--------|
| **v1.0** | Feb 1, 2026 | Initial comprehensive plan (88 hours) | Superseded |
| **v2.0** | Feb 2, 2026 | M365 Copilot Phase 1: Tool owns write, runtime schema, MVP scope (40-52h) | Superseded |
| **v3.0** | Feb 2, 2026 | M365 Copilot Phase 2: Severity tiers, documentation modes, config support, dry-run | Superseded |
| **v4.0** | Feb 2, 2026 | M365 Copilot Phase 3: Section merge engine, mode resolution, overwrite policy, telemetry | Superseded |
| **v5.0** | Feb 2, 2026 | M365 Copilot Phase 5: Security hardening, config standardization, merge idempotency, telemetry updates | Superseded |
| **v5.1** | Feb 3, 2026 | M365 Copilot Final Clarifications: Output path resolution, merge disabled gating, replace mode requirements, rewrite output example, effective config precedence, enhanced telemetry | Superseded |
| **v5.2** | Feb 3, 2026 | M365 Copilot Final Polish: Removed duplication in Replace Mode section, renamed telemetry 'mode' to 'write_action', added Phase scope note for Template Schema, tightened config.output_path override rule | Superseded |
| **v5.3** | Feb 3, 2026 | M365 Copilot Final Polish Complete: Fixed Template Schema Format Rules markdown, updated telemetry samples to show actual values, updated Integration Point 2 API contract, added write_action derivation rules | **Current** |

---

## 🔄 Key Updates in v5.3 (Final Polish Complete)

### Markdown and Consistency Improvements:
1. ✅ **Fixed Template Schema Format Rules markdown** - Removed broken code fence, moved validation rules outside code blocks for proper rendering
2. ✅ **Updated telemetry samples to show actual values** - Changed `VALIDATION_RUN.details.mode` and `WRITE_FAILURE.details.error_type` from enum lists to actual chosen values
3. ✅ **Added `effective_mode` to VALIDATION_RUN** - Consistent with WRITE_ATTEMPT telemetry field naming
4. ✅ **Updated Integration Point 2 API contract** - Changed `config: dict (workspace_root, output_path)` to `config: dict (workspace_root, optional requested output_path)`
5. ✅ **Added `write_action` derivation rules** - Clear rules for how write_action is determined from update_mode + file existence

---

## 🔄 Key Updates in v5.2 (Final Polish)

### Formatting and Consistency Improvements:
1. ✅ **Removed duplicate text** in Replace Mode Overwrite Requirement section (clean single block)
2. ✅ **Renamed telemetry field** `mode` → `write_action` to avoid confusion with documentation mode (per_file/per_module)
3. ✅ **Added Phase scope clarification** - Marker, diagram, and table validations are Phase 2+ features (Phase 1 focuses on YAML + sections + order + heading hierarchy)
4. ✅ **Tightened config.output_path rule** - Provided path must be derivable from a matching pathMappings rule (prevents governance bypass)
5. ✅ **Improved telemetry example values** - Shows actual chosen values instead of enum lists

---

## 🔄 Key Updates in v5.1 (Final Clarifications)

### Final Clarifications Applied:
1. ✅ **Clarified output path resolution** - `config.output_path` is optional; tool resolves deterministically from pathMappings
2. ✅ **Added merge disabled gating** - Returns `MERGE_DISABLED` error when merge not enabled but update_mode resolves to merge_sections
3. ✅ **Added replace mode overwrite requirement** - Returns `REPLACE_REQUIRES_OVERWRITE` when update_mode=replace with existing file and overwrite=false
4. ✅ **Added Phase 2+ rewrite recommended output example** - Shows full_rewrite_recommended, requires_overwrite, and suggested_action fields
5. ✅ **Added effective settings precedence rules** - Clear 4-step precedence order for tool params → per-mapping overrides → global config → hard-coded defaults
6. ✅ **Enhanced telemetry WRITE_ATTEMPT** - Added overwrite, update_mode, and effective_mode to audit logs

---

## 🔄 Key Updates in v5.0 (Phase 5 Assessment)

### Must-Fix Issues Resolved:
1. ✅ **Removed duplicate server.py integration pseudocode** (no contradictory flows)
2. ✅ **Converted code-like tables to bullet logic** (render-safe format)
3. ✅ **Standardized config example to `documentation.pathMappings`** (modern schema)

### Strongly Recommended Hardening Added:
4. ✅ **Canonical path/symlink protection** in file writes
5. ✅ **Atomic write guidance** for concurrency safety
6. ✅ **Telemetry user field optional** with safe fallbacks

### Nice-to-Have Improvements Applied:
7. ✅ **Merge idempotency requirement** added to success criteria
8. ✅ **MergeResult now includes actionable outputs** (`requires_overwrite`, `suggested_action`)
9. ✅ **Flexible `pathMappings` schema** (string OR object overrides)

### Result:
- **Production-ready hardening complete** (security, schema clarity, merge stability)
- **All Phase 5 feedback addressed** with no conflicting architecture notes

---

## 🔄 Key Updates in v4.0 (Phase 3 Assessment)

### Must-Fix Issues Resolved:
1. ✅ **Fixed duplicate/malformed JSON** in Failure Requiring Retry section (single canonical schema)
2. ✅ **Corrected file-writing ownership** in example flows (tool writes, not server.py)
3. ✅ **Split DocumentStructureParser** into 2A (Phase 1 basic) and 2B (Phase 2 AST)
4. ✅ **Added explicit mode resolution rules** with output path computation for per-file and per-module

### High-Impact Features Added:
5. ✅ **Mode Resolution & Output Path Rules** section - Auto-detect algorithm, {name}/{module} substitution, path validation
6. ✅ **File Overwrite & Merge Policy** - `overwrite` parameter, `update_mode` options, safe defaults
7. ✅ **Telemetry & Audit Logging** - Structured log events (SCHEMA_BUILT, VALIDATION_RUN, WRITE_*), JSON Lines format
8. ✅ **Template Source Precedence refinement** - Clarified production default vs overrides, `allow_local_templates` gate
9. ✅ **Component 8: SectionMergeEngine** (Phase 2) - Section-level merge, change impact detection, ownership classification, full rewrite thresholds
10. ✅ **Merge configuration** added to config schema - `section_ownership`, `rewrite_threshold`, `write_policy`

### Result:
- **Comprehensive production-ready plan** with clear path from MVP (Phase 1) to advanced features (Phase 2+)
- **Enterprise-grade capabilities:** Audit logging, safe overwrites, section-level merge, team customization
- **No contradictions or ambiguities** remaining - truly implementation-ready

---

## 🔄 Key Updates from M365 Copilot Assessments (v2.0-v3.0)

This document was reviewed and improved based on critical feedback from M365 Copilot (Phase 1 and Phase 2). Key changes:

| Item | Original | Updated (v2.0) | Updated (v3.0) | Impact |
|------|----------|---------|---------------|--------|
| **File Writing** | Agent mode writes | Tool owns write | *(unchanged)* | Deterministic, governance-enforced output |
| **Phase 1 Scope** | Full 6 components | Minimal viable (3-4 components) | *(unchanged)* | Faster delivery (5-7 days vs. 2 weeks) |
| **Schema Strategy** | Hardcoded | Runtime parsing + caching | *(unchanged)* | No drift between schema and templates |
| **Validation Approach** | All-or-nothing | Incremental ladder (Phase 1 → 2 → 3) | Severity tiers (BLOCKER/FIXABLE/WARN) | Clear decision logic, configurable strictness |
| **Documentation Modes** | *(implicit)* | *(implicit)* | Explicit support for per-file & per-module | Works with diverse team workflows |
| **Config Schema** | *(implicit)* | *(implicit)* | Support both `pathMappings` & `component_mappings` | Backward compatibility + future-ready |
| **Template Sources** | *(implicit)* | *(implicit)* | Precedence: team extension → local → resource manager | Flexibility for customization |

### Change Log

- **v1.0:** Initial 88-hour implementation plan (comprehensive approach)
- **v2.0:** Simplified Phase 1 MVP to 40-52 hours; tool owns write; runtime schema parsing
- **v3.0:** Fixed parser inconsistency, added severity tiers, documentation modes, config schema support, template source precedence, dry-run capability, validation rules configuration

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Tool Purpose & Scope](#tool-purpose--scope)
4. [Design Specification](#design-specification)
5. [Required Components](#required-components)
6. [Key Design Decisions](#key-design-decisions)
7. [Integration Architecture](#integration-architecture)
8. [Success Metrics](#success-metrics)
9. [Implementation Roadmap](#implementation-roadmap)
10. [Risk Assessment](#risk-assessment)
11. [Appendix](#appendix)

---

## Executive Summary

### The Problem

Current AKR MCP server workflow has a **critical gap between template selection and format enforcement**:

- ✅ `documentation.py` selects the correct template
- ❌ **No mechanism validates that LLM output matches template structure**
- ❌ **No enforcement that generated markdown follows required format**
- Result: ~60% of generated documentation deviates from template format (missing YAML front matter, reordered sections, wrong heading levels, etc.)

### The Solution

Create a dedicated **Template Enforcement Tool** that:
- **Deterministically generates YAML front matter** (not via LLM)
- **Validates LLM output against template schema** before any write
- **Enforces required sections, heading levels, and section order**
- **Writes validated markdown to filesystem** (server-owned, not Agent-dependent)
- Automatically fixes simple structural issues or retries LLM with stricter prompts
- **Guarantees** format compliance in a repeatable, auditable way

### Expected Outcome

- **Baseline:** ~60% compliance with template format
- **Target:** >95% compliance with template format
- **MVP Delivery:** 3-4 weeks (Phase 1: 5-7 days, Phase 2: optional value-adds)
- **Users:** No manual format fixes needed in >95% of cases

---

## Problem Statement

### Current Workflow Gap

```
[documentation.py] selects template ✅
    ↓
[server.py] sends template + code to LLM
    ↓
[LLM] generates markdown (treats template as "inspiration") ⚠️
    ↓
Generated output ≠ Template format ❌
    ↓
[Agent mode] writes malformed markdown to file (non-deterministic)
    ↓
User sees broken documentation (missing YAML, wrong sections, etc.)
```

### Why This Architecture is Suboptimal

**Leaving file writing to Agent mode introduces:**
- ❌ **Inconsistent behavior** across IDEs/versions (tool availability differs by client)
- ❌ **Non-deterministic output** (depends on user approvals, client capabilities)
- ❌ **Harder to audit** (write step not logged by server)
- ❌ **Path security risks** (Agent may misread config, write to wrong location)
- ❌ **CI/CD incompatible** (Agent mode unavailable in headless/automation)

### Improved Workflow (with this tool)

```
[documentation.py] selects template ✅
    ↓
[server.py] sends template + code to LLM
    ↓
[LLM] generates markdown ⚠️
    ↓
[enforcement_tool] validates + corrects ← NEW LAYER
    ├─ PASS → write file ✅
    ├─ AUTO-FIXABLE → fix + retry validation ✅
    └─ RETRY NEEDED → regenerate with LLM ✅
    ↓
[enforcement_tool] writes validated markdown to filesystem (deterministic)
    ↓
[server.py] logs validation results + write confirmation
    ↓
User gets correctly formatted documentation ✅
```

**Benefits:**
- ✅ **Deterministic output** (same input = same output always)
- ✅ **Client-independent** (works in VS Code, Visual Studio, CLI, CI/CD)
- ✅ **Auditable** (server logs all validation + writes)
- ✅ **Governance enforced** (pathMappings respected, unsafe writes blocked)
- ✅ **Repeatable** (rules in code, not dependent on prompting)

### Why This Happens

1. **LLM treats template as guidance, not schema**
   - Template markdown is 700+ lines with optional sections
   - LLM interprets optional = "skip this"
   - YAML front matter looks like "template scaffolding" to discard
   - LLM reorders for "better readability"

2. **No validation layer exists**
   - After LLM generates output, no gatekeeper checks format
   - No mechanism compares generated structure against template requirements
   - File write happens without validation

3. **Assumption that prompting is sufficient**
   - Current design assumes strict prompt = strict output
   - Reality: LLM optimizes for readability over format compliance
   - No enforcement mechanism

4. **Separation of concerns incomplete**
   - Template selection lives in `documentation.py`
   - Template enforcement lives nowhere
   - Result: Selected ≠ Generated

### Impact

| Aspect | Current Impact | Business Cost |
|--------|---|---|
| Manual format fixes needed | ~80% of generated docs | 10-15 min per doc × team size |
| Missing YAML front matter | ~100% omitted | Cannot index/search docs |
| Section reordering | ~40% reordered | Inconsistent doc organization |
| Flow diagrams malformed | ~70% wrong format | Hard to understand service flows |
| CI/CD automation fails | Cannot automate docs | Manual bottleneck in workflow |

---

## Tool Purpose & Scope

### Official Purpose

To guarantee that generated documentation adheres to AKR template structure, format rules, and organizational governance standards by:
1. Validating LLM output against template schema
2. Auto-correcting structural issues or retrying LLM with stricter prompts
3. **Deterministically writing compliant markdown to filesystem** (not delegating to Agent mode)
4. Enforcing path governance from `.akr-config.json` mappings

This ensures **repeatable, auditable, client-independent documentation generation**.

### Primary Responsibilities

1. **Schema Validation**
   - Define required structure for each template type
   - Parse generated markdown structure
   - Compare against schema
   - Report violations

2. **YAML Front Matter Management**
   - Generate deterministically from file metadata (not LLM)
   - Infer layer, component, etc. from file path
   - Fill unknown fields with `TBD`
   - Validate YAML syntax

3. **Format Enforcement**
   - Validate section presence and order
   - Check heading level hierarchy
   - Verify ASCII diagram format
   - Ensure marker placement (🤖/❓)
   - Validate table structures

4. **Error Correction**
   - Auto-fix simple issues (missing headers, wrong order)
   - Generate retry prompts for LLM
   - Flag issues requiring manual review

5. **File Management & Governance**
   - Validate output path against `.akr-config.json` pathMappings
   - Refuse unsafe writes (outside configured paths, parent dir references)
   - **Write validated markdown to filesystem deterministically**
   - Log validation + write operations for audit trail

6. **Template Metadata Integration**
   - Leverage `TemplateMetadata.required_sections` from `documentation.py`
   - Use `projectType` + `complexity` to determine enforcement rules
   - Different templates = different validation profiles (Lean vs. Standard vs. Comprehensive)

7. **Documentation Mode Support**
   - **Per-file mode:** 1 source file → 1 documentation file
   - **Per-module mode:** Multiple related files → 1 consolidated documentation file
   - Example: Enrollment module (Entity + Repository + Service + Controller → Enrollment.md)

8. **Dry-Run / Preview Capability**
   - Resolve output paths without writing files
   - Report template selection and expected validation rules
   - Show what *would* happen (path, template, schema) without side effects
   - Increases user trust and aids debugging

### What This Tool Does NOT Do

- ❌ Generate documentation content (LLM does this)
- ❌ Read source code (LLM does this)
- ❌ Select templates (documentation.py does this)
- ❌ Evaluate business logic quality (human does this)

### Scope Boundaries

**Phase 1 Priority (High ROI, Low Complexity):**
- ✅ YAML front matter generation + validation
- ✅ Required sections presence + order validation
- ✅ Heading level sanity checks (no jumps)
- ✅ Path validation against `.akr-config.json` pathMappings
- ✅ Deterministic file write to validated path

**Phase 2+ (Lower ROI, Higher Complexity):**
- Auto-fix structural issues (reorder, wrong heading levels)
- LLM retry prompts for missing sections
- ASCII diagram format validation
- Table structure rules
- Marker counting thresholds (🤖/❓)
- Audit logging

**Out of Scope:**
- Content quality assessment
- Business logic validation
- Grammar/spelling checks
- Code snippet accuracy
- Section depth/completeness

---

## Design Specification

### Input/Output Contract

#### Input
```json
{
  "generated_markdown": "string (full markdown from LLM)",
  "template_name": "string (e.g., 'lean_baseline_service_template.md')",
  "file_metadata": {
    "file_path": "string | string[] (per-file or per-module)",
    "component_name": "string (e.g., 'EnrollmentService' or 'Enrollment' for module)",
    "module_name": "string (optional: for per-module docs)",
    "complexity": "string (optional: 'minimal'|'lean'|'standard'|'comprehensive')",
    "feature_tag": "string (optional: 'FN12345_US067')",
    "domain": "string (optional: 'Training'|'PaymentProcessing'|etc.)"
  },
  "config": {
    "output_path": "string (optional: requested target path - must still pass mapping + governance checks)",
    "workspace_root": "string (to validate path is in workspace)"
  },
  "overwrite": "boolean (optional, default false)",
  "update_mode": "string (optional: replace | merge_sections | append; default from documentation.write_policy.default_update_mode)",
  "mode": "string (optional: 'per_file' | 'per_module', default: auto-detect)",
  "dry_run": "boolean (optional: if true, preview only, no write)"
}
```

**Output Path Resolution:**
If `config.output_path` is provided, it is treated as a requested target and must still pass mapping + governance checks. Specifically, **the provided path must be derivable from a matching `documentation.pathMappings` rule for the given source inputs**; otherwise the tool rejects the request.

If omitted (recommended), the tool resolves output path deterministically using `documentation.pathMappings` and returns `resolved_output_path`.

**Rationale:** The tool always validates that the output path is derived from a valid pathMappings transformation, regardless of whether the path was explicitly provided or auto-resolved. This prevents `config.output_path` from being used as a governance bypass.

**Update Mode Defaulting:** If `update_mode` is omitted, the tool resolves it from `documentation.write_policy.default_update_mode` (or a per-mapping override), subject to Phase gating (Phase 1 supports `replace` only; Phase 2+ supports `merge_sections`/`append`).

#### Output (Success - Dry Run)
```json
{
  "dry_run": true,
  "resolved_output_path": "docs/services/Enrollment.md",
  "chosen_template": "lean_baseline_service_template.md",
  "expected_schema": {
    "required_sections": ["Quick Reference", "What & Why", "How It Works", ...],
    "yaml_fields": ["feature", "domain", "layer", ...]
  },
  "path_allowed": true,
  "effective": {
    "mode": "per_module",
    "update_mode": "merge_sections",
    "overwrite": false,
    "template": "lean_baseline_service_template.md",
    "merge_enabled": true
  },
  "preview_summary": "Would write to docs/services/Enrollment.md using Lean Baseline template"
}
```

#### Output (Success - Write)
```json
{
  "valid": true,
  "written": true,
  "file_path": "docs/services/Enrollment.md",
  "violations": [],
  "severity_summary": {
    "blockers": 0,
    "fixable": 0,
    "warnings": 0
  },
  "yaml_frontmatter": "---\nfeature: TBD\n...\n---",
  "summary": "Documentation validated and written successfully"
}
```

#### Output (Phase 2+ - Full Rewrite Recommended)
```json
{
  "valid": true,
  "written": false,
  "full_rewrite_recommended": true,
  "requires_overwrite": true,
  "suggested_action": "re-run with overwrite=true",
  "reason": "Change threshold exceeded: changed_percentage=0.72, sections_needing_review=4",
  "resolved_output_path": "docs/services/Enrollment.md",
  "violations": [],
  "severity_summary": {
    "blockers": 0,
    "fixable": 0,
    "warnings": 0
  },
  "confidence": 0.85
}
```

#### Output (Failure with Auto-Fixes)
```json
{
  "valid": false,
  "written": false,
  "violations": [
    {
      "type": "missing_yaml",
      "severity": "FIXABLE",
      "line": 1,
      "message": "Missing YAML front matter"
    },
    {
      "type": "section_reordered",
      "severity": "FIXABLE",
      "line": 47,
      "message": "Section 'Business Rules' appears after 'Architecture' (should be before)"
    }
  ],
  "severity_summary": {
    "blockers": 0,
    "fixable": 2,
    "warnings": 0
  },
  "auto_fixable": true,
  "corrected_markdown": "string (with auto-fixes applied)",
  "fixes_applied": [
    "Generated and prepended YAML front matter",
    "Reordered sections to match template"
  ]
}
```

#### Output (Failure Requiring Retry)
```json
{
  "valid": false,
  "written": false,
  "violations": [
    {
      "type": "missing_section",
      "severity": "BLOCKER",
      "section_name": "How It Works",
      "message": "Required section 'How It Works' not found"
    },
    {
      "type": "diagram_format",
      "severity": "WARN",
      "line": 85,
      "message": "Flow diagram uses prose instead of ASCII boxes (configurable rule)"
    }
  ],
  "severity_summary": {
    "blockers": 1,
    "fixable": 0,
    "warnings": 1
  },
  "requires_llm_retry": true,
  "retry_prompt": "The generated documentation is missing the required 'How It Works' section. Please regenerate the documentation including this section with: 1) a high-level overview of the service flow, 2) key processing steps, and 3) interaction points with other components.",
  "suggestions": [
    "Regenerate with template structure enforcement",
    "Add missing section: How It Works"
  ]
}
```

---

### Template Schema Structure

Each template has a **TemplateSchema** that defines:

#### 1. Section Hierarchy
```
Required Sections (must appear, order preserved):
  - YAML Front Matter (level 0, no header)
  - Service: [NAME] (level 1, H1)
  - Quick Reference (level 2, H2)
    - What it does (level 3, H3, marker: 🤖)
    - When to use it (level 3, H3, marker: ❓)
    - Watch out for (level 3, H3, marker: ❓)
  - What & Why (level 2, H2)
    - Purpose (level 3, H3)
    - Capabilities (level 3, H3)
    - Not Responsible For (level 3, H3)
  - How It Works (level 2, H2)
  - Business Rules (level 2, H2)
  - Architecture (level 2, H2)
  - Data Operations (level 2, H2)
  - Questions & Gaps (level 2, H2)

Optional Sections (can be empty, structure preserved):
  - Optional Sections (level 2, H2, contains: "Add when needed")
```

#### 2. Format Rules

**Validation Rules:**

- **YAML Front Matter:**
  - Must be first element (before any markdown)
  - Syntax: lines 1-11, format: key: value
  - Required fields: feature, domain, layer, component, status, version, componentType, priority, lastUpdated
  - All fields present (no omissions), even if value is "TBD"

- **Heading Hierarchy:**
  - H1 used only for title (once)
  - H2 for major sections (Quick Reference, What & Why, etc.)
  - H3 for subsections
  - No jumps (H1 → H3 without H2 is invalid)

- **Flow Diagrams (in "How It Works"):**
  - Must use ASCII box characters: ┌ ─ ┐ └ ┘ │
  - Not plain prose description
  - Example format enforced

- **Markers:**
  - 🤖 must appear min 5 times (AI-generated content)
  - ❓ must appear min 3 times (human-needed content)
  - Should not appear in section headers only

- **Tables:**
  - Markdown format: | col1 | col2 |
  - Minimum 2 rows (header + 1 data)
  - Consistent column count

- **Placeholders:**
  - Unknown values: "TBD" (not blank, not "??", not omitted)
  - Human-needed content: ❓ [HUMAN: description of what's needed]

**Phase Scope Note:** Marker, diagram, and table validations are **Phase 2+ features** (or WARN-only in Phase 1 unless explicitly promoted by config). Phase 1 MVP focuses on YAML + required sections + order + heading hierarchy.

#### 3. YAML Field Requirements
```
YAML Schema:
  feature:
    - Type: string
    - Valid values: Feature tag (e.g., "FN12345_US067") or "TBD"
    - Required: Yes
    - Inferred from: Metadata (feature_tag parameter)
  
  domain:
    - Type: string
    - Valid values: Business domain or "TBD"
    - Required: Yes
    - Inferred from: Metadata (domain parameter)
  
  layer:
    - Type: string
    - Valid values: "API" | "Service" | "Data" | "UI" | "TBD"
    - Required: Yes
    - Inferred from: File path (Controllers→API, Services→Service, etc.)
  
  component:
    - Type: string
    - Valid values: Service/Component name
    - Required: Yes
    - Inferred from: Component name from file_path
  
  status:
    - Type: string
    - Valid values: "deployed" | "draft" | "planned" | "deprecated"
    - Required: Yes
    - Default: "deployed"
  
  version:
    - Type: string
    - Valid values: Semantic version (e.g., "1.0")
    - Required: Yes
    - Default: "1.0"
  
  componentType:
    - Type: string
    - Valid values: "Service" | "Component" | "Table" | "Utility"
    - Required: Yes
    - Inferred from: Template type
  
  priority:
    - Type: string
    - Valid values: "P1" | "P2" | "P3" | "P4" | "TBD"
    - Required: Yes
    - Default: "TBD"
  
  lastUpdated:
    - Type: date (ISO 8601: YYYY-MM-DD)
    - Valid values: Valid date
    - Required: Yes
    - Default: Current date
```

---

## Required Components

### Architecture Note: Incremental Enforcement Ladder

Per M365 Copilot's recommendation, this tool uses an **incremental enforcement ladder** rather than building all validation rules at once:

**Phase 1 Focus (High ROI):**
- Components 1, 2 (basic), 3, 4, 5 (schema builder, basic parser, validator, YAML, file writer)
- **Note:** Phase 1 includes **basic DocumentStructureParser** (regex-based for YAML/headings/order)
- Simplest, most impactful rules

**Phase 2+ (Advanced Features):**
- Component 2 (upgrade to full AST parser)
- Components 6, 7 (auto-fixes, retry prompts)
- Diagram/table/marker validation
- Deferred until Phase 1 proven successful

**Clarification:** Phase 1 needs basic parsing to validate sections/order. Phase 2 upgrades to sophisticated AST-based parsing for complex validation.

This reduces risk and delivers value faster.

---

### Component 1: TemplateSchemaBuilder

**Purpose:** Extract schema from template markdown at runtime, with caching

**Responsibilities:**
- Read template markdown from filesystem via AKRResourceManager
- Parse required sections and hierarchy from template content
- Extract format rules (heading levels, marker placement)
- Build `TemplateSchema` data structure
- Cache schemas with checksum (detect changes automatically)

**Key Methods:**
- `build_schema(template_name: str, template_content: str) -> TemplateSchema`
- `get_required_sections(template_content: str) -> List[Section]`
- `extract_heading_hierarchy(template_content: str) -> Dict[str, int]` (section → heading level)
- `cache_schema(template_name: str, schema: TemplateSchema)`
- `get_cached_schema(template_name: str) -> Optional[TemplateSchema]`

**Data Structures:**
- `TemplateSchema`: Schema definition (required sections, heading levels, format rules)
- `Section`: Individual section (name, heading_level, required)

**Key Insight:** 
Use `TemplateMetadata.required_sections` from `documentation.py` as baseline, but also parse template to validate consistency. If template changes, schema automatically updates on next validation.

**Phase:** Phase 1

---

### Component 2A: BasicDocumentParser (Phase 1)

**Purpose:** Parse generated markdown using regex-based pattern matching for structural validation

**Responsibilities:**
- Read markdown content
- Extract YAML front matter (basic key-value parsing)
- Parse heading hierarchy (detect `#` symbols, level, text)
- Identify sections by heading text
- Extract section order
- Build simple document structure (headings list + YAML dict)

**Key Methods:**
- `parse_document(content: str) -> BasicDocumentStructure`
- `extract_yaml_frontmatter(content: str) -> Dict[str, str]`
- `extract_headings(content: str) -> List[Heading]`
- `get_section_order(content: str) -> List[str]`

**Data Structures:**
- `BasicDocumentStructure`: YAML data + headings list + section order
- `Heading`: Heading info (level, text, line_number)

**Limitations (acceptable for Phase 1):**
- No AST parsing (can't detect malformed tables, nested lists)
- Basic YAML parsing (doesn't validate complex structures)
- No code block or link extraction
- No content-level analysis (length, markers, diagrams)

**Phase:** Phase 1 (MVP) - ships in v1.0

---

### Component 2B: FullASTParser (Phase 2+)

**Purpose:** Full markdown AST parsing for advanced validation and section-level merge operations

**Responsibilities:**
- Parse markdown into full Abstract Syntax Tree (AST)
- Extract nested structures (lists, tables, code blocks, diagrams)
- Detect content markers (🤖, ❓) and their context
- Extract section content boundaries (for merge operations)
- Build hierarchical document tree (parent-child relationships)

**Key Methods:**
- `parse_full_ast(content: str) -> FullDocumentAST`
- `extract_section_content(section_name: str) -> SectionContent`
- `detect_markers(content: str) -> List[MarkerLocation]`
- `validate_tables(ast: FullDocumentAST) -> List[Violation]`
- `validate_diagrams(ast: FullDocumentAST) -> List[Violation]`

**Data Structures:**
- `FullDocumentAST`: Complete tree representation with node types
- `SectionContent`: Section boundaries + content + child nodes
- `MarkerLocation`: Marker type + line number + context

**Use Cases (Phase 2+):**
- Section-level merge (SectionMergeEngine requires section boundaries)
- Advanced validation rules (table structure, diagram format)
- Content-aware auto-fixes (reformatting lists, fixing tables)

**Phase:** Phase 2+ (deferred from MVP)

---

### Component 3: ValidationEngine

**Purpose:** Compare document structure against schema and report violations with severity tiers (Phase 1)

**Responsibilities:**
- Accept parsed document and template schema
- Execute Phase 1 validation rules only:
  1. YAML front matter: syntax valid, all required fields present
  2. Required sections: all present (✅ check only, not content)
  3. Section order: matches template order
  4. Heading hierarchy: no level jumps (e.g., H1 → H3 without H2)
- Generate violation report with **severity tiers**
- Calculate summary metrics

**Key Methods:**
- `validate_phase1(parsed_doc: DocumentStructure, schema: TemplateSchema) -> ValidationResult`
- `check_yaml_frontmatter(yaml_data: Dict) -> List[Violation]`
- `check_required_sections(sections: List[str], schema: TemplateSchema) -> List[Violation]`
- `check_section_order(sections: List[str], schema: TemplateSchema) -> List[Violation]`
- `check_heading_hierarchy(headings: List[Heading]) -> List[Violation]`
- `calculate_severity_summary(violations: List[Violation]) -> Dict[str, int]`

**Data Structures:**
- `ValidationResult`: Pass/fail + violations + severity summary
- `Violation`: Individual violation (type, **severity**, line number, message)
- `ViolationSeverity`: Enum = **BLOCKER | FIXABLE | WARN**

**Severity Tier Decision Logic:**
```
BLOCKER (fail validation, retry required):
  - Missing required section
  - Invalid YAML syntax
  - No YAML front matter (if can't auto-generate)

FIXABLE (auto-fix possible):
  - Missing YAML front matter (can generate deterministically)
  - Sections out of order (can reorder)
  - Wrong heading levels (can adjust # symbols)

WARN (pass validation, log for review):
  - Diagram format issues (configurable rule)
  - Marker count thresholds (configurable rule)
  - Table structure issues (configurable rule)
```

**Decision Logic:**
```python
if any(v.severity == BLOCKER): 
    result = FAIL → retry with LLM
elif any(v.severity == FIXABLE):
    result = AUTO-FIX → apply fixes, revalidate
elif only(v.severity == WARN):
    result = PASS with warnings → write file
else:
    result = PASS → write file
```

**Phase 1 Validation Rules:**
```
✅ YAML Front Matter (BLOCKER if missing AND can't generate, FIXABLE otherwise)
   - Must exist (starts with "---\n") or be generatable
   - Must have all fields: feature, domain, layer, component, status, version, componentType, priority, lastUpdated
   - lastUpdated must be valid date (YYYY-MM-DD)

✅ Required Sections (BLOCKER if missing)
   - All sections from TemplateMetadata.required_sections must be present
   - Check by heading text (case-insensitive)

✅ Section Order (FIXABLE if wrong)
   - Sections must appear in template order (allow extras, but required ones must be in correct position)

✅ Heading Levels (FIXABLE if inconsistent)
   - No jumps (## must not follow # without H1)
   - Consistent nesting (### must follow ##)
```

**Phase:** Phase 1

---

### Component 4: YAMLFrontmatterGenerator

**Purpose:** Generate deterministically correct YAML front matter (Phase 1)

**Responsibilities:**
- Accept file metadata (component_name, file_path, template_name, etc.)
- Infer layer from file path conventions
- Fill known YAML fields deterministically
- Mark unknown fields as "TBD"
- Return valid YAML block
- Validate syntax before returning

**Key Methods:**
- `generate(metadata: FileMetadata, template_name: str) -> str` (returns YAML block)
- `infer_layer_from_path(file_path: str) -> str`
- `infer_component_type(template_name: str) -> str`
- `validate_yaml_syntax(yaml_str: str) -> List[str]` (errors, empty if valid)

**Data Structures:**
- `FileMetadata`: Input (file_path, component_name, feature_tag, domain, etc.)

**YAML Generation Rules (Phase 1):**
```
feature:        # Use metadata.feature_tag if provided, else "TBD"
domain:         # Use metadata.domain if provided, else "TBD"
layer:          # Inferred from file_path (Controllers→API, Services→Service, etc.)
component:      # Use metadata.component_name
status:         # Hardcoded: "deployed" (can change in config)
version:        # Hardcoded: "1.0"
componentType:  # Inferred from template_name (Service/Component/Table)
priority:       # Hardcoded: "TBD"
lastUpdated:    # Current date (YYYY-MM-DD)
```

**Phase:** Phase 1

---

### Component 5: FileWriter

**Purpose:** Write validated markdown to filesystem with security checks (Phase 1)

**Responsibilities:**
- Validate output path against `.akr-config.json` pathMappings
- Prevent writes outside workspace or to invalid paths
- Write markdown content to file
- Create directory structure if needed
- Return write confirmation with file path

**Key Methods:**
- `write(markdown: str, output_path: str, config: AKRConfig) -> WriteResult`
- `validate_path(output_path: str, config: AKRConfig) -> List[str]` (errors, empty if valid)
- `ensure_directory(path: str) -> bool`
- `write_file(path: str, content: str) -> bool`

**Concurrency Safety:**
- Use **atomic write** pattern: write to temp file + rename to avoid partial writes
- Implementation: `write_file(path) → write(path + ".tmp") → rename(path + ".tmp", path)`
- Rationale: Prevents corruption if two users/agents trigger tool simultaneously
- File lock (optional): If multiple processes may write same file concurrently, consider file lock before write

**Data Structures:**
- `WriteResult`: (success, file_path, errors, warnings)
- `AKRConfig`: Config with workspaceRoot, pathMappings

**Path Validation Rules (Phase 1):**
```
✅ Path must be inside workspace_root
✅ Path must be derived from the same pathMapping that matched the input source(s)
✅ Resolved path must be inside configured documentation root (e.g., docs/)
✅ Path must not contain ".." (parent directory traversal after normalization)
✅ Resolve canonical/realpath before validation (reject if resolved path escapes workspace/doc root)
✅ Extension must be ".md"
```

**Security Note:** The tool resolves the canonical path (following symlinks) before validation to prevent symlink traversal attacks. A malicious symlink inside `docs/` pointing outside the repo will be detected and rejected. This provides the same class of protection as the `..` rule but handles the symlink edge case.

**Validation Order (implementation sequence):**
1. Normalize + join workspace root with relative path
2. Resolve realpath (follow symlinks)
3. Validate inside workspace root
4. Validate inside documentation root
5. Validate extension (must be `.md`)

**Path Transformation Note:** Path validation enforces that the resolved output path came from a valid `pathMappings` transformation (source glob → output pattern). The tool does NOT validate against "template type" but rather against the actual mapping rule that was applied during path resolution.

**Phase:** Phase 1

---

### Component 6: FormatFixer (Phase 2+)

Deferred to Phase 2. Will handle auto-fixing:
- Missing YAML front matter
- Sections out of order
- Wrong heading levels
- Missing empty sections

**Phase:** Phase 2+

---

### Component 7: PromptEnhancer (Phase 2+)

Deferred to Phase 2. Will generate retry prompts for LLM when Phase 1 validation fails for content-related issues (missing sections, etc.).

**Phase:** Phase 2+

---

### Component 8: SectionMergeEngine (Phase 2+)

**Purpose:** Safely update existing documentation by merging only sections impacted by code changes, preserving human-written content

**Problem:** Overwriting entire docs destroys manual edits. Teams need section-level merge capabilities.

**Responsibilities:**
- Load and parse existing documentation (using Component 2B: FullASTParser)
- Parse newly generated documentation
- Determine change impact for each section
- Classify sections by ownership (LLM-managed vs human-managed)
- Merge strategies: preserve, replace, add, or flag for human review
- Detect when full rewrite is needed (threshold-based)
- Generate merge result with audit trail

**Key Methods:**
- `merge_documents(existing: FullDocumentAST, generated: FullDocumentAST, config: MergeConfig) -> MergeResult`
- `detect_section_changes(existing_section: SectionContent, generated_section: SectionContent) -> ChangeImpact`
- `classify_section_ownership(section_name: str, config: MergeConfig) -> SectionOwnership`
- `should_full_rewrite(change_summary: ChangeSummary, thresholds: RewriteThreshold) -> bool`
- `apply_merge_strategy(sections: List[SectionMerge]) -> str`

**Data Structures:**
```python
@dataclass
class SectionOwnership(Enum):
    LLM_MANAGED = "llm"       # LLM can freely replace
    HUMAN_MANAGED = "human"   # Preserve, never auto-replace
    HYBRID = "hybrid"         # Requires careful merge

@dataclass
class ChangeImpact:
    section_name: str
    impact_level: str  # "unchanged" | "minor" | "major" | "new" | "deleted"
    similarity_score: float  # 0.0 to 1.0
    detected_changes: List[str]  # ["heading changed", "content expanded"]

@dataclass
class SectionMerge:
    section_name: str
    strategy: str  # "preserve" | "replace" | "add" | "human_review"
    content: str
    reason: str

@dataclass
class MergeResult:
    merged_markdown: str
    sections_preserved: int
    sections_replaced: int
    sections_added: int
    sections_flagged: List[str]  # Sections needing human review
    full_rewrite_recommended: bool
    requires_overwrite: bool  # True if rewrite recommended and overwrite=false
    suggested_action: Optional[str]  # e.g., "re-run with overwrite=true" or "review conflicts manually"
    reason: Optional[str]  # Human-readable explanation (e.g., rewrite threshold exceeded)
    audit_trail: List[SectionMerge]
```

**Merge Algorithm:**

```python
def merge_documents(existing, generated, config):
    # Step 1: Parse both documents
    existing_sections = parse_into_sections(existing)
    generated_sections = parse_into_sections(generated)
    
    # Step 2: Analyze each section
    merge_plan = []
    for section_name in config.required_sections:
        ownership = config.section_ownership.get(section_name, "llm")
        
        if section_name in existing_sections and section_name in generated_sections:
            # Case A: both exist - detect changes
            change = detect_section_changes(
                existing_sections[section_name],
                generated_sections[section_name]
            )
            
            if ownership == "human":
                # Always preserve human-managed sections
                merge_plan.append(SectionMerge(
                    section_name, "preserve", 
                    existing_sections[section_name].content,
                    "Human-managed section, preserving existing content"
                ))
            
            elif ownership == "hybrid" and change.impact_level in ["minor", "major"]:
                # Hybrid section with changes - flag for human review
                merge_plan.append(SectionMerge(
                    section_name, "human_review",
                    existing_sections[section_name].content,
                    f"Hybrid section changed - manual merge required (similarity: {change.similarity_score})"
                ))

            elif change.impact_level == "unchanged":
                # No change detected - preserve
                merge_plan.append(SectionMerge(
                    section_name, "preserve",
                    existing_sections[section_name].content,
                    "No detected changes"
                ))
            
            else:
                # LLM-managed changes - replace
                merge_plan.append(SectionMerge(
                    section_name, "replace",
                    generated_sections[section_name].content,
                    f"{change.impact_level.capitalize()} changes detected"
                ))
        
        elif section_name in generated_sections:
            # Case B: only generated exists - add
            merge_plan.append(SectionMerge(
                section_name, "add",
                generated_sections[section_name].content,
                "New required section generated"
            ))
        
        elif section_name in existing_sections:
            # Case C: only existing exists - removed in generated
            if ownership == "human":
                # Preserve human content even if LLM didn't regenerate
                merge_plan.append(SectionMerge(
                    section_name, "preserve",
                    existing_sections[section_name].content,
                    "Human-managed section, preserving despite absence in generated doc"
                ))
            else:
                # Flag for human review (LLM removed it - intentional?)
                merge_plan.append(SectionMerge(
                    section_name, "human_review",
                    existing_sections[section_name].content,
                    "Section removed in generated doc - manual review required"
                ))
        else:
            # Case D: neither exists (should not happen for required sections)
            pass
    
    # Step 3: Check if full rewrite recommended
    change_summary = summarize_changes(merge_plan)
    full_rewrite = should_full_rewrite(change_summary, config.rewrite_threshold)
    
    if full_rewrite:
        return MergeResult(
            merged_markdown=None,
            sections_preserved=0,
            sections_replaced=0,
            sections_added=0,
            sections_flagged=[],
            full_rewrite_recommended=True,
            requires_overwrite=True,
            suggested_action="re-run with overwrite=true",
            reason=f"Change threshold exceeded: {change_summary}",
            audit_trail=merge_plan
        )
    
    # Step 4: Apply merge strategy
    merged_markdown = apply_merge_strategy(merge_plan)
    
    return MergeResult(
        merged_markdown=merged_markdown,
        sections_preserved=count(merge_plan, "preserve"),
        sections_replaced=count(merge_plan, "replace"),
        sections_added=count(merge_plan, "add"),
        sections_flagged=[s.section_name for s in merge_plan if s.strategy == "human_review"],
        full_rewrite_recommended=False,
        requires_overwrite=False,
        suggested_action=None,
        reason=None,
        audit_trail=merge_plan
    )
```

**Full Rewrite Thresholds:**

Recommend full rewrite if ANY of these conditions met:

| Condition | Threshold | Rationale |
|-----------|-----------|-----------|
| **Blocker violations** | ≥ 3 | Multiple structural issues indicate template mismatch |
| **Changed percentage** | > 60% | Most content changed, merge overhead not worth it |
| **Sections needing review** | ≥ 3 | Too many conflicts for automated merge |
| **New sections** | ≥ 50% of required | Major structure change, cleaner to rewrite |

**Configuration:**

Teams configure via `.akr-config.json`:

```json
{
  "documentation": {
    "merge": {
      "enabled": true,
      "section_ownership": {
        "What it does": "llm",
        "How It Works": "llm",
        "Architecture": "llm",
        "Data Operations": "llm",
        "Business Rules": "human",
        "Questions & Gaps": "human",
        "Team-Specific Notes": "human"
      },
      "rewrite_threshold": {
        "blockers": 3,
        "changed_percentage": 0.6,
        "sections_needing_review": 3,
        "new_sections_percentage": 0.5
      },
      "default_ownership": "llm"
    }
  }
}
```

**Integration with FileWriter:**

```python
def write_documentation(..., update_mode="merge_sections", overwrite=False):
    if file_exists(output_path) and update_mode == "merge_sections":
        # Load existing doc
        existing_content = read(output_path)
        existing_ast = FullASTParser.parse(existing_content)
        
        # Parse generated doc
        generated_ast = FullASTParser.parse(generated_markdown)
        
        # Merge
        merge_result = SectionMergeEngine.merge_documents(
            existing_ast, generated_ast, config.merge
        )
        
        if merge_result.full_rewrite_recommended:
            # Prompt user or require overwrite
            logger.warning(f"Full rewrite recommended: {merge_result.reason}")
            if not overwrite:
                return error("Full rewrite needed, set overwrite=true")
        
        # Write merged content
        write(output_path, merge_result.merged_markdown)
        
        return success(
            path=output_path,
            sections_preserved=merge_result.sections_preserved,
            sections_replaced=merge_result.sections_replaced
        )
    else:
        # Normal write (create or replace)
        write(output_path, generated_markdown)
```

**Change Detection Strategies (Priority Order):**

The tool uses the **first available strategy** in this priority order:

1. **Git diff analysis** (if git available AND file is tracked)
   - **Best signal:** Shows actual code changes that triggered regeneration
   - **Method:** `git diff HEAD -- <source_files>` line count, changed percentage
   - **Fallback if unavailable:** File not tracked or git not accessible

2. **Content similarity scoring** (if no git or git unavailable)
   - **Good proxy:** Levenshtein distance or difflib.SequenceMatcher ratio (0.0-1.0)
   - **Method:** Compare section body text between existing and generated
   - **Threshold:** <0.7 similarity = major change, 0.7-0.9 = minor, >0.9 = unchanged

3. **AST structure comparison** (if similarity scoring inconclusive)
   - **Structural signal:** Detects added/removed subsections, lists, tables, code blocks
   - **Method:** Compare node counts and types in section AST
   - **Use case:** Content rewrites that maintain same structure

4. **Conservative preserve** (default fallback)
   - **Safe default:** If detection uncertain, preserve existing unless explicitly LLM-managed
   - **Rationale:** Better to keep stale content than destroy human edits

**Implementation Note:** Implementers should prioritize git diff (most accurate) and avoid over-engineering AST comparison initially. Similarity scoring covers 80% of cases where git is unavailable.

**Example Merge Audit Trail:**

```json
{
  "sections": [
    {
      "section": "Quick Reference",
      "strategy": "preserve",
      "reason": "No detected changes",
      "similarity": 1.0
    },
    {
      "section": "How It Works",
      "strategy": "replace",
      "reason": "Major changes detected - new implementation details",
      "similarity": 0.42
    },
    {
      "section": "Business Rules",
      "strategy": "preserve",
      "reason": "Human-managed section, preserving existing content",
      "similarity": 0.95
    },
    {
      "section": "Performance Considerations",
      "strategy": "add",
      "reason": "New required section generated"
    }
  ],
  "summary": {
    "preserved": 2,
    "replaced": 1,
    "added": 1,
    "flagged": 0
  }
}
```

**Phase:** Phase 2 (deferred from MVP)

**Dependencies:**
- Component 2B: FullASTParser (for section boundary detection)
- Component 3: ValidationEngine (for blocker detection)
- `.akr-config.json` merge configuration

**Human Content Protection Mechanisms:**

In addition to `section_ownership` configuration, the tool supports **inline sentinel markers** for fine-grained content protection:

**Supported Markers:**
```markdown
<!-- HUMAN_MANAGED_START -->
... human-written content that should never be auto-replaced ...
<!-- HUMAN_MANAGED_END -->

<!-- AKR:preserve -->
... single paragraph or block to preserve ...
```

**Behavior:**
- Content between `HUMAN_MANAGED_START/END` is **always preserved**, even if section ownership is `llm`
- `AKR:preserve` protects the next block (paragraph, list, table, or code block)
- Markers are invisible in rendered markdown but visible in source
- Tool logs when markers are encountered (for audit trail)

**Example:**
```markdown
## Business Rules

<!-- HUMAN_MANAGED_START -->
### Team-Specific Constraints
- WebApp1 team requires approval for rules > $10k
- Must sync with FinanceService before commit
<!-- HUMAN_MANAGED_END -->

### Standard Rules
(LLM can regenerate this section)
```

**Rationale:** Configuration files can become stale; inline markers travel with the content and are harder to forget.

**Success Criteria:**
- 0 accidental overwrites of human content in Phase 2 rollout
- >90% of incremental updates use merge instead of full rewrite
- <5% of merges require manual conflict resolution
- **Merge is idempotent:** Running merge twice with same inputs produces no additional changes (prevents drift where each run rewrites slightly differently)

**Merge Conflict Handling:**

When a section is flagged as `human_review` (e.g., hybrid ownership with detected changes), the tool applies a **safe conflict resolution strategy**:

**Output Format:**
```markdown
## Section Name

<!-- EXISTING CONTENT (preserved) -->
... original human-written or hybrid content ...

---

<details>
<summary>❓ <b>HUMAN: Resolve Conflict</b> - LLM generated new content for this section</summary>

**Generated content (review and merge manually):**

... newly generated content from LLM ...

**Detected changes:**
- Content similarity: 0.65
- Structural changes: Added 2 subsections
- Recommendation: Review and integrate relevant updates

</details>

---
```

**Rationale:**
- **Preserves existing content** (no data loss)
- **Makes conflict visible** (developer sees both versions)
- **Collapsible details** (doesn't clutter rendered doc)
- **Actionable** (human can review and integrate)
- **Auditable** (marked with `❓ HUMAN:` prefix for tracking)

**Alternative Strategy (if markdown renderer doesn't support `<details>`):**
```markdown
## Section Name

... existing content ...

---

> ❗ **MERGE CONFLICT** 
> LLM generated updated content for this section.  
> Review the changes below and integrate manually:

<!-- LLM_GENERATED_START -->
... new content ...
<!-- LLM_GENERATED_END -->

---
```

This ensures **no silent loss** even in hybrid/human-managed sections with conflicts.

---

## Key Design Decisions

### Decision 1: Schema Strategy - Resolve Contradiction

**Question:** Should schema be hardcoded or derived from templates?

**Critical Note:** Previous version had internal contradiction:
- Said: "TemplateSchemaBuilder parses templates to extract structure"
- But also said: "Schema defined in code (not in template)" as mitigation

**Recommended Strategy (M365 Copilot):**
**Runtime parsing with caching** (not hardcoded)

**Rationale:**
- ✅ Ensures schema always matches actual template (no drift)
- ✅ Automatically picks up template changes (e.g., new required section)
- ✅ No duplication (single source of truth = template file)
- ✅ Easier maintenance (update template, schema updates automatically)
- ❌ Slight parsing overhead (mitigated by caching)

**Implementation:**
```
1. Load template markdown from AKRResourceManager
2. Parse for required sections (regex: "^## " headings)
3. Build schema structure
4. Cache with timestamp + checksum
5. On next run, validate checksum (if template unchanged, use cache)
6. If template changed, re-parse and update cache
```

**Risk Mitigation:**
- Version templates in git (track schema changes)
- Unit tests snapshot expected sections per template
- Schema caching with checksum validation
- Logging when schema is regenerated (indicates template change)

---

### Decision 2: Validation Timing

**Question:** When should validation occur?

**Options:**
- **Option A:** Validate after LLM generation, before write (current plan)
- **Option B:** Validate after write, surface warnings to user
- **Option C:** Validate in real-time during LLM streaming

**Selected:** **Option A** (validate before write)

**Rationale:**
- ✅ Prevents writing malformed documentation to repo
- ✅ Enables retry without re-reading bad files
- ✅ Aligns with security model (don't write unsafe content)
- ✅ User sees validation result immediately
- ❌ Adds ~5-10s latency for retry (acceptable tradeoff)

---

### Decision 2: Auto-Fix Strategy

**Question:** When schema violations occur, what should tool do?

**Options:**
- **Option A:** Auto-fix everything possible, flag rest for manual review
- **Option B:** Only flag violations, never auto-fix
- **Option C:** Auto-fix only highest-confidence issues, retry LLM for rest

**Selected:** **Option A** (auto-fix simple + retry for complex)

**Rationale:**
- ✅ Removes simple, structural issues (wrong order, missing headers)
- ✅ Retries LLM only when content regeneration needed
- ✅ Reduces manual intervention
- ✅ Fastest path to valid documentation
- ❌ Auto-fixes may change user intent (mitigated by logging all fixes)

**Auto-fix candidates:**
- Missing YAML front matter (generate deterministically)
- Sections reordered (reorder to template order)
- Wrong heading levels (adjust # symbols)
- Missing empty section (add with ❓ placeholder)

**Not auto-fixable:**
- Incomplete content (needs LLM regeneration)
- Wrong format (diagrams, tables - needs LLM understanding)
- Insufficient depth (needs LLM content generation)

---

### Decision 3: Confidence Scoring

**Question:** How should tool express confidence in validation?

**Options:**
- **Option A:** Boolean pass/fail only
- **Option B:** Confidence score (0-1.0) with violation count
- **Option C:** Severity-based scoring (critical/warning/info)

**Selected:** **Option B** (confidence score 0-1.0)

**Rationale:**
```
Confidence calculation:
  - Perfect compliance = 1.0
  - Each critical violation = -0.3 (missing required section)
  - Each warning violation = -0.1 (format inconsistency)
  - Each info violation = -0.05 (minor formatting)
  - Auto-fixable issues = -0.05 (low confidence until fixed)

Example:
  - All required sections present, YAML OK, markers OK = 1.0 (PASS)
  - Missing 1 section, reordered = 0.4 (RETRY)
  - Missing YAML only = 0.95 (AUTO-FIX)
```

**Benefits:**
- Tells user "how wrong" the output is
- Guides retry strategy (low confidence = retry, high = auto-fix)
- Enables analytics (track confidence trends)

---

### Decision 4: Retry Logic

**Question:** How many retries before surfacing to user?

**Options:**
- **Option A:** Single retry (strict prompt → fixed output)
- **Option B:** Two retries (strict, then ultra-strict)
- **Option C:** No retries (tell user, let them try manual fix)

**Selected:** **Option A** (single retry)

**Rationale:**
- ✅ 80% of LLM failures fixable with strict prompt
- ✅ Second retry shows diminishing returns (10% additional)
- ✅ Avoids excessive LLM calls (cost/latency)
- ✅ If still failing, surface to user with clear guidance

**Retry prompt characteristics:**
- Explicit format requirements
- Section order checklist
- Example of correct format
- Marker placement rules
- No optional sections (all required for retry)

---

### Decision 5: Path Security Validation

**Question:** Should tool validate output paths against `.akr-config.json` mappings?

**Options:**
- **Option A:** Yes, block writes outside configured paths
- **Option B:** Yes, warn but allow override
- **Option C:** No, let Agent mode handle security

**Selected:** **Option A** (block writes outside configured paths)

**Rationale:**
- ✅ Enforces governance (docs only in designated folders)
- ✅ Prevents accidental writes to wrong location
- ✅ Aligns with MCP security model
- ✅ Respects team's organizational rules
- ❌ Requires config validation (add to tool requirements)

**Implementation:**
```
if output_path not in workspace_root:
  REJECT: "Path outside workspace"

if not derived_from_matching_pathMapping(source_files, output_path):
  REJECT: "Output path not derived from pathMappings transformation"
  
allow write
```

---

## Integration Architecture

### Template Source Precedence

**Question:** Where does the tool load template markdown from?

**Answer:** Tool supports multiple sources with precedence rules to balance production consistency with team flexibility.

**Precedence Order (highest to lowest):**

1. **Team template extension** (if configured in `.akr-config.json`)
   - **Purpose:** Team-specific customizations (e.g., add sections, adjust markers)
   - **Governance:** Team-controlled, optional
   - **Example:** `team/ui-component-webapp1.md` extends `ui_component_template.md`
   - **Use case:** WebApp1 team requires additional "Performance Considerations" section

2. **Local clone path** (if configured: `templates.local_path` AND `allow_local_templates=true`)
   - **Purpose:** Development/testing of template changes before production rollout
   - **Governance:** Gated by config flag (disabled by default in production)
   - **Example:** Template author testing new structure before committing
   - **Use case:** Template maintainer iterating on new section organization

3. **AKRResourceManager** (default fallback: `akr://template/...`)
   - **Purpose:** Production default, shared across all teams
   - **Governance:** Source of truth maintained by documentation standards team
   - **Example:** `lean_baseline_service_template.md` from `akr_content/templates/`
   - **Use case:** Standard template used by 90% of teams

**Key Clarification:**
- **Production default** = AKRResourceManager (always available, versioned, tested)
- **Team override** = Team extension (opt-in customization, team-managed)
- **Local override** = Local clone (dev/testing only, requires explicit config flag)

**This prevents accidental drift:** Local templates do NOT silently override production unless `allow_local_templates=true` is explicitly set in config.

**Implementation:**
```python
def load_template(template_name: str, config: AKRConfig) -> str:
    # 1. Check team template extension (team customization)
    if config.team_template_extension:
        if exists(config.team_template_extension):
            logger.info(f"Loading team extension: {config.team_template_extension}")
            return read(config.team_template_extension)
    
    # 2. Check local clone path (dev/testing only, gated)
    if config.templates.allow_local_templates and config.templates.local_path:
        local_template = join(config.templates.local_path, template_name)
        if exists(local_template):
            logger.warning(f"Loading LOCAL template (non-production): {local_template}")
            return read(local_template)
    
    # 3. Fallback to AKRResourceManager (production default)
    logger.info(f"Loading production template from AKRResourceManager: {template_name}")
    uri = f"akr://template/{template_name}"
    return AKRResourceManager.get_resource_content(uri)
```

**Config Example:**
```json
{
  "templates": {
    "local_path": "C:/dev/akr-templates",
    "allow_local_templates": false,  // ❗ Must be explicit true to enable local override
    "team_template_extension": "team/extensions/ui-webapp1.md"
  }
}
```

**Recommended Strategy for Teams:**

For per-module documentation, teams should **prefer `pathMappings` with `{module}` placeholders** as the primary strategy:

**✅ Preferred Approach: `pathMappings` with `{module}`**
```json
"pathMappings": {
  "src/**/Enrollment*.cs": "docs/services/{module}.md",
  "src/services/**/*.cs": "docs/services/{module}.md"
}
```

**Why preferred:**
- Pattern-based (scales to many modules without explicit config per module)
- Flexible (works with glob matching, DRY principle)
- Automatic (tool infers module name from common prefix)
- Consistent with per-file mappings (same schema)

**✅ Use `moduleNamePatterns` when:**
- Explicit file lists required (module boundaries are not glob-pattern-friendly)
- Module composition is non-standard (files don't share naming convention)
- Need to document exact file membership for governance

**Example: Mixed Strategy**
```json
{
  "documentation": {
    "pathMappings": {
      "src/services/**/*.cs": "docs/services/{module}.md"  // Default for most modules
    },
    "moduleNamePatterns": {
      "CoreAuthentication": [                              // Exception: specific files
        "src/Auth/AuthService.cs",
        "src/Identity/IdentityProvider.cs",
        "src/Security/TokenValidator.cs"
      ]
    }
  }
}
```

**Precedence (when both defined):**
1. Explicit `module_name` parameter (tool invocation)
2. `moduleNamePatterns` lookup (if files match a defined module)
3. `pathMappings` with `{module}` (infer from common prefix)

**Adoption Guidance:**
- **Start with `pathMappings`** (simpler, covers 80% of cases)
- **Add `moduleNamePatterns`** only for exceptions where inference fails or explicit control needed
- Both strategies are fully supported and can coexist

---

### Config Schema Support

**Question:** Which `.akr-config.json` schema does the tool support?

**Answer:** Tool supports **both** schemas for backward compatibility, plus new Phase 2 merge configuration.

**Schema A: `documentation.pathMappings` (preferred, new)**

**Flexible Mapping Format:** Each pathMapping value can be either:
- **Simple string** (80% of cases): `"output/path/{name}.md"`
- **Object with overrides** (when you need per-mapping control)

```json
{
  "documentation": {
    "output_path": "docs/",
    "pathMappings": {
      "src/components/**/*.tsx": {
        "output": "docs/ui/{name}.md",
        "mode": "per_file",
        "template": "ui_component_template.md",
        "write_policy": {
          "default_update_mode": "merge_sections"
        }
      },
      "src/**/Enrollment*.cs": {
        "output": "docs/services/{module}.md",
        "mode": "per_module",
        "module": "Enrollment",
        "template": "lean_baseline_service_template.md",
        "merge": {
          "enabled": true,
          "section_ownership": {
            "Business Rules": "human",
            "Questions & Gaps": "human"
          }
        }
      },
      "src/services/**/*.cs": "docs/services/{module}.md"
    },
    "write_policy": {
      "default_overwrite": false,
      "default_update_mode": "merge_sections",
      "require_explicit_overwrite": true
    },
    "merge": {
      "enabled": true,
      "section_ownership": {
        "What it does": "llm",
        "How It Works": "llm",
        "Business Rules": "human",
        "Questions & Gaps": "human"
      },
      "rewrite_threshold": {
        "blockers": 3,
        "changed_percentage": 0.6
      },
      "default_ownership": "llm"
    }
  },
  "templates": {
    "local_path": "C:/dev/akr-templates",
    "allow_local_templates": false,
    "team_template_extension": "team/extensions/ui-webapp1.md"
  },
  "validation": {
    "enforceYamlFrontmatter": true,
    "enforceAllRequiredSections": true,
    "autoFixSimpleIssues": true,
    "maxRetries": 1,
    "confidenceThreshold": 0.85,
    "severityOverrides": {
      "markers": "WARN",
      "architecture_diagrams": "WARN",
      "section_length": "WARN"
    }
  }
}
```

**Schema B: `component_mappings` (legacy, existing)**
```json
{
  "component_mappings": [
    {
      "source_pattern": "src/services/**/*.ts",
      "doc_path": "docs/services/",
      "template": "service-standard",
      "team_template_extension": "team/ui-component-webapp1.md"
    }
  ]
}
```

**Precedence Rules:**
1. If `documentation.pathMappings` exists → **use it** (preferred)
2. Else if `component_mappings` exists → **use it** (legacy fallback)
3. Else if `documentation.output_path` exists → **use as base default**
4. Else → **validation error** (no path configuration found)

**Effective Settings Precedence (Global vs Per-Mapping Overrides):**

When resolving effective configuration values across multiple layers:

1. **Tool call parameters** (if provided): `overwrite`, `update_mode`, `mode`
2. **Matching `documentation.pathMappings` entry overrides** (object form): `template`, `write_policy.default_update_mode`, `merge` settings
3. **Global documentation defaults**: `documentation.write_policy.*`, `documentation.merge.*`
4. **Hard-coded tool defaults** (only if not set anywhere): `overwrite=false`, `merge_sections` (Phase 2+)

**Example:** If a pathMapping defines `{"write_policy": {"default_update_mode": "replace"}}` but the tool call includes `update_mode="merge_sections"`, the tool call parameter wins.

**Rationale:** This precedence model allows per-mapping customization while maintaining predictable override semantics.

**Migration Path:**
- Teams should eventually migrate to `documentation.pathMappings`
- Tool warns if using legacy `component_mappings` (log deprecation notice)
- Both schemas supported until migration complete

**Phase 2 Configuration:**
- `write_policy`: Controls overwrite/merge behavior (Phase 2)
- `merge.enabled`: Enables SectionMergeEngine (Phase 2)
- `merge.section_ownership`: Defines LLM vs human-managed sections (Phase 2)
- `merge.rewrite_threshold`: Thresholds for recommending full rewrite (Phase 2)
- `templates.allow_local_templates`: Gate for local template override (Phase 1+)
- `validation.severityOverrides`: Per-team validation rule customization (Phase 2)

---

### Integration Point 1: With `documentation.py`

**Relationship:** Consumer of template metadata

**How it works:**
```
tool: template_enforcement_tool
  ↓
calls: documentation.py.get_template_metadata(template_name)
  ↓
gets: TemplateMetadata (complexity, project_type, uri, sections, etc.)
  ↓
uses: metadata to build validation schema
```

**API Contract:**
- Input: template_name (string)
- Output: TemplateMetadata object
- Already exists in current code

---

### Integration Point 2: With `server.py`

**Relationship:** Orchestrator calls tool, tool validates + writes

**Updated workflow in `server.py`:**
```python
def generate_documentation(template, source_files, file_metadata, config):
    # Step 1: Get prompt
    prompt = build_documentation_prompt(template, source_files)
    
    # Step 2: Call LLM
    generated_markdown = llm.generate(prompt)
    
    # Step 3: Call enforcement tool (validates + writes)
    result = template_enforcement_tool.validate_and_write(
        generated_markdown=generated_markdown,
        template_name=template,
        file_metadata=file_metadata,
        config=config,
        dry_run=False  # Set to True for preview
    )
    
    # Step 4: Handle result
    if result.written:
        return success(result.file_path, result.summary)
    
    elif result.severity_summary.blockers > 0:
        # Retry with stricter prompt
        strict_prompt = result.retry_prompt
        regenerated = llm.generate(strict_prompt)
        
        # Validate + write again
        result2 = template_enforcement_tool.validate_and_write(
            regenerated, template, file_metadata, config
        )
        
        if result2.written:
            return success(result2.file_path, result2.summary)
        else:
            return error("Still invalid after retry", result2.violations)
    
    else:
        return error("Manual review required", result.suggestions)
```

**Key Change:** **Tool owns the write** (not server.py). Server calls tool, tool returns `WriteResult`.

**API Contract:**
```
Input:
  - generated_markdown: str
  - template_name: str
  - file_metadata: dict
  - config: dict (workspace_root, optional requested output_path)
  - overwrite: bool (optional, default false)
  - update_mode: str (optional: replace | merge_sections | append; default from documentation.write_policy.default_update_mode)

Output:
  - valid: bool
  - violations: List[Violation]
  - confidence: float
  - corrected_markdown: Optional[str]
  - retry_prompt: Optional[str]
  - suggestions: List[str]
```

---

### Integration Point 3: With `AKRResourceManager`

**Relationship:** Consumer of template content

**How it works:**
```
tool: template_enforcement_tool
  ↓
needs: Full template markdown (to build schema)
  ↓
calls: AKRResourceManager.get_resource_content(template_uri)
  ↓
gets: Complete template markdown
  ↓
builds: TemplateSchema from content
```

**API Contract:**
- Input: template_uri (e.g., "akr://template/lean_baseline_service_template.md")
- Output: Template content (markdown string)
- Already exists in current code

---

### Integration Point 4: With `.akr-config.json`

**Relationship:** Consumer of path mappings and configuration

**How it works:**
```
tool: template_enforcement_tool
  ↓
validates: output_path against config
  ↓
reads: .akr-config.json
  ↓
checks: output_path is derived from matching pathMappings transformation
  ↓
allows/denies: File write
```

**Config structure expected:**
```json
{
  "documentation": {
    "output_path": "docs/",
    "pathMappings": {
      "src/services/**/*.cs": "docs/services/{name}.md"
    }
  }
}
```

**Note:** `pathMappings` is treated as a **transformation rule** (source glob → output pattern), not just a folder allow-list. The tool validates that the resolved output path was derived from the matching mapping.

---

### Integration Point 5: With PR Operations

**Relationship:** Source of validation metadata for PR

**How it works:**
```
After successful validation and write:

tool: template_enforcement_tool
  ↓
returns: Validation metadata
  ↓
passed to: PR_Manager.create_documentation_pr()
  ↓
includes: Validation metadata in PR body
  ```

**PR body example:**
```
## Documentation Generated

- **File:** docs/services/EnrollmentService.md
- **Template:** Lean Baseline Service
- **Validation:** PASSED ✅
  - All required sections present
  - YAML front matter valid
  - Format compliance: 100%
- **Complexity:** Lean (70% complete)
- **Next steps:** Manual review of business context (marked with ❓)
```

---

## Mode Resolution & Output Path Rules

The enforcement tool supports both **per-file** and **per-module** documentation modes. This section defines how the tool determines which mode to use and how output paths are computed.

### Mode Auto-Detection

When `mode` parameter is `"auto-detect"` (default):

**Auto-detect logic:**
- **If single source file** (`len(source_files) == 1`)
  - **Resolved mode:** `per_file`
  - **Rationale:** Single file → single doc

- **If multiple source files** (`len(source_files) > 1`)
  - **Resolved mode:** `per_module`
  - **Rationale:** Multiple files → module-level doc

### Output Path Computation

#### Per-File Mode

Uses `pathMappings` with `{name}` substitution:

```json
"pathMappings": {
  "src/services/**/*.cs": "docs/services/{name}.md"
}
```

**Algorithm:**
1. Match source file path against glob patterns
2. Extract file stem (filename without extension)
3. Replace `{name}` in output pattern
4. Validate resolved path (must be inside workspace + docs root)

**Example:**
- Source: `src/services/Enrollment/EnrollmentService.cs`
- Pattern match: `src/services/**/*.cs`
- File stem: `EnrollmentService`
- Output pattern: `docs/services/{name}.md`
- Resolved path: `docs/services/EnrollmentService.md` ✅

#### Per-Module Mode

Uses `pathMappings` with `{module}` substitution OR explicit `moduleNamePatterns`:

**Option A: Module name in mapping**
```json
"pathMappings": {
  "src/**/Enrollment*.cs": "docs/services/{module}.md"
}
```

**Option B: Explicit module definition**
```json
"moduleNamePatterns": {
  "Enrollment": [
    "src/Domain/Entities/Enrollment.cs",
    "src/Domain/Repositories/IEnrollmentRepository.cs",
    "src/Domain/Services/IEnrollmentService.cs",
    "src/Controllers/EnrollmentsController.cs"
  ]
}
```

**Algorithm:**
1. If `module_name` parameter provided, use it directly
2. Else if `moduleNamePatterns` defined, lookup module by file list
3. Else infer from common prefix/pattern in source files using these heuristics:
   - Extract common "root name" from filenames (e.g., Enrollment from Enrollment.cs, IEnrollmentRepository.cs)
   - Strip common prefix/suffix patterns (`I`, `Service`, `Controller`, `Repository`)
   - Choose the most frequent token across all files
   - If ambiguous, use the shortest common name (likely the root entity)
4. Replace `{module}` in output pattern
5. Validate resolved path

**Module Derivation Examples:**
- Files: `[Enrollment.cs, IEnrollmentRepository.cs, EnrollmentService.cs, EnrollmentsController.cs]`
  - Common tokens: `Enrollment` (appears in all 4)
  - Derived module: `Enrollment` ✅
  
- Files: `[User.cs, UserService.cs, IUserRepository.cs, UserValidator.cs]`
  - Common tokens: `User` (appears in all 4)
  - Derived module: `User` ✅
  
- Files: `[OrderProcessor.cs, OrderValidator.cs, OrderRepository.cs]`
  - Common tokens: `Order` (appears in all 3)
  - Derived module: `Order` ✅

**Example:**
- Source files: `[Enrollment.cs, IEnrollmentRepository.cs, EnrollmentService.cs, EnrollmentsController.cs]`
- Module name: `Enrollment` (from parameter or pattern match or inferred)
- Output pattern: `docs/services/{module}.md`
- Resolved path: `docs/services/Enrollment.md` ✅

### Path Validation Rules

All resolved output paths MUST satisfy:

1. **Inside workspace root:** `resolved_path.startswith(workspace_root)`
2. **Inside allowed doc root:** `resolved_path.startswith(doc_root)` (from config)
3. **No path traversal:** No `..` segments after normalization
4. **Matches config pattern:** Consistent with the mapping that matched source input

If validation fails, tool returns error (does not write).

---

## File Overwrite & Merge Policy

The enforcement tool provides configurable behavior for handling existing documentation files.

### Overwrite Parameter

**Default: `overwrite=false`** (safe by default)

| Scenario | `overwrite=false` | `overwrite=true` |
|----------|-------------------|------------------|
| File does not exist | Create new file ✅ | Create new file ✅ |
| File exists | Return error ❌ | Replace file ✅ |

**Phase 1 Behavior (MVP):**
- Tool only supports `overwrite=true` (replace) or fail-if-exists
- No merge capabilities in Phase 1
- User must explicitly set `overwrite=true` to replace existing docs
- **Safe default for MVP:** Fail-if-exists prevents accidental overwrites

**⚠️ Important Context:**
Although Phase 1 MVP uses fail/overwrite semantics for safety, **Phase 2 (SectionMergeEngine) is the expected default for teams maintaining docs with human content**. Phase 1 is designed for:
- Initial documentation creation (new projects, greenfield)
- Migration scenarios where docs don't yet exist
- Full rewrites where overwrite is intentional

Once Phase 2 ships, `update_mode=merge_sections` becomes the recommended default to preserve manual edits.

**Error Message (when overwrite=false and file exists):**
```json
{
  "success": false,
  "error": "FILE_EXISTS",
  "message": "Documentation file already exists at docs/services/Enrollment.md. Set overwrite=true to replace, or use update_mode in Phase 2 for section-level merge.",
  "existing_path": "docs/services/Enrollment.md"
}
```

### Update Mode (Phase 2+)

**Parameter: `update_mode`** (Phase 2 feature, not in MVP)

**Available Modes:**

- **`replace`**: Overwrite entire file
  - **Behavior:** Replaces entire document with newly generated content
  - **Use case:** Major refactor, template change, fresh start after threshold exceeded
  - **Risk:** Destroys all human-written content (use with caution)

- **`merge_sections`**: Section-level merge (see Component 8: SectionMergeEngine)
  - **Behavior:** Merges only sections impacted by code changes, preserves human-managed sections
  - **Use case:** Incremental updates, preserve manual edits, team collaboration
  - **Recommended:** Default for Phase 2+ when merge is enabled

- **`append`**: Add new sections only, preserve all existing content
  - **Behavior:** Adds missing required sections, never replaces existing sections
  - **Use case:** Expanding docs progressively, ultra-conservative merge
  - **Risk:** May result in stale sections if code changed significantly

**Phase 2 Workflow:**
```
IF file exists AND update_mode != "replace":
    Load existing doc
    Parse into sections (using Component 2B: FullASTParser)
    Merge via SectionMergeEngine (see Component 8)
    Write merged result
ELSE:
    Write new content (replace or create)
```

**Rewrite Threshold Handling:** If a full rewrite is recommended and `overwrite=false`, the tool **must not write** and should return `requires_overwrite=true` with `suggested_action="re-run with overwrite=true"`.

### Effective `update_mode` Resolution Order
1. Tool call parameter `update_mode` (if provided)
2. Matching `documentation.pathMappings` mapping override (object form can include `write_policy.default_update_mode`)
3. `documentation.write_policy.default_update_mode`
4. Fallback default: `"merge_sections"` (Phase 2+ only; see gating below)

### Phase 1 Gating Rule (No Merge Support)
If Phase 1 (no SectionMergeEngine / no FullASTParser) and resolved `update_mode` is `merge_sections` or `append`, **return a clear error**:

```
UPDATE_MODE_NOT_SUPPORTED_IN_PHASE1
Suggested actions:
  - Re-run with overwrite=true (replace), OR
  - Upgrade to Phase 2 to enable merge/append
```

### Phase 2+ Merge Disabled Gating
If Phase 2+ runtime exists but `documentation.merge.enabled=false` and effective `update_mode` is `merge_sections`, **return error**:

```
MERGE_DISABLED
Reason: documentation.merge.enabled=false but update_mode resolved to merge_sections
Suggested actions:
  - Enable merge: Set documentation.merge.enabled=true in .akr-config.json, OR
  - Use replace mode: Re-run with update_mode=replace and overwrite=true
```

### Replace Mode Overwrite Requirement
If `update_mode=replace` and file exists and `overwrite=false`, **return error**:

```
REPLACE_REQUIRES_OVERWRITE
Reason: update_mode=replace requires overwrite=true when file exists
Suggested action: Re-run with overwrite=true
```

**Rationale:** `update_mode=replace` is an explicit "overwrite entire file" operation. Requiring `overwrite=true` prevents accidental data loss and keeps overwrite semantics deterministic.

### Configuration

Teams can set defaults in `.akr-config.json`:

```json
{
  "documentation": {
    "write_policy": {
      "default_overwrite": false,
      "default_update_mode": "merge_sections",
      "require_explicit_overwrite": true
    }
  }
}
```

---

## Telemetry & Audit Logging

The enforcement tool emits structured log events for enterprise rollout tracking and governance.

### Log Event Schema

All events follow this structure:

```json
{
  "timestamp": "ISO-8601",
  "event_type": "SCHEMA_BUILT | VALIDATION_RUN | WRITE_ATTEMPT | WRITE_SUCCESS | WRITE_FAILURE",
  "session_id": "uuid",
  "user": "username or agent (optional)",
  "workspace": "absolute path",
  "details": { /* event-specific fields */ }
}
```

**User Identity Handling:**
- `user` field is **optional** (MCP server may not reliably know real user identity depending on client/environment)
- If unavailable, use `"unknown"` or `"client:<clientName>"`
- `session_id` remains the stable correlation ID for tracking related operations
- User identity is best-effort; don't fail logging if user cannot be determined

### Event Types

#### 1. SCHEMA_BUILT
Emitted when template schema is built or loaded from cache.

```json
{
  "event_type": "SCHEMA_BUILT",
  "details": {
    "template_name": "lean_baseline_service_template.md",
    "checksum": "sha256:abc123...",
    "source": "resource_manager | local_clone | team_extension",
    "cached": true,
    "required_sections": ["YAML", "Service Title", "Quick Reference", ...]
  }
}
```

#### 2. VALIDATION_RUN
Emitted after validation completes (success or failure).

```json
{
  "event_type": "VALIDATION_RUN",
  "details": {
    "template": "lean_baseline_service_template.md",
    "effective_mode": "per_module",
    "result": "PASS",
    "blockers": 0,
    "fixable": 0,
    "warnings": 1,
    "confidence": 0.92,
    "duration_ms": 45
  }
}
```

**Field Descriptions:**
- `effective_mode`: Documentation mode used for this validation - `"per_file"` | `"per_module"`
- `result`: Validation outcome - `"PASS"` | `"FAIL"`

#### 3. WRITE_ATTEMPT
Emitted before attempting file write (for audit trail).

```json
{
  "event_type": "WRITE_ATTEMPT",
  "details": {
    "target_path": "docs/services/Enrollment.md",
    "write_action": "create",
    "overwrite": false,
    "update_mode": "merge_sections",
    "effective_mode": "per_module",
    "path_validation": {
      "inside_workspace": true,
      "inside_doc_root": true,
      "allowed": true
    }
  }
}
```

**Field Descriptions:**
- `write_action`: Actual operation performed - `"create"` (new file) | `"replace"` (overwrite) | `"merge"` (section merge)
- `overwrite`: Tool parameter value (boolean)
- `update_mode`: Resolved update mode - `"merge_sections"` | `"replace"` | `"append"`
- `effective_mode`: Documentation mode used - `"per_file"` | `"per_module"`

**`write_action` Derivation Rules:**
- If file doesn't exist → `write_action="create"`
- If `update_mode="replace"` → `write_action="replace"`
- If `update_mode="merge_sections"` → `write_action="merge"`
- If `update_mode="append"` → `write_action="merge"` (append is a merge variant)

**Rationale:** Including `overwrite`, `update_mode`, and `effective_mode` in write attempt logs makes debugging much easier - you can answer "Why did it overwrite?" or "Why did merge fail?" with a single log entry.

#### 4. WRITE_SUCCESS
Emitted after successful file write.

```json
{
  "event_type": "WRITE_SUCCESS",
  "details": {
    "path": "docs/services/Enrollment.md",
    "bytes_written": 12543,
    "sections_merged": 0,
    "sections_replaced": 8,
    "duration_ms": 12
  }
}
```

#### 5. WRITE_FAILURE
Emitted when file write fails (permission, path validation, etc.).

```json
{
  "event_type": "WRITE_FAILURE",
  "details": {
    "path": "docs/services/Enrollment.md",
    "error_type": "PERMISSION_DENIED",
    "error_message": "Permission denied: cannot write to docs/services/",
    "resolved_path": "/abs/path/to/docs/services/Enrollment.md"
  }
}
```

**Field Descriptions:**
- `error_type`: Type of write failure - `"PERMISSION_DENIED"` | `"PATH_VALIDATION_FAILED"` | `"DISK_FULL"`

### Implementation

**Logger Configuration:**
```python
# In server.py or config
logging.config.dictConfig({
    "version": 1,
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/akr-mcp-audit.jsonl",  # JSON Lines format
            "formatter": "json"
        }
    },
    "loggers": {
        "akr.enforcement": {
            "level": "INFO",
            "handlers": ["file"]
        }
    }
})
```

**Usage in Tool:**
```python
import logging
import uuid

logger = logging.getLogger("akr.enforcement")

def validate_and_write(...):
    session_id = str(uuid.uuid4())
    
    # Log schema build
    logger.info({
        "event_type": "SCHEMA_BUILT",
        "session_id": session_id,
        "details": {...}
    })
    
    # Log validation
    logger.info({
        "event_type": "VALIDATION_RUN",
        "session_id": session_id,
        "details": {...}
    })
    
    # Log write attempt
    logger.info({
        "event_type": "WRITE_ATTEMPT",
        "session_id": session_id,
        "details": {...}
    })
    
    # Log outcome
    logger.info({
        "event_type": "WRITE_SUCCESS",
        "session_id": session_id,
        "details": {...}
    })
```

### Analytics Queries

Teams can analyze logs using tools like `jq`, `pandas`, or log aggregators:

```bash
# Count validation failures by template
cat logs/akr-mcp-audit.jsonl | jq -r 'select(.event_type=="VALIDATION_RUN" and .details.result=="FAIL") | .details.template' | sort | uniq -c

# Average blocker count per template
cat logs/akr-mcp-audit.jsonl | jq -r 'select(.event_type=="VALIDATION_RUN") | "\(.details.template),\(.details.blockers)"' | awk -F, '{sum[$1]+=$2; count[$1]++} END {for (t in sum) print t, sum[t]/count[t]}'

# Write success rate
cat logs/akr-mcp-audit.jsonl | jq -r '.event_type' | grep -E 'WRITE_(SUCCESS|FAILURE)' | sort | uniq -c
```

---

## Success Metrics

### Quantitative Metrics

| Metric | Baseline | Target | Method |
|--------|----------|--------|--------|
| **YAML front matter present** | ~0% | >98% | Count generated docs with valid YAML |
| **Required sections present** | ~60% | >98% | Count docs with all required headers |
| **Sections in correct order** | ~50% | >98% | Parse structure, compare order |
| **Heading level consistency** | ~65% | >98% | Check hierarchy (no jumps) |
| **Format violations detected** | 0% | >95% | Ratio of actual violations to detected |
| **Manual format fixes needed** | ~80% | <5% | Manual review of generated docs |
| **Auto-fix success rate** | N/A | >90% | Ratio of auto-fixes that pass validation |
| **LLM retry success rate** | N/A | >80% | Ratio of retries that pass validation |
| **First-pass pass rate** | ~60% | >70% | Docs valid on first generation |

### Qualitative Metrics

| Metric | Measurement |
|--------|-------------|
| **User satisfaction** | Survey: "Docs generated correctly first time" |
| **Reduced manual effort** | Time spent fixing format issues |
| **Trust in tool** | Percentage of generated docs user accepts without changes |
| **Process repeatability** | Consistency across different files/teams |
| **Documentation quality** | Team assessment (before/after) |

### Performance Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| **Validation time** | <5 seconds | Per document |
| **Schema build time** | <1 second | Cached after first run |
| **Auto-fix time** | <2 seconds | Per document |
| **Total generation time** | <60 seconds | Include LLM + validation + retry |
| **Tool startup time** | <2 seconds | Initialize schema cache |

---

## Implementation Roadmap

### Phase 1: Foundation - High ROI (Week 1 - Days 1-4)

**Goal:** Build minimal viable validation + write capability (per M365 Copilot recommendation)

**Scope (Phase 1 ONLY):**
- ✅ YAML front matter generation + validation
- ✅ Required sections presence + order validation
- ✅ Heading level sanity checks
- ✅ Path validation + deterministic file write
- ❌ Defer: Auto-fixes, LLM retry, diagram/table/marker validation

**Deliverables:**
- TemplateSchemaBuilder component (simple, regex-based, cached)
- DocumentStructureParser component (basic, not full AST)
- ValidationEngine component (Phase 1 rules only)
- YAMLFrontmatterGenerator component
- FileWriter component (write with path validation)

**Tasks:**
1. Define data structures (minimal: Section, TemplateSchema, Violation, ValidationResult)
2. Implement TemplateSchemaBuilder (parse "^## " headings via regex, cache with checksum)
3. Implement DocumentStructureParser (extract YAML, headings, section order - basic parsing only)
4. Implement ValidationEngine (Phase 1 checks: YAML, sections, order, heading hierarchy)
5. Implement YAMLFrontmatterGenerator (deterministic YAML generation)
6. Implement FileWriter (path validation + write)
7. Integration: Call from server.py after LLM generation
8. Write unit tests for each component (Phase 1 rules only)

**Estimated Effort:** 24-32 hours (3-4 days, focused on high ROI)

**Success Criteria:**
- YAML generated deterministically for all templates
- Required sections validated correctly
- Heading hierarchy checked
- Path validation works
- FileWriter writes validated markdown
- End-to-end: LLM output → validation → write works
- >85% test coverage for Phase 1 components

**Adoption Note:** Phase 1 is suitable for greenfield docs and initial generation; **Phase 2 is required** for safe incremental updates in mature repos with human-maintained content.

---

### Phase 2: Iteration (Week 2 - Days 5-7)

**Goal:** Auto-fix and retry capabilities (value-add features)

**Deliverables:**
- FormatFixer component (auto-fix structural issues)
- PromptEnhancer component (generate retry instructions)
- Integration with server retry logic
- Basic auto-fix for: missing YAML, reordered sections, wrong heading levels

**Tasks:**
1. Implement FormatFixer (auto-fix Phase 1 violations only)
2. Implement PromptEnhancer (generate retry prompts for content issues)
3. Modify server.py to support retry workflow
4. Add logging for fixes applied
5. Test with 10 real service files
6. Performance profiling (ensure <60 sec total time)
7. Add merge idempotency test: merge(existing, generated) → merged_1; merge(existing=merged_1, generated) → merged_2; assert merged_1 == merged_2

**Estimated Effort:** 16-20 hours (2 days)

**Success Criteria:**
- Auto-fixes applied without breaking content
- Retry prompts clear and actionable
- LLM retry success rate >80%
- End-to-end tests pass

---

### Phase 3: Hardening & Advanced (Week 3+ - Days 8-10)

**Goal:** Production readiness and advanced validation

**Scope:**
- Diagram/table format validation (if Phase 2 successful)
- Marker counting thresholds
- Comprehensive error handling
- Documentation and training

**Tasks:**
- Deferred based on Phase 2 results
- Build on Phase 1-2 foundation
- Focus on value vs. complexity tradeoff

---

### Implementation Timeline Summary

```
Week 1 (Days 1-4):  Phase 1 - Minimal viable validation + write (HIGH ROI)
Week 2 (Days 5-7):  Phase 2 - Auto-fix + retry (VALUE-ADD)
Week 3+ (Days 8+):  Phase 3 - Advanced features (DEFERRED)
```

**Total MVP Effort:** 40-52 hours ≈ 5-7 days (one developer)

**Rationale for Incremental Approach:**
- Deliver value in Phase 1 (YAML + sections + write)
- Validate concept with real data (Phase 2 is optional)
- Avoid overbuilding (complex features deferred until needed)
- Reduce risk (simpler code = fewer bugs)

**Success Criteria:**
- Tool successfully called in generation workflow
- Auto-fixes applied correctly
- Retry prompts produce better compliance
- End-to-end tests pass (generation → validation → fix/retry → write)

---

### Phase 3: Hardening (Week 3 - Days 7-9)

**Goal:** Production-hardening, monitoring, documentation

**Deliverables:**
- Path security validation (enforce .akr-config.json mappings)
- Comprehensive error handling and edge cases
- Monitoring and telemetry (validation success rates, violations tracked)
- Complete documentation of tool behavior
- Test with 20+ real service files (diverse scenarios)

**Tasks:**
1. Add path validation against .akr-config.json
2. Test edge cases (empty files, malformed YAML, unusual structures)
3. Add comprehensive logging and metrics
4. Document tool behavior, API, and troubleshooting
5. Create runbooks for common failure scenarios
6. Performance optimization (caching, lazy loading)
7. User documentation and examples

**Estimated Effort:** 24 hours (3 days × 8 hours)

**Success Criteria:**
- 95%+ test coverage
- All edge cases handled gracefully
- Logging provides clear visibility into validation
- Documentation complete and clear
- Team trained on tool usage

---

### Phase 4: Validation & Optimization (Week 4 - Days 10-12)

**Goal:** Real-world testing and performance optimization

**Deliverables:**
- Beta test with 50+ generated documents
- Performance optimization if needed
- Monitoring dashboard (optional)
- Final production release

**Tasks:**
1. Beta test with diverse repos (monorepo, API-only, UI-only)
2. Collect metrics on success/failure rates
3. Optimize performance if validation time >5 sec
4. Gather user feedback
5. Address production issues
6. Release to production

**Estimated Effort:** 16 hours (2 days × 8 hours)

**Success Criteria:**
- >95% first-pass or auto-fix rate on beta tests
- Validation time <5 seconds
- Zero critical bugs in production
- User feedback positive

**Note:** Phase 1 MVP timeline is 40-52 hours (5-7 days). See Phase 1 roadmap section for detailed breakdown. The above represents the full Phase 1-3 implementation effort if all features were built sequentially.

---

## Risk Assessment

### Risk 1: LLM Retry Loop Exceeds Limits

**Description:** Tool retries LLM, but LLM keeps generating invalid format (loops)

**Likelihood:** Low (10%)

**Impact:** High (blocks generation, user frustration)

**Mitigation:**
- Limit retries to 1 (current plan)
- If still invalid, surface to user with clear guidance
- Implement retry counter and abort after N attempts
- Log all retries for debugging

---

### Risk 2: Auto-Fix Breaks Content Unintentionally

**Description:** FormatFixer reorders sections, loses critical context or meaning

**Likelihood:** Low (15%)

**Impact:** Medium (content quality degraded, user doesn't notice)

**Mitigation:**
- Auto-fix only structural issues (not moving content around)
- Log all fixes applied (user can review/revert)
- Start with conservative auto-fixes (YAML, headers only)
- Gradual expansion after beta testing shows safety

---

### Risk 3: Performance Degradation

**Description:** Tool adds 30+ seconds to generation time (unacceptable)

**Likelihood:** Medium (30%)

**Impact:** Medium (users frustrated with latency)

**Mitigation:**
- Profile each component (identify bottleneck)
- Cache schema building (parse templates once)
- Lazy-load only needed components
- Optimize regex/parsing (avoid O(n²) algorithms)
- Target <5 sec validation + <5 sec retry

---

### Risk 4: Template Parsing Errors / Format Variability

**Description:** Runtime schema extraction fails due to template format variations, malformed templates, or parsing logic errors

**Likelihood:** Medium (30%)

**Impact:** Medium (tool generates incorrect schema, validates against wrong structure)

**Mitigation:**
- **Snapshot tests per template** (expected schema structure captured in unit tests)
- **Strict parsing rules with fallback:** If parsing fails, use `TemplateMetadata.required_sections` as baseline
- **Logging schema regeneration events** (when checksum changes, log what changed)
- **Schema caching with checksum validation** (detect template changes automatically)
- **Template validation tool** (lint templates for consistency before deployment)
- **Version templates in git** (track changes, rollback if needed)
- **Graceful degradation:** If schema parse fails, warn but don't block (use metadata baseline)

**Example Mitigation:**
```python
try:
    schema = TemplateSchemaBuilder.build_schema(template_content)
except ParseError as e:
    logger.warn(f"Template parse failed: {e}, falling back to metadata")
    schema = build_baseline_schema(TemplateMetadata.required_sections)
```

---

### Risk 5: Security: Path Traversal

**Description:** Tool validates path incorrectly, writes outside workspace

**Likelihood:** Low (10%)

**Impact:** Critical (writes to unintended location, security issue)

**Mitigation:**
- Validate output path is within workspace_root
- Validate output path matches .akr-config.json pathMappings
- Reject any path with ".." (parent directory references)
- Log all path validation attempts
- Unit tests for path validation

---

## Appendix

### A. Glossary

| Term | Definition |
|------|-----------|
| **Template Schema** | Formal definition of required structure for a template (sections, order, format rules) |
| **DocumentAST** | Abstract syntax tree of parsed markdown document |
| **Violation** | Format deviation from template schema (e.g., missing required section) |
| **Auto-fixable** | Violation that tool can correct without LLM regeneration |
| **Confidence Score** | 0-1.0 metric indicating likelihood document matches template correctly |
| **Retry Prompt** | Specific, structured LLM prompt designed to fix previous violations |
| **YAML Front Matter** | Structured metadata block at top of markdown document |
| **Marker** | Special emoji (🤖 or ❓) indicating AI-generated or human-needed content |

---

### B. Example: Validation Flow

**Input:**
```
User generates docs for EnrollmentService using Lean Baseline template
```

**Step 1: Parse template schema**
```
Load: lean_baseline_service_template.md
Build: TemplateSchema with required sections, format rules
Cache: For future use
```

**Step 2: LLM generates markdown**
```
LLM produces: 450 lines of documentation
Missing: YAML front matter, Flow It Works section
Present: Other sections but reordered
```

**Step 3: Parse generated markdown**
```
DocumentStructureParser reads generated markdown
Extracts: Sections found (Quick Reference, What & Why, Architecture, etc.)
Missing: YAML front matter, How It Works
Detects: Section order is wrong
```

**Step 4: Validate against schema**
```
ValidationEngine compares:
  Required: [YAML, Service Title, Quick Ref, What & Why, How It Works, ...]
  Found:    [Service Title, Quick Ref, What & Why, Architecture, Data Ops, ...]
  
Violations found:
  - Missing YAML front matter
  - Missing "How It Works" section
  - Section "Architecture" before "Data Operations" (wrong order)

Confidence: 0.45 (45% compliance)
```

**Step 5: Determine next action**
```
YAML front matter missing → AUTO-FIXABLE
Reordered sections → AUTO-FIXABLE
Missing "How It Works" section → REQUIRES LLM RETRY
  
Decision: Apply auto-fixes, then retry LLM
```

**Step 6: Apply auto-fixes**
```
FormatFixer generates YAML front matter
  output: ---\nfeature: TBD\n...\n---

FormatFixer reorders sections to match template
  output: Moved Architecture section to correct position

Result: Corrected markdown with YAML and correct order
Confidence: 0.70 (70% compliance, still missing How It Works)
```

**Step 7: Tool writes file**
```
FileWriter validates target path (must be within workspace, sanitize path)
FileWriter writes corrected markdown to disk:
  output_path: docs/services/backend/EnrollmentService.md
  
Result: File successfully written
Return: { success: true, path: "...", violations_fixed: [...] }
```

**Step 8: Server returns result to Agent**
```
server.py receives result from tool
server.py logs: "Documentation generated for EnrollmentService"
server.py returns: { success: true, file_path: "docs/...", message: "..." }
  
Agent sees success, informs user: 
  "✅ Documentation generated at docs/services/backend/EnrollmentService.md"
```

**Note:** If Step 7 still has BLOCKER violations after retry, tool returns failure:
```json
{
  "success": false,
  "violations": [
    {"type": "missing_section", "section": "How It Works", "severity": "BLOCKER"}
  ],
  "message": "Cannot write file - BLOCKER violations remain after auto-fix and retry"
}
```
Agent can then choose to retry with different prompt or ask user for guidance.Creates specific instructions:
  "Your documentation is missing the required section 'How It Works'.
   After 'What & Why', add section with heading '## How It Works'.
   Include ASCII flow diagram showing step-by-step process.
   
   Example format:
   ┌─────────────────────┐
   │ Step 1: Description │
   └─────────────────────┘"

Includes: Full template structure, section ordering rules, examples
```

**Step 8: Retry LLM with strict prompt**
```
LLM regenerates with new, stricter instructions
  output: Complete documentation with How It Works section

Result: 650 lines, more complete
```

**Step 9: Validate retry result**
```
ValidationEngine re-validates regenerated markdown

Violations: None (all required sections present, correct order, valid YAML)
Confidence: 0.98 (98% compliance)

Decision: PASS ✅
```

**Step 10: Tool writes file and returns result**
```
FileWriter validates output path and writes corrected markdown:
  docs/services/EnrollmentService.md
  
Result: Correctly formatted documentation written ✅

Tool returns to server.py:
{
  "valid": true,
  "written": true,
  "path": "docs/services/EnrollmentService.md",
  "summary": "Documentation validated and written successfully"
}

Server logs operation and returns success to Agent.
```

---

### C. Example: Auto-Fixable vs. Retry-Needed Violations

**Auto-Fixable (Simple, Structural):**
```
❌ Missing YAML front matter
   → Generate with: feature=TBD, domain=TBD, layer=inferred from path

❌ Sections out of order
   → Reorder to: [YAML, Service, Quick Ref, What & Why, How It Works, ...]

❌ Wrong heading levels (### used instead of ##)
   → Change "###" to "##" for top-level sections

❌ Missing "Optional Sections" header
   → Add empty section: "## Optional Sections (Add When Needed)"
```

**Requires LLM Retry (Content, Logic):**
```
❌ Missing entire section (e.g., "How It Works")
   → Need LLM to generate section content

❌ Flow diagram in prose format (not ASCII boxes)
   → Need LLM to understand and reformat to ASCII

❌ Insufficient markers (0x 🤖, 0x ❓)
   → Need LLM to re-examine content and add markers

❌ Table format malformed
   → Need LLM to understand table and reformat correctly

❌ Section content too sparse (1 line for 3-line section)
   → Need LLM to elaborate on content
```

---

## Validation Rules Configuration

The ValidationEngine uses **configurable severity rules** to determine how strictly to enforce different template elements. Teams can tune these in `.akr-config.json` or through team-specific extension files.

### Default Severity Mapping

| Element Type | Default Severity | Rationale |
|-------------|------------------|-----------|
| YAML front matter | BLOCKER | Required for metadata processing, traceability |
| Required sections (presence) | BLOCKER | Core structure - missing sections indicate incomplete docs |
| Section order | FIXABLE | Auto-correctable without LLM |
| Heading level violations | FIXABLE | Auto-correctable without LLM |
| Markers (🤖, ❓, etc.) | **WARN** | Content quality indicators, not structural blockers |
| ASCII diagrams/architecture | **WARN** | Nice-to-have, but subjective formatting |
| Table structure | FIXABLE (simple cases) / WARN (complex) | Tables vary by content type |
| Section length requirements | WARN | Content depth is subjective |

### Configuration Override Example

Teams can override default severities in `.akr-config.json`:

```json
{
  "validation": {
    "enforceYamlFrontmatter": true,
    "enforceAllRequiredSections": true,
    "autoFixSimpleIssues": true,
    "maxRetries": 1,
    "confidenceThreshold": 0.85,
    "severityOverrides": {
      "markers": "BLOCKER",          // Team requires all markers present
      "architecture_diagrams": "FIXABLE",  // Team wants auto-generated diagrams
      "section_length": "WARN"       // Team doesn't enforce minimum length
    }
  }
}
```

### Phase 1 vs Phase 2 Configurability

- **Phase 1 (MVP):** Hard-coded severity mapping (shown in Default Severity Mapping table above)
  - Rationale: Delivers 80% value with zero config complexity
  - Markers, diagrams, tables default to WARN (pass-through)
  
- **Phase 2:** Configurable via `.akr-config.json` `severityOverrides`
  - Teams can tighten (WARN → FIXABLE) or relax (BLOCKER → WARN) rules
  - Per-template overrides possible (e.g., comprehensive template stricter than minimal)

---

### D. Configuration Example (.akr-config.json)

**Complete Modern Config (Recommended):**

```json
{
  "akrMcpServer": {
    "enabled": true,
    "serverPath": "src/server.py"
  },
  "workspaceRoot": "/home/user/projects/training-tracker",
  "documentation": {
    "output_path": "docs/",
    "pathMappings": {
      "src/services/**/*.cs": "docs/services/{name}.md",
      "src/components/**/*.tsx": "docs/ui/{name}.md",
      "src/schema/**/*.sql": "docs/schema/tables/{name}.md"
    },
    "write_policy": {
      "default_overwrite": false,
      "default_update_mode": "merge_sections",
      "require_explicit_overwrite": true
    },
    "merge": {
      "enabled": true,
      "default_ownership": "llm",
      "section_ownership": {
        "Business Rules": "human",
        "Questions & Gaps": "human"
      },
      "rewrite_threshold": {
        "blockers": 3,
        "changed_percentage": 0.6
      }
    }
  },
  "validation": {
    "enforceYamlFrontmatter": true,
    "enforceAllRequiredSections": true,
    "autoFixSimpleIssues": true,
    "maxRetries": 1,
    "confidenceThreshold": 0.85
  }
}
```

---

