# Quick Start: Database Repository Setup

> **Time Required:** 5 minutes  
> **For:** SQL Tables, Views, Stored Procedures, Functions

---

## 🎯 Two Database Scenarios

### Scenario A: Separate Database Repository
You have a dedicated repository for database objects (tables, views, stored procedures).

### Scenario B: Database Folder in API Repository
Your database objects live in a folder within your Backend/API repository.

**Choose the appropriate section below** based on your scenario.

---

## ✅ Prerequisites

- ☑️ AKR MCP server already installed on your machine
- ☑️ VS Code installed
- ☑️ GitHub Copilot Chat extension enabled

**First time?** Go to [First-Time Installation Guide](FIRST_TIME_INSTALL.md) first.

---

## 📝 Scenario A: Separate Database Repository

### Step 1: Open Your Database Repository in VS Code

```powershell
# Navigate to your database repository
cd "C:\path\to\your-database-repo"

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

**If example file exists:**
```powershell
# Try copying database config template
Copy-Item "c:\Users\E1481541\OneDrive - Emerson\Documents\CDS - Team Hawkeye\AKR with MCP\core-akr-templates\.akr\examples\akr-config-webapp1-db.json" ".akr-config.json"
```

**If file doesn't exist, create manually:** (See Step 4)

---

### Step 4: Customize Configuration

Open or create `.akr-config.json` with **ALL** required fields:

```json
{
  "version": "2.0",
  "project": {
    "name": "TrainingTracker_Database",     ← Change this
    "type": "database",
    "description": "SQL Server database for Training Tracker"  ← Change this
  },
  "documentation": {
    "output_path": "docs/",
    "default_template": "table-doc"
  },
  "component_mappings": [
    {
      "source_pattern": "training/Tables/**/*.sql",
      "doc_path": "docs/tables/",
      "template": "table-doc"
    },
    {
      "source_pattern": "training/Views/**/*.sql",
      "doc_path": "docs/views/",
      "template": "embedded-database"
    },
    {
      "source_pattern": "training/StoredProcedures/**/*.sql",
      "doc_path": "docs/procedures/",
      "template": "service-standard"
    }
  ],
  "team": {
    "name": "Database Team",                 ← Change this
    "roles": {
      "tech-lead": ["db-lead@emerson.com"],               ← Update emails
      "db-developer": ["dba1@emerson.com"],              ← Update emails
      "product-owner": ["po@emerson.com"],               ← Update emails
      "qa": ["qa@emerson.com"]                            ← Update emails
    }
  }
}
```

## 🔧 What to Customize

### 1. Project Information (Required)
```json
"project": {
  "name": "YourApp_Database",
  "type": "database",
  "description": "SQL Server/PostgreSQL/Oracle database"
}
```

### 2. Component Mappings by Database Type

**SQL Server:**
```json
"component_mappings": [
  {
    "source_pattern": "Tables/**/*.sql",
    "doc_path": "docs/tables/",
    "template": "table-doc"
  },
  {
    "source_pattern": "Views/**/*.sql",
    "doc_path": "docs/views/",
    "template": "embedded-database"
  },
  {
    "source_pattern": "StoredProcedures/**/*.sql",
    "doc_path": "docs/procedures/",
    "template": "service-standard"
  }
]
```

**PostgreSQL:**
```json
"component_mappings": [
  {
    "source_pattern": "tables/**/*.sql",
    "doc_path": "docs/tables/"
  },
  {
    "source_pattern": "functions/**/*.sql",
    "doc_path": "docs/functions/"
  }
]
```

### 3. Team Roles (Required) ⚠️
**Update with your team's actual email addresses:**
```json
"team": {
  "name": "Database Team",
  "roles": {
    "tech-lead": ["jane.dba@emerson.com"],
    "db-developer": ["john.dev@emerson.com"],
    "product-owner": ["bob.manager@emerson.com"],
    "qa": ["sue.tester@emerson.com"]
  }
}
```

### 💡 Pro Tip: Let Copilot Validate Your Mappings

Instead of manually checking database folders, ask Copilot:

```
Analyze my database project's folder structure and validate the 
component_mappings section in .akr-config.json. Update it to match 
the actual SQL file organization (Tables, Views, Stored Procedures, 
Functions, etc.). Keep all other config unchanged.
```

Copilot will:
- ✅ Detect your database platform's folder structure
- ✅ Create patterns for all SQL object types
- ✅ Organize docs by object category
- ✅ Preserve your team settings

---

### Step 5: Plan Your Documentation Strategy (Recommended)

**Before generating docs**, ask Copilot to analyze your database schema:

```
Analyze this database project's schema relationships and dependencies. 
I need to generate documentation using AKR MCP server. Provide:

1. Table dependency hierarchy (parent tables vs child tables with FKs)
2. Core domain tables vs lookup/reference tables
3. Recommended documentation order (document referenced tables before 
   tables with foreign keys)
4. Logical batches by domain (e.g., User domain, Order domain)
5. Critical tables vs audit/logging tables

Format as a numbered list with SQL file paths.
```

**Why this helps:**
- 🔗 Understand foreign key relationships
- 📄 Document parent tables before child tables
- 📦 Group by business domain for cohesive docs
- 🔑 Prioritize core tables over lookup tables

**Example Copilot Response:**
```
Documentation Strategy:

1. CORE/REFERENCE TABLES (Document First)
   - training/Tables/Users.sql
   - training/Tables/Departments.sql
   - training/Tables/CourseCategories.sql

2. DOMAIN TABLES (Document Second)
   Batch A - Course Management:
   - training/Tables/Courses.sql (FK to CourseCategories)
   - training/Tables/CourseModules.sql (FK to Courses)
   
   Batch B - Enrollment:
   - training/Tables/Enrollments.sql (FK to Users, Courses)
   - training/Tables/Progress.sql (FK to Enrollments)

3. VIEWS (Document Third)
   - training/Views/vw_UserEnrollments.sql
   - training/Views/vw_CourseStatistics.sql

4. STORED PROCEDURES (Document Last)
   - training/StoredProcedures/usp_EnrollUser.sql
   - training/StoredProcedures/usp_GetUserProgress.sql
```

Now you can use `/docs.generate` following this schema!

---

### Step 6: Reload VS Code

1. Press `Ctrl+Shift+P`
2. Type: **"Developer: Reload Window"**
3. Press Enter

---

### Step 6: Test the Connection

Open Copilot Chat (`Ctrl+Shift+I`) and type:

```
/docs.health-check
```

**Expected Response:**
```
✅ AKR MCP Server - Health Check

Server Status: Running
Templates Available: 10
Workspace: Your-Database-Repo-Name
Configuration: Loaded
```

---

## 📝 Scenario B: Database Folder in API Repository

**If your database objects are in a folder within your API repository** (e.g., `MyAPI/Database/`), you only need to update `.akr-config.json` - no separate MCP config needed.

### Step 1: Update Existing `.akr-config.json`

If you already set up your API repository, add database path mappings to your existing `.akr-config.json`:

```json
{
  "version": "2.0",
  "repository": {
    "name": "TrainingTracker_API",
    "type": "api",
    "language": "csharp"
  },
  "documentation": {
    "outputPath": "docs/",
    "pathMappings": {
      "Domain/Services/**/*.cs": "docs/services/{name}.md",
      "Controllers/**/*.cs": "docs/api/{name}.md",
      
      "Database/Tables/**/*.sql": "docs/database/tables/{name}.md",
      "Database/Views/**/*.sql": "docs/database/views/{name}.md",
      "Database/StoredProcedures/**/*.sql": "docs/database/procedures/{name}.md"
    }
  }
}
```

**Key addition:** Database path mappings under `pathMappings`.

---

### Step 2: Reload VS Code

1. Press `Ctrl+Shift+P`
2. Type: **"Developer: Reload Window"**
3. Press Enter

---

### Step 3: Test Documentation Generation

```
/docs.generate Database/Tables/Courses.sql
```

Documentation will be created in `docs/database/tables/Courses.md`.

---

## 🎉 You're Ready! Now What?

### Generate Documentation for a Table

1. **Open a table file** (e.g., `training/Tables/Courses.sql`)
2. **In Copilot Chat, type:**
   ```
   /docs.generate training/Tables/Courses.sql
   ```

3. **Wait for documentation to be generated** in `docs/tables/Courses.md`

---

### Generate Documentation for a View

```
/docs.generate training/Views/vw_ActiveCourses.sql
```

Documentation will be created in `docs/views/vw_ActiveCourses.md`

---

### Generate Documentation for a Stored Procedure

```
/docs.generate training/StoredProcedures/sp_EnrollStudent.sql
```

Documentation will be created in `docs/procedures/sp_EnrollStudent.md`

---

### See Available Templates

```
/docs.list-templates
```

Shows all 10 documentation templates you can use.

---

### Interactive Documentation Assistant

Need help filling in business context?

```
/docs.interview training/Tables/Courses.sql
```

The assistant will ask you questions about:
- Business purpose of the table/view
- Key relationships and foreign keys
- Data retention policies
- Access patterns and indexes
- Known performance considerations

---

## 📚 Common Database Objects

| Object Type | Where to Find | Generate Command Example |
|-------------|--------------|--------------------------|
| **Tables** | `Tables/` or `training/Tables/` | `/docs.generate Tables/Users.sql` |
| **Views** | `Views/` or `training/Views/` | `/docs.generate Views/vw_ActiveUsers.sql` |
| **Stored Procedures** | `StoredProcedures/` | `/docs.generate StoredProcedures/sp_GetUserById.sql` |
| **Functions** | `Functions/` | `/docs.generate Functions/fn_CalculateAge.sql` |
| **Triggers** | `Triggers/` | `/docs.generate Triggers/trg_AuditUpdate.sql` |

---

## 💡 Pro Tips

### Document Table Relationships

When documenting tables, the AKR server automatically:
- ✅ Identifies primary keys
- ✅ Lists foreign key relationships
- ✅ Documents column types and constraints
- ✅ Identifies indexes

**You should add:**
- **Why** certain constraints exist (business rules)
- **When** data is archived or purged
- **How** the table fits in the overall data model
- **What** external systems interact with this table

---

### Document Complex Views

When documenting views:
- Explain the **business purpose** of the view
- Document **performance considerations** (indexed views?)
- List **which reports/APIs** use this view
- Note **refresh schedule** (if materialized)

---

### Document Stored Procedures

Focus on:
- **Why** this procedure exists (business logic)
- **What** edge cases it handles
- **Who** calls this procedure (apps, jobs, users)
- **Performance** characteristics (long-running?)

---

## ❓ Need Help?

- **MCP server not connecting?** → [Troubleshooting Guide](TROUBLESHOOTING.md)
- **Want to document multiple tables?** → Ask in Copilot Chat: "How do I batch generate documentation?"
- **Questions?** → Contact the AKR team

---

## 🔄 Next Steps

1. Generate documentation for core tables
2. Document important views and procedures
3. Review and customize generated docs
4. Commit documentation to your repository
5. Set up another repository? Choose from:
   - [API Repository Setup](QUICK_START_API_REPO.md)
   - [UI Repository Setup](QUICK_START_UI_REPO.md)

---

**Last Updated:** January 23, 2026
