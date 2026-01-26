# AKR MCP Server - Setup Guide

> **Welcome!** This guide helps you set up the AKR MCP server to automatically generate documentation for your codebase.

---

## 🎯 Choose Your Path

### 👤 Are you new to the team?

**First time setting up AKR MCP server on your laptop?**

➡️ **[First-Time Installation Guide](docs/FIRST_TIME_INSTALL.md)** (15-30 minutes, one-time only)

---

### 📂 Already have AKR MCP server installed?

**Want to add a new codebase/repository for documentation?**

Choose the guide that matches your repository type:

| Repository Type | Description | Guide |
|----------------|-------------|-------|
| **🎨 UI/Frontend** | React, Angular, Vue components | **[UI Repository Setup](docs/QUICK_START_UI_REPO.md)** ⭐ Most Common |
| **⚙️ API/Backend** | REST APIs, Services, Controllers | **[API Repository Setup](docs/QUICK_START_API_REPO.md)** ⭐ Most Common |
| **🗄️ Database** | SQL Tables, Views, Stored Procedures<br>*Also works for Database folders in API repos* | **[Database Repository Setup](docs/QUICK_START_DATABASE_REPO.md)** |
| **📦 Monorepo** | Single repo with UI, API, DB together | **[Monorepo Setup](docs/QUICK_START_MONOREPO.md)** |

⏱️ **Time Required:** 5 minutes per repository

---

## ❓ Need Help?

- **Something not working?** → [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- **How do I generate documentation?** → [Documentation Generation Guide](docs/HOW_TO_GENERATE_DOCUMENTATION.md) ⭐ **Important!**
- **Questions?** → Contact the AKR team

---

## 📖 After Setup

Once your repository is set up, learn how to generate documentation:

➡️ **[How to Generate Documentation](docs/HOW_TO_GENERATE_DOCUMENTATION.md)**

**Key Points:**
- ✅ Use natural language prompts (not slash commands!)
- ✅ Generate single files or logical batches
- ✅ Follow recommended documentation strategies
- ❌ Don't try to document 10+ files at once

**Note:** Use these commands directly in Copilot Chat **without** `@workspace` prefix.

---

## 📚 Documentation Structure

```
akr-mcp-server/
├── SETUP.md                    ← You are here (navigation hub)
├── README.md                   ← Feature overview
└── docs/
    ├── FIRST_TIME_INSTALL.md   ← One-time machine setup
    ├── QUICK_START_UI_REPO.md  ← Add UI repository
    ├── QUICK_START_API_REPO.md ← Add API repository
    ├── QUICK_START_DATABASE_REPO.md
    ├── QUICK_START_MONOREPO.md
    └── TROUBLESHOOTING.md      ← Common issues
```

---

**Last Updated:** January 23, 2026  
**Maintained by:** AKR Development Team

---

## Quick Start: New Repository Setup

> **⚠️ Prerequisites:** MCP server must already be installed on your machine. If not, go to [Quick Start (Automated Setup)](#quick-start-automated-setup) first.

### For Users Who Already Have MCP Server Installed

**This is the most common workflow:** You've already installed the AKR MCP server once on your machine. Now you want to document a new codebase.

#### Step 1: Open Your Application Repository in VS Code

```powershell
# Navigate to your application codebase
cd "C:\path\to\your\application"

# Open in VS Code
code .
```

#### Step 2: Create `.vscode/mcp.json` in Your Application Repository

Create `.vscode/mcp.json` in your application workspace root:

```powershell
# Create .vscode directory
New-Item -ItemType Directory -Path ".vscode" -Force
```

Create file: `.vscode/mcp.json`

```json
{
    "mcpServers": {
        "akr-documentation-server": {
            "command": "python",
            "args": [
                "C:\\Users\\E1481541\\OneDrive - Emerson\\Documents\\CDS - Team Hawkeye\\AKR with MCP\\akr-mcp-server\\src\\server.py"
            ],
            "env": {
                "PYTHONPATH": "C:\\Users\\E1481541\\OneDrive - Emerson\\Documents\\CDS - Team Hawkeye\\AKR with MCP\\akr-mcp-server\\src",
                "VSCODE_WORKSPACE_FOLDER": "${workspaceFolder}",
                "AKR_TEMPLATES_DIR": "C:\\Users\\E1481541\\OneDrive - Emerson\\Documents\\CDS - Team Hawkeye\\AKR with MCP\\core-akr-templates"
            }
        }
    }
}
```

**⚠️ IMPORTANT:** Replace the paths with your actual MCP server installation location:
- Update `command` path to point to your Python executable (or just use `python` if it's in PATH)
- Update `args[0]` path to your `akr-mcp-server\src\server.py` location
- Update `PYTHONPATH` to your `akr-mcp-server\src` location

#### Step 3: Create `.akr-config.json` in Your Application Repository

Choose the appropriate template based on your repository type:

**⚠️ Templates Location:** If templates are in your project directory instead of `$env:USERPROFILE\.akr\templates`, update the paths accordingly:
- **Standard location:** `$env:USERPROFILE\.akr\templates\.akr\examples\`
- **Project directory:** `<AKR-MCP-path>\core-akr-templates\.akr\examples\`

**For API/Backend:**
```powershell
# Option 1: Standard location (if symlink/junction created)
Copy-Item "$env:USERPROFILE\.akr\templates\.akr\examples\akr-config-webapp1-api.json" ".akr-config.json"

# Option 2: Project directory
Copy-Item "c:\Users\E1481541\OneDrive - Emerson\Documents\CDS - Team Hawkeye\AKR with MCP\core-akr-templates\.akr\examples\akr-config-webapp1-api.json" ".akr-config.json"
```

**For UI/Frontend:**
```powershell
# Option 1: Standard location (if symlink/junction created)
Copy-Item "$env:USERPROFILE\.akr\templates\.akr\examples\akr-config-webapp1-ui.json" ".akr-config.json"

# Option 2: Project directory
Copy-Item "c:\Users\E1481541\OneDrive - Emerson\Documents\CDS - Team Hawkeye\AKR with MCP\core-akr-templates\.akr\examples\akr-config-webapp1-ui.json" ".akr-config.json"
```

**For Database:**
```powershell
# Option 1: Standard location (if symlink/junction created)
Copy-Item "$env:USERPROFILE\.akr\templates\.akr\examples\akr-config-webapp1-db.json" ".akr-config.json"

# Option 2: Project directory (update path to your actual location)
Copy-Item "c:\Users\E1481541\OneDrive - Emerson\Documents\CDS - Team Hawkeye\AKR with MCP\core-akr-templates\.akr\examples\akr-config-webapp1-db.json" ".akr-config.json"
```

**For Monorepo:**
```powershell
# Option 1: Standard location (if symlink/junction created)
Copy-Item "$env:USERPROFILE\.akr\templates\.akr\examples\akr-config-monorepo.json" ".akr-config.json"

# Option 2: Project directory (update path to your actual location)
Copy-Item "c:\Users\E1481541\OneDrive - Emerson\Documents\CDS - Team Hawkeye\AKR with MCP\core-akr-templates\.akr\examples\akr-config-monorepo.json" ".akr-config.json"
```

Edit the file to match your project structure (see [Application Repository Setup](#application-repository-setup) for details).

#### Step 4: Reload VS Code

1. Press `Ctrl+Shift+P`
2. Type: **"Developer: Reload Window"**
3. Press Enter

#### Step 5: Verify Connection

Open GitHub Copilot Chat (Ctrl+Shift+I) and test:

```
@workspace /docs.health-check
```

**Expected Response:**
```
✅ AKR MCP Server - Health Check
Server Status: Running
Templates Available: 8
Workspace: Your Application Name
Configuration: Loaded
```

#### Step 6: Start Documenting!

```
@workspace /docs.generate path/to/your/file.cs
```

---

## Quick Start (Automated Setup)

### Option 1: Fully Automated Setup (Recommended)

```powershell
# Navigate to akr-mcp-server directory
cd "path\to\akr-mcp-server"

# Run automated setup script
.\setup.ps1
```

The script will:
1. ✅ Verify Python 3.10+ installation
2. ✅ Create Python virtual environment
3. ✅ Install all dependencies
4. ✅ Clone core-akr-templates repository to `~/.akr/templates`
5. ✅ Configure VS Code settings
6. ✅ Set up logging directory
7. ✅ Verify installation

**Setup script options:**
```powershell
# Skip VS Code configuration
.\setup.ps1 -SkipVSCode

# Use custom templates repository
.\setup.ps1 -TemplatesRepo "https://github.com/your-org/custom-templates"
```

---

## Manual Setup

### Step 1: Create Virtual Environment

```powershell
# Navigate to project directory
cd "C:\Users\YourName\Documents\akr-mcp-server"

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
```

**Execution Policy Error?**
```powershell
# If you get an execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Install Dependencies

```powershell
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

**Expected packages:**
- `mcp>=1.0.0` - Model Context Protocol SDK
- `pytest>=7.4.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async testing support
- `python-json-logger>=2.0.0` - Structured logging

### Step 3: Clone Template Repository

```powershell
# Create .akr directory in user profile
New-Item -ItemType Directory -Path "$env:USERPROFILE\.akr\templates" -Force

# Clone core-akr-templates repository
git clone https://github.com/reyesmelvinr-emr/core-akr-templates "$env:USERPROFILE\.akr\templates"
```

**Template repository structure:**
```
~/.akr/templates/
├── .akr/
│   ├── templates/          # 8 AKR templates
│   ├── charters/           # AKR charter files
│   ├── standards/          # Copilot instructions
│   └── examples/           # Sample .akr-config.json files
└── README.md
```

### Step 4: Create Logs Directory

```powershell
# Create logs directory for server output
New-Item -ItemType Directory -Path "logs" -Force
```

---

## VS Code Configuration

> **📍 This section is for the MCP server workspace only** (`akr-mcp-server` folder).  
> Application repositories use a different configuration (see [Application Repository Setup](#application-repository-setup)).

### Understanding Two Different Configurations

The AKR MCP server uses **two different** `.vscode/mcp.json` configurations:

| Configuration | Location | Purpose | Path Type |
|---------------|----------|---------|-----------|
| **MCP Server Config** | `akr-mcp-server/.vscode/mcp.json` | For testing/developing the MCP server itself | Relative paths (`${workspaceFolder}`) |
| **Application Config** | `your-app/.vscode/mcp.json` | For using MCP server to document your app | Absolute paths to MCP server |

**You are currently configuring:** The MCP Server workspace (first-time setup only).

### Step 1: Install Required Extensions

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Install:
   - **GitHub Copilot** (`GitHub.copilot`)
   - **GitHub Copilot Chat** (`GitHub.copilot-chat`)

### Step 2: Verify MCP Configuration

The MCP server configuration is defined in `.vscode/mcp.json`:

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
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        }
    }
}
```

### Step 3: Enable MCP Server in GitHub Copilot

1. Open GitHub Copilot Chat (Ctrl+Shift+I or click chat icon)
2. Click on the settings icon (⚙️) in chat panel
3. Navigate to **MCP Servers** section
4. Verify `akr-documentation-server` is listed and enabled
5. Toggle ON if disabled

### Step 4: Reload VS Code

```
1. Open Command Palette (Ctrl+Shift+P)
2. Type: "Developer: Reload Window"
3. Press Enter
```

---

## Verification

### Test 1: Python Environment

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Verify Python version
python --version
# Expected: Python 3.10.x or higher

# Verify MCP SDK installation
pip show mcp
# Expected: Version 1.0.0 or higher
```

### Test 2: Template Repository

```powershell
# Check if templates are cloned
Test-Path "$env:USERPROFILE\.akr\templates\.akr\TEMPLATE_MANIFEST.json"
# Expected: True

# List available templates
Get-ChildItem "$env:USERPROFILE\.akr\templates\.akr\templates" -Filter *.md
# Expected: 8 template files
```

### Test 3: MCP Server Connection

1. Open VS Code
2. Open GitHub Copilot Chat
3. Type: `@workspace What MCP servers are available?`
4. Expected response should mention `akr-documentation-server`

### Test 4: Server Tools (Optional)

In GitHub Copilot Chat:

```
@workspace Can you list all AKR templates?
```

Expected: List of 8 templates with descriptions

---

## Application Repository Setup

Once the MCP server is set up, configure your application repositories to use it.

### Repository Architecture Support

The AKR MCP server supports multiple repository architectures:

| Architecture | Description | Use Case | Setup Time |
|--------------|-------------|----------|------------|
| **Multi-Repo** | Separate repos for UI, API, Database | Standard web applications | <5 min per repo |
| **Monorepo** | Single repo with packages/ structure | Legacy applications | <5 min total |
| **Feature Repo** | GitHub repo for business documentation | All projects (always separate) | <5 min |

### Quick Setup (Automated)

**For any application repository (monorepo or multi-repo):**

```powershell
# Navigate to your application repository
cd C:\path\to\your\application

# Run setup with --ConfigureRepo flag
.\path\to\akr-mcp-server\setup.ps1 --ConfigureRepo

# What this does:
# - Detects repository type (monorepo/multi-repo)
# - Detects platform (Azure DevOps/GitHub)
# - Validates .akr-config.json exists
# - Creates .vscode/mcp.json with workspace variables
# - Displays configuration summary
```

### Manual Setup (If Needed)

#### Step 1: Create .akr-config.json

Choose the appropriate example based on your repository type:

**Multi-Repo (Standard):**
```powershell
# For UI repository
Copy-Item "$env:USERPROFILE\.akr\templates\.akr\examples\akr-config-webapp1-ui.json" ".akr-config.json"

# For API repository
Copy-Item "$env:USERPROFILE\.akr\templates\.akr\examples\akr-config-webapp1-api.json" ".akr-config.json"

# For API repository on Azure DevOps
Copy-Item "$env:USERPROFILE\.akr\templates\.akr\examples\akr-config-azure-devops-api.json" ".akr-config.json"
```

**Monorepo:**
```powershell
# For monorepo (single repo with packages/)
Copy-Item "$env:USERPROFILE\.akr\templates\.akr\examples\akr-config-monorepo.json" ".akr-config.json"
```

**Feature Repository (Always GitHub):**
```powershell
# For feature documentation repository
Copy-Item "$env:USERPROFILE\.akr\templates\.akr\examples\akr-config-feature-repo-dual-output.json" ".akr-config.json"
```

#### Step 2: Customize Configuration

Edit `.akr-config.json` to match your project:

**Multi-Repo Example:**
```json
{
  "version": "2.0",
  "repository": {
    "name": "YourApp_UI",
    "type": "ui",
    "language": "typescript"
  },
  "documentation": {
    "outputPath": "docs/",
    "pathMappings": {
      "src/components/**/*.tsx": "docs/components/{name}.md",
      "src/services/**/*.ts": "docs/services/{name}.md"
    }
  },
  "featureRepository": {
    "enabled": true,
    "url": "https://github.com/your-org/YourApp_Features.git"
  }
}
```

**Monorepo Example:**
```json
{
  "version": "2.0",
  "repository": {
    "name": "LegacyApp_Monorepo",
    "type": "monorepo",
    "packages": ["ui", "api", "database"]
  },
  "documentation": {
    "outputPath": "docs/",
    "pathMappings": {
      "packages/ui/**/*.tsx": "docs/components/{name}.md",
      "packages/api/**/*.cs": "docs/api/{name}.md",
      "packages/database/**/*.sql": "docs/database/{name}.md"
    }
  }
}
```

#### Step 3: Create VS Code MCP Configuration

**Important:** Each application repository needs its own `.vscode/mcp.json` that points to your MCP server installation.

**Manual Configuration:**
```powershell
# Create .vscode directory if it doesn't exist
New-Item -ItemType Directory -Path ".vscode" -Force

# Create .vscode/mcp.json file (see example below)
```

Create `.vscode/mcp.json` with **absolute paths** to your MCP server installation:

```json
{
  "mcpServers": {
    "akr-documentation-server": {
      "command": "python",
      "args": [
        "C:\\Users\\YourUsername\\path\\to\\akr-mcp-server\\src\\server.py"
      ],
      "env": {
        "PYTHONPATH": "C:\\Users\\YourUsername\\path\\to\\akr-mcp-server\\src",
        "VSCODE_WORKSPACE_FOLDER": "${workspaceFolder}",
        "AKR_TEMPLATES_DIR": "${env:USERPROFILE}\\.akr\\templates"
      }
    }
  }
}
```

**⚠️ Replace these paths:**
- `C:\\Users\\YourUsername\\path\\to\\akr-mcp-server\\src\\server.py` → Your actual MCP server location
- `C:\\Users\\YourUsername\\path\\to\\akr-mcp-server\\src` → Your actual src directory

**Example for typical installation:**
```json
{
  "mcpServers": {
    "akr-documentation-server": {
      "command": "python",
      "args": [
        "C:\\Users\\E1481541\\Documents\\akr-mcp-server\\src\\server.py"
      ],
      "env": {
        "PYTHONPATH": "C:\\Users\\E1481541\\Documents\\akr-mcp-server\\src",
        "VSCODE_WORKSPACE_FOLDER": "${workspaceFolder}",
        "AKR_TEMPLATES_DIR": "${env:USERPROFILE}\\.akr\\templates"
      }
    }
  }
}
```

**💡 Pro Tip:** You can also use just `python` as the command if Python is in your PATH:
```json
{
  "mcpServers": {
    "akr-documentation-server": {
      "command": "python",
      "args": [
        "C:\\path\\to\\akr-mcp-server\\src\\server.py"
      ],
      "env": {
        "PYTHONPATH": "C:\\path\\to\\akr-mcp-server\\src",
        "VSCODE_WORKSPACE_FOLDER": "${workspaceFolder}",
        "AKR_TEMPLATES_DIR": "${env:USERPROFILE}\\.akr\\templates"
      }
    }
  }
}
```

#### Step 4: Install Git Hook (Optional)

Automatically sync templates on `git pull`:

```powershell
# Copy hook script
Copy-Item "scripts\post-merge.ps1" ".git\hooks\post-merge.ps1"

# Or use bash version (Git Bash/WSL)
Copy-Item "scripts\post-merge" ".git\hooks\post-merge"
chmod +x .git/hooks/post-merge
```

### Workspace Detection Flow

When you open a repository in VS Code, the MCP server:

1. **Detects Workspace**: Reads `VSCODE_WORKSPACE_FOLDER` environment variable
2. **Loads Configuration**: Reads `.akr-config.json` from workspace root
3. **Identifies Type**: Determines if monorepo or multi-repo
4. **Maps Paths**: Configures source-to-docs mappings from config
5. **Ready**: Server is ready to generate documentation

### Verification

Test the workspace detection:

```
# In VS Code Copilot Chat
@workspace What is my current workspace and repository type?

# Or test MCP server
@workspace /docs.health-check
```

Expected output:
```
✓ Workspace detected: C:\path\to\your\application
✓ Repository type: monorepo (or standard)
✓ Configuration loaded: .akr-config.json
✓ Templates available: 8
✓ Ready to generate documentation
```

---

## Troubleshooting

### Problem: Python not found

**Symptom:** `python : The term 'python' is not recognized`

**Solution:**
1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Restart PowerShell/VS Code
4. Verify: `python --version`

---

### Problem: Virtual environment activation fails

**Symptom:** `Execution policy error` when running `Activate.ps1`

**Solution:**
```powershell
# Set execution policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Try activating again
.\venv\Scripts\Activate.ps1
```

---

### Problem: MCP server not appearing in Copilot

**Symptom:** MCP server not listed in GitHub Copilot Chat settings

**Solution:**
1. Verify `.vscode/mcp.json` exists in workspace
2. Check file has correct JSON syntax
3. Ensure virtual environment path is correct in config
4. Reload VS Code window: Ctrl+Shift+P → "Developer: Reload Window"
5. Check VS Code output panel: View → Output → Select "GitHub Copilot Chat"

---

### Problem: Template repository not found

**Symptom:** `Template directory not found` error

**Solution:**
```powershell
# Clone templates manually
git clone https://github.com/reyesmelvinr-emr/core-akr-templates "$env:USERPROFILE\.akr\templates"

# Verify
Test-Path "$env:USERPROFILE\.akr\templates\.akr\TEMPLATE_MANIFEST.json"
```

---

### Problem: Import errors in server.py

**Symptom:** `ModuleNotFoundError` or `ImportError`

**Solution:**
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Verify MCP installation
pip show mcp
```

---

### Problem: Git hook not executing

**Symptom:** Templates not syncing on `git pull`

**Solution:**
```powershell
# Verify hook file exists
Test-Path ".git\hooks\post-merge.ps1"

# Make sure Git is configured to use PowerShell hooks
git config core.hooksPath .git/hooks

# For bash version, ensure it's executable
chmod +x .git/hooks/post-merge  # Git Bash/WSL only
```

---

### Problem: GitHub Copilot organization policies block MCP

**Symptom:** MCP server loads but tools don't work

**Solution:**
1. Contact IT administrator
2. Request MCP server access in organization policies
3. Verify policies in GitHub organization settings:
   - Settings → Copilot → Policies → MCP Servers → **Enabled**
4. Verify model access: GPT-4.1, GPT-5.2 allowed

---

## Advanced Configuration

### Custom Template Repository

Use your organization's fork of core-akr-templates:

```powershell
# During setup
.\setup.ps1 -TemplatesRepo "https://github.com/your-org/akr-templates"

# Or manually
git clone https://github.com/your-org/akr-templates "$env:USERPROFILE\.akr\templates"
```

### Multiple Template Repositories

Support team-specific templates alongside organization templates:

```json
// In .akr-config.json
{
  "templates": {
    "sources": [
      "~/.akr/templates",           // Organization templates
      "./.akr/templates/team"       // Team-specific extensions
    ]
  }
}
```

### Environment-Specific Configuration

```powershell
# Development environment
$env:AKR_ENV = "development"
$env:AKR_LOG_LEVEL = "DEBUG"

# Production environment
$env:AKR_ENV = "production"
$env:AKR_LOG_LEVEL = "INFO"
```

### Logging Configuration

Edit `config.json` to customize logging:

```json
{
  "logging": {
    "level": "INFO",
    "file": "logs/akr-mcp-server.log",
    "max_size_mb": 10,
    "backup_count": 5
  }
}
```

---

## Next Steps

✅ **Setup Complete!** Now you can:

1. **Generate Documentation:** Use GitHub Copilot Chat with slash commands:
   ```
   @workspace /docs.generate <file-path>
   ```

2. **List Templates:** See available templates:
   ```
   @workspace /docs.list-templates
   ```

3. **Start Interview:** Get help filling human-required sections:
   ```
   @workspace /docs.interview <file-path>
   ```

4. **Update Documentation:** Surgically update existing docs:
   ```
   @workspace /docs.update <file-path>
   ```

---

## Support

- **Documentation:** See [README.md](README.md) for feature overview
- **Templates:** Browse `~/.akr/templates/.akr/templates/`
- **Examples:** Check `~/.akr/templates/.akr/examples/`
- **Issues:** Contact development team or create GitHub issue

---

## Quick Reference

### Setup Scenarios Comparison

| Task | First-Time Installation | Add New Repository |
|------|------------------------|-------------------|
| **Frequency** | Once per machine | Per codebase |
| **Time** | 15-30 minutes | 5 minutes |
| **Prerequisites** | None | MCP server installed |
| **Steps** | 1. Install Python<br>2. Clone templates<br>3. Setup venv<br>4. Configure MCP server workspace | 1. Create `.vscode/mcp.json`<br>2. Create `.akr-config.json`<br>3. Reload VS Code |
| **Configuration File** | `akr-mcp-server/.vscode/mcp.json` (relative paths) | `your-app/.vscode/mcp.json` (absolute paths) |
| **Section to Follow** | [Quick Start (Automated Setup)](#quick-start-automated-setup) | [Quick Start: New Repository Setup](#quick-start-new-repository-setup) |

### File Locations

| Item | Location |
|------|----------|
| MCP Server | `akr-mcp-server/src/server.py` |
| Templates | `~/.akr/templates/.akr/templates/` |
| MCP Server Config | `akr-mcp-server/.vscode/mcp.json` (relative paths) |
| Application Config | `your-app/.vscode/mcp.json` (absolute paths to MCP server) |
| Application Settings | `your-app/.akr-config.json` |
| Logs | `akr-mcp-server/logs/` |
| Git Hooks | `.git/hooks/post-merge.ps1` |

### Common Commands

```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Update templates
cd "$env:USERPROFILE\.akr\templates"
git pull origin main

# Reload VS Code
# Ctrl+Shift+P → "Developer: Reload Window"

# View server logs
Get-Content logs\akr-mcp-server.log -Tail 50
```

---

**Setup Guide Version:** 1.0  
**Last Updated:** January 14, 2026  
**Maintained by:** AKR Development Team
