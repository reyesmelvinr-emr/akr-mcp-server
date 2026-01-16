# Application Knowledge Repository (AKR) MCP Documentation Server

A Model Context Protocol (MCP) server that provides AKR documentation resources and tools to GitHub Copilot in VS Code.

## Overview

This MCP server enables Copilot to:
- Access AKR charter files (documentation standards)
- Use documentation templates for consistent formatting
- Reference developer guides for best practices
- Validate generated documentation against AKR standards

## Prerequisites

- **Python 3.10+** (verified: Python 3.12.10)
- **VS Code** with GitHub Copilot extension
- **Git** (optional, for version control)

## Quick Start

### 1. Set Up Virtual Environment

```powershell
# Navigate to project directory
cd "c:\Users\E1481541\OneDrive - Emerson\Documents\CDS - Team Hawkeye\AKR with MCP\akr-mcp-server"

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Add AKR Content Files

Copy your AKR markdown files to the appropriate folders:

| File Type | Destination Folder | Examples |
|-----------|-------------------|----------|
| Charters | `akr_content/charters/` | `AKR_CHARTER_BACKEND.md`, `AKR_CHARTER_UI.md` |
| Templates | `akr_content/templates/` | `comprehensive_service_template.md` |
| Guides | `akr_content/guides/` | `Backend_Service_Documentation_Developer_Guide.md` |

### 4. Verify Setup

```powershell
# Check Python version
python --version

# Verify MCP SDK installation
pip show mcp

# Run server test (once server.py is implemented)
python src/server.py
```

## Project Structure

```
akr-mcp-server/
├── src/
│   ├── __init__.py
│   ├── server.py              # Main MCP server (Sprint 1)
│   ├── resources/
│   │   ├── __init__.py
│   │   └── akr_resources.py   # Resource handlers (Sprint 1)
│   └── tools/
│       ├── __init__.py
│       ├── health.py          # Health check tool (Sprint 1)
│       ├── templates.py       # Template tools (Sprint 1)
│       └── validation.py      # Validation tools (Sprint 2)
├── akr_content/               # AKR markdown files
│   ├── charters/              # Charter files
│   ├── templates/             # Template files
│   └── guides/                # Guide files
├── tests/
│   └── test_server.py
├── logs/                      # Server logs
├── .vscode/
│   ├── mcp.json              # MCP configuration for Copilot
│   └── settings.json         # VS Code workspace settings
├── config.json               # Server configuration
├── requirements.txt          # Python dependencies
├── .gitignore
└── README.md
```

## Configuration

### config.json

The `config.json` file controls server behavior:

```json
{
    "server": {
        "name": "akr-documentation-server",
        "version": "0.1.0"
    },
    "paths": {
        "akr_content": "./akr_content",
        "charters": "./akr_content/charters",
        "templates": "./akr_content/templates",
        "guides": "./akr_content/guides"
    },
    "logging": {
        "level": "INFO"
    }
}
```

### VS Code MCP Configuration

The `.vscode/mcp.json` file registers the server with Copilot:

```json
{
    "servers": {
        "akr-documentation-server": {
            "type": "stdio",
            "command": "python",
            "args": ["${workspaceFolder}/src/server.py"]
        }
    }
}
```

## Available Tools

| Tool | Description | Status |
|------|-------------|--------|
| `health_check` | Verify server is running and show AKR content stats | ✅ Implemented |
| `get_server_info` | Get server capabilities and usage information | ✅ Implemented |
| `list_templates` | List available documentation templates with filtering | ✅ Implemented |
| `suggest_template` | Suggest template based on file type/extension | ✅ Implemented |
| `get_project_config` | Read project configuration from .akr-config.json | 🔜 Sprint 2 |
| `suggest_documentation_path` | Get recommended output path for docs | 🔜 Sprint 2 |
| `get_documentation_context` | Get full context for documentation generation | 🔜 Sprint 2 |
| `validate_documentation` | Validate docs against AKR standards | 🔜 Sprint 2 |

### Write Operations (Sprint 4)

| Tool | Description | Status |
|------|-------------|--------|
| `initialize_documentation_session` | Detect main branch and repo context | ✅ Implemented |
| `select_documentation_branch` | Create or select feature branch for writes | ✅ Implemented |
| `write_documentation` | Write new documentation file to feature branch | ✅ Implemented |
| `analyze_documentation_impact` | Detect which doc sections are affected by code changes | ✅ Implemented |
| `update_documentation_sections` | Surgically update only affected sections | ✅ Implemented |
| `create_documentation_pr` | Create PR for documentation changes | ✅ Implemented |

> **Note:** Write operations always target feature branches, never main. All changes require PR review before merge.

### Human Input Interview Tools (Sprint 4)

| Tool | Description | Status |
|------|-------------|--------|
| `start_documentation_interview` | Start interactive Q&A for human context | ✅ Implemented |
| `get_next_interview_question` | Get current/next question in interview | ✅ Implemented |
| `submit_interview_answer` | Submit answer to current question | ✅ Implemented |
| `skip_interview_question` | Skip question with reason for later | ✅ Implemented |
| `get_interview_progress` | Get progress and summary | ✅ Implemented |
| `end_documentation_interview` | End session, get all drafted content | ✅ Implemented |

## Role-Based Interview System

The interview system supports **role-based question filtering** to ensure team members only answer questions relevant to their expertise.

### Available Roles

| Role | Display Name | Primary Knowledge Areas |
|------|--------------|------------------------|
| `technical_lead` | Technical Lead | Design rationale, performance, security, known issues |
| `developer` | Developer | Configuration, error handling, known issues, integrations |
| `product_owner` | Product Owner | Business context, business rules, future plans, user context |
| `qa_tester` | QA Tester | Testing, known issues, edge cases |
| `scrum_master` | Scrum Master | Team ownership, historical context |
| `general` | General | All questions (no filtering) |

### Using Role-Based Interviews

```
"Start a documentation interview for UserService.cs as a technical_lead"
"Start interview for the Button component as the product owner"
```

When a role is specified:
- Questions matching the role's expertise are shown
- Questions outside the role's domain are delegated to other team members
- The end-of-interview summary lists questions for other roles

### Customizing Role Mappings

Teams can customize which questions each role answers via `.akr-config.json`:

```json
{
  "interviewRoles": {
    "technical_lead": {
      "displayName": "Tech Lead",
      "description": "Architecture and design decisions",
      "primaryCategories": ["design_rationale", "performance", "security_compliance"],
      "secondaryCategories": ["known_issues"],
      "excludedCategories": ["business_context", "business_rules", "future_plans"]
    },
    "security_engineer": {
      "displayName": "Security Engineer",
      "description": "Security-focused questions only",
      "primaryCategories": ["security_compliance"],
      "secondaryCategories": ["known_issues", "performance"],
      "excludedCategories": ["business_context", "business_rules", "team_ownership"]
    }
  }
}
```

#### Configuration Options

| Field | Description |
|-------|-------------|
| `displayName` | Human-readable name shown in output |
| `description` | Brief description of the role's focus |
| `primaryCategories` | Questions this role is best suited to answer |
| `secondaryCategories` | Questions this role can answer if needed |
| `excludedCategories` | Questions to delegate to other roles |

#### Available Categories

| Category | Description |
|----------|-------------|
| `business_context` | Business purpose and value |
| `historical_context` | History and evolution |
| `business_rules` | Validation rules and constraints |
| `accessibility` | WCAG and accessibility requirements |
| `security_compliance` | Security and regulatory requirements |
| `performance` | SLAs and performance targets |
| `external_integration` | Third-party integrations |
| `team_ownership` | Team contacts and ownership |
| `known_issues` | Bugs and limitations |
| `future_plans` | Planned enhancements |
| `design_rationale` | Architecture decisions |
| `configuration` | Environment configuration |
| `error_handling` | Error handling patterns |
| `testing` | Testing strategies |
| `edge_cases` | Edge cases and boundaries |
| `user_context` | User personas and usage |

#### Customization Rules

1. **No config = sensible defaults** - The 5 built-in roles work out of the box
2. **Partial config = override only specified roles** - Other roles keep defaults
3. **Custom roles** - Add new roles like `security_engineer` or `data_analyst`

### Tool Usage Examples

**List all templates:**
```
"List all documentation templates"
"Show me the backend templates"
"What templates are available for UI components?"
```

**Suggest a template:**
```
"What template should I use for UserService.cs?"
"Suggest a template for my React component Button.tsx"
"Recommend a documentation template for this SQL file"
```

**Write operations (Sprint 4):**
```
"Document UserService.cs and save it to the repository"
"Update the documentation for CourseCard.tsx based on my recent changes"
"Create a PR with the new documentation for the API endpoints"
```

## Available Resources

Resources are exposed via MCP URIs and provide access to AKR documentation files.

### Resource Categories

| Category | URI Pattern | Description |
|----------|-------------|-------------|
| Charters | `akr://charter/{filename}` | Documentation standards and requirements |
| Templates | `akr://template/{filename}` | Documentation structure templates |
| Guides | `akr://guide/{filename}` | Developer guides and best practices |

### Available Charters

| Resource URI | Description |
|--------------|-------------|
| `akr://charter/AKR_CHARTER.md` | Main AKR documentation charter with general standards |
| `akr://charter/AKR_CHARTER_BACKEND.md` | Backend service documentation requirements |
| `akr://charter/AKR_CHARTER_DB.md` | Database documentation requirements |
| `akr://charter/AKR_CHARTER_UI.md` | UI component documentation requirements |

### Available Templates

| Resource URI | Description |
|--------------|-------------|
| `akr://template/comprehensive_service_template.md` | Full-featured service template with all sections |
| `akr://template/standard_service_template.md` | Standard service template for most use cases |
| `akr://template/lean_baseline_service_template.md` | Minimal template for simple services |
| `akr://template/minimal_service_template.md` | Ultra-minimal documentation template |
| `akr://template/table_doc_template.md` | Database table documentation template |
| `akr://template/ui_component_template.md` | UI component documentation template |

### Available Guides

| Resource URI | Description |
|--------------|-------------|
| `akr://guide/Backend_Service_Documentation_Developer_Guide.md` | Guide for documenting backend services |
| `akr://guide/Backend_Service_Documentation_Guide.md` | Backend service documentation overview |
| `akr://guide/Table_Documentation_Developer_Guide.md` | Guide for documenting database tables |
| `akr://guide/UI_Component_Documentation_Developer_Guide.md` | Guide for documenting UI components |

### Accessing Resources

Resources can be accessed via MCP resource protocol. Copilot will automatically discover and use these resources when generating documentation.

## Usage with Copilot

Once the server is running, you can ask Copilot:

```
"Check the AKR documentation server health"
"List available documentation templates"
"What template should I use for a C# service file?"
"Show me the backend charter requirements"
```

## Development

### Running Tests

```powershell
pytest tests/ -v
```

### Viewing Logs

Logs are written to `logs/akr-mcp-server.log`:

```powershell
Get-Content logs/akr-mcp-server.log -Tail 50
```

## Troubleshooting

### Virtual Environment Not Activating

If PowerShell blocks script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### MCP Server Not Connecting

1. Ensure virtual environment is activated
2. Verify `mcp.json` path is correct
3. Check VS Code Output panel for MCP errors
4. Restart VS Code after configuration changes

### Missing Dependencies

```powershell
pip install -r requirements.txt --upgrade
```

## Next Steps

1. ✅ Project structure created
2. ✅ Dependencies defined
3. ✅ Configuration files created
4. ✅ Virtual environment created and deps installed
5. ✅ Implement `server.py` with health_check tool
6. ✅ AKR content files added
7. ✅ MCP Resources implemented (list_resources, read_resource)
8. ✅ Template tools implemented (list_templates, suggest_template)
9. 🔄 Test with VS Code Copilot (requires workspace restart)
10. ⬜ Implement project configuration support (User Story 3.1)
11. ⬜ Implement documentation context provider (User Story 3.2)

---

**Sprint 1: COMPLETE** ✅

*Version: 0.1.0*  
*Last Updated: November 26, 2025*
