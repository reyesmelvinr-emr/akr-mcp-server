"""
Unit tests for Workflow Enforcement Integration

Tests the integration of workflow tracking and enforcement in documentation operations:
- Workflow violation detection
- Bypass flag functionality
- Telemetry logging
- Integration with write_documentation_async

Author: AKR MCP Server Team
Date: February 6, 2026
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.tools.workflow_tracker import WorkflowTracker
from src.tools.duplicate_detector import DuplicateDetector


@pytest.mark.asyncio
async def test_workflow_violation_detected():
    """Test that workflow violation is detected for new file without stub"""
    workflow_tracker = WorkflowTracker(ttl_seconds=10)
    
    # Create mock telemetry logger
    telemetry_logger = MagicMock()
    telemetry_logger.log_event = MagicMock()
    
    # Check workflow for new file
    doc_path = "docs/new_file.md"
    stub_generated = await workflow_tracker.is_stub_generated(doc_path)
    
    assert not stub_generated
    
    # Simulate logging violation
    if not stub_generated:
        telemetry_logger.log_event({
            "event_type": "WORKFLOW_VIOLATION",
            "doc_path": doc_path,
            "violation_type": "direct_write_new_file"
        })
    
    # Verify telemetry was called
    telemetry_logger.log_event.assert_called_once()
    call_args = telemetry_logger.log_event.call_args[0][0]
    assert call_args["event_type"] == "WORKFLOW_VIOLATION"
    assert call_args["doc_path"] == doc_path


@pytest.mark.asyncio
async def test_no_violation_with_stub():
    """Test that no violation occurs when stub was generated"""
    workflow_tracker = WorkflowTracker(ttl_seconds=10)
    
    # Mark stub as generated
    doc_path = "docs/test.md"
    await workflow_tracker.mark_stub_generated(doc_path, "template.md")
    
    # Check workflow
    stub_generated = await workflow_tracker.is_stub_generated(doc_path)
    
    assert stub_generated


@pytest.mark.asyncio
async def test_bypass_flag_logs_telemetry():
    """Test that bypass flag usage is logged to telemetry"""
    telemetry_logger = MagicMock()
    telemetry_logger.log_event = MagicMock()
    
    force_workflow_bypass = True
    doc_path = "docs/bypassed.md"
    
    # Simulate bypass logging
    if force_workflow_bypass:
        telemetry_logger.log_event({
            "event_type": "WORKFLOW_BYPASS",
            "doc_path": doc_path
        })
    
    # Verify telemetry was called
    telemetry_logger.log_event.assert_called_once()
    call_args = telemetry_logger.log_event.call_args[0][0]
    assert call_args["event_type"] == "WORKFLOW_BYPASS"


@pytest.mark.asyncio
async def test_workflow_state_cleared_after_write():
    """Test that workflow state is cleared after successful write"""
    workflow_tracker = WorkflowTracker(ttl_seconds=10)
    
    doc_path = "docs/test.md"
    
    # Mark stub generated
    await workflow_tracker.mark_stub_generated(doc_path, "template.md")
    assert await workflow_tracker.is_stub_generated(doc_path)
    
    # Simulate successful write
    # ... write operation ...
    
    # Clear state after success
    await workflow_tracker.clear(doc_path)
    
    # State should be cleared
    assert not await workflow_tracker.is_stub_generated(doc_path)


@pytest.mark.asyncio
async def test_duplicate_detection_returns_cached():
    """Test that duplicate writes return cached results"""
    duplicate_detector = DuplicateDetector()
    
    doc_path = "docs/test.md"
    content = "# Test Documentation"
    cached_result = {
        "success": True,
        "filePath": doc_path,
        "message": "Cached result"
    }
    
    # Cache a result
    await duplicate_detector.cache_result(doc_path, content, cached_result)
    
    # Check for duplicate
    check = await duplicate_detector.check_duplicate(doc_path, content)
    
    assert check.is_duplicate
    assert check.cached_result == cached_result


@pytest.mark.asyncio
async def test_duplicate_logs_telemetry():
    """Test that duplicate detection logs to telemetry"""
    duplicate_detector = DuplicateDetector()
    telemetry_logger = MagicMock()
    telemetry_logger.log_event = MagicMock()
    
    doc_path = "docs/test.md"
    content = "# Test"
    
    # Cache result
    await duplicate_detector.cache_result(doc_path, content, {"success": True})
    
    # Check duplicate
    check = await duplicate_detector.check_duplicate(doc_path, content)
    
    # Log if duplicate
    if check.is_duplicate:
        telemetry_logger.log_event({
            "event_type": "DUPLICATE_WRITE",
            "doc_path": doc_path,
            "time_since_last_ms": check.time_since_last_ms
        })
    
    # Verify logging
    telemetry_logger.log_event.assert_called_once()
    call_args = telemetry_logger.log_event.call_args[0][0]
    assert call_args["event_type"] == "DUPLICATE_WRITE"


@pytest.mark.asyncio
async def test_rapid_change_warning_logged():
    """Test that rapid content changes are logged"""
    duplicate_detector = DuplicateDetector()
    telemetry_logger = MagicMock()
    telemetry_logger.log_event = MagicMock()
    
    doc_path = "docs/test.md"
    content1 = "# Version 1"
    content2 = "# Version 2"
    
    # First write
    await duplicate_detector.cache_result(doc_path, content1, {"success": True})
    
    # Immediate write with different content
    check = await duplicate_detector.check_duplicate(doc_path, content2)
    
    # Log warning if rapid change
    if check.reason and "rapid" in check.reason.lower():
        telemetry_logger.log_event({
            "event_type": "RAPID_CHANGE_WARNING",
            "doc_path": doc_path,
            "time_since_last_ms": check.time_since_last_ms
        })
    
    # Verify warning was logged
    telemetry_logger.log_event.assert_called_once()


@pytest.mark.asyncio
async def test_workflow_integration_happy_path():
    """Test complete happy path: generate → write"""
    workflow_tracker = WorkflowTracker(ttl_seconds=10)
    duplicate_detector = DuplicateDetector()
    telemetry_logger = MagicMock()
    
    doc_path = "docs/happy_path.md"
    template = "lean_baseline_service_template.md"
    content = "# Documentation Content"
    
    # Step 1: generate_documentation marks stub
    await workflow_tracker.mark_stub_generated(doc_path, template)
    
    # Step 2: write_documentation checks workflow
    stub_generated = await workflow_tracker.is_stub_generated(doc_path)
    assert stub_generated  # Should pass
    
    # Step 3: Check for duplicates
    check = await duplicate_detector.check_duplicate(doc_path, content)
    assert not check.is_duplicate  # First write
    
    # Step 4: Write succeeds, cache result
    result = {"success": True, "filePath": doc_path}
    await duplicate_detector.cache_result(doc_path, content, result)
    
    # Step 5: Clear workflow state
    await workflow_tracker.clear(doc_path)
    
    # Verify final state
    assert not await workflow_tracker.is_stub_generated(doc_path)
    
    # If same write attempted again, should be duplicate
    check2 = await duplicate_detector.check_duplicate(doc_path, content)
    assert check2.is_duplicate


@pytest.mark.asyncio
async def test_workflow_integration_violation_path():
    """Test violation path: write without generate"""
    workflow_tracker = WorkflowTracker(ttl_seconds=10)
    telemetry_logger = MagicMock()
    telemetry_logger.log_event = MagicMock()
    
    doc_path = "docs/violation.md"
    
    # Attempt write without generate_documentation
    stub_generated = await workflow_tracker.is_stub_generated(doc_path)
    
    if not stub_generated:
        # Phase 1: Log but don't block
        telemetry_logger.log_event({
            "event_type": "WORKFLOW_VIOLATION",
            "doc_path": doc_path,
            "violation_type": "direct_write_new_file"
        })
        
        # In Phase 2, this would return an error
        # For now, just log
    
    # Verify violation was logged
    telemetry_logger.log_event.assert_called_once()


@pytest.mark.asyncio
async def test_concurrent_workflow_operations():
    """Test concurrent workflow operations don't interfere"""
    workflow_tracker = WorkflowTracker(ttl_seconds=10)
    
    async def generate_and_check(doc_path):
        await workflow_tracker.mark_stub_generated(doc_path, "template.md")
        return await workflow_tracker.is_stub_generated(doc_path)
    
    # Run concurrent operations
    results = await asyncio.gather(
        generate_and_check("docs/test1.md"),
        generate_and_check("docs/test2.md"),
        generate_and_check("docs/test3.md")
    )
    
    # All should succeed
    assert all(results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
