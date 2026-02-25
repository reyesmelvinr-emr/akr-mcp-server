# Changelog

All notable changes to the AKR MCP Server are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] — 2026-02-24

### Added

#### Phase 1: Template Externalization & MCP Resources
- **Git submodule integration**: Core AKR templates now externalized to `core-akr-templates` repository
  - Submodule pinned to release tags for reproducible, stable template versions
  - Three-layer template resolution: submodule → local overrides → optional HTTP preview
  - Secure HTTP fetch with hash verification, trusted hosts, and TTL caching
- **MCP Resource handlers**: Templates and charters now discoverable as MCP resources
  - `@server.list_resources()`: List all available templates
  - `@server.read_resource(uri)`: Read specific template by URI (e.g., `akr://template/lean_baseline_service_template`)
  - `@server.list_resource_templates()`: Expose resource templates for dynamic URI construction
  - All resources return proper MIME types (`text/markdown`)
- **Documentation**:
  - [INSTALLATION_AND_SETUP.md](INSTALLATION_AND_SETUP.md): Cross-OS submodule setup guide
  - [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md): Template update workflow and version management
  - Updated [README.md](README.md) with resource discovery section

#### Phase 2: Write Operations Gating
- **Security model**: Write operations disabled by default
  - Environment flag: `AKR_ENABLE_WRITE_OPS` (default: `false`)
  - Conditional tool registration: Write tools only registered when flag is enabled
  - Per-call confirmation: `allowWrites: bool` parameter (default: `false`)
  - Two-layer gating prevents accidental modifications without explicit action
- **Documentation**:
  - [SECURITY.md](SECURITY.md): Trust model, MCP Inspector versions, identity roadmap
  - Updated [README.md](README.md) with "Write Operations (Disabled by Default)" section
  - [ARCHITECTURE.md](ARCHITECTURE.md) updated with security considerations

#### Phase 3: Dual-Faceted Validation
- **Validation engine** (`src/tools/validation_library.py`):
  - Core validation shared by MPC tool and CLI
  - YAML frontmatter validation using JSON Schema (per template manifest)
  - Section presence and order enforcement (configurable by tier)
  - Completeness calculation using word count + table/list heuristics
  - Auto-fix capability: generates patches for missing sections, YAML, reordering
  - Tier-based validation (strict/moderate/lenient):
    - `TIER_1`: ≥80% completeness, BLOCKER severity for violations
    - `TIER_2`: ≥60% completeness, FIXABLE severity (default)
    - `TIER_3`: ≥30% completeness, WARN severity
- **MCP tool**: `validate_documentation`
  - Input: `doc_path, template_id, tier_level, auto_fix, dry_run`
  - Output: JSON with violations, completeness %, suggestions, optional patched content
  - Default: `dry_run=true` (returns diff without writing to file)
- **CLI tool**: `scripts/akr_validate.py`
  - Local validation with JSON and text output formats
  - Exit codes: 0 (valid), 1 (invalid), 2 (arg error), 3 (file error), 4 (engine error)
  - Useful for CI/CD integration
- **Dependencies**: Added `jsonschema>=4.0.0` for JSON Schema validation
- **Documentation**:
  - [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md): Comprehensive validation usage guide
  - Tier-level explanations, auto-fix capabilities, CI/CD integration examples

#### Phase 4: Extractor Deprecation & Code Analytics
- **CodeAnalyzer** (`src/tools/code_analytics.py`):
  - Unified interface for deterministic code extraction
  - Composes `CSharpExtractor` and `SQLExtractor`
  - Methods:
    - `detect_language(file_path)`: Detect language from file extension
    - `extract_methods(file_path)`: Extract public/private methods
    - `extract_classes(file_path)`: Extract class/interface definitions
    - `extract_imports(file_path)`: Extract external dependencies
    - `extract_sql_tables(file_path)`: Extract SQL table schema
    - `analyze(file_path, extraction_types)`: Unified analysis entry point
- **MCP tool**: `extract_code_context` (replaces `analyze_codebase`)
  - Input: `repo_path, extraction_types, language, file_filter`
  - Output: JSON with methods, classes, imports, SQL tables, metadata
  - Deterministic: Uses only proven extractors (C#, SQL)

### Changed

- **Tool naming**: `analyze_codebase` → `extract_code_context`
  - New tool provides clearer semantics and deterministic guarantees
  - Old placeholder tool removed from tool list
- **Template resolution**: Now uses Git submodule as primary source
  - Local template copies in `akr_content/templates/` removed
  - Built on externalized `core-akr-templates` for single source of truth
- **Documentation**:
  - [ARCHITECTURE.md](ARCHITECTURE.md): Major update reflecting v0.2.0 design shift
    - Now a template/charter resource provider + validator (not a doc generator)
    - Component dependency diagrams (MCP resources, tools, validators)
    - Data flow: extract → charter → validate → write
  - [README.md](README.md): Simplified tool list with status indicators

### Deprecated

The following extractors **use heuristic-based regex patterns** and are inaccurate. Use Copilot Chat with code context instead.

**DEPRECATED EXTRACTORS** (Removal target: **v1.0.0**):
1. **TypeScript Extractor** (`src/tools/extractors/typescript_extractor.py`)
   - Migration: Copy React component code to Copilot Chat + reference UI charter
   
2. **Business Rule Extractor** (`src/tools/extractors/business_rule_extractor.py`)
   - Migration: Ask Copilot Chat to identify rules from code + backend charter
   
3. **Failure Mode Extractor** (`src/tools/extractors/failure_mode_extractor.py`)
   - Migration: Ask Copilot Chat to identify failure modes + reference backend charter
   
4. **Method Flow Analyzer** (`src/tools/extractors/method_flow_analyzer.py`)
   - Migration: Ask Copilot Chat to generate operation flows from method code
   
5. **Example Extractor** (`src/tools/extractors/example_extractor.py`)
   - Migration: Ask Copilot Chat to generate realistic JSON examples from DTOs

**Deprecation notice**: All deprecated extractors include clear warnings in their docstrings with migration guidance.

### Removed

- Placeholder tool descriptions: Old guidance text removed
- Local template duplicates: All templates in `akr_content/templates/` removed
  - Reason: Now sourced from Git submodule (`templates/core/`)

### Fixed

- **Schema dependency wiring**: `ValidationEngine` now correctly depends on `TemplateSchemaBuilder`
  - Previously: `ValidationEngine → TemplateResolver` (incorrect direction)
  - Now: `ValidationEngine → TemplateSchemaBuilder → TemplateResolver` (correct)
- **MCP resource handlers**: Confirmed to use official MCP Python SDK types
  - Resource handlers return proper `mimeType`, `uri`, `text` fields
  - Resource templates support dynamic URI construction
- **Cross-platform documentation**: All paths use repo-relative format
  - Removed Windows-specific OneDrive paths
  - All setup guides work on macOS, Linux, Windows

### Security

- **Write operations**: Off by default with two-layer gating
  - Environment flag: `AKR_ENABLE_WRITE_OPS=false`
  - Per-call confirmation: `allowWrites: bool` parameter
  - Clear error messages guide users on how to enable when needed
- **HTTP fetch** (if enabled): Hardened against TOCTOU and injection attacks
  - Trusted host whitelist
  - SHA-256 hash verification
  - TTL-based caching
  - Pinned version in config
- **MCP Inspector**: Requires v0.14.1+ for CVE fix (documented in [SECURITY.md](SECURITY.md))

### Documentation Updates

**New Files:**
- [CHANGELOG.md](CHANGELOG.md) — This file
- [SECURITY.md](SECURITY.md) — Trust model, MCP compliance, identity roadmap
- [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) — Submodule workflow
- [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) — Validation usage guide

**Updated Files:**
- [README.md](README.md) → Tool list, write-ops section, submodule note, security callout
- [ARCHITECTURE.md](ARCHITECTURE.md) → v0.2.0 design, MCP resources, data flow
- [INSTALLATION_AND_SETUP.md](INSTALLATION_AND_SETUP.md) → Cross-OS submodule setup
- [requirements.txt](../requirements.txt) → Added `jsonschema>=4.0.0`

---

## [0.1.0] — Initial Release

- Initial implementation with placeholder tools
- Basic MCP server structure
- Foundational extractors (TypeScript, C#, SQL, etc.)

---

## Migration Guide

### From v0.1.0 → v0.2.0

#### Using Deprecated Extractors

**Old way** (v0.1.0):
```
analyze_codebase(codebase_path="src/", file_types=[".ts", ".tsx"])
```

**New way** (v0.2.0):
```
extract_code_context(repo_path="src/foo.ts", extraction_types=["methods", "classes"])
```

**For semantic analysis** (recommended):
1. Copy code into Copilot Chat
2. Paste relevant charter (e.g., `akr://charter/ui`)
3. Ask: "Identify key components and generate documentation"

#### Template Access

**Old way** (v0.1.0):
- Templates in `akr_content/templates/` (local copies)

**New way** (v0.2.0):
- Templates in `templates/core/` (Git submodule)
- Accessible via MCP: `akr://template/{id}`
- Updated automatically via: `git submodule update --remote`

#### Write Operations

**Old way** (v0.1.0):
- Write tools always available

**New way** (v0.2.0):
```bash
# Enable write operations (off by default)
export AKR_ENABLE_WRITE_OPS=true

# Even when enabled, per-call confirmation required
write_documentation(..., allowWrites=true)
```

---

## Known Limitations

- **Heuristic extractors**: TypeScript, Business Rule, Failure Mode, Method Flow, Example extractors use regex patterns and are often inaccurate
  - Planned removal: v1.0.0
  - Recommendation: Use Copilot Chat for semantic analysis

- **Markdown parser**: v0.2.0 uses regex-based heading walk
  - Planned upgrade: markdown-it-py AST parser (v0.3.0)
  - Known edge cases: Nested subsections, complex formatting

- **Identity/team gating**: Not implemented in v0.2.0
  - Planned: v0.3.0 (Git author email or JWT token)
  - Current model: Environment flag + per-call confirmation sufficient for MVP

---

## Upgrade Instructions

### Git Submodule Setup

After updating to v0.2.0:

```bash
# Initialize submodule
git submodule update --init --recursive

# Verify submodule is present
git submodule foreach git log -1 --oneline
```

### Environment Setup

```bash
# Install new dependencies
pip install -r requirements.txt

# Verify validation library
python -m pytest tests/test_validation_library.py -v

# Run CLI validation tool
python scripts/akr_validate.py --help
```

### Update Copilot Chat Workflows

Replace references to `analyze_codebase` with `extract_code_context` in custom prompts/workflows.

---

## Contributors

- Melvin Reyes (@reyesmelvinr-emr)
- AKR Core Team

---

## License

See LICENSE in the repository root for details.

---

**Next Release**: v0.3.0 planned for May 2026 with:
- AST-based Markdown parser (markdown-it-py)
- Team-based identity model (Git author / JWT token)
- Enhanced error recovery and suggestions
- Performance optimizations (caching layer)
