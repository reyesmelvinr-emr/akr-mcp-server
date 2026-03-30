# Reusable Section Guidance Block (Draft)

Status: Draft
Owner: Standards Team
Intended phase: Phase 2 pilot adoption and feedback

## Purpose

This draft defines a reusable section-level guidance block that can be embedded inside module templates. The goal is to improve section quality and audience fit without duplicating global governance rules.

Use this block for section-specific writing expectations such as tone, depth, and required content elements.

Do not use this block for global policy rules that belong in copilot instructions, validator logic, or SKILL workflow sequencing.

## Reusable Block Template

Copy and adapt per section:

```markdown
### Section Guidance

Audience: [Primary reader personas]
Goal: [What this section must help the reader do]
Tone: [Plain language | mixed technical | deep technical]
Length target: [Word or bullet range]
Must include:
- [Required item 1]
- [Required item 2]
- [Required item 3]
Avoid:
- [Content type to avoid 1]
- [Content type to avoid 2]
Definition of done:
- [Check 1]
- [Check 2]
- [Check 3]
```

## Example: TL;DR Section Guidance

```markdown
### Section Guidance

Audience: Product Owner, QA, new developers
Goal: Explain what the module does and why it matters in business terms
Tone: Plain language first, minimal technical jargon
Length target: 3-5 bullets or up to 120 words
Must include:
- Business outcome enabled by the module
- Who is impacted (user, team, or process)
- One key caveat or risk to know before deeper reading
Avoid:
- Method-by-method flow detail
- Internal class names unless required for clarity
Definition of done:
- A Product Owner can understand the section without reading the rest of the document
- Business value is explicit
- At least one caveat is stated clearly
```

## Adoption Guidance by Artifact

- Template files: include section guidance under sections where audience clarity is critical (for example TL;DR, Business Rules, Data Operations).
- Copilot instructions: keep global constraints only; do not duplicate per-section writing advice.
- SKILL.md: reference that templates may include section guidance blocks; do not restate section-level prose rules.
- Charter: document why section guidance improves readability and governance outcomes.

## Pilot Validation Checklist

Use in Phase 2 runs:

- TL;DR readability validated by at least one non-implementing reviewer (Product Owner or QA)
- Fewer review comments requesting simplification or clarification
- No conflict with required sections or marker rules
- Guidance block remains short enough to avoid material context bloat

## Notes for Future Standardization

If pilot feedback is positive, promote this draft into core templates as a normalized reusable pattern and add a concise reference in the Phase 1 foundation standards docs.
