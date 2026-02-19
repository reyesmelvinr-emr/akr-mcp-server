# Installation and Setup Guide

This guide walks you through setting up AKR-MCP-Server on your local machine and configuring it for your project.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** — [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** (for UI projects) — [Download Node.js](https://nodejs.org/)
- **Git** — [Download Git](https://git-scm.com/)
- **Visual Studio Code** — [Download VS Code](https://code.visualstudio.com/)
- **GitHub Copilot Subscription** — Required for MCP integration with GitHub Copilot

For **API/Database projects** (C#):
- **.NET SDK 6.0+** — [Download .NET](https://dotnet.microsoft.com/download)

---

## Step 1: Clone and Verify AKR-MCP-Server

```bash
# Clone the repository (if not already done)
git clone <akr-mcp-server-repo>
cd akr-mcp-server

# Verify Python version
python --version        # Should be 3.10 or higher
```

---

## Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Windows (cmd):
venv\Scripts\activate.bat

# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

**What gets installed:**
- `mcp` — Model Context Protocol library for Copilot integration
- `pyyaml` — YAML parsing for documentation frontmatter
- `jinja2` — Template rendering engine
- `pydantic` — Data validation
- `pytest` — Test framework

---

## Step 3: Verify Installation

Run the verification test to ensure everything is working:

```bash
# Test Jinja2 pipeline
python test_jinja2_pipeline.py

# Expected output:
# ✓ Template rendering successful
# ✓ Custom filters working
# ✓ All fixtures validated
```

Check that the telemetry log file exists:

```bash
# Verify telemetry logging is working
ls -la logs/enforcement.jsonl

# Should show a file with recent entries (within last hour)
```

---

## Step 4: Configure Environment Variables

Create a `.env` file in the workspace root (or set system environment variables):

```bash
# Optional: Set workspace root (usually auto-detected)
AKR_WORKSPACE_ROOT=C:\path\to\your\project

# Optional: Set log level (default: INFO)
AKR_LOG_LEVEL=DEBUG

# Optional: Set enforcement strictness (default: standard)
# Options: lenient, standard, strict
AKR_ENFORCEMENT_LEVEL=standard
```

Check your workspace's `mcp.json` for project-specific configuration:

```json
{
  "workspace_root": "/path/to/project",
  "component_mappings": {
    "path/to/Service.cs": {
      "template": "lean_baseline_service_template.md",
      "doc_path": "docs/services/Service_doc.md"
    }
  },
  "team": {
    "maintainers": ["developer@example.com"],
    "review_required": true
  }
}
```

---

## Step 5: Configure VS Code and GitHub Copilot Extension

### 5.1 Install GitHub Copilot Extension

1. Open VS Code
2. Go to **Extensions** (Ctrl+Shift+X)
3. Search for "GitHub Copilot"
4. Click **Install**
5. Sign in with your GitHub account

### 5.2 Enable MCP Server

The AKR-MCP-Server automatically registers when VS Code detects `mcp.json` in your workspace.

**Verify registration:**
1. Open VS Code settings (Ctrl+,)
2. Search: `GitHub Copilot: MCP Enabled`
3. Should show ✓ enabled

**If not auto-detected:**
1. Create/update `.vscode/settings.json`:
   ```json
   {
     "github.copilot.mcp.servers": {
       "akr-mcp-server": {
         "command": "python",
         "args": ["path/to/akr-mcp-server/src/server.py"],
         "env": {
           "PYTHONPATH": "path/to/akr-mcp-server/src"
         }
       }
     }
   }
   ```

2. Reload VS Code (Ctrl+Shift+P → "Developer: Reload Window")

### 5.3 Verify MCP Connection

1. Open the **Copilot Chat** panel (Ctrl+L or Activity Bar icon)
2. Type: `@akr list available templates`
3. Should see a list of available documentation templates

---

## Step 6: Create Your First Documentation

Follow the quick start guide for your project type:

- **Backend/API Project** → [API Quick Start](WORKFLOWS_BY_PROJECT_TYPE.md#backend-api-project)
- **Frontend/UI Project** → [UI Quick Start](WORKFLOWS_BY_PROJECT_TYPE.md#frontend--ui-project)
- **Database Project** → [Database Quick Start](WORKFLOWS_BY_PROJECT_TYPE.md#database-project)
- **Monorepo** → [Monorepo Setup](WORKFLOWS_BY_PROJECT_TYPE.md#monorepo-setup)

---

## Step 7: Post-Installation Verification Checklist

- [ ] Python 3.10+ installed: `python --version`
- [ ] Dependencies installed: `pip list | grep {mcp,jinja2,pyyaml}`
- [ ] Virtual environment activated and working
- [ ] Jinja2 pipeline tests pass: `python test_jinja2_pipeline.py`
- [ ] Telemetry logging working: `logs/enforcement.jsonl` exists
- [ ] GitHub Copilot extension installed and signed in
- [ ] MCP server registered in VS Code
- [ ] Can list AKR templates via Copilot Chat
- [ ] `mcp.json` exists in workspace root
- [ ] `.env` file configured (if needed)

---

## Troubleshooting

### Issue: Python not found
**Solution:**
- Verify Python installation: `python --version`
- Add Python to PATH: [Python Windows PATH Setup](https://docs.python.org/3/using/windows.html)
- Use `python3` instead of `python` on some systems

### Issue: Module import errors (mcp, jinja2, etc.)
**Solution:**
```bash
# Ensure virtual environment is activated
# Then reinstall:
pip install --upgrade -r requirements.txt
```

### Issue: GitHub Copilot extension not showing AKR tools
**Solution:**
1. Verify `mcp.json` exists in workspace root
2. Reload VS Code (Ctrl+Shift+P → "Developer: Reload Window")
3. Check Copilot Chat: "What MCP servers are available?"
4. View VS Code output panel (View → Output → "MCP") for error messages

### Issue: Telemetry logging not working
**Solution:**
```bash
# Verify logs directory exists
mkdir -p logs

# Verify write permissions
touch logs/enforcement.jsonl

# Check file size (should grow as you use tools)
ls -la logs/enforcement.jsonl
```

### Issue: Validation errors when writing documentation
**Solution:**
- See [Troubleshooting Validation Errors](DEVELOPER_REFERENCE.md#troubleshooting-validation-errors)
- Common issues: missing required sections, incorrect YAML frontmatter

---

## Next Steps

1. **Choose your project type** and follow the quick start guide
2. **Read about AKR markers** (🤖 vs ❓) to understand how extraction works
3. **Review the Quick Reference** for command list
4. **Set up your first documentation** for a key service/component

---

## System Requirements Summary

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.10 | 3.11+ |
| Node.js | 16 LTS | 18 LTS |
| .NET SDK (if C#) | 6.0 | 7.0+ |
| VS Code | Latest | Latest |
| RAM | 4 GB | 8 GB |
| Disk Space | 500 MB | 2 GB |

---

## Getting Help

- **Installation issues?** → Check [Troubleshooting](#troubleshooting) section
- **Project-specific setup?** → See [WORKFLOWS_BY_PROJECT_TYPE.md](WORKFLOWS_BY_PROJECT_TYPE.md)
- **Technical details?** → See [DEVELOPER_REFERENCE.md](DEVELOPER_REFERENCE.md)
- **Quick answers?** → See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## Installation Complete! 🎉

Once you've verified all steps, you're ready to start documenting your project.

**Next:** Choose your project type guide from [Workflows by Project Type](WORKFLOWS_BY_PROJECT_TYPE.md)
