# AKR Charter: Database Documentation

**Version**: 1.0  
**Last Updated**: 2025-10-22  
**Extends**: AKR_CHARTER.md (universal principles)  
**Applies To**: Database objects (tables, views, stored procedures, functions, schemas)

---

## Purpose

This charter extends the universal **AKR_CHARTER.md** with conventions specific to database documentation. It applies to all database objects across all database projects (SQL Server, PostgreSQL, MySQL, etc.).

**Prerequisites**: Read AKR_CHARTER.md first for:
- Core principles (Lean, Flexible, Evolutionary, etc.)
- Universal conventions (generic types, feature tags, Git format)
- Documentation tiers (Essential/Recommended/Optional)

**This charter adds**:
- Database object naming conventions
- Schema organization patterns
- Database-specific documentation sections
- DDL and migration documentation practices

---

## Database Object Naming Conventions

### Tables

**Format**: `PascalCase` singular noun

**Examples**:
- ✅ `Courses`, `Users`, `Enrollments`
- ✅ `CourseCategories`, `CoursePrerequisites`
- ❌ `tbl_Courses` (avoid prefixes)
- ❌ `courses` (use PascalCase, not lowercase)
- ❌ `Course` table with multiple courses (should be `Courses`)

**Junction/Bridge Tables**:
- Format: `TableA_TableB` or `TableATableB`
- Example: `Course_Prerequisites` or `CoursePrerequisites`

---

### Views

**Format**: `vw_Description` (prefix with `vw_`)

**Examples**:
- ✅ `vw_ActiveCourses`
- ✅ `vw_UserEnrollmentSummary`
- ✅ `vw_ExpiredCertifications`
- ❌ `ActiveCoursesView` (use prefix, not suffix)
- ❌ `ActiveCourses` (ambiguous - table or view?)

**Rationale**: Prefix makes object type immediately clear in queries.

---

### Stored Procedures

**Format**: `usp_VerbNoun` (prefix with `usp_`)

**Examples**:
- ✅ `usp_GetUserCourses`
- ✅ `usp_EnrollUserInCourse`
- ✅ `usp_UpdateCourseStatus`
- ✅ `usp_DeleteExpiredEnrollments`
- ❌ `GetUserCourses` (missing prefix)
- ❌ `sp_GetUserCourses` (avoid `sp_` - reserved by SQL Server system)

**Verb conventions**:
- `Get` - Retrieve data (SELECT)
- `Create` / `Add` - Insert new records
- `Update` - Modify existing records
- `Delete` / `Remove` - Delete records
- `Process` - Complex multi-step operations
- `Calculate` - Computation-heavy operations

---

### Functions

**Scalar Functions**: `fn_Description`
**Table-Valued Functions**: `tvf_Description`

**Examples**:
- ✅ `fn_CalculateCertificationExpiry` (scalar)
- ✅ `tvf_GetActiveCoursesForUser` (table-valued)
- ❌ `CalculateCertificationExpiry` (missing prefix)

---

### Schemas

**Format**: Lowercase singular noun representing domain

**Examples**:
- ✅ `training` - Training/course management domain
- ✅ `auth` - Authentication/authorization
- ✅ `hr` - Human resources
- ✅ `finance` - Financial transactions
- ❌ `dbo` - Avoid default schema (organize by domain)
- ❌ `Training` - Use lowercase for schemas

**Rationale**: Schemas organize objects by business domain, making system architecture clear.

---

## Column Naming Conventions

### Primary Keys

**Format**: `Id` (GUID recommended)

**Examples**:
- ✅ `Id` (GUID, UNIQUEIDENTIFIER, UUID)
- ✅ `CourseId` (if composite key or for clarity)
- ❌ `course_id` (use PascalCase)
- ❌ `CourseID` (use `Id` not `ID`)

**Type**: GUID recommended over auto-increment INT
- Portability across systems
- Merge scenarios (no ID conflicts)
- Security (non-sequential IDs)

---

### Foreign Keys

**Format**: `[ReferencedTable]Id`

**Examples**:
- ✅ `UserId` (references Users.Id)
- ✅ `CourseId` (references Courses.Id)
- ✅ `CategoryId` (references Categories.Id)
- ❌ `User` (missing `Id` suffix)
- ❌ `FK_UserId` (avoid `FK_` prefix in column name)

---

### Boolean Flags

**Format**: `Is[Adjective]` or `Has[Noun]`

**Examples**:
- ✅ `IsActive`, `IsRequired`, `IsDeleted`
- ✅ `HasPrerequisites`, `HasExpiry`
- ❌ `Active` (ambiguous - what type is this?)
- ❌ `Deleted` (is this a date, flag, or status?)

**Type**: Boolean (native: BIT in SQL Server)

---

### Dates and Timestamps

**Format**: `[Action]At` or `[Event]Date`

**Examples**:
- ✅ `CreatedAt`, `UpdatedAt`, `DeletedAt`
- ✅ `EnrollmentDate`, `CompletionDate`, `ExpiryDate`
- ❌ `Created` (ambiguous - who or when?)
- ❌ `Timestamp` (too generic)

**Type**: DateTime (native: DATETIME2 in SQL Server for better precision)

---

### Audit Columns

**Standard audit columns** (recommended for all tables):
```sql
CreatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE()
CreatedBy UNIQUEIDENTIFIER NOT NULL -- FK to Users.Id
UpdatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE()
UpdatedBy UNIQUEIDENTIFIER NOT NULL -- FK to Users.Id
```

**Soft delete** (if using soft delete pattern):
```sql
IsDeleted BIT NOT NULL DEFAULT 0
DeletedAt DATETIME2 NULL
DeletedBy UNIQUEIDENTIFIER NULL -- FK to Users.Id
```

---

## Constraint Naming Conventions

### Primary Keys

**Format**: `PK_[TableName]`

**Example**: `PK_Courses`

---

### Foreign Keys

**Format**: `FK_[ChildTable]_[ParentTable]_[Column]`

**Examples**:
- ✅ `FK_Enrollments_Users_UserId`
- ✅ `FK_Enrollments_Courses_CourseId`
- ✅ `FK_CoursePrerequisites_Courses_PrerequisiteId`

**Rationale**: Format makes relationship immediately clear from constraint name.

---

### Unique Constraints

**Format**: `UQ_[TableName]_[Column(s)]`

**Examples**:
- ✅ `UQ_Users_Email` (single column)
- ✅ `UQ_Enrollments_UserId_CourseId` (composite)

---

### Check Constraints

**Format**: `CK_[TableName]_[Description]`

**Examples**:
- ✅ `CK_Courses_Title_NotEmpty`
- ✅ `CK_Enrollments_Status_ValidValues`
- ✅ `CK_Users_Email_Format`

---

### Default Constraints

**Format**: `DF_[TableName]_[Column]`

**Examples**:
- ✅ `DF_Courses_IsActive`
- ✅ `DF_Users_CreatedAt`

---

### Indexes

**Format**: `IX_[TableName]_[Column(s)]`

**Examples**:
- ✅ `IX_Courses_Category` (non-clustered index)
- ✅ `IX_Enrollments_UserId_Status` (composite index)
- ✅ `IX_Users_Email` (covering index for lookups)

---

## Documentation Structure for Database Objects

### Tables

**Essential Sections** (Tier 1):
- Table name, schema, last updated
- Purpose (what and why)
- Columns (all columns with descriptions)

**Recommended Sections** (Tier 2):
- Constraints (PK, FK, Unique, Check)
- Business Rules (BR-TABLENAME-### format)
- Related Objects (views, SPs, referenced tables)

**Optional Sections** (Tier 3):
- External Integrations (if accessed by other systems)
- Performance Considerations (indexes, query patterns, volume)
- Known Limitations (technical debt, design compromises)
- Future Considerations (planned refactoring)
- Security Notes (PII, encryption, access control)
- Data Migration Notes (legacy system sync, transformations)

**Template**: Use `table_doc_template.md`

---

### Views

**Essential Sections** (Tier 1):
- View name, schema, last updated
- Purpose (what data this view provides and why)
- Base Tables (which tables are queried)
- Columns (all columns with descriptions)

**Recommended Sections** (Tier 2):
- Filters/Conditions (what data is included/excluded)
- Joins (how tables are related)
- Performance Notes (materialized? indexed?)
- Usage Guidance (when to use this view)

**Optional Sections** (Tier 3):
- External Integrations
- Known Limitations (e.g., not real-time if materialized)

**Template**: Future `view_doc_template.md`

---

### Stored Procedures

**Essential Sections** (Tier 1):
- Procedure name, schema, last updated
- Purpose (what this procedure does and why)
- Parameters (all parameters with descriptions)
- Return Value (what is returned)

**Recommended Sections** (Tier 2):
- Business Logic (key steps/operations)
- Error Handling (what errors can occur)
- Transaction Scope (does it use transactions?)
- Performance Notes (expected execution time, optimization)

**Optional Sections** (Tier 3):
- Calling Examples (sample usage)
- Known Limitations
- Security Notes

**Template**: Future `sp_doc_template.md`

---

### Functions

**Similar to Stored Procedures**, but emphasize:
- Return type (scalar value or table)
- Determinism (deterministic or non-deterministic)
- Side effects (does it modify data? usually not)

---

## Database-Specific Documentation Patterns

### Documenting Constraints

**Check Constraints** - Translate to plain English:

**Example**:
```markdown
### Check Constraints

- `CK_Courses_Title_NotEmpty`: Enforces that Title cannot be empty or whitespace only
  - Expression: `len(ltrim(rtrim([Title])))>(0)`
  
- `CK_Enrollments_Status_ValidValues`: Restricts Status to valid enum values
  - Expression: `[Status] IN ('Pending', 'Active', 'Completed', 'Cancelled')`
```

**Rationale**: SQL expressions are hard to read. Plain English makes intent clear.

---

### Documenting Foreign Keys

**Format**:
```markdown
### Foreign Keys

- `UserId` → `auth.Users.Id` - Links enrollment to user account
- `CourseId` → `training.Courses.Id` - Links enrollment to course
```

**Include**:
- Column name
- Referenced schema.table.column
- Relationship description

---

### Documenting Indexes

**When to document**:
- ✅ Covering indexes (explain why these columns)
- ✅ Filtered indexes (explain filter condition)
- ✅ Indexes for specific query patterns
- ❌ Clustered index on PK (standard, no need to document)

**Format**:
```markdown
### Performance Considerations

**Indexes**:
- `IX_Enrollments_UserId_Status`: Optimized for "get enrollments by user and status" query
- `IX_Courses_Category_IsActive`: Filtered index (IsActive = 1) for active course lookups
```

---

### Documenting Triggers

**If triggers exist** (generally discouraged, but if used):

**Format**:
```markdown
### Triggers

- `TR_Users_Audit_Insert`: Logs user creation to audit table
  - Event: AFTER INSERT
  - Action: Inserts record to AuditLog with action 'USER_CREATED'
```

**Include**:
- Trigger name
- Event (AFTER INSERT, BEFORE UPDATE, etc.)
- Action (what the trigger does)
- Rationale (why this trigger exists)

---

## DDL and Migration Documentation

### Schema Changes

**Where**: Document in Git commit messages, not in table docs

**Format**:
```bash
git commit -m "db: add ValidityMonths to Courses table (FN99999_US089)" -m "
ALTER TABLE training.Courses
ADD ValidityMonths INT NULL;

Allows tracking certification expiration periods.
Existing courses will have NULL (no expiration).
"
```

**Rationale**: DDL changes are code-level. Git is the right place.

---

### Migration Scripts

**Where**: `migrations/` directory in database project

**Naming**: `YYYYMMDD_HHMM_Description.sql`

**Example**: `20251022_1430_AddValidityMonthsToCourses.sql`

**Content**:
```sql
-- Migration: Add ValidityMonths to Courses table
-- Feature: FN99999_US089
-- Date: 2025-10-22
-- Author: Alice Smith

-- Idempotent check
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID('training.Courses') 
    AND name = 'ValidityMonths'
)
BEGIN
    ALTER TABLE training.Courses
    ADD ValidityMonths INT NULL;
    
    PRINT 'ValidityMonths column added to Courses table';
END
ELSE
BEGIN
    PRINT 'ValidityMonths column already exists - skipping';
END
GO
```

**Key elements**:
- Header comment with context
- Idempotent (can run multiple times safely)
- Informative output messages

---

## Database-Specific Features Documentation

**When to document**: Any feature specific to your database that affects portability

**Examples for SQL Server**:
- NEWSEQUENTIALID()
- UNIQUEIDENTIFIER type
- CLUSTERED INDEX
- ROWVERSION / TIMESTAMP
- MERGE statement
- XML/JSON data types

**Examples for PostgreSQL**:
- UUID_GENERATE_V4()
- SERIAL type
- Array types
- JSONB type
- Extensions (e.g., PostGIS, pg_trgm)

**Format**:
```markdown
## Database-Specific Features

- **NEWSEQUENTIALID()** - SQL Server function for sequential GUIDs
  - Alternative in PostgreSQL: `UUID_GENERATE_V1()`
  - Alternative in MySQL: Generate GUID in application layer

- **UNIQUEIDENTIFIER** - SQL Server GUID type
  - Alternative in PostgreSQL: `UUID`
  - Alternative in MySQL: `CHAR(36)` with validation

⚠️ **Portability Note**: If migrating to a different database, 
these features will need alternative implementations.
```

---

## Schema Organization Best Practices

### Schema as Domain Boundary

**Recommended approach**: One schema per business domain

**Example**:
```
training.Courses
training.Enrollments
training.CourseCategories

auth.Users
auth.Roles
auth.Permissions

hr.Employees
hr.Departments
```

**Rationale**:
- Clear domain boundaries
- Easier to understand system architecture
- Supports eventual microservices split (if needed)
- Enables schema-level permissions

---

### Cross-Schema References

**Document when foreign keys cross schemas**:

**Example**:
```markdown
### Cross-Schema Dependencies

- `UserId` → `auth.Users.Id` - References user from authentication domain
```

**Rationale**: Highlights coupling between domains.

---

## Data Volume and Performance Documentation

### When to Document

**Don't document on Day 1** (no data yet)

**Do document when**:
- Table exceeds 100,000 rows
- Query performance becomes concern
- Indexes added for specific query patterns
- Partitioning implemented

**Format**:
```markdown
### Performance Considerations

**Current Volume**: ~500,000 courses (as of 2025-10)

**Growth Pattern**: +10,000 courses/year

**Query Patterns**:
- Most common: Filter by Category + IsActive (uses IX_Courses_Category_IsActive)
- Dashboard: Top 10 recent courses (uses IX_Courses_CreatedAt)

**Performance Notes**:
- Description field occasionally exceeds 1000 chars, consider limiting
- Full-text search needed if search functionality expands

**Indexes**:
- `IX_Courses_Category_IsActive`: Filtered index (IsActive = 1) - 95% of queries
- `IX_Courses_CreatedAt`: DESC index for recent courses queries
```

---

## Security and Compliance Documentation

### When to Document

**When table contains**:
- PII (Personally Identifiable Information)
- Sensitive data (passwords, tokens, financial data)
- Regulated data (GDPR, HIPAA, PCI-DSS, etc.)

**Format**:
```markdown
### Security & Compliance

**PII Fields**: Email, FirstName, LastName
**Compliance**: GDPR (right to deletion, data portability)

**Encryption**:
- PasswordHash: Bcrypt with cost factor 12
- Tokens: Encrypted at rest using TDE (Transparent Data Encryption)

**Access Control**:
- Read: Authenticated users (their own data)
- Write: Admin role only
- Audit: All changes logged to AuditLog table

**Retention**:
- Active users: Indefinite
- Inactive users: 7 years after last login (compliance requirement)
- Deleted users: 30-day soft delete, then permanent deletion
```

---

## Multi-Database Support

### If Supporting Multiple Database Platforms

**Document variations**:

**Example**:
```markdown
## Platform-Specific Implementations

### SQL Server
```sql
CREATE TABLE training.Courses (
    Id UNIQUEIDENTIFIER DEFAULT NEWSEQUENTIALID() PRIMARY KEY,
    ...
);
```

### PostgreSQL
```sql
CREATE TABLE training.courses (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    ...
);
```

**Key Differences**:
- SQL Server: PascalCase table/column names
- PostgreSQL: lowercase (convention)
- GUID generation functions differ
```

**Rationale**: Helps teams working across multiple platforms.

---

## Common Anti-Patterns to Avoid

### ❌ Don't: Hungarian Notation

**Bad**: `tblCourses`, `vwActiveCourses`, `spGetCourses`
**Good**: `Courses`, `vw_ActiveCourses`, `usp_GetCourses`

**Why**: Prefixes in object names are redundant (metadata shows object type).

---

### ❌ Don't: Abbreviations Without Reason

**Bad**: `Usr`, `Crs`, `Enr`
**Good**: `Users`, `Courses`, `Enrollments`

**Why**: Readability > brevity. Disk space is cheap, confusion is expensive.

---

### ❌ Don't: Generic Column Names

**Bad**: `Value`, `Data`, `Info`, `Details`
**Good**: `Amount`, `Description`, `Metadata`, `Configuration`

**Why**: Generic names provide no semantic meaning.

---

### ❌ Don't: Plural Table Names with Singular Primary Keys

**Bad**: `Courses` table with `CourseID` column
**Good**: `Courses` table with `Id` or `CourseId` column

**Why**: Consistency. If table is plural, either use `Id` or match table name.

---

## Quick Reference for Database Documentation

### Creating Table Documentation

1. Use `table_doc_template.md`
2. Follow AKR_CHARTER.md universal conventions
3. Use generic data types, note native types
4. Document constraints in plain English
5. Add optional sections as needed (not Day 1)
6. Commit with feature tag

**Time**: 15-30 minutes with LLM/script assistance

---

### Creating View Documentation

1. Use `view_doc_template.md` (when available)
2. Explain what data view provides
3. List base tables
4. Document filters/conditions
5. Note performance characteristics

---

### Creating Stored Procedure Documentation

1. Use `sp_doc_template.md` (when available)
2. Explain purpose
3. Document all parameters
4. Describe business logic
5. Note error handling
6. Provide usage example

---

## Technology-Specific Charter Evolution

### Version History

**Version 1.0** (2025-10-22): Initial database charter
- Naming conventions for all database objects
- Schema organization patterns
- Documentation structure for tables, views, SPs
- Constraint and index documentation patterns

---

## Questions & Support

**Questions about database conventions?**
- Reference this charter (AKR_CHARTER_DB.md)
- Check universal charter (AKR_CHARTER.md)
- Ask database team or DBA

**Proposing changes to database conventions?**
- Open PR with rationale
- Tag database team for review
- Cross-team discussion if it affects multiple projects

**Need help documenting complex database objects?**
- Check templates for structure
- Ask database team for examples
- Use LLM/script to generate first draft

---

**Remember**: Document what helps the team understand the database. Perfect documentation is less important than useful documentation.

---

**AKR Charter: Database - End of Document**
