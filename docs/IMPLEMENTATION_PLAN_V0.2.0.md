# AKR-MCP-Server Implementation Plan v0.2.0
## Refined Implementation (Consolidated & Corrected)

**Last Updated:** February 23, 2026  
**Status:** Ready for Implementation  
**Effort Estimate:** 20–25 days across 5 phases  
**Target Release:** v0.2.0

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Critical Corrections Before Implementation](#critical-corrections-before-implementation)
3. [Refined Phase Breakdown](#refined-phase-breakdown)
4. [First PR Checklist](#first-pr-checklist)
5. [Key Decisions Finalized](#key-decisions-finalized)
6. [Effort & Risk Summary](#effort--risk-summary)
7. [Integration Points](#integration-points)
8. [Testing Strategy](#testing-strategy)
9. [Documentation Updates](#documentation-updates)

---

## Executive Summary

The AKR-MCP-server shifts from **doc generation orchestrator** to **template/charter resource provider + validator**. Copilot Chat uses LLM intelligence for prose generation; the MCP server provides:

- **Resources**: Templates and charters via MCP resource URIs (`akr://template/{id}`)
- **Tools**: Code extraction, validation, charter reference
- **Enforcement**: Write operations gated (off by default) with per-call confirmation
- **Single source of truth**: Templates externalized to [core-akr-templates](https://github.com/reyesmelvinr-emr/core-akr-templates) via Git submodule

### Key Principles

✅ **MCP Compliance**: Uses MCP resources + tools correctly; matches official Python SDK patterns  
✅ **Security-First**: Write ops off by default; explicit per-call confirmation; no identity gaps  
✅ **Cross-Platform**: OS-agnostic docs; cross-OS submodule setup proven  
✅ **Single SSoT**: Externalized templates prevent drift; pinned via submodule commit  
✅ **Deterministic**: Core extractors (C#, SQL) reliable; heuristic extractors deprecated  

### Consolidation Notes

This plan incorporates feedback from **both initial assessment** and **M365 Copilot review**:
- Initial assessment: Identified architectural misalignments, incomplete components, tool deprecations
- M365 feedback: Identified 8 critical implementation gaps (schema wiring, MCP SDK compliance, security hardening, parser decisions, etc.)
- **This document**: Resolves all gaps and provides corrected implementation path

---

## Critical Corrections Before Implementation

These **8 issues** were identified in review and must be fixed before coding starts.

### 1. Schema Dependency Wiring (Critical Bug)

**Issue:** Plan shows `ValidationEngine.validate()` calling `self.template_resolver.build_schema(template_id)`, but `TemplateResolver` doesn't define `build_schema()`. It's in `TemplateSchemaBuilder`.

**Fix:**

**Correct dependency order:**
```
ValidationEngine
  ├─ depends on: TemplateSchemaBuilder
       ├─ depends on: TemplateResolver
```

**Implementation:**
- [src/tools/validation_library.py](src/tools/validation_library.py): Constructor takes `schema_builder: TemplateSchemaBuilder` (not resolver)
- Call: `schema = self.schema_builder.build_schema(template_id)`
- [src/tools/template_schema_builder.py](src/tools/template_schema_builder.py): Already correct (takes resolver, returns schema)
- [src/server.py](src/server.py): Wire at startup:
  ```python
  resolver = TemplateResolver(repo_root, config)
  schema_builder = TemplateSchemaBuilder(resolver)
  validator = ValidationEngine(schema_builder)
  ```

**Files affected:**
- [src/tools/validation_library.py](src/tools/validation_library.py) — **Update constructor**
- [src/tools/template_schema_builder.py](src/tools/template_schema_builder.py) — No change
- [src/server.py](src/server.py) — Wire dependencies at startup

---

### 2. MCP Resource Handlers Must Match Official SDK

**Issue:** Plan sketches decorators without confirming they match the **official MCP Python SDK** exact types and patterns.

**Fix:**

**Action before coding:**
1. Confirm SDK choice: **FastMCP** (recommended, modern) or **low-level MCP Python SDK**
2. Review official SDK docs for:
   - Exact decorator names (`@mcp.resource()` vs. `@server.list_resources()`)
   - Return type signatures (must include `mimeType`, `uri`, `contents`)
   - Resource template pattern (for dynamic URIs)

**Correct implementation pattern:**

For templates as resources:
```python
# SDK-agnostic pseudocode
@server.list_resources()
async def list_resources():
    """List all available template resources."""
    return [
        Resource(
            uri=f"akr://template/{template_id}",
            mimeType="text/markdown",
            name=f"Template: {template_id}"
        )
        for template_id in self.template_resolver.list_templates()
    ]

@server.read_resource(uri_pattern="akr://template/{template_id}")
async def read_template(uri: str):
    """Read a specific template resource."""
    template_id = uri.replace("akr://template/", "")
    content = self.template_resolver.get_template(template_id)
    return ResourceContent(
        uri=uri,
        mimeType="text/markdown",
        text=content
    )
```

**Resource templates (for dynamic URIs):**
```python
@server.list_resource_templates()
async def list_resource_templates():
    """Expose resource template for clients to construct URIs."""
    return [
        ResourceTemplate(
            uriTemplate="akr://template/{id}",
            name="AKR Documentation Templates",
            description="Access templates by ID"
        )
    ]
```

**Files to verify/update:**
- [src/server.py](src/server.py) — Confirm decorators match chosen SDK; ensure return types correct
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Document exact MCP resource shape + types

---

### 3. Cross-OS Submodule Documentation

**Issue:** Windows OneDrive paths with spaces; macOS/Linux contributors will fail when copy-pasting commands.

**Fix:**

**In all docs, use repo-root relative paths:**
- ❌ Bad: `C:\Users\E1481541\OneDrive - Emerson\Documents\...\templates\core`
- ✅ Good: `templates/core` (relative to repo root)

**Submodule setup section (cross-OS):**
```bash
# After cloning the repository
cd akr-mcp-server

# Initialize and update submodules (all platforms)
git submodule update --init --recursive

# Verify submodule is present
git submodule foreach git log -1 --oneline
```

**Clearly document submodule behavior:**
> "Git submodules pin a specific commit and do **not auto-update** to new branches or tags. This is intentional—it ensures stable, reproducible template versions. To update to a new template version, you must explicitly run `git submodule update --remote --merge` and review the diff in your PR."

**Template update workflow section (NEW):**
```bash
# Check for new versions of core-akr-templates
git submodule foreach git fetch --all --tags

# Update submodule to latest tag (after review)
git submodule update --remote --rebase  # or --merge

# Review the diff
git diff templates/core

# Commit the submodule bump
git add .gitmodules templates/core
git commit -m "chore: bump core-akr-templates to vX.Y.Z"
```

**Files to create/update:**
- [SETUP.md](SETUP.md) or [docs/INSTALLATION_AND_SETUP.md](docs/INSTALLATION_AND_SETUP.md) — Add cross-OS submodule setup
- [docs/VERSION_MANAGEMENT.md](docs/VERSION_MANAGEMENT.md) — NEW; document template version management

---

### 4. Secure HTTP Fetch + Cache (If Enabled)

**Issue:** Optional HTTP fetch for template previews has placeholder `requests.get()`; needs security hardening.

**Requirements for `_fetch_from_remote()` in [src/resources/akr_resources.py](src/resources/akr_resources.py):**

✅ **Whitelist trusted hosts** — Only fetch from official [core-akr-templates](https://github.com/reyesmelvinr-emr/core-akr-templates) repo  
✅ **Pin to release tag or commit** — Never fetch HEAD; require explicit version in config  
✅ **Verify SHA-256 hash** — Check fetched content against trusted manifest  
✅ **Cache with TTL** — Store `{templateId, version, sha256_hash, fetch_timestamp, ttl_seconds}`  
✅ **Fail closed** — If fetch fails or hash mismatch, fall back to local/submodule; do NOT write partial  

**Config structure:**
```json
{
  "http_fetch_enabled": false,
  "http_fetch_config": {
    "repo_url": "https://github.com/reyesmelvinr-emr/core-akr-templates",
    "allowed_hosts": ["github.com", "raw.githubusercontent.com"],
    "cache_ttl_seconds": 86400,
    "verify_checksums": true,
    "pinned_version": "v1.3.0",
    "timeout_seconds": 10,
    "max_retries": 1
  }
}
```

**Implementation pattern:**
```python
def _fetch_from_remote(self, template_id: str, version: str) -> str:
    """Securely fetch template from remote with verification."""
    
    # 1. Validate host
    if "github.com" not in self.config.get("repo_url"):
        raise ValueError("Remote fetch: untrusted repository")
    
    # 2. Check cache first
    cache_entry = self._get_cache(template_id, version)
    if cache_entry and not self._cache_expired(cache_entry):
        return cache_entry["content"]
    
    # 3. Fetch with explicit version and timeout (5-10s to prevent Chat hangs)
    url = f"{self.config['repo_url']}/releases/download/{version}/templates/{template_id}.md"
    timeout = self.config.get("timeout_seconds", 10)  # Prevent Copilot Chat hangs
    retry_count = self.config.get("max_retries", 1)
    
    for attempt in range(retry_count + 1):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            content = response.text
            break
        except requests.exceptions.RequestException as e:
            if attempt == retry_count:
                raise ValueError(f"Failed to fetch {template_id} after {retry_count + 1} attempts: {e}")
            # Retry logic; sleep briefly before retry
            time.sleep(1)
    
    # 4. Verify hash (if checksum available)
    if self.config.get("verify_checksums"):
        expected_hash = self._get_expected_hash(template_id, version)
        actual_hash = hashlib.sha256(content.encode()).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError(f"Hash mismatch for {template_id}@{version}")
    
    # 5. Cache and return with provenance metadata
    self._cache_set(template_id, version, content, sha256=actual_hash, source="remote")
    return content
```

**Provenance Tracking:** Log `templateSource` ("submodule"|"local-override"|"remote-preview") and `templateCommit` SHA in metadata for audit trail visibility.

**Files to update:**
- [src/resources/akr_resources.py](src/resources/akr_resources.py) — Implement with security checks
- [config.json](config.json) — Add `http_fetch_config` section

---

### 5. Write-Ops Team Gating – Identity Model

**Issue:** Plan references `CURRENT_USER_TEAMS`, but MCP servers don't provide built-in user identity.

**Fix for v0.2.0:**

**Keep it simple — no team gating in v0.2.0:**
- Only: `AKR_ENABLE_WRITE_OPS=false` (default) + per-call `allowWrites=true`
- No attempted user/team validation

**Remove from [src/server.py](src/server.py):**
- ❌ Delete: `WRITE_OPS_ALLOWED_TEAMS` env var parsing
- ❌ Delete: `CURRENT_USER_TEAMS` variable

**Simplified [src/tools/write_operations.py](src/tools/write_operations.py):**
```python
async def write_documentation(
    doc_path: str,
    content: str,
    mode: str = "dry-run",  # Default to dry-run (returns diff, no file write)
    allowWrites: bool = False,
    ...
) -> Dict:
    """Write doc with per-call confirmation; no team gating in v0.2.0.
    
    Default behavior: dry-run mode returns unified diff only.
    Only writes to file when mode="feature-branch" (aligns with VS Code review UI).
    """
    
    # Check 1: Environment flag
    if not os.getenv('AKR_ENABLE_WRITE_OPS', 'false').lower() == 'true':
        raise PermissionError(
            "Write operations are disabled by default. "
            "Set AKR_ENABLE_WRITE_OPS=true to enable."
        )
    
    # Check 2: Explicit per-call confirmation (required even in dry-run mode)
    if not allowWrites:
        raise PermissionError(
            "Write operations require explicit allowWrites=true. "
            "This prevents accidental modifications."
        )
    
    # (No team gating in v0.2.0)
    
    # Determine behavior based on mode
    if mode == "dry-run":
        # Return unified diff without writing
        diff = generate_unified_diff(original_content, content)
        return {
            "success": True,
            "mode": "dry-run",
            "diff": diff,
            "message": "Dry-run mode: no file written. Review diff and use mode='feature-branch' to write."
        }
    elif mode == "feature-branch":
        # Actually write to file (VS Code review UI context)
        return await enforce_and_fix(doc_path, content, ...)
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'dry-run' or 'feature-branch'.")
```

**Roadmap for v0.3.0:**

Deferred options (document in [SECURITY.md](SECURITY.md)):
- **Option A**: Git author email (read from `git config user.email`; allow-list in config)
- **Option B**: Signed JWT token passed in tool call (requires explicit setup)
- **Option C**: VS Code workspace settings (future; requires extension integration)

**Files to update:**
- [src/server.py](src/server.py) — Remove team gating references
- [src/tools/write_operations.py](src/tools/write_operations.py) — Simplify permission checks
- [SECURITY.md](SECURITY.md) — Document v0.3.0 roadmap for team gating

---

### 6. Front-Matter JSON Schema in Manifest

**Issue:** Plan mentions front-matter validation but doesn't show the actual JSON Schema or field validation logic.

**Action (coordinate with [core-akr-templates](https://github.com/reyesmelvinr-emr/core-akr-templates)):**

Extend `TEMPLATE_MANIFEST.json` to include front-matter schema per template:

**In core-akr-templates repo:**
```json
{
  "version": "1.3.0",
  "templates": [
    {
      "id": "lean_baseline_service_template",
      "version": "1.3.0",
      "sections": [
        {"name": "Quick Reference", "level": 2, "required": true},
        {"name": "What & Why", "level": 2, "required": true}
      ],
      "frontmatterSchema": {
        "type": "object",
        "required": ["templateId", "project", "repo", "generatedAtUTC"],
        "properties": {
          "templateId": {
            "type": "string",
            "enum": ["lean_baseline_service_template"]
          },
          "templateVersion": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+\\.\\d+$"
          },
          "project": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
          },
          "repo": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$"
          },
          "branch": {
            "type": "string",
            "minLength": 1
          },
          "commitSha": {
            "type": "string",
            "pattern": "^[a-f0-9]{7,40}$"
          },
          "generator": {
            "type": "string",
            "enum": ["akr-mcp-server"]
          },
          "generatorVersion": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+\\.\\d+$"
          },
          "generatedAtUTC": {
            "type": "string",
            "format": "date-time"
          }
        }
      }
    }
  ]
}
```

**In [src/tools/validation_library.py](src/tools/validation_library.py):**

```python
import jsonschema

class ValidationEngine:
    def validate(...) -> ValidationResult:
        violations = []
        
        # ... existing checks ...
        
        # NEW: Validate front matter against schema from manifest
        if parsed.frontmatter:
            schema = self.template_resolver.manifest.get(
                "templates", [{}]
            )[0].get("frontmatterSchema", {})
            
            try:
                jsonschema.validate(parsed.frontmatter, schema)
            except jsonschema.ValidationError as e:
                violations.append(Violation(
                    type="invalid_frontmatter",
                    severity="BLOCKER",
                    field=e.path[0] if e.path else "root",
                    message=f"Front matter validation failed: {e.message}",
                    suggestion=f"Check YAML field '{e.path[0]}': {e.validator}",
                    auto_fixable=False
                ))
```

**Files to update:**
- [src/tools/validation_library.py](src/tools/validation_library.py) — Add front-matter schema validation
- [requirements.txt](requirements.txt) — Add `jsonschema>=4.0.0`

---

### 7. Resource Templates for Dynamic URIs

**Issue:** Clients should know how to construct template URIs without enumerating all templates.

**Fix:**

In [src/server.py](src/server.py), expose a **resource template**:

```python
@server.list_resource_templates()
async def list_resource_templates():
    """Expose resource templates for dynamic URI construction."""
    return [
        ResourceTemplate(
            uriTemplate="akr://template/{id}",
            name="AKR Documentation Templates",
            description="Access AKR templates by ID (e.g., akr://template/lean_baseline_service_template)"
        ),
        ResourceTemplate(
            uriTemplate="akr://charter/{domain}",
            name="AKR Charters",
            description="Access AKR charters by domain (backend, ui, database)"
        )
    ]
```

This allows Copilot Chat to discover `akr://template/lean_baseline_service_template` without seeing the full list first.

**Files to update:**
- [src/server.py](src/server.py) — Add `@server.list_resource_templates()` handler

---

### 8. Parser Implementation Decisions

**Issue:** Plan leaves document parsing methods as placeholders. Need to decide on parser approach.

**Parser Decision Matrix:**

| Parser | Pros | Cons | Recommendation |
|--------|------|------|-----------------|
| **markdown-it-py** | Full AST; handles modern Markdown; JS port (stable) | ~50KB library | ✅ **Upgrade path (v0.3.0)** |
| **Python-Markdown** | Native Python; simple API | Weaker on modern Markdown | Use as fallback |
| **Regex + heading walk** | Minimal deps; fast for MVP | Fragile on formatting edge cases | ✅ **v0.2.0 MVP approach** |

**v0.2.0 (MVP) Implementation:**

Use simple regex-based heading extraction + word count:

```python
import re

class DocumentParser:
    @staticmethod
    def parse(content: str) -> ParsedDocument:
        """Parse Markdown with YAML frontmatter (regex-based MVP)."""
        
        # Split frontmatter from content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_str = parts[1]
                body = parts[2]
            else:
                frontmatter_str = ""
                body = content
        else:
            frontmatter_str = ""
            body = content
        
        # Parse YAML frontmatter
        frontmatter = {}
        if frontmatter_str.strip():
            try:
                frontmatter = yaml.safe_load(frontmatter_str)
            except yaml.YAMLError:
                pass
        
        # Extract sections (##  and ### headings; enforce ## order at top level)
        sections = {}
        section_order = []
        subsection_order = {}
        current_section = None
        current_subsection = None
        
        for line in body.split("\n"):
            # Skip fenced code blocks (detect ``` markers)
            if line.startswith("```"):
                # TODO: Track code block state; skip content inside
                continue
            
            # Match ## Heading (level 2) - top-level sections, enforce order
            match_h2 = re.match(r"^## (.+)$", line)
            if match_h2:
                section_name = match_h2.group(1).strip()
                sections[section_name] = ""
                section_order.append(section_name)
                subsection_order[section_name] = []
                current_section = section_name
                current_subsection = None
            # Match ### Heading (level 3) - subsections
            elif re.match(r"^### (.+)$", line):
                if current_section:
                    subsection_name = re.match(r"^### (.+)$", line).group(1).strip()
                    if current_section in subsection_order:
                        subsection_order[current_section].append(subsection_name)
                    current_subsection = subsection_name
            # Match Markdown table divider (|---|) - explicit table recognition
            elif "|---" in line and current_section:
                sections[current_section] += "[TABLE]\n"
            elif current_section:
                sections[current_section] += line + "\n"
        
        return ParsedDocument(
            frontmatter=frontmatter,
            sections=sections,
            section_order=section_order,
            body=body
        )
    
    @staticmethod
    def calculate_completeness(sections: Dict[str, str]) -> float:
        """Estimate % of sections filled (MVP heuristic)."""
        if not sections:
            return 0.0
        
        filled = 0
        for section_content in sections.values():
            # Skip content inside fenced code blocks when counting
            # (Remove lines between ``` markers)
            cleaned_content = section_content
            cleaned_content = re.sub(r'```[^`]*```', '', cleaned_content, flags=re.DOTALL)
            
            word_count = len(cleaned_content.split())
            has_table = "[TABLE]" in section_content or "|" in section_content  # Explicit table check
            has_list = "\n-" in section_content or "\n*" in section_content
            
            # Section is "filled" if it has >50 words, or table/list present
            if word_count > 50 or has_table or has_list:
                filled += 1
        
        return filled / len(sections)
```

**Parser Edge Cases (v0.2.0 MVP Scope):**
- ✅ Support `##` (level 2) and `###` (level 3) headings
- ✅ Enforce section order on top-level `##` headings
- ✅ Skip fenced code blocks (` ```language ` markers) during word-counting
- ✅ Recognize Markdown tables explicitly (`|…|` + `|---|` dividers)
- ⚠️ Known limitation: Nested subsections not enforced; planned for v0.3.0 AST upgrade

**v0.3.0+ (Enhanced):**

Plan AST-based upgrade (markdown-it-py):
- Full Markdown AST parsing
- Semantic completeness checks (e.g., "API Contract must have table")
- Inline code/link validation

**Files to update:**
- [src/tools/validation_library.py](src/tools/validation_library.py) — Implement MVP parser methods with regex
- [requirements.txt](requirements.txt) — No new dependencies (uses PyYAML already in use)
- [CHANGELOG.md](CHANGELOG.md) — Note: "Parser upgraded to AST-based in v0.3.0"

---

## Refined Phase Breakdown

### Phase 1: Template Externalization & MCP Resources (Days 1–6)

**Corrections applied:**
- ✅ Submodule: Clear cross-OS setup docs + commit-pinning explanation
- ✅ TemplateResolver + TemplateSchemaBuilder: Correct dependency direction
- ✅ MCP resources: Use official SDK types; include resource templates
- ✅ Secure remote fetch: Hash verification, TTL, trusted hosts

**Key deliverables:**

1. **Git submodule setup**
   - Add submodule: `git submodule add https://github.com/reyesmelvinr-emr/core-akr-templates.git templates/core`
   - Pinned to release tag (e.g., `v1.3.0`)
   - Cross-OS docs in [SETUP.md](SETUP.md) / [docs/INSTALLATION_AND_SETUP.md](docs/INSTALLATION_AND_SETUP.md)

2. **[src/resources/akr_resources.py](src/resources/akr_resources.py)** — Refactor
   - `TemplateResolver` class with layered loading:
     - Primary: submodule (`templates/core/`)
     - Fallback: local overrides (`akr_content/templates/`)
     - Optional: HTTP fetch + cache (with security checks)
   - Methods: `get_template()`, `list_templates()`, `get_manifest_version()`
   - No `build_schema()` on resolver (moved to TemplateSchemaBuilder)

3. **[src/tools/template_schema_builder.py](src/tools/template_schema_builder.py)** — Create/enhance
   - `TemplateSchemaBuilder` class (takes `TemplateResolver`)
   - Derives schema from manifest + fallback to file parsing
   - Caches schemas for performance

4. **[src/server.py](src/server.py)** — Add MCP resource handlers
   - `@server.list_resources()` — Enumerate all templates
   - `@server.read_resource(uri)` — Read specific template by URI
   - `@server.list_resource_templates()` — Expose `akr://template/{id}` template
   - Ensure return types match SDK (include `mimeType: text/markdown`)

5. **Documentation**
   - [docs/INSTALLATION_AND_SETUP.md](docs/INSTALLATION_AND_SETUP.md) — Cross-OS submodule setup
   - [docs/VERSION_MANAGEMENT.md](docs/VERSION_MANAGEMENT.md) — Template update workflow
   - Update [README.md](README.md) with resource discovery section

6. **Cleanup**
   - Delete local template duplicates: [akr_content/templates/](akr_content/templates/)
   - Keep: [akr_content/charters/](akr_content/charters/), [akr_content/guides/](akr_content/guides/)

**Acceptance criteria:**
- [ ] Submodule pinned to tag; `git submodule foreach git log -1` shows correct commit
- [ ] `TemplateResolver` loads templates in priority order (submodule → local → HTTP)
- [ ] MCP resources discoverable; Copilot Chat can list and read templates
- [ ] Resource templates allow clients to construct `akr://template/{id}` URIs
- [ ] [docs/VERSION_MANAGEMENT.md](docs/VERSION_MANAGEMENT.md) has clear update workflow

---

### Phase 2: Write Operations Gating (Days 7–8)

**Corrections applied:**
- ✅ Team gating removed from v0.2.0; deferred to v0.3.0
- ✅ Keep only: env flag + per-call `allowWrites` confirmation

**Key deliverables:**

1. **[src/server.py](src/server.py)** — Update
   - Add: `WRITE_OPS_ENABLED = os.getenv('AKR_ENABLE_WRITE_OPS', 'false').lower() == 'true'`
   - Remove: `WRITE_OPS_ALLOWED_TEAMS`, `CURRENT_USER_TEAMS`
   - Conditional tool registration: only register write tools if flag is true
   - Log on startup: "Write operations: ENABLED" or "DISABLED (default)"

2. **[src/tools/write_operations.py](src/tools/write_operations.py)** — Simplify
   - `write_documentation()` signature includes `allowWrites: bool = False`
   - Check 1: Environment flag disabled → raise `PermissionError`
   - Check 2: `allowWrites == False` → raise `PermissionError`
   - Remove all team/identity checks

3. **[src/tools/tool_schemas.py](src/tools/tool_schemas.py)** — Add/update
   - `WriteDocumentationInput` with `allowWrites: bool` field (default=False)
   - Clear docstring: "MUST be True to prevent accidental writes"

4. **[SECURITY.md](SECURITY.md)** — Create (NEW)
   - MCP trust model (stdio → secure; HTTP → auth required)
   - MCP Inspector version guidance (≥0.14.1 for CVE fix)
   - Write operations: "off by default, per-call approval required"
   - VS Code tool approval workflow
   - Deferred roadmap: "v0.3.0 team gating via Git author or JWT token"

5. **[README.md](README.md)** — Update
   - "Write Operations (Disabled by Default)" section
   - Example: `write_documentation(..., allowWrites=true)`
   - Link to [SECURITY.md](SECURITY.md)

**Acceptance criteria:**
- [ ] `AKR_ENABLE_WRITE_OPS=false` by default; write tools not registered
- [ ] `write_documentation(..., allowWrites=false)` raises error with clear message
- [ ] `write_documentation(..., allowWrites=true)` proceeds (with env flag enabled)
- [ ] [SECURITY.md](SECURITY.md) documents MCP trust, Inspector versions, future roadmap
- [ ] Users understand write ops are "off by default" from README

---

### Phase 3: Dual-Faceted Validation (Days 9–13)

**Corrections applied:**
- ✅ Schema dependency fixed: `ValidationEngine` → `TemplateSchemaBuilder` → `TemplateResolver`
- ✅ Front-matter JSON Schema from manifest + `jsonschema` validation
- ✅ Parser decisions made: regex-based v0.2.0, AST v0.3.0+

**Key deliverables:**

1. **[src/tools/validation_library.py](src/tools/validation_library.py)** — Create (NEW)
   - Core validation shared by MCP tool + CLI
   - `Violation` dataclass: `{type, severity, field, message, suggestion, auto_fixable, field_path, validator}`
   - `ValidationResult` dataclass: `{is_valid, violations, auto_fixed_content, metadata, diff}`
   - `ValidationEngine` class:
     - Constructor: `__init__(schema_builder: TemplateSchemaBuilder, config: Dict)`
     - `validate(doc_content, template_id, tier_level, auto_fix, dry_run=True) -> ValidationResult`
     - Checks:
       - YAML frontmatter presence (BLOCKER if missing)
       - YAML schema validation (against manifest, using `jsonschema`; include field_path + validator in violation)
       - Section presence (BLOCKER or FIXABLE per tier)
       - Section order (BLOCKER or FIXABLE per tier)
       - Completeness (WARN or FIXABLE per tier)
     - Auto-fix methods:
       - `_auto_fix(content, violations) -> str` — return patched content
       - `_generate_diff(original, patched) -> str` — unified diff for dry-run mode
   - Provenance metadata:
     - Return `metadata: {templateSource, templateCommit, timestamp}`
     - `templateSource`: "submodule"|"local-override"|"remote-preview"
   - Parser methods:
     - `DocumentParser.parse(content) -> ParsedDocument`
     - `_calculate_completeness(sections) -> float` — word count + table/list heuristics
   - Tier-based thresholds:
     - TIER_1 (strict): BLOCKER for missing sections, wrong order; ≥80% completeness
     - TIER_2 (moderate): FIXABLE for missing sections; ≥60% completeness
     - TIER_3 (lenient): FIXABLE for missing sections; ≥30% completeness

2. **[src/server.py](src/server.py)** — Add MCP tool
   - Real `validate_documentation` tool (not placeholder)
   - Input: `doc_path, template_id, tier_level, dry_run=true` (from `ValidateDocumentationInput`)
   - Output: `{success, is_valid, violations, suggestions, auto_fixed_content, diff, metadata}`
   - Default behavior: `dry_run=true` (returns structured diff, no file write); only returns patched content (not file writes)
   - For writing to file: caller must invoke separate `write_documentation` tool with patched content

3. **[src/tools/tool_schemas.py](src/tools/tool_schemas.py)** — Add/update
   - `ValidateDocumentationInput`: `doc_path, template_id, tier_level`
   - `ViolationSchema`: `type, severity, field, message, suggestion, auto_fixable`
   - `ValidateDocumentationOutput`: `success, is_valid, violations, suggestions, auto_fixed_content, metadata`

4. **[scripts/akr_validate.py](scripts/akr_validate.py)** — Create CLI
   - Entry point: `python scripts/akr_validate.py --doc <path> --template <id> --tier <TIER_1|2|3>`
   - Options: `--output {json|text}`, `--auto-fix`
   - Output: JSON for CI parsing, or human-readable text
   - Exit code: 0 if valid, 1 if invalid

5. **[requirements.txt](requirements.txt)** — Update
   - Add: `jsonschema>=4.0.0`

6. **[docs/VALIDATION_GUIDE.md](docs/VALIDATION_GUIDE.md)** — Create (NEW)
   - Explanation of validation tiers
   - Tier 1 vs. 2 vs. 3 use cases
   - Auto-fix capabilities
   - How to use `validate_documentation` MCP tool from Copilot Chat
   - How to use `akr-validate` CLI locally

**Acceptance criteria:**
- [ ] `ValidationEngine` correctly wired to `TemplateSchemaBuilder`
- [ ] YAML front matter validated against JSON Schema from manifest
- [ ] Tier levels control violation severity (BLOCKER vs. FIXABLE vs. WARN)
- [ ] MCP tool `validate_documentation` callable from Copilot Chat
- [ ] CLI `akr-validate` produces consistent results (same as MCP tool)
- [ ] Auto-fix capable tools return patched content (not file writes)

---

### Phase 4: Extractor Deprecation & Cleanup (Days 14–20)

**No corrections needed — plan is solid.**

**Key deliverables:**

1. **[src/tools/code_analytics.py](src/tools/code_analytics.py)** — Create (NEW)
   - `CodeAnalyzer` class: unified interface for language-specific extraction
   - Methods:
     - `detect_language() -> str` — Detect primary language
     - `extract_methods() -> List[Dict]` — Public methods/functions
     - `extract_classes() -> List[Dict]` — Class/interface definitions
     - `extract_imports() -> List[str]` — External dependencies
     - `extract_sql_tables() -> List[Dict]` — SQL schema
   - Composition: Uses existing extractors (CSharpExtractor, SQLExtractor)

2. **[src/server.py](src/server.py)** — Register & cleanup
   - Register new tool: `extract_code_context`
   - Input: `repo_path, extraction_types, language, file_filter`
   - Output: `{methods, classes, imports, sql_schema, metadata: {language_detected, partial, timestamp, server_version}}`
   - Remove: `analyze_codebase` tool (deprecated)
   - Comment out: deprecated tool registrations

3. **Deprecation headers** — Add to extractor files:
   - [src/tools/extractors/typescript_extractor.py](src/tools/extractors/typescript_extractor.py)
   - [src/tools/extractors/business_rule_extractor.py](src/tools/extractors/business_rule_extractor.py)
   - [src/tools/extractors/failure_mode_extractor.py](src/tools/extractors/failure_mode_extractor.py)
   - [src/tools/extractors/method_flow_analyzer.py](src/tools/extractors/method_flow_analyzer.py)
   - [src/tools/extractors/example_extractor.py](src/tools/extractors/example_extractor.py)

   Header template:
   ```python
   """
   ⚠️ DEPRECATED in v0.2.0
   
   This extractor uses [reason: heuristic-based/regex/speculative].
   For better results, use Copilot Chat with code context + charters.
   
   This module will be removed in v1.0.0.
   """
   ```

4. **Test updates**
   - Mark skipped tests with `@pytest.mark.skip(reason="...")`
   - Tests for deprecated tools: remove or mark skip

5. **[CHANGELOG.md](CHANGELOG.md)** — Create (NEW)
   - v0.2.0 section:
     - Added: Submodule, resources, validation, extraction, gating, security
     - Changed: `analyze_codebase` → `extract_code_context`, validation moved to shared library
     - Deprecated: List all deprecated extractors + migration guidance
     - Removed: Local template copies, placeholder tools

**Acceptance criteria:**
- [ ] `extract_code_context` works with C# and SQL repos
- [ ] Returns `{methods, classes, imports, metadata}` (no 🤖/❓ markers)
- [ ] Deprecated extractors have clear warning headers
- [ ] Deprecated tools removed from server registration
- [ ] Tests for deprecated tools marked with skip reason
- [ ] [CHANGELOG.md](CHANGELOG.md) provides migration guidance

---

### Phase 5: Testing & Documentation (Days 21–25)

**Key deliverables:**

1. **New test files:**

   - **[tests/test_template_resolver.py](tests/test_template_resolver.py)**
     - Submodule loading (templates/core/)
     - Local override priority
     - Optional HTTP fetch + cache
     - Secure hash verification
     - TTL expiry

   - **[tests/test_mcp_resources.py](tests/test_mcp_resources.py)** (NEW)
     - Resource list handler (`@server.list_resources()`)
     - Resource read handler (`@server.read_resource()` by URI)
     - Resource templates discovery (`@server.list_resource_templates()`)
     - Correct MIME types (`text/markdown`)
     - FastMCP return types verified: `mimeType`, `uri`, `text` fields present
     - Pagination support for `list_resources()` (even if unused in v0.2.0)

   - **[tests/test_validation_library.py](tests/test_validation_library.py)**
     - YAML front matter validation (with JSON Schema)
     - Section presence & order checks
     - Completeness calculation
     - Tier-based violation severity
     - Auto-fix capability

   - **[tests/test_extract_code_context.py](tests/test_extract_code_context.py)**
     - Extraction with C# sample (methods, classes)
     - Extraction with SQL sample (tables)
     - Language detection
     - Partial flag when incomplete

   - **[tests/test_cli_akr_validate.py](tests/test_cli_akr_validate.py)**
     - CLI output: JSON format
     - CLI output: text format
     - Exit codes (0=valid, 1=invalid)
     - `--auto-fix` flag

   - **[tests/test_integration_e2e.py](tests/test_integration_e2e.py)** (NEW)
     - Full flow: extract → get_charter → validate → write
     - Submodule → resource discovery → doc generation → validation
     - Audit trail creation

2. **Documentation updates:**

   - **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Major update
     - v0.2.0 design shift (template provider + validator, not generator)
     - MCP resources + tools diagram
     - Component dependencies
     - Data flow: extract → charter → Chat → validate → write

   - **[docs/COPILOT_CHAT_WORKFLOW.md](docs/COPILOT_CHAT_WORKFLOW.md)** (NEW)
     - Step-by-step: extract code context
     - Review charter
     - Ask Chat to draft doc
     - Validate with `validate_documentation`
     - Refine in Chat
     - Write to disk with `write_documentation`
     - Tips for tier levels, validation, security

   - **Update [README.md](README.md)**
     - Simplify tool list (active, deprecated, removed)
     - Link to workflows and guides
     - Quick start for submodule setup
     - Security/trust section

3. **Coverage verification**
   - Run: `pytest --cov=src --cov-report=html`
   - Target: ≥80% coverage maintained
   - Report: [htmlcov/index.html](htmlcov/index.html)

**Acceptance criteria:**
- [ ] All new tests pass (unit + integration)
- [ ] MCP resource handlers tested and spec-compliant
- [ ] CLI tool tested for output formats
- [ ] Coverage ≥80%
- [ ] [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) reflects v0.2.0 design
- [ ] [docs/COPILOT_CHAT_WORKFLOW.md](docs/COPILOT_CHAT_WORKFLOW.md) provides clear workflow

---

## First PR Checklist (Server-Only, Corrected)

### Pre-Coding Decisions

- [ ] Confirm MCP SDK choice (FastMCP recommended; document in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md))
- [ ] Coordinate with [core-akr-templates](https://github.com/reyesmelvinr-emr/core-akr-templates) to add `frontmatterSchema` to manifest
- [ ] Decide on Markdown parser (recommend regex-walk v0.2.0, upgrade to markdown-it-py v0.3.0+)
- [ ] Review MCP spec for resource templates and ensure SDK supports them

### Phase 1: Submodule + Resources

- [ ] Add Git submodule: `git submodule add https://github.com/reyesmelvinr-emr/core-akr-templates.git templates/core`
- [ ] Pin to release tag (e.g., `v1.3.0`)
- [ ] Implement `TemplateResolver` with layered loading (submodule → local → HTTP)
- [ ] Add secure HTTP fetch (hash verification, trusted hosts, TTL)
- [ ] Implement `TemplateSchemaBuilder` with manifest parsing
- [ ] Wire MCP resource handlers (list, read, resource templates) using SDK
- [ ] Create [docs/INSTALLATION_AND_SETUP.md](docs/INSTALLATION_AND_SETUP.md) — cross-OS submodule setup
- [ ] Create [docs/VERSION_MANAGEMENT.md](docs/VERSION_MANAGEMENT.md) — template update workflow
- [ ] Remove local template copies ([akr_content/templates/](akr_content/templates/))
- [ ] Test: Submodule present, templates discoverable as MCP resources, resource templates work

### Phase 2: Write Gating

- [ ] Add `AKR_ENABLE_WRITE_OPS` env flag with default `false`
- [ ] Implement conditional tool registration (write tools only if flag true)
- [ ] Remove team gating references from code
- [ ] Simplify `write_documentation` permission checks (env flag + allowWrites param only)
- [ ] Create [SECURITY.md](SECURITY.md) with trust model, Inspector version, future roadmap
- [ ] Update [README.md](README.md) with "Write Operations (Disabled by Default)" section
- [ ] Test: Tools not registered when disabled, error raised when allowWrites=false

### Phase 3: Validation

- [ ] Extract validation core to [src/tools/validation_library.py](src/tools/validation_library.py)
- [ ] Implement `ValidationEngine` with corrected schema dependency
- [ ] Implement parser: YAML frontmatter, section extraction, completeness calc
- [ ] Add front-matter JSON Schema validation using `jsonschema` library
- [ ] Implement auto-fix methods (return patched content)
- [ ] Expose as MPC tool `validate_documentation` in [src/server.py](src/server.py)
- [ ] Create CLI [scripts/akr_validate.py](scripts/akr_validate.py)
- [ ] Add `jsonschema>=4.0.0` to [requirements.txt](requirements.txt)
- [ ] Create [docs/VALIDATION_GUIDE.md](docs/VALIDATION_GUIDE.md)
- [ ] Test: Validation tiers work, MCP tool + CLI return same results, auto-fix works

### Phase 4: Extractors

- [ ] Implement `CodeAnalyzer` in [src/tools/code_analytics.py](src/tools/code_analytics.py)
- [ ] Register `extract_code_context` tool in [src/server.py](src/server.py)
- [ ] Remove `analyze_codebase` from tool registration
- [ ] Add deprecation headers to: typescript, business_rule, failure_mode, method_flow, example extractors
- [ ] Mark deprecated tool tests with `@pytest.mark.skip(reason="...")`
- [ ] Test: Extraction works, returns clean JSON, metadata.partial flag works

### Phase 5: Tests & Docs

- [ ] Create all new test files: template_resolver, mcp_resources, validation_library, extract_context, cli, integration
- [ ] Run: `pytest --cov=src` → coverage ≥80%
- [ ] Update [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) with v0.2.0 design
- [ ] Create [docs/COPILOT_CHAT_WORKFLOW.md](docs/COPILOT_CHAT_WORKFLOW.md)
- [ ] Create [CHANGELOG.md](CHANGELOG.md) with v0.2.0 release notes
- [ ] Test: All integration tests pass, coverage maintained

### General Checks

- [ ] No Windows-specific paths in documentation (use repo-relative paths)
- [ ] Cross-OS commands in setup guides
- [ ] Deprecation messages clear + migration guidance in CHANGELOG
- [ ] MCP resource URIs consistent (akr://template/*, akr://charter/*)
- [ ] Error messages actionable (suggest fixes)

---

## Key Decisions Finalized

| Decision | Resolution | Rationale |
|----------|-----------|-----------|
| **Dependency wiring** | `ValidationEngine` → `TemplateSchemaBuilder` → `TemplateResolver` | Correct direction; builder depends on resolver, validator depends on builder |
| **MCP SDK** | Use official Python SDK (FastMCP recommended) with confirmed decorators | Ensure compliance with spec; resource handlers must match SDK types |
| **Submodule behavior** | Pin to commit via tag; document no auto-update | Provides stable, reproducible template versions; user controls updates |
| **Remote fetch security** | Hash verification + trusted hosts + TTL + pinned version | Prevent TOCTOU, injection, drift; fail closed if verification fails |
| **Team gating v0.2.0** | Removed; env flag + per-call confirmation only | Simplifies implementation; deferred to v0.3.0 (Git author / JWT options) |
| **Markdown parser v0.2.0** | Regex-based heading walk + word count heuristics | Minimal deps for MVP; upgrade to markdown-it-py AST in v0.3.0 |
| **Front-matter validation** | JSON Schema from manifest + `jsonschema` library | Deterministic, field-level validation; matches manifest structure |
| **Resource templates** | Expose `akr://template/{id}` pattern to clients | Allows dynamic URI construction without enumerating all templates |
| **Write-ops experience v0.2.0** | Off by default + per-call `allowWrites=true` + env flag | Least privilege; aligns with VS Code security guidance |
| **Extractor simplification** | Keep C#/SQL (deterministic); deprecate TypeScript, business rules, flows, examples | Reduce maintenance; let Copilot Chat handle semantic analysis |

---

## Effort & Risk Summary

### Effort Breakdown

| Phase | Days | Focus |
|-------|------|-------|
| **Phase 1** | 6 | Submodule setup, template resolution, MCP resources |
| **Phase 2** | 2 | Write-ops gating, security documentation |
| **Phase 3** | 5 | Validation core, dual APIs (MCP + CLI), front-matter schema |
| **Phase 4** | 7 | Extractor cleanup, code analytics, deprecation |
| **Phase 5** | 5 | Testing, documentation, integration |
| **Total** | **25** | Full server-side refactor |

### Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Submodule merge conflicts on template updates | Medium | Clear workflow docs; coordinate updates; tag-based pinning avoids drift |
| MCP SDK exact types hard to match | Medium | Pre-code: confirm SK choice + decorators; review spec early; test resource handlers first |
| Regex parser fragile on formatting edge cases | Medium | Good test coverage; document limitations in v0.2.0; plan AST upgrade for v0.3.0 |
| Front-matter schema coordination | Medium | Coordinate with core-akr-templates early; include in manifest PR |
| Write-ops identity gap deferred | Low | Clear roadmap in SECURITY.md for v0.3.0; current model (env + allowWrites) sufficient |
| Cross-OS path issues in docs | Low | Use repo-relative paths only; test with macOS/Linux contributors |
| Test coverage gap | Low | Write tests for each component; target ≥80%; tools support coverage reports |

### Risks Mitigated vs. Original Plan

✅ Schema dependency bug → Fixed (ValidationEngine → SchemaBuilder → Resolver)  
✅ MCP SDK compliance → Fixed (confirm exact decorators + types)  
✅ Security holes → Fixed (no identity gap, secure HTTP with verification, team gating deferred + documented)  
✅ Cross-OS confusion → Fixed (repo-relative paths, example workflows)  
✅ Parser ambiguity → Fixed (regex MVP + AST v0.3.0 plan clear)  

---

## Integration Points

### External Dependencies

| Dependency | Version | Purpose | Notes |
|------------|---------|---------|-------|
| **mcp** | >=1.0.0 | MCP Python SDK | Confirm FastMCP or low-level; decorators must match |
| **Jinja2** | >=3.0.0 | Template rendering | Already in use; no change |
| **PyYAML** | >=6.0.1 | YAML parsing | Already in use; no change |
| **jsonschema** | >=4.0.0 | JSON Schema validation | NEW; for front-matter validation |
| **python-json-logger** | >=2.0.0 | Structured logging | Already in use; no change |
| **pytest**, **pytest-cov** | Latest | Testing | Already in use; no change |

### External Repos

| Repo | Role | Integration |
|------|------|-----------|
| **[core-akr-templates](https://github.com/reyesmelvinr-emr/core-akr-templates)** | Template SSoT | Git submodule pinned to release tag; runtime loading + HTTP preview (optional) |

### GitHub Actions (Deferred to Separate Phase)

- Not in scope for server-side v0.2.0
- Planned: CI gates (markdownlint, front-matter schema, template conformance, audit)
- Will integrate with [src/tools/validation_library.py](src/tools/validation_library.py) once server is ready

---

## Testing Strategy

### Test Matrix

| Level | Coverage | Examples |
|-------|----------|----------|
| **Unit** | Core modules in isolation | Parser, schema builder, validators |
| **Integration** | Multi-module flows | Submodule → resource discovery, extraction → validation |
| **E2E** | Full user workflows | Chat → extract → validate → write (fictional scenario) |
| **MCP compliance** | SDK-specific behavior | Resource handlers return correct types, decorators match spec |

### Test Execution

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Run specific test file
pytest tests/test_validation_library.py -v

# Run tests matching pattern
pytest -k "test_extract" -v
```

### Negative Test Cases (Critical for v0.2.0)

Ensure error handling is robust:

- **Malformed YAML front-matter:**
  - Invalid YAML syntax → `Violation` with field `frontmatter`, field_path pointing to specific line, and validator indicating YAML error
  - Missing required fields → `Violation` with field_path `frontmatter.{fieldName}` and schema validator reference

- **Schema validation failures:**
  - Unknown template ID → Return list of valid template IDs in error message
  - Schema mismatch (field type, enum validation) → `Violation` includes field_path and validator name (e.g., "type", "enum", "pattern")

- **Parser edge cases:**
  - Heading order violations (### before ##) → `Violation` for order
  - Missing top-level ## sections → `Violation` for section presence
  - Code blocks breaking section detection → Verify code blocks are properly skipped

### Coverage Target

- **Minimum:** ≥80% (maintain current baseline)
- **Preferred:** ≥85% (new modules)
- **Report:** [htmlcov/index.html](htmlcov/index.html)

---

## Documentation Updates

### Files to Create (NEW)

1. **[IMPLEMENTATION_PLAN_V0.2.0.md](IMPLEMENTATION_PLAN_V0.2.0.md)** — This checklist document
2. **[SECURITY.md](SECURITY.md)** — Trust model, versions, future roadmap
3. **[docs/VERSION_MANAGEMENT.md](docs/VERSION_MANAGEMENT.md)** — Submodule update workflow
4. **[docs/VALIDATION_GUIDE.md](docs/VALIDATION_GUIDE.md)** — Tier levels, validation usage
5. **[docs/COPILOT_CHAT_WORKFLOW.md](docs/COPILOT_CHAT_WORKFLOW.md)** — Step-by-step guide
6. **[CHANGELOG.md](CHANGELOG.md)** — v0.2.0 release notes

### Files to Update

1. **[README.md](README.md)**
   - Tool list (active, deprecated, removed)
   - Write operations section
   - Security/trust callout
   - Submodule setup note

2. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**
   - v0.2.0 design shift (template provider, not generator)
   - MPC resource + tool diagram
   - Component dependencies
   - Data flow diagram

3. **[docs/INSTALLATION_AND_SETUP.md](docs/INSTALLATION_AND_SETUP.md)**
   - Cross-OS submodule setup
   - Verify submodule is present
   - Note about commit pinning

4. **[requirements.txt](requirements.txt)**
   - Add: `jsonschema>=4.0.0`

### Files to Delete

1. **[akr_content/templates/](akr_content/templates/)** — All markdown templates (sourced from submodule now)

### Files to Keep (No Change)

- [akr_content/charters/](akr_content/charters/) — Project-local charter customizations
- [akr_content/guides/](akr_content/guides/) — Project-local guide customizations

---

## Roll-Out Plan

### PR Strategy

**PR 1: Submodule + Resources (Phase 1)**
- Add submodule
- Implement TemplateResolver + TemplateSchemaBuilder
- Add MCP resource handlers
- Update docs for submodule setup
- Remove local template copies
- Tests: template loading, resource discovery

**PR 2: Write Gating + Security (Phase 2)**
- Add AKR_ENABLE_WRITE_OPS flag
- Simplify permission checks
- Create SECURITY.md
- Tests: tool gating, permission errors

**PR 3: Validation Dual-Facet (Phase 3)**
- ValidationEngine + parser
- MCP tool + CLI
- Front-matter schema validation
- Tests: validation, completeness, auto-fix

**PR 4: Extractors (Phase 4)**
- CodeAnalyzer + extract_code_context
- Deprecation headers
- Remove deprecated tools
- Tests: extraction, metadata

**PR 5: Tests + Docs (Phase 5)**
- Integration tests
- Coverage reports
- Update ARCHITECTURE.md
- Create COPILOT_CHAT_WORKFLOW.md
- Create CHANGELOG.md

### Release

After all PRs merge:
1. Create VERSION file → `0.2.0`
2. Tag commit: `git tag v0.2.0`
3. Push tag: `git push origin v0.2.0`
4. GitHub Actions publishes release (setup in future phase)

---

## Appendix: Quick Reference

### Core Dependencies

```
ValidationEngine
├─ TemplateSchemaBuilder
│  └─ TemplateResolver
│     ├─ File: templates/core/ (submodule)
│     ├─ File: akr_content/ (local overrides)
│     └─ HTTP: optional HTTP fetch (disabled by default)
└─ DocumentParser
   ├─ YAML front-matter parsing (PyYAML)
   └─ Section extraction (regex MVP)
```

### MCP Resources Exposed

| URI Pattern | Description | Handler |
|-------------|-------------|---------|
| `akr://template/{id}` | Template content | `@server.read_resource()` |
| `akr://charter/{domain}` | Charter content | Future |
| Template pattern | Dynamic template discovery | `@server.list_resource_templates()` |

### MCP Tools Exposed

| Tool | Status | Input | Output |
|------|--------|-------|--------|
| `extract_code_context` | ✅ Active | repo_path, types, lang | methods, classes, imports, metadata |
| `validate_documentation` | ✅ Active | doc_path, template_id, tier | violations, suggestions, auto_fixed_content |
| `get_charter` | ✅ Active | domain | charter_content |
| `write_documentation` | ⚠️ Gated | doc_path, content, allowWrites | success, audit_entry |
| `update_documentation_sections` | ⚠️ Gated | doc_path, sections, allowWrites | success, audit_entry |
| `analyze_codebase` | ❌ Deprecated | — | — |

### Environment Variables

| Var | Default | Notes |
|-----|---------|-------|
| `AKR_ENABLE_WRITE_OPS` | `false` | Enable write operations (v0.2.0: env flag only) |
| `AKR_SKIP_INITIALIZATION` | `false` | Skip heavyweight startup (for fast mode) |
| `AKR_FAST_MODE` | `false` | Lazy-load resources on first use |

### Config Keys

```json
{
  "enforcement": {
    "enabled": true,
    "validationStrictness": "baseline"
  },
  "http_fetch_enabled": false,
  "http_fetch_config": {
    "repo_url": "https://github.com/reyesmelvinr-emr/core-akr-templates",
    "cache_ttl_seconds": 86400,
    "verify_checksums": true
  }
}
```

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Feb 23, 2026 | Melvin Reyes + M365 Copilot | Initial: consolidated both assessments; 8 critical corrections |

---

**Status:** ✅ Ready for Implementation  
**Next Step:** Confirm pre-coding decisions (SDK choice, parser, coordination); start Phase 1

