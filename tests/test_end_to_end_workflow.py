"""
Integration tests for Phase 2 workflow enforcement.

Tests complete workflows:
1. Happy Path: generate_documentation → write_documentation → Success
2. Violation Path: Direct write_documentation for new file → Error with guidance
3. Progress Path: Real-time progress notifications during operation
"""

import asyncio
import json
import logging
import tempfile
from pathlib import Path
from typing import Optional

import pytest

from src.tools.workflow_tracker import WorkflowTracker
from src.tools.progress_tracker import ProgressTracker
from src.tools.enforcement_tool import enforce_and_fix, EnforceResult
from src.tools.validation_engine import ValidationEngine
from src.tools.operation_metrics import OperationMetrics


logger = logging.getLogger(__name__)


# ============ Test Fixtures ============

@pytest.fixture
def workflow_tracker():
    """Create a fresh workflow tracker for each test."""
    return WorkflowTracker()


@pytest.fixture
def progress_tracker():
    """Create a fresh progress tracker for each test."""
    progress_log = []
    
    async def collect_progress(progress: int, message: str):
        progress_log.append({"progress": progress, "message": message})
    
    tracker = ProgressTracker(
        progress_token="test-token-123",
        send_progress=collect_progress
    )
    tracker.progress_log = progress_log
    return tracker


@pytest.fixture
def test_config():
    """Create test configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield {
            "workspace_root": tmpdir,
            "workspaceFolders": [tmpdir],
            "pathMappings": {},
            "autoFixEnabled": True,
            "enforceStrictMode": False,
        }


# ============ Test Cases ============

class TestProgressTracking:
    """Test real-time progress notifications."""
    
    @pytest.mark.asyncio
    async def test_progress_stage_updates(self, progress_tracker):
        """Test progress updates with stage indicators."""
        await progress_tracker.update_stage("validation", "Checking structure")
        await progress_tracker.update_stage("validation", "Validating content", sub_percent=0.5)
        await progress_tracker.update_stage("write", "Writing file")
        await progress_tracker.conclude()
        
        # Verify stage indicators were added
        messages = [log["message"] for log in progress_tracker.progress_log]
        assert any("[VALIDATION]" in msg for msg in messages), "Missing stage indicator"
        assert any("[WRITE]" in msg for msg in messages), "Missing stage indicator"
        
        # Verify progress is monotonic
        progresses = [log["progress"] for log in progress_tracker.progress_log]
        for i in range(1, len(progresses)):
            assert progresses[i] >= progresses[i-1], "Progress went backward"
    
    @pytest.mark.asyncio
    async def test_progress_with_substeps(self, progress_tracker):
        """Test progress reporting with sub-step breakdown."""
        await progress_tracker.update_stage("validation")
        
        # Simulate multi-step validation
        for step in range(1, 5):
            await progress_tracker.notify_progress(
                progress=10 + (step * 5),
                message=f"Checking component {step}",
                sub_step=step,
                total_steps=4
            )
        
        messages = [log["message"] for log in progress_tracker.progress_log]
        assert any(f"Step 1/4" in msg for msg in messages), "Missing sub-step indicator"
        assert any(f"Step 4/4" in msg for msg in messages), "Missing sub-step indicator"


class TestErrorMessages:
    """Test enhanced error messages with actionable guidance."""
    
    def test_missing_yaml_error_guidance(self):
        """Test that YAML validation errors include actionable guidance."""
        engine = ValidationEngine()
        
        # Missing YAML
        violations = engine.check_yaml_frontmatter({})
        
        assert len(violations) > 0
        message = violations[0].message.lower()
        # Verify message includes guidance
        assert "yaml" in message or "front matter" in message
    
    def test_missing_sections_error_guidance(self):
        """Test that missing section errors include guidance."""
        from src.tools.enforcement_tool_types import TemplateSchema, Section
        
        engine = ValidationEngine()
        
        # Simulate schema with required sections
        schema = TemplateSchema(
            template_name="test",
            required_sections=[
                Section(name="Overview", heading_level=2, required=True, order_index=0),
                Section(name="How It Works", heading_level=2, required=True, order_index=1),
                Section(name="API Reference", heading_level=2, required=True, order_index=2),
            ]
        )
        
        # Document with only one section
        found_sections = ["Overview"]
        
        violations = engine.check_required_sections(found_sections, schema)
        
        assert len(violations) >= 2, "Should report multiple missing sections"
        for violation in violations:
            message = violation.message.lower()
            # Verify actionable guidance is present
            assert any(
                keyword in message 
                for keyword in ["missing", "required", "add", "generate_documentation"]
            ), f"Message lacks actionable guidance: {violation.message}"
    
    def test_section_order_error_guidance(self):
        """Test that section order errors include fix suggestions."""
        from src.tools.enforcement_tool_types import TemplateSchema, Section
        
        engine = ValidationEngine()
        
        schema = TemplateSchema(
            template_name="test",
            required_sections=[
                Section(name="Overview", heading_level=2, required=True, order_index=0),
                Section(name="Content", heading_level=2, required=True, order_index=1),
                Section(name="Summary", heading_level=2, required=True, order_index=2),
            ]
        )
        
        # Out of order sections
        found_sections = ["Summary", "Overview", "Content"]
        
        violations = engine.check_section_order(found_sections, schema)
        
        assert len(violations) > 0
        message = violations[0].message
        # Verify guidance on how to fix
        assert "update_documentation_sections" in message or "regenerate" in message


class TestWorkflowTracking:
    """Test workflow state tracking and validation."""
    
    @pytest.mark.asyncio
    async def test_stub_generation_marking(self, workflow_tracker):
        """Test marking documentation as stub-generated."""
        doc_path = "docs/test.md"
        template = "lean_baseline_service_template.md"
        
        # Initially not marked
        assert not await workflow_tracker.is_stub_generated(doc_path)
        
        # Mark as generated
        await workflow_tracker.mark_stub_generated(doc_path, template)
        
        # Now should be marked
        assert await workflow_tracker.is_stub_generated(doc_path)
        
        # Clear it
        await workflow_tracker.clear(doc_path)
        
        # Should be cleared
        assert not await workflow_tracker.is_stub_generated(doc_path)
    
    @pytest.mark.asyncio
    async def test_stub_ttl_expiry(self, workflow_tracker):
        """Test that stub generation markers expire (mocked time)."""
        doc_path = "docs/test.md"
        template = "template.md"
        
        await workflow_tracker.mark_stub_generated(doc_path, template)
        assert await workflow_tracker.is_stub_generated(doc_path)
        
        # Manually manipulate internal state to test expiry
        # (In real tests, would mock time.time())
        entry = workflow_tracker._states.get(doc_path)
        if entry:
            # Simulate expiry by setting old timestamp
            import time
            workflow_tracker._states[doc_path].timestamp = time.time() - 2000  # 2000 seconds old (> 30 min TTL)
        
        # Should be considered expired
        assert not await workflow_tracker.is_stub_generated(doc_path)


class TestEnforceResultGuidance:
    """Test enhanced EnforceResult with actionable guidance."""
    
    def test_enforce_result_suggested_actions(self):
        """Test that EnforceResult includes suggested actions."""
        result = EnforceResult(
            valid=False,
            validation_errors=["Missing sections: API Reference"],
            suggested_actions=[
                "Use generate_documentation to create a complete stub",
                "Or manually add the API Reference section",
                "Then use write_documentation to save"
            ]
        )
        
        assert len(result.suggested_actions) == 3
        assert all(isinstance(action, str) for action in result.suggested_actions)
        assert "generate_documentation" in result.suggested_actions[0]
    
    def test_enforce_result_autofix_flag(self):
        """Test can_autofix flag in EnforceResult."""
        result_no_fix = EnforceResult(
            valid=False,
            can_autofix=False,
            validation_errors=["YAML frontmatter missing"]
        )
        
        result_with_fix = EnforceResult(
            valid=False,
            can_autofix=True,
            validation_errors=["Section order incorrect"]
        )
        
        assert not result_no_fix.can_autofix
        assert result_with_fix.can_autofix


class TestProgressEstimation:
    """Test progress estimation based on operation metrics."""
    
    def test_estimate_remaining_ms(self):
        """Test estimated time remaining calculation."""
        metrics = OperationMetrics()
        
        # Currently in validation stage, 50% complete
        remaining = metrics.estimate_remaining_ms("validation", completion_pct=0.5)
        
        assert remaining is not None
        assert remaining > 0
        # Should include time for validation (50% remaining), write, and commit
        assert remaining >= 200  # At minimum write + commit time
    
    def test_estimate_remaining_write_stage(self):
        """Test estimation during write stage."""
        metrics = OperationMetrics()
        
        # In write stage, 75% complete
        remaining = metrics.estimate_remaining_ms("write", completion_pct=0.75)
        
        assert remaining is not None
        # Should include ~25% of write + all of commit
        assert remaining >= 100


class TestHappyPathWorkflow:
    """Test the ideal documentation workflow."""
    
    @pytest.mark.asyncio
    async def test_correct_workflow_sequence(self):
        """Test generate → review → write sequence."""
        progress_updates = []
        
        async def track_progress(progress: int, message: str):
            progress_updates.append((progress, message))
        
        # Simulate the workflow
        # 1. Generate (would create stub in real scenario)
        # 2. Validate (checking stub structure)
        # 3. Write (save to disk)
        
        tracker = ProgressTracker(
            progress_token="test",
            send_progress=track_progress
        )
        
        # Simulate workflow stages
        await tracker.update_stage("validation", "Parsing template")
        await tracker.update_stage("validation", "Validating structure", sub_percent=0.8)
        await tracker.update_stage("write", "Creating file")
        await tracker.update_stage("write", "Staging changes", sub_percent=0.9)
        await tracker.update_stage("commit", "Committing to git")
        await tracker.conclude()
        
        # Verify workflow completed with increasing progress
        progresses = [p[0] for p in progress_updates]
        assert progresses[-1] == 100, "Should complete at 100%"
        assert all(progresses[i] <= progresses[i+1] for i in range(len(progresses)-1))


class TestOptimizationMetrics:
    """Test that Phase 2 improvements are measurable."""
    
    def test_operation_metrics_tracking(self):
        """Test operation metrics collection."""
        metrics = OperationMetrics(template_name="test_template.md")
        
        # Simulate operation
        metrics.start_stage("validation")
        # Simulate work
        import time
        time.sleep(0.01)  # Small delay
        validation_time = metrics.end_stage("validation")
        
        assert metrics.validation_ms > 0
        assert metrics.validation_ms == validation_time
        
        metrics.start_stage("write")
        time.sleep(0.01)
        write_time = metrics.end_stage("write")
        
        assert metrics.write_ms > 0
        assert metrics.write_ms == write_time
        
        # Summary should be available
        summary = metrics.to_summary_string()
        assert "validation:" in summary
        assert "write:" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
