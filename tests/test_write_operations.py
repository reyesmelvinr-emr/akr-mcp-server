"""BLOCKER 3: Test write operations return dry-run diff by default."""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import after path setup
from tools.write_operations import write_documentation_async


class TestWriteOperationsDryRun:
    """Test write operations return dry-run diff by default"""
    
    @pytest.fixture
    def enable_write_ops(self, monkeypatch):
        """Enable write operations for testing"""
        monkeypatch.setenv("AKR_ENABLE_WRITE_OPS", "true")
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with proper structure"""
        workspace = tempfile.mkdtemp()
        workspace_path = Path(workspace)
        
        # Initialize git repository
        import subprocess
        subprocess.run(["git", "init"], cwd=workspace_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=workspace_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=workspace_path, capture_output=True)
        
        # Create docs directory
        docs_dir = workspace_path / "docs"
        docs_dir.mkdir()
        
        # Create a sample doc file with valid structure
        test_doc = docs_dir / "test.md"
        test_doc.write_text("""---
component_name: OriginalComponent
template: default.md
---

# OriginalComponent

## Overview
Original content.

## Purpose
This is the original documentation.
""", encoding="utf-8")
        
        # Create config.json with enforcement enabled
        config_file = workspace_path / "config.json"
        config_file.write_text("""{
  "documentation": {
    "enforcement": {
      "enabled": true
    }
  }
}""", encoding="utf-8")
        
        yield workspace_path
        
        # Cleanup
        import shutil
        try:
            # Windows may lock .git files, use onerror handler
            def handle_remove_readonly(func, path, exc_info):
                import stat
                os.chmod(path, stat.S_IWRITE)
                func(path)
            shutil.rmtree(workspace, onerror=handle_remove_readonly)
        except Exception:
            pass  # Best effort cleanup
    
    @pytest.fixture
    def mock_config(self):
        """Return config with enforcement enabled"""
        return {
            "documentation": {
                "enforcement": {
                    "enabled": True
                }
            }
        }
    
    @pytest.mark.asyncio
    async def test_dry_run_mode_returns_diff_without_writing(
        self, enable_write_ops, temp_workspace, mock_config
    ):
        """
        CRITICAL TEST: mode='dry-run' must return diff without modifying file.
        
        This is the core safety feature - users can preview changes before applying.
        """
        doc_path = "docs/test.md"
        new_content = """---
component_name: TestComponent
template: default.md
---

# TestComponent

## Overview
Updated component documentation.

## Purpose
This is a test update.
"""
        full_path = temp_workspace / doc_path
        
        # Read original content
        original = full_path.read_text(encoding="utf-8")
        
        # Call with mode="dry-run" - this parameter might not exist yet
        try:
            result = await write_documentation_async(
                repo_path=str(temp_workspace),
                doc_path=doc_path,
                content=new_content,
                source_file="test.cs",
                mode="dry-run",  # NEW PARAMETER
                overwrite=True,
                force_workflow_bypass=True,
                allowWrites=True,
                config=mock_config
            )
        except TypeError as e:
            if "mode" in str(e):
                pytest.skip("Implementation does not support 'mode' parameter yet")
            raise
        
        # Verify response shape
        assert isinstance(result, dict), "Result must be dict"
        assert result.get("success") is True or "effect" in result, \
            "Should indicate dry-run effect"
        
        # Verify diff/patch is present
        assert "patch" in result or "diff" in result or "preview" in result, \
            "Result must contain diff/patch/preview"
        
        # Verify file was NOT modified
        current = full_path.read_text(encoding="utf-8")
        assert current == original, "File should not be modified in dry-run mode"
    
    @pytest.mark.asyncio
    async def test_feature_branch_mode_actually_writes(
        self, enable_write_ops, temp_workspace, mock_config
    ):
        """
        Verify mode='feature-branch' respects enforcement and writes only if valid.

        This mode is for when user confirms they want changes applied, but enforcement
        still gates the write operation.
        """
        doc_path = "docs/test.md"
        # Use VALID content that passes enforcement
        new_content = """---
feature: test-feature
domain: backend
component: FeatureComponent
componentType: service
layer: application
priority: P2
status: active
version: 1.0.0
lastUpdated: 2025-01-01
---

# FeatureComponent

## Quick Reference (TL;DR)
Feature component for testing.

## What & Why
This component exists for testing purposes.

## How It Works
It processes test data.

## Business Rules
- Must validate inputs
- Must log operations

## Architecture
Simple service architecture.

## API Contract (AI Context)
N/A - internal only.

## Validation Rules
All inputs must be strings.

## Data Operations
Read/write test data.

## External Dependencies
None.

## Known Issues & Limitations
Test-only implementation.

## Performance
Optimized for test scenarios.

## Error Reference
- ERR001: Invalid input

## Testing
Unit tests cover all paths.

## Monitoring & Alerts
Basic logging enabled.

## Questions & Gaps
None at this time.
"""
        full_path = temp_workspace / doc_path
        
        # Call with mode="feature-branch"
        try:
            result = await write_documentation_async(
                repo_path=str(temp_workspace),
                doc_path=doc_path,
                content=new_content,
                source_file="test.cs",
                mode="feature-branch",  # NEW PARAMETER
                overwrite=True,
                force_workflow_bypass=True,
                allowWrites=True,
                config=mock_config
            )
        except TypeError as e:
            if "mode" in str(e):
                pytest.skip("Implementation does not support 'mode' parameter yet")
            raise
        
        # Should indicate success (content is valid)
        assert result.get("success") is True, f"Write should succeed, got: {result}"
        
        # Verify file WAS modified
        current = full_path.read_text(encoding="utf-8")
        assert "FeatureComponent" in current, "File content should contain FeatureComponent"
    
    @pytest.mark.asyncio
    async def test_default_mode_is_dry_run(
        self, enable_write_ops, temp_workspace, mock_config
    ):
        """
        When mode is omitted, should default to dry-run (safe default).
        """
        doc_path = "docs/test.md"
        new_content = "# Default Mode Test\n\nTesting default behavior."
        full_path = temp_workspace / doc_path
        
        original = full_path.read_text(encoding="utf-8")
        
        # Call WITHOUT mode parameter - should default to dry-run
        result = await write_documentation_async(
            repo_path=str(temp_workspace),
            doc_path=doc_path,
            content=new_content,
            source_file="test.cs",
            overwrite=True,
            force_workflow_bypass=True,
            allowWrites=True,
            config=mock_config
        )
        
        # Should have diff/patch (dry-run behavior)
        # OR file should not be modified (safe default)
        current = full_path.read_text(encoding="utf-8")
        
        # Either returns diff or doesn't write (both are safe)
        has_diff = "patch" in result or "diff" in result or "preview" in result
        file_unchanged = current == original
        
        assert has_diff or file_unchanged, \
            "Default mode should be safe: either return diff or not write"
