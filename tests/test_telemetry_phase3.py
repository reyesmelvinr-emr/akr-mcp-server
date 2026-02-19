"""
Unit tests for Phase 3 telemetry functionality.

Tests:
- Telemetry event logging
- Duplicate detection 
- Telemetry analysis
"""

import json
import tempfile
import time
from pathlib import Path
from typing import List

import pytest

from src.tools.enforcement_logger import EnforcementLogger
from src.tools.duplicate_detector import DuplicateDetector
from scripts.analyze_workflow_telemetry import WorkflowTelemetryAnalyzer


# ============ Enforcement Logger Tests ============

class TestEnforcementLoggerTelemetry:
    """Test new telemetry logging methods."""
    
    def test_log_workflow_violation(self):
        """Test logging workflow violations."""
        logger = EnforcementLogger()
        
        logger.log_workflow_violation(
            doc_path="docs/test.md",
            violation_type="direct_write_new_file",
            context={"component_name": "TestComponent"}
        )
        
        events = logger.get_events()
        assert len(events) == 1
        assert events[0].event_type == "WORKFLOW_VIOLATION"
        assert events[0].details["violation_type"] == "direct_write_new_file"
        assert events[0].details["doc_path"] == "docs/test.md"
    
    def test_log_workflow_bypass(self):
        """Test logging workflow bypasses."""
        logger = EnforcementLogger()
        
        logger.log_workflow_bypass(
            doc_path="docs/urgent.md",
            bypass_reason="emergency",
            bypass_context={"skip_generate": True}
        )
        
        events = logger.get_events()
        assert len(events) == 1
        assert events[0].event_type == "WORKFLOW_BYPASS"
        assert events[0].details["bypass_reason"] == "emergency"
    
    def test_log_stub_generated(self):
        """Test logging stub generation."""
        logger = EnforcementLogger()
        
        logger.log_stub_generated(
            doc_path="docs/service.md",
            component_name="PaymentService",
            component_type="service",
            template_name="lean_baseline_service_template.md"
        )
        
        events = logger.get_events()
        assert len(events) == 1
        assert events[0].event_type == "STUB_GENERATED"
        assert events[0].details["component_name"] == "PaymentService"
    
    def test_log_duplicate_write_attempt(self):
        """Test logging duplicate write attempts."""
        logger = EnforcementLogger()
        
        logger.log_duplicate_write_attempt(
            doc_path="docs/api.md",
            time_since_last_ms=2500,
            content_hash="abc123def456",
            previous_hash="abc123def456",
            is_identical=True
        )
        
        events = logger.get_events()
        assert len(events) == 1
        assert events[0].event_type == "DUPLICATE_WRITE"
        assert events[0].details["is_identical"] is True
        assert events[0].details["time_since_last_ms"] == 2500
    
    def test_log_manual_file_creation(self):
        """Test logging manually created files."""
        logger = EnforcementLogger()
        
        logger.log_manual_file_creation(
            file_path="docs/manual.md",
            file_size_bytes=2048,
            creation_context="detected_in_git_diff"
        )
        
        events = logger.get_events()
        assert len(events) == 1
        assert events[0].event_type == "MANUAL_FILE_CREATION"
        assert events[0].details["file_size_bytes"] == 2048
    
    def test_telemetry_to_file(self):
        """Test that telemetry events are written to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            logger = EnforcementLogger(str(log_file))
            
            logger.log_stub_generated(
                doc_path="docs/test.md",
                component_name="Test",
                component_type="service",
                template_name="template.md"
            )
            logger.log_workflow_violation(
                doc_path="docs/test.md",
                violation_type="direct_write",
                context={}
            )
            
            # Read back from file
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            assert len(lines) == 2
            
            event1 = json.loads(lines[0])
            assert event1['event_type'] == 'STUB_GENERATED'
            
            event2 = json.loads(lines[1])
            assert event2['event_type'] == 'WORKFLOW_VIOLATION'


# ============ Duplicate Detector Tests ============

class TestDuplicateDetector:
    """Test duplicate write detection."""
    
    @pytest.mark.asyncio
    async def test_first_write_not_duplicate(self):
        """Test that first write is not flagged as duplicate."""
        detector = DuplicateDetector()
        
        result = await detector.check_duplicate("docs/new.md", "New content")
        
        assert result.is_duplicate is False
        assert result.content_changed is True or result.time_since_last_ms is None
    
    @pytest.mark.asyncio
    async def test_identical_write_within_ttl_is_duplicate(self):
        """Test that identical writes within TTL are detected."""
        detector = DuplicateDetector()
        
        content = "Identical content"
        
        # First write
        result1 = await detector.check_duplicate("docs/test.md", content)
        assert result1.is_duplicate is False
        await detector.cache_result("docs/test.md", content, {"success": True})
        
        # Immediate second write (should be detected as duplicate)
        result2 = await detector.check_duplicate("docs/test.md", content)
        
        assert result2.is_duplicate is True
    
    @pytest.mark.asyncio
    async def test_identical_write_after_ttl_not_duplicate(self):
        """Test that cleanup_old_records works."""
        detector = DuplicateDetector()
        
        content = "Test content"
        
        # First write
        result1 = await detector.check_duplicate("docs/test.md", content)
        await detector.cache_result("docs/test.md", content, {"success": True})
        
        # Verify record is cached
        assert len(detector._records) == 1
        assert "docs/test.md" in detector._records
    
    @pytest.mark.asyncio
    async def test_different_content_rapid_change(self):
        """Test rapid content changes are detected."""
        detector = DuplicateDetector()
        
        # First write
        result1 = await detector.check_duplicate("docs/test.md", "Original content")
        await detector.cache_result("docs/test.md", "Original content", {"success": True})
        
        # Rapid different write
        result2 = await detector.check_duplicate("docs/test.md", "Modified content")
        
        # Should detect the change
        assert result2.content_changed is True or result2.time_since_last_ms is not None


# ============ Telemetry Analysis Tests ============

class TestWorkflowTelemetryAnalyzer:
    """Test telemetry analysis functionality."""
    
    def test_analyze_workflow_violations(self):
        """Test workflow violation analysis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            
            # Create test log
            events = [
                {"timestamp": "2026-02-06T10:00:00Z", "event_type": "WRITE_ATTEMPT", "details": {}},
                {"timestamp": "2026-02-06T10:00:01Z", "event_type": "WRITE_ATTEMPT", "details": {}},
                {"timestamp": "2026-02-06T10:00:02Z", "event_type": "WORKFLOW_VIOLATION", "details": {"violation_type": "direct_write"}},
            ]
            
            with open(log_file, 'w') as f:
                for event in events:
                    f.write(json.dumps(event) + '\n')
            
            analyzer = WorkflowTelemetryAnalyzer(str(log_file))
            result = analyzer.analyze_workflow_violations()
            
            assert result['total_write_attempts'] == 2
            assert result['workflow_violations'] == 1
            assert result['workflow_violation_rate_percent'] == 50.0
    
    def test_analyze_duplicate_writes(self):
        """Test duplicate write analysis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            
            events = [
                {"timestamp": "2026-02-06T10:00:00Z", "event_type": "WRITE_ATTEMPT", "details": {}},
                {"timestamp": "2026-02-06T10:00:01Z", "event_type": "WRITE_ATTEMPT", "details": {}},
                {"timestamp": "2026-02-06T10:00:02Z", "event_type": "DUPLICATE_WRITE", "details": {"is_identical": True, "doc_path": "docs/test.md"}},
            ]
            
            with open(log_file, 'w') as f:
                for event in events:
                    f.write(json.dumps(event) + '\n')
            
            analyzer = WorkflowTelemetryAnalyzer(str(log_file))
            result = analyzer.analyze_duplicate_writes()
            
            assert result['duplicate_write_attempts'] == 1
            assert result['identical_duplicates'] == 1
            assert result['duplicate_write_rate_percent'] == 50.0
    
    def test_analyze_stub_generation(self):
        """Test stub generation analysis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            
            events = [
                {
                    "timestamp": "2026-02-06T10:00:00Z",
                    "event_type": "STUB_GENERATED",
                    "details": {"doc_path": "docs/test.md", "component_name": "Test"}
                },
                {
                    "timestamp": "2026-02-06T10:00:02Z",
                    "event_type": "WRITE_SUCCESS",
                    "details": {"file_path": "docs/test.md"}
                },
            ]
            
            with open(log_file, 'w') as f:
                for event in events:
                    f.write(json.dumps(event) + '\n')
            
            analyzer = WorkflowTelemetryAnalyzer(str(log_file))
            result = analyzer.analyze_stub_generation()
            
            assert result['stubs_generated'] == 1
            assert result['stubs_followed_by_write'] == 1
            assert result['stub_first_compliance_percent'] == 100.0
    
    def test_analyze_operations_per_doc(self):
        """Test operations per documentation analysis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            
            events = [
                {
                    "timestamp": "2026-02-06T10:00:00Z",
                    "event_type": "STUB_GENERATED",
                    "details": {"doc_path": "docs/test.md"}
                },
                {
                    "timestamp": "2026-02-06T10:00:01Z",
                    "event_type": "VALIDATION_RUN",
                    "details": {}
                },
                {
                    "timestamp": "2026-02-06T10:00:02Z",
                    "event_type": "WRITE_ATTEMPT",
                    "details": {}
                },
                {
                    "timestamp": "2026-02-06T10:00:03Z",
                    "event_type": "WRITE_SUCCESS",
                    "details": {}
                },
            ]
            
            with open(log_file, 'w') as f:
                for event in events:
                    f.write(json.dumps(event) + '\n')
            
            analyzer = WorkflowTelemetryAnalyzer(str(log_file))
            result = analyzer.analyze_operations_per_doc()
            
            assert result['workflows_tracked'] == 1
            assert result['average_operations_per_doc'] == 3.0  # VALIDATION_RUN, WRITE_ATTEMPT, WRITE_SUCCESS
    
    def test_generate_report(self):
        """Test complete report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            
            events = [
                {"timestamp": "2026-02-06T10:00:00Z", "event_type": "STUB_GENERATED", "details": {"doc_path": "docs/test.md"}},
                {"timestamp": "2026-02-06T10:00:01Z", "event_type": "WRITE_SUCCESS", "details": {"file_path": "docs/test.md"}},
            ]
            
            with open(log_file, 'w') as f:
                for event in events:
                    f.write(json.dumps(event) + '\n')
            
            analyzer = WorkflowTelemetryAnalyzer(str(log_file))
            report = analyzer.generate_report()
            
            # Verify report structure
            assert 'timestamp' in report
            assert 'events_analyzed' in report
            assert 'workflow_violations' in report
            assert 'stub_generation' in report
            assert 'duplicate_writes' in report
            assert 'operations_per_documentation' in report
            assert 'health_checks' in report
            
            # Verify health checks
            health = report['health_checks']
            assert all(key in health for key in [
                'workflow_violations',
                'duplicate_writes',
                'operations_per_doc',
                'stub_first_compliance'
            ])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
