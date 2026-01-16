# Service: [SERVICE_NAME]

**Namespace/Project**: [Project.Services]  
**File Location**: `src/Services/[ServiceName].cs`  
**Last Updated**: [YYYY-MM-DD]  
**Complexity**: Simple (CRUD operations)

---

## Purpose

[1-3 sentences describing what this service does and why it exists]

**Example:**
> CourseService provides basic CRUD operations for training course management. Handles course creation, updates, retrieval, and soft deletion with simple validation.

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `GetByIdAsync(Guid id)` | Retrieve single course by ID | Course entity or null |
| `GetAllAsync()` | Retrieve all active courses | List of courses |
| `CreateAsync(CreateCourseDto dto)` | Create new course | Created course entity |
| `UpdateAsync(Guid id, UpdateCourseDto dto)` | Update existing course | Updated course entity |
| `DeleteAsync(Guid id)` | Soft-delete course (IsActive=false) | Boolean success |

---

## Dependencies

**Required Services:**
[List injected dependencies, or "None"]

**Example:**
- `ICourseRepository` - Data access for Courses table
- `IMapper` - DTO to entity mapping

**Database Tables:**
[List tables accessed]

**Example:**
- Reads/Writes: `training.Courses`

---

## API Endpoints

📋 **Full Documentation:** [API Portal](https://api-docs.company.com/[resource]) | **Last Sync:** [YYYY-MM-DD]

| Method | Route | Purpose |
|--------|-------|--------|
| `GET` | `/v1/[resource]` | Retrieve all |
| `GET` | `/v1/[resource]/{id}` | Retrieve by ID |
| `POST` | `/v1/[resource]` | Create new |
| `PUT` | `/v1/[resource]/{id}` | Update existing |
| `DELETE` | `/v1/[resource]/{id}` | Delete |

**Example:**
| Method | Route | Purpose |
|--------|-------|--------|
| `GET` | `/v1/courses` | Retrieve all courses |
| `GET` | `/v1/courses/{id}` | Retrieve course by ID |
| `POST` | `/v1/courses` | Create new course |

### Error Response Format

```json
{
  "statusCode": 400,
  "message": "Validation failed.",
  "validationErrors": [
    { "fieldName": "title", "message": "Title is required." }
  ]
}
```

> ⚠️ **AI Context:** This section provides Copilot with API contract information.
> Keep synchronized with API Portal when endpoints change.

---

## Business Rules

[List key rules if any exist, otherwise: "None - straightforward CRUD operations"]

**Example:**
- Course title is required and must be unique
- Soft delete preserves history (IsActive=false)
- Only active courses appear in public listings

---

## Notes

[Any special considerations, gotchas, or future work]

**Example:**
- Future: Add course prerequisites validation
- Future: Add approval workflow for course creation

---

## Questions & Gaps

[List unknowns or areas needing clarification]

**Example:**
- ❓ Should deleted courses be hidden from admin panel too?
- ❓ Need validation for course duration (currently unconstrained)

---

## Tags & Metadata

**Tags**: 🤖 #[feature-domain] #service #[status]

❓ **Add feature tags** (see TAGGING_STRATEGY_TAXONOMY.md):
- Feature Domain tag (e.g., #course-catalog)
- Technical tag: #service
- Status tag (e.g., #deployed)

**Example**: `#course-catalog #service #deployed`

**Related Features**: ❓ [Links to features in AKR_Main/features/]

---

## Documentation Standards

This template follows the **Minimal Service Documentation** approach:
- For simple CRUD services (<200 lines)
- Focuses on quick reference
- Detailed documentation in API database
- Augment with inline code comments for complex logic

See `backend_service_template_proposals.md` for template selection guidance.

---

**Template Version**: Minimal v1.1  
**Time to Complete**: 13-18 minutes  
**Best For**: Simple CRUD services, small teams, self-explanatory code  
**Last Updated**: 2024-12-05 (Added API Endpoints section for AI context)
