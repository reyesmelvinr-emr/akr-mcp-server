# Installation and Setup Guide

> **Time Required:** 15-30 minutes  
> **For:** New team members setting up AKR MCP Server for the first time

---

## 🎯 What You're Installing

The **AKR MCP Server** is a documentation assistant that:
- ✅ Automatically extracts code context from your projects
- ✅ Provides templates and validation for consistent documentation
- ✅ Integrates seamlessly with GitHub Copilot Chat
- ✅ Works with C#, SQL, TypeScript, and more

**You only need to do this once per laptop/PC.**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Clone Repository](#step-1-clone-repository-and-initialize-submodules)
3. [Step 2: Set Up Python Environment](#step-2-set-up-python-virtual-environment)
4. [Step 3: Install Dependencies](#step-3-install-python-dependencies)
5. [Step 4: Configure VS Code](#step-4-configure-vs-code-and-github-copilot)
6. [Step 5: Verify Installation](#step-5-verify-installation)
7. [Optional: Global Tasks](#step-6-configure-global-akr-tasks-optional)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:

| Requirement | How to Check | Install If Missing |
|-------------|--------------|-------------------|
| **Python 3.10+** | `python --version` | [Download Python](https://www.python.org/downloads/) |
| **Git 2.13+** | `git --version` | [Download Git](https://git-scm.com/downloads) |
| **VS Code** | `code --version` | [Download VS Code](https://code.visualstudio.com/) |
| **GitHub Copilot** | Extensions panel in VS Code | [Install Extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) |

### Quick Check (All Platforms)

**Windows (PowerShell):**
```powershell
python --version
git --version
code --version
```

**macOS/Linux (Bash):**
```bash
python3 --version
git --version
code --version
```

**Expected:** All commands return version numbers

**If any are missing, install them before continuing.**

---

## Step 1: Clone Repository and Initialize Submodules

⚠️ **CRITICAL:** Starting with v0.2.0, templates are managed via Git submodule. You **MUST** initialize the submodule after cloning.

### Clone and Initialize

**Windows (PowerShell):**
```powershell
# Navigate to your preferred location
cd "$env:USERPROFILE\Documents"

# Clone repository with submodules
git clone --recursive <akr-mcp-server-repo-url> akr-mcp-server

# Navigate into folder
cd akr-mcp-server
```

**macOS/Linux (Bash):**
```bash
# Navigate to your preferred location
cd ~/Documents

# Clone repository with submodules
git clone --recursive <akr-mcp-server-repo-url> akr-mcp-server

# Navigate into folder
cd akr-mcp-server
```

### If You Already Cloned Without `--recursive`

Initialize the submodule manually:

```bash
# From within akr-mcp-server directory
git submodule update --init --recursive
```

### Verify Submodule Loaded

**Windows (PowerShell):**
```powershell
# Should list template files
Get-ChildItem templates\core\*.md | Select-Object -First 5

# Should show recent commit
git submodule foreach git log -1 --oneline
```

**macOS/Linux (Bash):**
```bash
# Should list template files
ls templates/core/*.md | head -5

# Should show recent commit
git submodule foreach git log -1 --oneline
```

**Expected output:**
```
templates/core
a1b2c3d chore: update templates for v1.3.0
```

⚠️ **If templates/core is empty:** See [Troubleshooting: Submodule Issues](#submodule-issues)

---

## Step 2: Set Up Python Virtual Environment

**Why?** Keeps AKR dependencies isolated from other Python projects.

### Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

**If you get an execution policy error:**
```powershell
# Allow scripts to run (one-time fix)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Try activating again
.\venv\Scripts\Activate.ps1
```

**macOS/Linux (Bash):**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**Success:** You should see `(venv)` appear in your terminal prompt.

---

## Step 3: Install Python Dependencies

Make sure your virtual environment is activated (`(venv)` visible in prompt).

```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

**What gets installed:**
- `fastmcp` or `mcp` — Model Context Protocol library
- `pyyaml` — YAML parsing for frontmatter
- `jinja2` — Template rendering engine
- `jsonschema` — Schema validation
- `pytest` — Testing framework

**Installation takes about 2-3 minutes.**

---

## Step 4: Configure VS Code and GitHub Copilot

### 4.1 Install GitHub Copilot Extension

1. Open VS Code
2. Go to **Extensions** (Ctrl+Shift+X or Cmd+Shift+X)
3. Search for "GitHub Copilot"
4. Click **Install**
5. Sign in with your GitHub account when prompted

### 4.2 Create MCP Configuration

The AKR MCP Server uses MCP (Model Context Protocol) to integrate with GitHub Copilot.

**Create `.vscode/mcp.json` in the akr-mcp-server folder:**

**Windows (PowerShell):**
```powershell
# Create .vscode directory
New-Item -ItemType Directory -Path ".vscode" -Force

# Create mcp.json (edit the content after creation)
New-Item -ItemType File -Path ".vscode\mcp.json" -Force
```

**macOS/Linux (Bash):**
```bash
# Create .vscode directory
mkdir -p .vscode

# Create mcp.json
touch .vscode/mcp.json
```

**Add this content to `.vscode/mcp.json`:**

**Windows:**
```json
{
    "mcpServers": {
        "akr-mcp-server": {
            "command": "${workspaceFolder}\\venv\\Scripts\\python.exe",
            "args": ["${workspaceFolder}\\src\\server.py"],
            "env": {
                "PYTHONPATH": "${workspaceFolder}\\src"
            }
        }
    }
}
```

**macOS/Linux:**
```json
{
    "mcpServers": {
        "akr-mcp-server": {
            "command": "${workspaceFolder}/venv/bin/python",
            "args": ["${workspaceFolder}/src/server.py"],
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        }
    }
}
```

### 4.3 (Optional) Configure Environment Variables

Create a `.env` file in the workspace root for optional configuration:

```bash
# Optional: Enable write operations (off by default for safety)
AKR_ENABLE_WRITE_OPS=false

# Optional: Set log level (default: INFO)
AKR_LOG_LEVEL=INFO

# Optional: Workspace root (usually auto-detected)
# AKR_WORKSPACE_ROOT=/path/to/your/project
```

---

## Step 5: Verify Installation

### Test 1: Open in VS Code

**Open the akr-mcp-server folder in VS Code:**

```bash
# From within akr-mcp-server directory
code .
```

### Test 2: Reload VS Code Window

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
2. Type: **"Developer: Reload Window"**
3. Press Enter

### Test 3: Check MCP Server Status

1. Open **Output** panel: **View → Output** (or `Ctrl+Shift+U`)
2. Select **"GitHub Copilot Chat"** from the dropdown
3. Look for:
   ```
   [info] Starting server akr-mcp-server
   [info] Connection state: Running
   [info] Discovered tools from akr-mcp-server
   ```

**If you see errors:** Check [Troubleshooting](#troubleshooting) section below.

### Test 4: Enable MCP Server in Copilot

1. Open **Copilot Chat** panel (`Ctrl+Shift+I` or sidebar icon)
2. Click the **settings icon** (⚙️) in chat panel
3. Look for **"MCP Servers"** section
4. Verify `akr-mcp-server` is listed and **enabled** (toggle ON)

### Test 5: Run Health Check

In Copilot Chat, type:

```
Run AKR health check
```

**Expected Response:**
```
✅ AKR MCP Server - Health Check

Server Status: Running
Templates Available: 10+
Resources Available: Yes
Tools Available: Yes
```

**🎉 If you see this, installation is complete!**

---

## Step 6: Configure Global AKR Tasks (Optional)

**NEW:** Make AKR tasks available in ALL your VS Code workspaces! 🚀

This optional step allows you to run AKR tasks from any workspace without switching to the akr-mcp-server folder.

### Why Configure Global Tasks?

- ✅ Run tasks from any workspace (UI repo, API repo, database repo)
- ✅ No workspace switching needed
- ✅ One-time setup, use everywhere
- ✅ Simplified workflow

### How to Configure

**Ensure virtual environment is activated, then run:**

```bash
python scripts/setup_global_tasks.py
```

**The script will:**
1. Detect your akr-mcp-server installation path
2. Set environment variables
3. Configure VS Code user settings
4. Backup existing settings

**Follow the prompts and restart VS Code when complete.**

### Verify Global Task Setup

```bash
python scripts/verify_global_tasks.py
```

**Expected:** All checks should pass ✓

**If you skip this step:** You can still run tasks from the akr-mcp-server workspace or use Copilot Chat. You can always add global tasks later.

---

## Post-Installation Checklist

- [ ] Python 3.10+ installed: `python --version`
- [ ] Git submodule initialized: `templates/core/*.md` files exist
- [ ] Virtual environment created and activated
- [ ] Dependencies installed: `pip list | grep mcp`
- [ ] `.vscode/mcp.json` created
- [ ] GitHub Copilot extension installed
- [ ] VS Code reloaded
- [ ] MCP server shows "Running" in Output panel
- [ ] MCP server enabled in Copilot Chat settings
- [ ] Health check passes in Copilot Chat
- [ ] (Optional) Global tasks configured

---

## Next Steps

### Choose Your Workflow

Now that the MCP server is installed, you can:

1. **Document a new project:**
   - [Backend/API Project Quick Start](WORKFLOWS_BY_PROJECT_TYPE.md#backend-api-project)
   - [Frontend/UI Project Quick Start](WORKFLOWS_BY_PROJECT_TYPE.md#frontend--ui-project)
   - [Database Project Quick Start](WORKFLOWS_BY_PROJECT_TYPE.md#database-project)

2. **Learn the Copilot Chat workflow:**
   - See [Copilot Chat Workflow Guide](COPILOT_CHAT_WORKFLOW.md)

3. **Explore available tools:**
   - See [Quick Reference](QUICK_REFERENCE.md)

---

## Troubleshooting

### Submodule Issues

#### Problem: `templates/core/` directory is empty

This means Git didn't clone the submodule content.

**Solution:**
```bash
# Initialize submodule
git submodule update --init --recursive

# If that doesn't work, try:
git submodule update --remote --merge

# Verify templates are now present
ls templates/core/*.md
```

#### Problem: "No submodule mapping found in .gitmodules"

**Solution:**
```bash
# Check if .gitmodules exists
cat .gitmodules

# If missing, you need to add the submodule
git submodule add <core-akr-templates-repo-url> templates/core
git add .gitmodules templates/core
git commit -m "chore: add templates submodule"
```

For more submodule help, see [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md).

---

### Python Issues

#### Problem: Python not found

**Symptom:** `python : The term 'python' is not recognized`

**Solution:**
1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. **During installation:** Check ✅ "Add Python to PATH"
3. Restart your terminal
4. Try `python3` instead of `python` (macOS/Linux)

#### Problem: Virtual environment won't activate

**Windows - Execution policy error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

**macOS/Linux - Permission denied:**
```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

#### Problem: Module import errors

**Solution:**
```bash
# Make sure virtual environment is activated
# Then reinstall:
pip install --upgrade pip
pip install -r requirements.txt
```

---

### VS Code / MCP Issues

#### Problem: MCP Server not starting

**Check Output Panel:**
1. **View → Output** (Ctrl+Shift+U)
2. Select "GitHub Copilot Chat"
3. Look for error messages

**Common issues:**
- Wrong Python version (need 3.10+)
- Missing dependencies (reinstall: `pip install -r requirements.txt`)
- Incorrect paths in `.vscode/mcp.json`
- Virtual environment not activated when starting VS Code

**Solution:**
```bash
# Ensure virtual environment is activated
# Deactivate and reactivate
deactivate
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows

# Reload VS Code
# Ctrl+Shift+P → "Developer: Reload Window"
```

#### Problem: MCP Server not listed in Copilot settings

**Solution:**
1. Verify `.vscode/mcp.json` exists in akr-mcp-server root
2. Check JSON syntax (no missing commas/brackets)
3. Reload VS Code: `Ctrl+Shift+P` → "Developer: Reload Window"
4. Open Copilot Chat → Settings (⚙️) → MCP Servers

#### Problem: Health check fails or shows 0 templates

**Solution:**
```bash
# Verify templates exist
ls templates/core/*.md

# Should see multiple .md files
# If empty, see "Submodule Issues" above
```

---

### GitHub Copilot Issues

#### Problem: Copilot extension not installed

**Solution:**
1. Open Extensions: `Ctrl+Shift+X`
2. Search: "GitHub Copilot"
3. Click Install
4. Sign in with GitHub account

#### Problem: Not subscribed to Copilot

**Solution:**
- You need an active GitHub Copilot subscription
- Check: https://github.com/settings/copilot

---

## System Requirements Summary

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.10 | 3.11+ |
| Git | 2.13+ | Latest |
| VS Code | Latest | Latest |
| RAM | 4 GB | 8 GB |
| Disk Space | 500 MB | 2 GB |

---

## Getting Help

### Documentation Resources

- **Installation issues?** → This guide's [Troubleshooting](#troubleshooting) section
- **Project-specific setup?** → [Workflows by Project Type](WORKFLOWS_BY_PROJECT_TYPE.md)
- **Using Copilot Chat?** → [Copilot Chat Workflow Guide](COPILOT_CHAT_WORKFLOW.md)
- **Command reference?** → [Quick Reference](QUICK_REFERENCE.md)
- **Technical details?** → [Developer Reference](DEVELOPER_REFERENCE.md)

### Team Support

- **Team Lead:** Template access or repository questions
- **IT Support:** Python/Git installation issues
- **AKR Team:** MCP server bugs or feature requests

---

## 💡 Tips for Success

### Keep Everything Updated

```bash
# Update templates (from templates/core directory)
cd templates/core
git pull origin main
cd ../..

# Update Python dependencies
pip install -r requirements.txt --upgrade

# Update VS Code and Copilot extension regularly
# Help → Check for Updates
```

### Deactivate Virtual Environment When Done

```bash
# When finished working with AKR
deactivate
```

The `(venv)` prefix will disappear from your prompt.

### Save Your Installation Path

Remember where you installed AKR MCP Server:
- **Windows:** `C:\Users\<YourUsername>\Documents\akr-mcp-server`
- **macOS/Linux:** `~/Documents/akr-mcp-server`

You may need this path when setting up application repositories.

---

## Installation Complete! 🎉

Once you've verified all steps, you're ready to start using AKR MCP Server with GitHub Copilot.

**Next:** Choose your project type guide from [Workflows by Project Type](WORKFLOWS_BY_PROJECT_TYPE.md) or try the [Copilot Chat Workflow](COPILOT_CHAT_WORKFLOW.md).

---

**Last Updated:** February 25, 2026  
**Guide Version:** 2.0 (Merged)
