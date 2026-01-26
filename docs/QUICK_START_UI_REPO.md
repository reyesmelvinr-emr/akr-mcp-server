# Quick Start: UI/Frontend Repository Setup

> **Time Required:** 5 minutes  
> **For:** React, Angular, Vue, or any frontend codebase

---

## ✅ Prerequisites

- ☑️ AKR MCP server already installed on your machine
- ☑️ VS Code installed
- ☑️ GitHub Copilot Chat extension enabled

**First time?** Go to [First-Time Installation Guide](FIRST_TIME_INSTALL.md) first.

---

## 📝 Step-by-Step Setup

### Step 1: Open Your UI Repository in VS Code

```powershell
# Navigate to your UI/Frontend repository
cd "C:\path\to\your-ui-repo"

# Open in VS Code
code .
```

---

### Step 2: Create MCP Configuration File

Create a new file: `.vscode/mcp.json`

```powershell
# Create .vscode folder
New-Item -ItemType Directory -Path ".vscode" -Force
```

**Copy this content into `.vscode/mcp.json`:**

```json
{
    "servers": {
        "akr-documentation-server": {
            "type": "stdio",
            "command": "python",
            "args": [
                "c:\\Users\\E1481541\\OneDrive - Emerson\\Documents\\CDS - Team Hawkeye\\AKR with MCP\\akr-mcp-server\\src\\server.py"
            ],
            "env": {
                "PYTHONPATH": "c:\\Users\\E1481541\\OneDrive - Emerson\\Documents\\CDS - Team Hawkeye\\AKR with MCP\\akr-mcp-server\\src",
                "VSCODE_WORKSPACE_FOLDER": "${workspaceFolder}",
                "AKR_TEMPLATES_DIR": "c:\\Users\\E1481541\\OneDrive - Emerson\\Documents\\CDS - Team Hawkeye\\AKR with MCP\\core-akr-templates"
            }
        }
    }
}
```

**⚠️ Important:** Update the paths if your AKR MCP server is installed in a different location.

---

### Step 3: Copy Configuration Template

```powershell
# Copy UI configuration template
Copy-Item "c:\Users\E1481541\OneDrive - Emerson\Documents\CDS - Team Hawkeye\AKR with MCP\core-akr-templates\.akr\examples\akr-config-webapp1-ui.json" ".akr-config.json"
```

---

### Step 4: Customize Configuration

Open `.akr-config.json` and update **ALL** of these fields:

```json
{
  "version": "2.0",
  "project": {
    "name": "TrainingTracker_UI",           ← Change this
    "type": "ui",
    "description": "React/TypeScript UI for Training Tracker"  ← Change this
  },
  "documentation": {
    "output_path": "docs/",
    "default_template": "ui-component"
  },
  "component_mappings": [
    {
      "source_pattern": "src/components/**/*.tsx",
      "doc_path": "docs/components/",
      "template": "ui-component"
    },
    {
      "source_pattern": "src/services/**/*.ts",
      "doc_path": "docs/services/",
      "template": "service-standard"
    }
  ],
  "team": {
    "name": "Frontend Team",                  ← Change this
    "roles": {
      "tech-lead": ["your-tech-lead@emerson.com"],           ← Update emails
      "developer": ["dev1@emerson.com", "dev2@emerson.com"], ← Update emails
      "product-owner": ["po@emerson.com"],                   ← Update emails
      "qa": ["qa@emerson.com"]                                ← Update emails
    }
  }
}
```

## 🔧 What to Customize

### 1. Project Information (Required)
```json
"project": {
  "name": "YourApp_UI",                      ← Your project name
  "type": "ui",                              ← Keep as "ui"
  "description": "Brief description"         ← Describe your app
}
```

### 2. Component Mappings (Required)
Match your **actual folder structure**:
```json
"component_mappings": [
  {
    "source_pattern": "src/components/**/*.tsx",  ← Your actual path
    "doc_path": "docs/components/",              ← Where docs go
    "template": "ui-component"                   ← Template to use
  }
]
```

### 3. Team Roles (Required) ⚠️
**Update with your team's actual email addresses:**
```json
"team": {
  "name": "Your Team Name",
  "roles": {
    "tech-lead": ["jane.smith@emerson.com"],
    "developer": ["john.doe@emerson.com", "alice.jones@emerson.com"],
    "product-owner": ["bob.manager@emerson.com"],
    "qa": ["sue.tester@emerson.com"]
  }
}
```

**Why this matters:** Team emails are used for:
- Documentation ownership tracking
- Notification of doc updates
- Responsibility assignment

### 💡 Pro Tip: Let Copilot Validate Your Mappings

Instead of manually checking folders, ask Copilot:

```
Analyze my project's folder structure under "src" and validate the 
component_mappings section in .akr-config.json. Update it to match 
the actual folders, ensuring all source files are covered with 
appropriate doc paths and templates. Keep all other config unchanged.
```

Copilot will:
- ✅ Find all your actual source folders
- ✅ Create accurate glob patterns
- ✅ Suggest logical doc output paths
- ✅ Preserve your team and project settings

---

### Step 5: Plan Your Documentation Strategy (Recommended)

**Before generating docs**, ask Copilot to analyze your architecture:

```
Analyze this UI project's architecture and component relationships. I need 
to generate documentation using AKR MCP server. Provide:

1. Component hierarchy (core/shared components vs feature components)
2. Dependency relationships (which components use others)
3. Recommended documentation order (document foundational components first)
4. Logical batches for documentation (group related components)
5. Priority levels (critical vs nice-to-have docs)

Format as a numbered list with component paths.
```

**Why this helps:**
- 🧠 Understand the codebase architecture before documenting
- 📄 Document dependencies before dependents (logical flow)
- 📦 Group related components for batch documentation
- ⏱️ Focus on high-value components first

**Example Copilot Response:**
```
Documentation Strategy:

1. CORE/SHARED (Document First)
   - src/components/common/Button.tsx
   - src/components/common/Input.tsx
   - src/services/api-client.ts
   - src/hooks/useAuth.ts

2. FEATURES (Document Second)
   Batch A - User Management:
   - src/components/UserProfile.tsx
   - src/components/UserList.tsx
   
   Batch B - Dashboard:
   - src/pages/Dashboard.tsx
   - src/components/DashboardWidget.tsx

3. UTILITIES (Document Last)
   - src/utils/formatters.ts
   - src/utils/validators.ts
```

Now you can generate documentation in logical batches!

---

### Step 6: Reload VS Code

1. Press `Ctrl+Shift+P`
2. Type: **"Developer: Reload Window"**
3. Press Enter

---

### Step 7: Test the Connection

Open Copilot Chat (`Ctrl+Shift+I`) and type:

```
Check the AKR documentation server health
```

**Expected Response:**
```
✅ AKR MCP Server - Health Check

Server Status: Running
Templates Available: 10
Workspace: Your-UI-Repo-Name
Configuration: Loaded
```

If you see errors, see [Troubleshooting Guide](TROUBLESHOOTING.md#health-check-not-working).

---

## 🎉 You're Ready! Now What?

### ⚠️ IMPORTANT: Initialize Documentation Session First

**Before generating any documentation**, you MUST initialize a session. This creates a feature branch for your docs.

In Copilot Chat, type:

```
Initialize an AKR documentation session for this workspace and create a new feature branch
```

**What this does:**
- ✅ Creates a new branch named `docs/documentation-YYYYMMDD-HHMMSS`
- ✅ Sets up branch management
- ✅ Loads your .akr-config.json
- ✅ Prepares for documentation generation

**Expected Response:**
```
✅ Documentation session initialized

Branch: docs/documentation-20260123-143052
Workspace: training-tracker-ui
Configuration: Loaded from .akr-config.json
Ready to generate documentation!
```

**Important:** You only need to do this **once per session**. After initialization, you can generate multiple files without reinitializing.

---

### How to Generate Documentation

**Now you can generate documentation!** The AKR MCP server provides tools that Copilot uses automatically. Just ask Copilot in natural language!

#### Generate Single Component

```
Generate AKR documentation for src/components/CourseCard.tsx
```

Copilot will:
1. Initialize documentation session
2. Analyze the component code
3. Select appropriate template
4. Generate documentation
5. Save to docs/components/CourseCard.md

#### Generate Multiple Related Files (Batch)

```
Generate AKR documentation for all files in src/services/
```

**OR be more specific:**

```
Generate AKR documentation for these files:
- src/services/authService.ts  
- src/services/userService.ts
- src/services/courseService.ts
```

**Pro Tip:** Use the documentation strategy from Step 5 to batch logically!

---

### See Available Templates

```
List all AKR documentation templates
```

Shows all 10 templates with descriptions.

---

### Interactive Documentation Assistant

Need help filling in business context?

```
Start an AKR documentation interview for src/components/CourseCard.tsx
```

The assistant will ask questions about:
- Business purpose and value
- Historical context
- Team ownership
- Integration points

---

## 📚 Example Prompts by File Type

| What You Want | Example Prompt |
|---------------|----------------|
| **Single Component** | `Generate AKR documentation for src/components/Header.tsx` |
| **Single Page** | `Generate AKR documentation for src/pages/Dashboard.tsx` |
| **Single Service** | `Generate AKR documentation for src/services/apiClient.ts` |
| **All Services** | `Generate AKR documentation for all TypeScript files in src/services/` |
| **All Components** | `Generate AKR documentation for all React components in src/components/` |
| **Specific Files** | `Generate AKR documentation for Header.tsx, Footer.tsx, and Navigation.tsx` |

---

## ⚠️ Important: Batch Processing

**Generating documentation for many files at once can take time!** Here's why:

1. **Each file requires:**
   - Code analysis
   - Template selection
   - Documentation generation
   - File writing
   - Git commit

2. **Best Practices:**
   - ✅ Start with 3-5 files at a time
   - ✅ Use the documentation strategy (Step 5) to batch logically
   - ✅ Document foundational components first (shared components, utilities)
   - ✅ Then document features that use them
   - ❌ Don't try to document entire folders (10+ files) at once

3. **If processing seems stuck:**
   - Wait 30 seconds - large files take time
   - Check the terminal for progress messages
   - If truly frozen, press `Esc` and try with fewer files

---

## 🔄 After Generating Documentation

### Review Generated Docs

Check the `docs/` folder for generated documentation. Review and customize as needed.

### Create Pull Request

When you're done documenting, create a PR:

```
End the AKR documentation session and create a pull request titled "Add component documentation" with description "Generated AKR documentation for UI components"
```

This will:
- ✅ Push your docs branch to GitHub
- ✅ Create a pull request against main
- ✅ Include summary of documented files

### Or Just End Session

If you want to review locally first:

```
End the AKR documentation session
```

You can manually create the PR later using `gh pr create` or GitHub UI.

---

## ❓ Need Help?

- **MCP server not connecting?** → [Troubleshooting Guide](TROUBLESHOOTING.md)
- **Want to document multiple files?** → Ask in Copilot Chat: "How do I batch generate documentation?"
- **Questions?** → Contact the AKR team

---

## 🔄 Next Steps

1. Generate documentation for key components
2. Review and customize generated docs
3. Commit documentation to your repository
4. Set up another repository? Choose from:
   - [API Repository Setup](QUICK_START_API_REPO.md)
   - [Database Repository Setup](QUICK_START_DATABASE_REPO.md)

---

**Last Updated:** January 23, 2026
