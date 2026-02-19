# AKR MCP Server - Setup Hub

This file is a short navigation hub for getting AKR-MCP-Server running and connected to your codebases. Detailed setup and workflows live in the consolidated docs.

---

## Start Here

### 1) First-Time Setup (new machine)

Follow the full installation guide:
- [docs/INSTALLATION_AND_SETUP.md](docs/INSTALLATION_AND_SETUP.md)

This includes:
- Python and dependency setup
- VS Code + GitHub Copilot configuration
- MCP server registration
- Verification checklist

### 2) Add a New Codebase (already installed)

Follow the project-type workflow guide:
- [Backend/API project](docs/WORKFLOWS_BY_PROJECT_TYPE.md#backend-api-project)
- [Frontend/UI project](docs/WORKFLOWS_BY_PROJECT_TYPE.md#frontend--ui-project)
- [Database project](docs/WORKFLOWS_BY_PROJECT_TYPE.md#database-project)
- [Monorepo](docs/WORKFLOWS_BY_PROJECT_TYPE.md#monorepo-setup)

---

## Quick Pointers

### MCP Configuration (important)

Use "servers" (not "mcpServers") in your MCP config:

```json
{
  "servers": {
    "akr-documentation-server": {
      "type": "stdio",
      "command": "python",
      "args": ["C:\\path\\to\\akr-mcp-server\\src\\server.py"],
      "env": {
        "PYTHONPATH": "C:\\path\\to\\akr-mcp-server\\src",
        "VSCODE_WORKSPACE_FOLDER": "${workspaceFolder}",
        "AKR_TEMPLATES_DIR": "C:\\path\\to\\core-akr-templates"
      }
    }
  }
}
```

### Documentation Tasks and Commands

Use the quick reference for AKR tasks and troubleshooting:
- [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)

### Developer and Architecture Details

- [docs/DEVELOPER_REFERENCE.md](docs/DEVELOPER_REFERENCE.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Need Help?

- Setup issues: [docs/INSTALLATION_AND_SETUP.md](docs/INSTALLATION_AND_SETUP.md)
- How to document your project: [docs/WORKFLOWS_BY_PROJECT_TYPE.md](docs/WORKFLOWS_BY_PROJECT_TYPE.md)
- Troubleshooting quick links: [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)

---

## Documentation Index

- Main entry point: [docs/README.md](docs/README.md)
- Installation: [docs/INSTALLATION_AND_SETUP.md](docs/INSTALLATION_AND_SETUP.md)
- Workflows: [docs/WORKFLOWS_BY_PROJECT_TYPE.md](docs/WORKFLOWS_BY_PROJECT_TYPE.md)
- Developer reference: [docs/DEVELOPER_REFERENCE.md](docs/DEVELOPER_REFERENCE.md)
- System architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

**Last Updated:** 2026-02-19  
**Maintained by:** AKR Development Team