# Application Knowledge Repo (AKR) Charter

**Version**: 1.0  
**Last Updated**: 2025-10-22  
**Authority**: System-wide (applies to all teams and projects)  
**Maintained By**: Architecture Team / Tech Leads

---

## Purpose

The **Application Knowledge Repo (AKR)** is our system for capturing, organizing, and maintaining knowledge about our applications. This Charter defines the universal principles, conventions, and standards that apply across all documentation types and all teams.

**What the AKR provides**:
- Shared understanding of system architecture and behavior
- Context for new developers joining the team
- Historical record of decisions and evolution (via Git)
- Foundation for cross-team consistency

**What the AKR is NOT**:
- A compliance checkbox exercise
- Exhaustive documentation of every detail
- A replacement for code comments or API docs
- Static documentation that never changes

---

## Core Principles

### 1. Lean by Default

**Principle**: Start with minimal documentation, add detail as knowledge accumulates.

**Why**: Upfront comprehensive documentation is often speculative and becomes outdated. Better to document what we know now and expand as we learn.

**Practice**:
- Essential sections only at creation (what, why, how)
- Add optional sections when real experience reveals they're valuable
- Don't document "future plans" - document current reality
- Avoid placeholder text like "TBD" or "To be determined"

**Example**:
```
Day 1: Document table structure, purpose, basic constraints
Month 3: Add "Known Limitations" after production issues discovered
Month 6: Add "External Integrations" section after mobile app integration
```

---

### 2. Flexible to Context

**Principle**: Templates are starting points, not rigid contracts. Customize to reality.

**Why**: Different tables/components have different complexity. A lookup table needs less documentation than a business-critical transactional table.

**Practice**:
- Required sections: minimum viable documentation
- Recommended sections: include if applicable
- Optional sections: add when they provide value
- Custom sections: encouraged when context demands it

**Example**:
```
Simple lookup table: 50 lines (minimal)
Complex business table: 250 lines (comprehensive, custom sections)
Both are acceptable if they serve their purpose
```

---

### 3. Evolutionary

**Principle**: Documentation grows as knowledge and systems evolve.

**Why**: We don't know everything on Day 1. Production teaches us limitations, integrations emerge, requirements change.

**Practice**:
- Update docs when schema changes
- Add sections when new context emerges
- Don't force completeness upfront
- Git history shows evolution (don't duplicate in docs)

**Example**:
```
Initial: Basic table documentation
+ 3 months: Add performance notes (learned from production)
+ 6 months: Add external integration notes (new mobile app)
+ 1 year: Add migration notes (preparing for refactoring)
```

---

### 4. Tool-Assisted, Human-Verified

**Principle**: Use automation (LLMs, scripts) to accelerate, but humans verify accuracy.

**Why**: Tools can generate structure and infer context, but can't know business rules or make judgment calls.

**Practice**:
- LLMs generate first drafts (60-70% complete)
- Python scripts ensure consistent structure
- Developers add business context tools can't infer
- Tech Leads review for accuracy and value
- Human judgment is final quality gate

**Example**:
```
1. LLM generates doc from DDL (structure, inferred descriptions)
2. Developer adds: business context, external integrations, limitations
3. Tech Lead reviews: Is this useful? Is this accurate?
4. Approved → Merge
```

---

### 5. Git-Integrated

**Principle**: Git is the authoritative source for history and versioning.

**Why**: Git provides better tooling for history than embedded changelogs. Don't duplicate what Git does well.

**Practice**:
- Git commits show what changed and when
- Feature tags in commit messages link to work items
- Git blame shows who wrote each section
- Git diff shows evolution between versions
- Documentation files do NOT include "Change History" sections

**Example**:
```
Git commit: "docs: add Courses external integration note (FN99999_US145)"
Git log: Shows all changes to file over time
Git blame: Shows who documented each section
```

---

## Universal Conventions

### Generic Data Types

All AKR documentation uses **generic data types** with native types noted when different.

**Purpose**: 
- Portability (easier to migrate to different databases)
- Clarity (generic types are self-explanatory)
- Consistency (same vocabulary across all docs)

**Format**: `GenericType (native: DatabaseSpecificType)`

**Mapping Table**:

| Generic Type | SQL Server | PostgreSQL | MySQL | Notes |
|--------------|-----------|------------|-------|-------|
| **GUID** | UNIQUEIDENTIFIER | UUID | CHAR(36) | Always note native type |
| **String** | VARCHAR/NVARCHAR | VARCHAR/TEXT | VARCHAR | Note max length if limited |
| **Integer** | INT/BIGINT | INTEGER/BIGINT | INT/BIGINT | Note size (INT, BIGINT) if relevant |
| **Boolean** | BIT | BOOLEAN | TINYINT(1) | Always note native type |
| **DateTime** | DATETIME/DATETIME2 | TIMESTAMP | DATETIME | Note precision if relevant |
| **Decimal** | DECIMAL/NUMERIC | NUMERIC | DECIMAL | Always note precision and scale |
| **Binary** | VARBINARY | BYTEA | BLOB | Note max length |

**Examples**:
```markdown
✅ Good:
- `Id` (GUID, Required) - Primary key (native: UNIQUEIDENTIFIER)
- `IsActive` (Boolean, Required) - Status flag (native: BIT)
- `Amount` (Decimal(18,2), Required) - Transaction amount (native: DECIMAL)

❌ Bad:
- `Id` (UNIQUEIDENTIFIER, Required) - Primary key
- `IsActive` (BIT, Required) - Status flag
```

**Rationale**: If we migrate from SQL Server to PostgreSQL, generic types make search/replace easier.

---

### Feature Tag Convention

**Format**: `FN#####_US#####`

**Components**:
- `FN#####` = Feature number from Azure Boards
- `US#####` = User Story number

**Purpose**: Links documentation changes to work items for traceability.

**Usage in Git Commits**:
```bash
Format: docs: [action] [object] - [description] (FN#####_US#####) #tag1 #tag2

Examples:
git commit -m "docs: add Courses table documentation (FN99999_US002) #course-catalog #course-management"
git commit -m "docs: update Users table - add external integration (FN99999_US145) #user-profile #authentication"
git commit -m "docs: clarify Enrollments.Status values (FN99999_US089) #enrollment #enrollment-validation"
```

**Usage in Documentation** (optional):
```markdown
## Notes
This table was created as part of FN99999_US002 to support employee training tracking.
```

**Flexibility**: 
- Teams can extend to task level if needed: `FN#####_US#####_T###`
- Format may evolve based on team needs
- Consistency within project > perfect convention

---

### Documentation Tagging Strategy

**Format**: `#tag-name` (hashtag prefix, kebab-case)

**Purpose**: Enable automated documentation consolidation and discovery

**Why Tags Matter**:
- ✅ **Automated Consolidation**: Link technical docs to feature docs automatically
- ✅ **Cross-Cutting Discovery**: Find all components using authentication, audit logging, etc.
- ✅ **Impact Analysis**: Identify which features are affected by changes
- ✅ **Bidirectional Linking**: Component ↔ Features (searchable, queryable)

**Tag Categories**:

1. **Feature Domain Tags** - Which business feature this component supports
   - Examples: `#user-profile` `#course-enrollment` `#prerequisite-validation`
   
2. **Cross-Cutting Concern Tags** - System-wide capabilities this component implements
   - Examples: `#authentication` `#audit-logging` `#caching` `#error-handling`
   
3. **Technical Component Tags** - Technical layer or type
   - Examples: `#table` `#service` `#ui-component` `#endpoint`
   
4. **Priority Tags** - Business criticality
   - Examples: `#core-feature` `#important` `#nice-to-have`

**Tag Placement**:
```markdown
## Metadata

**Component Type**: Table  
**Repository**: training-tracker-database  
**File Path**: `schema/tables/Users.sql`  
**Last Updated**: 2025-11-12  
**Tags**: #user-profile #authentication #audit-logging #table #core-feature
```

**Tag Usage in Commits**:
```bash
# Commit message includes both feature tag AND hashtags
git commit -m "docs: add Country column to Users table (FN12345_US123) #country-access #schema-change #user-profile"

# Multiple related commits with consistent tags
git commit -m "docs: update EnrollmentService with Country validation (FN12345_US123) #country-access #enrollment-validation"
git commit -m "docs: add Country filter to CourseCard component (FN12345_US123) #country-access #ui-component"
```

**Benefits**:

| Use Case | Without Tags | With Tags |
|----------|--------------|-----------|
| Find all auth components | Manual search, ask tech lead | `grep -r "#authentication" docs/` |
| Identify affected features | Read every feature doc | Query by tag (automated) |
| Consolidation time | 30-60 min manual review | 5 min automated analysis |
| Audit compliance | Manual audit trail | Query all `#data-privacy` components |

**Complete Tag Taxonomy**: See [TAGGING_STRATEGY_TAXONOMY.md](../AKR%20files/TAGGING_STRATEGY_TAXONOMY.md)

**Implementation Guide**: See [TAGGING_STRATEGY_IMPLEMENTATION.md](../AKR%20files/TAGGING_STRATEGY_IMPLEMENTATION.md)

**Tagging is REQUIRED for**:
- All technical documentation (database, API, UI)
- All feature documentation
- All Git commits that modify documentation

**Tagging Principles**:
- ✅ Use 3-8 tags per component (be selective, not exhaustive)
- ✅ Use kebab-case format (`#country-based-access` not `#CountryBasedAccess`)
- ✅ Prefer existing taxonomy tags (consistency > creativity)
- ✅ Add new tags to taxonomy when justified
- ❌ Don't create redundant tags (`#user` vs `#users` - pick one)
- ❌ Don't tag with obvious info already in metadata (`#database` when Component Type = Table)

---

### File Naming Conventions

**Format**: `[ObjectName]_doc.md`

**Examples**:
- Tables: `Courses_doc.md`, `Users_doc.md`
- Views: `vw_ActiveCourses_doc.md`
- Stored Procedures: `usp_GetUserCourses_doc.md`
- Domain Docs: `authentication_domain.md`, `user-management_domain.md`

**Rules**:
- Use PascalCase for object names (matches code/schema)
- Suffix with `_doc.md` to distinguish from other files
- No spaces in filenames (use underscores or hyphens)
- Lowercase for domain docs (filesystem friendly)

**Directory Structure**:
```
docs/
├── tables/
│   ├── Courses_doc.md
│   ├── Users_doc.md
│   └── Enrollments_doc.md
├── views/
│   └── vw_ActiveCourses_doc.md
├── stored-procedures/
│   └── usp_GetUserCourses_doc.md
└── domains/
    ├── authentication_domain.md
    └── user-management_domain.md
```

---

### Git Commit Message Format

**Standard Format**:
```
docs: [action] [object] - [description] (FN#####_US#####)
```

**Actions**:
- `add` - Creating new documentation
- `update` - Modifying existing documentation
- `clarify` - Improving clarity without adding new info
- `fix` - Correcting errors
- `remove` - Deleting deprecated documentation

**Examples**:
```bash
docs: add Courses table documentation (FN99999_US002)
docs: update Users table - add OAuth integration notes (FN99999_US124)
docs: clarify Enrollments.Status enum values (FN99999_US089)
docs: fix typo in Courses.Category description
docs: remove deprecated Payment table documentation
```

**Commit Body** (optional but recommended):
```bash
git commit -m "docs: update Courses - add external integration (FN99999_US145)" -m "
Mobile app now queries Courses table directly for catalog display.
Added External Integrations section with performance notes.
"
```

---

### Change History: NOT Included in Docs

**Principle**: Git is the authoritative source for change history.

**Applies to**: All documentation types (tables, views, stored procedures, domains)

**Rationale**:
- Git commit messages contain: what changed, when, who, why
- Git log provides complete timeline
- Git blame shows line-by-line evolution
- Git tags mark significant milestones
- Embedding history in docs creates redundancy and maintenance burden

**To view change history**:
```bash
# View all changes to a documentation file
git log docs/tables/Courses_doc.md

# View changes with diffs
git log -p docs/tables/Courses_doc.md

# Search for specific feature
git log --grep="FN99999_US089" docs/tables/Courses_doc.md

# See what changed between versions
git diff v1.0..v2.0 docs/tables/Courses_doc.md

# Find when a specific line was added
git blame docs/tables/Courses_doc.md
```

**Exception**: Domain documentation MAY include high-level milestones if it helps business understanding:
```markdown
## Evolution Milestones
- **2025-10**: Initial authentication system (password only)
- **2025-11**: Added OAuth 2.0 support (Google, Microsoft)
- **2026-01**: Added MFA support (authenticator apps)
```

---

## Tool Integration

### LLM Generation (Copilot, Claude, ChatGPT)

**Standard Prompt Prefix**:
```
Follow the principles in AKR_CHARTER.md and use template at [specific_template.md].

Key requirements from AKR Charter:
- Use generic data types (see AKR_CHARTER.md for mappings)
- Be concise (explain what and why, not implementation details)
- Start lean, mark sections for human enhancement
- Follow feature tag convention: FN#####_US#####
- Do not create "Change History" section (Git is source of truth)
```

**Content Guidelines**:
- **Purpose**: 1-3 sentences explaining what and why
- **Descriptions**: 5-20 words per item (clear but concise)
- **Business rules**: Use BR-OBJECTNAME-### format
- **Mark uncertainty**: Use `[verify: ...]` for uncertain items
- **Avoid speculation**: Don't document future plans, document current reality

**LLM Output Expectations**:
- 60-70% complete documentation (structure + inferred content)
- Requires human enhancement (business context, custom sections)
- Accuracy verification needed (LLMs can hallucinate)
- First draft quality (not final)

**Developer Responsibilities**:
- Review LLM output for accuracy
- Add business context LLM can't know
- Add custom sections as needed
- Verify technical details
- Remove AI-generated placeholder text

---

### Python Script Integration

**Scripts should**:
- Read AKR_CHARTER.md for generic type mappings
- Apply AKR conventions (feature tags, file naming)
- Generate AKR-compliant structure (no Change History sections)
- Reference technology-specific charters (AKR_CHARTER_DB.md, etc.)
- Produce clean first drafts requiring human enhancement

**Script Output Expectations**:
- Consistent structure across all generated docs
- Generic types with native types noted
- Database-specific features identified
- Placeholder text clearly marked for human input
- No speculative content

---

## Common Patterns Across Documentation Types

### Business Rules Format

**Format**: `- BR-OBJECTNAME-###: Rule description`

**Purpose**: 
- Consistent numbering makes rules easier to reference
- Links documentation to code/validation logic
- Enables traceability in discussions and code reviews

**Examples**:
```markdown
## Business Rules
- BR-COURSES-001: Course title cannot be empty or whitespace only
- BR-COURSES-002: Each course has a unique identifier (GUID)
- BR-COURSES-003: Courses default to optional (IsRequired = false)
```

**Applies to**: Tables, Views, Domain documentation, API endpoints

**Numbering**:
- Start at 001 for each object
- Sequential numbering (001, 002, 003...)
- Gaps are acceptable (if rule 002 deleted, don't renumber)

---

### Database-Specific Features Section

**Format**:
```markdown
## Database-Specific Features

This [object] uses the following database-specific features:
- **FeatureName** - Description and portability implications

⚠️ **Portability Note**: If migrating to a different database system, 
these features will need alternative implementations.
```

**Examples**:
```markdown
## Database-Specific Features

- **NEWSEQUENTIALID()** - SQL Server specific sequential GUID function 
  (Alternative: UUID_GENERATE_V1() in PostgreSQL)
- **UNIQUEIDENTIFIER** - SQL Server specific GUID data type 
  (Alternative: UUID in PostgreSQL)
- **CLUSTERED INDEX** - SQL Server specific index type 
  (Alternative: Standard indexes in PostgreSQL)
```

**Applies to**: Tables, Views, Stored Procedures, Functions

**Purpose**: 
- Highlights portability concerns
- Aids migration planning
- Documents technical dependencies

---

### Optional Sections: Add When Valuable

**Philosophy**: Don't force sections that provide no value.

**Common optional sections**:
- **External Integrations** - When other systems access this object
- **Performance Considerations** - When production revealed bottlenecks
- **Known Limitations** - When technical debt exists
- **Future Considerations** - When refactoring is planned
- **Security Notes** - When special security requirements exist
- **Compliance Notes** - When regulatory requirements apply

**Add these sections**:
- ✅ When you have real information to share
- ✅ When it helps the team understand context
- ✅ When it prevents future confusion

**Don't add these sections**:
- ❌ On Day 1 with placeholder text
- ❌ Just because template suggests it
- ❌ With speculative/future content

---

## Documentation Tiers

### Tier 1: Essential (Always Required)

**What**: Minimum viable documentation

**Sections**:
- Object identification (name, schema/namespace, type)
- Purpose (what and why - 1-3 sentences)
- Structure (columns, properties, endpoints - depends on object type)

**Why**: Without these, documentation provides no value.

**Enforcement**: Validation scripts may error if missing.

---

### Tier 2: Recommended (Include When Applicable)

**What**: Sections that add significant value for most objects

**Sections**:
- Constraints (for tables)
- Business rules (when rules exist)
- Related objects (dependencies, relationships)
- Parameters (for procedures/functions)
- Error handling (for APIs)

**Why**: Most objects have these, documenting them helps developers.

**Enforcement**: Validation scripts may warn if missing.

---

### Tier 3: Optional (Add as Needed)

**What**: Context-specific sections that vary by object complexity

**Sections**:
- External integrations
- Performance considerations
- Known limitations
- Future considerations
- Security/compliance notes
- Data migration notes
- Custom sections

**Why**: Varies by table/component complexity and production experience.

**Enforcement**: Never enforced. Always allowed.

---

## Team Customization

### Relationship: AKR Charter vs. Team Standards

**AKR Charter** (this document):
- **Scope**: System-wide (all teams)
- **Authority**: Architecture/Tech Lead approval required
- **Change frequency**: Rare (quarterly or less)
- **Content**: Principles, universal conventions, shared patterns
- **Cannot be overridden**: Teams must follow Charter

**Team Standards** (OUR_STANDARDS.md in each project):
- **Scope**: Team-specific (single team/project)
- **Authority**: Team Lead approval sufficient
- **Change frequency**: Frequent (weekly/monthly as needed)
- **Content**: Required sections, team formats, validation rules
- **Can extend Charter**: Teams can be stricter, but can't contradict

**Example**:
```
AKR Charter says: "Use generic data types"
Team A: "Generic types required, native types optional to note"
Team B: "Generic types required, native types required - validation checks"

Both teams follow Charter (use generic types), but customize enforcement.
```

---

### What Teams Can Customize

**Teams CAN**:
- ✅ Reclassify sections (Optional → Recommended → Required)
- ✅ Add team-specific format requirements
- ✅ Define validation rules
- ✅ Add team-specific conventions
- ✅ Set stricter standards than Charter

**Teams CANNOT**:
- ❌ Contradict Charter principles
- ❌ Use database-specific types as primary (must use generic)
- ❌ Ignore feature tag convention
- ❌ Override file naming conventions
- ❌ Create "Change History" sections in docs

**Example Team Customization**:
```markdown
# OUR_STANDARDS.md

## Our Team's Extensions to AKR Charter

### Required Sections (for us)
- All sections in Tier 1 (Essential) - per AKR Charter
- Business Rules - REQUIRED for all tables (elevated from Recommended)
- External Integrations - REQUIRED for externally-accessed tables

### Team-Specific Formats
- Business rules must include rationale: BR-XXX-###: Rule (Rationale: ...)
- External integrations must note SLA implications
```

---

## Governance

### How the Charter Evolves

**Process**:
1. Developer/Team proposes change (PR to AKR_CHARTER.md)
2. Cross-team discussion (not just one team affected)
3. Architecture/Tech Lead approval required
4. Technology-specific charters updated to align (if applicable)
5. Teams update their OUR_STANDARDS.md if affected
6. Documentation communicated to all teams

**When to update Charter**:
- ✅ New documentation type added (need shared conventions)
- ✅ Cross-template inconsistency discovered
- ✅ Common instruction duplicated across docs
- ✅ System-wide principle needs refinement

**When NOT to update Charter**:
- ❌ Team-specific need (goes in team's OUR_STANDARDS.md)
- ❌ Template-specific detail (goes in specific template)
- ❌ Personal preference without broad impact
- ❌ Temporary experiment (try in team first, generalize if successful)

---

### Authority Hierarchy

```
AKR_CHARTER.md (System-wide)
    ↓ Applies to
    ├─ AKR_CHARTER_DB.md (Database-specific)
    ├─ AKR_CHARTER_UI.md (UI-specific)
    └─ AKR_CHARTER_API.md (API-specific)
        ↓ Used by
        Templates (table_doc_template.md, view_doc_template.md, etc.)
            ↓ Customized by
            OUR_STANDARDS.md (Team-specific)
                ↓ Used by
                Individual Developers
```

**Conflict Resolution**:
- Charter > Team Standards (if conflict, Charter wins)
- Team Standards > Individual preference
- Technology-specific Charter > Template (if conflict, Charter wins)

---

### Charter Version History

**Version 1.0** (2025-10-22): Initial Charter
- Established five core principles
- Defined universal conventions (types, tags, Git format)
- Set documentation tiers (Essential/Recommended/Optional)
- Clarified governance model

---

## Technology-Specific Charters

**The AKR system includes technology-specific charters** that extend this universal Charter with conventions specific to databases, UIs, APIs, etc.

**Current charters**:
- **AKR_CHARTER_DB.md** - Database-specific conventions

**Future charters** (when needed):
- **AKR_CHARTER_UI.md** - UI component documentation
- **AKR_CHARTER_API.md** - API endpoint documentation

**These charters**:
- Reference and build upon this universal Charter
- Add technology-specific conventions
- Must not contradict universal Charter
- Maintained alongside universal Charter

---

## Quick Reference

### For Developers

**When creating new documentation**:
1. Use appropriate template (table_doc_template.md, etc.)
2. Follow AKR Charter conventions (generic types, feature tags)
3. Check technology-specific charter (AKR_CHARTER_DB.md, etc.)
4. Check team standards (OUR_STANDARDS.md if exists)
5. Use tools to assist (LLM or Python script)
6. Review and enhance tool output
7. Submit PR with feature tag in commit message

**When updating existing documentation**:
1. Keep structure consistent with template
2. Add sections as needed (don't remove valuable content)
3. Update "Last Updated" date
4. Use feature tag in commit message
5. Review for accuracy

**When reviewing documentation PRs**:
1. Is this useful? (most important question)
2. Is this accurate?
3. Does it follow AKR Charter conventions?
4. Are custom sections justified?
5. Approve if yes to all

---

## Questions & Support

**Questions about Charter interpretation?**
- Ask Architecture/Tech Lead team
- Reference technology-specific charters
- Check team standards for team-specific guidance

**Proposing Charter changes?**
- Open PR with rationale
- Tag Architecture/Tech Leads for review
- Expect cross-team discussion

**Need help with documentation?**
- Check templates for structure
- Check quick reference guides for workflow
- Ask team members for examples

---

**Remember**: The goal is useful documentation that helps the team, not perfect documentation that becomes a burden. When in doubt, prioritize value over compliance.

---

**AKR Charter - End of Document**
