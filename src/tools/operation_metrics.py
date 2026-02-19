"""
Operation metrics tracking for documentation generation and updates.

Captures performance metrics (processing time, file sizes, estimated tokens)
for reporting to users and developers.
"""

import time
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class StageMetric:
    """Metrics for a single stage of operation."""
    name: str                   # e.g., "validation", "write", "commit"
    duration_ms: int = 0        # Time taken (milliseconds)
    
    def __post_init__(self):
        """Validate stage name."""
        if not self.name:
            raise ValueError("Stage name cannot be empty")


@dataclass
class OperationMetrics:
    """
    Complete metrics for a documentation operation.
    
    Captures timing breakdowns, content metrics, and resource usage
    for performance analysis and user feedback.
    """
    
    # Timing breakdown (per stage)
    validation_ms: int = 0      # Schema build + parse + validate
    write_ms: int = 0           # File creation + write + git stage
    commit_ms: int = 0          # Git commit operation
    total_ms: int = 0           # Total operation time
    
    # Content metrics
    content_chars: int = 0      # Character count of generated content
    content_lines: int = 0      # Line count of generated content
    content_tokens_est: int = 0 # Estimated token count (rough LLM approximation)
    file_size_bytes: int = 0    # Final file size in bytes
    
    # Context
    template_name: str = ""     # Template used (e.g., "lean_baseline_service_template.md")
    sections_count: int = 0     # Number of sections in final document
    
    # Operational flags
    auto_fixed: int = 0         # Number of auto-fixed issues
    violations_found: int = 0   # Number of violations (if any)
    
    # Timestamps for audit
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    # Per-stage tracking (internal use)
    _stage_timers: dict[str, float] = field(default_factory=dict, init=False)
    _stage_active: Optional[str] = field(default=None, init=False)
    
    def start_stage(self, stage_name: str) -> None:
        """Mark the start of a stage."""
        self._stage_timers[stage_name] = time.time()
        self._stage_active = stage_name
        logger.debug(f"Stage started: {stage_name}")
    
    def end_stage(self, stage_name: str) -> int:
        """
        Mark the end of a stage and return its duration (ms).
        
        Args:
            stage_name: Name of the stage (must match start_stage call)
        
        Returns:
            Duration in milliseconds
        """
        if stage_name not in self._stage_timers:
            logger.warning(f"Ending stage '{stage_name}' that was not started")
            return 0
        
        duration_ms = int((time.time() - self._stage_timers[stage_name]) * 1000)
        
        # Store in appropriate field
        if stage_name == "validation":
            self.validation_ms = duration_ms
        elif stage_name == "write":
            self.write_ms = duration_ms
        elif stage_name == "commit":
            self.commit_ms = duration_ms
        
        self._stage_active = None
        logger.debug(f"Stage completed: {stage_name} ({duration_ms}ms)")
        
        return duration_ms
    
    def estimate_tokens(self) -> int:
        """
        Estimate token count using rough LLM approximation.
        
        Formula: chars / 4 + lines (very rough approximation for documentation)
        Typical: 1 token ≈ 4 characters in English text
        
        Returns:
            Estimated token count
        """
        if self.content_chars == 0:
            return 0
        
        # Rough estimate: ~4 characters per token for English text
        # Plus extra tokens for line breaks and structure
        estimated = (self.content_chars // 4) + self.content_lines
        return max(0, estimated)
    
    def finalize(self) -> None:
        """Finalize metrics and calculate totals."""
        self.end_time = time.time()
        self.total_ms = int((self.end_time - self.start_time) * 1000)
        self.content_tokens_est = self.estimate_tokens()
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dict suitable for json.dumps()
        """
        return {
            "timing": {
                "validation_ms": self.validation_ms,
                "write_ms": self.write_ms,
                "commit_ms": self.commit_ms,
                "total_ms": self.total_ms,
            },
            "content": {
                "chars": self.content_chars,
                "lines": self.content_lines,
                "estimated_tokens": self.content_tokens_est,
                "file_size_bytes": self.file_size_bytes,
            },
            "context": {
                "template": self.template_name,
                "sections_count": self.sections_count,
            },
            "enforcement": {
                "auto_fixed": self.auto_fixed,
                "violations_found": self.violations_found,
            }
        }
    
    def to_summary_string(self) -> str:
        """
        Generate human-readable summary of metrics.
        
        Returns:
            Summary string suitable for logging or display
        """
        return (
            f"Operation metrics: {self.total_ms}ms total "
            f"(validation: {self.validation_ms}ms, "
            f"write: {self.write_ms}ms, "
            f"commit: {self.commit_ms}ms) | "
            f"Content: {self.content_chars} chars, "
            f"~{self.content_tokens_est} tokens, "
            f"{self.file_size_bytes} bytes"
        )
    
    def estimate_remaining_ms(self, current_stage: str, completion_pct: float = 0.5) -> Optional[int]:
        """
        Estimate time remaining based on historical stage metrics and current progress.
        
        Uses P50 (median) times from similar operations to estimate remaining duration.
        This is a conservative estimate based on observed patterns.
        
        Args:
            current_stage: Name of current stage (validation, write, commit)
            completion_pct: Estimated completion percentage within current stage (0.0-1.0)
        
        Returns:
            Estimated milliseconds remaining, or None if insufficient data
        """
        # Standard stage durations (P50 from experience)
        # These are conservative estimates; actual times vary by content size
        STANDARD_STAGE_TIMES = {
            "validation": 400,   # Parse + validate typically 300-500ms
            "write": 300,        # File write + staging 200-400ms
            "commit": 200,       # Git commit 100-300ms
        }
        
        if current_stage not in STANDARD_STAGE_TIMES:
            return None
        
        # Time remaining in current stage
        current_stage_total = STANDARD_STAGE_TIMES[current_stage]
        remaining_in_current = int(current_stage_total * (1.0 - completion_pct))
        
        # Time for remaining stages
        remaining_stages = []
        stages_list = ["validation", "write", "commit"]
        current_idx = stages_list.index(current_stage) if current_stage in stages_list else -1
        
        for i in range(current_idx + 1, len(stages_list)):
            remaining_stages.append(STANDARD_STAGE_TIMES[stages_list[i]])
        
        total_remaining = remaining_in_current + sum(remaining_stages)
        return max(100, total_remaining)  # At least 100ms estimate
