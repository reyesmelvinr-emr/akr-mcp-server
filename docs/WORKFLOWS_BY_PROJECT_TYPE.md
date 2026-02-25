# Workflows by Project Type

This guide provides step-by-step instructions for setting up AKR documentation in your project, tailored to your project type. Choose the section that matches your project.

## Table of Contents

1. [Understanding AKR Markers](#understanding-markers) — Start here if new to AKR
2. [Backend/API Project](#backend-api-project) — .NET/C# API services
3. [Frontend/UI Project](#frontend--ui-project) — React/Vue/Angular components
4. [Database Project](#database-project) — SQL database and schema
5. [Monorepo Setup](#monorepo-setup) — Combined API + UI + Database

---

## Understanding Markers

Before you start, it's essential to understand how AKR marks content.

### 🤖 Auto-Extracted Marker
Appears when AKR successfully extracted information from your code.

**What it means:** "I found this in your code and filled it in automatically"

**What you should do:**
- ✅ Review for accuracy
- ✅ Fix any misinterpreted information
- ✅ Add links or context that helps other developers

**Example:**
```markdown
## API Endpoints

🤖 The following endpoints were extracted from your code:

- `GET /api/v1/users` — Retrieve all users
- `POST /api/v1/users` — Create new user
- `GET /api/v1/users/{id}` — Get user by ID
- `PUT /api/v1/users/{id}` — Update user
- `DELETE /api/v1/users/{id}` — Delete user
```

### ❓ Human Input Required Marker
Appears when AKR couldn't automatically extract information.

**What it means:** "I need your expertise here"

**What you should do:**
- 📝 Fill in with your knowledge
- 🎯 Be specific and actionable
- 🔗 Reference related documentation where appropriate

**Example:**
```markdown
## Business Rules

❓ Please add business rules specific to this service. Examples:
- Rate limiting constraints (e.g., max 100 requests/minute per user)
- Validation rules (e.g., email must be unique, password length >= 12)
- State transitions (e.g., order can only be cancelled if status is "pending")
- Data retention policies (e.g., logs deleted after 90 days)
```

### Mixed Example

Here's what a real generated document might look like:

```markdown
## Quick Reference

This service manages user authentication and profile information.

🤖 **Status:** Active and in production since 2023
🤖 **Owner Team:** Auth-Platform Team
🤖 **Language:** C#
🤖 **Key Dependencies:** 
- Identity.Core (password hashing)
- Email.Service (verification emails)

## API Endpoints

🤖 **Extracted 8 endpoints from codebase:**
- `POST /auth/register` — User registration
- `POST /auth/login` — User login
- `POST /auth/refresh` — Refresh token
- `GET /auth/profile` — Get current user profile
- `PUT /auth/profile` — Update user profile
- `POST /auth/logout` — User logout
- `POST /auth/password-reset` — Request password reset
- `POST /auth/password-reset/confirm` — Confirm password reset

## Business Rules

❓ **Please add business rules for this service:**
- What password validation rules apply?
- How long are tokens valid?
- What triggers account lockout?
- Do you enforce email verification?
- Rate limiting for auth endpoints?

Example answer:
```
- Minimum password length: 12 characters
- Must include: uppercase, lowercase, number, special character
- Token validity: 1 hour for access token, 30 days for refresh token
- Account lockout: After 5 failed login attempts for 15 minutes
- Email verification: Required before login
- Rate limit: 10 login attempts per 5 minutes per IP
```
```

---

## Backend/API Project

This section covers setting up documentation for .NET API services, controllers, and business logic.

### Step 1: Create mcp.json Configuration

In your project root, create or update `mcp.json`:

```json
{
  "workspace_root": "/path/to/your/project",
  "project_type": "backend-api",
  "language": "csharp",
  "documentation_root": "docs/services",
  "component_mappings": {
    "TrainingTracker.Api/Domain/Services/CourseService.cs": {
      "template": "lean_baseline_service_template.md",
      "doc_path": "docs/services/CourseService_doc.md",
      "component_type": "service"
    },
    "TrainingTracker.Api/Controllers/CoursesController.cs": {
      "template": "lean_baseline_service_template.md",
      "doc_path": "docs/services/CoursesController_doc.md",
      "component_type": "controller"
    },
    "TrainingTracker.Api/Infrastructure/Database/": {
      "template": "table_doc_template.md",
      "doc_path": "docs/database/",
      "component_type": "database"
    }
  },
  "team": {
    "maintainers": ["backend-team@company.com"],
    "review_required": true,
    "notification_channel": "slack"
  },
  "validation": {
    "enforce_completeness": 80,
    "require_examples": true,
    "require_error_cases": true
  }
}
```

**Key fields:**
- `workspace_root` — Root path of your project (usually project folder)
- `project_type` — Always "backend-api" for this guide
- `language` — "csharp" for .NET projects
- `component_mappings` — Maps source files to documentation templates
- `team` — Team info for documentation ownership
- `validation` — Compliance rules (80%+ completeness required)

### Step 2: Generate Service Documentation

Documenting the `CourseService`:

1. **Ask Copilot to generate stub:**
   ```
   Generate AKR documentation for CourseService using lean_baseline_service_template.md
   ```

2. **Copilot will:**
   - Extract service methods and dependencies
   - Identify parameters and return types
   - Extract XML documentation comments
   - Create documentation stub with 🤖 auto-populated sections

3. **Example output structure:**
   ```
   # CourseService
   
   🤖 **Service Type:** Business Logic Service
   🤖 **Namespace:** TrainingTracker.Api.Domain.Services
   🤖 **Key Dependencies:**
   - IRepository<Course>
   - IEmailService
   - IValidator<CourseDto>
   
   🤖 **Public Methods:**
   - GetAllCourses(int pageNumber, int pageSize)
   - GetCourseById(int courseId)
   - CreateCourse(CreateCourseDto dto)
   - UpdateCourse(int courseId, UpdateCourseDto dto)
   - DeleteCourse(int courseId)
   
   ## How It Works
   
   🤖 The service follows these patterns:
   - Dependency injection via constructor
   - Async/await for all I/O operations
   - Validation before data mutations
   - Exception handling with custom exceptions
   
   ## Business Rules
   
   ❓ Please document business rules:
   - Can deleted courses be recovered?
   - Does creating a course trigger notifications?
   - What validates course title (length, uniqueness)?
   - Are there approval workflows for course creation?
   ```

### Step 3: Review and Enhance

Review the generated stub and fill in ❓ sections:

```markdown
## Business Rules

✅ Filled in by you:
- Courses must have unique titles within same department
- Course creation triggers notification to department head
- Deleted courses are soft-deleted (flagged as inactive, not removed)
- Only active courses appear in public listings
- Draft courses only visible to course creator and admins

## Data Operations

🤖 Extracted database interactions:
- Course records stored in dbo.Courses table
- Related records: Enrollments (foreign key on CourseId)
- Indexes: IX_Courses_DepartmentId, IX_Courses_CreatedDate

## Common Problems & Solutions

❓ What issues have developers encountered?

✅ Filled in by you:
1. **Getting 404 for course that exists**
   - Likely the course is marked inactive
   - Check `IsActive` flag in database
   - Use admin dashboard to reactivate

2. **Slow course load for courses with 10k+ enrollments**
   - N+1 query problem: always use .Include(c => c.Enrollments) when loading
   - Consider pagination if returning all enrollments
   - Use filtered queries for reporting (e.g., enrollments in last 30 days)
```

### Step 4: Validate and Write

Before saving:

```bash
# Run validation to check compliance
python scripts/validation/validate_documentation.py docs/services/CourseService_doc.md
```

Expected output:
```
✓ Frontmatter valid
✓ All required sections present
✓ Completeness: 87% (exceeds 80% minimum)
✓ No dead links detected
✓ Ready to write to git
```

Then save:
```
Use Copilot to write the documentation with: write_documentation tool
```

### Step 5: Document Related Components

Document all services in your API:

**Typical structure:**
```
docs/
├── services/
│   ├── CourseService_doc.md       # Business logic service
│   ├── CoursesController_doc.md   # API controller
│   ├── EnrollmentService_doc.md
│   ├── EnrollmentsController_doc.md
│   ├── PaymentService_doc.md
│   └── PaymentController_doc.md
└── database/
    ├── Courses_table.md
    ├── Enrollments_table.md
    └── Payments_table.md
```

### Backend Example: Complete CourseService Documentation

Here's what a completed service documentation looks like after filling in manual sections:

```markdown
---
service_name: CourseService
service_type: business_logic
language: csharp
namespace: TrainingTracker.Api.Domain.Services
created_date: 2026-02-19
last_updated: 2026-02-19
version: 1.0
---

# CourseService

Core service managing course lifecycle including creation, updates, and retrievals.

## Quick Reference (TL;DR)

🤖 **Language:** C# | **Type:** Service | **Status:** Active in production
🤖 **Dependencies:** 3 (IRepository<Course>, IEmailService, IValidator<CourseDto>)
🤖 **Public Methods:** 5 (GetAllCourses, GetCourseById, CreateCourse, UpdateCourse, DeleteCourse)

✅ **Owned by:** Backend Team | **Review Required:** Yes

## What & Why

Course management is a critical path in the training platform. The CourseService abstracts all course-related operations, providing a clean interface for controllers while enforcing business rules at the service layer.

❓ Why this service exists:
- Centralizes course business logic (not scattered in controller)
- Ensures consistent validation and error handling
- Makes it easy to reuse course operations across multiple controllers/features

## How It Works

🤖 Service uses dependency injection pattern:

```csharp
public CourseService(
  IRepository<Course> courseRepository,
  IEmailService emailService,
  IValidator<CourseDto> courseValidator)
{
  _courseRepository = courseRepository;
  _emailService = emailService;
  _courseValidator = courseValidator;
}
```

All methods are async and follow this pattern:
1. Validate input with injected validator
2. Query/modify repository
3. Trigger notifications if needed
4. Return result or throw specific exception

## Business Rules

✅ Documented by team:

1. **Course titles must be unique** within the same department
   - Exception: Archived courses can have duplicate titles (they're hidden from UI)

2. **Course creation notifications**
   - Department head receives email notification
   - Auto-add department head as co-instructor

3. **Course deletion is soft-delete**
   - Records never truly removed from database
   - IsActive flag set to false
   - Deleted courses don't appear in public listings

4. **Public/Draft visibility**
   - Draft courses only visible to creator and admins
   - Published courses visible to all authenticated users
   - Preview by guests possible with special token

## Architecture

🤖 Layered architecture pattern:

```
Controllers (HTTP)
    ↓
CourseService (Business Logic)
    ↓
IRepository<Course> (Data Access)
    ↓
Database
```

Service layer validates and enforces rules before persistence.

## API Contract (AI Context)

🤖 Extracted public methods:

```csharp
// GET - Retrieve paginated list
public async Task<PagedResult<CourseDto>> GetAllCourses(
  int pageNumber = 1,
  int pageSize = 20,
  string? searchTerm = null,
  bool onlyActive = true)

// GET - Single record
public async Task<CourseDto> GetCourseById(int courseId)

// POST - Create new
public async Task<CourseDto> CreateCourse(CreateCourseDto dto)

// PUT - Update existing
public async Task<CourseDto> UpdateCourse(int courseId, UpdateCourseDto dto)

// DELETE - Soft delete
public async Task DeleteCourse(int courseId)
```

## Validation Rules

🤖 Validators extracted from code:

- Course title: Required, 3-100 characters, unique per department
- Course description: Optional, max 500 characters
- DepartmentId: Required, must exist in database
- StartDate: Required, must not be in past
- EndDate: Required, must be after StartDate
- InstructorIds: Required, at least 1, max 5 instructors

❓ Additional validation rules:

- Course code must follow format: [DEPT]-[YEAR]-[NUMBER] (e.g., ENG-2024-101)
- No two courses can run simultaneously in same room
- Course fees must be $0 or $10-$500 (no arbitrary amounts)

## Data Operations

🤖 Database tables involved:

- **dbo.Courses** (primary)
  - Columns: CourseId, Title, Description, DepartmentId, StartDate, EndDate, IsActive, CreatedDate, ModifiedDate
  - Primary Key: CourseId
  - Indexes: IX_DepartmentId, IX_StartDate, IX_IsActive

- **dbo.Enrollments** (related)
  - Foreign key: CourseId → dbo.Courses.CourseId
  - Deleting course cascades to enrollments (soft-delete only)

- **dbo.CourseInstructors** (related)
  - Maps instructors to courses
  - Deleting course removes all instructor mappings

## Questions & Gaps

❓ Current unknowns:

- [ ] What's the SLA for GetAllCourses with 100k+ records?
- [ ] Should deleted courses be permanently purged after 1 year?
- [ ] Need audit trail of who created/updated each course?
- [ ] Should duplicate titles be allowed in different departments with different names? (E.g., "English 101" in both ENG and CORE departments)
```

---

## Frontend / UI Project

This section covers setting up documentation for React, Vue, or Angular components.

### Step 1: Create mcp.json Configuration

```json
{
  "workspace_root": "/path/to/your/project",
  "project_type": "ui",
  "language": "typescript",
  "framework": "react",
  "documentation_root": "docs/components",
  "component_mappings": {
    "src/components/CourseList/CourseList.tsx": {
      "template": "ui_component_template.md",
      "doc_path": "docs/components/CourseList_doc.md",
      "component_type": "visual_component"
    },
    "src/components/CourseForm/CourseForm.tsx": {
      "template": "ui_component_template.md",
      "doc_path": "docs/components/CourseForm_doc.md",
      "component_type": "visual_component"
    },
    "src/hooks/useCourses.ts": {
      "template": "lean_baseline_service_template.md",
      "doc_path": "docs/hooks/useCourses_doc.md",
      "component_type": "custom_hook"
    }
  },
  "team": {
    "maintainers": ["frontend-team@company.com"],
    "design_token_owner": "design-team@company.com"
  },
  "validation": {
    "require_accessibility_notes": true,
    "require_responsive_behavior": true,
    "require_storybook_examples": true
  }
}
```

### Step 2: Generate Component Documentation

For `CourseList` component:

```
Generate AKR documentation for CourseList component using ui_component_template.md
```

### Step 3: Complete Generated Documentation

Example completed documentation:

```markdown
---
component_name: CourseList
component_type: List/Table component
framework: React
language: TypeScript
created_date: 2026-02-19
last_updated: 2026-02-19
---

# CourseList Component

Displays a paginated list of courses with filtering, sorting, and bulk actions.

## Quick Reference

🤖 **Type:** Functional Component | **Framework:** React | **Language:** TypeScript
🤖 **Props:** 7 (courses, isLoading, error, onView, onEdit, onDelete, onBulkAction)
🤖 **State:** Managed via Redux (CourseState)
🤖 **Dependencies:** Material-UI, React Router

## Purpose & Context

Displays courses in a table format with:
- Sorting by title, date, instructor
- Filtering by department, status
- Bulk actions (archive, share, delete)
- Row-level actions (view, edit, delete)
- Responsive design for mobile/tablet

## Props API

🤖 Extracted from component code:

```typescript
interface CourseListProps {
  // Data
  courses: Course[];
  
  // Loading states
  isLoading: boolean;
  error?: Error | null;
  
  // Pagination
  pageNumber: number;
  pageSize: number;
  totalCount: number;
  
  // Callbacks
  onView: (courseId: number) => void;
  onEdit: (courseId: number) => void;
  onDelete: (courseId: number) => void;
  onBulkAction: (action: 'archive' | 'share' | 'delete', courseIds: number[]) => void;
}
```

## Visual States & Variants

❓ Document visual states:

**Empty State:**
- When courses.length === 0
- Shows icon + message: "No courses yet. Create your first course."
- Provides CTA button to CourseForm

**Loading State:**
- Shows skeleton loaders instead of rows
- Maintains table grid to prevent layout shift
- Disables all interactions

**Error State:**
- Shows error icon + message
- Provides "Retry" button to reload
- Example: "Failed to load courses. Server returned 500."

**Mobile/Tablet:**
- On screens < 1024px: hide Department column, inline Actions
- On screens < 768px: switch to card view instead of table
- Touch-friendly: increase button padding and spacing

## Component Behavior

🤖 Extracted interactions:

- **Sort:** Click column headers to sort (toggles asc/desc)
- **Filter:** Open filter drawer, select criteria, click Apply
- **Paginate:** Use Next/Previous buttons or page selector
- **Row Action:** Click row opens detail view (onView or onEdit)
- **Bulk Select:** Checkbox to select multiple, shows bulk action toolbar
- **Refresh:** Click refresh icon to reload data

✅ Additional behaviors documented by you:

- **Keyboard Navigation:**
  - Tab: Move between rows
  - Enter: Open detail view
  - Space: Select/deselect row
  - Escape: Clear selection

- **Error Recovery:**
  - Network error → Show retry button
  - Invalid data → Log warning, render placeholders
  - Permission denied → Hide restricted columns, disable actions

## Styling & Theming

🤖 Material-UI components used:
- MuiTable for layout
- MuiTableHead, MuiTableBody, MuiTableRow
- MuiButton for actions
- MuiCheckbox for selection
- MuiCircularProgress for loading

✅ Custom styling by you:

- **Color scheme:** Uses theme colors
  - Text: theme.palette.text.primary
  - Actions: theme.palette.primary.main
  - Disabled: theme.palette.action.disabled

- **Spacing:** Uses theme.spacing()
  - Row height: 52px (default)
  - Cell padding: 16px

- **Dark mode:** Fully supported
  - Background: theme.palette.background.paper
  - Text contrast maintained

## Accessibility

🤖 Built with accessibility:
- Table semantic HTML (table, thead, tbody, tr, td)
- Buttons have aria-label for screen readers
- Loading states announced with aria-busy

✅ Ensuring accessibility by you:

- **Screen Reader:**
  - Table has caption: "Published Courses"
  - Sort buttons announce current sort state
  - Bulk action toolbar announces selection count

- **Keyboard Access:**
  - All interactions available via keyboard
  - Tab order is logical and predictable
  - Focus indicators always visible

- **Color:** No information conveyed by color alone
  - Status shown with icon + text
  - Error messages use icon + text (not red alone)

## Usage Examples

### Basic usage:

```tsx
<CourseList
  courses={courses}
  isLoading={false}
  pageNumber={1}
  pageSize={20}
  totalCount={150}
  onView={(id) => navigate(`/courses/${id}`)}
  onEdit={(id) => navigate(`/courses/${id}/edit`)}
  onDelete={(id) => dispatch(deleteCourse(id))}
  onBulkAction={(action, ids) => dispatch(bulkAction(action, ids))}
/>
```

### With error handling:

```tsx
<CourseList
  courses={visibleCourses}
  isLoading={loading}
  error={error}
  pageNumber={page}
  pageSize={20}
  totalCount={total}
  onView={handleView}
  onEdit={handleEdit}
  onDelete={handleDelete}
  onBulkAction={handleBulkAction}
/>

{error && (
  <Alert severity="error">
    {error.message}
    <Button onClick={() => refetchCourses()}>Retry</Button>
  </Alert>
)}
```

## Performance Considerations

🤖 Current implementation:

- Component re-renders when props change
- No memoization (renders every parent change)

✅ Performance optimizations documented:

- [ ] **Use React.memo** to prevent unnecessary re-renders when parent changes
- [ ] **Virtualize tall lists** (100+ rows) using react-window
- [ ] **Debounce filter changes** to avoid excessive API calls
- [ ] **Paginate** to limit rows rendered (never show >100 rows)

Estimated performance:
- 20 rows: <100ms render
- 100 rows: <300ms render
- 1000 rows: Consider virtualization

## Testing

✅ Test coverage by you:

```typescript
describe('CourseList', () => {
  test('renders course list with data', () => {
    // 4 course items rendered
    expect(screen.getAllByRole('row')).toHaveLength(5); // 4 data + 1 header
  });

  test('calls onView when clicking course row', () => {
    const onView = jest.fn();
    render(<CourseList courses={mockCourses} onView={onView} {...props} />);
    fireEvent.click(screen.getByText('English 101'));
    expect(onView).toHaveBeenCalledWith(1);
  });

  test('shows loading skeleton when isLoading=true', () => {
    render(<CourseList isLoading={true} courses={[]} {...props} />);
    expect(screen.getAllByTestId('skeleton-loader')).toHaveLength(5);
  });

  test('shows error message when error prop set', () => {
    render(<CourseList error={new Error('Failed')} courses={[]} {...props} />);
    expect(screen.getByText(/Failed to load/)).toBeInTheDocument();
  });
});
```

## Known Issues & Limitations

❓ Current limitations documented:

- **Large datasets:** Slow with 1000+ rows (need virtualization)
- **Bulk delete:** No undo after deletion
- **Filter state:** Lost on page refresh (not persisted)
- **Mobile:** Horizontal scroll on tables < 1024px (not responsive columns yet)

## Migration Guide

If upgrading from v0.5 to v1.0:

- Props structure unchanged (backward compatible)
- New: Add `totalCount` prop for pagination
- New: onBulkAction callback for multi-select
- Deprecated: onDeleteAll callback (use onBulkAction instead)

```tsx
// Old (v0.5)
<CourseList courses={courses} onDeleteAll={handleDeleteAll} />

// New (v1.0)
<CourseList 
  courses={courses}
  totalCount={150}
  onBulkAction={(action, ids) => action === 'delete' && handleDelete(ids)}
/>
```

## Questions & Gaps

❓ Design questions:

- [ ] Should filter state persist across page navigation?
- [ ] Should we add export to CSV feature?
- [ ] Need drag-to-reorder columns feature?
- [ ] Should bulk actions show confirmation dialog?
```

---

## Database Project

This section covers documenting SQL database schemas and tables.

### Step 1: Create mcp.json Configuration

```json
{
  "workspace_root": "/path/to/your/project",
  "project_type": "database",
  "language": "sql",
  "database_type": "sqlserver",
  "documentation_root": "docs/database",
  "component_mappings": {
    "POC_SpecKitProj.sqlproj": {
      "template": "embedded_database_template.md",
      "doc_path": "docs/database/SpecKit_Database_doc.md"
    },
    "dbo.Courses": {
      "template": "table_doc_template.md",
      "doc_path": "docs/database/Courses_table.md"
    },
    "dbo.Enrollments": {
      "template": "table_doc_template.md",
      "doc_path": "docs/database/Enrollments_table.md"
    }
  },
  "team": {
    "maintainers": ["dba-team@company.com"],
    "review_required": true
  },
  "validation": {
    "require_constraints": true,
    "require_business_rules": true
  }
}
```

### Step 2: Generate Database Documentation

For your database schema:

```
Generate AKR documentation for SpecKit database using embedded_database_template.md
```

### Step 3: Generate Table Documentation

For individual tables:

```
Generate AKR documentation for Courses table using table_doc_template.md
```

### Step 4: Complete Database Documentation

Example completed Courses table documentation:

```markdown
---
table_name: dbo.Courses
database: SpecKit
row_estimate: 500
last_modified: 2026-02-15
---

# dbo.Courses Table

Stores information about training courses offered in the system.

## Purpose

Courses are the core organizational unit. Each course represents a distinct training offering with specific instructors, schedule, and attendees.

## Columns

🤖 Extracted from schema:

| Column | Type | Nullable | Key | Description |
|--------|------|----------|-----|-------------|
| CourseId | int | No | PK | Unique course identifier |
| Title | nvarchar(200) | No | | Course display name |
| Description | nvarchar(max) | Yes | | Extended course description |
| DepartmentId | int | No | FK | Reference to Department |
| StartDate | datetime | No | | Course start date and time |
| EndDate | datetime | No | | Course end date and time |
| InstructorId | int | No | FK | Primary instructor |
| Capacity | int | No | | Maximum enrollments |
| IsActive | bit | No | | Soft-delete flag (0=archived, 1=active) |
| CreatedDate | datetime | No | | Record creation timestamp |
| ModifiedDate | datetime | Yes | | Last update timestamp |
| CreatedBy | nvarchar(100) | No | | User who created |
| ModifiedBy | nvarchar(100) | Yes | | User who last modified |

❓ Document column purposes beyond schema:

- **Capacity:** Once reached, course marked full. Waitlist opens at capacity + 5.
- **IsActive:** Provides soft delete. Archived courses retain enrollment history.

## Constraints

🤖 Extracted from schema:

**Primary Key:**
- PK_Courses_CourseId (CourseId)

**Foreign Keys:**
- FK_Courses_DepartmentId → Department.DepartmentId
- FK_Courses_InstructorId → Instructor.InstructorId

**Unique Constraints:**
- (DepartmentId, Title) — Course titles unique per department

**Check Constraints:**
- StartDate < EndDate
- Capacity > 0
- Capacity <= 500 (no course can exceed 500)

**Indexes:**
- IX_Courses_DepartmentId
- IX_Courses_StartDate
- IX_Courses_IsActive
- IX_Courses_CreatedDate

❓ Additional constraints by you:

- No course can start before department's academic year start
- No course can end after department's academic year end
- Course title cannot contain only numbers

## Business Rules

✅ Business rules documented:

1. **Course Lifecycle:**
   - Created with StartDate in future (cannot create backdated courses)
   - Once StartDate passes, cannot modify StartDate or EndDate
   - Can be archived anytime via IsActive = 0
   - Archived courses visible only to admins and enrolled users

2. **Enrollment Rules:**
   - When Capacity reached, course status = "Full"
   - Waitlist begins accepting at Capacity + 1
   - Users can self-enroll if capacity available
   - Dropping course 24 hours before start deletes enrollment
   - Dropping course < 24 hours before start marks as no-show

3. **Financial:**
   - Course cost determined by DepartmentId, not stored here
   - Override pricing stored in CourseOverride table
   - Refunds follow department policy (30/60/90 day tiers)

4. **Data Retention:**
   - Active courses: indefinitely
   - Archived courses (< 3 years old): indefinitely (audit trail)
   - Archived courses (> 3 years old): can be permanently deleted
   - Enrollment records always retained (separate table, separate retention policy)

## Related Objects

🤖 Relationships:

- **Department** (parent) — Many-to-One
  - Cannot delete department if has active courses
  - Cascade soft-delete when department archived

- **Enrollments** (child) — One-to-Many
  - ~5-50 enrollments per course typical
  - When course archived, enrollments not deleted but marked as "orphaned"
  - ~500k enrollment records total

- **Instructors** (parent) — Many-to-One  
  - ~2-10 courses per instructor typical
  - Cannot delete instructor with active courses (reassign first)

- **CourseInstructor** (bridge) — One-to-Many
  - Primary instructor in Courses table
  - Additional instructors in separate CoursInstructor bridge table
  - Max 5 instructors per course (enforced by app logic, not DB)

❓ Are there other related tables?

- CourseSchedule? (if meeting times vary)
- CourseLocation? (if offered at multiple locations)
- CoursePrerequisites? (if prerequisites exist)
```

---

## Monorepo Setup

For projects combining Backend (API) + Frontend (UI) + Database in single git repo.

### Step 1: Directory Structure

```
my-project/
├── mcp.json                    # Single config for all 3 components
├── docs/
│   ├── services/              # Backend services
│   │   ├── UserService_doc.md
│   │   └── PaymentService_doc.md
│   ├── components/            # Frontend components
│   │   ├── UserForm_doc.md
│   │   └── PaymentWidget_doc.md
│   └── database/              # Database docs
│       ├── Users_table.md
│       └── Payments_table.md
├── api/                       # Backend .NET project
├── ui/                        # Frontend React/Vue/Angular
└── database/                  # SQL project
```

### Step 2: Configure Single mcp.json

```json
{
  "workspace_root": "/path/to/project",
  "project_type": "monorepo",
  "projects": {
    "api": {
      "type": "backend-api",
      "language": "csharp",
      "root": "api/",
      "documentation_root": "docs/services/"
    },
    "ui": {
      "type": "ui",
      "language": "typescript",
      "framework": "react",
      "root": "ui/",
      "documentation_root": "docs/components/"
    },
    "database": {
      "type": "database",
      "language": "sql",
      "database_type": "sqlserver",
      "root": "database/",
      "documentation_root": "docs/database/"
    }
  },
  "component_mappings": {
    "api/Domain/Services/UserService.cs": {
      "template": "lean_baseline_service_template.md",
      "doc_path": "docs/services/UserService_doc.md"
    },
    "ui/src/components/UserForm/UserForm.tsx": {
      "template": "ui_component_template.md",
      "doc_path": "docs/components/UserForm_doc.md"
    },
    "database/dbo.Users": {
      "template": "table_doc_template.md",
      "doc_path": "docs/database/Users_table.md"
    }
  },
  "team": {
    "maintainers": ["team@company.com"],
    "review_required": true
  }
}
```

### Step 3: Generate Documentation for Each Component

Generate documentation for a service:
```
Generate AKR documentation for api/Domain/Services/UserService.cs using lean_baseline_service_template.md
```

Generate documentation for a component:
```
Generate AKR documentation for ui/src/components/UserForm/UserForm.tsx using ui_component_template.md
```

Generate documentation for a table:
```
Generate AKR documentation for database/dbo.Users using table_doc_template.md
```

### Step 4: Consistency Across Layers

Ensure documentation shows how layers interact:

**UserService documentation (backend/services/UserService_doc.md):**
```markdown
## What & Why

The UserService encapsulates all user-related business logic for the training platform.

## How It Works

Follows standard layered architecture:
- HttpRequest → UserController → UserService → UserRepository → Database

## API Contract

🤖 Endpoints exposed via UserController:
- GET /api/users — GetAllUsers
- GET /api/users/{id} — GetUserById  
- POST /api/users — CreateUser
- PUT /api/users/{id} — UpdateUser

## Database Operations

Uses dbo.Users table. See Users Table Documentation (docs/database/Users_table.md).
```

**UserForm documentation (frontend/components/UserForm_doc.md):**
```markdown
## Purpose & Context

Form for creating and editing users. Calls UserController endpoints.

## Data Flow

1. User submits form
2. Component calls POST /api/users or PUT /api/users/{id}
3. UserController validates and calls UserService
4. UserService applies business rules and saves to dbo.Users
5. Response returned to component, UI updates

See UserService Documentation (docs/services/UserService_doc.md) for backend logic.

## API Integration

```typescript
const response = await fetch('/api/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    firstName: formData.firstName,
    lastName: formData.lastName,
    email: formData.email
  })
});
```

See API Contract in UserService docs (docs/services/UserService_doc.md#api-contract) for full endpoint spec.
```

**Users table documentation (database/database/Users_table.md):**
```markdown
## Purpose

Stores user profile data for all platform users.

## Columns

| Column | Type | Notes |
|--------|------|-------|
| UserId | int | PK, auto-increment |
| FirstName | nvarchar(100) | From UserForm.firstName |
| LastName | nvarchar(100) | From UserForm.lastName |
| Email | nvarchar(255) | Unique, from UserForm.email |

## Related Tables

- Users → Enrollments (user can have many enrollments)
- See Enrollments Table (docs/database/Enrollments_table.md)

## Data Source

UserController calls UserService which persists to this table.
See UserService Documentation (docs/services/UserService_doc.md).
```

This creates a documentation web where each piece links to related pieces, showing how the full system works end-to-end.

---

## Summary

You now have:
- ✅ Understood 🤖 vs ❓ markers
- ✅ Set up mcp.json for your project type
- ✅ Generated documentation stubs
- ✅ Completed documentation with business rules and examples
- ✅ Validated documentation compliance
- ✅ Written documentation to disk with git integration

## Next Steps

1. **Generate docs for all major components** in your project
2. **Link documentation together** (see cross-references in examples)
3. **Share with team** and get feedback on auto-extracted sections
4. **Review quarterly** to keep documentation current as code changes
5. **Reference in pull requests** — Link documentation in PR descriptions

---

## Getting Help

- **Installation issues?** → See [Installation and Setup](INSTALLATION_AND_SETUP.md)
- **Quick answers?** → See [Quick Reference](QUICK_REFERENCE.md)
- **Technical details?** → See [Developer Reference](DEVELOPER_REFERENCE.md)
- **System architecture?** → See [System Architecture](ARCHITECTURE.md)
