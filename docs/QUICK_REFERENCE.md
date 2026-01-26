# AKR MCP Server - Quick Reference Card

> **Print this page for quick access to commands and paths**

---

## 🚀 Slash Commands (Use in Copilot Chat)

```
/docs.health-check              Check server connection
/docs.list-templates            See available templates  
/docs.generate <file-path>      Generate documentation
/docs.interview <file-path>     Interactive Q&A assistant
/docs.update <file-path>        Update existing docs
```

**⚠️ Important:** Use commands **without** `@workspace` prefix

---

## 📁 Installation Paths (Update with your actual paths)

```
MCP Server:
c:\Users\<Username>\Documents\akr-mcp-server\

Templates:
c:\Users\<Username>\Documents\CDS - Team Hawkeye\AKR with MCP\core-akr-templates\

Python Virtual Env:
c:\Users\<Username>\Documents\akr-mcp-server\venv\
```

---

## ⚙️ Setup Checklist

### First-Time Setup (Once per machine)
- [ ] Install Python 3.10+
- [ ] Install Git
- [ ] Install VS Code + GitHub Copilot
- [ ] Clone akr-mcp-server repository
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Configure `.vscode/mcp.json` in MCP server folder
- [ ] Test with `/docs.health-check`

### New Repository Setup (Per codebase)
- [ ] Open repository in VS Code
- [ ] Create `.vscode/mcp.json` with absolute paths
- [ ] Copy `.akr-config.json` template
- [ ] Customize config for your project
- [ ] Reload VS Code window
- [ ] Test with `/docs.health-check`

---

## 📝 .vscode/mcp.json Template

```json
{
    "servers": {
        "akr-documentation-server": {
            "type": "stdio",
            "command": "python",
            "args": [
                "c:\\path\\to\\akr-mcp-server\\src\\server.py"
            ],
            "env": {
                "PYTHONPATH": "c:\\path\\to\\akr-mcp-server\\src",
                "VSCODE_WORKSPACE_FOLDER": "${workspaceFolder}",
                "AKR_TEMPLATES_DIR": "c:\\path\\to\\core-akr-templates"
            }
        }
    }
}
```

**⚠️ Must include:** `"type": "stdio"` and use `"servers"` not `"mcpServers"`

---

## 🎯 Common Tasks

### Activate Virtual Environment
```powershell
cd c:\path\to\akr-mcp-server
.\venv\Scripts\Activate.ps1
```

### Update Dependencies
```powershell
pip install -r requirements.txt --upgrade
```

### Check MCP Server Logs
1. View → Output (Ctrl+Shift+U)
2. Select "GitHub Copilot Chat" from dropdown

### Reload VS Code
```
Ctrl+Shift+P → "Developer: Reload Window"
```

---

## 🔧 Quick Fixes

### Health Check Returns Long Response
- ✅ Remove `@workspace` prefix
- ✅ Use `/docs.health-check` directly

### MCP Server Not Connecting
- ✅ Check `.vscode/mcp.json` exists in repo root
- ✅ Verify JSON uses `"servers"` not `"mcpServers"`
- ✅ Reload VS Code window

### Templates Not Found
- ✅ Check `AKR_TEMPLATES_DIR` path in `.vscode/mcp.json`
- ✅ Verify templates folder exists at that location

### Wrong Workspace Detected
- ✅ Close VS Code
- ✅ Open repository folder directly: `code .`
- ✅ Check `.akr-config.json` exists in repo root

---

## 📚 Documentation Guides

| Guide | Use When |
|-------|----------|
| [FIRST_TIME_INSTALL.md](FIRST_TIME_INSTALL.md) | Setting up AKR MCP for first time |
| [QUICK_START_UI_REPO.md](QUICK_START_UI_REPO.md) | Documenting UI/Frontend |
| [QUICK_START_API_REPO.md](QUICK_START_API_REPO.md) | Documenting API/Backend |
| [QUICK_START_DATABASE_REPO.md](QUICK_START_DATABASE_REPO.md) | Documenting Database |
| [QUICK_START_MONOREPO.md](QUICK_START_MONOREPO.md) | Documenting Monorepo |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Having issues |

---

## 📞 Get Help

**Team Lead:** _________________________  
**AKR Team Contact:** _________________________  
**IT Support:** _________________________  

---

**Last Updated:** January 23, 2026  
**Version:** 1.0
