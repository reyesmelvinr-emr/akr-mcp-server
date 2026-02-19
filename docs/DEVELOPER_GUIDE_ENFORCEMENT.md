# Developer Guide: Enforcement Integration

## Overview
The enforcement gate ensures all documentation writes are validated against AKR templates, YAML front matter requirements, and section order rules before any file is written or committed.

### High-Level Flow

```
LLM Output
   │
   ▼
[ENFORCEMENT: enforce_and_fix()]  ◄── HARD GATE
   │
   ├─→ INVALID? Return error, no write
   │
   └─→ VALID?
       │
       ▼
   [Insert AI header AFTER YAML]
       │
       ▼
   [DocumentationWriter.write_file()]
       │
       ▼
   stage → commit → push (git workflow)
```

## APIs

### write_documentation
Use for new documentation writes. This call enforces templates and writes only if the content is valid.

Required inputs:
- `content`
- `source_file` (repo-relative)
- `doc_path` (repo-relative)

Optional inputs:
- `template` (default: standard_service_template.md)
- `component_type`
- `overwrite`

### update_documentation_sections_and_commit
Use for surgical updates to existing docs. This path updates sections, then enforces and commits.

Required inputs:
- `doc_path` (repo-relative)
- `section_updates` (dict of section_id → new content)

Optional inputs:
- `template`
- `source_file`
- `component_type`
- `add_changelog`

## Configuration
Enforcement settings are read from `config.json` at:

```
config["documentation"]["enforcement"]
```

Key fields:
- `enabled` (bool)
- `validationStrictness` (baseline)
- `requireYamlFrontmatter` (bool)
- `enforceSectionOrder` (bool)
- `autoFixEnabled` (bool)
- `allowRetry` (bool)
- `maxRetries` (int)
- `writeMode` (git)
- `allowWorkflowBypass` (bool, default false)

**Safety rule:** If `enabled=false`, all write operations refuse to write.

## Template Resolution
Templates are loaded via `AKRResourceManager` from:

```
akr_content/templates/
```

## Telemetry
The enforcement logger writes structured events to:

```
logs/enforcement.jsonl
```

Key event types:
- `SCHEMA_BUILT`
- `VALIDATION_RUN`
- `WRITE_ATTEMPT`
- `WRITE_SUCCESS`
- `WRITE_FAILURE`
- `enforcement_start`
- `enforcement_result`
- `enforcement_error`

## Troubleshooting

### Bypass Detection
Run the bypass scan script to ensure no direct writes exist outside the enforcement gate:

```
./scripts/validation/bypass_scan.sh
```

### Common Issues
- **Missing template**: Ensure the template file exists in `akr_content/templates/`.
- **YAML missing**: Enforcement can auto-generate YAML if `autoFixEnabled=true`.
- **Section order errors**: Ensure section headings match the template H2 headings.

## Testing
Recommended checks:
- E2E enforcement tests: `tests/test_enforcement_e2e.py`
- Full test suite: `pytest tests/ -v --cov=src`
