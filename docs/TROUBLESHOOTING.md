# Troubleshooting Guide

> **Quick fixes for common issues when using AKR MCP server**

---

## 🔍 Table of Contents

- [Health Check Not Working](#health-check-not-working)
- [MCP Server Not Connecting](#mcp-server-not-connecting)
- [Templates Not Found](#templates-not-found)
- [AKR Tasks Not Found](#akr-tasks-not-found)
- [Wrong Workspace Detected](#wrong-workspace-detected)

---

## Health Check Not Working

### Symptom
When you ask Copilot Chat to run a health check, you get a long explanation instead of a short status message.

### Solution 1: Use a Short Health Check Prompt

**✅ Example:**
```
Run AKR MCP health check for this workspace.
```

---

### Solution 2: Check MCP Server is Running

1. Open Output panel: `View → Output` (or `Ctrl+Shift+U`)
2. Select "GitHub Copilot Chat" from dropdown
3. Look for:
   ```
   [info] Discovered 27 tools
   [info] Connection state: Running
   ```

**If you see errors:**
- Check that Python is installed: `python --version`
- Verify the paths in `.vscode/mcp.json` are correct

---

### Solution 3: Reload VS Code

1. Press `Ctrl+Shift+P`
2. Type: **"Developer: Reload Window"**
3. Press Enter
4. Try `/docs.health-check` again

---

## MCP Server Not Connecting

### Symptom
Copilot Chat cannot access AKR MCP tools or tasks are not available in Command Palette.

### Solution 1: Check .vscode/mcp.json Exists

Make sure `.vscode/mcp.json` file exists in your **application repository root** (not in the AKR MCP server folder).

```powershell
# Check if file exists
Test-Path ".vscode\mcp.json"
```

If False, go back to the setup guide for your repository type:
- [UI Repository Setup](WORKFLOWS_BY_PROJECT_TYPE.md#frontend--ui-project)
- [API Repository Setup](WORKFLOWS_BY_PROJECT_TYPE.md#backend-api-project)

---

### Solution 2: Verify JSON Schema

Open `.vscode/mcp.json` and ensure it uses this structure:

```json
{
    "servers": {               ← Must be "servers" not "mcpServers"
        "akr-documentation-server": {
            "type": "stdio",   ← Must include "type": "stdio"
            "command": "python",
            "args": [ "path/to/server.py" ],
            "env": { ... }
        }
    }
}
```

**Common mistakes:**
- ❌ Using `"mcpServers"` instead of `"servers"`
- ❌ Missing `"type": "stdio"`
- ❌ Wrong file paths (use double backslashes `\\` on Windows)

---

### Solution 3: Enable MCP Server in Copilot Settings

1. Open Copilot Chat (`Ctrl+Shift+I`)
2. Click **settings icon** (⚙️) in chat panel
3. Look for **"MCP Servers"** section
4. Verify `akr-documentation-server` is **enabled** (toggle ON)

---

## Templates Not Found

### Symptom
```
Error: Template directory not found
Error: Cannot copy akr-config-webapp1-ui.json
```

### Solution: Templates Are in Project Directory

The templates are located in:
```
c:\Users\E1481541\OneDrive - Emerson\Documents\CDS - Team Hawkeye\AKR with MCP\core-akr-templates\
```

**Use this path when copying configuration:**

```powershell
Copy-Item "c:\Users\E1481541\OneDrive - Emerson\Documents\CDS - Team Hawkeye\AKR with MCP\core-akr-templates\.akr\examples\akr-config-webapp1-ui.json" ".akr-config.json"
```

---

## AKR Tasks Not Found

### Symptom
You cannot find AKR tasks in **Tasks: Run Task** or task execution fails immediately.

### Solution 1: Check Global Task Setup

**NEW:** AKR tasks can be configured globally to be available in all workspaces.

Check if global tasks are configured:

```powershell
python "C:\path\to\akr-mcp-server\scripts\verify_global_tasks.py"
```

If checks fail, run the global task setup:

```powershell
cd "C:\path\to\akr-mcp-server"
python scripts\setup_global_tasks.py
```

Then restart VS Code.

### Solution 2: Check Environment Variable

Global tasks require the `AKR_MCP_SERVER_PATH` environment variable.

**Windows:**
```powershell
# Check if variable is set
$env:AKR_MCP_SERVER_PATH

# Expected: Path to your akr-mcp-server installation
# If empty, run: python scripts\setup_global_tasks.py
```

**Mac/Linux:**
```bash
# Check if variable is set
echo $AKR_MCP_SERVER_PATH

# Expected: Path to your akr-mcp-server installation
# If empty, add to ~/.bashrc or ~/.zshrc:
# export AKR_MCP_SERVER_PATH="/path/to/akr-mcp-server"
```

### Solution 3: Check VS Code User Settings

Verify AKR tasks are in your VS Code user settings:

1. Open VS Code
2. `Ctrl+,` (Settings)
3. Click "Open Settings (JSON)" icon (top right)
4. Search for `"tasks.tasks"`
5. Look for tasks with labels starting with "AKR:"

If missing, run: `python scripts\setup_global_tasks.py`

### Solution 4: Reload VS Code

After configuring global tasks or setting environment variables:

1. Press `Ctrl+Shift+P`
2. Type: **"Developer: Reload Window"**
3. Press Enter

### Solution 5: Legacy Approach - Run from MCP Server Workspace

If global tasks are not configured, you can still run tasks from the akr-mcp-server workspace:

1. Open a second VS Code window: `File` → `New Window`
2. Open the `akr-mcp-server` folder
3. Run tasks from there

**Note:** This is the legacy approach. Global task configuration is recommended for better workflow.

---

## Wrong Workspace Detected

### Symptom
In server logs, you see:
```
No .akr-config.json found in workspace: C:\Users\E1481541
```

But your `.akr-config.json` is in `C:\path\to\your-repo\.akr-config.json`

### Solution: Open Repository Directly in VS Code

1. **Close all VS Code windows**
2. **Navigate to your application repository:**
   ```powershell
   cd "C:\path\to\your-application-repo"
   ```
3. **Open in VS Code:**
   ```powershell
   code .
   ```
4. **Reload window:** `Ctrl+Shift+P` → "Developer: Reload Window"
5. **Test:** `/docs.health-check`

The workspace folder **must** be your application repository, not a parent folder or the AKR MCP server folder.

---

## MCP Server Logs Show Errors

### Symptom
Output panel shows Python errors or module not found.

### Solution: Verify Python Environment

```powershell
# Check Python version (must be 3.10+)
python --version

# Check MCP SDK is installed
pip show mcp
```

**If MCP not found:**
```powershell
# Navigate to AKR MCP server directory
cd "c:\...\AKR with MCP\akr-mcp-server"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Still Having Issues?

### Check These Common Mistakes

- [ ] `.vscode/mcp.json` is in the **application repository**, not AKR MCP server folder
- [ ] `.akr-config.json` is in the **application repository root**
- [ ] Paths in `.vscode/mcp.json` use **double backslashes** (`\\`)
- [ ] Using **"servers"** not "mcpServers" in JSON
- [ ] Using slash commands **without** `@workspace` prefix
- [ ] Opened VS Code in the **correct repository folder**

---

### Get Help

1. **Check server logs:**
   - Open: `View → Output`
   - Select: "GitHub Copilot Chat"
   - Look for error messages

2. **Share error message with team:**
   - Copy relevant error lines
   - Include what you were trying to do
   - Mention which guide you followed

3. **Contact AKR Team:**
   - Include your repository type (UI/API/Database/Monorepo)
   - Share error messages from Output panel
   - Let us know which step failed

---

**Last Updated:** January 23, 2026
