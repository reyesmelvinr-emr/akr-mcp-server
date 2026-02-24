#!/usr/bin/env python3
"""
AKR Validation CLI Tool.

Validate documentation against AKR templates from the command line.

Usage:
    python scripts/akr_validate.py --doc docs/API.md --template lean_baseline_service_template
    python scripts/akr_validate.py --doc docs/API.md --template lean_baseline_service_template --tier TIER_1
    python scripts/akr_validate.py --doc docs/API.md --template lean_baseline_service_template --auto-fix --output json
    python scripts/akr_validate.py --doc docs/API.md --template lean_baseline_service_template --output text

Output:
    JSON (default): Structured output for CI/CD integration
    Text: Human-readable summary with violation details

Exit Codes:
    0: Document is valid (no BLOCKER violations)
    1: Document is invalid (has BLOCKER violations)
    2: Command-line argument error
    3: File not found or read error
    4: Validation engine error
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.validation_library import ValidationEngine, ValidationTier
from tools.template_schema_builder import get_or_create_schema_builder
from resources.template_resolver import TemplateResolver


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate documentation against AKR templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic validation
  python akr_validate.py --doc docs/API.md --template lean_baseline_service_template
  
  # Strict validation (TIER_1)
  python akr_validate.py --doc docs/API.md --template lean_baseline_service_template --tier TIER_1
  
  # With auto-fix suggestions
  python akr_validate.py --doc docs/API.md --template lean_baseline_service_template --auto-fix
  
  # Text output for human review
  python akr_validate.py --doc docs/API.md --template lean_baseline_service_template --output text
  
  # JSON output for CI/CD
  python akr_validate.py --doc docs/API.md --template lean_baseline_service_template --output json
        """,
    )

    parser.add_argument(
        "--doc",
        "--doc-path",
        required=True,
        dest="doc_path",
        help="Path to documentation file to validate (e.g., docs/API.md)",
    )

    parser.add_argument(
        "--template",
        "--template-id",
        required=True,
        dest="template_id",
        help="Template ID to validate against (e.g., lean_baseline_service_template)",
    )

    parser.add_argument(
        "--tier",
        "--tier-level",
        default="TIER_2",
        choices=["TIER_1", "TIER_2", "TIER_3"],
        dest="tier_level",
        help=(
            "Validation strictness level. "
            "TIER_1: strict (≥80%% complete); "
            "TIER_2: moderate (≥60%% complete); "
            "TIER_3: lenient (≥30%% complete). "
            "Default: TIER_2"
        ),
    )

    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Attempt to auto-fix common violations",
    )

    parser.add_argument(
        "--output",
        choices=["json", "text"],
        default="json",
        help="Output format: json (for CI/CD) or text (human-readable). Default: json",
    )

    parser.add_argument(
        "--diff",
        action="store_true",
        help="Show unified diff of auto-fixes (only with --auto-fix and --output text)",
    )

    parser.add_argument(
        "--no-exit-code",
        action="store_true",
        help="Always exit with 0 (useful for warnings-only runs)",
    )

    return parser.parse_args()


def load_document(doc_path: str) -> Optional[str]:
    """Load document content from file."""
    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {doc_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: Failed to read file: {str(e)}", file=sys.stderr)
        return None


def output_json(result, args) -> int:
    """Output validation result as JSON."""
    output = {
        "success": True,
        "is_valid": result.is_valid,
        "completeness_percent": round(result.completeness * 100, 1),
        "tier_level": result.tier_level,
        "violations": [v.to_dict() for v in result.violations],
        "summary": {
            "total_violations": len(result.violations),
            "blockers": sum(1 for v in result.violations if v.severity == "BLOCKER"),
            "fixable": sum(1 for v in result.violations if v.severity == "FIXABLE"),
            "warnings": sum(1 for v in result.violations if v.severity == "WARN"),
        },
    }

    if result.auto_fixed_content and result.diff:
        output["auto_fixed_available"] = True
        output["diff_preview"] = result.diff[:500] + (
            "...[truncated]" if len(result.diff) > 500 else ""
        )
    else:
        output["auto_fixed_available"] = False

    if result.metadata:
        output["metadata"] = {
            "template_source": result.metadata.template_source,
            "validated_at_utc": result.metadata.validated_at_utc,
            "server_version": result.metadata.server_version,
        }

    print(json.dumps(output, indent=2))

    # Exit code
    if args.no_exit_code:
        return 0
    return 0 if result.is_valid else 1


def output_text(result, args) -> int:
    """Output validation result in human-readable format."""
    print("=" * 70)
    print(f"AKR VALIDATION REPORT - {result.tier_level}")
    print("=" * 70)

    # Summary
    print(f"\nDocument Status: {'✓ VALID' if result.is_valid else '✗ INVALID'}")
    print(f"Completeness: {result.completeness * 100:.1f}%")
    print()

    # Violations
    if result.violations:
        print("VIOLATIONS:")
        print("-" * 70)

        # Group by severity
        by_severity = {}
        for v in result.violations:
            severity = v.severity
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(v)

        for severity in ["BLOCKER", "FIXABLE", "WARN"]:
            if severity in by_severity:
                violations = by_severity[severity]
                print(f"\n{severity} ({len(violations)}):")
                for i, v in enumerate(violations, 1):
                    print(f"  {i}. {v.message}")
                    print(f"     Field: {v.field_path}")
                    if v.suggestion:
                        print(f"     → {v.suggestion}")
                    if v.validator:
                        print(f"     Validator: {v.validator}")
    else:
        print("✓ No violations found!")

    # Auto-fix info
    if result.auto_fixed_content and result.diff:
        print("\n" + "=" * 70)
        print("AUTO-FIX AVAILABLE")
        print("=" * 70)
        if args.diff:
            print("\nDIFF:")
            print("-" * 70)
            print(result.diff)
        else:
            print("\nAuto-fixes are available. Use --diff to see changes.")
    elif result.violations and any(v.auto_fixable for v in result.violations):
        print("\n" + "=" * 70)
        print("AUTO-FIX POSSIBLE")
        print("Use --auto-fix flag to generate suggested fixes.")
        print("=" * 70)

    # Summary footer
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("-" * 70)
    total = len(result.violations)
    blockers = sum(1 for v in result.violations if v.severity == "BLOCKER")
    fixable = sum(1 for v in result.violations if v.severity == "FIXABLE")
    warnings = sum(1 for v in result.violations if v.severity == "WARN")
    print(f"Total Violations: {total}")
    print(f"  - Blockers:    {blockers}")
    print(f"  - Fixable:     {fixable}")
    print(f"  - Warnings:    {warnings}")
    print("=" * 70)

    # Exit code
    if args.no_exit_code:
        return 0
    return 0 if result.is_valid else 1


def main() -> int:
    """Main entry point."""
    args = parse_arguments()

    # Load document
    doc_content = load_document(args.doc_path)
    if doc_content is None:
        return 3

    # Initialize validation engine
    try:
        repo_root = Path(__file__).parent.parent
        resolver = TemplateResolver(repo_root=repo_root)
        schema_builder = get_or_create_schema_builder(resolver)
        validation_engine = ValidationEngine(schema_builder=schema_builder)
    except Exception as e:
        print(f"ERROR: Failed to initialize validation engine: {str(e)}", file=sys.stderr)
        return 4

    # Run validation
    try:
        result = validation_engine.validate(
            doc_content=doc_content,
            template_id=args.template_id,
            tier_level=args.tier_level,
            auto_fix=args.auto_fix,
            dry_run=True,  # Always dry-run for CLI; don't modify files
        )
    except Exception as e:
        print(f"ERROR: Validation failed: {str(e)}", file=sys.stderr)
        return 4

    # Output result
    if args.output == "json":
        return output_json(result, args)
    else:  # text
        return output_text(result, args)


if __name__ == "__main__":
    sys.exit(main())
