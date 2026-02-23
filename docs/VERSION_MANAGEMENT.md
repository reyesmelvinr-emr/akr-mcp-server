# Version Management Guide

## Overview

This guide covers how AKR manages template versions and how to safely update templates used by the MCP server.

**Starting with v0.2.0**, templates are managed via Git submodule (`templates/core`) and pinned to specific version tags in `core-akr-templates` repository. This ensures reproducible documentation generation across team members and CI/CD pipelines.

---

## Key Concepts

### Template Versions

Templates are released from the [core-akr-templates](https://github.com/reyesmelvinr-emr/core-akr-templates) repository with semantic versioning:

- **v1.0.0** — Major breaking changes to template structure
- **v1.1.0** — New templates or backward-compatible enhancements
- **v1.1.1** — Bug fixes, typo corrections

See the [core-akr-templates releases](https://github.com/reyesmelvinr-emr/core-akr-templates/releases) page for the changelog.

### Submodule Pins

The `akr-mcp-server` repository pins `templates/core` to a **specific Git commit** (usually via tag). This means:

✅ **Good:**
- All team members use identical templates
- CI/CD generates reproducible docs
- No surprises from auto-updated dependencies
- Easy to rollback if a new version breaks something

❌ **Not good:**
- Templates won't auto-update (you must manually pin new versions)
- Requires deliberate update workflow
- Old templates may have bugs until you manually update

---

## Checking Current Template Version

### View Submodule Commit

```bash
# Show the current commit hash in templates/core
git submodule foreach git log -1 --oneline

# Output example:
# templates/core
# a1b2c3d (HEAD -> main, tag: v1.1.0) docs: update template for service documentation
```

The last part (`v1.1.0` or `a1b2c3d`) is the pinned version.

### Check TEMPLATE_MANIFEST.json

The manifest inside templates/core shows available templates:

```bash
cat templates/core/TEMPLATE_MANIFEST.json
```

**Example structure:**
```json
{
  "version": "1.1.0",
  "templates": {
    "lean_backend_service": {
      "version": "1.1.0",
      "path": "templates/lean_backend_service.md",
      "sha256": "abc123..."
    }
  }
}
```

---

## Updating Templates to a New Version

### Step 1: Check Available Updates

```bash
cd templates/core

# Fetch latest tags from upstream
git fetch origin --tags

# List available versions
git tag | sort -V | tail -10

# View changes in a specific version
git log v1.0.0..v1.1.0 --oneline
```

### Step 2: Review What's Changing

Before updating, review the changelog:

```bash
# Show full changelog for a version range
git log v1.0.0..v1.1.0

# Or check GitHub releases:
# https://github.com/reyesmelvinr-emr/core-akr-templates/releases/tag/v1.1.0
```

**Look for:**
- ✅ Bug fixes you need
- ⚠️ Breaking changes (may affect your documentation)
- ⚠️ New templates you might want to use

### Step 3: Pin the New Version

Update the submodule to point to the new version tag:

```bash
cd templates/core
git checkout v1.1.0    # Replace with desired version
cd ../..

# Verify the update
git submodule foreach git log -1 --oneline
# Output: templates/core
#         abc123d (HEAD -> main, tag: v1.1.0) ...
```

### Step 4: Commit the Update

```bash
# Stage the submodule bump
git add templates/core

# Commit with version reference
git commit -m "chore: update templates to v1.1.0

- Fix: correct formatting in lean_backend_service template
- Feature: new enum_values template for data modeling"

# Push to your branch
git push origin your-branch
```

### Step 5: Verify in Your Project

```bash
# Verify the resolver can load templates
python -c "
from src.resources.template_resolver import create_template_resolver
resolver = create_template_resolver('.', {})
templates = resolver.list_templates()
print(f'✅ Loaded {len(templates)} templates')
print(f'Manifest version: {resolver.get_manifest_version()}')
"
```

**Expected output:**
```
✅ Loaded 15 templates
Manifest version: v1.1.0
```

### Step 6: Submit Pull Request

```bash
# Create PR with version bump details
# Title: "chore: update templates to v1.1.0"
# Description: Link the core-akr-templates changelog
```

---

## Handling Breaking Changes

If a template update includes **breaking changes**, you may need to regenerate documentation:

### Identify Impacted Docs

```bash
# Find docs using the affected template
grep -r "template: old_template_name" docs/

# Or search for section headers that might have changed
grep -r "## Validation Rules" docs/ | head -5
```

### Regenerate Affected Documentation

```bash
# Use the AKR generation tools to regenerate with new template
python scripts/generate_and_write_documentation.py \
  --module-name YOUR_MODULE \
  --source-files src/your_module.py

# Or use the VS Code task:
# Press Ctrl+Shift+P → "AKR: Generate and Write Documentation"
```

### Review Changes

```bash
# Check what changed in generated docs
git diff docs/YOUR_MODULE.md | head -50

# If happy, commit:
git add docs/YOUR_MODULE.md
git commit -m "docs: regenerate with new template format (templates v1.1.0)"
```

---

## Rollback Procedure

If a new template version causes problems, revert to the previous version:

### Quick Rollback

```bash
cd templates/core

# List recent versions
git tag | sort -V | tail -5

# Rollback to previous version
git checkout v1.0.0    # Or the stable version hash

cd ../..

# Commit the rollback
git add templates/core
git commit -m "Revert: templates back to v1.0.0

Reason: v1.1.0 introduced breaking changes to service template format"
```

### Hard Reset (Last Resort)

If something went wrong:

```bash
cd templates/core

# Discard any changes
git reset --hard

# Go back to the commit we want
git checkout v1.0.0

cd ../..
```

---

## Automation & CI/CD

### GitHub Actions Workflow (Future)

Once you have a stable template process, consider automating:

```yaml
# .github/workflows/template-updates.yml
name: Check for Template Updates

on:
  schedule:
    - cron: '0 0 * * MON'  # Weekly check on Monday

jobs:
  check-updates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: 'recursive'
      
      - name: Check for new template versions
        run: |
          cd templates/core
          git fetch origin --tags
          LATEST=$(git describe --tags --abbrev=0)
          CURRENT=$(git describe --tags)
          if [ "$LATEST" != "$CURRENT" ]; then
            echo "❗ New template version available: $LATEST"
            exit 1
          fi
```

---

## Best Practices

### DO's ✅

- ✅ **Update regularly** — Check for template updates monthly
- ✅ **Review changelogs** — Understand what's changing before updating
- ✅ **Test in a branch** — Try new templates on a feature branch first
- ✅ **Document breaking changes** — Note them in your commit message
- ✅ **Pin to stable releases** — Use version tags (`v1.1.0`), not floating branches

### DON'Ts ❌

- ❌ **Point to HEAD** — Don't use floating refs like `main` or `master`
- ❌ **Pin to commit hashes** — Use tags instead (more readable)
- ❌ **Update multiple things at once** — Only change templates, not your code
- ❌ **Ignore validation failures** — If tests fail after update, investigate
- ❌ **Merge without review** — Have someone verify template changes

---

## Troubleshooting Version Issues

### Issue: "templates/core detached HEAD"

This means the submodule isn't on a branch. Return to a tag:

```bash
cd templates/core
git checkout v1.1.0    # Attach to tag
cd ../..
git add templates/core
git commit -m "chore: reattach templates submodule to v1.1.0"
```

### Issue: Submodule out of sync with git

```bash
# Resync the submodule
git submodule sync
git submodule update --init --recursive
```

### Issue: TEMPLATE_MANIFEST.json missing

```bash
# Verify submodule is properly initialized
ls -la templates/core/TEMPLATE_MANIFEST.json

# If missing, reinit the submodule
git submodule deinit templates/core
git submodule init
git submodule update --recursive
```

---

## Support & References

- **Core Templates Repo:** [core-akr-templates](https://github.com/reyesmelvinr-emr/core-akr-templates)
- **Releases & Changelog:** [releases page](https://github.com/reyesmelvinr-emr/core-akr-templates/releases)
- **Submodule Docs:** [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- **Installation Help:** [INSTALLATION_AND_SETUP.md](INSTALLATION_AND_SETUP.md#submodule-issues-phase-1---critical)

---

## Quick Reference

| Task | Command |
|------|---------|
| Check current version | `git submodule foreach git log -1 --oneline` |
| List available versions | `cd templates/core && git tag \| sort -V` |
| Update to v1.1.0 | `cd templates/core && git checkout v1.1.0 && cd .. && git add templates/core` |
| Rollback to v1.0.0 | `cd templates/core && git checkout v1.0.0 && cd .. && git add templates/core` |
| View changelog | `git log v1.0.0..v1.1.0 --oneline` |
| Verify templates load | `python -c "from src.resources.template_resolver import create_template_resolver; r = create_template_resolver('.', {}); print(f'{len(r.list_templates())} templates')"` |

---

**Last updated:** 2025-01-14  
**MCP Server Version Requirement:** ≥ 0.2.0  
**Git Minimum:** 2.13+
