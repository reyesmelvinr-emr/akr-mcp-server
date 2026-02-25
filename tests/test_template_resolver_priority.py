"""BLOCKER 1: Test TemplateResolver priority loading (submodule > local override > remote)."""

import os
import pytest
import tempfile
import shutil
import hashlib
from pathlib import Path
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from resources.template_resolver import TemplateResolver


class TestTemplateResolverPriority:
    """Test template resolution priority: submodule > local override > remote preview"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with all 3 template locations"""
        workspace = tempfile.mkdtemp()
        
        # Create submodule directory
        submodule_dir = Path(workspace) / "templates" / "core"
        submodule_dir.mkdir(parents=True)
        (submodule_dir / "test_template.md").write_text("SUBMODULE_CONTENT", encoding="utf-8")
        
        # Create local override directory
        local_dir = Path(workspace) / "akr_content" / "templates"
        local_dir.mkdir(parents=True)
        (local_dir / "test_template.md").write_text("LOCAL_OVERRIDE_CONTENT", encoding="utf-8")
        
        yield workspace
        shutil.rmtree(workspace)
    
    def test_submodule_beats_local_override(self, temp_workspace):
        """When template exists in both submodule and local, submodule wins"""
        resolver = TemplateResolver(repo_root=temp_workspace)
        content = resolver.get_template("test_template")
        assert content is not None, "Template should be found"
        assert "SUBMODULE_CONTENT" in content, "Submodule content should be used"
        assert "LOCAL_OVERRIDE_CONTENT" not in content, "Local override should not be used"
    
    def test_local_override_when_submodule_missing(self, temp_workspace):
        """When template missing from submodule, local override is used"""
        # Remove from submodule
        submodule_file = Path(temp_workspace) / "templates" / "core" / "test_template.md"
        submodule_file.unlink()
        
        resolver = TemplateResolver(repo_root=temp_workspace)
        content = resolver.get_template("test_template")
        assert content is not None, "Template should be found"
        assert "LOCAL_OVERRIDE_CONTENT" in content, "Local override should be used"
    
    @pytest.mark.skipif(not os.getenv("TEST_REMOTE_FETCH"), reason="Remote fetch disabled")
    def test_remote_preview_with_hash_verification(self, temp_workspace):
        """Remote preview used when local sources missing, with SHA-256 verification"""
        # Remove local sources
        shutil.rmtree(Path(temp_workspace) / "templates" / "core")
        shutil.rmtree(Path(temp_workspace) / "akr_content" / "templates")
        
        # Mock HTTP fetch
        remote_content = "REMOTE_PREVIEW_CONTENT"
        expected_hash = hashlib.sha256(remote_content.encode()).hexdigest()
        
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = remote_content
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            resolver = TemplateResolver(repo_root=temp_workspace, config={
                "http_fetch_enabled": True,
                "http_fetch_config": {
                    "verify_checksums": True,
                    "expected_hashes": {"test_template": expected_hash}
                }
            })
            
            content = resolver.get_template("test_template")
            assert content is not None, "Remote template should be fetched"
            assert "REMOTE_PREVIEW_CONTENT" in content, "Remote content should be used"
    
    @pytest.mark.skipif(not os.getenv("TEST_REMOTE_FETCH"), reason="Remote fetch disabled")
    def test_remote_hash_mismatch_fails_closed(self, temp_workspace):
        """Remote fetch aborts on SHA-256 hash mismatch (fail-closed)"""
        # Remove local sources
        shutil.rmtree(Path(temp_workspace) / "templates" / "core")
        shutil.rmtree(Path(temp_workspace) / "akr_content" / "templates")
        
        # Mock HTTP fetch with wrong hash
        remote_content = "TAMPERED_CONTENT"
        wrong_hash = hashlib.sha256(b"EXPECTED_CONTENT").hexdigest()
        
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = remote_content
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            resolver = TemplateResolver(repo_root=temp_workspace, config={
                "http_fetch_enabled": True,
                "http_fetch_config": {
                    "verify_checksums": True,
                    "expected_hashes": {"test_template": wrong_hash}
                }
            })
            
            # Should return None or raise error when hash doesn't match
            content = resolver.get_template("test_template")
            # Fail-closed means we should NOT get the tampered content
            if content is not None:
                assert "TAMPERED_CONTENT" not in content, "Tampered content should be rejected"
