# Backend Service Documentation System - Implementation Guide

**Version:** 1.0  
**Last Updated:** October 28, 2025  
**Target Audience:** Development Teams & Technical Leaders  
**Technology Stack:** ASP.NET Core, React, SQL Server, Azure Boards  

---

## 📋 Table of Contents

1. [Quick Start (TL;DR)](#quick-start-tldr)
2. [System Overview](#system-overview)
3. [Template Structure](#template-structure)
4. [Workflow Process](#workflow-process)
5. [Implementation Steps](#implementation-steps)
6. [Quality Gates & Success Criteria](#quality-gates--success-criteria)
7. [Reference Materials](#reference-materials)
8. [FAQ](#faq)

---

## Quick Start (TL;DR)

### The Problem

Legacy backend services lack documentation. Developers struggle to:
- Understand business rules embedded in code
- Know why specific validations exist
- Identify what breaks when making changes
- Onboard new team members efficiently

AI tools like GitHub Copilot cannot provide context about code that has no documentation.

### The Solution

**Hybrid AI-Human Documentation System:**
1. **AI (Copilot) generates 65-70%** - Technical structure, method calls, data flow
2. **Developers add 30-35%** - Business context, WHY decisions, critical gotchas
3. **Result:** Production-ready documentation in **25 minutes per service**

### Time Investment

| Activity | Time | Output |
|----------|------|--------|
| AI generates baseline | 5 minutes | 65% complete documentation |
| Developer enhances | 20 minutes | 90% complete, production-ready |
| **Total per service** | **25 minutes** | **Useful, maintainable documentation** |

### Expected Outcomes

**After 1 month:**
- ✅ 10-15 services documented (baseline quality)
- ✅ 3-5 critical services enhanced (90%+ quality)
- ✅ New developers reference docs regularly
- ✅ Fewer "why does this work this way?" questions

**After 3 months:**
- ✅ 30+ services documented
- ✅ Documentation referenced in code reviews
- ✅ Onboarding time reduced 30-50%
- ✅ Team maintains documentation naturally

### Key Decisions Already Made

✅ Documentation happens AFTER code deployment (separate work items)  
✅ No inline comments in existing code (too invasive, deployment risk)  
✅ API endpoints link to existing API documentation database (no duplication)  
✅ Git is source of truth for change history (no "Change History" section in docs)  
✅ Focus on service/business logic layer (not controllers, not repositories)  

---

## System Overview

### What We're Documenting

**Target:** Backend service layer (business logic)

```
┌──────────────────────┐
│   Controllers        │  → Already documented in API database
│   (API Layer)        │     (Link to existing docs)
└──────────────────────┘
           ↓
┌──────────────────────┐
│   ► SERVICES ◄       │  ← THIS is what we document
│   (Business Logic)   │     (New documentation system)
└──────────────────────┘
           ↓
┌──────────────────────┐
│   Repositories       │  → Database operations
│   (Data Layer)       │     (Straightforward, low documentation need)
└──────────────────────┘
```

**Why services?**
- Contain business rules (BR-XXX-### format)
- Contain WHY decisions (not visible in code)
- Complex orchestration logic
- Cross-cutting concerns (validation, authorization, side effects)

### What AI Can vs Cannot Do

| Aspect | AI Capability | Human Requirement |
|--------|---------------|-------------------|
| **Method signatures** | ✅ 95% accurate | Review for business terms |
| **Call flow** | ✅ 90% accurate | Add WHY explanations |
| **Error messages** | ✅ 95% accurate | Add when/why they occur |
| **Dependencies** | ✅ 90% accurate | Add failure behavior |
| **Business rules** | ⚠️ 40% accurate | Add WHY rules exist |
| **Historical context** | ❌ 0% accurate | Human must provide |
| **Performance notes** | ❌ 0% accurate | Add after production use |
| **Side effects** | ⚠️ 50% accurate | Clarify async/blocking |

**Key Insight:** AI extracts WHAT code does. Humans must add WHY it does it.

### Integration with Existing Systems

**Azure Boards:**
- User Story (US###) → Code implementation → Deploy → Close
- NEW: Documentation Task (DOC-US###) → Generate + enhance docs → PR review → Close

**API Documentation Database:**
- Existing system documents REST endpoints
- Service documentation links to API docs (no duplication)
- Service docs focus on business logic, not HTTP contracts

**Git Repositories:**
- Service documentation lives in same repo as code: `/docs/services/`
- Change history tracked via Git (not in documentation files)
- Documentation PRs reviewed like code PRs

---

## Template Structure

### Template Files

1. **Service_Documentation_Template_v3.md** - The template (reference file)
2. **EnrollmentService_Baseline_Sample.md** - Example of AI-generated baseline
3. **This guide** - How to use the template

### Baseline vs Optional Sections

#### 📋 Baseline Sections (Required - 25 minutes)

These sections form the **minimum viable documentation**:

```
✅ Quick Reference (TL;DR)
   - What it does, when to use, watch out for

✅ What & Why
   - Purpose, capabilities, scope boundaries

✅ How It Works
   - Primary operation step-by-step flow
   - Input/output, success/failure paths

✅ Business Rules
   - Table format: Rule ID, Description, Why, Since

✅ Architecture
   - Dependencies, consumers, failure modes

✅ Data Operations
   - Reads from, writes to, side effects

✅ Questions & Gaps
   - AI-flagged unknowns, human uncertainties
```

**Output:** 65-70% complete, immediately useful

---

#### 🔧 Optional Sections (Add Later - 10-15 minutes each)

Add these as knowledge accumulates:

```
⏳ Alternative Paths
   Add when: Complex conditional logic exists

⏳ Performance
   Add when: Production metrics available

⏳ Known Issues & Limitations
   Add when: Bugs discovered, workarounds needed

⏳ External Dependencies
   Add when: External system integrations exist

⏳ Common Problems & Solutions
   Add when: Support tickets/incidents occur

⏳ What Could Break
   Add when: Understanding downstream impact
```

**Trigger-based:** Add sections when circumstances warrant, not upfront.

### Section-by-Section AI/Human Split

| Section | AI Generates | Human Adds | Time |
|---------|--------------|------------|------|
| Quick Reference | Structure | Usage scenarios, gotchas | 3 min |
| What & Why | Technical description | Business value, rationale | 5 min |
| How It Works | Flow, calls | WHY each step | 5 min |
| Business Rules | Rule detection | WHY rules exist, since when | 5 min |
| Architecture | Dependencies list | Failure behavior | 2 min |
| Data Operations | Tables, operations | Business purpose | 1 min |
| Questions & Gaps | Technical unknowns | Business questions | 2 min |
| **Total** | **15 min (AI)** | **20-25 min (Human)** | **~25 min** |

---

## Workflow Process

### Three-Phase Approach

```
Phase 1: Initial Baseline (Week 1)
    ↓ Generate 70% documentation for all services
    ↓ Time: 25 min per service × 10 services = 4 hours

Phase 2: Selective Enhancement (Ongoing)
    ↓ Enhance critical services to 90%+
    ↓ Add optional sections as needed
    ↓ Time: 15 min per update, as knowledge grows

Phase 3: Knowledge Accumulation (Continuous)
    ↓ Documentation updates during normal work
    ↓ Bug fixes → add to Known Issues
    ↓ Incidents → add to Common Problems
    ↓ Time: 5-10 min per code change
```

---

### Phase 1: Initial Baseline (Week 1)

**Goal:** Get 65-70% documentation for all backend services

**Process:**

```
For each service:

1. Developer identifies target service
   Example: EnrollmentService
   Time: 1 minute

2. Developer finds related files
   - ServiceFile.cs (main service)
   - ControllerFile.cs (or note API docs link)
   - RepositoryFile.cs (data access)
   - EntityFile.cs (domain model - optional)
   Time: 2-3 minutes

3. Developer attaches files to Copilot Chat
   - Open VSCode
   - Open Copilot Chat (Ctrl+Shift+I)
   - Use @ to attach 3-5 files
   Time: 1 minute

4. Developer uses prompt (see Implementation Steps)
   - Paste prompt
   - AI generates documentation
   Time: 5 minutes (AI processing)

5. Developer reviews and enhances
   - Add WHY to business rules (5 min)
   - Add failure modes to dependencies (3 min)
   - Add questions to Questions & Gaps (2 min)
   - Review flow diagram for accuracy (5 min)
   - Add Quick Reference details (3 min)
   Time: 20 minutes

6. Developer saves and commits
   - Save to /docs/services/[ServiceName]_doc.md
   - Create PR: "docs: add [ServiceName] baseline documentation"
   - Link to documentation task in Azure Boards
   Time: 2 minutes

Total: 25 minutes per service
```

**Azure Boards Integration:**

```
User Story US### → Code implemented → Deployed → Closed

NEW Work Item Created:
DOC-US### "Document [ServiceName]"
Type: Task
Assigned to: Original developer or documentation specialist
Estimate: 1 hour (includes review time)
Acceptance Criteria:
- Baseline documentation created
- All ❓ NEEDS HUMAN INPUT items addressed
- PR reviewed and merged
```

**Week 1 Output:**
- 10-15 services documented (baseline)
- Each service: 65-70% complete
- Immediately useful for team

---

### Phase 2: Selective Enhancement (Ongoing)

**Goal:** Enhance critical services to 90%+, add optional sections

**Triggers for Enhancement:**

```
→ Performance Issue Discovered
  Add "Performance" section with:
  - Response time metrics
  - Bottlenecks identified
  - Optimization attempts
  Time: 15 minutes

→ Production Incident Occurs
  Add to "Common Problems & Solutions":
  - What happened
  - Why it happened
  - How to fix
  - How to prevent
  Time: 15 minutes

→ External Integration Added
  Add to "External Dependencies":
  - System details
  - Failure behavior
  - Contact information
  Time: 10 minutes

→ Breaking Change Planned
  Add to "What Could Break":
  - Dependencies identified
  - Downstream impacts
  - Migration strategy
  Time: 15 minutes
```

**Process:**

```
When trigger occurs:

1. Developer updates relevant section
2. Adds date and context
3. Creates PR: "docs: add [topic] to [ServiceName]"
4. Links to work item (bug fix, feature, incident)
5. Team reviews and merges

Time: 10-15 minutes per update
```

**Month 2-3 Output:**
- 3-5 critical services at 90%+ quality
- Optional sections added where valuable
- Documentation reflects production learnings

---

### Phase 3: Knowledge Accumulation (Continuous)

**Goal:** Documentation grows naturally as team learns

**Integration with Development Workflow:**

```
Code Change Workflow:

1. Developer makes code change (bug fix, feature, refactor)
2. Before creating PR, check documentation
3. Update documentation if behavior changed:
   - Business rule added/changed → Update Business Rules table
   - New validation → Update How It Works flow
   - New dependency → Update Architecture section
   - New error → Update Error Reference Guide
4. Include documentation update in same PR
5. Code review includes documentation review

Time: +5-10 minutes per code change
```

**Documentation Maintenance Checklist** (in every service doc):

```markdown
**When making code changes:**

- [ ] Update this doc if behavior changes
- [ ] Update error codes if new errors added
- [ ] Update flow diagram if steps changed
- [ ] Update performance metrics if significant impact
- [ ] Add to "Known Issues" if introducing limitation
```

**Result:** Documentation stays current without heroic effort

---

## Implementation Steps

### Step 1: File Setup (One-Time)

**Directory Structure:**

```
your-api-repo/
├── src/
│   └── Services/
│       ├── EnrollmentService.cs
│       ├── CourseService.cs
│       └── ...
├── docs/
│   ├── services/                    ← Create this
│   │   ├── _template.md             ← Template file
│   │   ├── EnrollmentService_doc.md
│   │   ├── CourseService_doc.md
│   │   └── ...
│   └── README.md                    ← Link to this guide
└── README.md
```

**Setup Commands:**

```bash
# From repository root
mkdir -p docs/services

# Copy template (download from project files)
cp Service_Documentation_Template_v3.md docs/services/_template.md

# Create README linking to this guide
echo "# Service Documentation" > docs/services/README.md
echo "See: Backend_Service_Documentation_Guide.md" >> docs/services/README.md
```

---

### Step 2: Using Copilot Chat

**VSCode Setup:**

1. **Install GitHub Copilot** (if not already installed)
2. **Open Copilot Chat:** `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Shift+I` (Mac)
3. **Attach files using @:** Type `@` in chat to select files

**File Selection Strategy:**

```
Minimum (3 files):
- @ServiceFile.cs (the main service)
- @RepositoryFile.cs (data access)
- @EntityFile.cs (domain model)

Recommended (4-5 files):
- @ServiceFile.cs
- @ControllerFile.cs (to see API usage)
- @RepositoryFile.cs
- @EntityFile.cs
- @RequestDto.cs (if complex request models)

Avoid:
- Too many files (>6) - confuses AI
- Unrelated files - adds noise
- Interface files only - AI needs implementations
```

**Pro Tip:** If Copilot output is poor, try reducing to just service file first, then incrementally add related files.

---

### Step 3: The Copilot Prompt

**Recommended Prompt:**

```
Generate baseline service documentation following the template at docs/services/_template.md

**Include ONLY baseline sections (skip optional sections):**
1. Quick Reference (TL;DR)
2. What & Why - Purpose, Capabilities, Not Responsible For
3. How It Works - Primary operation with step-by-step flow
4. Business Rules - Table format with Rule ID, Description, Why, Since
5. Architecture - Dependencies and Consumers
6. Data Operations - Reads, Writes, Side Effects
7. Questions & Gaps - Flag unknowns

**Important instructions:**
- For API Layer: Reference API documentation at [YOUR_API_DOCS_URL] instead of duplicating endpoint details
- Mark each item with 🤖 (AI generated) or ❓ (needs human clarification)
- Use text-based flow diagrams in boxes (NOT Mermaid)
- Focus on WHAT code does (AI can extract from code)
- Flag WHY questions for human input (AI cannot determine business context)
- Keep business rule descriptions simple, mark "Why It Exists" column as ❓
- Flag magic numbers, hardcoded values, or unclear logic
- For side effects (email, audit logs), mark async/blocking behavior as ❓

**Attached files:**
- [List the files you attached]

**Service name:** [ServiceName]

**Output format:** Complete markdown following exact template structure
```

**Customization:**
- Replace `[YOUR_API_DOCS_URL]` with actual API documentation link
- Replace `[ServiceName]` with actual service name
- Adjust file list to match what you attached

---

### Step 4: Review AI Output

**Validation Checklist:**

```
Quick Scan (1 minute):
- [ ] Service name correct in title
- [ ] All baseline sections present
- [ ] Flow diagram has reasonable structure
- [ ] No obvious errors or hallucinations

Structure Check (2 minutes):
- [ ] Quick Reference has all three items (what/when/watch out)
- [ ] Business Rules in table format
- [ ] Architecture shows dependencies and consumers
- [ ] Questions & Gaps has AI-flagged items

Accuracy Check (3 minutes):
- [ ] Method names correct
- [ ] Parameters and return types accurate
- [ ] Error messages match code
- [ ] Dependencies list complete
```

**Common AI Errors to Fix:**

| Error | How to Spot | How to Fix |
|-------|-------------|------------|
| Hallucinated methods | Method doesn't exist in code | Delete or correct |
| Wrong parameter types | Type doesn't match signature | Fix type |
| Incorrect flow order | Steps don't match code sequence | Reorder steps |
| Missing dependencies | Constructor has more injections | Add missing items |
| Generic descriptions | "Handles enrollment logic" (too vague) | Make specific |

---

### Step 5: Human Enhancement (20 minutes)

**Priority Order:**

#### **1. Business Rules (5 minutes - CRITICAL)**

Find the Business Rules table. For each rule:

```markdown
Before (AI-generated):
| **BR-ENR-001** | User must complete prerequisites | ❓ NEEDS INPUT | ❓ NEEDS INPUT |

After (Human-enhanced):
| **BR-ENR-001** | User must complete prerequisites | Training progression - basic before advanced. Safety requirement. | Initial (2024-07) |
```

**Action:** Add WHY each rule exists, when it was added

---

#### **2. Flow Diagram "Why" (5 minutes - HIGH VALUE)**

Add business context to each step:

```markdown
Before (AI-generated):
│  Why   → ❓ NEEDS HUMAN INPUT                           │

After (Human-enhanced):
│  Why   → User must complete basic courses before         │
│          advanced ones (safety requirement, BR-ENR-001)  │
```

**Action:** Explain business rationale for each validation

---

#### **3. Dependencies Failure Modes (3 minutes)**

Add what happens if dependency unavailable:

```markdown
Before:
| `IEmailService` | Send confirmation | ❓ NEEDS INPUT |

After:
| `IEmailService` | Send confirmation | ⚠️ Non-blocking - enrollment succeeds, email queued for retry |
```

**Action:** Clarify critical vs non-blocking for each dependency

---

#### **4. Quick Reference Details (3 minutes)**

Complete the TL;DR section:

```markdown
Before:
**When to use it:** ❓ NEEDS HUMAN INPUT

After:
**When to use it:** Anytime a user needs enrollment - web UI, mobile app, admin tools, bulk imports
```

**Action:** Add usage scenarios and critical gotcha

---

#### **5. Questions & Gaps Review (2 minutes)**

Review AI-flagged questions, answer what you can:

```markdown
AI flagged:
- ❓ Magic number "3" - Why 3 specifically?

Human adds:
- ❓ Magic number "3" - Why 3 specifically? 
  → Added after Incident #1234 (Aug 2024) when users hoarded slots. 
     Data showed 95% completion at ≤3 vs 30% at >3. Ask @product-lead for details.
```

**Action:** Answer questions you know, note who to ask for others

---

#### **6. What & Why Expansion (2 minutes)**

Add business context:

```markdown
Before (AI):
EnrollmentService manages course enrollments with validation.

After (Human):
EnrollmentService centralizes enrollment business rules that must be 
consistently enforced across web, mobile, and admin tools. Without it, 
validation would scatter across controllers, causing inconsistent rule 
enforcement. This is business-critical - incorrect enrollments affect 
compliance reporting.
```

**Action:** Explain business value, why it exists

---

### Step 6: Save and Submit

**File Naming:**

```
Format: [ServiceName]_doc.md
Examples:
- EnrollmentService_doc.md
- AuthenticationService_doc.md
- PaymentProcessingService_doc.md
```

**Git Workflow:**

```bash
# Create documentation branch
git checkout -b docs/add-enrollment-service-documentation

# Save file
# Location: docs/services/EnrollmentService_doc.md

# Stage and commit
git add docs/services/EnrollmentService_doc.md
git commit -m "docs: add EnrollmentService baseline documentation

- Generated baseline using Copilot (70% complete)
- Enhanced with business rules context
- Linked to API documentation database
- Flagged questions for product team review

Related: DOC-US124"

# Push and create PR
git push origin docs/add-enrollment-service-documentation

# Create PR in GitHub/Azure DevOps
# Title: "docs: EnrollmentService baseline documentation"
# Description: Link to Azure Boards task DOC-US124
# Reviewers: Tech lead or senior developer
```

---

### Step 7: Review Process

**Documentation PR Review Checklist:**

```
Reviewer checks:

Technical Accuracy (5 minutes):
- [ ] Method signatures correct
- [ ] Flow diagram matches code logic
- [ ] Dependencies complete
- [ ] Error messages accurate

Business Context (3 minutes):
- [ ] Business rules have "Why It Exists"
- [ ] Flow steps have business rationale
- [ ] "What & Why" explains business value
- [ ] Quick Reference has usage scenarios

Completeness (2 minutes):
- [ ] All baseline sections present
- [ ] All ❓ NEEDS INPUT items addressed or noted
- [ ] Questions & Gaps has next steps
- [ ] Related docs linked (API database)

Quality (2 minutes):
- [ ] No obvious errors or hallucinations
- [ ] Descriptions are specific, not generic
- [ ] Reasonable level of detail (not too sparse/verbose)
```

**Approval Criteria:**

✅ **Approve if:**
- Technical accuracy verified
- Business context added (even if incomplete)
- Immediately useful for team

❌ **Request changes if:**
- Technical errors (wrong methods, flow, parameters)
- No business context added (still all ❓)
- Missing critical sections

**Review Time:** 10-15 minutes per documentation PR

---

## Quality Gates & Success Criteria

### What "Good Enough" Looks Like

#### Baseline Documentation (70% Complete)

**Minimum Standard:**

```
✅ All baseline sections present
✅ Flow diagram shows actual code path
✅ Business rules have descriptions
✅ Dependencies listed with purpose
✅ No obvious technical errors
✅ At least 50% of ❓ items addressed
✅ Questions & Gaps identifies unknowns
```

**Is useful for:**
- New developer understanding what service does
- Existing developer making changes
- Code reviewer understanding context
- Incident responder debugging issues

**Example verdict:** "This is 70% complete but immediately valuable."

---

#### Enhanced Documentation (90% Complete)

**High Standard:**

```
✅ All baseline items PLUS:
✅ Every business rule has "Why It Exists"
✅ Flow diagram has business rationale for each step
✅ Dependencies have failure modes
✅ Side effects clarified (async/blocking)
✅ Quick Reference has critical gotcha
✅ 80%+ of questions answered
✅ At least 1 optional section added (if applicable)
```

**Is useful for:**
- Everything baseline provides PLUS:
- Product/business understanding why system works this way
- Architecture decisions when planning changes
- Incident post-mortems understanding context
- Compliance audits showing why rules exist

**Example verdict:** "This is production-ready, comprehensive documentation."

---

### Metrics to Track

**Process Metrics (How Well Is System Working?):**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Documentation coverage | 80% of services | Count documented vs total services |
| Average completion time | <30 min per service | Track time in Azure Boards |
| Documentation age | <3 months for 80% | Last updated date |
| PR review time | <1 day | Time from PR open to merge |

**Value Metrics (Is Documentation Actually Useful?):**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Documentation references | 10+ per week | Search "see docs/" in Slack/PRs |
| Onboarding time reduction | 30% reduction | Survey new developers |
| Questions in code reviews | 20% reduction | Count "why does this" questions |
| Incident resolution time | 15% faster | Compare before/after average |

**Leading Indicators (Early Warning Signs):**

🚨 **Red Flags:**
- Documentation not referenced in 2+ weeks (unused)
- >20% of docs not updated in 6+ months (stale)
- Developers consistently skip documentation tasks (resistance)
- PRs approved without review (rubber-stamping)

✅ **Green Lights:**
- Developers voluntarily update docs during code changes
- New developers cite docs in PRs/questions
- Tech lead references docs in architecture discussions
- Documentation debt backlog <5 items

---

### Quarterly Review Process

**Every 3 months, evaluate:**

```
1. Coverage Assessment (15 minutes)
   - How many services documented?
   - Which critical services missing?
   - Update documentation roadmap

2. Quality Spot Check (30 minutes)
   - Review 5 random service docs
   - Check for staleness
   - Verify accuracy against code
   - Grade: Excellent / Good / Needs Work

3. Value Assessment (15 minutes)
   - Review metrics (usage, onboarding time)
   - Survey team: "Is documentation helping?"
   - Identify gaps: what's missing?

4. Process Improvements (15 minutes)
   - What's working well?
   - What's painful?
   - Adjust template if needed
   - Adjust workflow if needed

5. Decision Point (15 minutes)
   - Continue as-is?
   - Expand to more services?
   - Simplify if too complex?
   - Add automation?
```

**Decision Framework:**

```
If metrics are GREEN:
→ Expand: Document more services
→ Enhance: Add more optional sections
→ Automate: Invest in tooling

If metrics are YELLOW:
→ Investigate: Why not being used?
→ Simplify: Is template too complex?
→ Train: Do developers need help?

If metrics are RED:
→ Pause: Stop new documentation
→ Retrospective: What went wrong?
→ Pivot: Try different approach
```

---

## Reference Materials

### Template Files

1. **Service_Documentation_Template_v3.md**
   - Full template with all sections
   - AI/Human indicators throughout
   - Baseline/Optional section markers
   - Location: `docs/services/_template.md`

2. **EnrollmentService_Baseline_Sample.md**
   - Real example of AI-generated baseline
   - Shows what 70% complete looks like
   - Includes all ❓ NEEDS INPUT markers
   - Location: Project files or shared drive

3. **Backend_Service_Documentation_Guide.md**
   - This document
   - Complete implementation guide
   - Location: Project files or shared drive

---

### Copilot Resources

**Prompt Library:**

```markdown
# Basic Prompt (5 services)
[See Step 3 above]

# Extended Prompt (Complex services)
[Basic prompt] + 
"This is a complex service with:
- Multiple conditional flows
- External system integrations
- Performance-critical operations
Please flag any unclear logic or magic numbers."

# Focused Prompt (Update existing)
"Update the Business Rules section in this documentation 
to reflect the new BR-ENR-005 rule added in the latest code.

Current documentation: [paste relevant section]
Code changes: [paste new validation logic]

Follow existing format and style."
```

**Troubleshooting Copilot Issues:**

| Issue | Cause | Solution |
|-------|-------|----------|
| Output too generic | Too few files attached | Attach service + repository files |
| Hallucinated methods | Code analysis error | Review and correct manually |
| Incomplete flow | Complex nested logic | Break into smaller methods first |
| Missing dependencies | Interface without implementation | Attach implementation files |
| Poor business context | Expected (AI limitation) | Human must add context |

---

### Integration Points

**Azure Boards Configuration:**

```yaml
Documentation Task Template:

Title: "Document [ServiceName]"
Type: Task
Area Path: Documentation
Parent: [Link to User Story that implemented the service]

Description Template:
"Generate and enhance baseline documentation for [ServiceName].

Files to document:
- src/Services/[ServiceName].cs
- src/Controllers/[ControllerName].cs
- src/Repositories/[RepositoryName].cs

Acceptance Criteria:
- [ ] Baseline documentation generated using Copilot
- [ ] All ❓ NEEDS INPUT items addressed
- [ ] Business rules have "Why It Exists" context
- [ ] Dependencies have failure modes
- [ ] PR created and reviewed
- [ ] Documentation merged to main

Estimated Effort: 1 hour"

Tags: documentation, baseline, [service-name]
```

**Git Commit Convention:**

```
Format: docs: [action] [object] - [description]

Examples:
docs: add EnrollmentService baseline documentation
docs: update CourseService - add performance section
docs: fix typo in AuthService business rules
docs: enhance PaymentService with incident learnings

Include in commit message:
- Related Azure Boards item: "Related: DOC-US124"
- What % complete: "70% baseline" or "Enhanced to 90%"
- Next steps if incomplete: "TODO: Get performance metrics"
```

**API Documentation Database Integration:**

```markdown
# In Service Documentation

## Architecture

### Where This Fits

```
┌──────────────────────┐
│   API Layer          │  EnrollmentController
│   (Entry Point)      │  → See API Reference Database:
│                      │     https://api-docs.company.com/enrollments
│                      │     (Endpoints: POST, GET, PATCH, DELETE)
└──────────────────────┘
```

**Link format:** Always use full URL, not relative path
**Update frequency:** Verify link quarterly (API docs may move)
```

---

### Directory Structure Best Practices

**Recommended Layout:**

```
your-api-repo/
├── docs/
│   ├── services/                    # Service documentation (this system)
│   │   ├── _template.md             # Template
│   │   ├── README.md                # Quick guide
│   │   ├── EnrollmentService_doc.md
│   │   ├── CourseService_doc.md
│   │   └── ...
│   ├── api/                         # API endpoint docs (existing system)
│   │   └── [links to API database]
│   ├── database/                    # Database schema docs (if exists)
│   │   ├── tables/
│   │   └── stored-procedures/
│   └── architecture/                # High-level architecture docs
│       ├── system-overview.md
│       └── decision-records/
└── src/
    └── Services/
        ├── EnrollmentService.cs     # Code
        └── ...
```

**Why this structure:**
- Documentation near code (same repo)
- Clear separation by type (services vs API vs database)
- Easy to navigate
- Scales as documentation grows

---

## FAQ

### General Questions

**Q: Why not just use inline comments in code?**

**A:** For existing legacy code:
- Too invasive (requires touching all code files)
- Deployment risk (code changes require testing)
- Hard to get buy-in (developers resist modifying working code)
- For NEW code, inline comments are encouraged as supplement

---

**Q: Why separate documentation work items instead of including in feature work?**

**A:** Pragmatic reasons:
- Feature work shouldn't be blocked by documentation
- Documentation happens after code is stable
- Makes documentation effort visible to management
- Allows specialization (best writer can do documentation)

---

**Q: What if AI generates wrong information?**

**A:** Expected and manageable:
- Developer reviews AI output (Step 4)
- Validation checklist catches common errors
- Code reviewer double-checks technical accuracy
- Worst case: Fix in follow-up PR (documentation is versioned)

**Key:** AI generates 70%, human reviews 100%

---

**Q: How do we keep documentation from getting stale?**

**A:** Three strategies:
1. **Just-in-time updates:** Update docs when touching code
2. **Maintenance checklist:** Built into every service doc
3. **Quarterly review:** Spot-check docs, update stale ones

**Acceptable:** Some staleness is OK. 80% accurate is infinitely better than 0% documented.

---

### Technical Questions

**Q: What if service has no controller (internal service)?**

**A:** Skip the Architecture diagram's API layer:

```markdown
## Architecture

This is an internal service (not exposed via API).

**Consumers (Who Uses This Service):**
- OtherService.cs - For [use case]
- BackgroundJob.cs - For [scheduled task]
```

---

**Q: What if service is very simple (just CRUD)?**

**A:** Use minimal documentation:

```markdown
# Simple Service Template

**What it does:** Basic CRUD operations for [Entity]

**No complex business rules** - Straightforward create/read/update/delete

**See:** 
- API Database for endpoint details
- [Entity]Repository for data operations
```

**Time:** 5 minutes. Don't over-document simple services.

---

**Q: What if we don't have GitHub Copilot?**

**A:** Alternatives:
1. **ChatGPT/Claude:** Copy code into chat, use same prompt
2. **Manual documentation:** Use template, fill in sections (takes longer)
3. **Hybrid:** Use free AI tools for generation, manual for enhancement

**Note:** This system works without AI, just takes 60-90 minutes instead of 25 minutes.

---

**Q: Can we customize the template for our team?**

**A:** Yes! Template is starting point:
- Add sections specific to your domain
- Remove sections that don't apply
- Adjust level of detail up/down
- Change formatting/structure

**Caution:** Stay consistent within your team. Don't let each developer use different template.

---

### Process Questions

**Q: Who reviews documentation PRs?**

**A:** Recommended:
- **First choice:** Tech lead or senior developer
- **Second choice:** Original code author (if different from doc author)
- **Not recommended:** Junior developers (may miss business context)

**Review time:** 10-15 minutes per documentation PR

---

**Q: What if developer doesn't know answers to business questions?**

**A:** Perfectly acceptable:
- Leave ❓ markers in documentation
- Add to Questions & Gaps: "Ask @product-lead"
- Create follow-up task: "DOC-US124-FOLLOWUP: Get BR-ENR-004 rationale"

**Don't:** Block documentation on getting all answers. 70% complete now > 100% complete never.

---

**Q: How do we prioritize which services to document first?**

**A:** Prioritization framework:

```
Priority 1 (Document first):
- High complexity (>300 lines)
- Frequent changes (touched in last 3 months)
- Business-critical (payments, auth, core features)
- Common confusion (new developers ask about it)

Priority 2 (Document soon):
- Medium complexity
- Occasional changes
- Important but not critical
- Some confusion

Priority 3 (Document later):
- Simple CRUD operations
- Rarely changed
- Self-explanatory
- No confusion
```

**Pro tip:** Ask team "Which 5 services cause the most confusion?" Start there.

---

**Q: What if team resists documenting?**

**A:** Common issue. Strategies:

**Week 1-2: Lead by example**
- Tech lead documents 2-3 services
- Shows it's valuable, not painful
- Demonstrates time investment is reasonable

**Week 3-4: Make it easy**
- Provide clear template
- Copilot prompt ready to copy/paste
- Documentation tasks right-sized (1 hour max)

**Month 2: Show value**
- New developer references docs in PR
- Code review time reduced
- Questions answered by "see docs/"

**Month 3: Reinforce**
- Celebrate good documentation in team meetings
- Include documentation in performance reviews
- Make it normal part of workflow

**If still resistant:** Something is wrong. Retrospective: Is template too complex? Is documentation not useful? Adjust approach.

---

### Maintenance Questions

**Q: How often should we update documentation?**

**A:** Event-driven, not time-driven:

```
Update documentation when:
✅ Code behavior changes (business logic modified)
✅ New business rule added
✅ Dependency added/removed
✅ Bug fix reveals misunderstanding
✅ Performance characteristic changes significantly

Don't update documentation when:
❌ Refactoring without behavior change
❌ Code formatting changes
❌ Test-only changes
❌ Minor optimization (no visible impact)
```

**Rule of thumb:** If code reviewer would want to know about it, document it.

---

**Q: What about documentation for deprecated services?**

**A:** Update status and freeze:

```markdown
# [ServiceName] Documentation

**Status:** 🔴 Deprecated - [Date]
**Replacement:** [NewServiceName] - See [link]
**Deprecation Reason:** [Why being replaced]
**Sunset Date:** [When will be removed]

[Rest of documentation unchanged]
```

Don't delete documentation for deprecated services until code is actually removed.

---

**Q: How do we handle documentation for shared/library services?**

**A:** Extra care required:

```markdown
# Shared Service: [ServiceName]

**Consumers:** Multiple projects
**Change Policy:** Backward compatible changes only
**Contact:** [Team/Person responsible]

⚠️ **Before changing:** Consult with all consumers
```

**Process:**
- More thorough documentation (90%+ quality)
- More thorough review (all consuming teams)
- More careful about breaking changes
- Consider versioning strategy

---

## Getting Started Checklist

### Week 1: Setup (1 hour)

- [ ] Create `/docs/services/` directory in repository
- [ ] Copy template to `docs/services/_template.md`
- [ ] Create README linking to this guide
- [ ] Set up Azure Boards documentation task template
- [ ] Train 1-2 developers on process
- [ ] Document first service (pilot)

### Week 2: Pilot (4 hours team time)

- [ ] Identify 5 services for initial documentation
- [ ] Assign documentation tasks in Azure Boards
- [ ] Generate baseline docs using Copilot
- [ ] Enhance with business context
- [ ] Submit PRs and review
- [ ] Gather feedback from team

### Week 3-4: Iterate (2 hours)

- [ ] Refine template based on feedback
- [ ] Adjust workflow if needed
- [ ] Document 5 more services
- [ ] Train rest of team
- [ ] Establish review cadence

### Month 2: Expand (Ongoing)

- [ ] Continue documenting services (1-2 per week)
- [ ] Add optional sections to critical services
- [ ] Start tracking metrics (usage, coverage)
- [ ] Make documentation part of normal workflow

### Month 3: Evaluate (2 hours)

- [ ] Review metrics (coverage, usage, value)
- [ ] Survey team: Is this helping?
- [ ] Quarterly review meeting
- [ ] Decision: Continue / Adjust / Expand

---

## Success Stories (What Good Looks Like)

### Scenario 1: New Developer Onboarding

**Before Documentation System:**
```
New developer joins, assigned bug in EnrollmentService
Asks: "Why do we limit to 3 enrollments?"
Senior dev explains (20 minutes)
Asks: "Why this validation order?"
Another 15 minutes explanation
Asks: "What if email fails?"
Another 10 minutes
Total: 45 minutes senior dev time
```

**After Documentation System:**
```
New developer reads EnrollmentService_doc.md (10 minutes)
Finds: BR-ENR-004 explains 3-enrollment limit with history
Finds: Flow diagram shows validation order with rationale
Finds: Side effects section clarifies email is non-blocking
Still asks 1-2 clarifying questions (5 minutes)
Total: 15 minutes total time, 40 minutes saved
```

**Result:** 30+ minutes saved per onboarding interaction

---

### Scenario 2: Incident Response

**Before Documentation System:**
```
Production incident: User enrolled despite prerequisites not met
Developer digs through code (30 minutes)
Traces validation logic (15 minutes)
Discovers prerequisite check has bug
Still unclear: When was this added? Why this way?
Escalates to senior dev who wrote it (20 minutes to respond)
Total: 65 minutes to understand context
```

**After Documentation System:**
```
Opens EnrollmentService_doc.md (2 minutes)
Finds: BR-ENR-001 prerequisites rule, when added, why
Finds: Flow diagram step 1 shows prerequisite validation
Identifies bug in code vs documented flow
Fixes bug with full context (10 minutes)
Total: 12 minutes to understand and fix
```

**Result:** 53 minutes saved, faster resolution

---

### Scenario 3: Architecture Decision

**Before Documentation System:**
```
Product wants to change 3-enrollment limit to 5
Tech lead doesn't remember: Why 3?
Searches Slack (no results)
Searches Azure Boards (finds ticket but no rationale)
Schedules meeting with original developer (2 days wait)
Total: 2 days + 30-minute meeting to get context
```

**After Documentation System:**
```
Opens EnrollmentService_doc.md
Finds: BR-ENR-004 documents why 3 specifically
"Added after Incident #1234, data showed 95% completion 
at ≤3 enrollments vs 30% at >3"
Tech lead: "Let's get updated data before changing"
Total: 5 minutes to get context, informed decision
```

**Result:** 2 days saved, better decision

---

## Conclusion

This documentation system balances:
- **AI efficiency** (65-70% generated in minutes)
- **Human expertise** (30-35% critical context)
- **Pragmatic investment** (25 minutes per service)
- **Sustainable maintenance** (just-in-time updates)

**Remember:**
- Start with baseline (70% complete is valuable)
- Enhance critical services (90%+ for top 20%)
- Let knowledge accumulate (documentation grows naturally)
- Measure value (usage, not completeness)

**Success = Documentation that helps the team, not perfect documentation that's never used.**

---

**Version:** 1.0  
**Last Updated:** October 28, 2025  
**Maintained By:** [Your Team Name]  
**Questions?** Contact: [Tech Lead] or [Documentation Champion]

---

*"Good documentation saves debugging time. Great documentation enables better decisions."*
