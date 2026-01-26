# How to Generate Documentation with AKR MCP Server

## 🎯 Ensuring AKR Standards Compliance

### The Key Question
**"If we depend on natural language prompts, how do we ensure documentation follows AKR standards?"**

**Answer:** The AKR MCP server enforces standards automatically. Users only need to provide a few critical signals.

---

### Critical: What You MUST Do

#### 1. **Always Say "AKR"** 🔴 CRITICAL

This signals to Copilot to use AKR MCP tools instead of generating generic documentation.

- ✅ "Generate **AKR** documentation for src/services/UserService.ts"
- ❌ "Generate documentation for src/services/UserService.ts" ← Generic docs, no standards

**What happens:**
- With "AKR" → Copilot calls AKR MCP server → Standards enforced
- Without "AKR" → Copilot generates generic markdown → No standards

#### 2. **Provide Full File Paths** 🔴 CRITICAL

The server uses file extensions to automatically select the correct template.

- ✅ "Generate AKR documentation for **src/Services/AuthService.cs**"
- ❌ "Generate AKR documentation for the auth service"

**What the server does automatically:**
- `.cs` → Detects C# → Selects backend service template
- `.tsx` → Detects TypeScript React → Selects UI component template  
- `.sql` → Detects SQL → Selects database table template

**You don't specify the template—the server figures it out.**

#### 3. **Initialize Session for Batch Work** 🔴 CRITICAL

Before generating multiple files, always initialize a documentation session.

```
Initialize an AKR documentation session for this workspace and create a new feature branch
```

**Why this matters:**
- ✅ Creates feature branch (not main!)
- ✅ Loads your `.akr-config.json` settings
- ✅ Enables PR creation
- ✅ Proper branch management

**Do this ONCE at the start, then generate as many files as you want.**

---

### What You DON'T Need to Specify

The server handles these automatically—don't overthink it:

#### ❌ Template Details
- Server selects template based on file type
- Section structure enforced automatically
- Required sections always included

#### ❌ Formatting Standards
- Metadata blocks (`<!-- akr:metadata -->`) added automatically
- AI-generated markers applied automatically
- Heading levels enforced
- Code block formatting standardized

#### ❌ File Organization
- Output paths read from `.akr-config.json`
- Directories created as needed
- Naming conventions handled automatically

#### ❌ Version Control
- Branch management via session initialization
- Commit messages generated automatically

---

### Minimal Effective Prompts

**For single file:**
```
Generate AKR documentation for src/services/UserService.ts
```

**For batch (after session initialized):**
```
Generate AKR documentation for all TypeScript files in src/services/
```

**That's it.** The server enforces all standards automatically.

---

### When to Add More Context

Add context only when file purpose is ambiguous:

**Ambiguous filename:**
```
Generate AKR documentation for utils/helpers.ts as a shared utility module
```

**Specific component type:**
```
Generate AKR documentation for src/components/DatePicker.tsx as a reusable UI component
```

**Custom complexity:**
```
Generate comprehensive AKR documentation for src/Services/PaymentEngine.cs
```

---

### The Mental Model

**Think of the AKR MCP server as a documentation expert on your team:**

1. **You point them to code:** "Document this file"
2. **They analyze it:** Code structure, dependencies, patterns
3. **They pick the right template:** Based on what they see
4. **They generate compliant docs:** Following all AKR standards
5. **They ask for help when needed:** Business context interviews

**You tell them WHAT and WHERE. They handle HOW.**

---

### Remember These 3 Things

1. **Say "AKR"** → Triggers AKR tools
2. **Provide file paths** → Enables template selection
3. **Initialize session** → Enables branch management and PRs

**Everything else is enforced automatically.**

---

## ⚠️ Important: No Slash Commands!

**The AKR MCP server does NOT use slash commands.** It provides **tools** that Copilot uses automatically when you ask in natural language.

### ❌ Wrong (Doesn't Work)
```
/docs.generate src/components/Header.tsx
/docs.generate-batch src/services/
/docs.list-templates
/docs.health-check
```

These slash commands **do not exist** and will not work!

### ✅ Correct (Works!)
```
Generate AKR documentation for src/components/Header.tsx
Generate AKR documentation for all files in src/services/
List all AKR documentation templates
Check the AKR documentation server health
```

---

## How It Works

When you ask Copilot to generate documentation:

1. **You ask in natural language** → Copilot understands your intent
2. **Copilot calls MCP tools** → Server receives the request
3. **Server generates docs** → Uses templates, analyzes code
4. **Files are created** → Documentation saved to your project

---

## ⚠️ CRITICAL: Initialize Session First!

**Before generating ANY documentation**, you MUST initialize a documentation session. This creates a feature branch.

### Why This Matters

Without initialization:
- ❌ Docs go directly to your main branch (bad!)
- ❌ No branch management
- ❌ Config not loaded properly
- ❌ Can't create PRs

With initialization:
- ✅ Creates feature branch (`docs/documentation-TIMESTAMP`)
- ✅ Loads your .akr-config.json
- ✅ Sets up branch management
- ✅ Enables PR creation

### Initialize a Session

```
Initialize an AKR documentation session for this workspace and create a new feature branch
```

**Expected Response:**
```
✅ Documentation session initialized

Branch: docs/documentation-20260123-143052
Workspace: your-repo-name
Configuration: Loaded from .akr-config.json
Ready to generate documentation!
```

**You only do this ONCE** at the start of your documentation work. Then generate as many files as you want.

---

## Single File Documentation

### UI Component
```
Generate AKR documentation for src/components/UserProfile.tsx
```

### API Service
```
Generate AKR documentation for src/Services/AuthService.cs
```

### Database Table
```
Generate AKR documentation for training/Tables/Users.sql
```

---

## Batch Documentation (Multiple Files)

### Option 1: By Folder
```
Generate AKR documentation for all TypeScript files in src/services/
```

```
Generate AKR documentation for all C# files in src/Controllers/
```

```
Generate AKR documentation for all SQL tables in training/Tables/
```

### Option 2: Specific Files
```
Generate AKR documentation for these files:
- src/services/authService.ts
- src/services/userService.ts
- src/services/courseService.ts
```

### Option 3: By Pattern
```
Generate AKR documentation for all React components in src/components/
```

---

## ⚠️ Batch Processing Best Practices

**Problem:** Generating many files at once can take a long time or appear to hang.

**Why:** Each file requires:
- Code analysis
- Template selection
- Content generation
- File writing
- Git operations

### Best Practices

1. **Start Small**
   - ✅ 3-5 files at a time
   - ✅ Test with one file first
   - ❌ Don't try 10+ files at once

2. **Use Logical Batches**
   - ✅ Document by layer (data → business → presentation)
   - ✅ Document by domain (user module, order module)
   - ✅ Document dependencies first (shared components before features)
   - ❌ Don't randomly pick files

3. **Plan First** (See Step 5 in Quick Start Guides)
   ```
   Analyze this project's architecture and recommend a documentation order
   ```

4. **If It Seems Stuck**
   - Wait 30-60 seconds (large files take time)
   - Check VS Code's Output panel for progress
   - Press `Esc` to cancel if truly frozen
   - Try again with fewer files

---

## Other Common Tasks

### List Available Templates
```
List all AKR documentation templates
```

or

```
Show me available AKR templates for API services
```

### Check Server Health
```
Check the AKR documentation server health
```

or 

```
Is the AKR MCP server running?
```

### Start Interview (for business context)
```
Start an AKR documentation interview for src/services/PaymentService.cs
```

### Get Documentation Strategy
```
Analyze my project's architecture and recommend which files to document first
```

---

## Example Workflows

### UI Project (React/TypeScript)

**0. Initialize session (MUST DO FIRST!):**
   ```
   Initialize an AKR documentation session for this workspace and create a new feature branch
   ```

1. **Plan:**
   ```
   Analyze this UI project and recommend documentation order
   ```

2. **Document shared components:**
   ```
   Generate AKR documentation for these shared components:
   - src/components/common/Button.tsx
   - src/components/common/Input.tsx
   - src/components/common/Modal.tsx
   ```

3. **Document services:**
   ```
   Generate AKR documentation for all files in src/services/
   ```

4. **Document feature components:**
   ```
   Generate AKR documentation for all components in src/components/user/
   ```

5. **Create PR:**
   ```
   End the AKR documentation session and create a pull request titled "Add UI component documentation" with description "Generated AKR documentation for shared components, services, and feature components"
   ```

### API Project (C#/.NET)

**0. Initialize session (MUST DO FIRST!):**
   ```
   Initialize an AKR documentation session for this workspace and create a new feature branch
   ```

1. **Plan:**
   ```
   Analyze this API project's layered architecture and recommend documentation order
   ```

2. **Document data layer:**
   ```
   Generate AKR documentation for all repository files in src/Repositories/
   ```

3. **Document business layer:**
   ```
   Generate AKR documentation for these services:
   - src/Services/UserService.cs
   - src/Services/AuthService.cs
   - src/Services/EmailService.cs
   ```

4. **Document API layer:**
   ```
   Generate AKR documentation for all controllers in src/Controllers/
   ```

5. **Create PR:**
   ```
   End the AKR documentation session and create a pull request titled "Add API documentation" with description "Generated AKR documentation for data layer, business logic, and API endpoints"
   ```

### Database Project

**0. Initialize session (MUST DO FIRST!):**
   ```
   Initialize an AKR documentation session for this workspace and create a new feature branch
   ```

1. **Plan:**
   ```
   Analyze this database schema and recommend documentation order
   ```

2. **Document core tables:**
   ```
   Generate AKR documentation for these tables:
   - training/Tables/Users.sql
   - training/Tables/Departments.sql
   - training/Tables/Courses.sql
   ```

3. **Document domain tables:**
   ```
   Generate AKR documentation for all enrollment tables
   ```

4. **Document views and procedures:**
   ```
   Generate AKR documentation for all views in training/Views/
   ```

5. **Create PR:**
   ```
   End the AKR documentation session and create a pull request titled "Add database documentation" with description "Generated AKR documentation for tables, views, and stored procedures"
   ```

---

## Ending Your Documentation Session

After you've generated all your documentation, you need to end the session.

### Option 1: End with Pull Request (Recommended)

```
End the AKR documentation session and create a pull request titled "Add component documentation" with description "Generated AKR documentation for services, controllers, and components"
```

This will:
- ✅ Push your docs branch to GitHub
- ✅ Create a pull request against main
- ✅ Include summary of all documented files
- ✅ Mark as draft for review

### Option 2: End Without PR

If you want to review locally first or create PR manually:

```
End the AKR documentation session
```

Then manually create PR later:
- Using GitHub CLI: `gh pr create`
- Using GitHub web UI

### Checking PR Requirements

Before creating a PR, you can check if everything is ready:

```
Check if I'm ready to create a documentation pull request
```

This verifies:
- ✅ GitHub CLI installed
- ✅ Authenticated to GitHub
- ✅ On a documentation branch
- ✅ Changes committed

---

## Troubleshooting

### "Documentation went to main branch instead of feature branch"
**Problem:** Forgot to initialize documentation session first.
**Solution:** Always run initialization before generating:
```
Initialize an AKR documentation session for this workspace and create a new feature branch
```

### "Command '/docs.generate' not found"
**Problem:** You're using slash commands that don't exist.
**Solution:** Use natural language prompts instead (see examples above).

### "Processing seems stuck"
**Problem:** Too many files at once.
**Solution:** 
- Press `Esc` to cancel
- Try with 3-5 files only
- Check Output panel for errors

### "MCP server not responding"
**Problem:** Server not connected or crashed.
**Solution:**
```
Check the AKR documentation server health
```

If no response:
1. Press `Ctrl+Shift+P`
2. Type "Developer: Reload Window"
3. Try again

### "No workspace detected"
**Problem:** Wrong folder opened in VS Code.
**Solution:**
1. Close VS Code
2. Navigate to your repository folder
3. Run: `code .`
4. Try again

---

**Last Updated:** January 23, 2026
