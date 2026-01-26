---
feature: [FEATURE_NAME]
domain: [DOMAIN]
layer: API
component: [SERVICE_NAME]
status: deployed
version: 1.0
componentType: Service
priority: P1
lastUpdated: [YYYY-MM-DD]
---

# Service: [SERVICE_NAME]

**Namespace/Project**: [Project.Services]  
**File Location**: `src/Services/[ServiceName].cs`  
**Complexity**: [Simple / Medium / Complex]  
**Criticality**: [High / Medium / Low]  
**Documentation Level**: 🟢 Standard (85% complete)

---

## Quick Reference (TL;DR)

**What it does:**  
[2-3 sentences on what service accomplishes and its business value]

**When to use it:**  
[Specific scenarios where this service should be used - web UI, API, background jobs, integrations]

**Critical dependencies:**  
[List top 3 most critical dependencies with failure impacts]

**Watch out for:**  
[Top 2-3 gotchas or common mistakes]

**SLA / Performance Target:**  
[Response time target if applicable, or "No SLA defined"]

---

## What & Why

### Purpose

**Technical:**  
[Detailed technical description of what service does]

**Business:**  
[Business purpose - what problem does this solve? Why did we build it? What business value?]

**Historical Context:**  
[When was this built? What prompted its creation? Any migration/replacement notes?]

### Capabilities

[Comprehensive bullet list of what service can do]

**Core Functions:**
- [Primary capability 1]
- [Primary capability 2]
- [Primary capability 3]

**Supporting Functions:**
- [Supporting capability 1]
- [Supporting capability 2]

### Not Responsible For

[Clear scope boundaries - what this service explicitly does NOT do]

**Out of Scope:**
- [What's handled by other services]
- [What's handled by controllers/UI]
- [What's future work (not yet implemented)]

---

## How It Works

### Primary Operation: [Main Method Name]

**Purpose:**  
[Detailed description of what this method accomplishes and business context]

**Input:**  
```csharp
[Method signature with parameter types]
```

**Output:**  
```csharp
[Return type and what it represents]
```

**Business Scenarios:**
- [Scenario 1: When/why this is called]
- [Scenario 2: Common use case]
- [Scenario 3: Edge case]

**Step-by-Step Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: [Action]                                             │
│  What  → [Technical action taken - method calls, logic]     │
│  Why   → [Business reason for this step]                    │
│  Data  → [What data is accessed/modified]                   │
│  Error → [What can go wrong and how it's handled]           │
│  Impact→ [Business impact if this step fails]               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: [Action]                                             │
│  What  → [Technical action taken]                           │
│  Why   → [Business reason]                                  │
│  Data  → [Data accessed/modified]                           │
│  Error → [Potential errors]                                 │
│  Impact→ [Business impact]                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
                 [Continue for all steps]
                          ↓
                    [SUCCESS] or [FAILURE]
```

**Success Path:**  
[What happens on successful completion - return value, side effects, downstream impacts]

**Failure Paths:**

| Error Type | When It Occurs | Business Impact | How It's Handled |
|------------|----------------|-----------------|------------------|
| [ErrorType1] | [Condition] | [Impact] | [Handling strategy] |
| [ErrorType2] | [Condition] | [Impact] | [Handling strategy] |

---

### Alternative Paths

[Document non-primary operations and conditional logic]

#### Alternative Operation: [Method Name]

**When Used:**  
[Conditions that trigger this alternative path]

**How It Differs:**  
[Key differences from primary operation]

**Flow:**  
[Simplified flow diagram or bullet points]

---

## Business Rules

[Comprehensive table of business rules enforced by this service]

| Rule ID | Description | Why It Exists | Since When | Related To |
|---------|-------------|---------------|------------|------------|
| **BR-[SVC]-001** | [Rule description] | [Business rationale with history] | [Date added] | [User story/ticket] |
| **BR-[SVC]-002** | [Rule description] | [Business rationale with history] | [Date added] | [User story/ticket] |
| **BR-[SVC]-003** | [Rule description] | [Business rationale with history] | [Date added] | [User story/ticket] |

**Rule ID Format:** BR-[ServiceAbbreviation]-### (e.g., BR-ENR-001 for EnrollmentService)

**Rule Categories:**
- **Validation Rules:** [List rule IDs that validate input]
- **Authorization Rules:** [List rule IDs that control access]
- **Business Logic Rules:** [List rule IDs that enforce business constraints]

**Recent Rule Changes:**
[Document any rules added or modified in last 6 months]

---

## Architecture

### System Context

```
┌──────────────────────────────────────────────────────────────┐
│                        External Systems                       │
│  [External API 1]    [External API 2]    [External Service]  │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                          API Layer                            │
│              [ControllerName] (See API Docs)                  │
│              → [Link to API Reference Database]               │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    ► THIS SERVICE ◄                           │
│                     [ServiceName]                             │
│          [1-2 sentence purpose statement]                     │
└──────────────────────────────────────────────────────────────┘
                              ↓
├────────────────┬────────────────┬────────────────┬────────────┤
│  Dependency 1  │  Dependency 2  │  Dependency 3  │ Repository │
└────────────────┴────────────────┴────────────────┴────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                        Database Layer                         │
│              [Tables] - See Database Docs                     │
└──────────────────────────────────────────────────────────────┘
```

### Dependencies (What This Service Needs)

| Dependency | Interface | Purpose | Failure Mode | Mitigation |
|------------|-----------|---------|--------------|------------|
| [Name] | `IInterfaceName` | [What it's used for] | ⚠️ [Critical/Non-blocking] | [How failure handled] |
| [Name] | `IInterfaceName` | [What it's used for] | ⚠️ [Critical/Non-blocking] | [How failure handled] |

**Critical Dependencies:**  
[List dependencies where failure blocks operation]

**Non-Critical Dependencies:**  
[List dependencies where failure is logged but operation continues]

### Consumers (Who Uses This Service)

| Consumer | Type | Use Case | Impact of Failure |
|----------|------|----------|-------------------|
| [Name] | [Controller/Service/Job] | [How they use it] | [User-facing impact] |
| [Name] | [Controller/Service/Job] | [How they use it] | [User-facing impact] |

**User-Facing Consumers:**  
[List consumers directly called from UI/API]

**Internal Consumers:**  
[List services/jobs that use this internally]

---

## API Contract (AI Context)

> 📋 **Interactive Documentation:** [API Portal](https://apim.gateway.emerson.com/...) — for testing and full examples
> 
> **Purpose:** Provides AI assistants with API context for code generation.
> **Sync Status:** Last verified against portal on `YYYY-MM-DD`

### Endpoints

| Method | Route | Purpose | Auth | Request Body | Response |
|--------|-------|---------|------|--------------|----------|
| `GET` | `/v1/[resource]` | List all | Yes | N/A | `List<ResourceDto>` |
| `GET` | `/v1/[resource]/{id}` | Get by ID | Yes | N/A | `ResourceDto` |
| `POST` | `/v1/[resource]` | Create | Yes | `CreateResourceDto` | `ResourceDto` |
| `PUT` | `/v1/[resource]/{id}` | Update | Yes | `UpdateResourceDto` | `ResourceDto` |
| `DELETE` | `/v1/[resource]/{id}` | Delete | Yes | N/A | `204 No Content` |

### Request Example: POST /v1/[resource]

```json
{
  "name": "Example Resource",
  "description": "Description text",
  "categoryId": 1,
  "isActive": true
}
```

| Property | Type | Required | Validation | Description |
|----------|------|----------|------------|-------------|
| `name` | `string` | Yes | Max 200 chars | Resource name |
| `description` | `string` | No | Max 2000 chars | Optional description |
| `categoryId` | `int` | Yes | Must exist | FK to Categories |
| `isActive` | `bool` | No | Default: true | Active status |

### Success Response Example (200/201)

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Example Resource",
  "description": "Description text",
  "categoryId": 1,
  "categoryName": "Category A",
  "isActive": true,
  "createdDate": "2024-12-05T10:30:00Z",
  "createdBy": "user@company.com"
}
```

### Error Response Models

**BadRequestStandardResponse (400/500):**
```json
{
  "path": "/v1/[resource]",
  "method": "POST",
  "statusCode": 400,
  "message": "Validation failed.",
  "exceptionMessage": "One or more validation errors occurred.",
  "validationErrors": [
    { "fieldName": "name", "message": "Name is required." },
    { "fieldName": "categoryId", "message": "Category does not exist." }
  ]
}
```

| Property | Type | Description |
|----------|------|-------------|
| `path` | `string` | Request path |
| `method` | `string` | HTTP method |
| `statusCode` | `int` | HTTP status code |
| `message` | `string` | User-friendly message |
| `exceptionMessage` | `string?` | Technical details (dev only) |
| `validationErrors` | `ValidationError[]` | Field-level errors |

### Response Status Codes

| Endpoint | 200 | 201 | 400 | 401 | 404 | 500 |
|----------|-----|-----|-----|-----|-----|-----|
| `GET /resource` | ✅ | - | - | ✅ | - | ✅ |
| `GET /resource/{id}` | ✅ | - | - | ✅ | ✅ | ✅ |
| `POST /resource` | - | ✅ | ✅ | ✅ | - | ✅ |
| `PUT /resource/{id}` | ✅ | - | ✅ | ✅ | ✅ | ✅ |
| `DELETE /resource/{id}` | - | - | - | ✅ | ✅ | ✅ |

> ❓ [HUMAN: Sync this section with API Portal when endpoints change. Last sync: ________]

---

## Validation Rules

[Extract from FluentValidation *Validator.cs classes]

| Property | Rule | Error Message | Business Context |
|----------|------|---------------|------------------|
| `[Property]` | `NotEmpty()` | "[Property] is required" | [Why required?] |
| `[Property]` | `MaximumLength(N)` | "Cannot exceed N chars" | [Why this limit?] |
| `[Property]` | `Must(custom)` | "Custom validation" | [Business rule] |

**Validation Categories:**
- **Required Fields:** [List property names]
- **Length Constraints:** [List property names with limits]
- **Custom Business Rules:** [List with explanations]

---

## Data Operations

### Reads From

| Table/Source | Purpose | Query Type | Volume |
|--------------|---------|------------|--------|
| `schema.TableName` | [What data retrieved] | [Single/Multiple/Aggregate] | [Typical record count] |

**Cross-Repository Reference:**  
For table schema details, see:
- [Table1_doc.md](../../database-repo/docs/tables/Table1_doc.md)
- [Table2_doc.md](../../database-repo/docs/tables/Table2_doc.md)

### Writes To

| Table/Destination | Operation | Purpose | Business Event |
|-------------------|-----------|---------|----------------|
| `schema.TableName` | [INSERT/UPDATE/DELETE] | [What's being saved] | [Business context] |

**Transaction Scope:**  
[Which operations happen in same transaction? Rollback behavior?]

### Side Effects

| Side Effect | When | Blocking? | Retry Logic | Monitoring |
|-------------|------|-----------|-------------|------------|
| Email notification | [After what action] | No (async) | [Retry strategy] | [Alert if N failures] |
| Audit log | [After what action] | Yes (sync) | [None] | [Log entry count] |
| Cache invalidation | [After what action] | No (fire-and-forget) | [None] | [None] |

**Side Effect Diagram:**

```
[Primary Operation]
      ↓
      ├─→ [Side Effect 1] (blocking)
      ├─→ [Side Effect 2] (async)
      └─→ [Side Effect 3] (fire-and-forget)
```

---

## External Dependencies

[This section is REQUIRED for Standard template]

### [External System Name]

**Purpose:**  
[Why we integrate with this system]

**Integration Type:**  
[REST API / SOAP / Database / Message Queue / etc.]

**Endpoints Used:**
- `[HTTP Method] [Endpoint URL]` - [Purpose]

**Authentication:**  
[API key / OAuth / etc.]

**Failure Behavior:**

| Failure Type | Service Response | User Impact | Monitoring |
|--------------|------------------|-------------|------------|
| Timeout | [How handled] | [What user sees] | [Alert rule] |
| 4xx Error | [How handled] | [What user sees] | [Alert rule] |
| 5xx Error | [How handled] | [What user sees] | [Alert rule] |

**Contact Information:**
- **Provider:** [Company name]
- **Support:** [Email/phone]
- **Documentation:** [URL]

**Known Issues:**  
[List any known reliability/performance issues]

---

## Known Issues & Limitations

[Document current limitations, technical debt, workarounds]

### Active Issues

| Issue ID | Description | Workaround | Planned Fix |
|----------|-------------|------------|-------------|
| [Ticket #] | [What's broken/limited] | [How to work around] | [Timeline] |

### Technical Debt

| Debt Item | Impact | Priority | Effort Estimate |
|-----------|--------|----------|-----------------|
| [Description] | [Performance/Maintenance/Scalability] | [High/Med/Low] | [Time estimate] |

### Design Compromises

[Document deliberate shortcuts or temporary solutions]

**Example:**
> We're using synchronous email sending instead of queue-based to meet tight deadline. Plan to refactor to async queue in Q2.

---

## Performance

### Response Time Targets

| Operation | Target | P50 | P95 | P99 |
|-----------|--------|-----|-----|-----|
| [Method name] | [Target ms] | [Actual] | [Actual] | [Actual] |

**Last Measured:** [Date]  
**Measurement Method:** [APM tool / manual testing]

### Bottlenecks Identified

1. **[Bottleneck description]**
   - **Cause:** [Root cause]
   - **Impact:** [Performance degradation]
   - **Mitigation:** [What was done or planned]

### Optimization History

| Date | Change | Result |
|------|--------|--------|
| [YYYY-MM] | [What was optimized] | [Performance improvement] |

---

## Error Reference

[Comprehensive list of errors this service can throw]

| Error Code | Error Message | Cause | Resolution |
|------------|---------------|-------|------------|
| [Code] | [Message] | [When it occurs] | [How to fix] |

**Error Handling Strategy:**  
[How errors are logged, monitored, and escalated]

---

## Testing

### Unit Tests

**Location:** `tests/Services/[ServiceName]Tests.cs`  
**Coverage:** [Percentage if known]

**Key Test Scenarios:**
- [Test scenario 1]
- [Test scenario 2]
- [Test scenario 3]

### Integration Tests

**Location:** `tests/Integration/[ServiceName]IntegrationTests.cs`

**External Dependencies Mocked:**
- [Dependency 1]
- [Dependency 2]

---

## Monitoring & Alerts

### Key Metrics

| Metric | Threshold | Alert Rule |
|--------|-----------|------------|
| Error rate | [X%] | [Alert if exceeded] |
| Response time | [X ms] | [Alert if exceeded] |
| Throughput | [X req/sec] | [Alert if drops below] |

### Dashboards

**Primary Dashboard:** [Link to monitoring dashboard]  
**Logs:** [Link to log query]

---

## Questions & Gaps

### Open Questions

- ❓ [Unresolved question about business logic]
- ❓ [Unresolved question about performance]
- ❓ [Unresolved question about future direction]

### Next Steps

- [ ] [Follow-up action 1]
- [ ] [Follow-up action 2]
- [ ] [Person to contact for clarification]

---

## Maintenance Checklist

**When making code changes to this service:**

- [ ] Update this documentation if behavior changes
- [ ] Update business rules table if validation logic changes
- [ ] Update flow diagram if steps added/removed
- [ ] Update error reference if new errors introduced
- [ ] Update performance metrics if significant impact
- [ ] Update external dependencies if integrations change
- [ ] Add to "Known Issues" if introducing limitation
- [ ] Update test scenarios if new paths added

---

## Related Documentation

**API Endpoints:** [Link to API Reference Database]  
**Database Tables:** [Links to relevant table documentation]  
**Related Services:** 
- [Dependency service 1 docs]
- [Dependency service 2 docs]
- [Consumer service docs]

**Architecture Decisions:**  
[Link to ADR (Architecture Decision Records) if applicable]

---

## Change History

**Schema evolution is tracked in Git**, not in this document.

```bash
# View all changes
git log docs/services/[ServiceName]_doc.md

# View changes with diffs
git log -p docs/services/[ServiceName]_doc.md

# Search for specific feature
git log --grep="BR-[SVC]" docs/services/[ServiceName]_doc.md
```

---

## Documentation Standards

This template follows the **Standard Service Documentation** approach:
- 60% generated by AI, 40% human-enhanced
- Includes baseline + pre-selected optional sections
- Target: 85% complete, production-ready
- Time investment: 30-40 minutes

**Included Sections:**
- All baseline sections (Quick Reference through Questions & Gaps)
- Architecture (expanded with diagrams)
- External Dependencies (required)
- Known Issues & Limitations (required)
- Performance (required)

**Optional Sections (Add When Needed):**
- Common Problems & Solutions (add after incidents)
- What Could Break (add before major changes)

See `Backend_Service_Documentation_Guide.md` for complete implementation guide.

---

**Template Version**: Standard v1.1  
**Time to Complete**: 35-45 minutes (with AI assistance)  
**Best For**: Critical services, external integrations, compliance requirements  
**Documentation Level**: 🟢 85% complete (comprehensive, audit-ready)  
**Last Updated**: 2024-12-05 (Added API Contract and Validation Rules sections)

---

**Pro tip:** This template is for services where thorough upfront documentation pays off - payment processing, authentication, external integrations, or compliance-heavy services. For most services, use Lean Baseline template instead.
