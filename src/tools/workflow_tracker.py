"""
Workflow State Tracking for Documentation Generation

Tracks the state of documentation generation workflows to enforce proper tool usage patterns
and detect workflow violations. This helps prevent common issues like:
- Bypassing generate_documentation and writing directly
- Multiple redundant write operations
- Manual file creation outside the tool system

Author: AKR MCP Server Team
Date: February 6, 2026
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class WorkflowState:
    """State information for a documentation generation workflow"""
    doc_path: str
    template: str
    timestamp: float
    stub_generated: bool


class WorkflowTracker:
    """
    Tracks documentation generation workflow state to enforce proper tool usage.
    
    This class maintains an in-memory cache of workflow states with TTL-based expiry.
    It's thread-safe using asyncio locks for concurrent access.
    
    Typical workflow:
    1. generate_documentation called → marks stub_generated=True
    2. write_documentation called → checks if stub was generated
    3. After TTL expires → state cleared automatically
    
    Example:
        tracker = WorkflowTracker(ttl_seconds=1800)  # 30 minutes
        
        # Mark stub generated
        tracker.mark_stub_generated("docs/api.md", "lean_baseline_service_template.md")
        
        # Check if stub was generated
        if tracker.is_stub_generated("docs/api.md"):
            # Proceed with write
            pass
    """
    
    def __init__(self, ttl_seconds: int = 1800):
        """
        Initialize workflow tracker.
        
        Args:
            ttl_seconds: Time-to-live for workflow state entries (default 30 minutes)
        """
        self._states: Dict[str, WorkflowState] = {}
        self._lock = asyncio.Lock()
        self._ttl_seconds = ttl_seconds
        logger.info(f"WorkflowTracker initialized with TTL={ttl_seconds}s")
    
    async def mark_stub_generated(self, doc_path: str, template: str) -> None:
        """
        Mark that a documentation stub has been generated.
        
        This should be called by generate_documentation after successfully creating a stub.
        
        Args:
            doc_path: Path to the documentation file
            template: Template used for generation
        """
        async with self._lock:
            state = WorkflowState(
                doc_path=doc_path,
                template=template,
                timestamp=time.time(),
                stub_generated=True
            )
            self._states[doc_path] = state
            logger.debug(f"Marked stub generated: {doc_path} (template: {template})")
    
    async def is_stub_generated(self, doc_path: str) -> bool:
        """
        Check if a stub has been generated for the given document path.
        
        This performs TTL-based expiry checking. If the state is expired, it's
        automatically removed and False is returned.
        
        Args:
            doc_path: Path to the documentation file
            
        Returns:
            True if stub was generated and not expired, False otherwise
        """
        async with self._lock:
            state = self._states.get(doc_path)
            
            if state is None:
                return False
            
            # Check if expired
            age_seconds = time.time() - state.timestamp
            if age_seconds > self._ttl_seconds:
                logger.debug(f"Workflow state expired for {doc_path} (age: {age_seconds:.1f}s)")
                del self._states[doc_path]
                return False
            
            return state.stub_generated
    
    async def get_state(self, doc_path: str) -> Optional[WorkflowState]:
        """
        Get the workflow state for a document path.
        
        Returns None if state doesn't exist or is expired.
        
        Args:
            doc_path: Path to the documentation file
            
        Returns:
            WorkflowState if exists and not expired, None otherwise
        """
        async with self._lock:
            state = self._states.get(doc_path)
            
            if state is None:
                return None
            
            # Check if expired
            age_seconds = time.time() - state.timestamp
            if age_seconds > self._ttl_seconds:
                del self._states[doc_path]
                return None
            
            return state
    
    async def clear(self, doc_path: str) -> None:
        """
        Clear workflow state for a document path.
        
        This should be called after successful write completion or on error.
        
        Args:
            doc_path: Path to the documentation file
        """
        async with self._lock:
            if doc_path in self._states:
                del self._states[doc_path]
                logger.debug(f"Cleared workflow state: {doc_path}")
    
    async def cleanup_expired(self) -> int:
        """
        Clean up all expired workflow states.
        
        This can be called periodically to prevent memory growth.
        
        Returns:
            Number of states cleaned up
        """
        async with self._lock:
            current_time = time.time()
            expired_paths = [
                path for path, state in self._states.items()
                if (current_time - state.timestamp) > self._ttl_seconds
            ]
            
            for path in expired_paths:
                del self._states[path]
            
            if expired_paths:
                logger.info(f"Cleaned up {len(expired_paths)} expired workflow states")
            
            return len(expired_paths)
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about the workflow tracker state.
        
        Returns:
            Dictionary with stats: active_states, total_tracked
        """
        return {
            "active_states": len(self._states),
            "total_tracked": len(self._states),
            "ttl_seconds": self._ttl_seconds
        }
