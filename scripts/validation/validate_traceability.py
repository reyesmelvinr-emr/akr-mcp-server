#!/usr/bin/env python3
"""
Documentation Traceability Validation Script

Validates bidirectional links between feature and testing documentation.
Ensures that:
1. Every feature doc with testing has a corresponding testing doc
2. Every testing doc has a corresponding feature doc
3. Bidirectional links are valid (files exist)
4. Front matter contains correct relatedFeature/relatedTesting fields

Usage:
    python validate_traceability.py --docs-dir docs/
    python validate_traceability.py --features-dir docs/features/ --testing-dir docs/testing/
    python validate_traceability.py --fix  # Auto-fix broken links
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
import yaml
import re


@dataclass
class DocumentInfo:
    """Information about a documentation file."""
    path: Path
    feature_name: str
    document_type: str  # 'feature' or 'testing'
    related_doc: Optional[str] = None  # Path from front matter
    last_synchronized: Optional[str] = None


class TraceabilityValidator:
    """Validates traceability between feature and testing documentation."""
    
    def __init__(self, docs_dir: Path = None, features_dir: Path = None, testing_dir: Path = None):
        """Initialize validator.
        
        Args:
            docs_dir: Root documentation directory (if using standard structure)
            features_dir: Features documentation directory
            testing_dir: Testing documentation directory
        """
        if docs_dir:
            self.features_dir = docs_dir / 'features'
            self.testing_dir = docs_dir / 'testing'
        else:
            self.features_dir = features_dir
            self.testing_dir = testing_dir
        
        self.feature_docs: Dict[str, DocumentInfo] = {}
        self.testing_docs: Dict[str, DocumentInfo] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def extract_front_matter(self, file_path: Path) -> Optional[Dict]:
        """Extract YAML front matter from markdown file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---\n'):
            return None
        
        end_match = re.search(r'\n---\n', content[4:])
        if not end_match:
            return None
        
        front_matter = content[4:4 + end_match.start()]
        
        try:
            return yaml.safe_load(front_matter)
        except yaml.YAMLError:
            return None
    
    def scan_documentation(self):
        """Scan all documentation files and extract metadata."""
        print(f"🔍 Scanning feature documentation: {self.features_dir}")
        
        if self.features_dir.exists():
            for doc_file in self.features_dir.rglob('*.md'):
                front_matter = self.extract_front_matter(doc_file)
                if not front_matter or 'feature' not in front_matter:
                    self.warnings.append(f"Missing front matter or feature tag: {doc_file}")
                    continue
                
                feature_name = front_matter['feature']
                doc_info = DocumentInfo(
                    path=doc_file,
                    feature_name=feature_name,
                    document_type='feature',
                    related_doc=front_matter.get('relatedTesting'),
                    last_synchronized=front_matter.get('lastSynchronized')
                )
                
                self.feature_docs[feature_name] = doc_info
        
        print(f"   Found {len(self.feature_docs)} feature documents")
        
        print(f"🔍 Scanning testing documentation: {self.testing_dir}")
        
        if self.testing_dir.exists():
            for doc_file in self.testing_dir.rglob('*.md'):
                front_matter = self.extract_front_matter(doc_file)
                if not front_matter or 'feature' not in front_matter:
                    self.warnings.append(f"Missing front matter or feature tag: {doc_file}")
                    continue
                
                feature_name = front_matter['feature']
                doc_info = DocumentInfo(
                    path=doc_file,
                    feature_name=feature_name,
                    document_type='testing',
                    related_doc=front_matter.get('relatedFeature'),
                    last_synchronized=front_matter.get('lastSynchronized')
                )
                
                self.testing_docs[feature_name] = doc_info
        
        print(f"   Found {len(self.testing_docs)} testing documents")
    
    def validate_bidirectional_links(self) -> bool:
        """Validate that bidirectional links exist and are valid.
        
        Returns:
            True if all links are valid, False otherwise
        """
        print("\n✅ Validating bidirectional links...")
        
        valid = True
        
        # Check feature docs have corresponding testing docs
        for feature_name, feature_doc in self.feature_docs.items():
            if feature_name not in self.testing_docs:
                self.warnings.append(f"Feature '{feature_name}' has no testing documentation")
                continue
            
            testing_doc = self.testing_docs[feature_name]
            
            # Check feature doc has relatedTesting link
            if not feature_doc.related_doc:
                self.errors.append(f"Feature '{feature_name}' missing relatedTesting link")
                valid = False
                continue
            
            # Check relatedTesting link is valid
            expected_testing_path = testing_doc.path.relative_to(feature_doc.path.parent.parent)
            if feature_doc.related_doc != str(expected_testing_path):
                self.errors.append(
                    f"Feature '{feature_name}' has incorrect relatedTesting link: "
                    f"expected '{expected_testing_path}', got '{feature_doc.related_doc}'"
                )
                valid = False
        
        # Check testing docs have corresponding feature docs
        for feature_name, testing_doc in self.testing_docs.items():
            if feature_name not in self.feature_docs:
                self.errors.append(f"Testing doc '{feature_name}' has no corresponding feature doc")
                valid = False
                continue
            
            feature_doc = self.feature_docs[feature_name]
            
            # Check testing doc has relatedFeature link
            if not testing_doc.related_doc:
                self.errors.append(f"Testing '{feature_name}' missing relatedFeature link")
                valid = False
                continue
            
            # Check relatedFeature link is valid
            expected_feature_path = feature_doc.path.relative_to(testing_doc.path.parent.parent)
            if testing_doc.related_doc != str(expected_feature_path):
                self.errors.append(
                    f"Testing '{feature_name}' has incorrect relatedFeature link: "
                    f"expected '{expected_feature_path}', got '{testing_doc.related_doc}'"
                )
                valid = False
        
        return valid
    
    def validate_file_existence(self) -> bool:
        """Validate that all linked files exist.
        
        Returns:
            True if all linked files exist, False otherwise
        """
        print("✅ Validating file existence...")
        
        valid = True
        
        for feature_name, feature_doc in self.feature_docs.items():
            if not feature_doc.path.exists():
                self.errors.append(f"Feature doc does not exist: {feature_doc.path}")
                valid = False
            
            if feature_doc.related_doc:
                related_path = feature_doc.path.parent.parent / feature_doc.related_doc
                if not related_path.exists():
                    self.errors.append(
                        f"Feature '{feature_name}' links to non-existent testing doc: {related_path}"
                    )
                    valid = False
        
        for feature_name, testing_doc in self.testing_docs.items():
            if not testing_doc.path.exists():
                self.errors.append(f"Testing doc does not exist: {testing_doc.path}")
                valid = False
            
            if testing_doc.related_doc:
                related_path = testing_doc.path.parent.parent / testing_doc.related_doc
                if not related_path.exists():
                    self.errors.append(
                        f"Testing '{feature_name}' links to non-existent feature doc: {related_path}"
                    )
                    valid = False
        
        return valid
    
    def validate_synchronization(self) -> bool:
        """Check if documents are synchronized (have matching timestamps).
        
        Returns:
            True if all documents are synchronized, False otherwise
        """
        print("✅ Validating synchronization timestamps...")
        
        synchronized = True
        
        for feature_name in set(self.feature_docs.keys()) & set(self.testing_docs.keys()):
            feature_doc = self.feature_docs[feature_name]
            testing_doc = self.testing_docs[feature_name]
            
            if not feature_doc.last_synchronized or not testing_doc.last_synchronized:
                self.warnings.append(f"Feature '{feature_name}' missing synchronization timestamp")
                continue
            
            if feature_doc.last_synchronized != testing_doc.last_synchronized:
                self.warnings.append(
                    f"Feature '{feature_name}' documentation out of sync: "
                    f"feature={feature_doc.last_synchronized}, testing={testing_doc.last_synchronized}"
                )
                synchronized = False
        
        return synchronized
    
    def generate_report(self) -> Dict:
        """Generate comprehensive traceability report.
        
        Returns:
            Dictionary with validation results
        """
        report = {
            'total_features': len(self.feature_docs),
            'total_testing_docs': len(self.testing_docs),
            'matched_pairs': len(set(self.feature_docs.keys()) & set(self.testing_docs.keys())),
            'orphaned_features': list(set(self.feature_docs.keys()) - set(self.testing_docs.keys())),
            'orphaned_testing': list(set(self.testing_docs.keys()) - set(self.feature_docs.keys())),
            'broken_links': [],
            'missing_links': [],
            'out_of_sync': [],
            'errors': self.errors,
            'warnings': self.warnings
        }
        
        # Categorize errors
        for error in self.errors:
            if 'missing' in error.lower():
                report['missing_links'].append(error)
            elif 'incorrect' in error.lower() or 'non-existent' in error.lower():
                report['broken_links'].append(error)
        
        # Categorize warnings
        for warning in self.warnings:
            if 'out of sync' in warning.lower():
                report['out_of_sync'].append(warning)
        
        return report
    
    def print_report(self, report: Dict):
        """Print human-readable validation report."""
        print("\n" + "="*70)
        print("📊 TRACEABILITY VALIDATION REPORT")
        print("="*70)
        
        print(f"\n📈 Statistics:")
        print(f"   Total feature docs: {report['total_features']}")
        print(f"   Total testing docs: {report['total_testing_docs']}")
        print(f"   Matched pairs: {report['matched_pairs']}")
        
        if report['orphaned_features']:
            print(f"\n⚠️  Orphaned feature docs (no testing): {len(report['orphaned_features'])}")
            for feature in report['orphaned_features'][:5]:
                print(f"      - {feature}")
            if len(report['orphaned_features']) > 5:
                print(f"      ... and {len(report['orphaned_features']) - 5} more")
        
        if report['orphaned_testing']:
            print(f"\n🔴 Orphaned testing docs (no feature): {len(report['orphaned_testing'])}")
            for feature in report['orphaned_testing'][:5]:
                print(f"      - {feature}")
            if len(report['orphaned_testing']) > 5:
                print(f"      ... and {len(report['orphaned_testing']) - 5} more")
        
        if report['missing_links']:
            print(f"\n🔴 Missing links: {len(report['missing_links'])}")
            for error in report['missing_links'][:5]:
                print(f"      - {error}")
            if len(report['missing_links']) > 5:
                print(f"      ... and {len(report['missing_links']) - 5} more")
        
        if report['broken_links']:
            print(f"\n🔴 Broken links: {len(report['broken_links'])}")
            for error in report['broken_links'][:5]:
                print(f"      - {error}")
            if len(report['broken_links']) > 5:
                print(f"      ... and {len(report['broken_links']) - 5} more")
        
        if report['out_of_sync']:
            print(f"\n⚠️  Out of sync: {len(report['out_of_sync'])}")
            for warning in report['out_of_sync'][:5]:
                print(f"      - {warning}")
            if len(report['out_of_sync']) > 5:
                print(f"      ... and {len(report['out_of_sync']) - 5} more")
        
        print("\n" + "="*70)
        
        # Summary
        if not report['errors']:
            print("✅ VALIDATION PASSED - All traceability links are valid")
        else:
            print(f"🔴 VALIDATION FAILED - {len(report['errors'])} errors found")
        
        if report['warnings']:
            print(f"⚠️  {len(report['warnings'])} warnings")
        
        print("="*70 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate traceability between feature and testing documentation'
    )
    parser.add_argument(
        '--docs-dir',
        type=Path,
        help='Root documentation directory (expects docs/features/ and docs/testing/)'
    )
    parser.add_argument(
        '--features-dir',
        type=Path,
        help='Features documentation directory'
    )
    parser.add_argument(
        '--testing-dir',
        type=Path,
        help='Testing documentation directory'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Auto-fix broken links (not yet implemented)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output report as JSON'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.docs_dir and (not args.features_dir or not args.testing_dir):
        parser.error("Must provide either --docs-dir or both --features-dir and --testing-dir")
    
    # Initialize validator
    validator = TraceabilityValidator(
        docs_dir=args.docs_dir,
        features_dir=args.features_dir,
        testing_dir=args.testing_dir
    )
    
    # Scan documentation
    validator.scan_documentation()
    
    # Validate
    links_valid = validator.validate_bidirectional_links()
    files_exist = validator.validate_file_existence()
    in_sync = validator.validate_synchronization()
    
    # Generate report
    report = validator.generate_report()
    
    if args.json:
        import json
        print(json.dumps(report, indent=2))
    else:
        validator.print_report(report)
    
    # Exit with appropriate code
    if report['errors']:
        sys.exit(1)
    elif report['warnings']:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
