# AKR Charter: Backend Service Documentation

**Version**: 1.1  
**Last Updated**: 2025-12-05  
**Change Summary**: Added API Contract Documentation, Middleware Pipeline, AI Context Accessibility, enhanced Validation Rules  
**Extends**: AKR_CHARTER.md (universal principles)  
**Applies To**: Backend services, business logic layer, domain services, application services

---

## Purpose

This charter extends the universal **AKR_CHARTER.md** with conventions specific to backend service documentation. It applies to service-layer components in backend applications (ASP.NET Core, Node.js, Java Spring, Python Django/FastAPI, etc.) where business logic resides.

**Prerequisites**: Read AKR_CHARTER.md first for:
- Core principles (Lean, Flexible, Evolutionary, etc.)
- Universal conventions (generic types, feature tags, Git format)
- Documentation tiers (Essential/Recommended/Optional)

**This charter adds**:
- Service layer naming and organizational patterns
- Backend service documentation structure
- Business logic documentation conventions
- Enterprise best practices for maintainable service documentation

---

## Service Layer Architecture Context

### What We Document

**Target:** Service/Business Logic Layer (where business rules live)

```
┌──────────────────────┐
│   Controllers        │  → API/presentation layer
│   (HTTP Endpoints)   │     Link to API documentation
└──────────────────────┘
           ↓
┌──────────────────────┐
│   ► SERVICES ◄       │  ← THIS is what we document
│   (Business Logic)   │     (This charter applies here)
│   - Validation       │
│   - Orchestration    │
│   - Business Rules   │
└──────────────────────┘
           ↓
┌──────────────────────┐
│   Repositories       │  → Data access layer
│   (Data Layer)       │     Straightforward CRUD
└──────────────────────┘
           ↓
┌──────────────────────┐
│   Database           │  → Use AKR_CHARTER_DB.md
│   (Persistence)      │     for database objects
└──────────────────────┘
```

**Why focus on services?**
- Contain business rules (the WHY, not just the WHAT)
- Orchestrate complex workflows across multiple repositories
- Enforce validation and authorization
- Handle cross-cutting concerns (logging, caching, notifications)
- Most complex and least self-documenting layer

**What we do NOT document here:**
- Controllers/API endpoints → Use existing API documentation system
- Repositories → Usually straightforward CRUD, minimal documentation needed
- Domain entities → Document only if complex business logic embedded
- Database objects → Use AKR_CHARTER_DB.md

---

## Service Naming Conventions

### Service Classes

**Format**: `[Entity/Domain]Service` or `[Capability]Service`

**Examples**:
- ✅ `EnrollmentService` (entity-based)
- ✅ `CourseService` (entity-based)
- ✅ `NotificationService` (capability-based)
- ✅ `EmailService` (capability-based)
- ✅ `UserAuthenticationService` (compound - clarity over brevity)
- ❌ `EnrollmentLogic` (avoid -Logic suffix)
- ❌ `ServiceEnrollment` (don't start with Service)
- ❌ `EnrollSvc` (avoid abbreviations)

**Namespace conventions**:
```
# ASP.NET Core / C#
YourApp.Services
YourApp.Domain.Services (if using DDD)

# Node.js / TypeScript
src/services/
src/domain/services/

# Java Spring
com.yourapp.services
com.yourapp.domain.services

# Python Django/FastAPI
yourapp/services/
yourapp/domain/services/
```

---

### Service Method Naming

**Format**: `Verb[Entity][Qualifier]`

**CRUD Operations:**
```
✅ GetCourseById(Guid id)
✅ GetActiveCourses()
✅ CreateCourse(CourseDto dto)
✅ UpdateCourse(Guid id, CourseDto dto)
✅ DeleteCourse(Guid id)
✅ SoftDeleteCourse(Guid id)  // If using soft delete pattern
```

**Business Operations:**
```
✅ EnrollUserInCourse(Guid userId, Guid courseId)
✅ ValidateEnrollmentEligibility(Guid userId, Guid courseId)
✅ CalculateCertificationExpiry(Guid enrollmentId)
✅ SendEnrollmentConfirmation(Guid enrollmentId)
✅ ProcessPendingEnrollments()  // Batch operations
```

**Query Methods:**
```
✅ GetEnrollmentsByUser(Guid userId)
✅ GetActiveEnrollmentsForCourse(Guid courseId)
✅ FindExpiredCertifications(DateTime asOfDate)
```

**Async conventions:**
```
# C# / ASP.NET Core
✅ EnrollUserInCourseAsync(...)
✅ GetActiveCourses Async(...)

# JavaScript / TypeScript
✅ async enrollUserInCourse(...)
✅ async getActiveCourses(...)

# Python
✅ async def enroll_user_in_course(...)
✅ async def get_active_courses(...)
```

---

### File and Documentation Naming

**Service implementation files:**
- `EnrollmentService.cs` (C#)
- `enrollment.service.ts` (TypeScript/Angular)
- `enrollmentService.js` (JavaScript)
- `enrollment_service.py` (Python)

**Service documentation files:**
- `EnrollmentService_doc.md`
- `CourseService_doc.md`
- `NotificationService_doc.md`

**Format**: `[ServiceName]_doc.md`

**Rationale**: 
- Consistent with AKR_CHARTER.md file naming conventions
- `_doc.md` suffix distinguishes from other markdown files
- PascalCase matches service class name (traceability)

---

## Service Documentation Structure

### Essential Sections (Tier 1 - Always Required)

**Minimum viable documentation** (15-20 minutes):

```markdown
✅ Service Identification
   - Name, namespace, file location, last updated, complexity

✅ Quick Reference (TL;DR)
   - What it does (1-2 sentences)
   - When to use it
   - Watch out for (critical gotchas)

✅ What & Why
   - Purpose: Technical + business context
   - Capabilities: What it can do
   - Not Responsible For: Scope boundaries

✅ Primary Operation(s)
   - Main method flow with step-by-step explanation
   - Input/output
   - Success/failure paths
```

**Time**: 15-20 minutes with AI assistance (AI generates 60%, human adds 40%)

---

### Recommended Sections (Tier 2 - Include When Applicable)

Add these when the information exists and is valuable:

```markdown
✅ Business Rules
   - Table format: Rule ID, Description, Why, Since When
   - Use BR-[SVC]-### format

✅ Architecture
   - Dependencies (what this service needs)
   - Consumers (who uses this service)
   - Failure modes (what happens when dependencies fail)

✅ Data Operations
   - Reads from (tables/sources)
   - Writes to (tables/destinations)
   - Side effects (emails, cache, events)

✅ Questions & Gaps
   - AI-flagged unknowns
   - Human-identified questions
   - Follow-up actions
```

**Time**: +10 minutes to baseline documentation

---

### Optional Sections (Tier 3 - Add When Needed)

**Event-driven documentation** - add sections when circumstances warrant:

```markdown
⏳ Alternative Paths
   Add when: Service has complex conditional logic, multiple workflows

⏳ Performance Considerations
   Add when: Production metrics available, bottlenecks identified

⏳ Known Issues & Limitations
   Add when: Bugs discovered, workarounds implemented, technical debt

⏳ External Dependencies
   Add when: Third-party API integrations, external systems

⏳ Common Problems & Solutions
   Add when: Support tickets, production incidents, troubleshooting patterns

⏳ What Could Break
   Add when: Planning major refactoring, assessing downstream impact

⏳ Security & Authorization
   Add when: Special security requirements, sensitive data handling

⏳ Testing Guidance
   Add when: Complex test setup, integration test patterns
```

**Time**: 10-15 minutes per optional section (add incrementally)

**Trigger examples:**
- Performance section → Production response times consistently >2 seconds
- Known Issues section → Bug discovered but fix delayed to next sprint
- External Dependencies → Integrating with payment gateway
- Common Problems section → Same support ticket opened 3+ times

---

## Service Documentation Patterns

### Business Rules Format

**Format**: `BR-[ServiceAbbreviation]-###: Rule description`

**Table structure:**

```markdown
| Rule ID | Description | Why It Exists | Since When |
|---------|-------------|---------------|------------|
| BR-ENR-001 | Users cannot enroll in same course twice | Prevent duplicate charges and confusion | v1.0 (2025-01) |
| BR-ENR-002 | Prerequisites must be completed before enrollment | State licensing requirement | v1.2 (2025-03) |
| BR-ENR-003 | Maximum 5 active enrollments per user | System capacity limitation | v1.0 (2025-01) |
```

**Key elements:**
- **Rule ID**: Consistent numbering (BR-[ServiceAbbr]-###)
- **Description**: WHAT the rule enforces (observable behavior)
- **Why It Exists**: Business rationale (most critical column - requires human input)
- **Since When**: Version or date added (helps understand evolution)

**Example in code comment:**
```csharp
// BR-ENR-001: Users cannot enroll in same course twice
if (await _repository.HasActiveEnrollment(userId, courseId))
{
    throw new BusinessRuleException("BR-ENR-001", "User already enrolled");
}
```

**Rationale**: 
- Links documentation to code
- Makes rules traceable in discussions
- Enables validation that all code rules are documented

---

### Flow Diagrams for Service Operations

**Format**: Text-based boxes (NOT Mermaid - better for diffs, markdown-native)

**Template:**
```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: [Action Name]                                        │
│  What  → [Technical action: call repository, validate data]  │
│  Why   → [Business reason for this step]                     │
│  Error → [Exceptions: InvalidOperation, NotFound, etc.]      │
│  Impact→ [Business consequence if this step fails]           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: [Action Name]                                        │
│  What  → [Technical action]                                  │
│  Why   → [Business reason]                                   │
│  Error → [Exceptions]                                        │
│  Impact→ [Business consequence]                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
                    [SUCCESS] or [FAILURE]
```

**Real example:**
```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Validate Prerequisites                               │
│  What  → Query prerequisite courses, check completion        │
│  Why   → State licensing requires prerequisite completion    │
│  Error → PrerequisiteNotMetException                         │
│  Impact→ User cannot enroll, enrollment request rejected     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Check Enrollment Capacity                            │
│  What  → Count user's active enrollments (MAX: 5)            │
│  Why   → System capacity limitation, prevent overload        │
│  Error → EnrollmentLimitExceededException                    │
│  Impact→ User must complete existing course before enrolling │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Create Enrollment Record                             │
│  What  → Insert to Enrollments table, set Status='Pending'   │
│  Why   → Track enrollment lifecycle from pending to complete │
│  Error → DatabaseException, DuplicateKeyException            │
│  Impact→ Enrollment fails, user notified to retry            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Send Confirmation Email                              │
│  What  → Queue email notification (async)                    │
│  Why   → User expects confirmation, business requirement     │
│  Error → EmailServiceException (non-blocking)                │
│  Impact→ Enrollment succeeds, email retry handled separately │
└─────────────────────────────────────────────────────────────┘
                          ↓
                      [SUCCESS]
```

**Why this format:**
- ✅ Text-based: Better Git diffs than images or Mermaid
- ✅ WHAT + WHY: Captures both technical action and business rationale
- ✅ Error handling: Documents exceptions and business impact
- ✅ ASCII-art: Renders in any markdown viewer
- ✅ AI-friendly: Copilot can generate this format from code

---

### Dependencies and Consumers Documentation

**Dependencies table** (what this service needs):

```markdown
| Dependency | Purpose | Failure Mode | Critical? |
|------------|---------|--------------|-----------|
| `ICourseRepository` | Retrieve course details | Throws DatabaseException | ⚠️ Blocking |
| `IEmailService` | Send notifications | Throws EmailException | ✅ Non-blocking (queued) |
| `IAuthorizationService` | Check user permissions | Throws UnauthorizedException | ⚠️ Blocking |
| `ICacheService` | Performance optimization | Returns null on miss | ✅ Graceful degradation |
```

**Key elements:**
- **Dependency**: Interface or service name
- **Purpose**: What it's used for (technical)
- **Failure Mode**: What exception occurs, fallback behavior
- **Critical?**: ⚠️ Blocking (service fails) or ✅ Non-blocking (continues)

**Consumers table** (who uses this service):

```markdown
| Consumer | Use Case | Impact of Failure |
|----------|----------|-------------------|
| `EnrollmentsController` | User enrolls via web UI | HTTP 500, user sees error page |
| `BatchEnrollmentJob` | Bulk enrollment import | Job fails, admin notified, retry scheduled |
| `MobileApiController` | Mobile app enrollment | API error response, app shows retry |
```

**Key elements:**
- **Consumer**: Controller, job, or other service
- **Use Case**: What scenario triggers this
- **Impact of Failure**: User-facing? Background? Critical?

**Rationale**: 
- Documents coupling (which services depend on each other)
- Clarifies failure behavior (blocking vs non-blocking)
- Helps assess impact of changes

---

### Data Operations Documentation

**Reads From:**

```markdown
| Table/Source | Purpose | Business Context |
|--------------|---------|------------------|
| `training.Courses` | Retrieve course details, prerequisites | Needed to validate enrollment eligibility |
| `training.Enrollments` | Check existing enrollments | Prevent duplicate enrollments (BR-ENR-001) |
| `auth.Users` | Verify user exists and is active | Ensure valid user before creating enrollment |
```

**Writes To:**

```markdown
| Table/Destination | Operation | Business Purpose |
|-------------------|-----------|------------------|
| `training.Enrollments` | INSERT | Create enrollment record (lifecycle tracking) |
| `training.AuditLog` | INSERT | Compliance requirement (audit trail) |
| `training.UserProgress` | UPDATE | Track user's course progress |
```

**Side Effects:**

```markdown
| Side Effect | When | Blocking? | Business Purpose |
|-------------|------|-----------|------------------|
| Send enrollment email | After successful insert | ❌ Async (queued) | User expects confirmation |
| Invalidate cache | After enrollment created | ❌ Fire-and-forget | Keep dashboard data fresh |
| Publish event | After enrollment status change | ❌ Event bus | Notify downstream systems |
| Write audit log | Before any database write | ⚠️ Blocking | Compliance requirement |
```

**Key conventions:**
- **Cross-repository references**: Link to table documentation
  - Format: `See [Courses table](../../database-repo/docs/tables/Courses_doc.md)`
- **Business Context**: WHY this data is needed (not just WHAT)
- **Blocking behavior**: Critical for understanding failure impact

---

## Enterprise Best Practices

### 1. Separation of Concerns

**DO:**
```csharp
// ✅ Service handles business logic
public class EnrollmentService
{
    public async Task<EnrollmentResult> EnrollUserAsync(Guid userId, Guid courseId)
    {
        // Validation
        await ValidatePrerequisites(userId, courseId);
        
        // Business logic
        var enrollment = CreateEnrollment(userId, courseId);
        
        // Persistence
        await _repository.AddAsync(enrollment);
        
        // Side effects
        await _emailService.SendConfirmationAsync(enrollment.Id);
        
        return EnrollmentResult.Success(enrollment);
    }
}
```

**DON'T:**
```csharp
// ❌ Controller handling business logic (violates SoC)
[HttpPost]
public async Task<IActionResult> Enroll(EnrollmentRequest request)
{
    // ❌ Business rules in controller
    if (await _db.Enrollments.AnyAsync(e => e.UserId == request.UserId))
        return BadRequest("Already enrolled");
    
    // ❌ Direct database access from controller
    var enrollment = new Enrollment { UserId = request.UserId, ... };
    _db.Enrollments.Add(enrollment);
    await _db.SaveChangesAsync();
    
    return Ok();
}
```

**Document this pattern:**
```markdown
## Architecture

This service follows **Separation of Concerns** principle:
- Controllers → Handle HTTP concerns (routing, serialization)
- Services → Handle business logic (THIS service)
- Repositories → Handle data access (CRUD operations)
- Domain entities → Handle domain invariants

**Rationale**: Business logic centralized in service layer enables:
- Reuse across multiple controllers (web, mobile, batch jobs)
- Testability (mock dependencies, test business rules in isolation)
- Maintainability (single place to update business logic)
```

---

### 2. Dependency Injection

**DO:**
```csharp
// ✅ Constructor injection - explicit dependencies
public class EnrollmentService : IEnrollmentService
{
    private readonly IEnrollmentRepository _repository;
    private readonly ICourseRepository _courseRepository;
    private readonly IEmailService _emailService;
    private readonly ILogger<EnrollmentService> _logger;
    
    public EnrollmentService(
        IEnrollmentRepository repository,
        ICourseRepository courseRepository,
        IEmailService emailService,
        ILogger<EnrollmentService> logger)
    {
        _repository = repository;
        _courseRepository = courseRepository;
        _emailService = emailService;
        _logger = logger;
    }
}
```

**DON'T:**
```csharp
// ❌ Service locator anti-pattern
public class EnrollmentService
{
    public async Task EnrollAsync(Guid userId, Guid courseId)
    {
        var repository = ServiceLocator.Get<IEnrollmentRepository>();
        var emailService = ServiceLocator.Get<IEmailService>();
        // ...
    }
}
```

**Document dependencies:**
```markdown
## Dependencies

This service uses **Constructor Injection** for all dependencies:

| Dependency | Lifetime | Purpose |
|------------|----------|---------|
| `IEnrollmentRepository` | Scoped | Database operations |
| `ICourseRepository` | Scoped | Course data retrieval |
| `IEmailService` | Singleton | Email notifications |
| `ILogger<EnrollmentService>` | Singleton | Diagnostic logging |

**Testability**: All dependencies mockable for unit testing.

**Registration** (in `Program.cs` or `Startup.cs`):
```csharp
services.AddScoped<IEnrollmentService, EnrollmentService>();
services.AddScoped<IEnrollmentRepository, EnrollmentRepository>();
// ...
```
```

---

### 3. Exception Handling

**DO:**
```csharp
// ✅ Business exceptions with clear messages
public async Task<EnrollmentResult> EnrollUserAsync(Guid userId, Guid courseId)
{
    var course = await _courseRepository.GetByIdAsync(courseId);
    if (course == null)
        throw new EntityNotFoundException($"Course {courseId} not found");
    
    if (await HasActiveEnrollment(userId, courseId))
        throw new BusinessRuleException("BR-ENR-001", "User already enrolled");
    
    if (!await MeetsPrerequisites(userId, courseId))
        throw new PrerequisiteNotMetException(
            $"User {userId} does not meet prerequisites for course {courseId}");
    
    // ... success path
}
```

**DON'T:**
```csharp
// ❌ Generic exceptions, no context
public async Task EnrollUserAsync(Guid userId, Guid courseId)
{
    var course = await _courseRepository.GetByIdAsync(courseId);
    if (course == null)
        throw new Exception("Not found");  // ❌ Too generic
    
    if (await HasActiveEnrollment(userId, courseId))
        throw new Exception("Error");  // ❌ No context
}
```

**Document error handling:**
```markdown
## Error Handling

### Custom Exceptions

| Exception | When Thrown | HTTP Status | Retry? |
|-----------|-------------|-------------|--------|
| `EntityNotFoundException` | Course/User not found | 404 | ❌ No |
| `BusinessRuleException` | Business rule violated | 400 | ❌ No |
| `PrerequisiteNotMetException` | Prerequisites incomplete | 400 | ❌ No |
| `EnrollmentLimitException` | Max enrollments exceeded | 429 | ✅ Yes (after course completion) |
| `DatabaseException` | Database error | 500 | ✅ Yes (transient) |

### Error Response Format

```json
{
  "errorCode": "BR-ENR-001",
  "message": "User already enrolled in this course",
  "timestamp": "2025-10-31T14:30:00Z",
  "details": {
    "userId": "123e4567-e89b-12d3-a456-426614174000",
    "courseId": "223e4567-e89b-12d3-a456-426614174000"
  }
}
```

**Logging**: All exceptions logged with correlation ID for troubleshooting.
```

---

### 4. Async/Await Best Practices

**DO:**
```csharp
// ✅ Async all the way down
public async Task<EnrollmentResult> EnrollUserAsync(Guid userId, Guid courseId)
{
    var course = await _courseRepository.GetByIdAsync(courseId);
    var user = await _userRepository.GetByIdAsync(userId);
    
    // Validate
    await ValidatePrerequisitesAsync(userId, courseId);
    
    // Create enrollment
    var enrollment = CreateEnrollment(user, course);
    await _repository.AddAsync(enrollment);
    
    // Side effects (fire-and-forget OK for non-critical)
    _ = _emailService.SendConfirmationAsync(enrollment.Id);
    
    return EnrollmentResult.Success(enrollment);
}
```

**DON'T:**
```csharp
// ❌ Mixing sync/async, blocking calls
public async Task<EnrollmentResult> EnrollUserAsync(Guid userId, Guid courseId)
{
    var course = _courseRepository.GetById(courseId);  // ❌ Sync call
    var user = await _userRepository.GetByIdAsync(userId);
    
    // ❌ Blocking on async
    ValidatePrerequisitesAsync(userId, courseId).Wait();
    
    // ❌ Can cause deadlocks
    var result = ValidateAsync().Result;
}
```

**Document async behavior:**
```markdown
## Asynchronous Operations

**All public methods are async** to avoid thread pool starvation:
- Database operations: `await _repository.GetByIdAsync(...)`
- External API calls: `await _emailService.SendAsync(...)`
- Cache operations: `await _cache.GetOrSetAsync(...)`

### Fire-and-Forget Operations

| Operation | Why Fire-and-Forget | Error Handling |
|-----------|---------------------|----------------|
| Email notifications | Non-critical, user already enrolled | Logged + retry queue |
| Cache invalidation | Performance optimization, not required | Logged, no retry |
| Analytics events | Nice-to-have, not required for success | Logged, no retry |

**Pattern:**
```csharp
// Non-blocking side effect
_ = _emailService.SendConfirmationAsync(enrollmentId);
```

**Caution**: Only use for truly non-critical operations.
```

---

### 5. Transaction Management

**DO:**
```csharp
// ✅ Explicit transaction scope for multi-operation consistency
public async Task<EnrollmentResult> EnrollUserAsync(Guid userId, Guid courseId)
{
    using var transaction = await _dbContext.Database.BeginTransactionAsync();
    
    try
    {
        // Step 1: Create enrollment
        var enrollment = new Enrollment { UserId = userId, CourseId = courseId };
        await _repository.AddAsync(enrollment);
        
        // Step 2: Update user progress
        var progress = await _progressRepository.GetByUserIdAsync(userId);
        progress.ActiveEnrollments++;
        await _progressRepository.UpdateAsync(progress);
        
        // Step 3: Commit if both succeed
        await transaction.CommitAsync();
        
        return EnrollmentResult.Success(enrollment);
    }
    catch
    {
        await transaction.RollbackAsync();
        throw;
    }
}
```

**Document transaction scope:**
```markdown
## Transaction Management

### Operations Using Transactions

**EnrollUserAsync** uses explicit transaction:
- **Why**: Enrollment + UserProgress update must be atomic
- **Scope**: 2 tables (Enrollments, UserProgress)
- **Rollback conditions**: Any database error, validation failure after initial insert
- **Performance**: Typical duration <100ms

**Pattern:**
```csharp
using var transaction = await _dbContext.Database.BeginTransactionAsync();
try
{
    // Multi-step operations
    await transaction.CommitAsync();
}
catch
{
    await transaction.RollbackAsync();
    throw;
}
```

### Operations NOT Using Transactions

- **GetEnrollmentsByUserAsync**: Read-only, no transaction needed
- **SendEmailConfirmationAsync**: Side effect, separate from database transaction
```

---

### 6. Logging and Observability

**DO:**
```csharp
// ✅ Structured logging with context
public async Task<EnrollmentResult> EnrollUserAsync(Guid userId, Guid courseId)
{
    _logger.LogInformation(
        "Starting enrollment: UserId={UserId}, CourseId={CourseId}",
        userId, courseId);
    
    try
    {
        var result = await ProcessEnrollmentAsync(userId, courseId);
        
        _logger.LogInformation(
            "Enrollment successful: EnrollmentId={EnrollmentId}, UserId={UserId}, CourseId={CourseId}",
            result.EnrollmentId, userId, courseId);
        
        return result;
    }
    catch (BusinessRuleException ex)
    {
        _logger.LogWarning(ex,
            "Enrollment failed - business rule: Rule={RuleId}, UserId={UserId}, CourseId={CourseId}",
            ex.RuleId, userId, courseId);
        throw;
    }
    catch (Exception ex)
    {
        _logger.LogError(ex,
            "Enrollment failed - unexpected error: UserId={UserId}, CourseId={CourseId}",
            userId, courseId);
        throw;
    }
}
```

**Document logging conventions:**
```markdown
## Logging & Observability

### Log Levels

| Level | When Used | Example |
|-------|-----------|---------|
| **Debug** | Detailed flow for troubleshooting | "Checking prerequisite: CourseId={CourseId}" |
| **Information** | Normal operation events | "Enrollment successful: EnrollmentId={Id}" |
| **Warning** | Expected exceptions, business rules | "Enrollment denied - prerequisite not met" |
| **Error** | Unexpected exceptions | "Database connection failed during enrollment" |

### Structured Logging

**Always include context**:
- `UserId`: Who performed the action
- `CourseId` / `EnrollmentId`: What entity was affected
- `CorrelationId`: Request tracking (added by middleware)

**Query logs** (using Serilog/Seq/Application Insights):
```
EnrollmentService AND UserId="123e4567-e89b-12d3-a456-426614174000"
```

### Performance Metrics

**Logged automatically**:
- Method execution duration
- Database query duration
- External API call duration

**Monitored thresholds**:
- EnrollUserAsync: <500ms (p95)
- GetEnrollmentsByUserAsync: <200ms (p95)
```

---

### 7. Validation and Input Sanitization

**DO:**
```csharp
// ✅ Validate at service layer, defensive programming
public async Task<EnrollmentResult> EnrollUserAsync(Guid userId, Guid courseId)
{
    // Guard clauses
    if (userId == Guid.Empty)
        throw new ArgumentException("UserId cannot be empty", nameof(userId));
    
    if (courseId == Guid.Empty)
        throw new ArgumentException("CourseId cannot be empty", nameof(courseId));
    
    // Business validation
    var course = await _courseRepository.GetByIdAsync(courseId);
    if (course == null)
        throw new EntityNotFoundException($"Course {courseId} not found");
    
    if (!course.IsActive)
        throw new BusinessRuleException("BR-COURSE-001", "Cannot enroll in inactive course");
    
    // ... proceed with enrollment
}
```

#### FluentValidation Extraction Pattern

When services use FluentValidation, extract rules into documentation format:

**Source code (FluentValidation):**
```csharp
public class CreateEnrollmentValidator : AbstractValidator<CreateEnrollmentRequest>
{
    public CreateEnrollmentValidator()
    {
        RuleFor(x => x.UserId)
            .NotEmpty().WithMessage("User ID is required");
        
        RuleFor(x => x.CourseId)
            .NotEmpty().WithMessage("Course ID is required");
        
        RuleFor(x => x.Notes)
            .MaximumLength(500).WithMessage("Notes cannot exceed 500 characters");
    }
}
```

**Documented format:**
```markdown
## Validation Rules

> 🤖 **AI-Extractable**: Rules below are derived from `CreateEnrollmentValidator.cs`

| Field | Rule | Error Message | Category |
|-------|------|---------------|----------|
| `UserId` | Required | "User ID is required" | Input |
| `CourseId` | Required | "Course ID is required" | Input |
| `Notes` | Max 500 chars | "Notes cannot exceed 500 characters" | Format |
```

#### Validation Categories

Use consistent categories for validation rules:

| Category | Description | Examples |
|----------|-------------|----------|
| **Input** | Required fields, null checks | NotEmpty, NotNull |
| **Format** | Data format requirements | MaxLength, Regex, Email |
| **Range** | Numeric/date boundaries | GreaterThan, Between |
| **Business** | Domain-specific rules | Must be enrolled, prerequisite check |
| **Security** | Auth/permission validation | Role check, ownership |

**Document validation rules:**
```markdown
## Validation Rules

### Input Validation (Technical)

| Parameter | Validation | Exception |
|-----------|------------|-----------|
| `userId` | Not Guid.Empty, exists in database | ArgumentException, EntityNotFoundException |
| `courseId` | Not Guid.Empty, exists in database | ArgumentException, EntityNotFoundException |
| `enrollmentDate` | Not in future, not >1 year past | ArgumentException |

### Business Validation

| Rule | Validation Logic | Business Rule ID |
|------|------------------|------------------|
| Course must be active | `course.IsActive == true` | BR-COURSE-001 |
| Prerequisites must be met | All prerequisite courses completed | BR-ENR-002 |
| Enrollment limit not exceeded | `activeEnrollments < 5` | BR-ENR-003 |
| No duplicate enrollments | No existing active enrollment | BR-ENR-001 |

**Validation Order**:
1. Input validation (technical correctness)
2. Entity existence validation
3. Business rule validation
4. Authorization validation

**Rationale**: Fail fast, provide clear error messages.
```

---

## Middleware Pipeline Documentation

### When to Document Middleware

**Document middleware when:**
- Custom exception handling filters exist
- Authentication/authorization middleware is customized
- Request/response transformation occurs
- Rate limiting or throttling is implemented
- Correlation ID or logging middleware is used

### Middleware Documentation Format

```markdown
## Middleware Pipeline

### Request Flow
```
Request → [Auth] → [RateLimit] → [Correlation] → Controller → [ExceptionFilter] → Response
```

### Exception Handling Flow

```
Exception Thrown
       ↓
┌─────────────────────────┐
│ GlobalExceptionFilter   │
└─────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│ Exception Type?                         │
├─────────────────────────────────────────┤
│ ValidationException    → 400 BadRequest │
│ NotFoundException      → 404 NotFound   │
│ BusinessRuleException  → 409 Conflict   │
│ UnauthorizedException  → 401 Unauth     │
│ Other                  → 500 Internal   │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────┐
│ Structured Error Response │
│ { code, message, details }│
└─────────────────────────┘
```
```

### Error Response Model

**Standard error response structure:**
```json
{
  "code": "VALIDATION_ERROR",
  "message": "One or more validation errors occurred",
  "details": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ],
  "correlationId": "abc-123-def",
  "timestamp": "2025-12-05T10:30:00Z"
}
```

**Document in service files:**
```markdown
### Error Response Model

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Machine-readable error code |
| `message` | string | Human-readable description |
| `details` | array | Field-level errors (validation) |
| `correlationId` | string | Request tracking ID |
| `timestamp` | ISO8601 | When error occurred |
```

---

## AI-Assisted Documentation Workflow

### AI Context Accessibility

> ⚠️ **Critical Understanding**: AI assistants operate only within the repository context. They cannot:
> - Follow external URLs (API portals, wikis, Confluence)
> - Access Azure APIM or Swagger UI
> - Read linked documentation outside the repo
> - Query databases or live systems

**What AI CAN access:**
- ✅ All files in the repository
- ✅ Code comments and XML documentation
- ✅ Markdown files in docs/ folders
- ✅ Configuration files (appsettings.json, etc.)
- ✅ Test files showing usage patterns

**Implications for documentation:**

| Information Type | Make Available In-Repo? | Method |
|------------------|------------------------|--------|
| API endpoints & contracts | ✅ Yes | API Contract section |
| Validation rules | ✅ Yes | Extract from validators |
| Error codes & responses | ✅ Yes | Error Response Model section |
| Business rules | ✅ Yes | BR-XXX-### format |
| External API contracts | ✅ Yes | Integration section |
| Interactive API testing | ❌ No (link only) | Portal URL |
| Full OpenAPI spec | ❌ No (too verbose) | Link to generated spec |

### AI Extraction Rules

When Copilot analyzes service documentation, it extracts:

| Rule # | What AI Extracts | From Section |
|--------|------------------|-------------|
| 1 | Service purpose and scope | Header, Purpose |
| 2 | Method signatures and parameters | Primary Operations |
| 3 | Business rules with IDs | Business Rules table |
| 4 | Dependencies and integrations | Dependencies section |
| 5 | Error handling patterns | Error Handling section |
| 6 | Configuration requirements | Configuration section |
| 7 | **API routes and parameters** | API Contract section |
| 8 | **Request/response models** | API Contract section |
| 9 | **Validation rules by field** | Validation Rules table |
| 10 | **Error codes and status mapping** | Error Response Model |
| 11 | **Middleware pipeline flow** | Middleware section |

---

### Human/AI Responsibility Split

**AI generates (60-70%):**
- ✅ Service structure and method signatures
- ✅ Dependencies from constructor injection
- ✅ Database tables from repository calls
- ✅ Exception types from throw statements
- ✅ Flow diagram structure from method body
- ✅ Technical WHAT (observable from code)

**Human adds (30-40%):**
- ❓ Business WHY (intent, rationale)
- ❓ Business rule justification ("Why does this rule exist?")
- ❓ Historical context ("Why was this built this way?")
- ❓ Failure impact ("What breaks if this fails?")
- ❓ Performance characteristics (learned from production)
- ❓ Common gotchas ("What mistake do developers make?")

### Copilot Generation Instructions

**Standard prompt for service documentation:**

```
Generate service documentation following AKR_CHARTER_BACKEND.md conventions.

Use the lean_baseline_service_template.md as structure.

Include ONLY baseline sections:
1. Service Identification
2. Quick Reference (TL;DR)
3. What & Why
4. Primary Operation(s) with flow diagram
5. Business Rules (table format: ID, Description, Why, Since)
6. Architecture (Dependencies and Consumers tables)
7. Data Operations (Reads, Writes, Side Effects)
8. Questions & Gaps

Mark content:
- 🤖 = AI-generated (WHAT code does)
- ❓ = Needs human input (WHY decisions, business context)

Use text-based flow diagrams (boxes with arrows, NOT Mermaid).

Extract from code:
- Method signatures, parameters, return types
- Dependencies from constructor
- Database tables from repository calls
- Exceptions from throw statements
- Validation logic for business rules

Flag for human review:
- Magic numbers, hardcoded values
- Comments saying "temporary" or "workaround"
- Complex conditional logic
- External API calls
- Performance concerns
```

### Time Estimates

**AI generation:**
- Structure extraction: 2 minutes
- Method analysis: 3 minutes
- Dependency mapping: 2 minutes
- **Total AI time: ~5-7 minutes**

**Human enhancement:**
- Business rule WHY: 5 minutes
- Flow diagram WHY annotations: 5 minutes
- Failure mode analysis: 3 minutes
- Quick reference gotchas: 2 minutes
- Questions & gaps review: 3 minutes
- **Total human time: ~18-20 minutes**

**Grand total: ~25 minutes per service (baseline quality)**

---

## Cross-Repository Integration

### Linking to Database Documentation

**When service operates on database tables:**

```markdown
## Data Operations

### Reads From

| Table | Purpose | Business Context |
|-------|---------|------------------|
| `training.Courses` | Retrieve course details | Validate course eligibility |
| `training.Enrollments` | Check existing enrollments | Prevent duplicates (BR-ENR-001) |

**Table schemas**: See database repository documentation:
- [Courses table](../../training-tracker-database/docs/tables/Courses_doc.md)
- [Enrollments table](../../training-tracker-database/docs/tables/Enrollments_doc.md)

**Cross-repository note**: If database and API are in separate repositories,
update links to reference external repository.
```

### Linking to API Documentation

**When service is called by controllers:**

```markdown
## Architecture

### Consumers (Who Uses This Service)

| Consumer | Use Case | Impact of Failure |
|----------|----------|-------------------|
| `EnrollmentsController` | User enrolls via web UI | HTTP 500, user sees error page |

**API documentation**: See API Reference Database for endpoint details:
- `POST /api/enrollments` → EnrollUserAsync method
- `GET /api/enrollments/{userId}` → GetEnrollmentsByUserAsync method

**Link**: [API Documentation System](http://your-api-docs-url)

**Rationale**: Avoid duplicating API contract details (request/response schemas).
Service documentation focuses on business logic, API docs focus on HTTP contract.
```

---

## Common Anti-Patterns to Avoid

### ❌ Don't: Anemic Services

**Bad** (anemic service - just passes through to repository):
```csharp
public class CourseService
{
    private readonly ICourseRepository _repository;
    
    public async Task<Course> GetByIdAsync(Guid id) 
        => await _repository.GetByIdAsync(id);
    
    public async Task CreateAsync(Course course) 
        => await _repository.AddAsync(course);
}
```

**Good** (service adds value - validation, business logic):
```csharp
public class CourseService
{
    private readonly ICourseRepository _repository;
    private readonly ILogger<CourseService> _logger;
    
    public async Task<Course> GetByIdAsync(Guid id)
    {
        if (id == Guid.Empty)
            throw new ArgumentException("Course ID cannot be empty");
        
        var course = await _repository.GetByIdAsync(id);
        if (course == null)
            throw new EntityNotFoundException($"Course {id} not found");
        
        return course;
    }
    
    public async Task CreateAsync(CreateCourseDto dto)
    {
        // BR-COURSE-002: Course title must be unique
        if (await _repository.ExistsWithTitleAsync(dto.Title))
            throw new BusinessRuleException("BR-COURSE-002", "Course title must be unique");
        
        // BR-COURSE-003: Duration must be between 1-52 weeks
        if (dto.DurationWeeks < 1 || dto.DurationWeeks > 52)
            throw new BusinessRuleException("BR-COURSE-003", "Duration must be 1-52 weeks");
        
        var course = new Course
        {
            Id = Guid.NewGuid(),
            Title = dto.Title,
            DurationWeeks = dto.DurationWeeks,
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        };
        
        await _repository.AddAsync(course);
        
        _logger.LogInformation("Course created: CourseId={CourseId}, Title={Title}", 
            course.Id, course.Title);
    }
}
```

**Rationale**: If service just passes through to repository, it adds no value. Services should contain business logic, validation, orchestration.

---

### ❌ Don't: God Services

**Bad** (service doing too much):
```csharp
public class EnrollmentService
{
    // ❌ Handles too many responsibilities
    public async Task EnrollUserAsync(...) { }
    public async Task SendEmailAsync(...) { }  // Should be EmailService
    public async Task ProcessPaymentAsync(...) { }  // Should be PaymentService
    public async Task GenerateCertificateAsync(...) { }  // Should be CertificateService
    public async Task NotifyAdminAsync(...) { }  // Should be NotificationService
}
```

**Good** (single responsibility):
```csharp
public class EnrollmentService
{
    private readonly IEnrollmentRepository _repository;
    private readonly IEmailService _emailService;  // ✅ Delegate to specialized services
    private readonly IPaymentService _paymentService;
    private readonly ICertificateService _certificateService;
    
    public async Task EnrollUserAsync(Guid userId, Guid courseId)
    {
        // ✅ Focus on enrollment business logic
        var enrollment = CreateEnrollment(userId, courseId);
        await _repository.AddAsync(enrollment);
        
        // ✅ Delegate side effects to specialized services
        await _emailService.SendEnrollmentConfirmationAsync(enrollment.Id);
    }
}
```

**Rationale**: Each service should have single, well-defined responsibility.

---

### ❌ Don't: Missing Error Handling

**Bad** (no error handling, let exceptions bubble):
```csharp
public async Task<Enrollment> EnrollUserAsync(Guid userId, Guid courseId)
{
    // ❌ No validation, no error handling
    var enrollment = new Enrollment { UserId = userId, CourseId = courseId };
    await _repository.AddAsync(enrollment);
    return enrollment;
}
```

**Good** (explicit error handling):
```csharp
public async Task<EnrollmentResult> EnrollUserAsync(Guid userId, Guid courseId)
{
    // ✅ Validate inputs
    var course = await _courseRepository.GetByIdAsync(courseId);
    if (course == null)
        throw new EntityNotFoundException($"Course {courseId} not found");
    
    // ✅ Check business rules
    if (await HasActiveEnrollment(userId, courseId))
        throw new BusinessRuleException("BR-ENR-001", "User already enrolled");
    
    try
    {
        var enrollment = new Enrollment { UserId = userId, CourseId = courseId };
        await _repository.AddAsync(enrollment);
        return EnrollmentResult.Success(enrollment);
    }
    catch (DbUpdateException ex)
    {
        _logger.LogError(ex, "Database error during enrollment");
        throw new DatabaseException("Failed to create enrollment", ex);
    }
}
```

---

### ❌ Don't: Hardcoded Configuration

**Bad** (magic numbers, hardcoded URLs):
```csharp
public class EnrollmentService
{
    public async Task EnrollUserAsync(Guid userId, Guid courseId)
    {
        // ❌ Magic number - what does 5 mean?
        if (await GetActiveEnrollmentCount(userId) >= 5)
            throw new Exception("Too many enrollments");
        
        // ❌ Hardcoded URL
        await _httpClient.GetAsync("https://api.example.com/courses");
    }
}
```

**Good** (configuration injected):
```csharp
public class EnrollmentService
{
    private readonly EnrollmentSettings _settings;
    
    public EnrollmentService(IOptions<EnrollmentSettings> settings)
    {
        _settings = settings.Value;
    }
    
    public async Task EnrollUserAsync(Guid userId, Guid courseId)
    {
        // ✅ Configuration value, well-named
        if (await GetActiveEnrollmentCount(userId) >= _settings.MaxActiveEnrollments)
            throw new EnrollmentLimitException(
                $"Maximum {_settings.MaxActiveEnrollments} active enrollments allowed");
        
        // ✅ Configured base URL
        await _httpClient.GetAsync($"{_settings.CourseApiBaseUrl}/courses");
    }
}

// appsettings.json
{
  "EnrollmentSettings": {
    "MaxActiveEnrollments": 5,
    "CourseApiBaseUrl": "https://api.example.com"
  }
}
```

**Document configuration:**
```markdown
## Configuration

### Required Settings

| Setting | Type | Default | Purpose |
|---------|------|---------|---------|
| `EnrollmentSettings:MaxActiveEnrollments` | int | 5 | BR-ENR-003: Maximum concurrent enrollments |
| `EnrollmentSettings:CourseApiBaseUrl` | string | (none) | External course catalog API endpoint |

**Location**: `appsettings.json` or environment variables

**Example**:
```json
{
  "EnrollmentSettings": {
    "MaxActiveEnrollments": 5,
    "CourseApiBaseUrl": "https://api.example.com"
  }
}
```
```

---

## Maintenance and Evolution

### When to Update Service Documentation

**Always update documentation when:**
- ✅ Adding new methods (document primary operations)
- ✅ Adding/changing business rules
- ✅ Adding dependencies or external integrations
- ✅ Changing failure behavior
- ✅ Discovering performance issues
- ✅ Discovering bugs or limitations

**Include documentation in same PR as code changes:**
```bash
git add src/Services/EnrollmentService.cs
git add docs/services/EnrollmentService_doc.md
git commit -m "feat: add prerequisite validation (FN12345_US067)

- Added ValidatePrerequisites method
- Business rule BR-ENR-002: Prerequisites must be completed
- Updated service documentation with new flow diagram
"
```

### Quarterly Documentation Review

**Recommended cadence**: Once per quarter

**Review checklist:**
- [ ] Are all services documented? (target: 90%+)
- [ ] Are business rules up-to-date?
- [ ] Are optional sections needed? (performance, known issues)
- [ ] Are Questions & Gaps answered?
- [ ] Are links to external docs still valid?

**Process:**
1. Tech Lead assigns review to team member
2. Team member reviews 5-10 services, notes issues
3. Team dedicates 2 hours to documentation updates
4. PRs created for updates

**Goal**: Keep documentation current without heroic effort.

---

## Quick Reference

### Creating New Service Documentation

**Steps:**
1. Copy `lean_baseline_service_template.md` to `docs/services/[ServiceName]_doc.md`
2. Use Copilot to generate baseline (5 minutes)
3. Enhance with business context (20 minutes)
4. Create PR with feature tag
5. Tech Lead reviews for accuracy and value
6. Merge when approved

**Time**: ~25 minutes for baseline documentation

---

### Reviewing Service Documentation PRs

**Tech Lead checklist:**
- [ ] Is this useful for the team?
- [ ] Is business context included (WHY, not just WHAT)?
- [ ] Are business rules documented with rationale?
- [ ] Are failure modes documented?
- [ ] Are all ❓ markers addressed?
- [ ] Does it follow AKR_CHARTER_BACKEND.md conventions?

**Not evaluated**: Perfect grammar, exact template match, exhaustive detail

---

## Questions & Support

**Questions about backend service conventions?**
- Reference this charter (AKR_CHARTER_BACKEND.md)
- Check universal charter (AKR_CHARTER.md)
- Check Backend_Service_Documentation_Guide.md for implementation details
- Ask Tech Lead or team

**Proposing changes to backend conventions?**
- Open PR with rationale
- Tag Tech Leads for review
- Expect discussion if affects multiple teams

**Need help documenting complex service?**
- Check templates for structure
- Ask team for examples
- Use Copilot to generate first draft
- Focus on business value, not perfection

---

**Remember**: Document to help the team understand WHY, not just WHAT. The best documentation is documentation that gets used and maintained.

---

**AKR Charter: Backend Service - End of Document**
