# Copilot Chat Workflow - Step-by-Step Guide

## Overview

This guide walks you through the complete workflow for creating and maintaining technical documentation using AKR MCP Server integrated with GitHub Copilot Chat.

**Key Principle:** You control the entire process. AKR provides code extraction, validation, and writing tools. Chat provides the intelligence. You provide the judgment.

## Workflow Phases

### Phase 1: Extract Code Context

**Goal:** Get AI-digestible summaries of your code  
**Duration:** 30 seconds - 2 minutes  
**Effort:** Minimal (one tool call)

#### Step 1.1: Open Copilot Chat
1. In VS Code, open GitHub Copilot Chat (`Ctrl+Shift+I`)
2. Say: *"Extract code context from my AuthService.cs file"*

**In Chat:**
```
"Extract code context from /src/services/AuthService.cs. 
Include methods and classes."
```

#### Step 1.2: Let Chat Call the Tool
Copilot will call `extract_code_context` tool.

**Example Output:**
```json
{
  "language_detected": "csharp",
  "classes": [
    {
      "name": "AuthenticationService",
      "namespace": "MyApp.Services",
      "methods": [
        {
          "name": "AuthenticateAsync",
          "signature": "async Task<LoginResult> AuthenticateAsync(string username, string password)",
          "return_type": "Task<LoginResult>"
        },
        {
          "name": "LogoutUser",
          "signature": "void LogoutUser(string userId)",
          "return_type": "void"
        }
      ],
      "properties": [
        {
          "name": "TokenExpiry",
          "type": "TimeSpan"
        }
      ]
    }
  ],
  "imports": [
    {
      "module_name": "System.Threading.Tasks",
      "import_type": "using"
    },
    {
      "module_name": "MyApp.Models",
      "import_type": "using"
    }
  ],
  "metadata": {
    "extractor_version": "0.2.0",
    "language_detected": "csharp",
    "extraction_errors": [],
    "partial": false
  }
}
```

#### Step 1.3: Review the Extraction
Review the extracted context:
- ✅ Are all important methods included?
- ✅ Are the signatures accurate?
- ✅ Are the namespaces correct?
- ❌ If something's wrong, ask Chat: *"The LogoutUser method also accepts a sessionId parameter"*

### Phase 2: Get Charter Template

**Goal:** Load the right template for documentation  
**Duration:** 10 seconds

#### Step 2.1: Ask for Template
In Chat, say:
```
"Get the charter template for a backend service."
```

Copilot will call `list_resources` to find available templates.

**Example Response:**
- Templates available:
  - `lean_baseline_service_template`: 5 sections, estimated 15-20 minutes to complete
  - `api_endpoint_charter`: 7 sections, for REST APIs specifically
  - `integration_service_charter`: 6 sections, for inter-service communication

#### Step 2.2: Choose Your Template
Say: *"Show me the lean_baseline_service_template"*

**Template Content:**
```markdown
# Service Charter: {SERVICE_NAME}

## Overview
{What does this service do? Single paragraph describing purpose and scope.}

## Responsibilities
{Bullet list of primary responsibilities}

## Interfaces
{Public methods/endpoints exposed by this service}

## Dependencies
{Services or systems this service depends on}

## Error Handling
{How does it handle failures? Retry strategies?}
```

### Phase 3: Draft Charter with Chat

**Goal:** Generate your first draft using AI  
**Duration:** 2-5 minutes  
**Effort:** Light review and feedback

#### Step 3.1: Ask Chat to Draft
```
Using the extracted context from AuthService.cs and the lean_baseline_service_template,
draft a service charter for the Authentication Service. 

Include:
- Clear responsibilities for auth and session management
- List the main interfaces (AuthenticateAsync, LogoutUser, RefreshToken)
- Mention dependencies (database, token service)
- What happens when auth fails
```

**What Chat Does:**
- Reads the extracted code
- Applies it to the template structure
- Fills in sections with generated content
- Marks uncertain sections with [❓ clarification needed]

**Draft Output:**
```markdown
# Service Charter: Authentication Service

## Overview
The Authentication Service manages user identity verification and session lifecycle. 
It provides secure login/logout capabilities, token validation, and session 
expiration handling for the entire platform.

## Responsibilities
- User password validation against secure stores
- OAuth2/JWT token generation and rotation
- Session lifecycle management (creation, extension, termination)
- Multi-factor authentication (MFA) coordination [❓ currently supported?]
- Failed login attempt tracking and account lockout [❓ implemented?]

## Interfaces
- `AuthenticateAsync(username, password)`: Returns LoginResult with session token
- `LogoutUser(userId)`: Terminates user session
- `RefreshToken(refreshToken)`: [❓ is this method exposed?]
- `ValidateToken(token)`: Checks token validity [❓ or is this internal?]

## Dependencies
- User Database: Stores hashed passwords and user profiles
- Token Service: Manages token encryption/decryption keys
- Audit Service: Logs authentication events
- [❓ MFA Provider?] [❓ Email/SMS service for verification?]

## Error Handling
- InvalidCredentialsException: Logged, no details returned to client
- TokenExpiredException: Client requests re-authentication  
- AccountLockedException: After 5 failed attempts, 15-minute lockout
- DatabaseUnavailableException: [❓ Graceful degradation or fail-fast?]
```

#### Step 3.2: Review the Draft
Read through the draft and note:
- ✅ Good sections that match your service
- ❌ Placeholders needing clarification (marked with [❓ ...])
- Missing context
- Inaccuracies

#### Step 3.3: Refine with Chat
For each [❓ ...] placeholder:

```
In Chat: "Regarding MFA authentication - we currently support:
- Google Authenticator (TOTP)
- SMS verification (via Twilio)
- Not implemented yet: FIDO2/WebAuthn

Update the Dependencies section and Error Handling to reflect this."
```

Chat will refine the draft. Repeat until you're satisfied.

### Phase 4: Validate Structure

**Goal:** Ensure your document meets compliance standards  
**Duration:** 10-30 seconds  
**Effort:** Minimal (review automated results)

#### Step 4.1: Ask for Validation
In Chat:
```
"Validate this charter against the lean_baseline_service_template 
using TIER_1 (strict) validation."
```

(Or copy-paste your refined markdown)

**Validation Tiers:**
- **TIER_1**: Strict - all sections required, ≥80% completeness, no placeholders allowed
- **TIER_2**: Moderate - main sections required, ≥60% completeness, some flexibility  
- **TIER_3**: Lenient - basic sections required, ≥30% completeness, informational

#### Step 4.2: Review Validation Results

**Example Output:**
```json
{
  "is_valid": false,
  "errors": [
    {
      "type": "PLACEHOLDER_FOUND",
      "severity": "BLOCKER",
      "field": "## Responsibilities",
      "message": "Found unresolved placeholder: [❓ currently supported?]"
    },
    {
      "type": "INCOMPLETE_FIELD",
      "severity": "ERROR",
      "field": "## Error Handling",
      "message": "Missing error class: TimeoutException"
    }
  ],
  "warnings": [
    {
      "type": "MISSING_EXAMPLES",
      "severity": "WARNING",
      "field": "## Interfaces",
      "message": "Consider adding usage examples"
    }
  ],
  "metadata": {
    "tier_level": "TIER_1",
    "template_id": "lean_baseline_service_template",
    "completeness_percent": 78,
    "validation_passed": false
  }
}
```

**Key Issues:**
- ❌ BLOCKER: `[❓ currently supported?]` placeholder in Responsibilities
- ❌ ERROR: TimeoutException not documented
- ⚠️  WARNING: No usage examples

#### Step 4.3: Fix Issues

**For Blockers/Errors:**
```
In Chat: "Remove all [❓ ...] placeholders. 
For MFA - we support Google Authenticator and SMS only.
For TimeoutException - add it under Error Handling with 30-second default."
```

**For Warnings:**
```
In Chat: "Add a brief usage example for the AuthenticateAsync method."
```

Chat refines the document. Re-validate if you made significant changes.

### Phase 5: Write to Repository

**Goal:** Save your finalized documentation  
**Duration:** 5 seconds  
**Effort:** Confirmation

#### Step 5.1: Prepare for Writing
Once validation passes (or issues are acceptable):

```
In Chat: "Write this charter to the repository at:
/docs/services/authentication_charter.md

Operation: create (this is a new file)
Tier: TIER_1"
```

#### Step 5.2: Review Write Parameters
Before Chat takes action, verify:
- ✅ File path is correct: `/docs/services/authentication_charter.md`
- ✅ Operation: `create` (not overwriting existing file)
- ✅ Validation: Strict (TIER_1)
- ✅ You have write permissions to `/docs/`

#### Step 5.3: Confirm Write
```
In Chat: "Yes, proceed with writing the charter."
```

**Write Operation:**
```json
{
  "success": true,
  "file_path": "/docs/services/authentication_charter.md",
  "operation": "create",
  "bytes_written": 2847,
  "metadata": {
    "timestamp": "2024-01-15T10:35:00Z",
    "audit_id": "write_abc123def456",
    "validation_tier": "TIER_1",
    "template_source": "git_submodule"
  }
}
```

✅ **File written successfully!**

Your charter is now in the repository with an audit trail.

---

## Advanced Workflows

### Multi-Service Documentation

**Scenario:** You need charters for 5 services.

**Workflow:**
1. Extract context for Service A → Draft → Validate → Write
2. Extract context for Service B → Draft → Validate → Write
3. Extract context for Service C → Draft → Validate → Write
4. Extract context for Service D → Draft → Validate → Write
5. Extract context for Service E → Draft → Validate → Write

**Efficiency Tip:**
- Reuse refined sections from Service A's charter in Service B
- Ask Chat: *"Use the Error Handling section from the Authentication Service charter as a starting template for the Payment Service Error Handling"*

### Database Schema Documentation

**Scenario:** You need to document your database schema.

**Workflow:**
1. Extract code context from `schema.sql`
   ```
   Chat: "Extract code context from database/schema.sql. 
   Include SQL tables."
   ```

2. Chat calls `extract_code_context` → returns tables, columns, constraints

3. Ask Chat to draft schema charter using `database_schema_template`

4. Validate with TIER_2 (databases often have complex relationships)

5. Write to `/docs/database/schema_charter.md`

### Updating Existing Documentation

**Scenario:** Service changed, need to update charter.

**Workflow:**
1. Extract new context from updated `AuthService.cs`
2. Ask Chat:
   ```
   "Compare the new extraction with the existing charter at:
   /docs/services/authentication_charter.md
   
   Show changes needed."
   ```

3. Chat identifies:
   - New methods (RefreshToken)
   - Changed signatures
   - Removed methods

4. Draft updates:
   ```
   Chat: "Update the charter to reflect:
   - New RefreshToken method
   - Changed LogoutUser signature (now requires sessionId)
   - Removed ValidateTokenAsync method (internal only now)"
   ```

5. Validate changes with TIER_1

6. Write with `operation: update`

### Team Review & Approval

**Scenario:** TIER_1 validation requires team review.

**Workflow:**
1. Generate and validate charter
2. In Chat: "Create a PR with this charter for team review"
3. Chat (with future GitHub integration):
   - Creates branch: `charter/auth-service-2024-01-15`
   - Commits charter
   - Opens PR with charter content
   - Requests review from architecture team

4. Team reviews in PR
5. Once approved, Chat merges to main

---

## Troubleshooting

### "Extraction returned partial=true"

**Problem:** Code extraction couldn't fully parse the file.

**Solution:**
1. Check file syntax (compile errors?)
2. Verify file is supported language (C# or SQL only)
3. Ask Chat: *"Extract just the public methods from AuthService.cs"*
4. Manually add missing context in the charter draft

### "Validation error: Placeholder found: [❓ ...]"

**Problem:** Your charter still has unresolved placeholders.

**Solution:**
1. Identify the placeholder
2. Ask Chat: *"I need to clarify: [what was the placeholder asking]? Here's the answer: [your clarification]"*
3. Chat updates the section
4. Re-validate

### "Write failed: Permission denied"

**Problem:** User account doesn't have write access.

**Solution:**
1. Verify file path is in writable directory (`/docs/`)
2. Check repository permissions
3. Use `operation: dry_run` first to see if validation passes
4. Ask repository administrator for write access

### "Validation passed but Charter doesn't feel complete"

**Problem:** Document passes validation but feels missing context.

**Solution:**
1. Ask Chat: *"Review this charter against these requirements: [add requirements]"*
2. Chat provides gaps analysis
3. Refine with Chat
4. Re-validate (may need to lower tier: TIER_1 → TIER_2)
5. Document the rationale for tier choice in comments

---

## Best Practices

### 1. Start with Extraction
Always extract real code first. Don't ask Chat to fabricate services.

❌ **Wrong:**
```
"Write a charter for a hypothetical PaymentService"
```

✅ **Right:**
```
"Extract code context from /src/services/PaymentService.cs. 
Then draft a charter."
```

### 2. Review Each Phase
Don't skip validation. It catches inconsistencies and missing requirements.

### 3. Use Appropriate Tier
- **TIER_1** (Strict): Critical services, public APIs, high-traffic paths
- **TIER_2** (Moderate): Internal services, moderate complexity
- **TIER_3** (Lenient): Legacy services, internal tools, learning documents

### 4. Iterate with Chat
Your expertise + Chat's generation speed = best results.

If validation finds issues:
1. Don't immediately accept Chat's auto-fix
2. Ask: *"Why is this an issue? Can we address it differently?"*
3. Discuss options in Chat
4. Let Chat refine, then re-validate

### 5. Add Examples
Even if validation passes, well-documented examples help future developers.

Ask Chat: *"Add usage examples for the three main methods in the Interfaces section."*

### 6. Track Decisions
In comments, note architectural decisions:

```markdown
## Error Handling

### Timeout Strategy
[Decision: 30-second timeout chosen after analysis showing 99th percentile 
latency at 25s. Standard across all auth services.]
```

This helps future reviewers understand the "why" behind choices.

### 7. Enable Audit Trail
Always write with `audit_id` logged. This enables:
- Compliance queries: "Who modified this charter?"
- Change tracking: "When was the last update?"
- Rollback: "Revert to commit X if needed"

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open Copilot Chat | `Ctrl+Shift+I` |
| Ask inline | Highlight text + `Ctrl+/` |
| Reference file | Type `#` in chat |
| Reference symbol | Type `@` in chat |

---

## Examples by Service Type

### REST API Service
1. Extract from controller files
2. Draft using `api_endpoint_charter`
3. Validate TIER_1 (public APIs are critical)
4. Include HTTP methods, status codes, authentication

### Database Service
1. Extract from `.sql` schema files
2. Draft using `database_schema_charter`
3. Validate TIER_2 (databases are complex)
4. Include relationships, constraints, migration strategy

### Background Job Service
1. Extract from job scheduler/worker classes
2. Draft using `background_job_charter`
3. Validate TIER_2
4. Include retry logic, failure handling, monitoring

### Integration Service
1. Extract from both sides (API client code + webhook handlers)
2. Draft using `integration_service_charter`
3. Validate TIER_1 (integrations need clear contracts)
4. Include rate limits, error recovery, data transformation

---

## When to Use Each Validation Tier

### TIER_1 (Strict) ✅
Use for:
- Public APIs
- Authentication/security services
- Payment processing
- High-traffic services
- Customer-facing features

Requires: All sections, ≥80% completeness, no placeholders

### TIER_2 (Moderate) ✅
Use for:
- Internal services
- Moderate-traffic features
- Business logic services
- Integration points

Requires: Core sections, ≥60% completeness, limited flexibility

### TIER_3 (Lenient) ✅
Use for:
- Administration tools
- Legacy systems
- Prototypes/spikes
- Learning/training documentation

Requires: Basic structure, ≥30% completeness, informational

---

## Summary Checklist

- [ ] Extracted code context from real source files
- [ ] Reviewed extraction for accuracy
- [ ] Selected appropriate template
- [ ] Drafted charter with Chat
- [ ] Resolved all [❓ ...] placeholders
- [ ] Validated against appropriate tier
- [ ] Fixed or accepted validation issues
- [ ] Re-validated if made significant changes
- [ ] Confirmed file path and operation type
- [ ] Written to repository with audit trail
- [ ] Charter appears in `/docs/` directory

✅ **You've created professional technical documentation!**
