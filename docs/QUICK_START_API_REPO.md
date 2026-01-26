# Quick Start: API/Backend Repository Setup

> **Time Required:** 5 minutes  
> **For:** REST APIs, Services, Controllers (C#, Java, Node.js, Python)

---

## ✅ Prerequisites

- ☑️ AKR MCP server already installed on your machine
- ☑️ VS Code installed
- ☑️ GitHub Copilot Chat extension enabled

**First time?** Go to [First-Time Installation Guide](FIRST_TIME_INSTALL.md) first.

---

## 📝 Step-by-Step Setup

### Step 1: Open Your API Repository in VS Code

```powershell
# Navigate to your API/Backend repository
cd "C:\path\to\your-api-repo"

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
# Copy API configuration template
Copy-Item "c:\Users\E1481541\OneDrive - Emerson\Documents\CDS - Team Hawkeye\AKR with MCP\core-akr-templates\.akr\examples\akr-config-webapp1-api.json" ".akr-config.json"
```

---

### Step 4: Customize Configuration

Open `.akr-config.json` and update **ALL** of these fields:

```json
{
  "version": "2.0",
  "project": {
    "name": "TrainingTracker_API",           ← Change this
    "type": "backend",
    "description": ".NET Core API for Training Tracker"  ← Change this
  },
  "documentation": {
    "output_path": "docs/",
    "default_template": "service-standard"
  },
  "component_mappings": [
    {
      "source_pattern": "src/Controllers/**/*.cs",
      "doc_path": "docs/api/",
      "template": "service-standard"
    },
    {
      "source_pattern": "src/Services/**/*.cs",
      "doc_path": "docs/services/",
      "template": "service-standard"
    },
    {
      "source_pattern": "src/Repositories/**/*.cs",
      "doc_path": "docs/data-access/",
      "template": "service-standard"
    }
  ],
  "team": {
    "name": "Backend Team",                   ← Change this
    "roles": {
      "tech-lead": ["your-tech-lead@emerson.com"],           ← Update emails
      "developer": ["dev1@emerson.com", "dev2@emerson.com"], ← Update emails
      "product-owner": ["po@emerson.com"],                   ← Update emails
      "qa": ["qa@emerson.com"]                                ← Update emails
    }
  },
  "validation": {
    "required_sections": true,
    "transparency_markers": true,
    "completeness_threshold": 75              ← Adjust if needed (0-100)
  }
}
```

## 🔧 What to Customize

### 1. Project Information (Required)
```json
"project": {
  "name": "YourApp_API",                     ← Your project name
  "type": "backend",                         ← Keep as "backend"
  "description": "Brief description"         ← Describe your API
}
```

### 2. Component Mappings (Required)
Match your **actual folder structure**:

**C# .NET:**
```json
"source_pattern": "src/Controllers/**/*.cs",
"doc_path": "docs/api/"
```

**Node.js/TypeScript:**
```json
"source_pattern": "src/controllers/**/*.ts",
"doc_path": "docs/api/"
```

**Java Spring:**
```json
"source_pattern": "src/main/java/**/controller/**/*.java",
"doc_path": "docs/api/"
```

**Python Flask:**
```json
"source_pattern": "routes/**/*.py",
"doc_path": "docs/api/"
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
- Contact information in generated docs

### 4. Validation Settings (Optional)
```json
"validation": {
  "completeness_threshold": 75    ← 0-100, higher = stricter
}
```

**Recommended thresholds:**
- **75-80:** Balanced (recommended for most teams)
- **85-90:** Strict (for critical systems)
- **60-70:** Relaxed (for rapid prototyping)

### 💡 Pro Tip: Let Copilot Validate Your Mappings

Instead of manually checking folders, ask Copilot:

```
Analyze my project's folder structure and validate the component_mappings 
section in .akr-config.json. Update it to match the actual source code 
organization (Controllers, Services, Repositories, etc.), ensuring all 
files are covered. Keep all other config unchanged.
```

Copilot will:
- ✅ Detect your framework's folder conventions (ASP.NET, Express, Spring, etc.)
- ✅ Create accurate file patterns (*.cs, *.ts, *.java, *.py)
- ✅ Suggest appropriate templates for each component type
- ✅ Preserve your team and validation settings

---

### Step 5: Plan Your Documentation Strategy (Recommended)

**Before generating docs**, ask Copilot to analyze your architecture:

```
Analyze this API project's layered architecture and service dependencies. 
I need to generate documentation using AKR MCP server. Provide:

1. Architecture layers (Controllers → Services → Repositories → Models)
2. Service dependencies (which services call others)
3. Recommended documentation order (document data layer first, then business 
   logic, then API endpoints)
4. Logical batches by feature/domain (e.g., User module, Order module)
5. Critical endpoints vs internal services

Format as a numbered list with file paths.
```

**Why this helps:**
- 🏛️ Understand layered architecture (data → business → presentation)
- 🔗 Document dependencies before consumers
- 📦 Group by domain/feature for cohesive docs
- 🔑 Prioritize public APIs over internal utilities

**Example Copilot Response:**
```
Documentation Strategy:

1. DATA LAYER (Document First)
   - src/Models/User.cs
   - src/Repositories/UserRepository.cs
   - src/Data/AppDbContext.cs

2. BUSINESS LOGIC (Document Second)
   Batch A - User Domain:
   - src/Services/UserService.cs
   - src/Services/AuthService.cs
   
   Batch B - Order Domain:
   - src/Services/OrderService.cs
   - src/Services/PaymentService.cs

3. API ENDPOINTS (Document Third)
   - src/Controllers/UserController.cs
   - src/Controllers/OrderController.cs

4. MIDDLEWARE/UTILITIES (Document Last)
   - src/Middleware/AuthMiddleware.cs
   - src/Utils/ResponseHelper.cs
```

Now you can use `/docs.generate` following this architecture!

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
Workspace: Your-API-Repo-Name
Configuration: Loaded
```

If you see a long response instead, see [Troubleshooting Guide](TROUBLESHOOTING.md#health-check-not-working).

---

## 🎉 You're Ready! Now What?

### Generate Documentation for a Service

1. **Open a service file** (e.g., `Domain/Services/EnrollmentService.cs`)
2. **In Copilot Chat, type:**
   ```
   /docs.generate Domain/Services/EnrollmentService.cs
   ```

3. **Wait for documentation to be generated** in `docs/services/EnrollmentService.md`

---

### Generate Documentation for a Controller

```
/docs.generate Controllers/EnrollmentsController.cs
```

Documentation will be created in `docs/api/EnrollmentsController.md`

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
/docs.interview Domain/Services/EnrollmentService.cs
```

The assistant will ask you questions about:
- Business rules and why they exist
- Performance considerations
- Known limitations
- Integration points

---

## 📚 Common API File Types

| File Type | Where to Find | Generate Command Example |
|-----------|--------------|--------------------------|
| **Services** | `Services/` or `src/services/` | `/docs.generate Services/UserService.cs` |
| **Controllers** | `Controllers/` or `src/controllers/` | `/docs.generate Controllers/UsersController.cs` |
| **Repositories** | `Repositories/` or `src/repositories/` | `/docs.generate Repositories/UserRepository.cs` |
| **Models/DTOs** | `Models/` or `src/models/` | `/docs.generate Models/User.cs` |
| **Middleware** | `Middleware/` | `/docs.generate Middleware/AuthMiddleware.cs` |

---

## 💡 Pro Tips

### Document Your API Endpoints

When documenting controllers, the AKR server automatically:
- ✅ Extracts HTTP methods (GET, POST, PUT, DELETE)
- ✅ Documents route parameters
- ✅ Lists request/response models
- ✅ Identifies authentication requirements

### Document Business Logic

When documenting services, focus on:
- **Why** certain business rules exist
- **When** to use this service vs. others
- **What** external dependencies it has
- **How** errors are handled

---

## ❓ Need Help?

- **MCP server not connecting?** → [Troubleshooting Guide](TROUBLESHOOTING.md)
- **Want to document multiple files?** → Ask in Copilot Chat: "How do I batch generate documentation?"
- **Questions?** → Contact the AKR team

---

## 🔄 Next Steps

1. Generate documentation for core services
2. Document API controllers
3. Review and customize generated docs
4. Commit documentation to your repository
5. Set up another repository? Choose from:
   - [UI Repository Setup](QUICK_START_UI_REPO.md)
   - [Database Repository Setup](QUICK_START_DATABASE_REPO.md)

---

**Last Updated:** January 23, 2026
