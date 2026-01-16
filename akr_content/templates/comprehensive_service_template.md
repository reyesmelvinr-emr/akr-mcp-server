# Service: [SERVICE_NAME]

**Namespace/Project**: [Project.Services]  
**File Location**: `src/Services/[ServiceName].cs`  
**Last Updated**: [YYYY-MM-DD]  
**Complexity**: Complex  
**Criticality**: Mission-Critical ⚠️  
**Documentation Level**: 🔵 Comprehensive (95% complete)  
**Owner**: [Team/Person responsible]  
**On-Call Contact**: [Contact information]

---

## 🚨 Critical Service Alert

**This is a mission-critical service.** Changes require:
- [ ] Technical Lead approval
- [ ] Comprehensive testing (unit + integration + E2E)
- [ ] Performance impact analysis
- [ ] Rollback plan
- [ ] Post-deployment monitoring
- [ ] Documentation update (this file)

**Downstream Impact:** [Number] services depend on this  
**User Impact:** [Number] users affected if service fails  
**SLA:** [Response time / Uptime requirements]

---

## Quick Reference (TL;DR)

**What it does:**  
[2-3 sentences on critical business function this service provides]

**When to use it:**  
[All scenarios where this service should be used - comprehensive list]

**When NOT to use it:**  
[Scenarios where alternative services should be used]

**Critical dependencies:**  
[All dependencies with failure impacts and criticality ratings]

**Watch out for:**  
[Top 5 gotchas, common mistakes, or edge cases that cause production issues]

**SLA / Performance Target:**  
[Specific response time targets with percentiles]

**Emergency Contacts:**
- **Primary:** [Name, contact]
- **Secondary:** [Name, contact]
- **Escalation:** [Manager, contact]

---

## What & Why

### Purpose

**Technical:**  
[Comprehensive technical description of what service does, including all capabilities]

**Business:**  
[Detailed business purpose - critical business problem solved, stakeholder value, revenue/compliance impact]

**Strategic Value:**  
[Why this service is mission-critical - business risk if unavailable, competitive advantage provided]

**Historical Context:**  
[Detailed history: When built? What prompted creation? What did it replace? Migration notes? Evolution over time?]

### Capabilities

**Core Functions (Mission-Critical):**
- [Primary capability 1 with business value]
- [Primary capability 2 with business value]
- [Primary capability 3 with business value]

**Supporting Functions (Important):**
- [Supporting capability 1]
- [Supporting capability 2]

**Future Capabilities (Planned):**
- [Planned enhancement 1 with timeline]
- [Planned enhancement 2 with timeline]

### Not Responsible For

**Out of Scope:**
- [Functionality handled by other services - with service names]
- [Functionality not yet implemented - with future plans]
- [Functionality deprecated - with migration guidance]

**Common Misconceptions:**
- [Misconception 1 and clarification]
- [Misconception 2 and clarification]

---

## How It Works

### Primary Operation: [Main Method Name]

**Purpose:**  
[Comprehensive description of what this method accomplishes and critical business context]

**Signature:**  
```csharp
[Complete method signature with XML comments]
```

**Input Validation:**
- [Validation rule 1]
- [Validation rule 2]
- [Validation rule 3]

**Output:**  
```csharp
[Return type with all possible states/values]
```

**Business Scenarios:**
1. **[Scenario 1]** - [Description and frequency]
2. **[Scenario 2]** - [Description and frequency]
3. **[Edge Case]** - [Description and how handled]

**Complete Step-by-Step Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: [Action]                                             │
│  What      → [Technical action - specific method calls]     │
│  Why       → [Business reason - why needed]                 │
│  Data      → [Data accessed/modified with volumes]          │
│  Error     → [Possible errors with error codes]             │
│  Impact    → [Business impact - user experience]            │
│  Monitoring→ [Metrics/alerts for this step]                 │
│  Duration  → [Typical execution time]                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: [Action]                                             │
│  [Complete details for each step]                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
                 [Continue for all steps]
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Decision Point: [Condition]                                  │
│  If TRUE  → [Path A with detailed flow]                     │
│  If FALSE → [Path B with detailed flow]                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
                    [SUCCESS] or [FAILURE]
```

**Success Path:**  
[Comprehensive description of successful completion including all side effects, state changes, notifications]

**Failure Paths:**

| Error Type | HTTP Status | When It Occurs | Business Impact | User Message | How It's Handled | Retry Strategy |
|------------|-------------|----------------|-----------------|--------------|------------------|----------------|
| [Error1] | [Code] | [Condition] | [Impact] | [Message] | [Handling] | [Retry logic] |
| [Error2] | [Code] | [Condition] | [Impact] | [Message] | [Handling] | [Retry logic] |

**Rollback Behavior:**  
[What happens on failure? Transaction rollback? Compensation logic? Cleanup?]

---

### Alternative Paths

#### Alternative Operation 1: [Method Name]

**When Used:**  
[Specific conditions that trigger this path]

**How It Differs:**  
[Key differences from primary operation - business logic, validation, performance]

**Complete Flow:**  
[Detailed flow diagram or step-by-step]

#### Alternative Operation 2: [Method Name]

[Repeat for each alternative operation]

---

### Conditional Logic Decision Tree

```
START: [Entry point]
    ↓
    Is [Condition 1]?
    ├─ YES → [Path A]
    │        ├─ Is [Condition 2]?
    │        │  ├─ YES → [Outcome A1]
    │        │  └─ NO  → [Outcome A2]
    │        └─ [Continue...]
    │
    └─ NO  → [Path B]
             ├─ [Continue detailed decision tree]
             └─ [...]
```

---

## Business Rules

[Comprehensive table of ALL business rules - this is critical for mission-critical services]

| Rule ID | Description | Why It Exists (History) | Since When | Changed When | Related To | Enforcement |
|---------|-------------|------------------------|------------|--------------|------------|-------------|
| **BR-[SVC]-001** | [Rule] | [Business rationale + incident history] | [Date] | [Date] | [US###] | [Code/DB/UI] |
| **BR-[SVC]-002** | [Rule] | [Business rationale + incident history] | [Date] | [Date] | [US###] | [Code/DB/UI] |

**Rule Categories:**
- **Validation Rules:** [All rule IDs - input validation, data integrity]
- **Authorization Rules:** [All rule IDs - access control, permissions]
- **Business Logic Rules:** [All rule IDs - business constraints, calculations]
- **Compliance Rules:** [All rule IDs - regulatory requirements]

**Rule Change History:**
[Document every rule change with date, reason, impact assessment]

| Date | Rule ID | Change | Reason | Impact | Approval |
|------|---------|--------|--------|--------|----------|
| [Date] | [ID] | [What changed] | [Why] | [Impact assessment] | [Who approved] |

**Rule Dependencies:**
[Document rules that depend on each other or must be enforced in specific order]

---

## Architecture

### System Context (Full Diagram)

```
┌────────────────────────────────────────────────────────────────────┐
│                         External Systems                            │
│  [System 1]         [System 2]         [System 3]                  │
│  Purpose            Purpose            Purpose                      │
│  Criticality        Criticality        Criticality                  │
└────────────────────────────────────────────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────────────┐
│                          API Gateway                                │
│              Authentication, Rate Limiting, Routing                 │
└────────────────────────────────────────────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────────────┐
│                          API Layer                                  │
│              [Controller Names] - See API Docs                      │
│              → [Link to API Reference Database]                     │
└────────────────────────────────────────────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────────────┐
│                    ► THIS SERVICE ◄                                 │
│                     [ServiceName]                                   │
│          [Mission-critical business function]                       │
│          Owner: [Team]    On-Call: [Contact]                        │
└────────────────────────────────────────────────────────────────────┘
                                ↓
├──────────────┬──────────────┬──────────────┬──────────────┬────────┤
│ Dependency 1 │ Dependency 2 │ Dependency 3 │ Dependency 4 │  Repo  │
│ (Critical)   │ (Important)  │ (Non-block)  │ (Non-block)  │        │
└──────────────┴──────────────┴──────────────┴──────────────┴────────┘
                                ↓
┌────────────────────────────────────────────────────────────────────┐
│                        Database Layer                               │
│              [Tables] - See Database Docs                           │
│              [Indexes] - Performance critical                       │
└────────────────────────────────────────────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────────────┐
│                       Side Effects                                  │
│   [Emails]    [Webhooks]    [Cache]    [Audit Logs]               │
└────────────────────────────────────────────────────────────────────┘
```

### Dependencies (Comprehensive Analysis)

| Dependency | Interface | Purpose | Criticality | Failure Mode | Fallback Strategy | Monitoring | Contact |
|------------|-----------|---------|-------------|--------------|-------------------|------------|---------|
| [Name] | `IInterface` | [Purpose] | ⚠️ CRITICAL | [Blocks operation] | [Fallback logic] | [Alert rule] | [Contact] |
| [Name] | `IInterface` | [Purpose] | ⚠️ Important | [Degrades function] | [Fallback logic] | [Alert rule] | [Contact] |
| [Name] | `IInterface` | [Purpose] | ✅ Non-blocking | [Operation continues] | [Log only] | [None] | [Contact] |

**Dependency Health Checks:**
- [Dependency 1]: [How to verify health]
- [Dependency 2]: [How to verify health]

**Circuit Breaker Configuration:**
| Dependency | Failure Threshold | Timeout | Retry Policy |
|------------|-------------------|---------|--------------|
| [Name] | [X failures in Y sec] | [Z sec] | [Retry strategy] |

### Consumers (Complete Mapping)

| Consumer | Type | Use Case | Call Volume | Impact of Failure | Notification Required |
|----------|------|----------|-------------|-------------------|----------------------|
| [Name] | [Type] | [Use case] | [X/sec] | [Impact] | [Yes/No - Contact] |

**Consumer Dependency Graph:**
```
[This Service]
    ├─→ [Consumer 1] → [Downstream 1a] → [Downstream 1b]
    ├─→ [Consumer 2] → [Downstream 2a]
    └─→ [Consumer 3] → [Downstream 3a] → [Downstream 3b] → [Downstream 3c]
```

**What Breaks If This Service Fails:**
[Comprehensive list of all downstream impacts - be specific about user-facing features]

---

## API Contract (AI Context)

> 📋 **Interactive Documentation:** [API Portal](https://apim.gateway.emerson.com/...) — for testing and full OpenAPI spec
> 
> **Purpose:** Complete API contract for AI assistants and developer reference.
> **Sync Status:** Last verified against portal on `YYYY-MM-DD` by [Person]
> **OpenAPI Spec:** [Link to swagger.json] (for tooling only)

### Endpoints Summary

| Method | Route | Purpose | Auth | Rate Limit | SLA |
|--------|-------|---------|------|------------|-----|
| `POST` | `/v1/[resource]/search` | Search with filters | Yes | 100/min | 500ms |
| `GET` | `/v1/[resource]/{id}` | Get by ID | Yes | 200/min | 200ms |
| `POST` | `/v1/[resource]` | Create | Yes | 50/min | 1000ms |
| `PUT` | `/v1/[resource]/{id}` | Update | Yes | 50/min | 1000ms |
| `DELETE` | `/v1/[resource]/{id}` | Delete | Yes | 20/min | 500ms |

---

### POST /v1/[resource]/search

**Purpose:** Search resources by various criteria with pagination

**Request:**
```http
POST /v1/[resource]/search
Authorization: Bearer {token}
Content-Type: application/json

{
  "pageNumber": 1,
  "pageSize": 20,
  "queryFields": [
    { "name": "fieldName", "exactValue": "*searchTerm*" }
  ],
  "exportMode": false
}
```

**Request Schema: PaginationQuery**

| Property | Type | Required | Default | Validation | Description |
|----------|------|----------|---------|------------|-------------|
| `pageNumber` | `int` | No | 1 | Min: 1 | Page number |
| `pageSize` | `int` | No | 20 | 1-100 | Results per page |
| `queryFields` | `QueryField[]` | No | [] | Max 10 fields | Search filters |
| `exportMode` | `bool` | No | false | - | Enable export format |

**QueryField Schema:**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | `string` | Yes | Field name to filter |
| `exactValue` | `string` | Yes | Filter value (supports wildcards) |

**Success Response (200 OK):**
```json
{
  "data": [{
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Example Resource",
    "description": "Description text",
    "category": "Category A",
    "isActive": true,
    "fullCount": 1497
  }],
  "pageNumber": 1,
  "pageSize": 20,
  "nextPage": "https://api.example.com/v1/[resource]/search?pageNumber=2&pageSize=20"
}
```

**Response Schema:**

| Property | Type | Description |
|----------|------|-------------|
| `data` | `ResourceItem[]` | Array of results |
| `pageNumber` | `int` | Current page |
| `pageSize` | `int` | Results per page |
| `nextPage` | `string?` | URL for next page (null if last) |

---

### Error Response Models

**BadRequestStandardResponse (400/500):**
```json
{
  "path": "/v1/[resource]/search",
  "method": "POST",
  "statusCode": 400,
  "message": "Validation failed.",
  "exceptionMessage": "One or more validation errors occurred.",
  "validationErrors": [
    { "fieldName": "pageSize", "message": "Must be between 1 and 100" }
  ]
}
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `path` | `string` | No | Request path that caused error |
| `method` | `string` | No | HTTP method used |
| `statusCode` | `int` | No | HTTP status code |
| `message` | `string` | No | User-friendly error message |
| `exceptionMessage` | `string?` | No | Technical details (dev environments) |
| `validationErrors` | `ValidationError[]` | No | Field-level validation errors |

**ValidationError:**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `fieldName` | `string` | No | Name of field with error |
| `message` | `string` | No | Validation error message |

---

### Error Handling Decision Tree

```
Exception Thrown
    ↓
Is ValidationException?
├─ YES → Return 400 Bad Request
│        Body: BadRequestStandardResponse with validationErrors[]
│
Is NotFoundException?
├─ YES → Return 404 Not Found
│        Body: BadRequestStandardResponse (statusCode: 404)
│
Is UnauthorizedException?
├─ YES → Return 401 Unauthorized
│        Body: BadRequestStandardResponse (statusCode: 401)
│
Is ForbiddenException?
├─ YES → Return 403 Forbidden
│        Body: BadRequestStandardResponse (statusCode: 403)
│
DEFAULT (Unhandled)
└─ Return 500 Internal Server Error
   Body: BadRequestStandardResponse (exceptionMessage: null in prod)
   Action: Log full exception, alert on-call if critical
```

---

### Response Status Code Matrix

| Endpoint | 200 | 201 | 400 | 401 | 403 | 404 | 500 |
|----------|-----|-----|-----|-----|-----|-----|-----|
| `POST /search` | ✅ Success | - | ✅ Validation | ✅ No token | ✅ No access | - | ✅ Server error |
| `GET /{id}` | ✅ Found | - | - | ✅ No token | ✅ No access | ✅ Not found | ✅ Server error |
| `POST /` | - | ✅ Created | ✅ Validation | ✅ No token | ✅ No access | - | ✅ Server error |
| `PUT /{id}` | ✅ Updated | - | ✅ Validation | ✅ No token | ✅ No access | ✅ Not found | ✅ Server error |
| `DELETE /{id}` | ✅ Deleted | - | - | ✅ No token | ✅ No access | ✅ Not found | ✅ Server error |

> ❓ [HUMAN: Keep synchronized with API Portal. Last sync: __________ by __________]

---

## Middleware Pipeline

[AI: Extract from Program.cs app.UseMiddleware<T>() calls]

| Order | Middleware | Purpose | Source | Critical? |
|-------|------------|---------|--------|----------|
| 1 | `ExceptionMiddleware` | Global exception handling → ErrorDetails JSON | `Middleware/` | ⚠️ Yes |
| 2 | `RequestTimingMiddleware` | Request duration logging | `Middleware/` | No |
| 3 | `CorrelationIdMiddleware` | Request correlation tracking | `Middleware/` | ⚠️ Yes |

### Exception Handling Flow

```
Incoming Request
       ↓
┌──────────────────────────────────────┐
│ ExceptionMiddleware                   │
│  - Wraps pipeline in try/catch       │
│  - Catches all unhandled exceptions  │
│  - Formats as BadRequestStandard_    │
│    Response JSON                      │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│ RequestTimingMiddleware              │
│  - Records start time                │
│  - Logs duration on completion       │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│ Controller / Service Logic           │
└──────────────────────────────────────┘
       ↓
Response (Success or Error JSON)
```

❓ [HUMAN: Document any middleware-specific configuration or custom error handling]

---

## Validation Rules (Comprehensive)

[Extract from FluentValidation *Validator.cs classes]

### [EntityName]Validator

| Property | Rule | Error Message | Business Context | Enforcement |
|----------|------|---------------|------------------|-------------|
| `[Property]` | `NotEmpty()` | "[Property] is required" | [Business reason] | Code |
| `[Property]` | `MaximumLength(N)` | "Cannot exceed N chars" | [Why this limit] | Code |
| `[Property]` | `Must(custom)` | "Custom validation" | [Business rule] | Code |
| `[Property]` | `LessThanOrEqualTo(X)` | "Must not exceed X" | [Business constraint] | Code |

**Validation Categories:**
- **Required Fields:** [List all required properties]
- **Length Constraints:** [List all max/min length rules]
- **Range Constraints:** [List all numeric range rules]
- **Custom Business Rules:** [List all custom validators with explanations]
- **Cross-Field Validation:** [List rules that depend on multiple fields]

---

## Data Operations

### Database Schema

**Primary Tables:**

| Table | Purpose | Read Volume | Write Volume | Key Indexes | Lock Contention |
|-------|---------|-------------|--------------|-------------|-----------------|
| `schema.Table` | [Purpose] | [X/sec] | [Y/sec] | [Index names] | [Low/Med/High] |

**Cross-Repository Reference:**  
For complete table schema details:
- [Table1_doc.md](../../database-repo/docs/tables/Table1_doc.md) - [Purpose]
- [Table2_doc.md](../../database-repo/docs/tables/Table2_doc.md) - [Purpose]

### Read Operations

| Query | Table | Purpose | Frequency | Avg Duration | P99 Duration | Optimization Notes |
|-------|-------|---------|-----------|--------------|--------------|-------------------|
| [Query type] | [Table] | [Purpose] | [X/sec] | [Y ms] | [Z ms] | [Notes] |

### Write Operations

| Operation | Table | Purpose | Frequency | Transaction Scope | Rollback Impact |
|-----------|-------|---------|-----------|-------------------|-----------------|
| [INSERT/UPDATE] | [Table] | [Purpose] | [X/sec] | [Scope] | [Impact] |

**Transaction Management:**
- **Isolation Level:** [Read Committed / Serializable / etc.]
- **Deadlock Risk:** [Low / Medium / High]
- **Rollback Strategy:** [How transactions are rolled back on failure]

### Side Effects (Comprehensive)

| Side Effect | Trigger | Async/Sync | Critical? | Retry Logic | Failure Impact | Monitoring |
|-------------|---------|------------|-----------|-------------|----------------|------------|
| Email | [Event] | Async | No | [3 retries, exp backoff] | [Logged only] | [Email queue depth] |
| Webhook | [Event] | Async | Yes | [5 retries, exp backoff] | [Alert + rollback] | [Webhook failures] |
| Cache invalidate | [Event] | Sync | Yes | [None] | [Stale data] | [Cache hit rate] |

**Side Effect Ordering:**
[If order matters, document the sequence and why]

---

## External Dependencies (Mission-Critical)

### [External System 1 Name]

**Business Purpose:**  
[Why we integrate - critical business function provided]

**Integration Type:**  
[REST API / SOAP / GraphQL / Message Queue / Database / etc.]

**Criticality:** ⚠️ CRITICAL / Important / Optional

**Endpoints Used:**
| Endpoint | Method | Purpose | Call Volume | Timeout | Retry |
|----------|--------|---------|-------------|---------|-------|
| [URL] | [GET/POST] | [Purpose] | [X/min] | [Y sec] | [Z attempts] |

**Authentication:**  
[Detailed auth mechanism - API key location, OAuth flow, certificate details]

**Request/Response Examples:**

**Request:**
```json
{
  "field1": "value",
  "field2": "value"
}
```

**Success Response:**
```json
{
  "status": "success",
  "data": { }
}
```

**Error Response:**
```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "Error description"
}
```

**Failure Behavior:**

| Failure Type | Condition | Service Response | User Impact | Alerting | Recovery |
|--------------|-----------|------------------|-------------|----------|----------|
| Timeout | [>X sec] | [Fallback logic] | [User message] | [PagerDuty alert] | [Auto-retry] |
| 4xx Error | [Which codes] | [How handled] | [User message] | [Log only] | [Manual fix] |
| 5xx Error | [Which codes] | [How handled] | [User message] | [Immediate alert] | [Auto-retry] |

**Circuit Breaker:**
- **Failure Threshold:** [X failures in Y seconds]
- **Open Duration:** [Z seconds]
- **Half-Open Test:** [How to test recovery]

**Rate Limiting:**
- **Provider Limit:** [X requests/minute]
- **Our Usage:** [Y requests/minute]
- **Buffer:** [Z% below limit]

**Contact Information:**
- **Provider:** [Company name]
- **Account Manager:** [Name, email, phone]
- **Technical Support:** [Email, phone, escalation process]
- **Documentation:** [URL to API docs]
- **Status Page:** [URL to status page]
- **SLA:** [Uptime guarantee, response time]

**Known Issues:**
| Issue | Impact | Workaround | Status |
|-------|--------|------------|--------|
| [Issue description] | [Impact] | [How to work around] | [Provider status] |

**Incident History:**
| Date | Incident | Impact | Resolution | Prevention |
|------|----------|--------|------------|------------|
| [YYYY-MM] | [What happened] | [Impact on us] | [How resolved] | [What we changed] |

---

## Known Issues & Limitations

### Active Issues

| Issue ID | Severity | Description | Workaround | User Impact | Planned Fix | Owner |
|----------|----------|-------------|------------|-------------|-------------|-------|
| [Ticket] | [P0-P4] | [Details] | [Workaround] | [Impact] | [Timeline] | [Person] |

### Technical Debt

| Debt Item | Category | Impact | Priority | Effort | Scheduled | Blocking Factors |
|-----------|----------|--------|----------|--------|-----------|------------------|
| [Description] | [Perf/Scale/Maint] | [Impact] | [P0-P4] | [Days] | [Q/Month] | [Dependencies] |

### Design Compromises

[Document ALL deliberate shortcuts with justification and remediation plan]

**Example:**
> **Compromise:** Using synchronous email sending instead of message queue  
> **Reason:** Tight Q3 deadline, queue infrastructure not ready  
> **Impact:** Email failures block operations, slower response times  
> **Remediation:** Migrate to async queue in Q4 (Epic #456)  
> **Risk:** High load can cause timeouts (mitigated by 5sec timeout + retry)

### Scalability Limits

| Limit | Current Capacity | Growth Rate | Breaking Point | Mitigation Plan |
|-------|------------------|-------------|----------------|-----------------|
| [Metric] | [Current] | [% per quarter] | [When breaks] | [What to do] |

---

## Performance

### Response Time Targets

| Operation | Target (P50) | Target (P95) | Target (P99) | Current (P50) | Current (P95) | Current (P99) | Status |
|-----------|--------------|--------------|--------------|---------------|---------------|---------------|--------|
| [Method] | [X ms] | [Y ms] | [Z ms] | [X ms] | [Y ms] | [Z ms] | [✅/⚠️/❌] |

**Last Measured:** [Date]  
**Measurement Method:** [APM tool name + link to dashboard]  
**Load Profile:** [X req/sec average, Y req/sec peak]

### Performance Baselines

**Established:** [Date]  
**Test Conditions:** [Load profile used for baseline]

| Metric | Baseline | Alert Threshold | Critical Threshold |
|--------|----------|-----------------|-------------------|
| Avg Response Time | [X ms] | [Y ms (+50%)] | [Z ms (+100%)] |
| Throughput | [X req/sec] | [Y req/sec (-20%)] | [Z req/sec (-50%)] |
| Error Rate | [X%] | [Y% (+50%)] | [Z% (+100%)] |
| CPU Usage | [X%] | [Y% (>80%)] | [Z% (>95%)] |
| Memory Usage | [X MB] | [Y MB (>80%)] | [Z MB (>95%)] |

### Bottlenecks Identified

1. **[Bottleneck Name]**
   - **Location:** [Code/Query/External call]
   - **Cause:** [Root cause analysis]
   - **Impact:** [Performance degradation details]
   - **Mitigation:** [What was done]
   - **Status:** [Resolved / Monitoring / Pending]

### Optimization History

| Date | Change | Metric Improved | Before | After | Effort | Notes |
|------|--------|-----------------|--------|-------|--------|-------|
| [YYYY-MM] | [Optimization] | [Metric] | [Value] | [Value] | [Days] | [Details] |

### Load Testing Results

**Last Run:** [Date]  
**Test Scenario:** [Description of load test]  
**Results:**
- **Peak Load Sustained:** [X req/sec for Y minutes]
- **Breaking Point:** [Z req/sec - what failed first]
- **Bottleneck:** [What limited throughput]

---

## Common Problems & Solutions

[Comprehensive troubleshooting guide - this is GOLD for on-call engineers]

### Problem 1: [Symptom]

**Symptoms:**
- [User-facing symptom]
- [System-level symptom]
- [Metrics/logs to check]

**Root Cause:**
[Detailed explanation of why this happens]

**Solution:**
1. [Immediate fix - stop the bleeding]
2. [Investigation steps]
3. [Permanent fix]

**Prevention:**
[What was changed to prevent recurrence]

**Last Occurred:** [Date]  
**Frequency:** [How often this happens]  
**Related Tickets:** [Links to incident tickets]

### Problem 2: [Symptom]

[Repeat for all known problems]

---

## What Could Break (Impact Analysis)

[Critical for planning changes - document downstream impacts]

### If We Change: [Business Rule / Method / Dependency]

**Affected Consumers:**
- [Consumer 1] - [Specific impact]
- [Consumer 2] - [Specific impact]

**Affected UI Features:**
- [Feature 1] - [How it breaks]
- [Feature 2] - [How it breaks]

**Data Migration Required:**
- [Data change 1]
- [Data change 2]

**Testing Required:**
- [ ] Unit tests: [Specific tests]
- [ ] Integration tests: [Specific tests]
- [ ] E2E tests: [Specific scenarios]
- [ ] Performance tests: [Load profile]

**Deployment Strategy:**
- [Blue-green / Canary / Rolling / etc.]
- [Rollback criteria]
- [Monitoring during deployment]

**Communication Required:**
- [Stakeholder 1] - [What to communicate]
- [Stakeholder 2] - [What to communicate]

---

## Security & Compliance

### Authentication & Authorization

**Authentication Method:** [How users/services authenticate]  
**Authorization Logic:** [How permissions are checked]  
**Role-Based Access:** [Roles and what they can do]

### Data Protection

**PII Handled:**
- [Data type 1] - [How protected]
- [Data type 2] - [How protected]

**Encryption:**
- **In Transit:** [TLS version, cipher suites]
- **At Rest:** [Database encryption, field-level encryption]

**Data Retention:**
- [Data type] - [Retention period] - [Deletion process]

### Compliance Requirements

| Requirement | Regulation | How Met | Evidence | Last Audit |
|-------------|------------|---------|----------|------------|
| [Requirement] | [GDPR/HIPAA/PCI/etc.] | [Implementation] | [Documentation] | [Date] |

### Security Incidents

| Date | Incident | Impact | Resolution | Prevention |
|------|----------|--------|------------|------------|
| [YYYY-MM] | [What happened] | [Impact] | [How fixed] | [What changed] |

---

## Disaster Recovery

### Backup Strategy

**Database Backups:**
- **Frequency:** [Hourly / Daily / etc.]
- **Retention:** [X days]
- **Location:** [Where backups stored]
- **RTO:** [Recovery Time Objective]
- **RPO:** [Recovery Point Objective]

**Configuration Backups:**
- [What's backed up and how]

### Recovery Procedures

**Scenario 1: Complete Service Failure**

1. [Step-by-step recovery]
2. [Who to contact]
3. [How to verify recovery]

**Scenario 2: Data Corruption**

1. [Step-by-step recovery]
2. [Who to contact]
3. [How to verify recovery]

**Scenario 3: Dependency Failure**

1. [Step-by-step recovery or failover]
2. [Fallback procedures]

---

## Monitoring & Alerts

### Dashboards

**Primary Dashboard:** [Link with description]  
**Performance Dashboard:** [Link with description]  
**Business Metrics Dashboard:** [Link with description]

### Key Metrics

| Metric | Collection | Threshold (Warning) | Threshold (Critical) | Alert Destination | Response Time |
|--------|------------|---------------------|----------------------|-------------------|---------------|
| Error Rate | [How collected] | [X%] | [Y%] | [PagerDuty/Email] | [SLA] |
| Response Time | [How collected] | [X ms] | [Y ms] | [PagerDuty/Email] | [SLA] |
| Throughput | [How collected] | [X req/s] | [Y req/s] | [PagerDuty/Email] | [SLA] |

### Alert Runbooks

**Alert: High Error Rate**

1. **Investigate:** [What to check first]
2. **Diagnose:** [Common root causes]
3. **Resolve:** [Fix procedures]
4. **Escalate:** [When and who]

[Repeat for all alerts]

### Logs

**Location:** [Log aggregation system + query]  
**Retention:** [How long logs kept]  
**Key Log Patterns:** [Patterns to search for during incidents]

---

## Testing Strategy

### Unit Tests

**Location:** `tests/Services/[ServiceName]Tests.cs`  
**Coverage:** [X%]  
**Run Frequency:** [On every commit]

**Critical Test Scenarios:**
- [Test 1 - what it validates]
- [Test 2 - what it validates]
- [Test 3 - what it validates]

### Integration Tests

**Location:** `tests/Integration/[ServiceName]IntegrationTests.cs`  
**Run Frequency:** [Pre-deployment]

**Dependencies Mocked:** [Which ones and why]  
**Real Dependencies:** [Which ones and why]

### End-to-End Tests

**Location:** [E2E test suite location]  
**Run Frequency:** [Daily / Pre-prod deployment]

**Critical User Journeys:**
- [Journey 1]
- [Journey 2]

### Performance Tests

**Location:** [Load test scripts location]  
**Run Frequency:** [Weekly / Before major releases]

**Test Scenarios:**
- [Scenario 1 with expected results]
- [Scenario 2 with expected results]

### Penetration Testing

**Last Run:** [Date]  
**Findings:** [Link to security report]  
**Remediations:** [What was fixed]

---

## Deployment

### Deployment Process

**CI/CD Pipeline:** [Link to pipeline]  
**Deployment Frequency:** [How often deployed]  
**Deployment Window:** [Preferred times]

**Pre-Deployment Checklist:**
- [ ] All tests passing (unit, integration, E2E)
- [ ] Performance tests completed
- [ ] Security scan completed
- [ ] Documentation updated
- [ ] Rollback plan prepared
- [ ] Stakeholders notified
- [ ] Monitoring alerts configured

**Deployment Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Post-Deployment Verification:**
- [ ] [Health check 1]
- [ ] [Health check 2]
- [ ] [Metric check 1]
- [ ] [Metric check 2]

**Rollback Procedure:**
1. [Step-by-step rollback]
2. [Verification]
3. [Notification]

### Configuration Management

**Configuration Sources:**
- [appsettings.json] - [What's configured]
- [Environment variables] - [What's configured]
- [Azure Key Vault] - [What's configured]

**Configuration Changes:**
[How to change configuration without deployment]

---

## Incident Response

### On-Call Procedures

**Primary On-Call:** [How to reach]  
**Secondary On-Call:** [How to reach]  
**Escalation Path:** [Who to escalate to and when]

### Incident Severity Levels

| Severity | Definition | Response Time | Example |
|----------|------------|---------------|---------|
| P0 (Critical) | [Definition] | [X minutes] | [Example] |
| P1 (High) | [Definition] | [Y minutes] | [Example] |
| P2 (Medium) | [Definition] | [Z hours] | [Example] |
| P3 (Low) | [Definition] | [W days] | [Example] |

### Incident History

| Date | Severity | Description | Root Cause | Resolution | Prevention | Duration |
|------|----------|-------------|------------|------------|------------|----------|
| [YYYY-MM-DD] | [P0-P3] | [What happened] | [Why] | [How fixed] | [What changed] | [Xh Ym] |

### Post-Mortem Template

[Link to post-mortem template]  
**Recent Post-Mortems:** [Links to completed post-mortems]

---

## Team & Ownership

### Primary Owner

**Team:** [Team name]  
**Tech Lead:** [Name, contact]  
**Product Owner:** [Name, contact]  
**Architecture Owner:** [Name, contact]

### Contributors

| Name | Role | Area of Expertise | Contact |
|------|------|-------------------|---------|
| [Name] | [Role] | [Expertise] | [Contact] |

### Knowledge Transfer

**Documentation:** This file + [other docs]  
**Code Walkthroughs:** [Video links if available]  
**Onboarding:** [How long to onboard new developer]

---

## Questions & Gaps

[Even comprehensive documentation has gaps]

### Open Questions

- ❓ [High-priority unresolved question]
- ❓ [Medium-priority unresolved question]

### Documentation Improvements Needed

- [ ] [Section that needs more detail]
- [ ] [Diagram that needs to be added]
- [ ] [Example that would be helpful]

### Next Steps

- [ ] [Follow-up task 1 with owner]
- [ ] [Follow-up task 2 with owner]

---

## Maintenance Checklist

**When making ANY change to this service:**

- [ ] Read this documentation FIRST (seriously - read it)
- [ ] Update this documentation if behavior changes
- [ ] Update business rules table if validation logic changes
- [ ] Update flow diagrams if steps added/removed
- [ ] Update error reference if new errors introduced
- [ ] Update performance metrics if significant impact
- [ ] Update external dependencies if integrations change
- [ ] Update "What Could Break" section
- [ ] Add to "Known Issues" if introducing limitation
- [ ] Update test scenarios if new paths added
- [ ] Update monitoring/alerts if new failure modes
- [ ] Update incident runbooks if new failure scenarios
- [ ] Notify all affected teams BEFORE deployment
- [ ] Update disaster recovery procedures if needed

---

## Related Documentation

**API Endpoints:** [Link to API Reference Database]  
**Database Tables:** [Links to all table documentation]  
**Related Services:**
- [Dependency service 1 docs]
- [Dependency service 2 docs]
- [Consumer service 1 docs]
- [Consumer service 2 docs]

**Architecture Decision Records (ADRs):**
- [ADR-###: Decision title](link)

**Runbooks:**
- [Runbook 1: Common scenario](link)
- [Runbook 2: Emergency procedure](link)

**Incident Post-Mortems:**
- [Post-mortem 1](link)
- [Post-mortem 2](link)

---

## Tags & Metadata

**Tags**: 🤖 #[feature-domain] #[cross-cutting] #service #[priority] #[status]

❓ **Add feature tags** (see TAGGING_STRATEGY_TAXONOMY.md):
- Feature Domain tags (e.g., #enrollment, #course-catalog, #user-profile)
- Cross-Cutting tags (e.g., #authentication, #audit-logging, #validation)
- Technical tag: #service
- Priority tag (e.g., #core-feature, #important, #nice-to-have)
- Status tag (e.g., #deployed, #stable, #beta)

**Example**: `#enrollment #prerequisite-validation #authentication #service #core-feature #deployed`

**Related Features**:
- 🤖 [Feature documentation that uses this service]
- ❓ [Add links to features in AKR_Main/features/ folder]

**Component Metadata**:
- **Domain**: ❓ [Business domain this service belongs to]
- **Priority**: ❓ [P0: Core | P1: Important | P2: Nice-to-have]
- **User Stories**: ❓ [US#12345, US#12467]
- **Sprint**: ❓ [Sprint number or date deployed]

---

## Change History

**Schema evolution is tracked in Git**, not in this document.

```bash
# View all changes
git log docs/services/[ServiceName]_doc.md

# View changes with diffs
git log -p docs/services/[ServiceName]_doc.md

# Search for specific changes
git log --grep="BR-[SVC]" docs/services/[ServiceName]_doc.md
git log --since="2024-01-01" docs/services/[ServiceName]_doc.md
```

---

## Documentation Standards

This template follows the **Comprehensive Service Documentation** approach:
- 50% generated by AI, 50% human-authored
- All sections included (baseline + all optional)
- Target: 95% complete, audit-ready, runbook quality
- Time investment: 45-60 minutes initial, ongoing maintenance

**Use this template ONLY for:**
- Mission-critical services (auth, payment, core platform)
- Services with complex external integrations
- Services with compliance requirements
- Services with frequent incidents
- Services with high change impact

**For most services, use Lean Baseline template instead.**

See `Backend_Service_Documentation_Guide.md` for complete implementation guide.

---

**Template Version**: Comprehensive v1.1  
**Time to Complete**: 55-70 minutes initial (with AI assistance)  
**Ongoing Maintenance**: 10-15 minutes per code change  
**Best For**: Mission-critical services only (top 5% of services)  
**Documentation Level**: 🔵 95% complete (runbook quality, audit-ready)  
**Last Updated**: 2024-12-05 (Added API Contract, Middleware Pipeline, Validation Rules sections)

---

## Emergency Quick Reference

**This Service:**
- **Does:** [One-liner]
- **Critical For:** [Business impact]
- **Fails If:** [Top 3 failure scenarios]
- **Owner:** [Contact]
- **On-Call:** [Contact]

**If This Breaks:**
1. [Immediate action]
2. [Who to call]
3. [How to verify fix]

**Dashboards:** [Link]  
**Logs:** [Link]  
**Runbook:** [Link]

---

**⚠️ WARNING:** This is a comprehensive template for mission-critical services. Do NOT use for all services - it's too much overhead. Use Lean Baseline for 90% of services, Standard for 5%, and Comprehensive for only the top 5% most critical services.
