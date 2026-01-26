# Quick Start: Monorepo Setup

> **Time Required:** 5-10 minutes  
> **For:** Single repository containing UI, API, and Database together

---

## 📦 What is a Monorepo?

A **monorepo** (monolithic repository) contains multiple projects in one repository, typically organized like:

```
MyApp/
├── packages/
│   ├── ui/              ← Frontend code
│   ├── api/             ← Backend code
│   └── database/        ← Database scripts
├── shared/              ← Shared utilities
└── docs/                ← Generated documentation
```

**Common in:** Legacy applications, Nx workspaces, Lerna projects, Turborepo setups

---

## ✅ Prerequisites

- ☑️ AKR MCP server already installed on your machine
- ☑️ VS Code installed
- ☑️ GitHub Copilot Chat extension enabled

**First time?** Go to [First-Time Installation Guide](FIRST_TIME_INSTALL.md) first.

---

## 📝 Step-by-Step Setup

### Step 1: Open Your Monorepo in VS Code

```powershell
# Navigate to your monorepo root
cd "C:\path\to\your-monorepo"

# Open in VS Code
code .
```

---

### Step 2: Create MCP Configuration File

Create a new file: `.vscode/mcp.json` **at the monorepo root**

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
# Copy monorepo configuration template
Copy-Item "c:\Users\E1481541\OneDrive - Emerson\Documents\CDS - Team Hawkeye\AKR with MCP\core-akr-templates\.akr\examples\akr-config-monorepo.json" ".akr-config.json"
```

**If file doesn't exist, create manually:** (See Step 4)

---

### Step 4: Customize Configuration

Open `.akr-config.json` and update **ALL** of these fields:

```json
{
  "version": "2.0",
  "repository": {
    "name": "TrainingTracker_Monorepo",      ← Change this
    "type": "monorepo",
    "language": "multi",
    "packages": ["ui", "api", "database"]    ← List your packages
  },
  "documentation": {
    "outputPath": "docs/",
    "pathMappings": {
      "packages/ui/src/components/**/*.tsx": "docs/ui/components/{name}.md",
      "packages/api/Services/**/*.cs": "docs/api/services/{name}.md",
      "packages/database/Tables/**/*.sql": "docs/database/tables/{name}.md"
    }
  },
  "team": {
    "roles": {
      "tech-lead": ["tech-lead@emerson.com"],              ← Update emails
      "ui-developer": ["ui-dev@emerson.com"],             ← Update emails
      "api-developer": ["api-dev@emerson.com"],           ← Update emails
      "db-developer": ["db-dev@emerson.com"],             ← Update emails
      "product-owner": ["po@emerson.com"],                ← Update emails
      "qa": ["qa@emerson.com"]                             ← Update emails
    }
  },
  "validation": {
    "enforceOrganizationMandatory": true,
    "completenessThreshold": 85,                          ← Adjust if needed
    "packageSpecificRules": {
      "ui": {
        "requiredSections": ["Accessibility", "Performance"]
      },
      "api": {
        "requiredSections": ["Security", "Monitoring"]
      }
    }
  }
}
```

## 🔧 What to Customize

### 1. Repository Information (Required)
```json
"repository": {
  "name": "YourApp_Monorepo",
  "type": "monorepo",
  "language": "multi",
  "packages": ["ui", "api", "database", "shared"]
}
```

### 2. Team Roles by Package (Required) ⚠️
**Monorepos need team assignments per package:**
```json
"team": {
  "roles": {
    "tech-lead": ["jane.lead@emerson.com"],
    "ui-developer": ["john.ui@emerson.com", "alice.ui@emerson.com"],
    "api-developer": ["bob.api@emerson.com", "carol.api@emerson.com"],
    "db-developer": ["dave.db@emerson.com"],
    "product-owner": ["eve.po@emerson.com"],
    "qa": ["frank.qa@emerson.com"]
  }
}
```

**Why different roles:** In monorepos, developers often specialize by package.

### 3. Package-Specific Validation (Optional)
```json
"validation": {
  "packageSpecificRules": {
    "ui": {
      "requiredSections": ["Accessibility", "Performance"]
    },
    "api": {
      "requiredSections": ["Security", "Monitoring"]
    },
    "database": {
      "requiredSections": ["Indexes", "Data Lifecycle"]
    }
  }
}
```

### 💡 Pro Tip: Let Copilot Validate Your Monorepo Mappings

For complex monorepos, ask Copilot:

```
Analyze my monorepo's multi-package folder structure (packages/*, apps/*, 
libs/*, etc.) and validate the component_mappings section in 
.akr-config.json. Update it to cover all packages with appropriate 
patterns for each package type (UI, API, shared libraries). Keep all 
other config unchanged.
```

Copilot will:
- ✅ Discover all packages/workspaces (Nx, Lerna, Turborepo, pnpm)
- ✅ Create per-package patterns with correct file extensions
- ✅ Organize docs by package and component type
- ✅ Preserve package-specific validation rules

**Especially helpful for:**
- Large monorepos with 10+ packages
- Mixed-language monorepos (TypeScript + C# + Python)
- Nested workspace structures

---

### Step 5: Plan Your Documentation Strategy (Recommended)

**Before generating docs**, ask Copilot to analyze your monorepo structure:

```
Analyze this monorepo's multi-package architecture and cross-package 
dependencies. I need to generate documentation using AKR MCP server. Provide:

1. Package dependency graph (which packages depend on others)
2. Shared/core packages vs feature packages
3. Recommended documentation order (document shared libraries first, then 
   packages that consume them)
4. Logical batches by package and domain
5. Public packages vs internal packages

Format as a numbered list with package names and key file paths.
```

**Why this helps:**
- 📦 Understand cross-package dependencies
- 🔗 Document shared libs before consuming packages
- 🏗️ Group by package for maintainability
- 🔑 Prioritize public APIs over internal packages

**Example Copilot Response:**
```
Documentation Strategy:

1. SHARED LIBRARIES (Document First)
   Package: @myapp/common
   - packages/common/src/types/User.ts
   - packages/common/src/utils/validation.ts
   
   Package: @myapp/ui-components
   - packages/ui-components/src/Button.tsx
   - packages/ui-components/src/Input.tsx

2. BACKEND SERVICES (Document Second)
   Package: @myapp/api
   Batch A - Core Services:
   - packages/api/src/services/UserService.cs
   - packages/api/src/services/AuthService.cs
   
   Batch B - Controllers:
   - packages/api/src/controllers/UserController.cs

3. FRONTEND APPS (Document Third)
   Package: @myapp/web
   - packages/web/src/pages/Dashboard.tsx
   - packages/web/src/components/UserProfile.tsx
   
   Package: @myapp/admin
   - packages/admin/src/pages/AdminDashboard.tsx

4. DATABASE/INFRASTRUCTURE (Document Last)
   Package: @myapp/database
   - packages/database/tables/Users.sql
```

**Pro Tip for Monorepos:** Document one complete package at a time rather than mixing files from different packages.

---

## 🎯 What to Customize

### 1. Repository Name

```json
"name": "YourApp_Monorepo"
```

Change to your actual project name.

---

### 2. Package List

```json
"packages": ["ui", "api", "database", "shared"]
```

List all your package folders. Common packages:
- `ui` or `frontend`
- `api` or `backend` or `server`
- `database` or `db`
- `shared` or `common`
- `mobile`

---

### 3. Path Mappings

Match your **actual folder structure**. Here are common patterns:

#### Pattern 1: Packages Folder Structure
```json
"pathMappings": {
  "packages/ui/**/*.tsx": "docs/ui/{name}.md",
  "packages/api/**/*.cs": "docs/api/{name}.md"
}
```

#### Pattern 2: Apps Folder Structure (Nx/Turborepo)
```json
"pathMappings": {
  "apps/web/**/*.tsx": "docs/web/{name}.md",
  "apps/api/**/*.ts": "docs/api/{name}.md",
  "libs/shared/**/*.ts": "docs/shared/{name}.md"
}
```

#### Pattern 3: Flat Structure
```json
"pathMappings": {
  "client/**/*.jsx": "docs/client/{name}.md",
  "server/**/*.js": "docs/server/{name}.md",
  "database/**/*.sql": "docs/database/{name}.md"
}
```

---

## 🔄 Step 5: Reload VS Code

1. Press `Ctrl+Shift+P`
2. Type: **"Developer: Reload Window"**
3. Press Enter

---

## ✅ Step 6: Test the Connection

Open Copilot Chat (`Ctrl+Shift+I`) and type:

```
/docs.health-check
```

**Expected Response:**
```
✅ AKR MCP Server - Health Check

Server Status: Running
Templates Available: 10
Workspace: Your-Monorepo-Name
Configuration: Loaded
Repository Type: monorepo
```

---

## 🎉 You're Ready! Now What?

### Generate Documentation for UI Component

```
/docs.generate packages/ui/src/components/Header.tsx
```

Documentation created in: `docs/ui/components/Header.md`

---

### Generate Documentation for API Service

```
/docs.generate packages/api/Services/UserService.cs
```

Documentation created in: `docs/api/services/UserService.md`

---

### Generate Documentation for Database Table

```
/docs.generate packages/database/Tables/Users.sql
```

Documentation created in: `docs/database/tables/Users.md`

---

### See Available Templates

```
/docs.list-templates
```

Shows all 10 documentation templates you can use.

---

## 📚 Documentation Organization

Your generated docs will be organized by package:

```
docs/
├── ui/
│   ├── components/
│   ├── pages/
│   └── services/
├── api/
│   ├── services/
│   ├── controllers/
│   └── repositories/
└── database/
    ├── tables/
    ├── views/
    └── procedures/
```

---

## 💡 Pro Tips for Monorepos

### 1. Document Shared Code First

Start by documenting shared utilities and libraries that multiple packages depend on:

```
/docs.generate shared/utils/formatDate.ts
/docs.generate libs/common/validation.ts
```

---

### 2. Use Consistent Naming

Keep documentation paths consistent with package structure:

```json
"packages/ui/src/**/*.tsx": "docs/ui/{name}.md",
"packages/api/src/**/*.cs": "docs/api/{name}.md"
```

Not:
```json
"packages/ui/src/**/*.tsx": "docs/frontend/{name}.md",  ← Confusing
"packages/api/src/**/*.cs": "docs/backend/{name}.md"
```

---

### 3. Document Cross-Package Dependencies

When documenting services or components, mention:
- **Which packages** they depend on
- **Which packages** depend on them
- **Shared interfaces** or types used

---

### 4. Batch Generate by Package

Generate documentation for an entire package:

**In Copilot Chat:**
```
Generate documentation for all services in packages/api/Services
```

Copilot will help you iterate through files.

---

## 🔍 Common Monorepo Structures

### Nx Workspace
```json
{
  "pathMappings": {
    "apps/web/src/**/*.tsx": "docs/web/{name}.md",
    "apps/api/src/**/*.ts": "docs/api/{name}.md",
    "libs/ui/**/*.tsx": "docs/libs/ui/{name}.md",
    "libs/data/**/*.ts": "docs/libs/data/{name}.md"
  }
}
```

### Turborepo
```json
{
  "pathMappings": {
    "apps/web/**/*.tsx": "docs/apps/web/{name}.md",
    "apps/docs/**/*.mdx": "docs/apps/docs/{name}.md",
    "packages/ui/**/*.tsx": "docs/packages/ui/{name}.md",
    "packages/config/**/*.ts": "docs/packages/config/{name}.md"
  }
}
```

### Lerna
```json
{
  "pathMappings": {
    "packages/client/**/*.jsx": "docs/client/{name}.md",
    "packages/server/**/*.js": "docs/server/{name}.md",
    "packages/shared/**/*.js": "docs/shared/{name}.md"
  }
}
```

---

## ❓ Need Help?

- **MCP server not connecting?** → [Troubleshooting Guide](TROUBLESHOOTING.md)
- **Want to document entire packages?** → Ask in Copilot Chat: "How do I batch generate docs for a package?"
- **Questions?** → Contact the AKR team

---

## 🔄 Next Steps

1. Generate documentation for shared/common code first
2. Document each package systematically (UI → API → Database)
3. Review and customize generated docs
4. Add cross-references between packages
5. Commit documentation to your repository

---

**Last Updated:** January 23, 2026
