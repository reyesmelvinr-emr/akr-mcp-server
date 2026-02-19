# System Architecture

This document describes the high-level architecture of AKR-MCP-Server, technology decisions, and how components interact.

## System Overview

AKR-MCP-Server is a documentation automation system that bridges GitHub Copilot with your codebase to generate and maintain architecture documentation.

```
┌─────────────────────────────────────────────────────────┐
│                  GitHub Copilot Chat                     │
│  "Generate docs for PaymentService"                      │
└────────────────────┬────────────────────────────────────┘
                     │ MCP Protocol
                     ▼
┌─────────────────────────────────────────────────────────┐
│              MCP Server (Python)                         │
│  • Handles tool calls (generate, write, update)          │
│  • Routes to appropriate handlers                        │
│  • Manages async I/O with Copilot                        │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌──────────┐
    │Generate│  │ Write  │  │  Update  │
    │  Docs  │  │  Docs  │  │Sections  │
    └─┬──────┘  └───┬────┘  └──────┬───┘
      │             │              │
      ▼             ▼              ▼
      Code        Template      Validation
      Analysis    Rendering     & Enforcement
          │           │              │
          └───────────┼──────────────┘
                      ▼
         ┌──────────────────────────┐
         │  File System & Git       │
         │  • docs/*.md files       │
         │  • enforcement.jsonl log │
         │  • git commits           │
         └──────────────────────────┘
```

## Key Technologies

| Layer | Technology | Why |
|-------|-----------|-----|
| **Protocol** | Model Context Protocol (MCP) | GitHub Copilot official spec for tool integration |
| **Runtime** | Python 3.10+ | Fast development, mature ecosystem |
| **Templating** | Jinja2 | Flexible template engine with custom filters |
| **Data Format** | YAML + Markdown | Human-readable, git-friendly, standard |
| **Parsing** | AST + Regex | C# parsing via Roslyn, TypeScript via TypeScript compiler API, SQL via simple regex |
| **Validation** | Custom schemas | Enforce AKR compliance standards |
| **Telemetry** | JSON Lines | Streaming logs without need for database |
| **Version Control** | Git | Track documentation changes alongside code |

## Architecture Patterns

### 1. Layered Architecture

```
┌───────────────────────────────────┐
│      Presentation Layer           │
│   (GitHub Copilot via MCP)        │
└────────────────┬──────────────────┘
                 │
┌────────────────▼──────────────────┐
│      Application Layer            │
│   • Tool handlers (generate, write)│
│   • Orchestration logic           │
│   • Error handling & response      │
└────────────────┬──────────────────┘
                 │
┌────────────────▼──────────────────┐
│     Business Logic Layer          │
│   • Code analysis                 │
│   • Template rendering            │
│   • Validation & enforcement      │
│   • Telemetry                     │
└────────────────┬──────────────────┘
                 │
┌────────────────▼──────────────────┐
│      Data Access Layer            │
│   • File I/O                      │
│   • Git operations                │
│   • Configuration loading         │
└───────────────────────────────────┘
```

### 2. Plugin Architecture for Code Extractors

The code analysis layer uses plugins to support multiple languages:

```
┌─────────────────────────────────┐
│   Code Analyzer (Dispatcher)     │
└──────────────┬──────────────────┘
               │
      ┌────────┼────────┬──────────┐
      ▼        ▼        ▼          ▼
   ┌──────┐┌──────┐┌──────┐┌──────────┐
   │C#    ││TypeS ││SQL   ││Python    │
   │Parser││Script││Parser││Parser    │
   │      ││Parser││      ││(future)  │
   └───┬──┘└───┬──┘└───┬──┘└────┬─────┘
       │       │       │        │
       └───────┼───────┴────────┘
               │
               ▼
        ┌──────────────┐
        │ Unified Model│
        │ ServiceModel,│
        │ ComponentData│
        │ TableSchema  │
        └──────────────┘
```

Each extractor must implement:
- `extract_services(path)` → List[ServiceEntity]
- `extract_components(path)` → List[ComponentEntity]
- `extract_tables(path)` → List[TableEntity]

### 3. Pipeline Architecture

The documentation generation follows a clear pipeline where each stage validates and enriches the previous:

```
INPUT: User asks Copilot to generate docs
         │
         ▼
    ┌──────────────┐
    │ 1. Extract   │ Parse code, find methods, parameters, types
    │   Code Data  │ Output: ServiceTemplateContext or ComponentTemplateContext
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ 2. Load      │ Read template file (lean_baseline_service.md)
    │ Template     │ Validate schema (required sections defined)
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ 3. Render    │ Jinja2 renders: {{ context.methods }} + ❓ placeholders
    │ Template     │ Apply custom filters (title_case, http_method_color, etc.)
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ 4. Format    │ Add YAML frontmatter, clean markdown
    │ Output       │ Add git metadata
    └──────┬───────┘
           │
           ▼
OUTPUT: Markdown doc with 🤖 + ❓ markers
         Ready for user review in Copilot
```

## Component Responsibilities

### MCP Server (src/server.py)

**Responsibility:** Bridge between GitHub Copilot and documentation tools

**Key Functions:**
- `generate_documentation()` — Creates empty documentation templates
- `write_documentation()` — Writes and validates documentation
- `update_documentation_sections()` — Updates specific sections

**Design decisions:**
- Single-threaded with async/await (handles concurrent Copilot requests)
- Stateless (each request independent, no shared mutable state)
- MCP protocol compliant (works with official Copilot integration)

### Code Analyzer (src/tools/code_analyzer.py)

**Responsibility:** Extract relevant code information from source files

**Key Functions:**
- `populate_template(template, extracted_data, ...)` — Merges code data into template
- `extract_services(path)` — Find service classes and their methods
- `extract_components(path)` — Identify UI components and props
- `extract_tables(path)` — Scan schema for database tables

**Design decisions:**
- Pluggable extractors by language (supports C#, TypeScript, SQL)
- AST-based parsing where available (more reliable than regex)
- Graceful degradation (logs gaps, continues if extraction incomplete)
- No modification of source code (read-only analysis)

### Template Renderer (src/tools/template_renderer.py)

**Responsibility:** Render Jinja2 templates with custom filters

**Key Functions:**
- `render(template_name, context)` — Render template with data
- Custom filters (yes_no, title_case, http_method_color, etc.)

**Design decisions:**
- Singleton pattern (one Jinja2 environment per process)
- Custom filters registered globally (reusable across templates)
- Safe rendering (no arbitrary code execution)

### Enforcement Tool (src/tools/enforcement_tool.py)

**Responsibility:** Validate documentation against AKR standards

**Key Functions:**
- `enforce(doc_content, template, config)` → EnforceResult
- Checks: YAML frontmatter, required sections, section order, completeness

**Design decisions:**
- Hard gate enforcement (blocks unless passes validation)
- Configurable severity levels (BLOCKER, FIXABLE, WARN)
- Actionable error messages with suggested fixes
- Extensible rules system

### Template Schema Builder (src/tools/template_schema_builder.py)

**Responsibility:** Maintain  mapping of templates to required sections

**Key Data:**
```python
TEMPLATE_BASELINE_SECTIONS = {
    "lean_baseline_service_template.md": [
        "Quick Reference (TL;DR)",
        "What & Why",
        # ... 7 more
    ],
    # ... other templates
}
```

**Design decisions:**
- Hardcoded baseline sections (not extracted from files)
- Single source of truth for template requirements
- Easy to version control and peer review changes

## Data Models

### ServiceTemplateContext

```python
@dataclass
class ServiceTemplateContext:
    service_name: str
    namespace: str
    language: str
    dependencies: List[Dependency]
    public_methods: List[MethodSignature]
    business_rules: List[str]                # ❓ to be filled by user
    validation_rules: List[str]              # Auto-extracted
    data_operations: List[DataOperation]     # Auto-extracted
```

### ComponentTemplateContext

```python
@dataclass
class ComponentTemplateContext:
    component_name: str
    component_type: str                      # List, Form, Modal, etc.
    framework: str                           # React, Vue, Angular
    props: List[PropDefinition]              # Auto-extracted from JSDoc
    visual_states: List[str]                 # ❓ to be filled
    accessibility: AccessibilityNotes        # ⚠️ Partial extraction
```

### TableTemplateContext

```python
@dataclass
class TableTemplateContext:
    table_name: str
    database: str
    columns: List[ColumnDefinition]          # Auto-extracted
    primary_key: str
    foreign_keys: List[ForeignKey]           # Auto-extracted
    constraints: List[Constraint]            # Auto-extracted
    business_rules: List[str]                # ❓ to be filled
```

## Data Flow Examples

### Example 1: Generate Service Documentation

```
1. User: "Generate docs for CourseService using lean template"

2. MCP Server
   └─> Call code_analyzer.populate_template()

3. Code Analyzer
   ├─> Extract public methods from CourseService.cs
   ├─> Extract dependencies (constructors)
   ├─> Extract XML doc comments
   └─> Return ServiceTemplateContext

4. Template Renderer  
   ├─> Load service.jinja2
   ├─> Inject ServiceTemplateContext
   ├─> Apply custom filters
   └─> Render markdown

5. Output
   ├─ YAML frontmatter (auto-filled)
   ├─ Quick Reference (🤖 auto-extracted)
   ├─ What & Why (❓ user fills in)
   ├─ How It Works (🤖 auto-extracted)
   ├─ Business Rules (❓ user fills in)
   └─ ... rest of sections

6. Return to Copilot
   └─> User reviews 🤖 sections and fills ❓ placeholders
```

### Example 2: Write and Validate Documentation

```
1. User: "Write this documentation" (filled-in content from step above)

2. MCP Server
   └─> Call enforcement_tool.enforce()

3. Enforcement Tool
   ├─> Check YAML frontmatter valid ✓
   ├─> Check all required sections present ✓
   ├─> Check sections in correct order ✓
   ├─> Check completeness >= 80% ✓
   └─> Return EnforceResult(is_valid=True)

4. File Writer
   ├─> Create docs/CourseService_doc.md
   ├─> Git commit with message
   └─> Log to enforcement.jsonl

5. Return to Copilot
   └─> "✓ Documentation written successfully and committed to git"
```

## Technology Trade-offs

### Decision: Jinja2 vs. String Interpolation

**Chose:** Jinja2 template engine

**Alternatives:**
- String interpolation (simple, but limited)
- Handlebars.js (web-focused)
- Golang text/template (not Python ecosystem)

**Rationale:**
- ✅ Powerful custom filter system
- ✅ Mature, well-tested library
- ✅ Great documentation
- ✅ Handles complex conditionals (❓ optional sections)
- ❌ Learning curve for filter developers

### Decision: YAML + Markdown vs. JSON

**Chose:** YAML frontmatter + Markdown body

**Alternatives:**
- Pure JSON (structured but unreadable)
- XML (verbose)
- HTML (harder to edit)

**Rationale:**
- ✅ Human-readable and editable
- ✅ Git-friendly (diffs make sense)
- ✅ Web-friendly (github renders .md)
- ✅ Language agnostic
- ❌ Some structure loss vs. JSON

### Decision: Schema Validation Approach

**Chose:** Hard gate enforcement (block on failure)

**Alternatives:**
- Soft validation (warnings only)
- Post-commit validation (check after write)

**Rationale:**
- ✅ Prevents incomplete documentation in codebase
- ✅ Catches errors early (before commit)
- ✅ Enables high quality standards
- ❌ Can be frustrating if rules too strict (configurable via enforcement level)

### Decision: Telemetry for Observability

**Chose:** JSON Lines log file (no database)

**Alternatives:**
- Structured logging to ElasticSearch/Splunk
- Database (PostgreSQL)
- File system metrics

**Rationale:**
- ✅ Zero external dependencies
- ✅ Easy to analyze with Python scripts
- ✅ Works offline
- ✅ Version-controllable (can be committed to git)
- ❌ No real-time dashboards (batch analysis only)

---

## Deployment & Scaling

### Single Developer Setup

Local installation on one machine, uses VS Code + GitHub Copilot.

**Performance targets:**
- Documentation generation: 500ms - 1s
- Validation: 50-300ms
- Total: 1-2s per operation

### Team Setup

Shared MCP server serving multiple developers via VS Code extensions.

**Considerations:**
- Async request handling (supports concurrent Copilot chats)
- Rate limiting (optional, if needed)
- Telemetry aggregation to shared logs
- Git repo accessible to all team members

### Enterprise Setup

Multiple MCP servers across teams, potentially different codebases.

**Considerations:**
- Separate `mcp.json` per codebase
- Separate documentation roots per team
- Aggregated telemetry dashboards
- Read-only extractors (no prod code changes)

---

## Future Enhancements

### Planned Improvements

1. **Language Support**
   - Add Python, Java, Go extractors
   - Support additional templates (Java service, Python utility, etc.)

2. **Advanced Analysis**
   - Dependency graph visualization
   - API surface analysis (not just method names but behavior)
   - Performance metrics extraction

3. **Collaboration Features**
   - Documentation review workflow
   - Comments and suggestions in docs
   - Team consensus tracking

4. **Tooling Integration**
   - Swagger/OpenAPI sync
   - Figma design tokens extraction
   - Storybook integration

---

## Architecture Diagrams

### Component Interaction Diagram

```
┌──────────────────────┐
│ GitHub Copilot Chat  │
│  (User Interface)    │
└──────────────┬───────┘
               │ MCP requests
               ▼
┌──────────────────────────────────────────┐
│           MCP Server                     │
│  ┌────────────────────────────────────┐  │
│  │ Tool Handlers:                     │  │
│  │ • generate_documentation           │  │
│  │ • write_documentation              │  │
│  │ • update_documentation_sections    │  │
│  └────────────────────────────────────┘  │
└──────────┬───────────────┬───────────┬───┘
           │               │           │
           ▼               ▼           ▼
    ┌────────────┐  ┌─────────────┐ ┌──────────────┐
    │Code        │  │Template     │ │Enforcement  │
    │Analyzer    │  │Renderer     │ │Tool         │
    │            │  │(Jinja2)     │ │             │
    │• C# parser │  │•Filters     │ │•Validation  │
    │• TS parser │  │•Contexts    │ │•Rules       │
    │• SQL parser│  │•Rendering   │ │             │
    └────┬───────┘  └──────┬──────┘ └──────┬──────┘
         │                 │               │
         └─────────────────┼───────────────┘
                           │
                           ▼
                    ┌────────────────┐
                    │File System +   │
                    │Git Operations  │
                    │                │
                    │✓ Docs written  │
                    │✓ Commits made  │
                    │✓ Telemetry log │
                    └────────────────┘
```

### Enforcement Gate Sequence

```
User submits documentation
          │
          ▼
    Validate YAML
    ├─ Required fields present?
    ├─ Frontmatter format valid?
    └─ Parse successful?
          │
          ▼ ✓ Pass
    Check Required Sections
    ├─ All sections present?
    ├─ Content not empty?
    └─ No ❓ placeholders remaining?
          │
          ▼ ✓ Pass
    Verify Section Order
    ├─ Matches template order?
    └─ No sections out of place?
          │
          ▼ ✓ Pass
    Check Link Validity
    └─ Cross-references exist?
          │
          ▼ ✓ Pass
    Measure Completeness
    └─ >= configured threshold?
          │
          ▼ ✓ Pass
    ┌─────────────────┐
    │ WRITE TO DISK   │
    │ GIT COMMIT      │
    │ LOG SUCCESS     │
    └─────────────────┘
```

---

## Getting Help

- **How to use?** → See [Workflows by Project Type](WORKFLOWS_BY_PROJECT_TYPE.md)
- **Implementation details?** → See [Developer Reference](DEVELOPER_REFERENCE.md)
- **Setup?** → See [Installation and Setup](INSTALLATION_AND_SETUP.md)
- **Quick answers?** → See [Quick Reference](QUICK_REFERENCE.md)
