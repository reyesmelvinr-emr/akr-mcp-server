#!/usr/bin/env python3
"""
Workflow Telemetry Analyzer

Parses enforcement.jsonl telemetry logs to generate workflow health metrics.
Analyzes patterns for:
- Workflow violation rates
- Average operations per documentation
- Duplicate write frequency
- Tool usage patterns
- Performance metrics

Usage:
    python analyze_workflow_telemetry.py [--since "1 hour ago"] [--output metrics.json]
"""

import json
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict


class WorkflowTelemetryAnalyzer:
    """Analyzes workflow telemetry from enforcement.jsonl logs."""
    
    def __init__(self, log_file: str):
        """
        Initialize analyzer.
        
        Args:
            log_file: Path to enforcement.jsonl file
        """
        self.log_file = Path(log_file)
        self.events: List[Dict[str, Any]] = []
        self._load_events()
    
    def _load_events(self) -> None:
        """Load and parse JSON Lines log file."""
        if not self.log_file.exists():
            print(f"Warning: Log file not found: {self.log_file}")
            return
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            event = json.loads(line)
                            self.events.append(event)
                        except json.JSONDecodeError:
                            continue
            print(f"Loaded {len(self.events)} events from {self.log_file}")
        except Exception as e:
            print(f"Error loading log file: {e}", file=sys.stderr)
    
    def filter_by_time(self, since_hours: int = 24) -> None:
        """
        Filter events to only those from the past N hours.
        
        Args:
            since_hours: Number of hours to look back
        """
        cutoff_time = datetime.now() - timedelta(hours=since_hours)
        
        filtered = []
        for event in self.events:
            try:
                event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                if event_time >= cutoff_time:
                    filtered.append(event)
            except (KeyError, ValueError):
                continue
        
        print(f"Filtered to {len(filtered)} events from past {since_hours} hours")
        self.events = filtered
    
    def analyze_workflow_violations(self) -> Dict[str, Any]:
        """
        Analyze workflow violations.
        
        Returns:
            Dict with violation metrics
        """
        total_writes = 0
        direct_write_violations = 0
        bypass_used = 0
        violation_types = defaultdict(int)
        
        for event in self.events:
            event_type = event.get('event_type', '')
            
            if event_type == 'WRITE_ATTEMPT':
                total_writes += 1
            elif event_type == 'WORKFLOW_VIOLATION':
                direct_write_violations += 1
                violation_type = event.get('details', {}).get('violation_type', 'unknown')
                violation_types[violation_type] += 1
            elif event_type == 'WORKFLOW_BYPASS':
                bypass_used += 1
        
        violation_rate = (direct_write_violations / total_writes * 100) if total_writes > 0 else 0
        
        return {
            "total_write_attempts": total_writes,
            "workflow_violations": direct_write_violations,
            "workflow_violation_rate_percent": round(violation_rate, 2),
            "workflow_bypasses_used": bypass_used,
            "violation_types": dict(violation_types)
        }
    
    def analyze_stub_generation(self) -> Dict[str, Any]:
        """
        Analyze stub generation workflow.
        
        Returns:
            Dict with stub generation metrics
        """
        stub_generated = 0
        stub_followed_by_write = 0
        stub_paths = set()
        
        # Track which stubs were followed by writes
        written_paths = set()
        for event in self.events:
            if event.get('event_type') == 'WRITE_SUCCESS':
                path = event.get('details', {}).get('file_path')
                if path:
                    written_paths.add(path)
        
        # Count stubs and check if they were written
        for event in self.events:
            if event.get('event_type') == 'STUB_GENERATED':
                stub_generated += 1
                path = event.get('details', {}).get('doc_path')
                if path:
                    stub_paths.add(path)
                    if path in written_paths:
                        stub_followed_by_write += 1
        
        stub_compliance = (stub_followed_by_write / stub_generated * 100) if stub_generated > 0 else 0
        
        return {
            "stubs_generated": stub_generated,
            "stubs_followed_by_write": stub_followed_by_write,
            "stub_first_compliance_percent": round(stub_compliance, 2),
            "unique_stub_paths": len(stub_paths)
        }
    
    def analyze_duplicate_writes(self) -> Dict[str, Any]:
        """
        Analyze duplicate write patterns.
        
        Returns:
            Dict with duplicate write metrics
        """
        duplicates = 0
        identical_duplicates = 0
        rapid_changes = 0
        paths_with_duplicates = set()
        
        for event in self.events:
            if event.get('event_type') == 'DUPLICATE_WRITE':
                duplicates += 1
                details = event.get('details', {})
                if details.get('is_identical'):
                    identical_duplicates += 1
                path = details.get('doc_path')
                if path:
                    paths_with_duplicates.add(path)
        
        total_writes = sum(1 for e in self.events if e.get('event_type') == 'WRITE_ATTEMPT')
        duplicate_rate = (duplicates / total_writes * 100) if total_writes > 0 else 0
        
        return {
            "duplicate_write_attempts": duplicates,
            "identical_duplicates": identical_duplicates,
            "rapid_change_warnings": rapid_changes,
            "duplicate_write_rate_percent": round(duplicate_rate, 2),
            "unique_paths_with_duplicates": len(paths_with_duplicates)
        }
    
    def analyze_operations_per_doc(self) -> Dict[str, Any]:
        """
        Analyze average operations per documentation generation.
        
        Returns:
            Dict with operation metrics
        """
        # Track operations within each stub generation workflow
        workflows = defaultdict(list)
        current_workflow_id = None
        
        for event in self.events:
            event_type = event.get('event_type')
            
            if event_type == 'STUB_GENERATED':
                current_workflow_id = event.get('details', {}).get('doc_path')
                if current_workflow_id:
                    workflows[current_workflow_id] = []
            
            # Count operations within each workflow
            if current_workflow_id and event_type in [
                'VALIDATION_RUN', 'WRITE_ATTEMPT', 'WRITE_SUCCESS', 
                'DUPLICATE_WRITE', 'WORKFLOW_VIOLATION'
            ]:
                workflows[current_workflow_id].append(event_type)
        
        operations_per_workflow = [len(ops) for ops in workflows.values() if ops]
        
        if operations_per_workflow:
            avg_ops = sum(operations_per_workflow) / len(operations_per_workflow)
            min_ops = min(operations_per_workflow)
            max_ops = max(operations_per_workflow)
            p95_ops = sorted(operations_per_workflow)[int(len(operations_per_workflow) * 0.95)]
        else:
            avg_ops = min_ops = max_ops = p95_ops = 0
        
        return {
            "workflows_tracked": len(workflows),
            "average_operations_per_doc": round(avg_ops, 2),
            "min_operations": min_ops,
            "max_operations": max_ops,
            "p95_operations": p95_ops
        }
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze performance metrics.
        
        Returns:
            Dict with timing metrics
        """
        validation_times = []
        write_times = []
        
        # Parse timing from events (if available in future phases)
        for event in self.events:
            # Extract metrics if available
            details = event.get('details', {})
            
            # This is a placeholder for future enhancement
            # Once operation_metrics are included in logs, we can extract:
            # - validation_ms, write_ms, commit_ms
            # - content_tokens_est, file_size_bytes
        
        return {
            "events_analyzed": len(self.events),
            "performance_metrics_available": False,
            "note": "Detailed timing metrics will be available in Phase 4"
        }
    
    def analyze_tool_usage_patterns(self) -> Dict[str, Any]:
        """
        Analyze tool usage patterns to identify confusion indicators.
        
        Returns:
            Dict with pattern metrics
        """
        event_types = defaultdict(int)
        event_sequence = []
        
        for event in self.events:
            event_type = event.get('event_type', 'UNKNOWN')
            event_types[event_type] += 1
            event_sequence.append(event_type)
        
        # Detect common problematic sequences
        bypass_before_stub = 0
        duplicate_patterns = 0
        
        for i in range(len(event_sequence) - 1):
            if event_sequence[i] == 'WORKFLOW_BYPASS' and event_sequence[i + 1] == 'STUB_GENERATED':
                bypass_before_stub += 1
            if event_sequence[i] == 'DUPLICATE_WRITE' and event_sequence[i + 1] in [
                'WRITE_ATTEMPT', 'VALIDATION_RUN'
            ]:
                duplicate_patterns += 1
        
        return {
            "event_type_distribution": dict(event_types),
            "bypass_before_stub_pattern": bypass_before_stub,
            "duplicate_followed_by_operation": duplicate_patterns,
            "total_event_sequences_analyzed": len(event_sequence)
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive workflow telemetry report.
        
        Returns:
            Complete metrics report
        """
        return {
            "timestamp": datetime.now().isoformat() + "Z",
            "events_analyzed": len(self.events),
            "workflow_violations": self.analyze_workflow_violations(),
            "stub_generation": self.analyze_stub_generation(),
            "duplicate_writes": self.analyze_duplicate_writes(),
            "operations_per_documentation": self.analyze_operations_per_doc(),
            "performance": self.analyze_performance(),
            "tool_usage_patterns": self.analyze_tool_usage_patterns(),
            "health_checks": self._generate_health_checks()
        }
    
    def _generate_health_checks(self) -> Dict[str, Any]:
        """
        Generate health checks based on thresholds.
        
        Returns:
            Health check results with pass/fail/warning status
        """
        violations = self.analyze_workflow_violations()
        duplicates = self.analyze_duplicate_writes()
        ops = self.analyze_operations_per_doc()
        stubs = self.analyze_stub_generation()
        
        checks = {
            "workflow_violations": {
                "threshold": "< 5%",
                "actual": violations['workflow_violation_rate_percent'],
                "status": "PASS" if violations['workflow_violation_rate_percent'] < 5 else "WARN"
            },
            "duplicate_writes": {
                "threshold": "< 10%",
                "actual": duplicates['duplicate_write_rate_percent'],
                "status": "PASS" if duplicates['duplicate_write_rate_percent'] < 10 else "WARN"
            },
            "operations_per_doc": {
                "threshold": "<= 5",
                "actual": ops['average_operations_per_doc'],
                "status": "PASS" if ops['average_operations_per_doc'] <= 5 else "WARN"
            },
            "stub_first_compliance": {
                "threshold": "> 95%",
                "actual": stubs['stub_first_compliance_percent'],
                "status": "PASS" if stubs['stub_first_compliance_percent'] > 95 else "WARN"
            }
        }
        
        return checks


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze AKR workflow telemetry logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze logs from last 24 hours
  python analyze_workflow_telemetry.py
  
  # Analyze logs from last 7 days
  python analyze_workflow_telemetry.py --hours 168
  
  # Output to JSON file
  python analyze_workflow_telemetry.py --output metrics.json
        """
    )
    
    parser.add_argument(
        '--log-file',
        default='logs/enforcement.jsonl',
        help='Path to enforcement.jsonl log file (default: logs/enforcement.jsonl)'
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Analyze logs from past N hours (default: 24)'
    )
    parser.add_argument(
        '--output',
        help='Output file for JSON report (default: stdout)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        default=True,
        help='Pretty-print JSON output (default: true)'
    )
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = WorkflowTelemetryAnalyzer(args.log_file)
    
    # Filter by time
    analyzer.filter_by_time(since_hours=args.hours)
    
    # Generate report
    report = analyzer.generate_report()
    
    # Output report
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2 if args.pretty else None)
        print(f"Report written to: {args.output}")
    else:
        print(json.dumps(report, indent=2 if args.pretty else None))
    
    # Print summary to console
    print("\n=== Workflow Health Summary ===")
    for check, result in report['health_checks'].items():
        status_symbol = "✓" if result['status'] == "PASS" else "⚠"
        print(f"{status_symbol} {check}: {result['actual']} (target: {result['threshold']})")


if __name__ == '__main__':
    main()
