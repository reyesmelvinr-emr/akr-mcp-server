"""
Progress tracking and reporting for long-running MCP operations.

Provides real-time progress notifications (0-100%) and cancellation support
for async documentation operations.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Optional, Callable, Awaitable

logger = logging.getLogger(__name__)


@dataclass
class ProgressStage:
    """Define a trackable stage in an operation."""
    name: str                    # e.g., "validation", "write", "commit"
    start_percent: int           # 0-100: starting percentage
    end_percent: int             # 0-100: ending percentage
    description: str = ""        # Human-readable description


# Standard stage definitions for documentation operations
STAGE_DEFINITIONS = {
    "validation": ProgressStage("validation", 0, 40, "Validating document structure"),
    "write": ProgressStage("write", 40, 80, "Writing file to disk"),
    "commit": ProgressStage("commit", 80, 100, "Committing to git"),
}


class ProgressTracker:
    """
    Track and report operation progress via MCP notifications.
    
    Supports:
    - Stage-based progress tracking (0-100%)
    - Real-time progress notifications
    - Cancellation token handling
    - Automatic percentage calculation based on stage boundaries
    """
    
    def __init__(
        self,
        progress_token: Optional[str] = None,
        send_progress: Optional[Callable[[int, str], Awaitable[None]]] = None,
        stages: Optional[dict[str, ProgressStage]] = None,
        estimate_remaining: Optional[Callable[[str, float], Optional[int]]] = None,
    ):
        """
        Initialize progress tracker.
        
        Args:
            progress_token: MCP progress token; if None, progress tracking is disabled
            send_progress: Async callback to send progress notifications
                          Signature: async def send_progress(progress: int, message: str) -> None
            stages: Dict of stage_name -> ProgressStage; defaults to STAGE_DEFINITIONS
        """
        self.progress_token = progress_token
        self.send_progress = send_progress
        self.stages = stages or STAGE_DEFINITIONS
        self.estimate_remaining = estimate_remaining
        self.current_stage: Optional[str] = None
        self.current_percent = 0
        self._is_cancelled = False
    
    async def update_stage(
        self,
        stage_name: str,
        message: Optional[str] = None,
        sub_percent: float = 0.0,
    ) -> None:
        """
        Update to a new stage and optionally report progress.
        
        Args:
            stage_name: Key from self.stages (e.g., "validation", "write", "commit")
            message: Optional custom message to display; defaults to stage description
            sub_percent: Optional 0-1 progress within the stage
        
        Raises:
            asyncio.CancelledError: If operation was cancelled mid-way
            ValueError: If stage_name not found in self.stages
        """
        self._check_cancelled()
        
        if stage_name not in self.stages:
            raise ValueError(f"Unknown stage: {stage_name}. Available: {list(self.stages.keys())}")
        
        self.current_stage = stage_name
        stage = self.stages[stage_name]
        
        # Calculate percentage within stage boundaries
        stage_range = stage.end_percent - stage.start_percent
        stage_progress = int(stage_range * sub_percent)
        self.current_percent = stage.start_percent + stage_progress
        
        # Use provided message or stage description
        display_message = message or stage.description
        
        await self.notify_progress(self.current_percent, display_message)
    
    async def notify_progress(
        self,
        progress: int,
        message: str,
        sub_step: Optional[int] = None,
        total_steps: Optional[int] = None,
    ) -> None:
        """
        Send progress notification to client with enhanced stage indicators.
        
        Args:
            progress: Current progress percentage (0-100)
            message: Status message to display
            sub_step: Current step number (for sub-task breakdown)
            total_steps: Total steps in current stage
        """
        self._check_cancelled()
        
        if not self.progress_token or not self.send_progress:
            return  # Progress tracking disabled
        
        # Ensure progress is monotonically increasing and within bounds
        progress = max(0, min(100, progress))
        if progress < self.current_percent and progress < 100:
            # Don't go backward unless completing
            progress = self.current_percent
        
        # Build enhanced message with stage indicator
        display_message = message
        
        # Add stage indicator if we have a current stage
        if self.current_stage:
            stage_indicator = f"[{self.current_stage.upper()}]"
            display_message = f"{stage_indicator} {message}"
        
        # Add sub-task breakdown if available
        if sub_step is not None and total_steps is not None:
            display_message = f"{display_message} (Step {sub_step}/{total_steps})"

        # Add ETA estimate if available
        if self.current_stage and self.estimate_remaining:
            completion_pct = self._compute_completion_pct(progress)
            eta_ms = self.estimate_remaining(self.current_stage, completion_pct)
            if eta_ms is not None:
                eta_display = self._format_eta(eta_ms)
                display_message = f"{display_message} (ETA {eta_display})"
        
        logger.debug(f"Progress: {progress}% - {display_message}")
        
        try:
            await self.send_progress(progress, display_message)
        except Exception as e:
            logger.error(f"Failed to send progress notification: {e}")
    
    def _check_cancelled(self) -> None:
        """Check if operation was cancelled; raise CancelledError if so."""
        if self._is_cancelled:
            raise asyncio.CancelledError("Operation was cancelled")

    def _compute_completion_pct(self, progress: int) -> float:
        """Estimate completion percentage within the current stage."""
        if not self.current_stage or self.current_stage not in self.stages:
            return 0.5
        stage = self.stages[self.current_stage]
        stage_range = max(1, stage.end_percent - stage.start_percent)
        pct = (progress - stage.start_percent) / stage_range
        return max(0.0, min(1.0, pct))

    def _format_eta(self, eta_ms: int) -> str:
        """Format an ETA in a compact, human-friendly way."""
        if eta_ms < 1000:
            return "<1s"
        seconds = int(round(eta_ms / 1000))
        if seconds < 60:
            return f"~{seconds}s"
        minutes = int(round(seconds / 60))
        if minutes < 60:
            return f"~{minutes}m"
        hours = int(round(minutes / 60))
        return f"~{hours}h"
    
    def cancel(self) -> None:
        """Mark operation as cancelled."""
        self._is_cancelled = True
    
    async def conclude(self) -> None:
        """Mark operation as complete (100%)."""
        self._check_cancelled()
        self.current_percent = 100
        await self.notify_progress(100, "Operation complete")


class AsyncOperationCancelled(Exception):
    """Raised when an async operation is cancelled mid-way."""
    pass
