#!/usr/bin/env python3
"""
Tag Validation and Normalization Script

Validates documentation tags against centralized tag registry.
Normalizes synonyms to approved feature names.
Checks tag completeness and format compliance.

Usage:
    python validate_tags.py <doc_file>
    python validate_tags.py --registry <registry_path> --check-all <docs_dir>
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import re
import yaml


class TagValidator:
    """Validates and normalizes documentation tags against registry."""
    
    def __init__(self, registry_path: Path):
        """Initialize validator with tag registry.
        
        Args:
            registry_path: Path to tag-registry.json file
        """
        self.registry_path = registry_path
        self.registry = self._load_registry()
        self.feature_synonyms = self._build_synonym_map()
        
    def _load_registry(self) -> Dict:
        """Load and validate tag registry."""
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Tag registry not found: {self.registry_path}")
        
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        # Basic validation
        required_keys = ['version', 'registry']
        for key in required_keys:
            if key not in registry:
                raise ValueError(f"Tag registry missing required key: {key}")
        
        return registry
    
    def _build_synonym_map(self) -> Dict[str, str]:
        """Build mapping from synonyms to approved feature names.
        
        Returns:
            Dict mapping synonym (lowercase) to approved feature name
        """
        synonym_map = {}
        features = self.registry['registry'].get('features', {})
        
        for feature_name, feature_data in features.items():
            if not feature_data.get('approved', False):
                continue
            
            # Add the feature name itself
            synonym_map[feature_name.lower()] = feature_name
            
            # Add all synonyms
            for synonym in feature_data.get('synonyms', []):
                synonym_map[synonym.lower()] = feature_name
        
        return synonym_map
    
    def normalize_feature_name(self, feature: str) -> Optional[str]:
        """Convert feature name or synonym to approved feature name.
        
        Args:
            feature: Feature name or synonym (any case)
            
        Returns:
            Approved feature name, or None if not found
        """
        return self.feature_synonyms.get(feature.lower())
    
    def extract_front_matter(self, file_path: Path) -> Optional[Dict]:
        """Extract YAML front matter from markdown file.
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            Parsed YAML front matter, or None if not found
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for YAML front matter (--- at start and end)
        if not content.startswith('---\n'):
            return None
        
        # Find end of front matter
        end_match = re.search(r'\n---\n', content[4:])
        if not end_match:
            return None
        
        front_matter = content[4:4 + end_match.start()]
        
        try:
            return yaml.safe_load(front_matter)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML front matter: {e}")
    
    def validate_tags(self, tags: Dict) -> Tuple[bool, List[str], List[str]]:
        """Validate tags against registry.
        
        Args:
            tags: Dictionary of tags from front matter
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ['feature', 'domain', 'layer', 'component']
        for field in required_fields:
            if field not in tags:
                errors.append(f"Missing required tag: {field}")
        
        # Validate feature
        if 'feature' in tags:
            feature = tags['feature']
            normalized = self.normalize_feature_name(feature)
            
            if normalized is None:
                errors.append(f"Unknown feature: '{feature}'. Not found in registry.")
            elif normalized != feature:
                warnings.append(
                    f"Feature '{feature}' should be normalized to '{normalized}' "
                    f"(approved name or synonym)"
                )
        
        # Validate domain
        if 'domain' in tags:
            domain = tags['domain']
            approved_domains = self.registry['registry'].get('domains', [])
            if domain not in approved_domains:
                errors.append(
                    f"Unknown domain: '{domain}'. "
                    f"Approved domains: {', '.join(approved_domains)}"
                )
        
        # Validate layer
        if 'layer' in tags:
            layer = tags['layer']
            approved_layers = self.registry['registry'].get('layers', [])
            if layer not in approved_layers:
                errors.append(
                    f"Unknown layer: '{layer}'. "
                    f"Approved layers: {', '.join(approved_layers)}"
                )
        
        # Validate status
        if 'status' in tags:
            status = tags['status']
            approved_statuses = self.registry['registry'].get('statuses', [])
            if status not in approved_statuses:
                errors.append(
                    f"Unknown status: '{status}'. "
                    f"Approved statuses: {', '.join(approved_statuses)}"
                )
        
        # Check component type if present
        if 'componentType' in tags:
            component_type = tags['componentType']
            approved_types = self.registry['registry'].get('componentTypes', [])
            if approved_types and component_type not in approved_types:
                warnings.append(
                    f"Non-standard component type: '{component_type}'. "
                    f"Consider using: {', '.join(approved_types[:5])}"
                )
        
        is_valid = len(errors) == 0
        return is_valid, errors, warnings
    
    def check_tag_completeness(self, tags: Dict) -> Tuple[float, List[str]]:
        """Calculate completeness score for tags.
        
        Args:
            tags: Dictionary of tags from front matter
            
        Returns:
            Tuple of (score 0-1, missing_recommended_fields)
        """
        required_fields = ['feature', 'domain', 'layer', 'component']
        recommended_fields = ['status', 'version', 'componentType', 'description']
        
        present_required = sum(1 for f in required_fields if f in tags)
        present_recommended = sum(1 for f in recommended_fields if f in tags)
        
        # Score: required fields worth 70%, recommended fields worth 30%
        required_score = (present_required / len(required_fields)) * 0.7
        recommended_score = (present_recommended / len(recommended_fields)) * 0.3
        
        total_score = required_score + recommended_score
        
        missing = [f for f in recommended_fields if f not in tags]
        
        return total_score, missing
    
    def validate_file(self, file_path: Path, verbose: bool = False) -> Dict:
        """Validate tags in a documentation file.
        
        Args:
            file_path: Path to markdown file
            verbose: Print detailed output
            
        Returns:
            Validation results dictionary
        """
        results = {
            'file': str(file_path),
            'valid': False,
            'has_tags': False,
            'errors': [],
            'warnings': [],
            'completeness': 0.0,
            'missing_recommended': []
        }
        
        try:
            # Extract front matter
            tags = self.extract_front_matter(file_path)
            
            if tags is None:
                results['errors'].append("No YAML front matter found")
                return results
            
            results['has_tags'] = True
            results['tags'] = tags
            
            # Validate tags
            is_valid, errors, warnings = self.validate_tags(tags)
            results['valid'] = is_valid
            results['errors'] = errors
            results['warnings'] = warnings
            
            # Check completeness
            score, missing = self.check_tag_completeness(tags)
            results['completeness'] = score
            results['missing_recommended'] = missing
            
            if verbose:
                self._print_results(results)
        
        except Exception as e:
            results['errors'].append(f"Error processing file: {str(e)}")
        
        return results
    
    def _print_results(self, results: Dict):
        """Print validation results in human-readable format."""
        file_path = results['file']
        
        print(f"\n{'='*80}")
        print(f"File: {file_path}")
        print(f"{'='*80}")
        
        if not results['has_tags']:
            print("❌ No YAML front matter found")
            return
        
        # Print tags
        print("\n📋 Tags:")
        for key, value in results.get('tags', {}).items():
            print(f"  {key}: {value}")
        
        # Print validation status
        if results['valid']:
            print("\n✅ Tag validation: PASSED")
        else:
            print("\n❌ Tag validation: FAILED")
        
        # Print errors
        if results['errors']:
            print("\n🔴 Errors:")
            for error in results['errors']:
                print(f"  - {error}")
        
        # Print warnings
        if results['warnings']:
            print("\n⚠️  Warnings:")
            for warning in results['warnings']:
                print(f"  - {warning}")
        
        # Print completeness
        score = results['completeness']
        score_pct = score * 100
        print(f"\n📊 Completeness: {score_pct:.0f}%")
        
        if results['missing_recommended']:
            print("  Missing recommended fields:")
            for field in results['missing_recommended']:
                print(f"    - {field}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate documentation tags against registry'
    )
    parser.add_argument(
        'file',
        type=Path,
        nargs='?',
        help='Documentation file to validate'
    )
    parser.add_argument(
        '--registry',
        type=Path,
        default=Path.home() / '.akr' / 'templates' / '.akr' / 'tags' / 'tag-registry.json',
        help='Path to tag registry (default: ~/.akr/templates/.akr/tags/tag-registry.json)'
    )
    parser.add_argument(
        '--check-all',
        type=Path,
        metavar='DIR',
        help='Validate all markdown files in directory'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed results'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.file and not args.check_all:
        parser.error("Either file or --check-all must be specified")
    
    if not args.registry.exists():
        print(f"❌ Tag registry not found: {args.registry}", file=sys.stderr)
        print("   Run setup script or specify correct path with --registry", file=sys.stderr)
        sys.exit(1)
    
    # Initialize validator
    try:
        validator = TagValidator(args.registry)
    except Exception as e:
        print(f"❌ Failed to load tag registry: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Collect files to validate
    files_to_check = []
    if args.file:
        files_to_check.append(args.file)
    elif args.check_all:
        files_to_check = list(args.check_all.rglob('*.md'))
    
    # Validate files
    all_results = []
    for file_path in files_to_check:
        if not file_path.exists():
            print(f"❌ File not found: {file_path}", file=sys.stderr)
            continue
        
        results = validator.validate_file(file_path, verbose=args.verbose and not args.json)
        all_results.append(results)
    
    # Output results
    if args.json:
        print(json.dumps(all_results, indent=2))
    elif not args.verbose:
        # Summary output
        total = len(all_results)
        valid = sum(1 for r in all_results if r['valid'])
        has_tags = sum(1 for r in all_results if r['has_tags'])
        
        print(f"\n{'='*80}")
        print(f"Validation Summary")
        print(f"{'='*80}")
        print(f"Total files: {total}")
        print(f"Files with tags: {has_tags}")
        print(f"Valid tags: {valid}")
        print(f"Invalid tags: {has_tags - valid}")
        print(f"Files without tags: {total - has_tags}")
        
        if has_tags - valid > 0:
            print("\n❌ Some files have invalid tags. Run with --verbose for details.")
            sys.exit(1)
        elif has_tags < total:
            print("\n⚠️  Some files are missing tags.")
            sys.exit(0)
        else:
            print("\n✅ All files have valid tags!")
            sys.exit(0)


if __name__ == '__main__':
    main()
