# Developer Reference

This document is for developers extending, maintaining, or troubleshooting the AKR-MCP-Server system. It covers architecture, APIs, telemetry, and integration points.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Enforcement Architecture](#enforcement-architecture)
3. [Template System & Jinja2](#template-system--jinja2)
4. [Code Integration Points](#code-integration-points)
5. [Telemetry & Monitoring](#telemetry--monitoring)
6. [Troubleshooting](#troubleshooting)

---

## System Architecture

### High-Level Overview

```
GitHub Copilot
      ↑
      ↓ (MCP Protocol)
   MCP Server (src/server.py)
      ↓
   Tool Handlers
   ├── generate_documentation
   ├── write_documentation
   └── update_documentation_sections
      ↓
   Processing Pipeline
   ├── code_analyzer.py         (Code extraction)
   ├── template_renderer.py     (Jinja2 rendering)
   ├── enforcement_tool.py      (Validation)
   └── template_schema_builder.py (Schema management)
      ↓
   File System & Git
   (Documentation files + enforcement.jsonl telemetry)
```

### Data Flow: Doc Generation

**Scenario: User asks Copilot to generate service documentation**

```
1. Copilot sends: generate_documentation(
     component_name="PaymentService",
     template="lean_baseline_service_template.md"
   )

2. MCP Server routes to tool handler

3. Code Analyzer extracts from codebase:
   - Public methods and signatures
   - Dependencies (constructors, fields)
   - Return types and parameters
   - XML documentation comments
   → ServiceTemplateContext filled with 🤖 data

4. Template Schema Builder loads template:
   - lean_baseline_service_template.md
   - Identifies required sections (9 baseline sections)
   - Validates schema definition

5. Template Renderer (Jinja2):
   - Loads template from templates/service.jinja2
   - Injects ServiceTemplateContext
   - Applies custom filters (yes_no, required_nullable, etc.)
   - Renders sections with auto-populated data + ❓ placeholders
   → Raw markdown output

6. Return to Copilot:
   - Markdown content with 🤖 markers for extracted parts
   - ❓ placeholders for manual input sections
   - YAML frontmatter with metadata
```

### Data Flow: Doc Writing & Validation

**Scenario: User asks Copilot to write documentation**

```
1. Copilot sends: write_documentation(
     doc_path="docs/services/PaymentService_doc.md",
     content="<filled-in markdown>"
   )

2. MCP Server routes to tool handler

3. Enforcement Tool validates:
   - YAML frontmatter check (all required fields present)
   - Section order verification (matches template order)
   - Section completeness check (no empty required sections)
   - Link validation (no broken references)
   - Severity assessment (BLOCKER/FIXABLE/WARN)
   → EnforceResult returned

4. If validation passes:
   - Git commit documentation + enforcement.jsonl log entry
   - Return success with metrics

5. If validation fails:
   - Return detailed error with:
     * Violated rules
     * Suggested fixes
     * Documentation references
   - NO file written to disk
```

---

## Enforcement Architecture

### Validation Flow (Hard Gate Pattern)

The enforcement system uses a "hard gate" pattern: documentation must pass validation before being written to disk.

```
                    write_documentation call
                            ↓
                    ┌──────────────────┐
                    │ Enforcement Gate │
                    └────────┬─────────┘
                             ↓
           ┌─────────────────────────────────────┐
           │ Run Validations (in order):         │
           │ 1. YAML frontmatter exists?         │
           │ 2. All required sections present?   │
           │ 3. Sections in correct order?       │
           │ 4. Section content not empty?       │
           │ 5. Links point to real files?       │
           │ 6. Completeness >= threshold?       │
           └─────────────────────────────────────┘
                             ↓
           ┌─────────────────┴──────────────────┐
           ↓                                    ↓
      ✅ ALL PASS                      ❌ ANY FAIL
           ↓                                    ↓
    Write to disk               Return error + guidance
    + Log success               + Log violation
    + Git commit                + Suggest fixes
```

### Validation Severity Levels

Each rule has a severity that determines whether it blocks the write:

| Level | Behavior | Example |
|-------|----------|---------|
| **BLOCKER** | Prevents write | Missing required sections |
| **FIXABLE** | Prevents write but auto-fixable | Section out of order |
| **WARN** | Logs warning, write allowed | Link may be broken |

### Template Baseline Sections

Each template defines which sections are required. The schema builder maintains this mapping:

**lean_baseline_service_template.md (9 required sections):**
1. Quick Reference (TL;DR)
2. What & Why
3. How It Works
4. Business Rules
5. Architecture
6. API Contract (AI Context)
7. Validation Rules (AUTO-GENERATED)
8. Data Operations
9. Questions & Gaps

**comprehensive_service_template.md (21 required sections):**
1. 🚨 Critical Service Alert
2. Quick Reference (TL;DR)
3. What & Why
4. How It Works
5. Business Rules
6. Architecture
7. API Contract (AI Context)
8. Middleware Pipeline
9. Validation Rules (Comprehensive)
10. Data Operations
11. External Dependencies (Mission-Critical)
12. Known Issues & Limitations
13. Performance
14. Common Problems & Solutions
15. What Could Break (Impact Analysis)
16. Security & Compliance
17. Disaster Recovery
18. Monitoring & Alerts
19. Testing Strategy
20. Deployment
21. Incident Response
22. Team & Ownership

**ui_component_template.md (16 required sections):**
1. Quick Reference
2. Purpose & Context
3. Props API
4. Visual States & Variants
5. Component Behavior
6. Styling & Theming
7. Accessibility
8. Usage Examples
9. Component Architecture
10. Data Flow
11. Performance Considerations
12. Error Handling
13. Testing
14. Known Issues & Limitations
15. Migration Guide
16. Questions & Gaps

**table_doc_template.md (6 required sections):**
1. Purpose
2. Columns
3. Constraints
4. Business Rules
5. Related Objects
6. Optional Sections

### Configuration Options

Enforcement can be configured via `mcp.json`:

```json
{
  "validation": {
    "enforce_completeness": 80,           // Require 80%+ fields populated
    "require_examples": true,             // examples section mandatory
    "require_error_cases": true,          // error handling examples required
    "allow_empty_sections": false,        // required sections must have content
    "severity": "standard",               // standard | lenient | strict
  }
}
```

---

## Template System & Jinja2

### Custom Filters

All custom filters are implemented in `src/tools/template_renderer.py`. Here's the complete API:

#### Filter: yes_no

Converts boolean to Yes/No string.

**Usage:**
```jinja2
{{ component.has_accessibility | yes_no }}
```

**Output:**
- Input: `True` → Output: "Yes"
- Input: `False` → Output: "No"
- Input: `None` → Output: "Unknown"

#### Filter: required_nullable

Formats required vs optional field indicator.

**Usage:**
```jinja2
{{ field.name }}: {{ field.type }} [{{ field.is_required | required_nullable }}]
```

**Output:**
- Input: `True` → Output: "Required"
- Input: `False` → Output: "Optional"

#### Filter: title_case

Converts string to Title Case.

**Usage:**
```jinja2
{{ 'payment service' | title_case }}
```

**Output:** "Payment Service"

#### Filter: http_method_color

Assigns color/badge to HTTP method for documentation.

**Usage:**
```jinja2
{{ 'GET' | http_method_color }}
```

**Output:**
- GET → `🟢 GET` (green)
- POST → `🔵 POST` (blue)
- PUT → `🟠 PUT` (orange)
- DELETE → `🔴 DELETE` (red)
- PATCH → `🟡 PATCH` (yellow)

#### Filter: join_list

Joins list items with flexible formatting.

**Usage:**
```jinja2
{{ dependencies | join_list(separator=", ", prefix="- ", suffix="") }}
```

**Output:**
```
- Dependency1
- Dependency2  
- Dependency3
```

#### Filter: code_block

Wraps text in code block with language specification.

**Usage:**
```jinja2
{{ sample_code | code_block(language="csharp") }}
```

**Output:**
````markdown
```csharp
// Your code here
```
````

#### Filter: truncate_smart

Intelligently truncates long text at word boundary.

**Usage:**
```jinja2
{{ long_description | truncate_smart(max_length=100) }}
```

**Output:** Text truncated at nearest word boundary with "..."

#### Filter: default_if_empty

Provides default text if field is empty.

**Usage:**
```jinja2
{{ optional_field | default_if_empty("Not provided") }}
```

**Output:** Field value or "Not provided" if empty

### Template Inheritance

Templates use Jinja2's inheritance system:

**Base template (templates/base.jinja2):**
```jinja2
---
title: {{ name }}
type: {{ component_type }}
---

# {{ name }}

{{ description }}

## Architecture
{% block architecture %}
Override in child template
{% endblock %}
```

**Service template (templates/service.jinja2):**
```jinja2
{% extends "base.jinja2" %}

{% block architecture %}
Service follows layered architecture:
- {{ service_name }} (business logic)
- {{ dependencies | length }} dependencies
{% endblock %}
```

### Adding a New Custom Filter

To add a new Jinja2 custom filter:

**1. Implement in src/tools/template_renderer.py:**
```python
def my_custom_filter(value: str, param: str = "default") -> str:
    """Filter description"""
    return result

# Register with Jinja environment
environment.filters['my_custom_filter'] = my_custom_filter
```

**2. Document in this Developer Reference file**

**3. Add unit tests in tests/test_template_renderer.py:**
```python
def test_my_custom_filter():
    env = get_jinja_environment()
    result = env.from_string("{{ 'input' | my_custom_filter }}").render()
    assert result == "expected_output"
```

---

## Code Integration Points

### Where Code Extraction Happens

**File:** `src/tools/code_analyzer.py`

Main entry point: `populate_template(template_content, extracted_data_list, project_type, service_name)`

```python
def populate_template(
    template_content: str,
    extracted_data_list: List[ExtractedEntity],
    project_type: str,
    service_name: str
) -> str:
    """
    Populates template with extracted code data using Jinja2
    
    Args:
        template_content: Raw Jinja2 template markup
        extracted_data_list: Entities extracted from codebase
        project_type: 'service' | 'controller' | 'component' | 'table'
        service_name: Name of the component being documented
    
    Returns:
        Rendered markdown with 🤖 markers and ❓ placeholders
    """
```

### Where Templates Are Rendered

**File:** `src/tools/template_renderer.py`

Main entry point: `JinjaEnvironment.render(template_name, context_dict)`

```python
class JinjaEnvironment:
    """Singleton managing Jinja2 environment and custom filters"""
    
    def render(self, template_name: str, context: dict) -> str:
        """Render template with context data"""
        # Loads template/service.jinja2, component.jinja2, etc.
        # Injects context with extracted code data
        # Applies all custom filters
        # Returns markdown
```

### Where Validation Happens

**File:** `src/tools/enforcement_tool.py`

Main class: `DocumentationEnforcer`

```python
class DocumentationEnforcer:
    """Validates documentation against template requirements"""
    
    async def enforce(
        self,
        doc_content: str,
        template: str,
        config: EnforcementConfig
    ) -> EnforceResult:
        """
        Validates documentation and returns result
        
        Returns:
            EnforceResult with:
            - is_valid: bool
            - violations: List[Violation]
            - suggested_fixes: List[str]
            - metrics: ValidationMetrics
        """
```

### Where Template Schema Is Stored

**File:** `src/tools/template_schema_builder.py`

Hard-coded baseline sections mapping:

```python
TEMPLATE_BASELINE_SECTIONS = {
    "lean_baseline_service_template.md": [
        "Quick Reference (TL;DR)",
        "What & Why",
        # ... 7 more sections
    ],
    "ui_component_template.md": [
        "Quick Reference",
        "Purpose & Context",
        # ... 14 more sections
    ],
    # ...
}

def get_required_sections(self, template_name: str) -> List[Section]:
    """Returns required sections for template (not extracted from file)"""
    baseline_names = TEMPLATE_BASELINE_SECTIONS.get(template_name, [])
    return [Section(name=name, required=True) for name in baseline_names]
```

### Extending Code Extractors

To add support for new language or project type:

**1. Create extractor in src/tools/extractors/:**
```python
# src/tools/extractors/python_extractor.py
from .base_extractor import BaseExtractor

class PythonExtractor(BaseExtractor):
    def extract_services(self, codebase_path: str) -> List[ServiceEntity]:
        """Extract Python service definitions"""
        # Parse .py files
        # Identify classes with docstrings
        # Extract methods, parameters, return types
        return services
```

**2. Register in src/tools/code_analyzer.py:**
```python
from extractors.python_extractor import PythonExtractor

EXTRACTORS = {
    'csharp': CSharpExtractor(),
    'typescript': TypeScriptExtractor(),
    'python': PythonExtractor(),  # NEW
}
```

**3. Add template for language:**
```jinja2
{# templates/python_service.jinja2 #}
# {{ service_name }}

🤖 **Language:** Python
🤖 **Module:** {{ module_name }}
```

---

## Telemetry & Monitoring

### Telemetry Log Format

All events logged to `logs/enforcement.jsonl` (JSON Lines format):

```json
{
  "timestamp": "2026-02-19T14:23:45.123Z",
  "event_type": "VALIDATION_RUN",
  "doc_path": "docs/services/PaymentService_doc.md",
  "template": "lean_baseline_service_template.md",
  "status": "PASS",
  "duration_ms": 145,
  "metrics": {
    "completeness": 87,
    "section_count": 9,
    "words": 2150
  }
}
```

### Event Types

**VALIDATION_RUN** — Documentation validation executed
```json
{
  "event_type": "VALIDATION_RUN",
  "status": "PASS|FAIL",
  "template": "...",
  "violations": ["section_order", "missing_content"],
  "metrics": {"completeness": 85}
}
```

**WRITE_ATTEMPT** — User attempted to write documentation
```json
{
  "event_type": "WRITE_ATTEMPT",
  "doc_path": "...",
  "new_file": true,
  "method": "generate|direct|update"
}
```

**WRITE_SUCCESS** — Documentation successfully written
```json
{
  "event_type": "WRITE_SUCCESS",
  "doc_path": "...",
  "git_commit": "abc1234",
  "file_size": 5432
}
```

**WRITE_FAILURE** — Documentation write blocked
```json
{
  "event_type": "WRITE_FAILURE",
  "doc_path": "...",
  "violations": ["BLOCKER: missing_section"],
  "error_code": "VALIDATION_FAILED"
}
```

**WORKFLOW_VIOLATION** — User bypassed intended workflow
```json
{
  "event_type": "WORKFLOW_VIOLATION",
  "violation_type": "direct_write_new_file",
  "doc_path": "docs/new/service.md",
  "bypass_used": false
}
```

**DUPLICATE_WRITE** — Same file written multiple times quickly
```json
{
  "event_type": "DUPLICATE_WRITE",
  "doc_path": "...",
  "writes_count": 3,
  "time_window_seconds": 30
}
```

**CODE_EXTRACTION** — Code analysis completed
```json
{
  "event_type": "CODE_EXTRACTION",
  "component_name": "PaymentService",
  "project_type": "backend-api",
  "entity_count": 12,
  "extraction_time_ms": 234
}
```

### Analyzing Telemetry

Use provided script:

```bash
python scripts/analyze_workflow_telemetry.py --since "1 day ago"
```

Output:
```json
{
  "summary": {
    "total_events": 245,
    "time_range": "2026-02-18 to 2026-02-19",
    "unique_documents": 18
  },
  "validation": {
    "runs": 127,
    "pass_rate": 94.5,
    "avg_completeness": 85.2
  },
  "workflow": {
    "violations": 5,
    "violation_rate": 2.0,
    "most_common_violation": "direct_write_new_file"
  },
  "performance": {
    "avg_validation_ms": 145,
    "p95_validation_ms": 380,
    "avg_write_ms": 234
  }
}
```

---

## Troubleshooting

### Validation Errors

#### Error: "Missing required section: Quick Reference"

**Cause:** Template requires a "Quick Reference" section but it's not present in the document.

**Fix Option 1 (Regenerate):**
```
Use Copilot: "Generate new documentation stub"
This will create a fresh document with all required sections.
```

**Fix Option 2 (Add Section):**
```markdown
## Quick Reference

<!-- Add 1-2 sentence summary of this component -->
```

**Prevention:** Always use `generate_documentation` first when creating new docs.

#### Error: "Section out of order: Expected 'What & Why' before 'How It Works'"

**Cause:** Sections are in wrong order compared to template.

**Fix:**
```
Use Copilot: update_documentation_sections tool with reorder: true
Or manually move section headings to correct position.
```

**Correct order for lean_baseline_service_template.md:**
1. Quick Reference (TL;DR)
2. What & Why
3. How It Works
4. Business Rules
5. Architecture
6. API Contract (AI Context)
7. Validation Rules (AUTO-GENERATED)
8. Data Operations
9. Questions & Gaps

#### Error: "YAML frontmatter invalid or missing"

**Cause:** Document missing YAML header or fields malformed.

**Fix:** Document must start with:
```yaml
---
service_name: YourServiceName
service_type: business_logic | controller | custom_hook
language: csharp | typescript | sql
created_date: 2026-02-19
last_updated: 2026-02-19
---
```

### Code Extraction Issues

#### Problem: "Methods not extracted from my service"

**Cause:** Code analyzer couldn't parse your code patterns.

**Diagnosis:**
```bash
# Enable debug logging
export AKR_LOG_LEVEL=DEBUG

# Re-run extraction and check logs
python scripts/test_extraction.py --service MyService --debug
```

**Possible fixes:**
- Ensure service is public (public class or public export)
- Check for XML documentation comments (extractors use these for descriptions)
- Verify service follows naming conventions (ends with "Service", "Controller", component name)

#### Problem: "Getting incomplete context from extraction"

**Extraction Limitations by Language:**

| Capability | C# | TypeScript | SQL |
|-----------|----|----|-----|
| Public methods | ✅ | ✅ | ✅ |
| Properties/fields | ✅ | ✅ | N/A |
| Parameters | ✅ | ✅ | ✅ |
| Return types | ✅ | ✅ | ✅ |
| Docstrings/comments | ⚠️ (XML docs) | ⚠️ (JSDoc) | ⚠️ (SQL comments) |
| Private methods | ❌ | ❌ | ❌ |
| Lambda expressions | ⚠️ | ⚠️ | N/A |
| Async patterns | ✅ | ✅ | N/A |

**Workaround:** Fill in ❓ placeholders manually with missing context.

### MCP Server Issues

#### Problem: "Copilot doesn't see AKR tools"

**Debugging:**
1. Check that `mcp.json` exists in workspace root
2. Reload VS Code: Ctrl+Shift+P → "Developer: Reload Window"
3. Verify MCP server started: Check Output panel (View → Output) → "MCP"
4. Check for errors in MCP server logs

**Solution:**
```bash
# Manually start MCP server to see errors
cd akr-mcp-server
python src/server.py
```

#### Problem: "Tool calls hang or timeout"

**Debugging:**
```bash
# Check if Python process is stuck
ps aux | grep server.py

# Check recent logs
tail -f logs/enforcement.jsonl

# Profile slow operation
python -m cProfile -s cumtime src/server.py
```

**Common causes:**
- Large codebase taking long to extract
- File I/O blocked (permissions issue)
- Git operations hanging

**Solution:**
- Break large projects into smaller mcp.json configs
- Check file permissions on docs folder
- Verify git repo in good state: `git status`

### Performance Issues

#### Problem: "Documentation generation taking 30+ seconds"

**Diagnosis:**
```bash
# Check telemetry for slow components
python scripts/analyze_workflow_telemetry.py --since "1 hour ago" | grep "duration_ms"

# Expected times:
# - Code extraction: 100-500ms
# - Template rendering: 50-200ms  
# - Validation: 50-300ms
# - Total: 200-1000ms
```

**Likely causes:**
1. **Large codebase:** Extract taking too long
   - Solution: Reduce component_mappings scope
   - Only map key services, not every file

2. **Slow disk I/O:** Git operations slow
   - Solution: Check disk health, move to faster drive
   - Run `git gc` to optimize repo

3. **Memory pressure:** Python interpreter slow
   - Solution: Increase available RAM
   - Check for memory leaks: `memory_profiler`

---

## Reference: File Locations

| Component | File | Purpose |
|-----------|------|---------|
| MCP Server | `src/server.py` | Tool handlers, dispatcher |
| Code Analysis | `src/tools/code_analyzer.py` | Code extraction |
| Template Renderer | `src/tools/template_renderer.py` | Jinja2 rendering + filters |
| Enforcement | `src/tools/enforcement_tool.py` | Validation gate |
| Schema Builder | `src/tools/template_schema_builder.py` | Template schema mgmt |
| Templates | `templates/service.jinja2` | Jinja2 templates |
| Telemetry | `src/tools/enforcement_logger.py` | Logging |
| Tests | `tests/test_*.py` | Unit + integration tests |
| Scripts | `scripts/validate_documentation.py` | CLI tools |

---

## Getting Help

- **Installation issues?** → See [Installation and Setup](INSTALLATION_AND_SETUP.md)
- **How to use?** → See [Workflows by Project Type](WORKFLOWS_BY_PROJECT_TYPE.md)
- **Quick answers?** → See [Quick Reference](QUICK_REFERENCE.md)
- **System design?** → See [System Architecture](ARCHITECTURE.md)
