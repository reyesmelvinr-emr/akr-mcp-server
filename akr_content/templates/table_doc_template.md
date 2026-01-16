# Table: [TABLE_NAME]

**Schema/Namespace**: [schema]  
**Object Type**: Table  
**Last Updated**: [YYYY-MM-DD]

---

## Purpose

🤖 [AI: Technical description - what data this table stores]

❓ [HUMAN: Business context - why this table exists, what business need it addresses]

---

## Columns

🤖 [AI: List all columns using this format:]
- `ColumnName` (GenericType, Required/Nullable, default: value) - Description (native: DBSpecificType)

**Example:**
- `Id` (GUID, Required, default: newsequentialid()) - **Primary Key** (native: UNIQUEIDENTIFIER)
- `Title` (String, max 200, Required) - Name of the training course (native: NVARCHAR)
- `IsActive` (Boolean, Required, default: true) - Indicates whether course is currently offered (native: BIT)

---

## Constraints

🤖 [AI: Document constraints that enforce business rules. Translate technical expressions to plain English.]

**Check Constraints:**
🤖 [AI: List all check constraints, or "(None)"]
- `ConstraintName`: 🤖 Plain English explanation
  - Technical expression: `[SQL expression]`
  - ❓ **Why**: Business rationale for this constraint

**Unique Constraints:**
🤖 [AI: List all unique constraints, or "(None)"]
- `ConstraintName` on (Column1, Column2): ❓ Why these columns must be unique (business reason)

**Foreign Keys:**
🤖 [AI: List all foreign keys, or "(None)"]
- `ColumnName` → `ReferencedSchema.ReferencedTable.ReferencedColumn` - 🤖 Describe the relationship

---

## Business Rules

🤖 [AI: List key business rules enforced by this table. Use format: BR-TABLENAME-###]

| Rule ID | Description | Why It Exists | Since When |
|---------|-------------|---------------|------------|
| 🤖 BR-[TABLE]-001 | 🤖 AI: Rule description from constraints/schema | ❓ HUMAN: Business rationale | ❓ HUMAN: When added (version, date) |
| 🤖 BR-[TABLE]-002 | 🤖 AI: Rule description from constraints/schema | ❓ HUMAN: Business rationale | ❓ HUMAN: When added (version, date) |

❓ [HUMAN: Add context for non-obvious rules, historical reasons, or recent changes]

---

## Related Objects

🤖 [AI: Document how this table relates to other database objects]

- **Views**: 🤖 [AI: List views that read from this table, or "None known"]
- **Stored Procedures**: 🤖 [AI: List SPs that modify this table, or "None - using ORM"]
- **Triggers**: 🤖 [AI: List triggers, or "None"]
- **Referenced By**: 🤖 [AI: List tables with foreign keys pointing here, or "None identified"]

❓ [HUMAN: Add external system integrations if applicable]

---

## Optional Sections

The sections above provide the minimum documentation for a table. Add additional sections below as your team discovers they're needed.

### External Integrations

❓ [HUMAN: Add this section only if external systems access this table]

**Example format:**
- **System Name**: Access pattern, frequency, impact

### Performance Considerations

❓ [HUMAN: Add this section only if production metrics, bottlenecks, or index recommendations exist]

**Example format:**
- Table volume: X rows
- Index recommendations
- Known bottlenecks

### Data Migration Notes

❓ [HUMAN: Add this section only if ETL, legacy sync, or data transformation exists]

### Known Limitations

❓ [HUMAN: Add this section only if technical debt, design compromises, or current constraints exist]

### Future Considerations

❓ [HUMAN: Add this section only if planned enhancements or refactoring is documented]

### Security & Compliance

❓ [HUMAN: Add this section only if PII, regulatory requirements, or special access controls exist]

---

## Database-Specific Features

🤖 [AI: Auto-detect database-specific features from DDL]

❓ [HUMAN: Document portability implications if migrating to different database]

**Example:**
- **NEWSEQUENTIALID()** - SQL Server specific (alternative: UUID_GENERATE_V1() in PostgreSQL)
- **UNIQUEIDENTIFIER** - SQL Server specific (alternative: UUID in PostgreSQL)

---

## Documentation Standards

### This template follows the Application Knowledge Repo (AKR) system

**For universal conventions, see**:
- **AKR_CHARTER.md** - Core principles, generic data types, feature tags, Git format

**For database-specific conventions, see**:
- **AKR_CHARTER_DB.md** - Database object naming, constraints, patterns

**For step-by-step documentation process, see**:
- **Table_Documentation_Developer_Guide.md** - How to use this template with Copilot/AI

---

## Change History

**Schema evolution is tracked in Git**, not in this document.

To see how this table evolved:
```bash
# View all changes to this documentation file
git log docs/tables/[TABLE_NAME]_doc.md

# View changes with diffs
git log -p docs/tables/[TABLE_NAME]_doc.md

# Search for specific feature
git log --grep="FN#####" docs/tables/[TABLE_NAME]_doc.md
```

**Include feature tags in commit messages**:
```bash
git commit -m "docs: update [TableName] table - add [ColumnName] (FN#####_US#####)"
```

---

## Tags & Metadata

**Tags**: 🤖 #[feature-domain] #[cross-cutting] #table #[priority] #[status]

❓ **Add feature tags** (see TAGGING_STRATEGY_TAXONOMY.md):
- Feature Domain tags (e.g., #enrollment, #course-catalog, #user-profile)
- Cross-Cutting tags (e.g., #audit-logging, #data-validation)
- Technical tag: #table
- Priority tag (e.g., #core-feature, #important, #nice-to-have)
- Status tag (e.g., #deployed, #stable)

**Example**: `#enrollment #audit-logging #table #core-feature #deployed`

**Related Features**:
- 🤖 [Feature documentation that uses this table]
- ❓ [Add links to features in AKR_Main/features/ folder]

**Table Metadata**:
- **Domain**: ❓ [Business domain this table belongs to]
- **Priority**: ❓ [P0: Core | P1: Important | P2: Nice-to-have]
- **User Stories**: ❓ [US#12345, US#12467]
- **Schema Version**: ❓ [Version when table was added]

---

## AI Generation Instructions

**For AI (Copilot/ChatGPT/Claude):**

When generating this documentation:
1. Mark all AI-generated content with 🤖
2. Mark sections needing human input with ❓
3. Extract column names, types, nullability, defaults from DDL
4. Translate constraints to plain English
5. Use generic data types (GUID, String, Integer, Boolean, DateTime, Decimal)
6. Always note native types: (native: UNIQUEIDENTIFIER), (native: NVARCHAR), etc.
7. Use BR-TABLENAME-### format for business rules
8. Flag magic numbers, hardcoded values, unclear logic
9. Focus on WHAT (observable from schema) - mark as 🤖
10. Flag WHY questions for human input (business context) - mark as ❓

**For Humans:**

After AI generates baseline:
1. Add business context to Purpose section (3 min)
2. Complete business rules "Why It Exists" and "Since When" columns (5 min)
3. Add constraint business rationale (3 min)
4. Add external integrations if applicable (2 min)
5. Review column descriptions for accuracy (2 min)
6. Add optional sections only if valuable (5 min)

**Total Time:** 15-25 minutes

**See Table_Documentation_Developer_Guide.md for complete workflow and standard prompts.**

---

## Template Metadata

**Template Version**: 3.0 (Separated from Developer Guide)  
**Last Updated**: 2025-11-10  
**Maintained By**: Architecture Team  
**Part of**: Application Knowledge Repo (AKR) system

**Related Files**:
- **Table_Documentation_Developer_Guide.md** - How to use this template
- **AKR_CHARTER.md** - Universal conventions
- **AKR_CHARTER_DB.md** - Database-specific conventions
