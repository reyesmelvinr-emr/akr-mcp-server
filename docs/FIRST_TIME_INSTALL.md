# First-Time Installation Guide

> **Time Required:** 15-30 minutes  
> **For:** New team members setting up AKR MCP server for the first time

---

## 🎯 What You're Installing

The **AKR MCP Server** is a documentation assistant that:
- ✅ Automatically generates documentation from your code
- ✅ Works with UI, API, and Database files
- ✅ Integrates with GitHub Copilot Chat
- ✅ Uses intelligent templates for consistency

**You only need to do this once per laptop/PC.**

---

## ✅ Prerequisites Check

Before starting, make sure you have:

| Requirement | How to Check | Install If Missing |
|-------------|--------------|-------------------|
| **Python 3.10+** | `python --version` | [Download Python](https://www.python.org/downloads/) |
| **Git** | `git --version` | [Download Git](https://git-scm.com/downloads) |
| **VS Code** | `code --version` | [Download VS Code](https://code.visualstudio.com/) |
| **GitHub Copilot** | Open VS Code Extensions | [Install Extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) |

### Check Prerequisites

Open PowerShell and run:

```powershell
# Check Python (must be 3.10 or higher)
python --version

# Check Git
git --version

# Check VS Code
code --version
```

**If any are missing, install them before continuing.**

---

## 📥 Step 1: Get the AKR MCP Server Files

### Option A: Clone from Repository (Recommended)

```powershell
# Navigate to where you want to install
cd "C:\Users\$env:USERNAME\Documents"

# Clone the repository
git clone <AKR-MCP-Server-Repository-URL> akr-mcp-server

# Navigate into the folder
cd akr-mcp-server
```

---

### Option B: Extract from Shared Drive

If your team provides a zip file:

```powershell
# Extract to Documents folder
Expand-Archive -Path "\\shared\akr-mcp-server.zip" -DestinationPath "C:\Users\$env:USERNAME\Documents\akr-mcp-server"

# Navigate into the folder
cd "C:\Users\$env:USERNAME\Documents\akr-mcp-server"
```

---

## 🐍 Step 2: Set Up Python Virtual Environment

**Why?** Keeps AKR dependencies separate from other Python projects.

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

**You should see `(venv)` appear in your terminal prompt.**

---

## 📦 Step 3: Install Dependencies

```powershell
# Make sure you're in the akr-mcp-server directory
# and virtual environment is activated (you see "(venv)")

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

**This will install:**
- MCP SDK (Model Context Protocol)
- Documentation templates
- Testing tools

**Takes about 2-3 minutes.**

---

## 📚 Step 4: Get Documentation Templates

The templates are already in your project. Let's verify:

```powershell
# Check if templates exist
Test-Path "C:\Users\$env:USERNAME\Documents\CDS - Team Hawkeye\AKR with MCP\core-akr-templates\.akr\templates"
```

**Expected:** `True`

**If False:**
```powershell
# Ask your team lead for the core-akr-templates location
# or clone from repository
git clone <core-akr-templates-repo-url> core-akr-templates
```

---

## ⚙️ Step 5: Configure VS Code Extensions

### Install Required Extensions

1. Open VS Code
2. Click Extensions icon (Ctrl+Shift+X)
3. Install these extensions:
   - **GitHub Copilot** (`GitHub.copilot`)
   - **GitHub Copilot Chat** (`GitHub.copilot-chat`)

**Sign in to GitHub Copilot when prompted.**

---

## 🔧 Step 6: Set Up MCP Server in VS Code

### Create MCP Configuration

In the `akr-mcp-server` folder, create: `.vscode/mcp.json`

```powershell
# Make sure you're in akr-mcp-server directory
New-Item -ItemType Directory -Path ".vscode" -Force
```

**Copy this into `.vscode/mcp.json`:**

```json
{
    "servers": {
        "akr-documentation-server": {
            "type": "stdio",
            "command": "${workspaceFolder}/venv/Scripts/python.exe",
            "args": [
                "${workspaceFolder}/src/server.py"
            ],
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src",
                "AKR_TEMPLATES_DIR": "c:\\Users\\E1481541\\OneDrive - Emerson\\Documents\\CDS - Team Hawkeye\\AKR with MCP\\core-akr-templates"
            }
        }
    }
}
```

**⚠️ Important:** Update `AKR_TEMPLATES_DIR` to point to where your templates are located.

---

## ✅ Step 7: Test Your Installation

### Test 1: Open AKR MCP Server in VS Code

```powershell
# Open the akr-mcp-server folder in VS Code
code .
```

---

### Test 2: Reload VS Code Window

1. Press `Ctrl+Shift+P`
2. Type: **"Developer: Reload Window"**
3. Press Enter

---

### Test 3: Check MCP Server Output

1. Open Output panel: **View → Output** (or `Ctrl+Shift+U`)
2. Select "GitHub Copilot Chat" from dropdown
3. Look for:
   ```
   [info] Starting server akr-documentation-server
   [info] Connection state: Running
   [info] Discovered 27 tools
   ```

**If you see errors:** See [Troubleshooting](#troubleshooting) section below.

---

### Test 4: Enable MCP Server

1. Open Copilot Chat (`Ctrl+Shift+I`)
2. Click **settings icon** (⚙️) in chat panel
3. Look for **"MCP Servers"** section
4. Verify `akr-documentation-server` is **enabled** (toggle ON)

---

### Test 5: Test Health Check

In Copilot Chat, type:

```
/docs.health-check
```

**Expected Response:**
```
✅ AKR MCP Server - Health Check

Server Status: Running
Templates Available: 10
Workspace: akr-mcp-server
```

**🎉 If you see this, installation is complete!**

---

## 📝 Step 8: Save Your Installation Path

**Important:** Remember where you installed the AKR MCP server!

Your installation path is likely:
```
C:\Users\<YourUsername>\Documents\akr-mcp-server\
```

**Write this down** - you'll need it when setting up application repositories.

---

## ✅ Installation Complete!

### What's Next?

Now that the MCP server is installed, you can set up **application repositories** to generate documentation:

1. **For UI/Frontend repos:** [UI Repository Setup](QUICK_START_UI_REPO.md)
2. **For API/Backend repos:** [API Repository Setup](QUICK_START_API_REPO.md)
3. **For Database repos:** [Database Repository Setup](QUICK_START_DATABASE_REPO.md)
4. **For Monorepos:** [Monorepo Setup](QUICK_START_MONOREPO.md)

---

## 🐛 Troubleshooting

### Problem: Python Not Found

**Symptom:** `python : The term 'python' is not recognized`

**Solution:**
1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. **During installation:** Check ✅ "Add Python to PATH"
3. Restart PowerShell
4. Verify: `python --version`

---

### Problem: Virtual Environment Won't Activate

**Symptom:** `Execution policy error` when running `Activate.ps1`

**Solution:**
```powershell
# Allow scripts to run
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Try again
.\venv\Scripts\Activate.ps1
```

---

### Problem: MCP Server Not Starting

**Check Output Panel:**
1. Open: **View → Output**
2. Select: "GitHub Copilot Chat"
3. Look for error messages

**Common issues:**
- Wrong Python version (need 3.10+)
- Missing dependencies (run `pip install -r requirements.txt` again)
- Template path incorrect in `.vscode/mcp.json`

---

### Problem: MCP Server Not Listed in Copilot

**Solution:**
1. Verify `.vscode/mcp.json` exists in `akr-mcp-server` folder
2. Check JSON syntax is correct (no missing commas/brackets)
3. Reload VS Code: `Ctrl+Shift+P` → "Developer: Reload Window"
4. Check Copilot settings: Chat icon → Settings (⚙️) → MCP Servers

---

### Problem: Templates Not Found

**Symptom:** `/docs.health-check` shows "Templates: 0"

**Solution:**
```powershell
# Verify templates directory exists
Test-Path "C:\...\core-akr-templates\.akr\templates"

# Count template files
Get-ChildItem "C:\...\core-akr-templates\.akr\templates" -Filter *.md
```

**Expected:** 10 template files (.md)

If missing, contact your team lead for the templates location.

---

## 💡 Tips for Success

### Keep VS Code and Copilot Updated

```powershell
# Check for VS Code updates
# Help → Check for Updates

# Check for Copilot extension updates
# Extensions → Search "GitHub Copilot" → Update if available
```

---

### Deactivate Virtual Environment When Done

```powershell
# When finished working with AKR MCP server
deactivate
```

The `(venv)` prefix will disappear from your prompt.

---

### Update Templates Regularly

```powershell
# Navigate to templates folder
cd "C:\...\core-akr-templates"

# Pull latest updates
git pull origin main
```

---

## 📋 Quick Reference

### Common Commands

```powershell
# Activate virtual environment
cd "C:\Users\<YourUsername>\Documents\akr-mcp-server"
.\venv\Scripts\Activate.ps1

# Deactivate when done
deactivate

# Update dependencies
pip install -r requirements.txt --upgrade

# Check MCP SDK version
pip show mcp
```

---

### Installation Checklist

- [ ] Python 3.10+ installed
- [ ] Git installed
- [ ] VS Code installed
- [ ] GitHub Copilot extension installed
- [ ] AKR MCP server cloned/extracted
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Templates verified
- [ ] `.vscode/mcp.json` created
- [ ] MCP server shows "Running" in Output
- [ ] `/docs.health-check` works in Copilot Chat

---

## 🎓 Learning Resources

### Understanding MCP Servers

MCP (Model Context Protocol) servers extend GitHub Copilot with custom tools and capabilities. The AKR server adds documentation generation tools to Copilot.

**Learn more:**
- [MCP Documentation](https://spec.modelcontextprotocol.io/)
- [GitHub Copilot Docs](https://docs.github.com/en/copilot)

---

### AKR Documentation Standards

The templates follow AKR (Accessible Knowledge Repository) standards for:
- Consistent documentation structure
- Clear separation of AI-generated vs human-required content
- Business context capture
- Code-to-docs traceability

**Ask your team lead for:** AKR Charter documentation

---

## 📞 Get Help

### Team Support

- **Team Lead:** Contact for templates or repository access
- **IT Support:** Contact for Python/Git installation issues
- **AKR Team:** Contact for MCP server bugs or feature requests

---

### Share Your Feedback

After installation, let the team know:
- ✅ What worked well?
- ❌ What was confusing?
- 💡 What could be clearer?

Your feedback helps improve this guide!

---

**Last Updated:** January 23, 2026  
**Installation Guide Version:** 1.0
