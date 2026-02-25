"""BLOCKER 7: Test auto-fix functionality for documentation enforcement."""

import pytest
import os
import tempfile
import subprocess
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.write_operations import write_documentation_async


class TestAutoFix:
    """Test auto-fix functionality in documentation enforcement"""

    @pytest.fixture
    def enable_write_ops(self, monkeypatch):
        """Enable write operations for testing"""
        monkeypatch.setenv("AKR_ENABLE_WRITE_OPS", "true")

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with git initialization"""
        workspace = tempfile.mkdtemp()
        workspace_path = Path(workspace)

        # Initialize git repository
        subprocess.run(["git", "init"], cwd=workspace_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=workspace_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=workspace_path,
            capture_output=True,
        )

        # Create docs directory
        docs_dir = workspace_path / "docs"
        docs_dir.mkdir()

        # Create config.json with enforcement enabled
        config_file = workspace_path / "config.json"
        config_file.write_text(
            """{
  "documentation": {
    "enforcement": {
      "enabled": true
    }
  }
}""",
            encoding="utf-8",
        )

        yield workspace_path

        # Cleanup
        import shutil
        try:
            def handle_remove_readonly(func, path, exc_info):
                import stat
                os.chmod(path, stat.S_IWRITE)
                func(path)
            shutil.rmtree(workspace, onerror=handle_remove_readonly)
        except Exception:
            pass

    @pytest.fixture
    def enforce_config(self):
        """Return config with enforcement enabled"""
        return {
            "documentation": {
                "enforcement": {
                    "enabled": True,
                    "allowWorkflowBypass": True
                }
            }
        }

    @pytest.mark.asyncio
    async def test_yaml_frontmatter_auto_generated(
        self, enable_write_ops, temp_workspace, enforce_config
    ):
        """Verify that missing YAML frontmatter is auto-generated (BLOCKER 7 core)."""
        doc_path = "docs/CacheService.md"

        # Content WITHOUT YAML frontmatter - should be auto-generated
        content = """# CacheService

## Quick Reference (TL;DR)
In-memory cache management.

## What & Why
Provides caching layer.

## How It Works
Uses Redis.

## Business Rules
None.

## Architecture
Simple.

## API Contract (AI Context)
None.

## Validation Rules (AUTO-GENERATED)
None.

## Data Operations
None.

## External Dependencies
Redis.

## Known Issues & Limitations
None.

## Performance
Fast.

## Error Reference
None.

## Testing
Basic.

## Monitoring & Alerts
None.

## Questions & Gaps
None.
"""

        # Ensure target doesn't exist
        file_path = temp_workspace / doc_path
        assert not file_path.exists(), "Test file should not exist yet"

        result = await write_documentation_async(
            repo_path=str(temp_workspace),
            doc_path=doc_path,
            content=content,
            source_file="src/services/CacheService.cs",
            mode="dry-run",
            component_type="service",
            template="lean_baseline_service_template.md",
            force_workflow_bypass=True,
            allowWrites=True,
            config=enforce_config,
        )

        # Verify operation succeeded
        assert result["success"] is True, f"Should succeed, got: {result}"

        # CRITICAL: autoFixed should show yaml_frontmatter was added
        assert "autoFixed" in result
        assert "yaml_frontmatter" in result["autoFixed"], (
            f"Expected yaml_frontmatter in autoFixed, got: {result['autoFixed']}"
        )

        # Verify YAML was actually added in dry-run preview
        preview_content = result.get("preview", "")
        assert preview_content.startswith("---"), "YAML frontmatter should be added"
        assert "component: CacheService" in preview_content

        # CRITICAL: File should NOT be created in dry-run mode
        assert not file_path.exists(), (
            "Dry-run mode must NOT write files to disk. "
            f"File was created at {file_path}"
        )

    @pytest.mark.asyncio
    async def test_feature_branch_writes_file(
        self, enable_write_ops, temp_workspace, enforce_config
    ):
        """Verify that feature-branch mode actually writes files (BLOCKER 7 core)."""
        doc_path = "docs/SearchService.md"

        content = """---
feature: search
domain: backend
component: SearchService
componentType: service
layer: application
priority: P2
status: active
version: 1.0.0
lastUpdated: 2025-01-01
---

# SearchService

## Quick Reference (TL;DR)
Full-text search.

## What & Why
Search capabilities.

## How It Works
Lucene indexing.

## Business Rules
None.

## Architecture
Distributed.

## API Contract (AI Context)
POST /search

## Validation Rules (AUTO-GENERATED)
Query 1-500 chars.

## Data Operations
Real-time indexing.

## External Dependencies
Elasticsearch.

## Known Issues & Limitations
Case-insensitive only.

## Performance
<1s average.

## Error Reference
ERR001: Timeout

## Testing
Integration tests.

## Monitoring & Alerts
Latency monitored.

## Questions & Gaps
None.
"""

        file_path = temp_workspace / doc_path
        assert not file_path.exists(), "File should not exist yet"

        result = await write_documentation_async(
            repo_path=str(temp_workspace),
            doc_path=doc_path,
            content=content,
            source_file="src/services/SearchService.cs",
            mode="feature-branch",
            component_type="service",
            template="lean_baseline_service_template.md",
            force_workflow_bypass=True,
            allowWrites=True,
            config=enforce_config,
        )

        # Verify operation succeeded
        assert result["success"] is True, f"Write should succeed, got: {result}"

        # File SHOULD be created in feature-branch mode
        assert file_path.exists(), "File should be written in feature-branch mode"

        # Verify file content
        file_content = file_path.read_text(encoding="utf-8")
        assert "SearchService" in file_content, "File should contain original content"

    @pytest.mark.asyncio
    async def test_autoFixed_list_present(
        self, enable_write_ops, temp_workspace, enforce_config
    ):
        """Verify autoFixed list is present in response (BLOCKER 7 core)."""
        doc_path = "docs/AuditService.md"

        content = """---
feature: audit
domain: backend
component: AuditService
componentType: service
layer: application
priority: P1
status: active
version: 1.0.0
lastUpdated: 2025-01-01
---

# AuditService

## Quick Reference (TL;DR)
Audit logging.

## What & Why
Compliance tracking.

## How It Works
Event sourcing.

## Business Rules
None.

## Architecture
Simple.

## API Contract (AI Context)
None.

## Validation Rules
None.

## Data Operations
Append-only.

## External Dependencies
None.

## Known Issues & Limitations
None.

## Performance
Good.

## Error Reference
None.

## Testing
Unit tests.

## Monitoring & Alerts
None.

## Questions & Gaps
None.
"""

        result = await write_documentation_async(
            repo_path=str(temp_workspace),
            doc_path=doc_path,
            content=content,
            source_file="src/services/AuditService.cs",
            mode="dry-run",
            component_type="service",
            template="lean_baseline_service_template.md",
            force_workflow_bypass=True,
            allowWrites=True,
            config=enforce_config,
        )

        # Verify operation succeeded
        assert result["success"] is True, f"Should succeed, got: {result}"

        # CRITICAL: autoFixed field must exist and be a list
        assert "autoFixed" in result, (
            "Response MUST include 'autoFixed' field"
        )
        assert isinstance(result["autoFixed"], list), (
            "autoFixed must be a list"
        )

    @pytest.mark.asyncio
    async def test_content_preserved_in_diff(
        self, enable_write_ops, temp_workspace, enforce_config
    ):
        """Verify auto-fixes preserve content in diffs (BLOCKER 7 safety)."""
        doc_path = "docs/OrderService.md"

        # Content without YAML - will trigger auto-fix
        content = """# OrderService

## Quick Reference (TL;DR)
Order processing.

## What & Why
Critical service that processes customer orders and validates business rules.

## How It Works
Validates orders, applies business rules, checks inventory.

## Business Rules
- Orders need valid customers
- Must check inventory
- Cannot exceed credit limit

## Architecture
Event-driven.

## API Contract (AI Context)
POST /orders

## Validation Rules (AUTO-GENERATED)
All fields required.

## Data Operations
CRUD operations.

## External Dependencies
Payment gateway.

## Known Issues & Limitations
None.

## Performance
Optimized.

## Error Reference
ERR001: Invalid order

## Testing
Full coverage.

## Monitoring & Alerts
All operations logged.

## Questions & Gaps
None.
"""

        result = await write_documentation_async(
            repo_path=str(temp_workspace),
            doc_path=doc_path,
            content=content,
            source_file="src/services/OrderService.cs",
            mode="dry-run",
            component_type="service",
            template="lean_baseline_service_template.md",
            force_workflow_bypass=True,
            allowWrites=True,
            config=enforce_config,
        )

        # Verify operation succeeded
        assert result["success"] is True, f"Should succeed, got: {result}"

        # Should have auto-fixed YAML
        assert "yaml_frontmatter" in result.get("autoFixed", [])

        # Extract preview (contains the auto-fixed content)
        preview_content = result.get("preview", "")

        # Verify critical content preserved
        critical_phrases = [
            "OrderService",
            "processes customer orders and validates business rules",
            "Orders need valid customers",
            "Must check inventory"
        ]

        for phrase in critical_phrases:
            assert phrase in preview_content, (
                f"Critical phrase '{phrase}' lost in processing"
            )

    @pytest.mark.asyncio
    async def test_workflow_dry_run_then_feature_branch(
        self, enable_write_ops, temp_workspace, enforce_config
    ):
        """Test complete workflow: dry-run preview, then feature-branch (BLOCKER 7 integration)."""
        doc_path = "docs/CompleteService.md"

        content = """---
feature: complete
domain: backend
component: CompleteService
componentType: service
layer: application
priority: P2
status: active
version: 1.0.0
lastUpdated: 2025-01-01
---

# CompleteService

## Quick Reference (TL;DR)
Complete implementation.

## What & Why
Full functionality.

## How It Works
Normal operations.

## Business Rules
None.

## Architecture
Simple.

## API Contract (AI Context)
None.

## Validation Rules (AUTO-GENERATED)
None.

## Data Operations
None.

## External Dependencies
None.

## Known Issues & Limitations
None.

## Performance
Good.

## Error Reference
None.

## Testing
Basic.

## Monitoring & Alerts
None.

## Questions & Gaps
None.
"""

        # Step 1: Dry-run preview
        dry_run_result = await write_documentation_async(
            repo_path=str(temp_workspace),
            doc_path=doc_path,
            content=content,
            source_file="src/services/CompleteService.cs",
            mode="dry-run",
            component_type="service",
            template="lean_baseline_service_template.md",
            force_workflow_bypass=True,
            allowWrites=True,
            config=enforce_config,
        )

        # Verify dry-run succeeded
        assert dry_run_result["success"] is True
        assert dry_run_result.get("effect") == "dry-run"

        # Step 2: Feature-branch write
        file_path = temp_workspace / doc_path
        assert not file_path.exists(), "File shouldn't exist yet"

        feature_result = await write_documentation_async(
            repo_path=str(temp_workspace),
            doc_path=doc_path,
            content=content,
            source_file="src/services/CompleteService.cs",
            mode="feature-branch",
            component_type="service",
            template="lean_baseline_service_template.md",
            force_workflow_bypass=True,
            allowWrites=True,
            config=enforce_config,
        )

        # Verify feature-branch succeeded
        assert feature_result["success"] is True
        assert file_path.exists(), "File should be written"

        # Verify file content
        file_content = file_path.read_text(encoding="utf-8")
        assert "CompleteService" in file_content
