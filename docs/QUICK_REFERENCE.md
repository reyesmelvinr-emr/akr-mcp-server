# AKR MCP Server - Quick Reference Card

> **Print this page for quick access to commands and paths**

---

## 🚀 Command Palette Tasks (Recommended)

Run AKR checks from VS Code (activate the venv first):
1. `Ctrl+Shift+P` → **Tasks: Run Task**
2. Select one of the AKR tasks below

### Available AKR Tasks

#### **AKR: Generate and Write Documentation (Unified)** ⚡ **NEW - RECOMMENDED**
**What it does:** Creates complete AKR documentation in ONE step - auto-detects project type, generates full template with placeholders, validates, and writes file

**When to use:**
- **PRIMARY WORKFLOW:** When you want documentation created start-to-finish in one command
- When scaffolding + generation as separate steps feels redundant
- When you want the fastest path from source code to documented file
- When you prefer automation over manual multi-step processes

**Example use case:**
```
1. Run "AKR: Generate and Write Documentation (Unified)"
2. Enter module name: "EnrollmentService"
3. Enter source files: "Domain/Services/IEnrollmentService.cs,Controllers/EnrollmentsController.cs"
4. ✅ File created at docs/services/EnrollmentService_doc.md with full template structure
5. Review file and fill in ❓ placeholders (Business Rules, What & Why, etc.)
6. Run "AKR: Validate Documentation (file)" to check compliance
7. Commit to git
```

**What it generates:**
- Full template structure with all sections (not just minimal stubs)
- All placeholder substitutions ([SERVICE_NAME], [DOMAIN], dates)
- Source file metadata as comments
- Sections requiring human input marked with ❓ (Business Rules, What & Why, etc.)
- Enforcement validation applied automatically

**Time:** < 1 minute per file (combines 3 steps into 1)

**Advantages over scaffold → generate → write:**
- **Faster:** One command vs. three separate operations
- **Simpler:** No need to orchestrate multiple tools
- **Consistent:** Auto-detects project type and selects correct template
- **Complete:** Gets you to reviewable documentation immediately

---

#### **AKR: Scaffold New Documentation** 🏗️ **(Legacy - Optional)**
**What it does:** Creates a template documentation file with boilerplate structure

**When to use:**
- When you want to preview the template structure before adding content
- When batch-documenting multiple related files (use Interactive Scaffolding Guide instead)
- When you prefer the old two-step workflow (scaffold first, then ask Copilot to fill in)

**Note:** This task is now **optional**. The new unified task above combines this step with generation and writing for faster results.

**Example use case:**
```
1. Run "AKR: Scaffold New Documentation"
2. Enter module name: "UserService"
3. Enter source files: "Domain/Services/UserService.cs"
4. Template file created at docs/services/UserService_doc.md
5. Open Copilot Chat and ask to generate content for that file
```

**Time:** < 1 minute per file

---

#### **AKR: Validate Documentation (file)** ✅
**What it does:** Checks one specific documentation file for compliance with AKR standards

**When to use:**
- After writing or editing a single documentation file
- To verify a file meets all required sections and standards
- Before committing a documentation file to git
- When you want detailed feedback on one specific doc

**Example use case:**
```
You just created docs/services/PaymentService.md
Run this task and select the file
Gets back: "✅ Valid - All sections present, 85% complete"
or "❌ Missing: Business Rules section, 3 ❓ placeholders unfilled"
```

**Time:** < 30 seconds per file

---

#### **AKR: Validate Documentation (changed files)** 🔄
**What it does:** Checks all documentation files you've modified since last commit

**When to use:**
- After creating or updating documentation files
- Before creating a pull request
- To batch-validate multiple files you've worked on
- Daily/weekly to catch issues early

**Example use case:**
```
You generated docs for 3 new components this session
Run this task
Returns validation for all 3 files at once
Shows which files need work before you commit
```

**Time:** < 1 minute for typical batch

---

#### **AKR: Validate Documentation (all in docs/)** 🏛️
**What it does:** Scans every documentation file in your `docs/` folder for compliance

**When to use:**
- Before major releases to ensure all docs are up-to-date
- To get a health check on documentation quality across the repo
- Monthly/quarterly audits of documentation coverage
- Before code freeze to ensure documentation completeness

**Example use case:**
```
Team lead runs before release
Reports back: "15/20 docs compliant, 5 missing business context"
Identifies which docs need attention before shipping
```

**Time:** 1-3 minutes depending on repo size

---

#### **AKR: Validate Traceability** 🔗
**What it does:** Checks that documentation is linked to source code (you documented what actually exists)

**When to use:**
- After refactoring or deleting source files
- To catch "orphaned" documentation (docs for deleted code)
- When verifying documentation accuracy against current codebase
- During code reviews to ensure docs match implementation

**Example use case:**
```
You deleted Services/OldService.cs from your codebase
Run this task
Returns: "⚠️ Orphaned doc found: docs/services/OldService.md refers to deleted code"
You delete the corresponding doc to stay in sync
```

**Time:** 1-2 minutes depending on repo size

---

#### **AKR: Scan Write Bypasses** 🚨
**What it does:** Detects documentation files created outside the AKR workflow (enforcement check)

**When to use:**
- To ensure team is using proper AKR workflow instead of creating docs manually
- After developers join the team (ensure they're following process)
- During code reviews to catch workflow violations
- For governance and audit compliance

**Example use case:**
```
Developer creates doc manually without using Copilot/scaffolding
Run this task
Returns: "⚠️ File created outside workflow: docs/services/Manual.md"
Tells developer to regenerate using proper AKR process
```

**Time:** < 30 seconds

---

## � Code Analysis & Extraction (NEW)

**What it does:** Automatically reads source files and extracts code structure into documentation templates

**Key Feature:** The unified workflow now includes **automatic code extraction** that reads your source files and populates documentation sections with actual code details (methods, routes, props, columns, etc.)

### What Gets Auto-Extracted

| Language | What's Extracted |
|----------|------------------|
| **C#** | Classes, methods, parameters, return types, HTTP routes, validation rules, dependencies, attributes |
| **TypeScript/React** | Components, props with types, state variables, event handlers, hooks, child components, CSS classes |
| **SQL** | Tables, columns with types/nullability, PRIMARY/FOREIGN KEYs, constraints, indexes |

### Configuration

Add to your workspace `.akr-config.json` or global `config.json`:

```json
{
  "code_analysis": {
    "enabled": true,
    "depth": "full",
    "languages": ["csharp", "typescript", "sql"],
    "timeout_seconds": 30,
    "fallback_on_error": "partial"
  }
}
```

### Options

| Option | Values | Description |
|--------|--------|-------------|
| `enabled` | `true`/`false` | Turn analysis on/off |
| `depth` | `signatures`/`moderate`/`full` | How deep to analyze |
| `languages` | Array | Which languages to support |
| `fallback_on_error` | `partial`/`stub`/`fail` | What to do if extraction fails |

### Example: Before & After

**Before extraction** (template):
```markdown
## Methods
🤖 Describe the methods exposed by this service
```

**After extraction** (auto-populated):
```markdown
## Methods
<!-- AI-extracted: Methods -->
| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `GetCourseAsync()` | id: int | `Task<CourseDto>` |  |
| `CreateCourseAsync()` | request: CreateCourseRequest | `Task<CourseDto>` |  |
```

### Template Markers

- **🤖 = AI-extractable**: Code analyzer fills this automatically
- **❓ = Human-required**: You need to fill this in (business context, rationale, etc.)

### When It Runs

Code analysis runs automatically during:
- **AKR: Generate and Write Documentation (Unified)** task
- Any MCP tool that generates documentation (`generate_and_write_documentation`)

You don't need to do anything special - it just works!

### Disabling Code Analysis

If you want to generate docs **without** code extraction:

**Option 1:** Set in `.akr-config.json`:
```json
{
  "code_analysis": { "enabled": false }
}
```

**Option 2:** Use environment variable:
```powershell
$env:AKR_CODE_ANALYSIS_ENABLED = "false"
```

---

## �📋 Quick Task Guide by Scenario

| Scenario | Task to Run | Why |
|----------|------------|-----|
| **Creating new documentation** | **Generate and Write Documentation (Unified)** | **Fastest one-step workflow** |
| **Just created a doc file** | Validate Documentation (file) | Verify it meets standards |
| **Generated docs for multiple files** | Validate Documentation (changed files) | Check everything at once |
| **Before committing to git** | Validate Documentation (changed files) | Catch issues before pushing |
| **Team lead doing weekly review** | Validate Documentation (all in docs/) | Overall health check |
| **Refactored code** | Validate Traceability | Ensure docs match code |
| **Enforcing documentation standards** | Scan Write Bypasses | Prevent workarounds |
| **Preview template before generating** | Scaffold New Documentation | See template structure first (optional) |

---

## 🎯 Beginner Workflow Example

**Scenario:** You're documenting 3 new backend services (NEW UNIFIED WORKFLOW)

```
Step 1: Generate documentation for all 3 in one command each
  → Run "AKR: Generate and Write Documentation (Unified)" × 3
  → Enter: EnrollmentService, CourseService, UserService
  → Each creates complete doc file with full template structure

Step 2: Review and enhance
  → Open each file and replace ❓ placeholders
  → Add business rules, What & Why, architectural details
  → Fill in human-required context

Step 3: Validate your work
  → Run "AKR: Validate Documentation (changed files)"
  → Shows which docs need improvement

Step 4: Fix any issues
  → Address validation feedback
  → Ensure all required sections are complete

Step 5: Final check before commit
  → Run "AKR: Validate Documentation (changed files)" again
  → Confirms all 3 files are ready
  → Commit to git and create PR
```

**Total time:** 15-20 minutes for 3 services (faster than old workflow)

---

## 🆚 Old vs. New Workflow Comparison

### Old Workflow (3 steps per file):
```
1. Run "AKR: Scaffold New Documentation"
   → Creates template file with placeholders
   
2. Open Copilot Chat
   → Ask: "Generate docs for EnrollmentService"
   → Copilot reads scaffold and fills content
   
3. Review and validate
   → Check generated content
   → Run validation tasks
```
**Time:** 20-30 minutes for 3 files

### New Unified Workflow (1 step per file):
```
1. Run "AKR: Generate and Write Documentation (Unified)"
   → Auto-detects project type
   → Generates full template with placeholders
   → Writes and validates file immediately
   → Returns validation results
   
2. Review and enhance
   → Replace ❓ placeholders with context
   → Run validation tasks
```
**Time:** 15-20 minutes for 3 files (25-30% faster)

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
- [ ] Run **AKR: Validate Documentation (changed files)**

### Documentation Workflow (Per project)
- [ ] **RECOMMENDED:** Run **AKR: Generate and Write Documentation (Unified)** for one-step generation, OR
- [ ] **ALTERNATIVE:** Run **AKR: Scaffold New Documentation** to create template first (legacy workflow)
- [ ] If using legacy: Use Copilot Chat to generate/enhance content
- [ ] Review generated files and replace ❓ placeholders with human context
- [ ] Run **AKR: Validate Documentation (changed files)** to check quality
- [ ] Fix any compliance issues identified by validation
- [ ] Run **AKR: Scan Write Bypasses** to ensure proper workflow (optional)
- [ ] Commit documentation to git

### New Repository Setup (Per codebase)
- [ ] Open repository in VS Code
- [ ] Create `.vscode/mcp.json` with absolute paths
- [ ] Copy `.akr-config.json` template
- [ ] Customize config for your project
- [ ] Reload VS Code window
- [ ] Run **AKR: Validate Documentation (changed files)**

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

## � Jinja2 Custom Filters Quick Lookup

When building or modifying AKR templates, use these custom filters to format documentation content.

**Quick Reference** (detailed docs in [DEVELOPER_REFERENCE.md](DEVELOPER_REFERENCE.md#custom-filters)):

| Filter | Input | Output | Example |
|--------|-------|--------|---------|
| `yes_no` | Boolean | "Yes" or "No" | `{{ has_auth \| yes_no }}` → "Yes" |
| `required_nullable` | Boolean | "Required" or "Optional" | `{{ field.required \| required_nullable }}` → "Required" |
| `title_case` | String | Title Cased Text | `{{ "payment service" \| title_case }}` → "Payment Service" |
| `http_method_color` | Method | Colored Badge | `{{ 'GET' \| http_method_color }}` → "🟢 GET" |
| `join_list` | List | Formatted Lines | `{{ deps \| join_list(separator=", ") }}` → "Dep1, Dep2, Dep3" |
| `code_block` | Text | Code Block | `{{ code \| code_block(language="csharp") }}` → `` ```csharp ... ``` `` |
| `truncate_smart` | Text | Truncated Text | `{{ long_text \| truncate_smart(100) }}` → "Text..." |
| `default_if_empty` | Any | Text or Default | `{{ empty \| default_if_empty("N/A") }}` → "N/A" |

**Usage Example:**
```jinja2
{{ 'POST' | http_method_color }}         {# Output: 🔵 POST #}
{{ "user service" | title_case }}        {# Output: User Service #}
{{ dependencies | join_list }}           {# Output: Dep1, Dep2, Dep3 #}
{{ content | truncate_smart(80) }}       {# Output: Long text truncated... #}
```

---

## 🐛 Troubleshooting Quick Links

| Problem | Check First | Solution |
|---------|------------|----------|
| ❓ placeholders not auto-filled | Is extraction happening? | See [No Auto-Extraction](#no-auto-extraction) below |
| 🤖 markers showing incorrectly | Template rendering issue | See [DEVELOPER_REFERENCE.md - Template System](DEVELOPER_REFERENCE.md#template-system--jinja2) |
| Validation error: "Missing section" | Check section name spelling | See [DEVELOPER_REFERENCE.md - Validation Errors](DEVELOPER_REFERENCE.md#validation-errors) |
| "Can't connect to MCP server" | Is Python process running? | See [MCP Server Not Connecting](#mcp-server-not-connecting) |
| Documentation too incomplete (< 80%) | Fill placeholder sections | See [WORKFLOWS_BY_PROJECT_TYPE.md - Understanding Markers](WORKFLOWS_BY_PROJECT_TYPE.md#understanding-markers) |

### No Auto-Extraction

**Symptoms:** 🤖 markers missing, only ❓ placeholders shown

**Causes & Fixes:**
1. **Code not scanned** — Ensure service is public, follows naming (ServiceName, Controller, etc.)
2. **Wrong language** — Extractor set wrong language in mcp.json
3. **Missing XML docs** — Add `/// <summary>` comments to methods (C#)
4. **No JSDoc comments** — Add `/** description */` to components (TypeScript)

**Solution:**
```bash
# Debug extraction
python scripts/test_extraction.py --service YourService --debug
# Check logs for "Extraction failed" or "Pattern not matched"
```

### MCP Server Not Connecting

**Symptoms:** "No MCP servers available" in Copilot Chat

**Causes & Fixes:**
1. **Server not running** — Check Windows processes, MCP tab in Output
2. **Wrong config path** — mcp.json should be in workspace root
3. **Invalid JSON** — Use `"servers"` not `"mcpServers"`, check syntax
4. **Port conflict** — Python process killed, VS Code not recognizing new start

**Solution:**
```powershell
# 1. Kill any existing Python processes
Stop-Process -Name python -Force

# 2. Reload VS Code window
# Ctrl+Shift+P → "Developer: Reload Window"

# 3. Check MCP Output panel
# View → Output → Select "MCP" or "GitHub Copilot Chat" dropdown
# Should see "Server started" message

# 4. If still not connecting:
# Try explicit start in terminal
cd akr-mcp-server
python src/server.py  # Should show "MCP server started" and NOT error out
```

### Validation Failures

**Error: "Section order incorrect"**
- ✅ Check section sequence matches template  
- ✅ Use Copilot to regenerate with `generate_documentation` tool
- ✅ Reference: [DEVELOPER_REFERENCE.md - Validation Errors](DEVELOPER_REFERENCE.md#validation-errors)

**Error: "Completeness < 80%"**
- ✅ Too many ❓ sections unfilled
- ✅ Fill in all placeholders or use `generate_documentation` again with more source code
- ✅ Reference: [WORKFLOWS_BY_PROJECT_TYPE.md - Understanding Markers](WORKFLOWS_BY_PROJECT_TYPE.md#understanding-markers)

---

## �🎯 Common Tasks

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

### Health Check Prompt Not Working
- ✅ Use Copilot Chat with a short prompt: "Run AKR MCP health check"
- ✅ Confirm MCP server is running in the Output panel

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
| [README.md](README.md) | 🎯 Main entry point - start here |
| [INSTALLATION_AND_SETUP.md](INSTALLATION_AND_SETUP.md) | Getting AKR-MCP-Server running on your machine |
| [WORKFLOWS_BY_PROJECT_TYPE.md](WORKFLOWS_BY_PROJECT_TYPE.md) | Step-by-step guide for your project type (API, UI, Database, Monorepo) |
| [DEVELOPER_REFERENCE.md](DEVELOPER_REFERENCE.md) | Architecture, APIs, integration points (for developers extending the system) |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, components, technology decisions |
| [_archived/README.md](_archived/README.md) | Historical phase documentation (design, implementation history) |

---

## 📞 Get Help

**For setup issues:** See [INSTALLATION_AND_SETUP.md](INSTALLATION_AND_SETUP.md)  
**For how-to guides:** See [WORKFLOWS_BY_PROJECT_TYPE.md](WORKFLOWS_BY_PROJECT_TYPE.md)  
**For technical details:** See [DEVELOPER_REFERENCE.md](DEVELOPER_REFERENCE.md)  
**For troubleshooting:** See [Troubleshooting Quick Links](#troubleshooting-quick-links) above  

Team Lead: _________________________  
AKR Team Contact: _________________________  
IT Support: _________________________  

---

**Last Updated:** 2026-02-19  
**Version:** 2.0 - Major consolidation with Jinja2 filters + troubleshooting quick links
