# Backend Service Documentation - Developer Guide

**Version**: 1.0  
**Last Updated**: 2025-11-01  
**Target Audience**: Developers documenting backend services  
**Tools Required**: VS Code or Visual Studio with GitHub Copilot  
**Time Required**: 25 minutes per service (5 min AI + 20 min human enhancement)

---

## Purpose

This guide helps you create high-quality backend service documentation in ~25 minutes using GitHub Copilot. You'll learn:
1. How to identify and attach the right files for Copilot context
2. How to use the standard prompt to generate baseline documentation
3. How to enhance AI-generated documentation with business context
4. How to handle legacy projects with non-standard naming

**Prerequisites**: 
- Read **AKR_CHARTER_BACKEND.md** for conventions
- Have access to GitHub Copilot in VS Code or Visual Studio
- Target service code must exist (not documenting before coding)

---

## Quick Start (TL;DR)

### Using VS Code/Visual Studio with Copilot
```
1. Identify service to document (e.g., EnrollmentService)
2. Find related files (Service + Repository + Controller + DTO)
3. Open Copilot Chat (Ctrl+Shift+I)
4. Attach 3-5 files using @ mentions
5. Paste standard prompt (see Step 3A.2)
6. Review and enhance output (add WHY, business context)
7. Save to docs/services/[ServiceName]_doc.md
8. Create PR with feature tag
```

**Total time**: 5 min (AI) + 20 min (human) = 25 minutes

### Using GitHub Copilot Spaces
```
1. Identify service to document (e.g., EnrollmentService)
2. Open service file
3. Open Copilot Spaces (Ctrl+Shift+.)
4. Paste standard prompt (see Step 3B.2) - no file attachment needed
5. Review and enhance output (add WHY, business context)
6. Save to docs/services/[ServiceName]_doc.md
7. Create PR with feature tag
```

**Total time**: 5 min (AI) + 20 min (human) = 25 minutes

**Recommendation**: Start with GitHub Copilot Spaces if available (easier, better workspace context). Fall back to VS Code Copilot for focused documentation tasks.

---

## Step-by-Step Process

### Step 1: Identify the Target Service (2 minutes)

**What to document**: Service layer classes that contain business logic

**Look for files with these patterns**:
```
✅ *Service.cs          (e.g., EnrollmentService.cs)
✅ *Manager.cs          (e.g., EnrollmentManager.cs - legacy projects)
✅ *Logic.cs            (e.g., EnrollmentLogic.cs - legacy projects)
✅ *Handler.cs          (e.g., EnrollmentHandler.cs - CQRS pattern)
✅ *Interactor.cs       (e.g., EnrollUserInteractor.cs - Clean Architecture)
✅ *ApplicationService.cs (e.g., EnrollmentApplicationService.cs - DDD)
```

**Don't document** (these are not service layer):
```
❌ *Controller.cs       (API layer - different documentation system)
❌ *Repository.cs       (Data layer - usually straightforward CRUD)
❌ *Entity.cs           (Domain model - document only if complex business logic)
❌ *Dto.cs / *Request.cs (Data transfer objects - self-documenting)
❌ *Validator.cs        (Validation logic - part of service documentation)
```

**Example**: In Training Tracker project, document:
- ✅ `EnrollmentService.cs`
- ✅ `CourseService.cs`
- ✅ `UserService.cs`
- ✅ `NotificationService.cs`

---

### Step 2: Find Related Files for Context (3-5 minutes)

**Goal**: Gather 3-5 files that show the complete flow of the service

#### Strategy A: Standard Project (Modern Naming)

**If your project follows standard patterns**, find these files:

```
Priority 1 (MUST HAVE):
├── Service implementation
│   └── src/Services/EnrollmentService.cs
│
└── Repository used by service
    └── src/Repositories/EnrollmentRepository.cs
```

```
Priority 2 (SHOULD HAVE):
├── Controller that calls service
│   └── src/Controllers/EnrollmentsController.cs
│
└── Main DTO/Request model
    └── src/Contracts/EnrollmentDto.cs
```

```
Priority 3 (NICE TO HAVE):
├── Domain entity
│   └── src/Domain/Enrollment.cs
│
└── Related service (if dependency exists)
    └── src/Services/CourseService.cs (if EnrollmentService uses it)
```

**Recommended starting set** (attach these 4 files):
1. `EnrollmentService.cs` - The target service
2. `EnrollmentRepository.cs` - How it accesses data
3. `EnrollmentsController.cs` - How it's called
4. `EnrollmentDto.cs` - What data it works with

---

#### Strategy B: Legacy Project (Non-Standard Naming)

**If your project uses different naming**, use this discovery process:

**Step 2.1: Find the service file**

Use VS Code search (Ctrl+Shift+F) or file explorer:
```
Search patterns:
- "Enrollment" (in file names)
- "class *Service" (in file contents)
- "class *Manager" (in file contents)
- "class *Logic" (in file contents)
```

**Common legacy patterns**:
```
✅ EnrollmentManager.cs
✅ EnrollmentBusinessLogic.cs
✅ EnrollmentBL.cs
✅ EnrollmentFacade.cs
✅ EnrollmentProcessor.cs
```

**Step 2.2: Find the repository/data access file**

Open the service file, look at constructor:
```csharp
public class EnrollmentService
{
    private readonly IEnrollmentRepository _repository;  // ← Look for this
    private readonly EnrollmentDataAccess _dataAccess;   // ← Or this
    private readonly EnrollmentDAO _dao;                 // ← Or this
    
    public EnrollmentService(IEnrollmentRepository repository)  // ← Constructor injection
    {
        _repository = repository;
    }
}
```

**Common repository patterns**:
```
✅ EnrollmentRepository.cs
✅ EnrollmentDataAccess.cs
✅ EnrollmentDAO.cs
✅ EnrollmentDb.cs
✅ EnrollmentData.cs
```

**Step 2.3: Find the controller**

Search for files that reference the service:
```
Search in files (Ctrl+Shift+F):
- "EnrollmentService" (the class name)
- "IEnrollmentService" (the interface)
```

**Common controller patterns**:
```
✅ EnrollmentsController.cs       (RESTful - plural)
✅ EnrollmentController.cs        (singular)
✅ EnrollmentApiController.cs
✅ EnrollmentWebService.cs        (legacy SOAP)
```

**Step 2.4: Find DTOs/Models**

Look in service method signatures:
```csharp
public async Task<EnrollmentResult> EnrollUserAsync(EnrollUserRequest request)
//                                                   ↑ This is the DTO
```

**Common DTO patterns**:
```
✅ EnrollUserRequest.cs
✅ EnrollmentDto.cs
✅ EnrollmentViewModel.cs
✅ EnrollmentModel.cs
✅ EnrollmentContract.cs
```

---

#### Strategy C: Complex Project (Multiple Layers)

**If your project uses Clean Architecture, DDD, or CQRS**, files might be organized differently:

**Clean Architecture**:
```
src/
├── Controllers/
│   └── EnrollmentsController.cs        ← Attach this
├── Application/
│   ├── UseCases/
│   │   └── EnrollUserUseCase.cs        ← Attach this (target)
│   └── Interfaces/
│       └── IEnrollmentRepository.cs
├── Domain/
│   ├── Entities/
│   │   └── Enrollment.cs               ← Attach this
│   └── Services/
│       └── EnrollmentDomainService.cs  ← Attach this if exists
└── Infrastructure/
    └── Repositories/
        └── EnrollmentRepository.cs     ← Attach this
```

**DDD (Domain-Driven Design)**:
```
src/
├── Presentation/
│   └── Controllers/
│       └── EnrollmentsController.cs
├── Application/
│   └── Services/
│       └── EnrollmentApplicationService.cs  ← Attach this (target)
├── Domain/
│   ├── Aggregates/
│   │   └── Enrollment.cs                     ← Attach this
│   └── Services/
│       └── EnrollmentDomainService.cs        ← Attach this if exists
└── Infrastructure/
    └── Repositories/
        └── EnrollmentRepository.cs           ← Attach this
```

**CQRS (Command Query Responsibility Segregation)**:
```
src/
├── Controllers/
│   └── EnrollmentsController.cs
├── Commands/
│   ├── EnrollUserCommand.cs                 ← Attach this
│   └── EnrollUserCommandHandler.cs          ← Attach this (target)
├── Queries/
│   ├── GetEnrollmentsQuery.cs
│   └── GetEnrollmentsQueryHandler.cs        ← Attach this (target)
└── Repositories/
    └── EnrollmentRepository.cs              ← Attach this
```

**For these architectures**: Attach the "use case" or "handler" as the target service.

---

### Step 3A: Use VS Code/Visual Studio with Copilot (10 minutes)

#### 3A.1: Open Copilot Chat and Attach Files

**In VS Code:**
1. Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Shift+I` (Mac)
2. Copilot Chat panel opens on the right side

**In Visual Studio:**
1. View → GitHub Copilot Chat
2. Chat window opens

**Attach files using @ mentions:**
```
Type @ in the chat box → File picker appears → Select files
```

**Recommended attachment order** (attach 3-5 files):
```
@EnrollmentService.cs           ← Target service (MUST)
@EnrollmentRepository.cs        ← Data access (MUST)
@EnrollmentsController.cs       ← API usage (SHOULD)
@EnrollmentDto.cs               ← Data contracts (SHOULD)
@Enrollment.cs                  ← Domain entity (OPTIONAL)
```

**Pro Tips**:
- ✅ Attach implementation files (.cs), not interfaces (.cs with just interface)
- ✅ If you attach >5 files, Copilot may hit token limits (output quality degrades)
- ✅ If output is poor, try with fewer files first (just service + repository)
- ✅ You can attach files mid-conversation if Copilot asks for more context

**Visual Example**:
```
Copilot Chat:

@EnrollmentService.cs @EnrollmentRepository.cs @EnrollmentsController.cs @EnrollmentDto.cs

[Your prompt goes here...]
```

---

#### 3A.2: Standard Prompt for VS Code/Visual Studio

Copy the prompt below and paste into Copilot Chat:

```
Generate backend service documentation following AKR_CHARTER_BACKEND.md conventions.

Use the lean_baseline_service_template.md structure from the AKR files folder.

**Target service**: [SERVICE_NAME_HERE - e.g., EnrollmentService]

**Include ONLY baseline sections** (skip optional sections for now):
1. Service Identification (name, namespace, file location, complexity)
2. Quick Reference (TL;DR: what it does, when to use, watch out for)
3. What & Why (purpose, capabilities, scope boundaries)
4. How It Works (primary operation with step-by-step flow)
5. Business Rules (table format: Rule ID, Description, Why It Exists, Since When)
6. Architecture (Dependencies and Consumers tables with failure modes)
7. Data Operations (Reads From, Writes To, Side Effects)
8. Questions & Gaps (flag unknowns, technical debt, magic numbers)

**Important conventions**:
- Use text-based flow diagrams with boxes and arrows (NOT Mermaid)
- Mark all AI-generated content with 🤖
- Mark sections needing human input with ❓
- For API Layer: Reference existing API documentation instead of duplicating endpoint details
- Use BR-[SERVICE_ABBREVIATION]-### format for business rules (e.g., BR-ENR-001)
- Focus on WHAT code does (observable from code) - mark as 🤖
- Flag WHY questions for human input (business context, rationale) - mark as ❓

**Flow diagram format** (use this structure):
```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: [Action Name]                                        │
│  What  → 🤖 [Technical action taken]                         │
│  Why   → ❓ [Business reason - needs human input]            │
│  Error → 🤖 [Exception types that can occur]                 │
│  Impact→ ❓ [Business impact - needs human input]            │
└─────────────────────────────────────────────────────────────┘
                          ↓
                    [NEXT STEP]
```

**Business rules table format**:
| Rule ID | Description | Why It Exists | Since When |
|---------|-------------|---------------|------------|
| 🤖 BR-[SVC]-001 | 🤖 [Rule from code] | ❓ [Human: business rationale] | ❓ [Human: when added] |

**Extract from code**:
- Method signatures and parameters
- Dependencies from constructor injection
- Database tables/repositories from method calls
- Exception types from throw statements
- Validation logic for business rules
- Call flow from method implementations

**Flag for human review**:
- Magic numbers or hardcoded values (Why these specific values?)
- Comments saying "temporary" or "workaround" (What's the permanent fix?)
- Complex conditional logic (Why these specific conditions?)
- External API calls or third-party dependencies
- Performance concerns (timeouts, retries, caching)

Generate the documentation now.
```

**Customization points** (modify before pasting):
- Replace `[SERVICE_NAME_HERE]` with actual service name (e.g., `EnrollmentService`)
- If using different architecture, adjust section names slightly
- If project doesn't have API documentation system, remove that note

---

### Step 3B: Use GitHub Copilot Spaces (Alternative) (10 minutes)

#### 3B.1: Open Copilot Spaces

**In VS Code:**
1. Open the service file (e.g., `EnrollmentService.cs`)
2. Press `Ctrl+Shift+.` or click Copilot Spaces icon
3. Copilot Spaces panel opens

**GitHub Copilot Spaces has more workspace context automatically**, so you don't need to attach files manually. It can see:
- ✅ All files in your workspace/solution
- ✅ Related services, repositories, controllers
- ✅ Project structure and dependencies
- ✅ Existing documentation patterns

---

#### 3B.2: Standard Prompt for GitHub Copilot Spaces

Copy the prompt below and paste into Copilot Spaces:

```
I need to document the [SERVICE_NAME] service following our AKR documentation system.

**Context**:
- Template: Use lean_baseline_service_template.md from AKR files folder
- Conventions: Follow AKR_CHARTER.md and AKR_CHARTER_BACKEND.md
- Target service: [SERVICE_NAME] (file: [PATH_TO_SERVICE])
- Output location: docs/services/[ServiceName]_doc.md

**Generate documentation with baseline sections**:
1. **Service Identification**: Namespace, file location, complexity (Simple/Medium/Complex)
2. **Quick Reference**: What it does (1-2 sentences), when to use, watch out for
3. **What & Why**: Purpose, capabilities, scope boundaries (what it does NOT do)
4. **How It Works**: Primary operation with step-by-step flow in text-based boxes
5. **Business Rules**: Table with BR-[SVC]-### format
6. **Architecture**: Dependencies table (what service needs), Consumers table (who uses it)
7. **Data Operations**: Reads From, Writes To, Side Effects tables
8. **Questions & Gaps**: Flag unknowns, magic numbers, technical debt

**Critical conventions to follow**:
✅ Use text-based flow diagrams (boxes with arrows), NOT Mermaid
✅ Mark AI-generated content with 🤖
✅ Mark sections needing human input with ❓
✅ Use BR-[SVC]-### format for business rules (e.g., BR-ENR-001)
✅ Focus on WHAT code does (observable) - mark 🤖
✅ Flag WHY questions (business context) - mark ❓

**Text-based flow diagram format** (use this structure):
```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: [Action Name]                                        │
│  What  → 🤖 [Technical action taken]                         │
│  Why   → ❓ [Business reason - needs human input]            │
│  Error → 🤖 [Exception types that can occur]                 │
│  Impact→ ❓ [Business impact - needs human input]            │
└─────────────────────────────────────────────────────────────┘
                          ↓
                    [NEXT STEP]
```

**What to extract from code**:
- Method signatures, parameters, return types from service class
- Dependencies from constructor injection (IRepository, IEmailService, etc.)
- Database operations from repository method calls
- Exception types from throw statements and try-catch blocks
- Validation logic for business rules
- Call flow from primary operation method

**What to flag for human input**:
- ❓ Business purpose of service (WHY it exists)
- ❓ Business rationale for rules (WHY these validations)
- ❓ Why specific error handling strategies chosen
- ❓ Magic numbers or hardcoded values (WHY these values?)
- ❓ Comments saying "temporary" or "workaround" (What's permanent fix?)
- ❓ Complex conditional logic (WHY these specific conditions?)
- ❓ Performance concerns (timeout values, retry strategies)

**Business rules table format**:
| Rule ID | Description | Why It Exists | Since When |
|---------|-------------|---------------|------------|
| 🤖 BR-[SVC]-001 | 🤖 [Rule from code] | ❓ [Business rationale] | ❓ [When added] |

**Dependencies table format**:
| Dependency | Purpose | Failure Mode |
|------------|---------|--------------|
| 🤖 `IDependencyName` | 🤖 [What it's used for] | ❓ [Critical? Blocking? Non-blocking?] |

**Data operations format**:
| Table/Source | Purpose | Business Context |
|--------------|---------|------------------|
| 🤖 `schema.TableName` | 🤖 [What data retrieved/modified] | ❓ [Why needed?] |

Generate complete baseline documentation following this structure.
```

**Customization points**:
- Replace `[SERVICE_NAME]` with actual service name (e.g., `EnrollmentService`)
- Replace `[PATH_TO_SERVICE]` with file path (e.g., `backend/Services/EnrollmentService.cs`)

---

### Step 4: Review Copilot Output (2 minutes)

**What to check**:

✅ **Structure is correct**
- All 8 baseline sections present
- Sections follow template order
- Markdown formatting valid

✅ **Technical content is accurate**
- Method signatures correct
- Dependencies list matches constructor
- Database tables match repository calls
- Exceptions match throw statements

✅ **AI markers are present**
- 🤖 marks AI-generated technical content
- ❓ marks sections needing human input
- Questions & Gaps section has flagged items

⚠️ **Common Copilot mistakes to watch for**:
- ❌ Hallucinating methods that don't exist (check against actual code)
- ❌ Guessing business reasons (should be marked ❓, not 🤖)
- ❌ Using Mermaid diagrams instead of text boxes (needs manual fix)
- ❌ Missing error handling details (check try-catch blocks)
- ❌ Incomplete dependency list (check all constructor parameters)

**If output quality is poor**:
1. Check if you attached the right files (service + repository minimum)
2. Try with fewer files (sometimes less is more)
3. Simplify prompt (remove some instructions)
4. Regenerate (click "Regenerate" in Copilot Chat)
5. As last resort: Start with manual structure, ask Copilot to fill specific sections

---

### Step 5: Key Differences - VS Code/Copilot vs GitHub Spaces

| Aspect | VS Code/Visual Studio with Copilot | GitHub Copilot Spaces |
|--------|-------------------------------------|------------------------|
| **Context** | Manual file attachment (@mentions) | Automatic workspace awareness |
| **File limit** | ~5 files (token limit) | Entire workspace/solution accessible |
| **Setup** | More manual (attach 3-5 files) | Less setup (workspace aware) |
| **Prompt style** | Explicit file references needed | Can reference by description |
| **Best for** | Focused documentation tasks | Broader context understanding |
| **Output quality** | High (if right files attached) | High (better cross-file insights) |
| **Learning curve** | Low (file picker straightforward) | Medium (need to understand Spaces) |

**Recommendation**: 
- **Start with GitHub Copilot Spaces** if available (easier, better context)
- **Fall back to VS Code/Visual Studio Copilot** if Spaces not available or for simple services

---

### Step 6: Enhance with Business Context (20 minutes)

**This is the critical step** - AI can't infer business context, only you can add it.

#### 6.1 Quick Reference Enhancement (3 minutes)

**AI generated** (technical):
```markdown
**What it does:**  
🤖 Manages user enrollment in courses with validation and notification.
```

**You add** (business context):
```markdown
**What it does:**  
🤖 Manages user enrollment in courses with validation and notification.  
❓ **Business value**: Ensures users meet prerequisites before enrollment, 
preventing training compliance violations and wasted seat capacity.

**When to use it:**  
❓ Called by web UI when user clicks "Enroll" button, by batch import job for 
bulk enrollments, and by admin panel for manual enrollment override.

**Watch out for:**  
❓ Prerequisite validation can fail silently if CourseService is down. 
Enrollment succeeds but user may not be notified. Check logs if users report 
missing confirmation emails.
```

---

#### 6.2 What & Why Enhancement (3 minutes)

**AI generated**:
```markdown
### Purpose
🤖 Handles user enrollment operations including validation, enrollment creation, 
and notification.
```

**You add**:
```markdown
### Purpose
🤖 Handles user enrollment operations including validation, enrollment creation, 
and notification.

❓ **Why this service exists**: 
- State licensing requires prerequisite tracking (courses must be taken in order)
- Business rule: Users limited to 5 active enrollments (system capacity constraint)
- Compliance requirement: All enrollments must be audited with timestamps
- Historical context: Built in v1.0 to replace manual Excel-based enrollment tracking

❓ **Business problem solved**: 
Before this service, enrollment was manual process taking 3-5 days. Caused:
- Training delays (users waiting for approval)
- Compliance issues (prerequisite violations not caught)
- Seat waste (users enrolled but prerequisites not met)

This service automates validation and reduces enrollment time to <1 minute.
```

---

#### 6.3 Business Rules Enhancement (5 minutes)

**AI generated** (partial):
```markdown
| Rule ID | Description | Why It Exists | Since When |
|---------|-------------|---------------|------------|
| 🤖 BR-ENR-001 | User cannot enroll in course twice | ❓ [HUMAN] | ❓ [HUMAN] |
| 🤖 BR-ENR-002 | Prerequisites must be completed | ❓ [HUMAN] | ❓ [HUMAN] |
| 🤖 BR-ENR-003 | Maximum 5 active enrollments | ❓ [HUMAN] | ❓ [HUMAN] |
```

**You complete**:
```markdown
| Rule ID | Description | Why It Exists | Since When |
|---------|-------------|---------------|------------|
| 🤖 BR-ENR-001 | User cannot enroll in course twice | ❓ Prevent duplicate charges ($500/course). Also prevents user confusion (which enrollment is active?). Business requested after 15 duplicate enrollments in pilot. | ❓ v1.0 (2025-01) |
| 🤖 BR-ENR-002 | Prerequisites must be completed before enrollment | ❓ State licensing requirement (Regulation 45.301). Incomplete prerequisites = invalid certification = legal liability. Non-negotiable rule. | ❓ v1.0 (2025-01) |
| 🤖 BR-ENR-003 | Maximum 5 active enrollments per user | ❓ System capacity limitation (Learning Management System license = 1000 concurrent users, 200 users max = 1000/5). Also prevents users from hoarding seats. Arbitrary limit, can be increased if LMS license upgraded. | ❓ v1.0 (2025-01) |
```

**What to document**:
- **Business rationale**: Why does this rule exist? (not "because PM said so")
- **Regulatory requirements**: If rule is legally required, cite regulation
- **Cost implications**: If rule prevents financial loss, state the cost
- **Historical context**: If rule was added because of incident, explain incident
- **Arbitrary vs critical**: If rule is arbitrary (can be changed), say so

---

#### 6.4 Flow Diagram Enhancement (5 minutes)

**AI generated** (technical What/Error):
```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Validate Prerequisites                               │
│  What  → 🤖 Query CourseRepository for prerequisite courses, │
│            check if user has completed all prerequisites     │
│  Why   → ❓ [HUMAN INPUT NEEDED]                             │
│  Error → 🤖 PrerequisiteNotMetException                      │
│  Impact→ ❓ [HUMAN INPUT NEEDED]                             │
└─────────────────────────────────────────────────────────────┘
```

**You complete** (business Why/Impact):
```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Validate Prerequisites                               │
│  What  → 🤖 Query CourseRepository for prerequisite courses, │
│            check if user has completed all prerequisites     │
│  Why   → ❓ State licensing requirement (Regulation 45.301). │
│            Incomplete prerequisites = invalid certification  │
│            = $50K fine per violation. Must validate upfront. │
│  Error → 🤖 PrerequisiteNotMetException                      │
│  Impact→ ❓ User sees error: "Complete [Course Name] first." │
│            Enrollment blocked. User must complete prereq     │
│            before retrying. No partial enrollment.           │
└─────────────────────────────────────────────────────────────┘
```

**For each step, document**:
- **Why**: Business reason, regulatory requirement, or historical context
- **Impact**: User-facing consequence, business consequence, downstream effects

---

#### 6.5 Architecture Enhancement (3 minutes)

**AI generated** (dependencies list):
```markdown
| Dependency | Purpose | Failure Mode |
|------------|---------|--------------|
| 🤖 `IEnrollmentRepository` | 🤖 Database operations | ❓ [HUMAN] |
| 🤖 `ICourseService` | 🤖 Retrieve course details | ❓ [HUMAN] |
| 🤖 `IEmailService` | 🤖 Send notifications | ❓ [HUMAN] |
```

**You complete** (failure modes and criticality):
```markdown
| Dependency | Purpose | Failure Mode | Critical? |
|------------|---------|--------------|-----------|
| 🤖 `IEnrollmentRepository` | 🤖 Database operations | ❓ Throws DatabaseException. Enrollment fails completely. User sees "System error, try again." Transaction rolled back, no partial state. | ⚠️ BLOCKING - Cannot proceed without database |
| 🤖 `ICourseService` | 🤖 Retrieve course details, prerequisites | ❓ Throws ServiceUnavailableException. Enrollment fails (cannot validate prerequisites). Rare (CourseService cached, 99.9% uptime). | ⚠️ BLOCKING - Cannot validate prerequisites |
| 🤖 `IEmailService` | 🤖 Send enrollment confirmation | ❓ Throws EmailException (non-blocking). Enrollment succeeds, email queued for retry (3 attempts over 24 hours). User doesn't see error. Email sent eventually or admin notified if all retries fail. | ✅ NON-BLOCKING - Enrollment completes |
```

**Document for each dependency**:
- **Failure Mode**: What exception? What happens to business operation?
- **Critical?**: Blocking (stops operation) or Non-blocking (continues with degraded functionality)
- **Fallback**: Is there graceful degradation? Retry logic? Manual intervention?

---

#### 6.6 Questions & Gaps Review (1 minute)

**AI flagged** (technical unknowns):
```markdown
### AI-Flagged Questions
🤖 Magic number "5" in max enrollments validation - why 5 specifically?
🤖 Hardcoded timeout of 30 seconds for email service - should be configurable?
🤖 Comment says "temporary workaround for CourseService bug" - what's permanent fix?
```

**You add** (business unknowns):
```markdown
### AI-Flagged Questions
🤖 Magic number "5" in max enrollments validation - why 5 specifically?
   ❓ ANSWERED: LMS license limit (1000/200 users = 5). Document in BR-ENR-003.

🤖 Hardcoded timeout of 30 seconds for email service - should be configurable?
   ❓ ANSWERED: Yes, should be in appsettings.json. Create tech debt ticket.

🤖 Comment says "temporary workaround for CourseService bug" - what's permanent fix?
   ❓ UNANSWERED: Ask John (CourseService owner). Bug ticket #3456 from 6 months ago.

### Human-Flagged Questions
❓ Why does prerequisite validation happen twice (in UI and service)?
   → Ask: Is UI validation just UX (fast feedback) and service validation is source of truth?

❓ Should we notify admin when enrollment fails due to capacity?
   → Ask: Product owner. Current behavior: Silent failure, user just sees error.

❓ Who decided 24-hour email retry window? Can it be longer?
   → Ask: Compliance team. May be regulatory requirement.
```

**For each flagged item**:
- Try to answer if you know the context
- If unanswered, identify who to ask
- Add new questions you discover while reviewing

---

### Step 7: Save Documentation (1 minute)

**File location**:
```
docs/services/[ServiceName]_doc.md
```

**Example**:
```
docs/services/EnrollmentService_doc.md
docs/services/CourseService_doc.md
docs/services/NotificationService_doc.md
```

**If docs/services folder doesn't exist**:
```bash
# From repository root
mkdir -p docs/services
```

**Naming convention**:
- Use PascalCase matching service class name: `EnrollmentService_doc.md`
- Don't use spaces: ❌ `Enrollment Service_doc.md`
- Don't abbreviate: ❌ `EnrollSvc_doc.md`
- Suffix with `_doc.md` to distinguish from other markdown files

---

### Step 8: Create Pull Request (2 minutes)

**Git commands**:
```bash
# From repository root
git checkout -b docs/enrollment-service-documentation
git add docs/services/EnrollmentService_doc.md
git commit -m "docs: add EnrollmentService baseline documentation (FN12345_US067)

- Generated baseline using GitHub Copilot
- Enhanced with business context (prerequisites rationale, failure modes)
- Documented business rules with regulatory requirements
- Identified dependencies and failure behavior
- Documented 3 business rules (BR-ENR-001, BR-ENR-002, BR-ENR-003)

Estimated effort: 25 minutes (5 min AI generation + 20 min human enhancement)
"
git push origin docs/enrollment-service-documentation
```

**Create PR** (in GitHub/Azure DevOps):
- Title: `docs: Add EnrollmentService baseline documentation`
- Link to work item: `FN12345_US067` (if using Azure Boards)
- Request review from: Tech Lead or senior developer
- Labels: `documentation`, `service-layer`

**PR description template**:
```markdown
## Summary
Baseline documentation for EnrollmentService following AKR_CHARTER_BACKEND.md conventions.

## Documentation Level
🔶 Baseline (70% complete) - Production-ready

## What's Included
- ✅ Service identification
- ✅ Quick reference (what, when, watch out for)
- ✅ What & Why (purpose, capabilities, scope)
- ✅ Primary operation flow (EnrollUserAsync)
- ✅ Business rules (3 rules with rationale)
- ✅ Architecture (dependencies and consumers with failure modes)
- ✅ Data operations (reads, writes, side effects)
- ✅ Questions & gaps (3 flagged items)

## Optional Sections Not Included (Can Add Later)
- ⏳ Alternative paths (not complex enough yet)
- ⏳ Performance metrics (no production data yet)
- ⏳ Known issues (none discovered yet)
- ⏳ External dependencies (no third-party integrations)

## Business Context Added
- Regulatory requirements (State Reg 45.301 for prerequisites)
- Cost implications ($500/course duplicate enrollment prevention)
- System capacity constraints (LMS license limits)
- Historical context (why rules exist)

## Questions Identified
- [ ] Clarify CourseService bug workaround (ask John)
- [ ] Determine if admin notification needed on capacity failures (ask PM)
- [ ] Validate 24-hour email retry window with compliance team

## Time Investment
- AI generation: 5 minutes
- Human enhancement: 20 minutes
- Total: 25 minutes

## Checklist
- [x] All 🤖 markers present for AI-generated content
- [x] All ❓ markers addressed or flagged as questions
- [x] Business rules include "Why It Exists" rationale
- [x] Flow diagram includes business WHY and impact
- [x] Dependencies documented with failure modes
- [x] Follows AKR_CHARTER_BACKEND.md conventions
- [x] File named correctly (EnrollmentService_doc.md)
```

---

## Common Scenarios and Solutions

### Scenario 1: Legacy Project with Unclear Architecture

**Problem**: Can't identify which layer is the "service"

**Solution**:
1. Start with the controller - it's usually obvious (has `[HttpPost]` attributes)
2. Look at controller constructor - what dependencies are injected?
3. The injected class that's NOT a repository is likely the service
4. If no clear service layer, document the class that contains business logic

**Example**:
```csharp
// Controller
public class EnrollmentsController : ControllerBase
{
    private readonly EnrollmentManager _manager;  // ← This is your "service"
    
    [HttpPost]
    public async Task<IActionResult> Enroll(EnrollRequest request)
    {
        var result = await _manager.ProcessEnrollment(request);
        return Ok(result);
    }
}

// Document EnrollmentManager even though it's not named "Service"
```

---

### Scenario 2: Service Has Too Many Dependencies

**Problem**: Service constructor has 10+ dependencies, can't attach all files

**Solution**:
1. **Attach only the core dependencies** (3-5 most important)
2. Priority: Repositories > Other services > External APIs
3. In documentation, list all dependencies but focus detail on critical ones
4. Use ⚠️ emoji to mark critical dependencies

**Example**:
```markdown
## Dependencies

### Critical Dependencies (Attached for AI Context)
| Dependency | Purpose | Failure Mode |
|------------|---------|--------------|
| ⚠️ `IEnrollmentRepository` | Database operations | BLOCKING |
| ⚠️ `ICourseService` | Prerequisite validation | BLOCKING |
| ⚠️ `IEmailService` | User notifications | NON-BLOCKING |

### Additional Dependencies (Not Critical)
| Dependency | Purpose | Failure Mode |
|------------|---------|--------------|
| `ILogger<EnrollmentService>` | Diagnostic logging | Non-blocking, logged to void if fails |
| `IMemoryCache` | Performance optimization | Non-blocking, degrades to database query |
| `IMetricsService` | Usage metrics | Non-blocking, fire-and-forget |
```

---

### Scenario 3: CQRS Architecture (Commands and Queries Separate)

**Problem**: No single "service" - logic split between command handlers and query handlers

**Solution**:
Document command handlers and query handlers separately, treating each as a "service"

**File naming**:
```
docs/services/EnrollUserCommandHandler_doc.md
docs/services/GetEnrollmentsQueryHandler_doc.md
```

**Prompt adjustment**:
```
**Target service**: EnrollUserCommandHandler (CQRS Command pattern)

[Rest of standard prompt...]
```

**In documentation**:
```markdown
# Service: EnrollUserCommandHandler

**Pattern**: CQRS Command Handler  
**Command**: EnrollUserCommand  
**Returns**: EnrollmentResult

**What & Why**:
This is a CQRS command handler responsible for the enrollment write operation.
Query operations are handled separately by GetEnrollmentsQueryHandler.
```

---

### Scenario 4: Service Uses Dependency Injection from Multiple Places

**Problem**: Service is used by controller, background job, and another service. Which to attach?

**Solution**:
**Attach the most common usage** (usually the controller), document others in "Consumers" section

**Example**:
```markdown
## Architecture

### Consumers (Who Uses This Service)

| Consumer | Use Case | Impact of Failure |
|----------|----------|-------------------|
| `EnrollmentsController` | User enrolls via web UI (80% of usage) | HTTP 500, user sees error page |
| `BatchEnrollmentJob` | Bulk enrollment import (15% of usage) | Job fails, admin notified, retry scheduled |
| `MobileApiController` | Mobile app enrollment (5% of usage) | API error, app shows retry button |
| `NotificationService` | Re-enrollment reminders | Background process, logged and skipped |
```

---

### Scenario 5: Copilot Output is Poor Quality

**Problem**: AI generated documentation is incomplete, incorrect, or nonsensical

**Troubleshooting steps**:

**Step 1: Check file attachments**
- Did you attach service implementation (not just interface)?
- Did you attach repository?
- Are attached files the correct ones (not unrelated services)?

**Step 2: Simplify prompt**
- Remove optional instructions
- Focus on structure generation first
- Ask for specific sections individually

**Step 3: Try fewer files**
- Start with just service file
- If output improves, incrementally add repository, then controller

**Step 4: Regenerate**
- Click "Regenerate" in Copilot Chat
- AI is probabilistic, second attempt may be better

**Step 5: Manual fallback**
- Copy template manually
- Ask Copilot to fill specific sections:
  - "Extract business rules from EnrollmentService"
  - "List dependencies from EnrollmentService constructor"
  - "Create flow diagram for EnrollUserAsync method"

**Step 6: Last resort - manual documentation**
- Use template as guide
- Fill in sections manually
- Still faster than writing from scratch (template provides structure)

---

## Quality Checklist

Use this checklist before submitting PR:

### Structure and Format
- [ ] All 8 baseline sections present
- [ ] Sections in correct order (matches template)
- [ ] Markdown formatting valid (renders correctly)
- [ ] File named correctly (`[ServiceName]_doc.md`)

### Technical Accuracy
- [ ] Service name, namespace, file location correct
- [ ] Method signatures match actual code
- [ ] Dependencies list matches constructor parameters
- [ ] Database tables match repository calls
- [ ] Exception types match throw statements
- [ ] Flow diagram steps match actual code flow

### AI Markers
- [ ] All AI-generated content marked with 🤖
- [ ] All sections needing human input marked with ❓
- [ ] Questions & Gaps section has flagged items
- [ ] No unmarked content (everything has 🤖 or ❓)

### Business Context
- [ ] "Why It Exists" column completed for all business rules
- [ ] Business rationale provided (regulatory, cost, historical)
- [ ] Flow diagram "Why" fields completed (business reason for each step)
- [ ] Flow diagram "Impact" fields completed (business consequence of failure)
- [ ] Failure modes documented for dependencies (blocking vs non-blocking)
- [ ] Quick Reference "Watch out for" includes real gotchas

### Completeness
- [ ] All ❓ markers addressed or moved to Questions & Gaps
- [ ] Business rules have Rule ID (BR-[SVC]-###), Description, Why, Since
- [ ] Dependencies have Failure Mode and Critical? columns
- [ ] Data Operations have Business Context column
- [ ] No placeholder text like "[TODO]" or "[Fill this in]"

### Conventions
- [ ] Business rules use BR-[SVC]-### format (e.g., BR-ENR-001)
- [ ] Flow diagram is text-based boxes (NOT Mermaid)
- [ ] Feature tag in commit message (FN#####_US#####)
- [ ] Cross-references to database docs use correct format
- [ ] Cross-references to API docs use correct format

---

## Time-Saving Tips

### Tip 1: Document in Batches
Document 3-5 related services in one sitting. Context switching costs time.

**Example batch**:
1. EnrollmentService (25 min)
2. CourseService (20 min - similar to Enrollment)
3. UserService (20 min - similar patterns)

**Total**: 65 minutes for 3 services (faster than 75 min if done separately)

---

### Tip 2: Reuse Business Context
If services share business rules, copy rationale across services.

**Example**:
```markdown
BR-ENR-002 in EnrollmentService:
"State licensing requirement (Regulation 45.301). Incomplete prerequisites = 
invalid certification = legal liability."

BR-COURSE-004 in CourseService (similar rule):
"State licensing requirement (Regulation 45.301). Course cannot be offered 
without approved curriculum = legal liability."
```

---

### Tip 3: Document After Code Review
Best time to document: Right after code review, before merge.
- Context fresh in your mind
- Code structure finalized (no more changes expected)
- Business rules clarified during review

---

### Tip 4: Collaborate on Business Context
Don't know business rationale? Ask during documentation:
- Product owner for business rules justification
- Tech lead for architectural decisions
- Domain expert for regulatory requirements
- Original developer for historical context

**Slack message template**:
```
@product-owner Quick question for EnrollmentService documentation:

BR-ENR-003: "Maximum 5 active enrollments per user"

Why 5 specifically? Is this:
- Technical limitation (system capacity)?
- Business rule (prevent seat hoarding)?
- Arbitrary number (can be increased)?

Need to document rationale for the team. Thanks!
```

---

### Tip 5: Use Documentation During Code Review
Documentation finds bugs before production:
- Writing "Why" forces you to question assumptions
- Flow diagram exposes logic gaps
- Business rules table reveals inconsistencies

**Example**: Documenting EnrollmentService revealed prerequisite validation was missing for admin override path. Bug fixed before production.

---

## Troubleshooting Guide

### Issue: Copilot doesn't generate business rules table

**Cause**: AI doesn't detect validation logic in code

**Solution**:
1. Manually search for validation in service:
   - `if` statements checking conditions
   - `throw new BusinessRuleException`
   - Method names containing "Validate"
2. Create table structure manually
3. Ask Copilot: "Extract validation rules from EnrollmentService as table"

---

### Issue: Flow diagram is Mermaid instead of text boxes

**Cause**: Copilot defaults to Mermaid (common diagram format)

**Solution**:
1. Regenerate with explicit instruction: "Use text-based boxes with ┌─┐ characters, NOT Mermaid"
2. Or manually convert Mermaid to text boxes (5 minutes)

**Mermaid → Text conversion**:
```
Mermaid:
graph TD
    A[Validate Prerequisites] --> B[Check Capacity]
    B --> C[Create Enrollment]

Text boxes:
┌─────────────────────────────┐
│ Validate Prerequisites      │
└─────────────────────────────┘
            ↓
┌─────────────────────────────┐
│ Check Capacity              │
└─────────────────────────────┘
            ↓
┌─────────────────────────────┐
│ Create Enrollment           │
└─────────────────────────────┘
```

---

### Issue: AI hallucinated methods that don't exist

**Cause**: AI inferring likely methods based on naming patterns

**Solution**:
1. Compare generated doc against actual code (line by line)
2. Delete hallucinated content
3. Flag in PR: "Verified against actual code, removed AI hallucinations"

**Prevention**: Attach implementation files (not just interfaces)

---

### Issue: Documentation too generic, no business context

**Cause**: You skipped Step 6 (human enhancement)

**Solution**:
Documentation without business context has little value. Must invest 20 minutes:
- Ask questions to product owner / domain experts
- Review requirements documents
- Check commit history for context
- Interview original developer

**Remember**: Code says WHAT, documentation says WHY. If doc just repeats WHAT from code, it's not useful.

---

## FAQ

**Q: Can I use ChatGPT instead of GitHub Copilot?**

A: Yes, but workflow is slightly different:
1. Copy service file content (not attach files)
2. Paste into ChatGPT with prompt
3. Copy output back to VS Code
4. Less convenient but works

**Limitation**: ChatGPT doesn't have workspace context, may miss dependencies.

---

**Q: Do I need to document every method in the service?**

A: No. Focus on **primary operations** (main business logic methods).

**Document**:
- ✅ `EnrollUserAsync` - core business operation
- ✅ `ValidatePrerequisites` - critical validation logic
- ✅ `CalculateEnrollmentFee` - complex calculation

**Don't document**:
- ❌ `MapToDto` - simple mapping, self-explanatory
- ❌ `ValidateNotNull` - trivial validation helper
- ❌ Private helper methods (document in code comments if needed)

**Rule of thumb**: Document methods called by consumers (controllers, other services).

---

**Q: What if service has no business rules?**

A: If service is truly just CRUD with no validation, state that:

```markdown
## Business Rules

This service performs straightforward CRUD operations with no business logic.
Validation is handled by the controller layer (FluentValidation).

If business rules are added in the future, document them here using BR-[SVC]-### format.
```

**Consider**: Maybe this shouldn't be a service? Simple CRUD can sometimes live in controller directly (see "Anemic Services" anti-pattern in AKR_CHARTER_BACKEND.md).

---

**Q: How do I document a service that calls multiple external APIs?**

A: Add "External Dependencies" optional section (triggered by external integrations):

```markdown
## External Dependencies

| External System | Purpose | Endpoint | Failure Behavior |
|----------------|---------|----------|------------------|
| Payment Gateway | Process enrollment fees | `https://api.stripe.com/v1/charges` | Timeout after 30s, retry 3 times, then fail enrollment |
| Email Service | Send confirmations | `https://api.sendgrid.com/v3/mail/send` | Non-blocking, queued for retry |

**Configuration**: Endpoints configured in `appsettings.json` under `ExternalServices`

**Circuit Breaker**: Enabled for Payment Gateway (trips after 5 consecutive failures)

**Monitoring**: External API failures logged to Application Insights with custom metric
```

---

**Q: Should I document private methods?**

A: Generally no. Documentation focuses on public interface (what consumers see).

**Exception**: Document private methods if:
- Complex business logic not obvious from code
- Shared pattern across team (reusable algorithm)
- Historical context needed (why built this way)

**Better approach**: Use code comments for private method documentation:
```csharp
/// <summary>
/// Calculates enrollment fee with early-bird discount logic.
/// Business rule BR-ENR-005: 20% discount if enrolled >30 days before course start.
/// Historical: Discount period was 14 days until Q3 2024, extended to 30 days per PM request.
/// </summary>
private decimal CalculateFeeWithDiscount(Course course, DateTime enrollmentDate) { }
```

---

**Q: How often should documentation be updated?**

A: **Update documentation in the same PR as code changes.**

**When code changes trigger documentation updates**:
- ✅ New business rule added → Update Business Rules table
- ✅ New dependency added → Update Architecture section
- ✅ Method signature changed → Update How It Works flow
- ✅ New error condition → Update Error handling
- ✅ Performance issue discovered → Add Performance section

**What doesn't require doc update**:
- ❌ Bug fix (no behavior change)
- ❌ Refactoring (internal change, same behavior)
- ❌ Code formatting, renaming variables

**Quarterly review**: Tech lead reviews all docs for staleness (every 3 months).

---

## Success Metrics

**You're successful when**:
- ✅ New developers reference docs instead of interrupting you
- ✅ Code reviews reference business rules by ID (BR-ENR-001)
- ✅ Fewer "why does this work this way?" questions
- ✅ Onboarding time reduced (new devs productive faster)
- ✅ Documentation stays current (updated with code changes)

**Documentation is working when**: Team uses it regularly without being forced.

---

## Getting Help

**Questions about this guide?**
- Check **AKR_CHARTER_BACKEND.md** for conventions
- Check **Backend_Service_Documentation_Guide.md** for system overview
- Ask Tech Lead or team documentation champion

**Copilot not working as expected?**
- Try with fewer files
- Simplify prompt
- Check GitHub Copilot status (may be down)
- Fall back to manual documentation with template

**Don't know business context?**
- Ask product owner for business rules rationale
- Ask domain expert for regulatory requirements
- Ask original developer for historical context
- Check requirements documents, Jira tickets, PRs

---

**Remember**: The goal is useful documentation in 25 minutes, not perfect documentation. Start with baseline (70% complete), enhance incrementally as you learn more.

---

**End of Developer Guide**
