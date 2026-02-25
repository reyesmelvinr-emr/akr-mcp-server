# AKR MCP Server v0.2.0 - Architecture

## Overview

The AKR MCP Server is a **design-centric documentation generator** that integrates with Copilot Chat to create technical charters, architecture documents, and compliance records. Rather than automatically generating documentation, it acts as an intelligent **template provider and validation engine**, enabling developers to leverage AI-assisted drafting with structured guidance.

### v0.2.0 Design Shift

**Old Model (v0.1.0):** Automatic analysis → heuristic extraction → document generation  
**New Model (v0.2.0):** Code context extraction → human/Chat review → structured validation → write on demand

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Copilot Chat Interface                   │
│         (Browser-based with integrated MCP resources)       │
└────────────┬──────────────────────────────────────┬─────────┘
             │                                      │
    ┌────────▼─────────────┐             ┌─────────▼──────────┐
    │ MCP Resources Layer  │             │  MCP Tools Layer   │
    │                      │             │                    │
    │ - list_resources()   │             │ - extract_code_... │
    │ - read_resource()    │             │ - get_charter()    │
    │ - list_resource_...  │             │ - validate_doc...  │
    │                      │             │ - write_document() │
    └─────────┬────────────┘             └─────────┬──────────┘
              │                                    │
    ┌─────────▼──────────────────────────────────▼────────────┐
    │              AKR Server Core (FastMCP)                  │
    └────┬────────────────┬──────────────────┬────────────────┘
         │                │                  │
    ┌────▼─────────────┐  │   ┌─────────────▼────────────┐
    │ Core Modules:    │  │   │  Tool Implementations:   │
    │ - Config         │  │   │  - CodeAnalyzer         │
    │ - Logging        │  │   │  - TemplateResolver     │
    │ - Schema Builder │  │   │  - ValidationEngine     │
    │ - Document       │  │   │  - Write Operations     │
    │   Parser         │  │   │  - Enforcement Logger   │
    └────────────┬─────┘  │   └──────────┬──────────────┘
                 │        │              │
                 │  ┌─────▼──────────────▼──────────┐
                 │  │  Business Logic Layer:        │
                 │  │  - Template + Charter loading │
                 │  │  - Code extraction (C#, SQL)  │
                 │  │  - Schema/tier validation     │
                 │  │  - Document writing           │
                 │  │  - Audit trail + security     │
                 │  └─────┬────────────┬──────────────┘
                 │        │            │
          ┌──────▼────┐  ┌▼──────────┐ │
          │ Git       │  │ HTTP      │ │
          │ Submodule │  │ Templates │ │
          │ (Primary  │  │ (Optional │ │
          │ Templates)│  │ Preview)  │ │
          └───────────┘  └───────────┘ │
                                       │
                         ┌─────────────▼──────────────┐
                         │  File System Layer:        │
                         │  - Docs/ directory         │
                         │  - Local file I/O          │
                         │  - Path resolution         │
                         └────────────────────────────┘
```

## Layer Architecture

### 1. MCP Interface Layer

**Purpose:** Expose functionality to Copilot Chat as standardized MCP resources and tools.

**Components:**

- **Resources (async discovery)**
  - `list_resources()`: Enumerate available templates and charters
  - `read_resource(uri)`: Fetch specific template/charter content
  - `list_resource_templates()`: List URI patterns for dynamic resource construction
  - URI Format: `akr://template/{id}`, `akr://charter/{domain}`
  - MIME Type: `text/markdown` (all resources are Markdown documents)

- **Tools (action-oriented)**
  - `extract_code_context()`: Deterministic code extraction (C# and SQL only)
  - `get_charter()`: Retrieve a charter document for a documentation domain
  - `validate_documentation()`: Validate documents against schema tiers (TIER_1/2/3)
  - `generate_documentation()`: Create template-compliant stubs with human placeholders
  - `generate_and_write_documentation()`: Unified scaffold + validate + write flow
  - `write_documentation()`: Write validated documents to disk with audit trail
  - `update_documentation_sections()`: Targeted section updates with enforcement

### 2. Core Business Logic Layer

**Purpose:** Implement the core algorithms and workflows for documentation generation and validation.

**Components:**

#### Code Extraction
- **`CodeAnalyzer`** (src/tools/code_analytics.py)
  - Deterministic extraction for C# and SQL only
  - Methods: `detect_language()`, `extract_methods()`, `extract_classes()`, `extract_imports()`, `extract_sql_tables()`, `analyze()`
  - Returns: Clean JSON with extracted symbols, types, relationships
  - Error Handling: Graceful degradation with 'partial' flag on failures
  - Version: v0.2.0+ (deprecated heuristic extractors in v0.1.0)

#### Template Management
- **`TemplateResolver`** (src/resources/template_resolver.py)
  - Three-layer resolution strategy:
    1. Git submodule (pinned tags for consistency)
    2. Local file overrides (project-specific customization)
    3. HTTP fetch (cloud templates with fallback)
  - Schema Caching: Compiled JSONSchema cached for performance
  - Security: URL validation, timeout limits, no automatic execution

#### Validation
- **`ValidationEngine`** (src/tools/validation_library.py)
  - Tier-based strictness levels:
    - **TIER_1**: Strict validation, ≥80% completeness, BLOCKER for structural issues
    - **TIER_2**: Moderate validation, ≥60% completeness, FIXABLE issues
    - **TIER_3**: Lenient validation, ≥30% completeness, informational only
  - Schema: JSON Schema for front-matter validation
  - Auto-Fix: Capable of suggesting and applying common fixes
  - Dry-Run Mode: Default behavior, shows changes without writing
  - Output: Structured result with errors, warnings, auto-fixes, diffs

#### Document Writing
- **`write_documentation` + `update_documentation_sections`** (src/tools/write_operations.py)
  - Enforced write operations with validation pre-checks
  - Audit Trail: Detailed logging of all write operations
  - Permission Gating: Two-layer write protection (env flag + allow flag)
  - Safety: Write tools are registered only when write ops are enabled

#### Security & Audit
- **`EnforcementLogger`** (src/tools/enforcement_logger.py)
  - Write operation tracking (JSONL audit log)
  - Operation metadata: timestamp, user, file, operation, status
  - Compliance tracking: Enables SoC2/audit trail requirements
  - Configurable: Adjustable detail levels and filtering

## Data Flow Sequences

### Extract → Charter → Validate → Write Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│ User initiates from Copilot Chat:                                       │
│ "Generate a charter for my AuthService.cs"                              │
└──────────────┬──────────────────────────────────────────────────────────┘
               │
        ┌──────▼────────────────────────────────────────┐
        │ 1. Extract Code Context                        │
        │    Tool: extract_code_context()                │
        │    Input: file_path, extraction_types          │
        │    Output: {methods, classes, imports, ...}     │
        └──────┬────────────────────────────────────────┘
               │
        ┌──────▼──────────────────────────────────────────┐
        │ 2. User Reviews + Chat Drafting                 │
        │    Location: Copilot Chat browser interface     │
        │    Action: Review extracted context             │
        │    Action: Ask Chat to draft charter            │
        │    Output: Drafted markdown document            │
        └──────┬───────────────────────────────────────────┘
               │
        ┌──────▼─────────────────────────────────────────┐
        │ 3. Validate Documentation                       │
        │    Tool: validate_documentation()               │
        │    Input: doc_path, tier, template_id           │
        │    Checking: Schema compliance, completeness    │
        │    Output: Errors, warnings, suggested fixes    │
        └──────┬────────────────────────────────────────┘
               │
        ┌──────▼──────────────────────────────────────────┐
        │ 4. User Refinement (if needed)                  │
        │    Location: Copilot Chat                       │
        │    Action: Ask Chat to fix validation issues    │
        │    Action: Manual editing if necessary          │
        │    Output: Refined document                     │
        └──────┬───────────────────────────────────────────┘
               │
        ┌──────▼──────────────────────────────────────────┐
        │ 5. Write to Repository                          │
        │    Tool: write_documentation()                  │
        │    Input: content, source_file, doc_path         │
        │    Checks: Final schema validation              │
        │    Audit: Logs to enforcement.jsonl             │
        │    Output: {success, file_path, metadata}       │
        └──────┬───────────────────────────────────────────┘
               │
        ┌──────▼──────────────────────────────────────┐
        │ Document written to disk                     │
        │ Path: /docs/{domain}/{component}_charter.md │
        │ Audit Trail: Recorded with timestamp + user │
        └─────────────────────────────────────────────┘
```

## Component Dependencies

```
CodeAnalyzer (Phase 4)
  ├── CSharpExtractor (Phase 4)
  └── SQLExtractor (Phase 4)

ValidationEngine (Phase 3)
  ├── BasicDocumentParser
  ├── TemplateSchemaBuilder
  └── EnforcedViolation types

WriteOperations (Phase 2)
  ├── EnforcementLogger
  ├── EnforcedViolation handling
  └── Path resolution

MCP Server
  ├── All tools above
  ├── TemplateResolver
  └── FastMCP decorators
```

## API Reference

### MCP Resources

#### `list_resources()`
Lists all discoverable resources (templates and charters).

**Response:**
```json
[
  {
    "uri": "akr://template/lean_baseline_service_template",
    "name": "Template: lean_baseline_service_template",
    "mimeType": "text/markdown"
  },
  {
    "uri": "akr://charter/backend",
    "name": "Charter: backend",
    "mimeType": "text/markdown"
  }
]
```

#### `read_resource(uri)`
Retrieves the content of a specific resource.

**Parameters:**
- `uri` (string): Resource URI, e.g., `akr://template/lean_baseline_service_template`

**Response:**
- Markdown content as plain text

#### `list_resource_templates()`
Lists URI patterns for dynamic resource construction.

**Response:**
```json
[
  {
    "uriTemplate": "akr://template/{id}",
    "name": "AKR Documentation Templates"
  },
  {
    "uriTemplate": "akr://charter/{domain}",
    "name": "AKR Charters"
  }
]
```

### MCP Tools

#### `extract_code_context(repo_path, extraction_types?, language?, file_filter?)`

Extracts code context from files using deterministic (C#, SQL) methods.

**Parameters:**
- `repo_path` (required): Repository or file path
- `extraction_types` (optional): Array of ["methods", "classes", "imports", "sql_tables"]
- `language` (optional): Force language detection ("csharp" or "sql")
- `file_filter` (optional): Glob pattern for file filtering

**Response:**
```json
{
  "language_detected": "csharp",
  "methods": [...],
  "classes": [...],
  "imports": [...],
  "metadata": {
    "language_detected": "csharp",
    "extractor_version": "0.2.0",
    "extraction_errors": [],
    "partial": false
  }
}
```

#### `validate_documentation(doc_path, template_id, tier_level?, auto_fix?, dry_run?)`

Validates a document against a schema template.

**Parameters:**
- `doc_path` (required): Documentation file path to validate
- `template_id` (required): Template identifier (e.g., "lean_baseline_service_template")
- `tier_level` (optional): "TIER_1" (strict), "TIER_2" (moderate), "TIER_3" (lenient). Default: TIER_2
- `auto_fix` (optional): Boolean, attempt to auto-fix violations. Default: false
- `dry_run` (optional): Boolean, don't write changes. Default: true

**Response:**
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [],
  "auto_fixed_content": null,
  "diff": null,
  "metadata": {
    "tier_level": "TIER_1",
    "template_id": "lean_baseline_service_template",
    "completeness_percent": 95
  }
}
```

#### `write_documentation(content, source_file, doc_path, template?, component_type?, overwrite?, force_workflow_bypass?, allowWrites?)`

Writes validated documentation to disk.

**Parameters:**
- `content` (required): Markdown content to write
- `source_file` (required): Repo-relative source file path
- `doc_path` (required): Repo-relative output doc path
- `template` (optional): Template filename or shortcut
- `component_type` (optional): Component type, e.g. service, controller
- `overwrite` (optional): Whether to overwrite existing file (default: false)
- `force_workflow_bypass` (optional): Allow direct write for new files without generate_documentation (default: false)
- `allowWrites` (optional): Must be true to allow file writes

**Response:**
```json
{
  "success": true,
  "file_path": "/docs/services/auth_charter.md",
  "bytes_written": 2847,
  "metadata": {
    "timestamp": "2024-01-15T10:35:00Z",
    "audit_id": "write_abc123def456"
  }
}
```

## Security Architecture

### Write Operation Gating
1. **Environment Control**: `AKR_ENABLE_WRITE_OPS` env var (default: false)
2. **Parameter Control**: `allowWrites` parameter in API calls
3. **User Tracking**: All writes logged with timestamp and user identity (if available)

### Template Security
- URL validation: Only HTTPS URLs accepted (if `HTTPS_REQUIRED_FOR_TEMPLATES=true`)
- Timeout limits: 5-second timeout on HTTP fetches
- Size limits: Max 1MB template fetch size
- No automatic code execution: Templates are static Markdown/YAML

### Audit Trail
- Every write operation logged to `enforcement.jsonl`
- Fields: timestamp, user_id, file_path, operation, status, error (if any)
- Query: Enables compliance reporting and forensic analysis

## Testing & Quality

### Test Coverage
- Phase 1 tests: 14 test cases (template resolution, schema building)
- Phase 2 tests: 8 test cases (write operations, enforcement)
- Phase 3 tests: 32 test cases (validation library)
- Phase 4 tests: 22 test cases (code extraction)
- Phase 5 tests: 18 test cases (e2e workflow, resources, integration)

### Total: 94 test cases, target coverage ≥80%

### Test Execution
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific module
pytest tests/test_extract_code_context.py -v
```

## v0.3.0 Roadmap

### Parser Improvements
- AST-based extraction replacing regex (more accurate, handles edge cases)
- Support for additional languages: Python, Java, Go, Rust
- Improved error recovery and partial extraction

### Team Identity Support
- Microsoft Entra ID integration for write operation tracking
- Group-based permissions (e.g., "architects" can modify charters)
- Approval workflow integration (TIER_1 changes require review)

### Performance Optimization
- Parallel multi-file extraction
- Distributed validation engine
- Caching of extracted symbols

## References

- [MCP Specification](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [JSON Schema Validation](https://json-schema.org)
- [AKR Validation Guide](./VALIDATION_GUIDE.md)
- [Developer Guide](./DEVELOPER_GUIDE_ENFORCEMENT.md)
- [Copilot Chat Workflow](./COPILOT_CHAT_WORKFLOW.md)
