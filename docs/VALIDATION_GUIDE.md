# AKR Validation Guide (Phase 3)

## Overview

The AKR validation system provides **dual-faceted validation** using:
- **MCP Tool**: `validate_documentation` — callable from Copilot Chat
- **CLI Tool**: `akr_validate.py` — run locally in your terminal

Both produce consistent results using the same underlying `ValidationEngine`.

---

## Validation Tiers

Validation strictness is controlled by **tier levels**. Choose based on your documentation maturity:

| Tier | Completeness Requirement | Use Case | Violation Behavior |
|------|--------------------------|----------|-------------------|
| **TIER_1** | ≥80% filled sections | Production docs, public APIs | Missing sections = BLOCKER (must fix before merge) |
| **TIER_2** | ≥60% filled sections | Standard development docs | Missing sections = FIXABLE (can auto-fix or fix manually) |
| **TIER_3** | ≥30% filled sections | Early/draft docs | Missing sections = WARN (informational; proceed anyway) |

**Default tier:** TIER_2 (recommended for most projects)

---

## Violation Severity Levels

Three severity levels control whether validation passes or fails:

```
┌──────────────────────────────────────────────────────────────┐
│ BLOCKER (red)    │ Must be fixed before document is valid    │
├──────────────────┼─────────────────────────────────────────────┤
│ FIXABLE (yellow) │ Can be auto-fixed OR fixed manually        │
├──────────────────┼─────────────────────────────────────────────┤
│ WARN (blue)      │ Informational; document is still valid     │
└──────────────────────────────────────────────────────────────┘
```

**Validation passes if:** No BLOCKER violations exist.

---

## Using the MCP Tool (Copilot Chat)

### Basic Usage

```
In Copilot Chat, ask:
"@akr validate my docs/API.md against lean_baseline_service_template"
```

### Tool Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `doc_path` | string | (required) | Path to documentation file (e.g., `docs/API.md`) |
| `template_id` | string | (required) | Template to validate against (e.g., `lean_baseline_service_template`) |
| `tier_level` | string | `TIER_2` | Validation strictness: `TIER_1`, `TIER_2`, or `TIER_3` |
| `auto_fix` | boolean | `false` | Whether to generate auto-fix suggestions |
| `dry_run` | boolean | `true` | Safety default: returns diff without writing to file |

### Tool Output

The tool returns:

```json
{
  "success": true,
  "is_valid": true,
  "completeness": 75.5,
  "tier_level": "TIER_2",
  "violations": [
    {
      "type": "incomplete_section",
      "severity": "FIXABLE",
      "field": "section",
      "field_path": "section.API Contract",
      "message": "Section 'API Contract' is less than 50% complete",
      "suggestion": "Add more details to the API Contract section",
      "auto_fixable": true
    }
  ],
  "violation_count": 1,
  "blocker_count": 0,
  "fixable_count": 1,
  "warning_count": 0,
  "auto_fixed_available": true,
  "diff": "... unified diff of suggested fixes ...",
  "metadata": {
    "template_source": "submodule",
    "validated_at_utc": "2026-02-24T10:30:00Z",
    "server_version": "0.2.0"
  }
}
```

### Example Workflow in Copilot Chat

1. **Generate documentation** using `generate_documentation` tool
2. **Review auto-generated content** in chat
3. **Validate** to check compliance:
   ```
   @akr validate docs/API.md against lean_baseline_service_template tier TIER_2 auto-fix
   ```
4. **Review violations** and auto-fix suggestions
5. **Apply fixes** by accepting the suggested changes or refining in chat
6. **Write to disk** using `write_documentation` tool with final content

---

## Using the CLI Tool (Local Validation)

### Installation

The CLI tool is part of the AKR MCP Server. Ensure `jsonschema>=4.0.0` is installed:

```bash
pip install -r requirements.txt
```

### Basic Usage

```bash
python scripts/akr_validate.py --doc docs/API.md --template lean_baseline_service_template
```

### Command-Line Options

```
Usage: akr_validate.py --doc <path> --template <id> [options]

Required:
  --doc <path>                 Path to documentation file
  --template <id>              Template ID to validate against

Options:
  --tier {TIER_1,TIER_2,TIER_3} Validation strictness (default: TIER_2)
  --auto-fix                   Generate auto-fix suggestions
  --output {json,text}         Output format: 'json' for CI/CD, 'text' for humans (default: json)
  --diff                       Show unified diff of auto-fixes (with --auto-fix and --output text)
  --no-exit-code               Always exit with 0 (for warnings-only runs)
  --help                       Show this help message
```

### Output Formats

#### JSON Output (Default for CI/CD)

```bash
python scripts/akr_validate.py --doc docs/API.md --template lean_baseline_service_template --output json
```

Returns structured JSON (see above) suitable for parsing in CI/CD pipelines.

**Exit codes:**
- `0` = Document is valid (no BLOCKER violations)
- `1` = Document is invalid (has BLOCKER violations)
- `2` = Command-line argument error
- `3` = File not found or read error
- `4` = Validation engine error

#### Text Output (For Human Review)

```bash
python scripts/akr_validate.py --doc docs/API.md --template lean_baseline_service_template --output text
```

Returns human-readable report:

```
======================================================================
AKR VALIDATION REPORT - TIER_2
======================================================================

Document Status: ✗ INVALID
Completeness: 65.3%

VIOLATIONS:
----------------------------------------------------------------------

BLOCKER (1):
  1. YAML front matter is missing.
     Field: frontmatter
     → Add YAML front matter at the start of the document with --- markers.

FIXABLE (2):
  1. Required section 'API Contract' is missing.
     Field: section.API Contract
     → Add a ## API Contract section to your document.
  2. Section 'Quick Reference' is less than 50% complete.
     Field: section.Quick Reference
     → Add more details to the Quick Reference section.

======================================================================
SUMMARY
----------------------------------------------------------------------
Total Violations: 3
  - Blockers:    1
  - Fixable:     2
  - Warnings:    0
======================================================================
```

### Example: Strict Validation with Auto-Fixes

```bash
# Check with TIER_1 (strict)
python scripts/akr_validate.py \
  --doc docs/API.md \
  --template lean_baseline_service_template \
  --tier TIER_1 \
  --auto-fix \
  --output text \
  --diff
```

---

## Violation Types

### YAML Front Matter Violations

| Type | Severity (Default) | Auto-Fixable | Description |
|------|-------------------|--------------|-------------|
| `missing_yaml_frontmatter` | BLOCKER | Yes | YAML front matter is missing entirely |
| `invalid_yaml_syntax` | BLOCKER | No | YAML syntax is malformed |
| `missing_yaml_field` | BLOCKER | No | Required YAML field is missing (e.g., `project`, `repo`) |
| `invalid_yaml_field_type` | BLOCKER | No | YAML field has wrong type (e.g., number instead of string) |

### Section Violations

| Type | Severity (Tier-Based) | Auto-Fixable | Description |
|------|-------------------|--------------|-------------|
| `missing_required_section` | BLOCKER (T1), FIXABLE (T2/T3) | Yes | Required section heading is missing |
| `wrong_section_order` | BLOCKER (T1), FIXABLE (T2/T3) | Partial | Section order doesn't match template |
| `incomplete_section` | FIXABLE (T1/T2), FIXABLE (T3) | No | Section has <50 words and no table/list |

### Heading Violations

| Type | Severity | Auto-Fixable | Description |
|------|----------|--------------|-------------|
| `invalid_heading_hierarchy` | WARN | No | Heading levels skip (e.g., `##` → `####`) |

---

## Auto-Fix Capabilities

Auto-fix can address these common issues:

### ✓ Can Auto-Fix

- **Missing YAML frontmatter** → Inserts minimal YAML at document start
- **Missing required sections** → Adds section stubs with placeholder text
- **Section order** → Reorders sections to match template (planned enhancement)

### ✗ Cannot Auto-Fix

- YAML syntax errors (must fix manually)
- Invalid field types (must fix manually)
- Incomplete section content (requires human authorship)

After auto-fix, **always review the suggested changes** before applying.

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Validate Documentation

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Validate docs
        run: |
          python scripts/akr_validate.py \
            --doc docs/API.md \
            --template lean_baseline_service_template \
            --tier TIER_2 \
            --output json > validation_report.json
        
      - name: Comment on PR
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('validation_report.json', 'utf8'));
            const status = report.is_valid ? '✓' : '✗';
            const comment = `
            ## ${status} Documentation Validation Report
            
            - **Status:** ${report.is_valid ? 'Valid' : 'Invalid'}
            - **Completeness:** ${report.completeness_percent}%
            - **Tier:** ${report.tier_level}
            - **Violations:** ${report.summary.total_violations}
              - Blockers: ${report.summary.blockers}
              - Fixable: ${report.summary.fixable}
              - Warnings: ${report.summary.warnings}
            `;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

---

## Troubleshooting

### Issue: "Validation engine not available"

**Solution:** Ensure `jsonschema>=4.0.0` is installed:
```bash
pip install jsonschema>=4.0.0
```

### Issue: "Template not found"

**Solution:** Verify template ID is correct. List available templates:
```
@akr list-resources   # In Copilot Chat
```

### Issue: Auto-fix suggestions look incomplete

**Auto-fix is intentionally conservative.** It handles structural issues (missing sections) but not content quality. Always review suggestions and enhance manually.

### Issue: Validation passes locally but fails in CI/CD

**Common causes:**
- Different Python versions (use 3.10+)
- Missing dependencies in CI environment
- Different working directory (use absolute or repo-relative paths)

---

## Best Practices

1. **Start with TIER_3 (lenient)** for draft docs, then graduate to TIER_2 and TIER_1
2. **Review auto-fixes before applying** — they handle structure, not semantics
3. **Use `--diff` in text mode** to see exactly what changes are proposed
4. **Validate early and often** during authorship, not only at end
5. **In CI/CD, default to TIER_2** for production docs

---

## Advanced: Custom Validation Rules (v0.3.0+)

Future versions will support:
- Custom violation types per template
- Custom completeness thresholds
- Semantic validation (e.g., "API Contract must have table")
- Auto-fix plugins

---

## Reference

- **Related files:**
  - [src/tools/validation_library.py](../src/tools/validation_library.py) — Core validation engine
  - [scripts/akr_validate.py](../scripts/akr_validate.py) — CLI tool
  - [src/server.py](../src/server.py) — MCP tool integration

- **Related concepts:**
  - [ARCHITECTURE.md](./ARCHITECTURE.md) — System design and components
  - [IMPLEMENTATION_PLAN_V0.2.0.md](./IMPLEMENTATION_PLAN_V0.2.0.md) — Phase breakdown and roadmap

---

**Version:** 0.2.0  
**Last Updated:** February 24, 2026  
**Status:** Phase 3 Implementation Complete
