# [Application Name] - Database Documentation

**Documentation Type**: Embedded Database (No Dedicated DB Project)  
**Repository**: [backend-api / monorepo / standalone]  
**Database Platform**: [SQL Server / PostgreSQL / MySQL / MongoDB / etc.]  
**Schema Name**: [dbo / public / custom]  
**Last Updated**: [YYYY-MM-DD]  
**Tags**: #database #embedded-schema #[app-name] [feature-tags]

---

## Overview

### Database Summary

| Attribute | Value |
|-----------|-------|
| **Total Object Count** | 🤖 [X tables, Y views, Z stored procedures] |
| **Active Objects (Tier 1)** | 🤖 [Count] - Modified in last 12 months |
| **Stable Objects (Tier 2)** | 🤖 [Count] - Unchanged 1-3 years, still in use |
| **Legacy Objects (Tier 3)** | 🤖 [Count] - Unchanged 3+ years, unknown usage |
| **Management Style** | Manual script execution |
| **Script Storage** | [See Script Repository section] |
| **Primary Owner** | ❓ [@team-member or Team Name] |
| **Change Frequency** | ❓ [Rare / Occasional / Frequent] |

### Why No Dedicated DB Project?

❓ *Select or describe the reason:*
- [ ] Small number of objects (< 20 tables)
- [ ] Team prefers manual control over automated deployments
- [ ] Legacy application with stable schema
- [ ] Database shared across multiple applications
- [ ] Historical: team never set up DB project
- [ ] Other: _______________

### Documentation Tiering Approach

> This database uses **tiered documentation** based on object activity level.

| Tier | Criteria | Documentation Level | Location |
|------|----------|---------------------|----------|
| **Tier 1: Active** | Modified in last 12 months OR used by active features | Full individual docs | `docs/database/active/` |
| **Tier 2: Stable** | No changes 1-3 years, still in use | Summary in this file | Inventory section below |
| **Tier 3: Legacy** | No changes 3+ years, unknown usage | Minimal tracking | `LEGACY_INVENTORY.md` |

---

## Script Repository

> **Important:** Even without a DB project, scripts should be stored in version control.

### Script Location

| Location Type | Path/URL |
|---------------|----------|
| **Primary (Recommended)** | `[repo]/database/scripts/` |
| **Current Location** | ❓ *Where are scripts stored today?* |
| **Backup Location** | ❓ *Where are backup scripts stored?* |

### Recommended Script Organization

> **Key Principle:** The folder structure is **ALWAYS THE SAME** regardless of database size (5 objects or 100+ objects). Only the **documentation depth** changes based on the tier classification.

```
[your-backend-repo]/
├── src/
│   └── Services/
├── database/                    ← ADD THIS FOLDER (same structure for all)
│   ├── scripts/
│   │   ├── tables/              ← All table scripts (any tier)
│   │   │   ├── Users.sql
│   │   │   ├── Orders.sql
│   │   │   └── OldLegacyTable.sql
│   │   ├── views/               ← All view scripts
│   │   ├── stored-procedures/   ← All stored procedure scripts
│   │   ├── functions/           ← All function scripts
│   │   └── seed-data/           ← Reference/lookup data
│   └── migrations/              ← Optional: if using migration approach
│       ├── V001__initial_schema.sql
│       └── V002__add_audit_columns.sql
├── docs/
│   └── database/
│       ├── DATABASE.md          ← This file (main inventory)
│       ├── tables/              ← Individual docs for Tier 1 objects
│       │   ├── Users.md
│       │   └── Orders.md
│       ├── stored-procedures/   ← Procedure docs (Tier 1 only)
│       └── LEGACY_INVENTORY.md  ← Tier 3 tracking list
└── README.md
```

> **What Scales:** 
> - **Small database (5-15 objects)**: Same structure, most objects get individual docs
> - **Medium database (15-50 objects)**: Same structure, only Tier 1 gets individual docs
> - **Large database (50+ objects)**: Same structure, Tier 1 individual docs, Tier 2/3 summary in DATABASE.md

---

## Tier 1: Active Objects (Full Documentation)

> Objects modified in the last 12 months or actively used by current features.
> Create individual documentation files in `docs/database/tables/` (or relevant object folder) using `table_doc_template.md`.

### Active Tables

| Table Name | Purpose | Last Modified | Doc Link | Tags |
|------------|---------|---------------|----------|------|
| 🤖 Users | 🤖 User account information | 🤖 2025-10 | [Users.md](tables/Users.md) | #users #authentication |
| 🤖 Orders | 🤖 Customer orders | 🤖 2025-11 | [Orders.md](tables/Orders.md) | #orders #transactions |
| ❓ | ❓ | ❓ | ❓ | ❓ |

### Active Views

| View Name | Purpose | Last Modified | Doc Link | Tags |
|-----------|---------|---------------|----------|------|
| 🤖 | 🤖 | 🤖 | 🤖 | #active |
| ❓ | ❓ | ❓ | ❓ | ❓ |

### Active Stored Procedures

| Procedure Name | Purpose | Last Modified | Doc Link | Tags |
|----------------|---------|---------------|----------|------|
| 🤖 | 🤖 | 🤖 | 🤖 | #active |
| ❓ | ❓ | ❓ | ❓ | ❓ |

### Active Functions

| Function Name | Purpose | Return Type | Last Modified | Tags |
|---------------|---------|-------------|---------------|------|
| 🤖 | 🤖 | 🤖 | 🤖 | #active |
| ❓ | ❓ | ❓ | ❓ | ❓ |

---

## Tier 2: Stable Objects (Summary Only)

> Objects unchanged 1-3 years but still referenced by active code.
> Documented here in summary format, not as individual files.

### Stable Tables

| Table Name | Purpose | Last Modified | Used By | Row Estimate | Tags |
|------------|---------|---------------|---------|--------------|------|
| 🤖 AuditLog | System audit trail | 2023-05 | Logging framework | ~500K | #audit #stable |
| 🤖 LookupCountry | Country reference data | 2022-01 | Multiple services | ~200 | #reference #stable |
| 🤖 ConfigSettings | App configuration | 2024-02 | Startup | ~50 | #config #stable |
| ❓ | ❓ | ❓ | ❓ | ❓ | ❓ |

### Stable Views

| View Name | Purpose | Base Tables | Last Modified | Tags |
|-----------|---------|-------------|---------------|------|
| 🤖 vw_ActiveUsers | Active user filtering | Users | 2023-08 | #users #stable |
| ❓ | ❓ | ❓ | ❓ | ❓ |

### Stable Stored Procedures

| Procedure Name | Purpose | Called By | Last Modified | Tags |
|----------------|---------|-----------|---------------|------|
| 🤖 sp_GetLookupData | Generic lookup retrieval | UI dropdowns | 2022-06 | #reference #stable |
| ❓ | ❓ | ❓ | ❓ | ❓ |

---

## Tier 3: Legacy Objects

> Objects unchanged 3+ years with unknown or obsolete usage.
> See [LEGACY_INVENTORY.md](LEGACY_INVENTORY.md) for full tracking and investigation status.

### Summary

| Status | Count | Action |
|--------|-------|--------|
| 🔴 Confirmed obsolete | ❓ | Candidate for removal |
| 🟡 Unknown usage | ❓ | Needs investigation |
| 🟢 Keep for compatibility | ❓ | Document dependency reason |

**Total Legacy Objects:** ❓ [Count]

---

## Change Management Process

### How Database Changes Are Made

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  1. Developer   │────►│  2. Review      │────►│  3. Execute     │
│  creates script │     │  (PR/Teams)     │     │  on target DB   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │  5. Update      │◄────│  4. Verify      │
                        │  documentation  │     │  changes        │
                        └─────────────────┘     └─────────────────┘
```

### Change Request Process

| Step | Action | Responsible | Artifact |
|------|--------|-------------|----------|
| 1 | Create SQL script | Developer | Save in `database/scripts/` folder |
| 2 | Peer review | ❓ *Who reviews?* | PR or Teams review |
| 3 | Test in Dev | Developer | Test results (manual/automated) |
| 4 | Execute in QA | ❓ *Who?* | ❓ *How tracked?* |
| 5 | Execute in Prod | ❓ *Who?* | ❓ *How tracked?* |
| 6 | Update docs | Developer | Update this file + object doc |

### Script Naming Convention

```
[Priority]_[ObjectType]_[ObjectName]_[Action].sql

Examples:
001_Table_Users_Create.sql
002_Table_Orders_Create.sql
003_View_vw_ActiveUsers_Create.sql
010_Table_Users_AddEmailColumn.sql
```

### Environment Details

| Environment | Server | Database | Access |
|-------------|--------|----------|--------|
| Development | ❓ | ❓ | Developers |
| QA/Test | ❓ | ❓ | QA Team |
| Staging | ❓ | ❓ | ❓ |
| Production | ❓ | ❓ | ❓ *Restricted to...* |

---

## Connection & Integration

### Services That Use This Database

| Service/Application | Connection Type | Tables Used | Access Level |
|---------------------|-----------------|-------------|--------------|
| 🤖 [ServiceName] | Entity Framework / Dapper / ADO.NET | ❓ | Read/Write |
| ❓ | ❓ | ❓ | ❓ |

### Connection String Configuration

| Environment | Config Location | Secret Management |
|-------------|-----------------|-------------------|
| Development | appsettings.Development.json | Plain text (local only) |
| QA | ❓ | ❓ |
| Production | ❓ Azure Key Vault? | ❓ *Key name* |

### External System Integrations

❓ *Does any external system access this database directly?*

| System | Access Type | Tables Accessed | Frequency |
|--------|-------------|-----------------|-----------|
| ❓ | ❓ | ❓ | ❓ |

---

## Backup & Recovery

### Backup Strategy

| Attribute | Value |
|-----------|-------|
| **Backup Type** | ❓ *Full / Differential / Transaction Log* |
| **Frequency** | ❓ *Daily / Weekly / etc.* |
| **Retention** | ❓ *X days* |
| **Storage Location** | ❓ *Where stored?* |
| **Owner** | ❓ *DBA / Ops / Cloud provider* |

### Recovery Procedures

❓ *Document or link to recovery procedures:*

1. **Point-in-time recovery:** _______________
2. **Full restore from backup:** _______________
3. **Emergency contact:** _______________

---

## Security & Compliance

### Access Control

| Role | Access Level | Members/Groups |
|------|--------------|----------------|
| Read-only | SELECT | ❓ |
| Application | CRUD | [Service Account Name] |
| Admin | Full | ❓ |

### Sensitive Data Inventory

| Table.Column | Data Type | Classification | Protection |
|--------------|-----------|----------------|------------|
| ❓ Users.Email | PII | Personal | ❓ *Encrypted / Masked / etc.* |
| ❓ Users.PasswordHash | Credential | Sensitive | Hashed (bcrypt) |
| ❓ | ❓ | ❓ | ❓ |

### Compliance Requirements

❓ *Does this database fall under any regulatory requirements?*
- [ ] GDPR (right to deletion, data portability)
- [ ] HIPAA (healthcare data)
- [ ] PCI-DSS (payment card data)
- [ ] SOC 2 (security controls)
- [ ] Other: _______________

---

## Known Issues & Technical Debt

| Issue | Impact | Workaround | Priority | Tags |
|-------|--------|------------|----------|------|
| ❓ | ❓ | ❓ | ❓ | #technical-debt |

---

## Interview Questions for This Database

> Use these questions during the MCP interview to capture critical context.

### For Developer Role

| Question | Answer |
|----------|--------|
| Where are database scripts currently stored? | ❓ |
| What ORM or data access pattern is used? | ❓ |
| Are there any undocumented stored procedures? | ❓ |
| Which tables have the most active development? | ❓ |
| Are there objects no one has touched in years? | ❓ |

### For Technical Lead Role

| Question | Answer |
|----------|--------|
| Who executes scripts against production? | ❓ |
| What backup/recovery process exists? | ❓ |
| Are there external systems that access this database? | ❓ |
| What objects are candidates for removal? | ❓ |
| Is there a migration path to a proper DB project? | ❓ |

### For Scrum Master / Process Role

| Question | Answer |
|----------|--------|
| How are schema changes communicated to the team? | ❓ |
| What approval process exists for production changes? | ❓ |
| Who owns database knowledge on the team? | ❓ |

---

## Migration Path (Optional)

> If the team decides to move to a proper database project in the future.

### Recommended Approach

1. **Phase 1:** Organize scripts in `database/scripts/` (this template)
2. **Phase 2:** Add migration tool (DbUp, Flyway, EF Migrations)
3. **Phase 3:** Create SSDT/DB project from existing schema
4. **Phase 4:** Set up CI/CD for automated deployments

### Current Blockers to Migration

❓ *What prevents moving to a DB project today?*
- [ ] Team bandwidth
- [ ] Legacy complexity
- [ ] Lack of expertise
- [ ] Not a priority
- [ ] Other: _______________

---

## Appendix: Quick Schema Reference

<details>
<summary>Click to expand full schema overview</summary>

### All Tables (Alphabetical)

🤖 *Auto-generate from database:*

```sql
-- Generate this list with:
SELECT TABLE_SCHEMA, TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_SCHEMA, TABLE_NAME;
```

| Schema | Table Name | Tier | Status |
|--------|------------|------|--------|
| 🤖 | 🤖 | 🤖 | 🤖 |

### All Views

```sql
SELECT TABLE_SCHEMA, TABLE_NAME 
FROM INFORMATION_SCHEMA.VIEWS
ORDER BY TABLE_SCHEMA, TABLE_NAME;
```

| Schema | View Name | Tier | Status |
|--------|-----------|------|--------|
| 🤖 | 🤖 | 🤖 | 🤖 |

### All Stored Procedures

```sql
SELECT ROUTINE_SCHEMA, ROUTINE_NAME 
FROM INFORMATION_SCHEMA.ROUTINES
WHERE ROUTINE_TYPE = 'PROCEDURE'
ORDER BY ROUTINE_SCHEMA, ROUTINE_NAME;
```

| Schema | Procedure Name | Tier | Status |
|--------|----------------|------|--------|
| 🤖 | 🤖 | 🤖 | 🤖 |

</details>

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | ❓ | ❓ | Initial documentation |

---

## Documentation Standards

### This template follows the Application Knowledge Repo (AKR) system

**For universal conventions, see:**
- **AKR_CHARTER.md** - Core principles, generic data types, feature tags

**For database-specific conventions, see:**
- **AKR_CHARTER_DB.md** - Database object naming, constraints, patterns

**Related Templates:**
- **table_doc_template.md** - Individual table documentation (for Tier 1 objects)
- **legacy_inventory_template.md** - Legacy object tracking (for Tier 3)

---

## AI Generation Instructions

**For AI (Copilot/ChatGPT/Claude):**

When generating this documentation:
1. Mark all AI-generated content with 🤖
2. Mark sections needing human input with ❓
3. Extract object inventory from database metadata queries
4. Classify objects into tiers based on last modified dates
5. Identify active objects from code references (grep for table names)
6. Flag legacy objects with no code references

**For Humans:**

After AI generates baseline:
1. Verify tier classifications (10 min)
2. Add change management process details (10 min)
3. Document connection/integration info (5 min)
4. Complete security & compliance section (5 min)
5. Answer interview questions (10 min)
6. Create individual docs for Tier 1 objects (15-30 min each)

**Total Time (Initial):** 2-4 hours for full database documentation

---

## Tags & Metadata

**Tags**: 🤖 #[feature-domain] #database #[priority] #[status]

❓ **Add feature tags** (see TAGGING_STRATEGY_TAXONOMY.md):
- Feature Domain tags (e.g., #user-profile, #course-catalog)
- Cross-Cutting tags (e.g., #audit-logging, #data-validation)
- Technical tag: #database
- Priority tag (e.g., #core-feature, #important)
- Status tag (e.g., #deployed, #stable, #legacy)

**Example**: `#enrollment #audit-logging #database #core-feature #stable`

**Related Features**:
- 🤖 [Feature documentation that uses this database]
- ❓ [Add links to features in AKR_Main/features/ folder]

**Database Metadata**:
- **Domain**: ❓ [Primary business domain]
- **Priority**: ❓ [P0: Core | P1: Important | P2: Legacy]
- **Management Approach**: ❓ [Manual scripts | Transitioning to formal tool]
- **Owner**: ❓ [Team responsible]

---

## Template Metadata

**Template Version**: 1.0  
**Created**: 2025-12-02  
**Template Type**: Embedded Database (No DB Project)  
**Part of**: Application Knowledge Repo (AKR) system  
**Maintained By**: Architecture Team

**When to use this template:**
- Database managed without SSDT, DbUp, Flyway, or similar tools
- Scripts maintained manually in shared drives or scattered locations
- Small to medium databases (< 100 objects typical)
- Legacy applications with stable schemas
- Teams transitioning toward formal DB management
