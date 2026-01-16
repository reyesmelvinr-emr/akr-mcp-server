# Table Documentation Developer Guide

**Version**: 1.0  
**Last Updated**: 2025-11-10  
**For**: Developers documenting database tables  
**Related**: AKR_CHARTER_DB.md, table_doc_template.md

---

## Purpose

This guide shows you **exactly how** to document database tables using the AKR system. It's practical, step-by-step, and designed to work with GitHub Copilot for maximum efficiency.

**Target time**: 15-25 minutes per table (baseline documentation)

**What you'll learn**:
1. Which files to attach to Copilot for best results
2. Standard prompts for VS Code/Visual Studio with Copilot
3. Standard prompts for GitHub Copilot Spaces
4. How to enhance AI-generated documentation
5. Common scenarios and solutions

---

## Quick Start (5-Minute Version)

If you're experienced and just need a reminder:

### Using VS Code/Visual Studio with Copilot
1. **Gather context**: Table DDL file + template
2. **Open Copilot Chat**: Ctrl+Shift+I (Windows) or Cmd+Shift+I (Mac)
3. **Attach files**: @table_doc_template.md @Tables.Courses.sql
4. **Use standard prompt**: See "Standard Prompt for VS Code/Visual Studio" section
5. **Enhance**: Add business context, verify constraints
6. **Save**: docs/tables/[TableName]_doc.md

### Using GitHub Copilot Spaces
1. **Open Spaces**: Select table DDL file, open Copilot Spaces
2. **Use standard prompt**: See "Standard Prompt for GitHub Copilot Spaces" section
3. **Enhance**: Add business context
4. **Save**: docs/tables/[TableName]_doc.md

**Now read the detailed guide for best practices...**

---

## The Complete Process (Step-by-Step)

### Step 1: Identify the Table to Document (1 minute)

**Start with tables that are**:
- ✅ Core business entities (Courses, Users, Enrollments)
- ✅ High transaction volume (frequently read/written)
- ✅ Complex constraints (many business rules)
- ✅ Referenced by many other tables (foreign key targets)

**Skip tables that are**:
- ❌ Framework/ORM tables (migrations, schema versions)
- ❌ Simple lookup tables with 2-3 columns and static data
- ❌ Temporary/staging tables
- ❌ Audit/log tables (unless complex business rules)

**Example prioritization**:
```
Priority 1 (document first):
- Courses (core business entity)
- Users (core business entity)
- Enrollments (core business entity)
- EnrollmentStatus (referenced by Enrollments)

Priority 2 (document when time permits):
- CoursePrerequisites (business logic)
- AuditLog (if complex retention rules)

Priority 3 (document only if complex):
- CourseCategories (simple lookup)
- States (static reference data)
```

---

### Step 2: Gather Required Files (2 minutes)

#### File Selection Strategy

Choose a strategy based on your database project structure:

---

#### **Strategy A: SQL Server Database Project (SSDT)**

Use this if your project uses Visual Studio SQL Server Data Tools.

**Priority 1 - MUST HAVE** (Core context):
```
✅ Table DDL file
   📁 POC_SpecKitProj/training/Tables/Courses.sql

✅ Template file
   📁 AKR files/table_doc_template.md
```

**Priority 2 - SHOULD HAVE** (Rich context):
```
✅ Related table DDL (for foreign key understanding)
   📁 POC_SpecKitProj/training/Tables/Enrollments.sql
   (If Enrollments references Courses)

✅ View that uses this table
   📁 POC_SpecKitProj/training/Views/vw_CourseEnrollmentSummary.sql
   (Shows how table is commonly queried)
```

**Priority 3 - NICE TO HAVE** (Optional enhancements):
```
✅ Stored procedure that modifies table
   📁 POC_SpecKitProj/training/Stored Procedures/usp_CreateCourse.sql
   (Shows business logic)
```

**Example attachment list for Courses table**:
```
Required (P1):
- POC_SpecKitProj/training/Tables/Courses.sql
- AKR files/table_doc_template.md

Recommended (P2):
- POC_SpecKitProj/training/Tables/Enrollments.sql (references Courses)
- POC_SpecKitProj/training/Views/vw_CourseEnrollmentSummary.sql
```

---

#### **Strategy B: Migration-Based Project (Entity Framework, Flyway, Liquibase)**

Use this if your schema is defined in migration files:

**Priority 1**:
```
✅ Latest CREATE TABLE migration
   📁 migrations/V001__Create_Courses_Table.sql

✅ Template file
   📁 AKR files/table_doc_template.md
```

**Priority 2**:
```
✅ ALTER TABLE migrations for this table
   📁 migrations/V015__Add_Courses_ValidityMonths.sql
   📁 migrations/V022__Add_Courses_IsArchived.sql
   (Shows table evolution)

✅ Entity/Model class (if using ORM)
   📁 src/Domain/Entities/Course.cs
   (Shows how application uses table)
```

---

#### **Strategy C: ORM-First Project (Code-First Entity Framework, Django, etc.)**

Use this if schema is generated from code:

**Priority 1**:
```
✅ Entity/Model class
   📁 backend/Domain/Entities/Course.cs
   (Source of truth for schema)

✅ Template file
   📁 AKR files/table_doc_template.md
```

**Priority 2**:
```
✅ DbContext/Configuration class
   📁 backend/Infrastructure/Data/Configurations/CourseConfiguration.cs
   (Shows constraints, indexes, relationships)

✅ Generated migration file (if available)
   📁 backend/Migrations/20251110_CreateCourses.cs
   (Shows actual SQL)
```

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

**Recommended attachment order** (attach 2-4 files):
```
@table_doc_template.md              ← Template (MUST)
@Tables.Courses.sql                 ← Target table (MUST)
@Tables.Enrollments.sql             ← Related table (OPTIONAL)
@vw_CourseEnrollmentSummary.sql     ← View using table (OPTIONAL)
```

---

#### 3A.2: Standard Prompt for VS Code/Visual Studio

Copy the prompt below and paste into Copilot Chat:

```
Generate database table documentation following AKR_CHARTER_DB.md conventions.

Use the table_doc_template.md structure.

**Target table**: [TABLE_NAME - e.g., Courses]

**Include all template sections**:
1. Table identification (schema, object type, last updated)
2. Purpose (what this table stores, business purpose)
3. Columns (all columns with generic types + native types)
4. Constraints (check, unique, foreign keys in plain English)
5. Business Rules (BR-TABLENAME-### format)
6. Related Objects (views, stored procedures, triggers, referenced by)

**Important conventions**:
- Use generic data types (GUID, String, Integer, DateTime, Boolean, Decimal)
- Always note native types: (native: UNIQUEIDENTIFIER), (native: VARCHAR), etc.
- Translate constraints to plain English
- Use BR-TABLENAME-### format for business rules (e.g., BR-COURSES-001)
- Mark all AI-generated content with 🤖
- Mark sections needing human input with ❓
- Focus on WHAT (observable from schema) - mark as 🤖
- Flag WHY questions for human input (business context) - mark as ❓

**Column documentation format**:
- `ColumnName` (GenericType, Required/Nullable, default: value) - Description (native: DBSpecificType)

**Example**:
- `Id` (GUID, Required, default: newsequentialid()) - **Primary Key** (native: UNIQUEIDENTIFIER)
- `Title` (String, max 200, Required) - Name of the training course (native: NVARCHAR)
- `IsActive` (Boolean, Required, default: true) - Indicates whether course is currently offered (native: BIT)

**Constraints documentation**:
- Translate CHECK constraints to plain English
- Explain UNIQUE constraints business purpose
- Document foreign keys showing relationships

**Extract from DDL**:
- All column names, types, nullability, defaults
- Primary key constraint
- Check constraints
- Unique constraints
- Foreign key relationships
- Table-level constraints

**Flag for human review**:
- Magic numbers in check constraints (Why these specific values?)
- Business purpose of unique constraints
- Why foreign keys cascade/restrict/set null
- Purpose statement needs business context

Generate the documentation now.
```

**Customization points** (modify before pasting):
- Replace `[TABLE_NAME]` with actual table name (e.g., `Courses`)
- If table is in non-standard schema, mention schema name

---

### Step 3B: Use GitHub Copilot Spaces (Alternative) (10 minutes)

#### 3B.1: Open Copilot Spaces

**In VS Code:**
1. Open the table DDL file (e.g., `Tables/Courses.sql`)
2. Press `Ctrl+Shift+.` or click Copilot Spaces icon
3. Copilot Spaces panel opens

**GitHub Copilot Spaces has more workspace context automatically**, so you don't need to attach files manually. It can see:
- ✅ All files in your workspace
- ✅ Related tables and views
- ✅ Project structure
- ✅ Existing documentation patterns

---

#### 3B.2: Standard Prompt for GitHub Copilot Spaces

Copy the prompt below and paste into Copilot Spaces:

```
I need to document the [TABLE_NAME] table following our AKR documentation system.

**Context**:
- Template: Use table_doc_template.md from AKR files folder
- Conventions: Follow AKR_CHARTER.md and AKR_CHARTER_DB.md
- Target table: [SCHEMA].[TABLE_NAME] (file: [PATH_TO_DDL])
- Output location: docs/tables/[TableName]_doc.md

**Generate documentation with these sections**:
1. **Table identification**: Schema, object type, last updated (use today's date)
2. **Purpose**: What this table stores and its business purpose (1-3 sentences)
3. **Columns**: All columns using format:
   - `ColumnName` (GenericType, Required/Nullable, default: value) - Description (native: DBSpecificType)
4. **Constraints**: Check, unique, foreign keys translated to plain English
5. **Business Rules**: Using BR-TABLENAME-### format
6. **Related Objects**: Views, stored procedures, triggers that use this table

**Critical conventions to follow**:
✅ Use generic data types: GUID (not UNIQUEIDENTIFIER), String (not VARCHAR), Integer (not INT), Boolean (not BIT), DateTime (not DATETIME), Decimal (not NUMERIC)
✅ Always note native types in parentheses: (native: UNIQUEIDENTIFIER)
✅ Mark primary keys inline: **Primary Key**
✅ Translate CHECK constraints to plain English
✅ Use BR-TABLENAME-### for business rules (e.g., BR-COURSES-001)
✅ Mark AI-generated content with 🤖
✅ Mark sections needing human input with ❓

**What to extract from DDL**:
- Column names, types, nullability, defaults, max lengths
- Primary key constraint
- Check constraints (translate to business meaning)
- Unique constraints (explain why these columns must be unique)
- Foreign keys (show relationships: ColumnName → Schema.Table.Column)

**What to flag for human input**:
- ❓ Business purpose of the table (WHY it exists)
- ❓ Business rationale for constraints (WHY these rules)
- ❓ Why specific default values chosen
- ❓ Meaning of magic numbers in check constraints
- ❓ When business rules were added (Since When column)

**Example column documentation**:
- `Id` (GUID, Required, default: newsequentialid()) - **Primary Key** (native: UNIQUEIDENTIFIER)
- `Title` (String, max 200, Required) - Name of the training course (native: NVARCHAR)
- `IsActive` (Boolean, Required, default: true) - Indicates whether course is currently offered (native: BIT)
- `CreatedAt` (DateTime, Required, default: getutcdate()) - When course was created (native: DATETIME2)

**Example constraint documentation**:
**Check Constraints:**
- `CK_Courses_ValidityMonths`: Validity months must be between 1 and 60
  - Technical expression: `[ValidityMonths] >= 1 AND [ValidityMonths] <= 60`
  - ❓ Why: Business rationale needed

**Example foreign key**:
- `CourseId` → `training.Courses.Id` - Links enrollment to specific course

Generate complete documentation following this structure.
```

**Customization points**:
- Replace `[TABLE_NAME]` with actual table name (e.g., `Courses`)
- Replace `[SCHEMA]` with actual schema (e.g., `training`)
- Replace `[PATH_TO_DDL]` with file path (e.g., `POC_SpecKitProj/training/Tables/Courses.sql`)

---

### Step 4: Review and Correct AI Output (3 minutes)

Check the AI-generated content for common mistakes:

#### Column Documentation

**Check**:
- [ ] All columns from DDL are documented
- [ ] Generic types used (GUID, String, Integer, Boolean, DateTime, Decimal)
- [ ] Native types noted: (native: UNIQUEIDENTIFIER), (native: NVARCHAR), etc.
- [ ] Required vs Nullable is correct
- [ ] Default values match DDL
- [ ] Primary key marked inline: **Primary Key**

**Common AI mistakes**:
```sql
-- DDL:
CREATE TABLE training.Courses (
    Id UNIQUEIDENTIFIER NOT NULL DEFAULT NEWSEQUENTIALID(),
    Title NVARCHAR(200) NOT NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    CONSTRAINT PK_Courses PRIMARY KEY (Id)
);

-- ❌ AI might use native types instead of generic:
- `Id` (UNIQUEIDENTIFIER, Required) - Primary key

-- ❌ AI might forget to note native type:
- `Id` (GUID, Required, default: newsequentialid()) - **Primary Key**

-- ✅ Correct documentation:
- `Id` (GUID, Required, default: newsequentialid()) - **Primary Key** (native: UNIQUEIDENTIFIER)
- `Title` (String, max 200, Required) - Name of the training course (native: NVARCHAR)
- `IsActive` (Boolean, Required, default: true) - Indicates whether course is currently offered (native: BIT)
```

---

#### Constraints

**Check**:
- [ ] All constraints from DDL are documented
- [ ] Constraints translated to plain English
- [ ] Unique constraints explain business purpose
- [ ] Foreign keys show full relationship path

**Common AI mistakes**:
```sql
-- DDL:
CONSTRAINT CK_Courses_ValidityMonths CHECK (ValidityMonths >= 1 AND ValidityMonths <= 60)

-- ❌ AI might just copy SQL:
- `CK_Courses_ValidityMonths`: ValidityMonths >= 1 AND ValidityMonths <= 60

-- ✅ Better documentation:
- `CK_Courses_ValidityMonths`: Validity months must be between 1 and 60
  - Technical expression: `[ValidityMonths] >= 1 AND [ValidityMonths] <= 60`
  - ❓ Why: Business rationale needed (human input)
```

---

#### Business Rules

**Check**:
- [ ] Business rules use BR-TABLENAME-### format
- [ ] Each rule has description
- [ ] "Why It Exists" column marked ❓ (human input needed)
- [ ] "Since When" column marked ❓ (human input needed)

**Example**:
```markdown
| Rule ID | Description | Why It Exists | Since When |
|---------|-------------|---------------|------------|
| 🤖 BR-COURSES-001 | Course title cannot be empty or whitespace | ❓ Human: business rationale | ❓ Human: when added |
| 🤖 BR-COURSES-002 | Validity months between 1-60 | ❓ Human: business rationale | ❓ Human: when added |
```

---

### Step 5: Enhance with Business Context (10 minutes)

Now fill in the ❓ sections that AI can't generate:

#### 5.1 Purpose Enhancement

**AI generated** (technical):
```markdown
## Purpose

🤖 Stores training course information.
```

**You add** (business context):
```markdown
## Purpose

🤖 Stores training course information including course titles, descriptions, and active status.

❓ **Business Context**:
This table is the central repository for all training courses offered to employees. 
Used by the Training Tracker system to:
- Display available courses in the course catalog
- Track which courses are required for compliance
- Manage course prerequisites
- Support enrollment workflows

Historical note: Originally created to support OSHA compliance training requirements 
(2020), expanded to all employee training in 2021.
```

---

#### 5.2 Business Rules Enhancement

**AI generated**:
```markdown
| Rule ID | Description | Why It Exists | Since When |
|---------|-------------|---------------|------------|
| 🤖 BR-COURSES-001 | Course title cannot be empty | ❓ | ❓ |
| 🤖 BR-COURSES-002 | Validity months between 1-60 | ❓ | ❓ |
```

**You enhance**:
```markdown
| Rule ID | Description | Why It Exists | Since When |
|---------|-------------|---------------|------------|
| 🤖 BR-COURSES-001 | Course title cannot be empty or whitespace | ❓ Ensures all courses have meaningful names for catalog display | ❓ Initial release (2020) |
| 🤖 BR-COURSES-002 | Validity months between 1-60 | ❓ Compliance requirement: certifications valid max 5 years, min 1 month for short courses | ❓ Added v2.1 (2021-03) per legal team requirement |
| 🤖 BR-COURSES-003 | Deleted courses soft-deleted (IsActive=false) | ❓ Preserves enrollment history for audit/compliance reporting | ❓ Initial release (2020) |
```

---

#### 5.3 Constraints Enhancement

**AI generated**:
```markdown
**Check Constraints:**
- `CK_Courses_ValidityMonths`: Validity months must be between 1 and 60
  - Technical expression: `[ValidityMonths] >= 1 AND [ValidityMonths] <= 60`
```

**You enhance**:
```markdown
**Check Constraints:**
- `CK_Courses_ValidityMonths`: Validity months must be between 1 and 60
  - Technical expression: `[ValidityMonths] >= 1 AND [ValidityMonths] <= 60`
  - ❓ **Why**: Legal requirement - certifications valid maximum 5 years (60 months) per industry regulations. Minimum 1 month to prevent data entry errors (courses with 0 validity don't make business sense).
  - ❓ **Added**: Version 2.1 (March 2021) after compliance audit identified courses with invalid expiration periods.
```

---

#### 5.4 Related Objects Enhancement

**AI generated**:
```markdown
## Related Objects

- **Views**: 🤖 vw_CourseEnrollmentSummary
- **Stored Procedures**: 🤖 None identified
- **Triggers**: 🤖 None
- **Referenced By**: 🤖 training.Enrollments (CourseId)
```

**You enhance**:
```markdown
## Related Objects

- **Views**: 
  - 🤖 `vw_CourseEnrollmentSummary` - Shows course enrollment statistics for dashboard
  - ❓ `vw_ActiveCourseList` - Public-facing course catalog (only shows IsActive=true)
  
- **Stored Procedures**: 
  - 🤖 None - Using Entity Framework ORM for all CRUD operations
  
- **Triggers**: 
  - 🤖 None
  
- **Referenced By**: 
  - 🤖 `training.Enrollments` (CourseId) - Tracks user enrollments
  - 🤖 `training.CoursePrerequisites` (CourseId, PrerequisiteCourseId) - Defines course sequence
  - ❓ External system: LMS Integration Service reads this table hourly for catalog sync
```

---

### Step 6: Add Optional Sections (If Needed) (5 minutes)

Only add optional sections when you have real information to share:

#### Performance Considerations

Add this section if:
- Table has millions of rows
- Specific indexes recommended
- Known query performance issues

**Example**:
```markdown
### Performance Considerations

❓ **Table volume**: ~500 courses (slow growth, ~50 new courses/year)

❓ **Index recommendations**:
- Existing clustered index on `Id` (PK) is appropriate
- Consider nonclustered index on `IsActive, Title` if course catalog queries slow down
  - Current catalog query averages 45ms, acceptable for now

❓ **Known bottlenecks**: None identified

❓ **Monitoring**: Course catalog page load time tracked in Application Insights
```

---

#### External Integrations

Add this section if:
- External systems read/write this table
- API exposes this data
- ETL processes sync this table

**Example**:
```markdown
### External Integrations

❓ **LMS Integration Service** (external Learning Management System):
- **Access pattern**: Reads this table hourly for course catalog sync
- **Columns read**: Id, Title, Description, IsActive, ValidityMonths
- **Performance impact**: Query runs <5 seconds, acceptable
- **Contact**: LMS Team (lms-support@company.com)

❓ **Compliance Reporting** (quarterly extracts):
- **Access pattern**: Quarterly export for audit reports
- **Columns read**: All columns
- **Process**: PowerBI scheduled refresh
```

---

#### Known Limitations

Add this section if:
- Current design has compromises
- Technical debt exists
- Future refactoring planned

**Example**:
```markdown
### Known Limitations

❓ **Single language support**: Course titles/descriptions in English only
- **Impact**: Cannot support multi-language training materials
- **Workaround**: External translation service for Spanish content
- **Future**: Planned localization table (FN12345_US089, backlog)

❓ **No version history**: Course updates overwrite previous data
- **Impact**: Cannot track historical course content changes
- **Workaround**: Manual backup before major course updates
- **Future**: Course version tracking under consideration
```

---

## Standard Workflow Summary

### For VS Code/Visual Studio Users

```
1. Open Copilot Chat (Ctrl+Shift+I)
2. Attach files: @table_doc_template.md @Tables.Courses.sql
3. Paste standard prompt (see Step 3A.2)
4. Review output (Step 4)
5. Enhance business context (Step 5)
6. Save to docs/tables/Courses_doc.md
7. Create PR with feature tag
```

**Time**: 5 min (AI) + 15 min (human) = 20 minutes

---

### For GitHub Copilot Spaces Users

```
1. Open table DDL file
2. Open Copilot Spaces (Ctrl+Shift+.)
3. Paste standard prompt (see Step 3B.2)
4. Review output (Step 4)
5. Enhance business context (Step 5)
6. Save to docs/tables/Courses_doc.md
7. Create PR with feature tag
```

**Time**: 5 min (AI) + 15 min (human) = 20 minutes

---

## Key Differences: VS Code/Copilot vs GitHub Spaces

| Aspect | VS Code/Visual Studio with Copilot | GitHub Copilot Spaces |
|--------|-------------------------------------|------------------------|
| **Context** | Manual file attachment (@mentions) | Automatic workspace awareness |
| **File limit** | ~5 files (token limit) | Entire workspace accessible |
| **Prompt style** | Explicit file references needed | Can reference by description |
| **Best for** | Focused documentation tasks | Broader context understanding |
| **Setup** | More manual (attach files) | Less setup (workspace aware) |
| **Output quality** | High (if right files attached) | High (better cross-file insights) |

**Recommendation**: 
- **Start with GitHub Spaces** if available (easier, better context)
- **Fall back to VS Code Copilot** if Spaces not available or for simple tables

---

## Common Scenarios

### Scenario 1: Table with Complex Constraints

**Challenge**: Table has many check constraints with business logic

**Solution**:
1. Use standard prompt to extract all constraints
2. Manually translate complex constraints to plain English
3. Add business rationale for each constraint
4. Link to business requirements doc if available

**Example**:
```sql
-- Complex constraint:
CONSTRAINT CK_Courses_Dates CHECK (
    (StartDate IS NULL AND EndDate IS NULL) OR
    (StartDate IS NOT NULL AND EndDate IS NOT NULL AND EndDate >= StartDate)
)

-- Document as:
**Check Constraints:**
- `CK_Courses_Dates`: Start and end dates must both be null OR both be set with end after start
  - Technical expression: `(StartDate IS NULL AND EndDate IS NULL) OR (StartDate IS NOT NULL AND EndDate IS NOT NULL AND EndDate >= StartDate)`
  - ❓ **Why**: Courses can be ongoing (no dates) or scheduled (both dates required). End must be after start to prevent data entry errors.
  - ❓ **Business context**: Introduced after incident where course scheduled to end before it started, causing enrollment errors.
```

---

### Scenario 2: Legacy Table with Poor Naming

**Challenge**: Table has cryptic column names, no comments in DDL

**Solution**:
1. Generate baseline documentation with AI
2. **Critical**: Interview team members who use the table
3. Add detailed column descriptions based on interviews
4. Document discovered business context

**Example**:
```markdown
## Columns

- `Id` (GUID, Required, default: newsequentialid()) - **Primary Key** (native: UNIQUEIDENTIFIER)
- `CrsNm` (String, max 200, Required) - ❓ Course name/title displayed in catalog (legacy column name, should be `Title`) (native: NVARCHAR)
- `CrsCd` (String, max 20, Required) - ❓ Course code for external LMS integration (format: XXX-### where XXX=category, ###=number) (native: VARCHAR)
- `FlgActv` (Boolean, Required, default: true) - ❓ Indicates course is active/published (legacy column name, should be `IsActive`) (native: BIT)

❓ **Naming note**: This table was created in 2015 before naming standards adopted. Column names abbreviated for database size constraints (no longer relevant). Refactoring to standard names planned for v3.0 (FN99999).
```

---

### Scenario 3: Table Used by External Systems

**Challenge**: Table read/written by external integrations

**Solution**:
1. Generate baseline documentation
2. Add "External Integrations" optional section
3. Document access patterns, frequency, impact
4. Include contact information for external system owners

**Example** (see "External Integrations" in Step 6)

---

### Scenario 4: ORM-Generated Table (No DDL)

**Challenge**: Schema created by Entity Framework/Django, no SQL DDL file

**Solution**:
1. **Option A**: Generate DDL from database
   ```sql
   -- SQL Server:
   sp_help 'training.Courses'
   -- Or use SSMS: Right-click table → Script Table as → CREATE To → New Query Window
   ```
   
2. **Option B**: Use entity class as source
   - Attach entity class to Copilot
   - Mention in prompt: "Generate from entity class, not DDL"
   
3. **Option C**: Use migration file
   - Find latest CREATE TABLE migration
   - Attach to Copilot

**Prompt adjustment**:
```
Generate database table documentation from Entity Framework entity class.

Use table_doc_template.md structure.

**Source**: Course.cs entity class (not DDL)

[Rest of standard prompt, but note to extract from C# annotations...]
```

---

## Maintenance Checklist

**When making schema changes to this table:**

- [ ] Update column documentation if columns added/removed/modified
- [ ] Update constraints documentation if constraints changed
- [ ] Update business rules table if validation logic changed
- [ ] Update related objects if new views/procedures created
- [ ] Add to "Known Limitations" if introducing technical debt
- [ ] Update "Purpose" if table scope changed

**Commit message format**:
```bash
git commit -m "docs: update Courses table - add ValidityMonths column (FN12345_US089)"
```

---

## Tips for High-Quality Documentation

### DO:
✅ Use generic data types (GUID, String, Integer, Boolean, DateTime, Decimal)  
✅ Always note native database types: (native: UNIQUEIDENTIFIER)  
✅ Translate constraints to plain English  
✅ Add business context for WHY things exist  
✅ Include feature tags in commit messages  
✅ Keep descriptions concise but meaningful (5-20 words per column)  
✅ Mark AI content with 🤖, human content with ❓  
✅ Add optional sections only when valuable  

### DON'T:
❌ Use native types as primary (UNIQUEIDENTIFIER) - use GUID instead  
❌ Copy SQL syntax without explanation  
❌ Leave business rules "Why It Exists" empty  
❌ Add optional sections with placeholder text  
❌ Skip review of AI-generated content  
❌ Forget to note database-specific features  
❌ Document implementation details better suited for code comments  

---

## Time Estimates

| Table Complexity | AI Generation | Human Enhancement | Total |
|------------------|---------------|-------------------|-------|
| **Simple** (lookup, 3-5 columns) | 3 min | 10 min | **15 min** |
| **Typical** (7-10 columns, constraints) | 5 min | 15 min | **20-25 min** |
| **Complex** (15+ columns, optional sections) | 7 min | 20 min | **30-40 min** |

---

## Getting Help

**Questions about template?**
- Check **AKR_CHARTER.md** for principles
- Check **AKR_CHARTER_DB.md** for database patterns
- Ask Tech Lead or team channel

**AI generated wrong info?**
- Normal - LLMs can hallucinate
- Review and correct
- Focus on structure, you add accuracy

**Not sure about business context?**
- Flag with ❓ in documentation
- Ask team members who use the table
- Check existing business requirements docs
- Add to "Questions & Gaps" section

---

## Template Metadata

**Guide Version**: 1.0  
**Last Updated**: 2025-11-10  
**Maintained By**: Architecture Team  
**Part of**: Application Knowledge Repo (AKR) system

**Related Documentation**:
- AKR_CHARTER.md - Universal conventions
- AKR_CHARTER_DB.md - Database-specific conventions
- table_doc_template.md - The template structure

---

**Pro tip**: The best documentation is documentation that gets maintained. Start lean, add detail when it helps the team, not for completeness.
