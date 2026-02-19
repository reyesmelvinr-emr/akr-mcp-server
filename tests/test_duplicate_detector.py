"""
Unit tests for DuplicateDetector

Tests duplicate write detection including:
- Same content detection
- Different content warnings
- Cache management
- Result caching and retrieval
- Cleanup of old records

Author: AKR MCP Server Team
Date: February 6, 2026
"""

import pytest
import asyncio
from src.tools.duplicate_detector import DuplicateDetector, DuplicateCheckResult


@pytest.mark.asyncio
async def test_no_duplicate_first_write():
    """Test that first write is not detected as duplicate"""
    detector = DuplicateDetector()
    
    content = "# Test Documentation"
    result = await detector.check_duplicate("docs/test.md", content)
    
    assert not result.is_duplicate
    assert result.cached_result is None


@pytest.mark.asyncio
async def test_duplicate_same_content():
    """Test that same content within window is detected as duplicate"""
    detector = DuplicateDetector()
    
    content = "# Test Documentation"
    doc_path = "docs/test.md"
    
    # First write - check and cache
    check1 = await detector.check_duplicate(doc_path, content)
    assert not check1.is_duplicate
    
    cached_result = {"success": True, "message": "Written"}
    await detector.cache_result(doc_path, content, cached_result)
    
    # Second write with same content immediately
    check2 = await detector.check_duplicate(doc_path, content)
    
    assert check2.is_duplicate
    assert check2.cached_result == cached_result
    assert check2.content_changed is False


@pytest.mark.asyncio
async def test_no_duplicate_different_content():
    """Test that different content is not marked as duplicate"""
    detector = DuplicateDetector()
    
    doc_path = "docs/test.md"
    
    # First write
    content1 = "# Version 1"
    check1 = await detector.check_duplicate(doc_path, content1)
    assert not check1.is_duplicate
    
    await detector.cache_result(doc_path, content1, {"success": True})
    
    # Second write with different content
    content2 = "# Version 2"
    check2 = await detector.check_duplicate(doc_path, content2)
    
    assert not check2.is_duplicate
    assert check2.content_changed is True


@pytest.mark.asyncio
async def test_rapid_change_warning():
    """Test that rapid content changes trigger warning"""
    detector = DuplicateDetector()
    
    doc_path = "docs/test.md"
    
    # First write
    content1 = "# Version 1"
    await detector.check_duplicate(doc_path, content1)
    await detector.cache_result(doc_path, content1, {"success": True})
    
    # Immediate write with different content
    content2 = "# Version 2"
    check = await detector.check_duplicate(doc_path, content2)
    
    # Should not be duplicate but flag rapid change
    assert not check.is_duplicate
    assert check.content_changed is True
    assert check.reason is not None
    assert "rapid" in check.reason.lower()


@pytest.mark.asyncio
async def test_no_duplicate_after_window():
    """Test that writes after window are not duplicates"""
    detector = DuplicateDetector()
    
    # Temporarily modify window for testing
    original_window = detector.DUPLICATE_WINDOW
    detector.DUPLICATE_WINDOW = 1  # 1 second window
    
    try:
        content = "# Test Documentation"
        doc_path = "docs/test.md"
        
        # First write
        await detector.check_duplicate(doc_path, content)
        await detector.cache_result(doc_path, content, {"success": True})
        
        # Wait for window to pass
        await asyncio.sleep(1.5)
        
        # Second write with same content after window
        check = await detector.check_duplicate(doc_path, content)
        
        assert not check.is_duplicate
    
    finally:
        detector.DUPLICATE_WINDOW = original_window


@pytest.mark.asyncio
async def test_cache_result():
    """Test caching write results"""
    detector = DuplicateDetector()
    
    content = "# Test"
    result = {"success": True, "filePath": "docs/test.md"}
    
    await detector.cache_result("docs/test.md", content, result)
    
    # Check duplicate should now find cached result
    check = await detector.check_duplicate("docs/test.md", content)
    
    assert check.is_duplicate
    assert check.cached_result == result


@pytest.mark.asyncio
async def test_clear_cache():
    """Test clearing cached record"""
    detector = DuplicateDetector()
    
    content = "# Test"
    doc_path = "docs/test.md"
    
    # Cache a result
    await detector.cache_result(doc_path, content, {"success": True})
    
    # Verify it's cached
    check1 = await detector.check_duplicate(doc_path, content)
    assert check1.is_duplicate
    
    # Clear cache
    await detector.clear(doc_path)
    
    # Should no longer be cached
    check2 = await detector.check_duplicate(doc_path, content)
    assert not check2.is_duplicate


@pytest.mark.asyncio
async def test_cleanup_old_records():
    """Test cleanup of old records"""
    detector = DuplicateDetector()
    
    # Cache some records
    await detector.cache_result("docs/test1.md", "content1", {"success": True})
    await detector.cache_result("docs/test2.md", "content2", {"success": True})
    
    # Wait a bit then add a fresh one
    await asyncio.sleep(0.5)
    await detector.cache_result("docs/test3.md", "content3", {"success": True})
    
    # Cleanup old records (max_age=0.3 seconds, so first two should be old)
    cleaned = await detector.cleanup_old_records(max_age_seconds=0.3)
    
    # Should have cleaned up 2 old records
    assert cleaned == 2
    
    # Fresh one should still be cached
    check = await detector.check_duplicate("docs/test3.md", "content3")
    assert check.is_duplicate
    
    # Old ones should be gone
    check1 = await detector.check_duplicate("docs/test1.md", "content1")
    check2 = await detector.check_duplicate("docs/test2.md", "content2")
    assert not check1.is_duplicate
    assert not check2.is_duplicate


@pytest.mark.asyncio
async def test_get_stats():
    """Test getting detector statistics"""
    detector = DuplicateDetector()
    
    # Initial stats
    stats = detector.get_stats()
    assert stats["cached_records"] == 0
    assert stats["duplicate_window_seconds"] == 30
    
    # Add some records
    await detector.cache_result("docs/test1.md", "content1", {"success": True})
    await detector.cache_result("docs/test2.md", "content2", {"success": True})
    
    # Check updated stats
    stats = detector.get_stats()
    assert stats["cached_records"] == 2


@pytest.mark.asyncio
async def test_content_hash_computation():
    """Test that identical content produces same hash"""
    detector = DuplicateDetector()
    
    content = "# Identical Content"
    doc_path = "docs/test.md"
    
    # Write twice with identical content
    await detector.cache_result(doc_path, content, {"success": True})
    
    check = await detector.check_duplicate(doc_path, content)
    
    assert check.is_duplicate


@pytest.mark.asyncio
async def test_multiple_files():
    """Test tracking multiple files independently"""
    detector = DuplicateDetector()
    
    # Cache results for multiple files
    await detector.cache_result("docs/test1.md", "content1", {"file": "test1"})
    await detector.cache_result("docs/test2.md", "content2", {"file": "test2"})
    await detector.cache_result("docs/test3.md", "content3", {"file": "test3"})
    
    # Check each file has its own cached result
    check1 = await detector.check_duplicate("docs/test1.md", "content1")
    check2 = await detector.check_duplicate("docs/test2.md", "content2")
    check3 = await detector.check_duplicate("docs/test3.md", "content3")
    
    assert check1.is_duplicate and check1.cached_result["file"] == "test1"
    assert check2.is_duplicate and check2.cached_result["file"] == "test2"
    assert check3.is_duplicate and check3.cached_result["file"] == "test3"


@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test thread safety with concurrent operations"""
    detector = DuplicateDetector()
    
    async def check_and_cache(doc_path, content):
        check = await detector.check_duplicate(doc_path, content)
        if not check.is_duplicate:
            await detector.cache_result(doc_path, content, {"path": doc_path})
        return check
    
    # Run concurrent operations
    results = await asyncio.gather(
        check_and_cache("docs/test1.md", "content1"),
        check_and_cache("docs/test2.md", "content2"),
        check_and_cache("docs/test3.md", "content3"),
        check_and_cache("docs/test4.md", "content4"),
        check_and_cache("docs/test5.md", "content5")
    )
    
    # All first writes should not be duplicates
    assert all(not r.is_duplicate for r in results)
    
    # All should now be cached
    stats = detector.get_stats()
    assert stats["cached_records"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
