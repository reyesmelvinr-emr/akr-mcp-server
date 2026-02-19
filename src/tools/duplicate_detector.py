"""
Duplicate Write Detection for Documentation Operations

Detects and prevents redundant documentation write operations by tracking content
hashes and timestamps. This helps identify workflow issues where the same content
is written multiple times, which indicates:
- Tool misuse or confusion
- Retry loops without meaningful changes
- Performance problems

Author: AKR MCP Server Team
Date: February 6, 2026
"""

import asyncio
import hashlib
import time
from dataclasses import dataclass
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class DuplicateCheckResult:
    """Result of a duplicate detection check"""
    is_duplicate: bool
    reason: Optional[str] = None
    cached_result: Optional[Dict[str, Any]] = None
    time_since_last_ms: Optional[int] = None
    content_changed: bool = False


@dataclass
class WriteRecord:
    """Record of a documentation write operation"""
    doc_path: str
    content_hash: str
    timestamp: float
    result: Dict[str, Any]


class DuplicateDetector:
    """
    Detects duplicate documentation write operations.
    
    Tracks write attempts with content hashes and timestamps to identify:
    - Identical writes (same content within time window) → Return cached result
    - Rapid rewrites (different content within short window) → Warn but allow
    
    Time windows:
    - DUPLICATE_WINDOW: 30 seconds for same content (return cached)
    - RAPID_CHANGE_WINDOW: 5 seconds for different content (warn)
    
    Example:
        detector = DuplicateDetector()
        
        # Check for duplicate
        check = await detector.check_duplicate("docs/api.md", content)
        if check.is_duplicate:
            return check.cached_result
        
        # Perform write...
        result = await write_operation()
        
        # Cache result
        await detector.cache_result("docs/api.md", content, result)
    """
    
    # Time windows in seconds
    DUPLICATE_WINDOW = 30  # Same content within 30s = duplicate
    RAPID_CHANGE_WINDOW = 5  # Different content within 5s = rapid change warning
    
    def __init__(self):
        """Initialize duplicate detector"""
        self._records: Dict[str, WriteRecord] = {}
        self._lock = asyncio.Lock()
        logger.info("DuplicateDetector initialized")
    
    @staticmethod
    def _compute_hash(content: str) -> str:
        """
        Compute SHA256 hash of content.
        
        Args:
            content: Content to hash
            
        Returns:
            Hex digest of SHA256 hash
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    async def check_duplicate(self, doc_path: str, content: str) -> DuplicateCheckResult:
        """
        Check if this write operation is a duplicate.
        
        Logic:
        1. If same doc_path + same content within 30s → duplicate (return cached)
        2. If same doc_path + different content within 5s → rapid change (warn, allow)
        3. Otherwise → not duplicate (allow)
        
        Args:
            doc_path: Path to documentation file
            content: Content to be written
            
        Returns:
            DuplicateCheckResult with detection details
        """
        async with self._lock:
            content_hash = self._compute_hash(content)
            current_time = time.time()
            
            # Check if we have a record for this doc_path
            record = self._records.get(doc_path)
            
            if record is None:
                # No previous write
                return DuplicateCheckResult(
                    is_duplicate=False,
                    content_changed=False
                )
            
            time_since_last = current_time - record.timestamp
            time_since_last_ms = int(time_since_last * 1000)
            
            # Check if content is identical
            content_changed = (content_hash != record.content_hash)
            
            if not content_changed and time_since_last <= self.DUPLICATE_WINDOW:
                # Same content within duplicate window → duplicate!
                logger.info(
                    f"Duplicate write detected: {doc_path} "
                    f"(same content within {time_since_last:.1f}s)"
                )
                return DuplicateCheckResult(
                    is_duplicate=True,
                    reason=f"Identical content written {time_since_last:.1f}s ago",
                    cached_result=record.result,
                    time_since_last_ms=time_since_last_ms,
                    content_changed=False
                )
            
            if content_changed and time_since_last <= self.RAPID_CHANGE_WINDOW:
                # Different content within rapid change window → warn but allow
                logger.warning(
                    f"Rapid content change detected: {doc_path} "
                    f"(different content within {time_since_last:.1f}s)"
                )
                return DuplicateCheckResult(
                    is_duplicate=False,
                    reason=f"Rapid rewrite detected ({time_since_last:.1f}s ago)",
                    time_since_last_ms=time_since_last_ms,
                    content_changed=True
                )
            
            # Normal write - enough time has passed or first write
            return DuplicateCheckResult(
                is_duplicate=False,
                time_since_last_ms=time_since_last_ms if record else None,
                content_changed=content_changed
            )
    
    async def cache_result(
        self,
        doc_path: str,
        content: str,
        result: Dict[str, Any]
    ) -> None:
        """
        Cache the result of a write operation.
        
        This should be called after a successful write to enable duplicate detection
        for subsequent writes.
        
        Args:
            doc_path: Path to documentation file
            content: Content that was written
            result: Result dictionary from the write operation
        """
        async with self._lock:
            content_hash = self._compute_hash(content)
            record = WriteRecord(
                doc_path=doc_path,
                content_hash=content_hash,
                timestamp=time.time(),
                result=result
            )
            self._records[doc_path] = record
            logger.debug(f"Cached write result: {doc_path}")
    
    async def clear(self, doc_path: str) -> None:
        """
        Clear cached record for a document path.
        
        Args:
            doc_path: Path to documentation file
        """
        async with self._lock:
            if doc_path in self._records:
                del self._records[doc_path]
                logger.debug(f"Cleared duplicate detection cache: {doc_path}")
    
    async def cleanup_old_records(self, max_age_seconds: int = 300) -> int:
        """
        Clean up old records to prevent memory growth.
        
        Removes records older than max_age_seconds (default 5 minutes).
        
        Args:
            max_age_seconds: Maximum age of records to keep
            
        Returns:
            Number of records cleaned up
        """
        async with self._lock:
            current_time = time.time()
            old_paths = [
                path for path, record in self._records.items()
                if (current_time - record.timestamp) > max_age_seconds
            ]
            
            for path in old_paths:
                del self._records[path]
            
            if old_paths:
                logger.info(f"Cleaned up {len(old_paths)} old duplicate detection records")
            
            return len(old_paths)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about duplicate detection.
        
        Returns:
            Dictionary with stats
        """
        return {
            "cached_records": len(self._records),
            "duplicate_window_seconds": self.DUPLICATE_WINDOW,
            "rapid_change_window_seconds": self.RAPID_CHANGE_WINDOW
        }
