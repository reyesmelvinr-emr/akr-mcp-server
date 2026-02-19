"""
Unit tests for WorkflowTracker

Tests workflow state tracking functionality including:
- Marking stub generation
- Checking stub status
- TTL-based expiry
- State cleanup
- Thread safety

Author: AKR MCP Server Team
Date: February 6, 2026
"""

import pytest
import asyncio
import time
from unittest.mock import patch
from src.tools.workflow_tracker import WorkflowTracker, WorkflowState


@pytest.mark.asyncio
async def test_mark_and_check_stub_generated():
    """Test marking a stub as generated and checking its status"""
    tracker = WorkflowTracker(ttl_seconds=10)
    
    # Mark stub generated
    await tracker.mark_stub_generated("docs/test.md", "lean_baseline_service_template.md")
    
    # Check that stub is marked as generated
    assert await tracker.is_stub_generated("docs/test.md")
    
    # Check that other paths return False
    assert not await tracker.is_stub_generated("docs/other.md")


@pytest.mark.asyncio
async def test_stub_not_generated():
    """Test checking non-existent stub"""
    tracker = WorkflowTracker(ttl_seconds=10)
    
    # Should return False for non-existent path
    assert not await tracker.is_stub_generated("docs/nonexistent.md")


@pytest.mark.asyncio
async def test_ttl_expiry():
    """Test that workflow states expire after TTL"""
    tracker = WorkflowTracker(ttl_seconds=1)  # 1 second TTL
    
    # Mark stub generated
    await tracker.mark_stub_generated("docs/test.md", "template.md")
    
    # Immediately should be marked
    assert await tracker.is_stub_generated("docs/test.md")
    
    # Wait for expiry
    await asyncio.sleep(1.5)
    
    # Should now be expired
    assert not await tracker.is_stub_generated("docs/test.md")


@pytest.mark.asyncio
async def test_get_state():
    """Test retrieving workflow state"""
    tracker = WorkflowTracker(ttl_seconds=10)
    
    # Mark stub generated
    await tracker.mark_stub_generated("docs/test.md", "template.md")
    
    # Get state
    state = await tracker.get_state("docs/test.md")
    
    assert state is not None
    assert state.doc_path == "docs/test.md"
    assert state.template == "template.md"
    assert state.stub_generated is True


@pytest.mark.asyncio
async def test_get_state_expired():
    """Test that expired states return None"""
    tracker = WorkflowTracker(ttl_seconds=1)
    
    # Mark stub generated
    await tracker.mark_stub_generated("docs/test.md", "template.md")
    
    # Wait for expiry
    await asyncio.sleep(1.5)
    
    # Should return None for expired state
    state = await tracker.get_state("docs/test.md")
    assert state is None


@pytest.mark.asyncio
async def test_clear_state():
    """Test clearing workflow state"""
    tracker = WorkflowTracker(ttl_seconds=10)
    
    # Mark stub generated
    await tracker.mark_stub_generated("docs/test.md", "template.md")
    assert await tracker.is_stub_generated("docs/test.md")
    
    # Clear state
    await tracker.clear("docs/test.md")
    
    # Should no longer be marked
    assert not await tracker.is_stub_generated("docs/test.md")


@pytest.mark.asyncio
async def test_cleanup_expired():
    """Test cleaning up expired states"""
    tracker = WorkflowTracker(ttl_seconds=1)
    
    # Mark multiple stubs
    await tracker.mark_stub_generated("docs/test1.md", "template.md")
    await tracker.mark_stub_generated("docs/test2.md", "template.md")
    
    # Wait for expiry
    await asyncio.sleep(1.5)
    
    # Add a fresh one
    await tracker.mark_stub_generated("docs/test3.md", "template.md")
    
    # Cleanup expired
    cleaned = await tracker.cleanup_expired()
    
    # Should have cleaned up 2 expired states
    assert cleaned == 2
    
    # Fresh one should still exist
    assert await tracker.is_stub_generated("docs/test3.md")
    
    # Expired ones should be gone
    assert not await tracker.is_stub_generated("docs/test1.md")
    assert not await tracker.is_stub_generated("docs/test2.md")


@pytest.mark.asyncio
async def test_get_stats():
    """Test getting tracker statistics"""
    tracker = WorkflowTracker(ttl_seconds=10)
    
    # Initial stats
    stats = tracker.get_stats()
    assert stats["active_states"] == 0
    assert stats["ttl_seconds"] == 10
    
    # Add some states
    await tracker.mark_stub_generated("docs/test1.md", "template.md")
    await tracker.mark_stub_generated("docs/test2.md", "template.md")
    
    # Check updated stats
    stats = tracker.get_stats()
    assert stats["active_states"] == 2


@pytest.mark.asyncio
async def test_concurrent_access():
    """Test thread safety with concurrent access"""
    tracker = WorkflowTracker(ttl_seconds=10)
    
    # Create multiple concurrent operations
    async def mark_and_check(doc_path):
        await tracker.mark_stub_generated(doc_path, "template.md")
        return await tracker.is_stub_generated(doc_path)
    
    # Run multiple operations concurrently
    results = await asyncio.gather(
        mark_and_check("docs/test1.md"),
        mark_and_check("docs/test2.md"),
        mark_and_check("docs/test3.md"),
        mark_and_check("docs/test4.md"),
        mark_and_check("docs/test5.md")
    )
    
    # All should have succeeded
    assert all(results)
    
    # All states should exist
    assert await tracker.is_stub_generated("docs/test1.md")
    assert await tracker.is_stub_generated("docs/test2.md")
    assert await tracker.is_stub_generated("docs/test3.md")
    assert await tracker.is_stub_generated("docs/test4.md")
    assert await tracker.is_stub_generated("docs/test5.md")


@pytest.mark.asyncio
async def test_multiple_marks_same_path():
    """Test marking same path multiple times (should update timestamp)"""
    tracker = WorkflowTracker(ttl_seconds=10)
    
    # Mark stub
    await tracker.mark_stub_generated("docs/test.md", "template1.md")
    state1 = await tracker.get_state("docs/test.md")
    
    # Wait a bit
    await asyncio.sleep(0.5)
    
    # Mark again with different template
    await tracker.mark_stub_generated("docs/test.md", "template2.md")
    state2 = await tracker.get_state("docs/test.md")
    
    # Should be updated
    assert state2.template == "template2.md"
    assert state2.timestamp > state1.timestamp


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
