# AKR-MCP-Server Documentation

Welcome to the AKR-MCP-Server documentation. This guide will help you understand, install, and use the AKR (Architecture Knowledge Representation) documentation system with the Model Context Protocol (MCP) integration.

## What is AKR-MCP-Server?

AKR-MCP-Server is a comprehensive documentation automation system designed to help development teams maintain accurate, current architecture and design documentation as code evolves. It automates the extraction of information from your codebase (C#, TypeScript, SQL) and populates structured documentation templates using Jinja2 templating.

**Key Features:**
- 🤖 **Automated Extraction** — Analyzes your code to extract services, components, endpoints, and database schema
- 📝 **Template-Based Documentation** — Generates consistent, well-structured documentation from extracted data
- ✅ **Enforcement Gates** — Validates documentation against AKR compliance standards before write
- 🔄 **MCP Integration** — Works directly with GitHub Copilot via the Model Context Protocol

## Quick Navigation

### 👤 I'm Setting Up for the First Time
Start here: [Installation and Setup Guide](INSTALLATION_AND_SETUP.md)
- Prerequisites and environment setup
- VS Code extension configuration
- Post-install verification

### 🚀 I Want to Document My Project
Choose your project type:
- **Backend/API Project:** [API Project Quick Start](WORKFLOWS_BY_PROJECT_TYPE.md#backend-api-project)
- **Frontend/UI Project:** [UI Project Quick Start](WORKFLOWS_BY_PROJECT_TYPE.md#frontend--ui-project)
- **Database Project:** [Database Quick Start](WORKFLOWS_BY_PROJECT_TYPE.md#database-project)
- **Monorepo (Multi-Project):** [Monorepo Setup](WORKFLOWS_BY_PROJECT_TYPE.md#monorepo-setup)

All guides include:
- Step-by-step workflow with examples
- Code snippets for your project type
- Understanding AKR markers (🤖 auto-extracted vs. ❓ human input)
- Common mistakes and how to avoid them

### 👨‍💻 I'm a Developer Extending the System
See: [Developer Reference](DEVELOPER_REFERENCE.md)
- Enforcement architecture and validation flow
- Template system and Jinja2 custom filters
- Telemetry and monitoring
- Code integration points

### 📚 I Need a Quick Lookup
See: [Quick Reference](QUICK_REFERENCE.md)
- Command reference for all AKR tasks
- Jinja2 custom filter API
- Common issues and fixes

### 🏗️ I Want to Understand the Architecture
See: [System Architecture](ARCHITECTURE.md)
- High-level system design
- Data flow diagrams
- Key components and their interactions
- Technology decisions and trade-offs

---

## Understanding AKR Markers

One of the first concepts to understand is the difference between **🤖 auto-extracted** and **❓ human input** sections. This is core to how AKR works.

| Marker | Meaning | When You See It | What to Do |
|--------|---------|-----------------|-----------|
| 🤖 | **Auto-extracted** | System automatically populated this from your code | Review and verify accuracy; enhance if needed |
| ❓ | **Requires Input** | System couldn't extract this automatically | Fill in manually with your knowledge |

**Example:**
```markdown
## API Endpoints

🤖 Extracted the following endpoints from your code:
- GET /api/v1/courses
- POST /api/v1/courses
- GET /api/v1/courses/{id}

## Business Rules

❓ Please add business rules specific to this service.
For example: rate limiting, validation constraints, state transitions.
```

For detailed examples and workflows, see the [project type guides](WORKFLOWS_BY_PROJECT_TYPE.md#understanding-markers).

---

## Common Workflows

### Workflow 1: Generate Documentation for a New Service

1. **Generate stub** — Creates empty documentation template
   ```
   Use: generate_documentation tool
   Parameters: component_name="PaymentService", template="lean_baseline_service_template.md"
   ```

2. **Review and enhance** — Review extracted data and add missing information
   ```
   Review 🤖 markers for accuracy
   Fill in ❓ sections with your knowledge
   ```

3. **Write and validate** — Save documentation with compliance checks
   ```
   Use: write_documentation tool
   System validates against AKR standards
   ```

### Workflow 2: Update Existing Documentation

1. **Identify sections** — Determine what needs updating
2. **Use update tool** — Update specific sections without regenerating entire doc
   ```
   Use: update_documentation_sections tool
   Select sections to update, keep others intact
   ```
3. **Validate** — System re-validates entire document

---

## Project Structure

```
akr-mcp-server/
├── docs/                          # User documentation
│   ├── README.md                  # You are here
│   ├── INSTALLATION_AND_SETUP.md  # Setup guide
│   ├── WORKFLOWS_BY_PROJECT_TYPE.md # Project-type workflows
│   ├── DEVELOPER_REFERENCE.md     # Developer guide
│   ├── QUICK_REFERENCE.md         # Quick lookup
│   ├── ARCHITECTURE.md            # System architecture
│   ├── architecture/              # Architecture diagrams & docs
│   └── _archived/                 # Historical phase documentation
├── src/                           # Main source code
│   ├── server.py                  # MCP server & tool definitions
│   ├── tools/                     # Tool implementations
│   │   ├── code_analyzer.py      # Code extraction logic
│   │   ├── template_renderer.py  # Jinja2 rendering
│   │   ├── enforcement_tool.py   # Validation & compliance
│   │   └── ...
│   └── ...
├── templates/                     # Jinja2 templates
│   ├── service.jinja2
│   ├── component.jinja2
│   └── table.jinja2
├── scripts/                       # Utility scripts
│   ├── validate_documentation.py # Pre-write validation
│   └── analyze_workflow_telemetry.py # Metrics analysis
└── tests/                         # Test suite
```

---

## Getting Help

### Problem: "I don't understand what 🤖 vs ❓ means"
👉 See [Understanding Markers](WORKFLOWS_BY_PROJECT_TYPE.md#understanding-markers) section in project-type guides

### Problem: "Documentation generation failed with validation error"
👉 See [Troubleshooting Validation](DEVELOPER_REFERENCE.md#troubleshooting-validation-errors) in Developer Reference

### Problem: "My code changes aren't showing up in documentation"
👉 See [Code Extraction Limitations](DEVELOPER_REFERENCE.md#code-extraction-capabilities) in Developer Reference

### Problem: "I want to understand enforcement rules"
👉 See [Enforcement Architecture](DEVELOPER_REFERENCE.md#enforcement-architecture) in Developer Reference

---

## Next Steps

1. **New to AKR?** → Read [Installation and Setup](INSTALLATION_AND_SETUP.md)
2. **Ready to document?** → Choose your [project type guide](WORKFLOWS_BY_PROJECT_TYPE.md)
3. **Building/extending?** → Read [Developer Reference](DEVELOPER_REFERENCE.md)
4. **Need quick answers?** → Use [Quick Reference](QUICK_REFERENCE.md)

---

## Documentation Version History

- **Current:** 2026-02-19 — Consolidated documentation focusing on current system state
- **Archive:** Historical phase documentation available in [_archived](/_archived/) directory

For historical context on the Jinja2 migration, regex→template evolution, and implementation phases, see [Archived Documentation](_archived/README.md).
