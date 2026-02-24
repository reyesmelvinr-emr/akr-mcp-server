# AKR MCP Documentation Server

The AKR MCP server provides documentation templates, enforcement, and code analysis tools to GitHub Copilot in VS Code. It helps teams keep architecture and design documentation accurate as code evolves.

---

## What This Server Does

- Provides AKR templates and guides to Copilot
- Extracts data from codebases (C#, TypeScript, SQL)
- Generates documentation stubs with structured sections
- Enforces documentation compliance before write
- Logs telemetry for validation and workflow insights

---

## Start Here

### Documentation Entry Point

- [docs/README.md](docs/README.md)

### Installation and Setup

- [docs/INSTALLATION_AND_SETUP.md](docs/INSTALLATION_AND_SETUP.md)

### Project Workflows

- [docs/WORKFLOWS_BY_PROJECT_TYPE.md](docs/WORKFLOWS_BY_PROJECT_TYPE.md)

### Developer Reference

- [docs/DEVELOPER_REFERENCE.md](docs/DEVELOPER_REFERENCE.md)

### System Architecture

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Quick Start (Server Workspace)

```powershell
# Navigate to the server repository
cd "C:\path\to\akr-mcp-server"

# Create virtual environment
python -m venv venv

# Activate virtual environment (PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Verify Jinja2 pipeline
python test_jinja2_pipeline.py
```

To connect VS Code to the MCP server, follow the configuration steps in [docs/INSTALLATION_AND_SETUP.md](docs/INSTALLATION_AND_SETUP.md).

---

## Repository Structure

```
akr-mcp-server/
├── docs/                       # Consolidated documentation
├── src/                        # MCP server and tool implementations
├── templates/                  # Jinja2 templates
├── akr_content/                # Charters, guides, and template content
├── scripts/                    # Validation and utility scripts
├── tests/                      # Unit and integration tests
├── logs/                       # Telemetry and enforcement logs
└── README.md                   # You are here
```

---

## Key Config Files

### MCP Server Config (this repo)

The workspace MCP configuration lives in [/.vscode/mcp.json](.vscode/mcp.json).

### Project Config (your application repo)

Each application repo should include [/.akr-config.json](.akr-config.json) to define documentation mappings and validation preferences.

---

## Validation and Enforcement

Documentation is validated before it can be written. Key enforcement rules include:

- Required sections must exist
- Section order must match the template
- YAML frontmatter must be present
- Completeness threshold must be met

See [docs/DEVELOPER_REFERENCE.md](docs/DEVELOPER_REFERENCE.md) for full enforcement details.

---

## Write Operations (Disabled by Default)

Write tools are gated to prevent accidental changes. To enable writes:

1. Set environment variable: `AKR_ENABLE_WRITE_OPS=true`
2. Pass `allowWrites=true` in the tool call

If either check is missing, write operations will return a permission error. See [SECURITY.md](SECURITY.md) for details.

---

## Troubleshooting

- Quick fixes and task references: [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)
- Installation troubleshooting: [docs/INSTALLATION_AND_SETUP.md](docs/INSTALLATION_AND_SETUP.md)

---

## Contributing

For development workflows, template changes, and validation logic, use:
- [docs/DEVELOPER_REFERENCE.md](docs/DEVELOPER_REFERENCE.md)

---

**Last Updated:** 2026-02-19