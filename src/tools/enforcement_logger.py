"""
EnforcementLogger: JSON Lines logging for enforcement tool operations.

Provides structured logging for:
- SCHEMA_BUILT: Template schema parsed and cached
- VALIDATION_RUN: Document validated with results
- WRITE_ATTEMPT: File write initiated
- WRITE_SUCCESS: File write completed successfully
- WRITE_FAILURE: File write failed
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


@dataclass
class LogEvent:
    """Base log event."""
    timestamp: str
    event_type: str
    details: Dict[str, Any]


class EnforcementLogger:
    """Handles JSON Lines logging for enforcement operations."""
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize logger.
        
        Args:
            log_file: Optional path to JSON Lines log file. If not provided, logs are only in-memory.
        """
        self.log_file = log_file
        self.events: List[LogEvent] = []
    
    def log_schema_built(
        self,
        template_name: str,
        section_count: int,
        checksum: str
    ) -> None:
        """
        Log that template schema was built and cached.
        
        Args:
            template_name: Name of template
            section_count: Number of required sections
            checksum: Schema checksum for cache validation
        """
        event = LogEvent(
            timestamp=self._get_timestamp(),
            event_type="SCHEMA_BUILT",
            details={
                "template_name": template_name,
                "section_count": section_count,
                "checksum": checksum
            }
        )
        self._append_event(event)
    
    def log_validation_run(
        self,
        template_name: str,
        file_path: str,
        valid: bool,
        confidence: float,
        blocker_count: int,
        fixable_count: int,
        warn_count: int,
        effective_mode: str
    ) -> None:
        """
        Log that document validation was run.
        
        Args:
            template_name: Template used for validation
            file_path: Path of document being validated
            valid: Whether validation passed
            confidence: Confidence score (0.0-1.0)
            blocker_count: Number of BLOCKER violations
            fixable_count: Number of FIXABLE violations
            warn_count: Number of WARN violations
            effective_mode: Effective documentation mode (per_file or per_module)
        """
        event = LogEvent(
            timestamp=self._get_timestamp(),
            event_type="VALIDATION_RUN",
            details={
                "template_name": template_name,
                "file_path": file_path,
                "valid": valid,
                "confidence": confidence,
                "severity_summary": {
                    "blockers": blocker_count,
                    "fixable": fixable_count,
                    "warnings": warn_count
                },
                "effective_mode": effective_mode
            }
        )
        self._append_event(event)
    
    def log_write_attempt(
        self,
        file_path: str,
        template_name: str,
        update_mode: str,
        effective_mode: str,
        overwrite: bool,
        dry_run: bool
    ) -> None:
        """
        Log that file write was attempted.
        
        Args:
            file_path: Target file path
            template_name: Template name
            update_mode: Update mode (replace, merge_sections, append)
            effective_mode: Effective documentation mode
            overwrite: Whether overwrite is enabled
            dry_run: Whether this is a dry run (no actual write)
        """
        event = LogEvent(
            timestamp=self._get_timestamp(),
            event_type="WRITE_ATTEMPT",
            details={
                "file_path": file_path,
                "template_name": template_name,
                "update_mode": update_mode,
                "effective_mode": effective_mode,
                "overwrite": overwrite,
                "dry_run": dry_run
            }
        )
        self._append_event(event)
    
    def log_write_success(
        self,
        file_path: str,
        file_size_bytes: int,
        dry_run: bool = False
    ) -> None:
        """
        Log successful file write.
        
        Args:
            file_path: File path that was written
            file_size_bytes: Size of written file
            dry_run: Whether this was a dry run (preview only)
        """
        event = LogEvent(
            timestamp=self._get_timestamp(),
            event_type="WRITE_SUCCESS",
            details={
                "file_path": file_path,
                "file_size_bytes": file_size_bytes,
                "dry_run": dry_run
            }
        )
        self._append_event(event)
    
    def log_write_failure(
        self,
        file_path: str,
        error_type: str,
        error_message: str
    ) -> None:
        """
        Log failed file write.
        
        Args:
            file_path: Target file path
            error_type: Type of error (PATH_INVALID, WRITE_ERROR, PERMISSION_DENIED, etc.)
            error_message: Detailed error message
        """
        event = LogEvent(
            timestamp=self._get_timestamp(),
            event_type="WRITE_FAILURE",
            details={
                "file_path": file_path,
                "error_type": error_type,
                "error_message": error_message
            }
        )
        self._append_event(event)

    def log_event(self, event: Dict[str, Any]) -> None:
        """Log a raw event payload to the log stream."""
        event_type = event.get("event_type", "CUSTOM_EVENT")
        timestamp = event.get("timestamp", self._get_timestamp())
        details = {k: v for k, v in event.items() if k not in {"event_type", "timestamp"}}
        self._append_event(LogEvent(timestamp=timestamp, event_type=event_type, details=details))
    
    def _append_event(self, event: LogEvent) -> None:
        """
        Append event to in-memory log and optionally to file.
        
        Args:
            event: LogEvent to append
        """
        self.events.append(event)
        
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    event_dict = asdict(event)
                    f.write(json.dumps(event_dict) + '\n')
            except Exception:
                # Silently fail if logging fails - don't break main tool
                pass
    
    def get_events(self) -> List[LogEvent]:
        """
        Get all logged events.
        
        Returns:
            List of LogEvent objects
        """
        return self.events.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of logged events.
        
        Returns:
            Dict with event counts by type
        """
        summary: Dict[str, int] = {}
        for event in self.events:
            event_type = event.event_type
            summary[event_type] = summary.get(event_type, 0) + 1
        return summary
    
    def _get_timestamp(self) -> str:
        """
        Get current timestamp in ISO 8601 format.
        
        Returns:
            Timestamp string
        """
        return datetime.now().isoformat() + "Z"
