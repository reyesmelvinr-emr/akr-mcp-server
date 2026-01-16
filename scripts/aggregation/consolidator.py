#!/usr/bin/env python3
"""
Documentation Consolidation Service

Aggregates technical documentation from multiple repositories to generate
high-level feature documentation. Maps relationships between UI, API, and
Database components across repositories based on feature tags.

Architecture:
- Clones/fetches documentation from multiple repos
- Parses front matter tags from documentation files
- Groups components by feature tag
- Maps component relationships (UI -> API -> DB)
- Synthesizes consolidated feature documentation
- Generates cross-repository architecture diagrams

Usage:
    python consolidator.py --config consolidation-config.json
    python consolidator.py --feature ApplicationEditor --output docs/features/
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import subprocess
import tempfile
import yaml
import re


@dataclass
class ComponentInfo:
    """Information about a single component."""
    name: str
    type: str  # Component, Service, Controller, Table, etc.
    layer: str  # UI, API, Database
    repository: str
    source_file: str
    doc_path: str
    feature: str
    domain: str
    status: str
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    endpoints: List[str] = field(default_factory=list)
    tags: Dict = field(default_factory=dict)
    test_sections: Dict[str, Dict] = field(default_factory=dict)  # Extracted testing sections


@dataclass
class FeatureDocumentation:
    """Consolidated documentation for a feature."""
    feature_name: str
    domain: str
    ui_components: List[ComponentInfo]
    api_components: List[ComponentInfo]
    db_components: List[ComponentInfo]
    relationships: List[Tuple[str, str, str]]  # (from, to, relationship_type)


class RepositoryCloner:
    """Handles cloning and updating repositories."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_repo_path(self, repo_url: str, repo_name: str) -> Path:
        """Get or clone repository to cache directory.
        
        Args:
            repo_url: Git repository URL
            repo_name: Repository name for caching
            
        Returns:
            Path to cloned repository
        """
        repo_path = self.cache_dir / repo_name
        
        if repo_path.exists():
            # Update existing repo
            print(f"Updating {repo_name}...")
            subprocess.run(
                ['git', 'pull'],
                cwd=repo_path,
                capture_output=True,
                check=True
            )
        else:
            # Clone repo
            print(f"Cloning {repo_name}...")
            subprocess.run(
                ['git', 'clone', repo_url, str(repo_path)],
                capture_output=True,
                check=True
            )
        
        return repo_path


class DocumentationParser:
    """Parses documentation files and extracts metadata."""
    
    @staticmethod
    def extract_front_matter(file_path: Path) -> Optional[Dict]:
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
    
    @staticmethod
    def extract_description(file_path: Path) -> str:
        """Extract first paragraph after overview as description."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find ## Overview section
        match = re.search(r'## Overview\s+(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if not match:
            return ""
        
        overview = match.group(1).strip()
        
        # Get first paragraph (up to double newline or 200 chars)
        lines = overview.split('\n')
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                break
            if not line.startswith('🤖') and not line.startswith('❓') and not line.startswith('👤'):
                description_lines.append(line)
        
        description = ' '.join(description_lines)
        return description[:200] + '...' if len(description) > 200 else description
    
    @staticmethod
    def extract_sections(file_path: Path, section_names: List[str]) -> Dict[str, str]:
        """Extract specific sections from markdown documentation.
        
        Args:
            file_path: Path to markdown file
            section_names: List of section names to extract
            
        Returns:
            Dictionary mapping section name to content
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = {}
        
        for section_name in section_names:
            # Match section heading (## or ###)
            pattern = rf'(?:^|\n)(#{{{2,3}}}) {re.escape(section_name)}\s+(.+?)(?=\n#{{{2,3}}} |\Z)'
            match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
            
            if match:
                level = match.group(1)
                section_content = match.group(2).strip()
                sections[section_name] = {
                    'level': len(level),
                    'content': section_content
                }
        
        return sections


class DocumentationAggregator:
    """Aggregates documentation from multiple repositories."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.cache_dir = Path(config.get('cacheDir', './.doc-cache'))
        self.cloner = RepositoryCloner(self.cache_dir)
        self.parser = DocumentationParser()
        self.tag_registry = self._load_tag_registry()
    
    def _load_tag_registry(self) -> Dict:
        """Load tag registry for feature normalization."""
        registry_path = Path(self.config.get('tagRegistryPath', '.akr/tags/tag-registry.json'))
        
        if not registry_path.exists():
            print(f"⚠️  Tag registry not found: {registry_path}")
            return {}
        
        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def collect_documentation(self, repo_config: Dict) -> List[ComponentInfo]:
        """Collect all documentation from a repository.
        
        Args:
            repo_config: Repository configuration (url, name, layer, docsPath)
            
        Returns:
            List of ComponentInfo objects
        """
        repo_url = repo_config['url']
        repo_name = repo_config['name']
        layer = repo_config['layer']
        docs_path = repo_config.get('docsPath', 'docs/')
        
        # Clone/update repository
        repo_path = self.cloner.get_repo_path(repo_url, repo_name)
        
        # Find all markdown files in docs path
        docs_dir = repo_path / docs_path
        if not docs_dir.exists():
            print(f"⚠️  Documentation directory not found: {docs_dir}")
            return []
        
        components = []
        
        # Get testing section names from config
        testing_sections = self.config.get('testingSectionNames', [
            'Testing',
            'Test Cases',
            'Test Coverage',
            'Test Strategy',
            'Happy Path Tests',
            'Edge Cases',
            'Performance Tests'
        ])
        
        for doc_file in docs_dir.rglob('*.md'):
            # Extract front matter
            front_matter = self.parser.extract_front_matter(doc_file)
            if not front_matter:
                continue
            
            # Check for required tags
            if 'feature' not in front_matter:
                continue
            
            # Extract description
            description = self.parser.extract_description(doc_file)
            
            # Extract testing sections
            test_sections = self.parser.extract_sections(doc_file, testing_sections)
            
            # Build ComponentInfo
            relative_path = doc_file.relative_to(repo_path)
            
            component = ComponentInfo(
                name=front_matter.get('component', doc_file.stem),
                type=front_matter.get('componentType', 'Unknown'),
                layer=layer,
                repository=repo_name,
                source_file=str(relative_path),
                doc_path=str(relative_path),
                feature=front_matter['feature'],
                domain=front_matter.get('domain', 'Unknown'),
                status=front_matter.get('status', 'unknown'),
                description=description,
                test_sections=test_sections,
                tags=front_matter
            )
            
            components.append(component)
        
        print(f"✅ Collected {len(components)} components from {repo_name}")
        return components
    
    def group_by_feature(self, components: List[ComponentInfo]) -> Dict[str, List[ComponentInfo]]:
        """Group components by feature tag.
        
        Args:
            components: List of all components
            
        Returns:
            Dictionary mapping feature name to list of components
        """
        features = {}
        
        for component in components:
            feature = component.feature
            if feature not in features:
                features[feature] = []
            features[feature].append(component)
        
        return features
    
    def detect_relationships(self, feature_components: List[ComponentInfo]) -> List[Tuple[str, str, str]]:
        """Detect relationships between components based on dependencies.
        
        Args:
            feature_components: Components belonging to same feature
            
        Returns:
            List of (from_component, to_component, relationship_type) tuples
        """
        relationships = []
        
        # Build component name index
        component_by_name = {c.name: c for c in feature_components}
        
        for component in feature_components:
            # Check dependencies
            for dep in component.dependencies:
                if dep in component_by_name:
                    relationships.append((component.name, dep, 'depends_on'))
            
            # Infer UI -> API relationships
            if component.layer == 'UI':
                # Look for API components in same domain
                for api_comp in feature_components:
                    if api_comp.layer == 'API' and api_comp.domain == component.domain:
                        relationships.append((component.name, api_comp.name, 'calls'))
            
            # Infer API -> Database relationships
            if component.layer == 'API':
                # Look for database components in same domain
                for db_comp in feature_components:
                    if db_comp.layer == 'Database' and db_comp.domain == component.domain:
                        relationships.append((component.name, db_comp.name, 'accesses'))
        
        return relationships
    
    def synthesize_feature_documentation(self, feature_name: str, components: List[ComponentInfo]) -> FeatureDocumentation:
        """Create consolidated feature documentation from components.
        
        Args:
            feature_name: Name of the feature
            components: All components implementing this feature
            
        Returns:
            FeatureDocumentation object
        """
        # Separate by layer
        ui_components = [c for c in components if c.layer == 'UI']
        api_components = [c for c in components if c.layer == 'API']
        db_components = [c for c in components if c.layer == 'Database']
        
        # Get domain (use most common domain)
        domains = [c.domain for c in components]
        domain = max(set(domains), key=domains.count) if domains else 'Unknown'
        
        # Detect relationships
        relationships = self.detect_relationships(components)
        
        return FeatureDocumentation(
            feature_name=feature_name,
            domain=domain,
            ui_components=ui_components,
            api_components=api_components,
            db_components=db_components,
            relationships=relationships
        )
    
    def generate_markdown(self, feature_doc: FeatureDocumentation, template_path: Path, output_path: Path, testing_output_path: Optional[Path] = None):
        """Generate markdown documentation from template.
        
        Args:
            feature_doc: Consolidated feature documentation
            template_path: Path to feature template
            output_path: Where to write generated documentation
            testing_output_path: Optional path to testing documentation (for bidirectional linking)
        """
        # Load template
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Build component lists
        ui_list = self._format_component_list(feature_doc.ui_components)
        api_list = self._format_component_list(feature_doc.api_components)
        db_list = self._format_component_list(feature_doc.db_components)
        
        # Build Mermaid diagram
        mermaid_diagram = self._build_mermaid_diagram(feature_doc)
        
        # Calculate relative path to testing doc if provided
        related_testing = ''
        if testing_output_path:
            relative_testing_path = self._get_relative_path(output_path, testing_output_path)
            related_testing = relative_testing_path
        
        # Replace placeholders
        content = template
        replacements = {
            '{FEATURE_NAME}': feature_doc.feature_name,
            '{DOMAIN}': feature_doc.domain,
            '{DATE}': datetime.now().strftime('%Y-%m-%d'),
            '{COMPONENT_COUNT}': str(len(feature_doc.ui_components) + len(feature_doc.api_components) + len(feature_doc.db_components)),
            '{UI_COMPONENT_COUNT}': str(len(feature_doc.ui_components)),
            '{API_COMPONENT_COUNT}': str(len(feature_doc.api_components)),
            '{DB_COMPONENT_COUNT}': str(len(feature_doc.db_components)),
            '{FOR_EACH_UI_COMPONENT}': ui_list,
            '{FOR_EACH_API_COMPONENT}': api_list,
            '{FOR_EACH_DB_COMPONENT}': db_list,
            '{UI_REPO}': ', '.join(set(c.repository for c in feature_doc.ui_components)) if feature_doc.ui_components else 'N/A',
            '{API_REPO}': ', '.join(set(c.repository for c in feature_doc.api_components)) if feature_doc.api_components else 'N/A',
            '{DB_REPO}': ', '.join(set(c.repository for c in feature_doc.db_components)) if feature_doc.db_components else 'N/A',
        }
        
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        # Add relatedTesting to front matter if testing doc exists
        if related_testing:
            content = self._add_front_matter_field(content, 'relatedTesting', related_testing)
            content = self._add_front_matter_field(content, 'lastSynchronized', datetime.now().strftime('%Y-%m-%d'))
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Generated feature documentation: {output_path}")
    
    def generate_testing_documentation(self, feature_doc: FeatureDocumentation, template_path: Path, output_path: Path, feature_output_path: Path):
        """Generate testing documentation from template.
        
        Args:
            feature_doc: Consolidated feature documentation
            template_path: Path to testing template
            output_path: Where to write generated testing documentation
            feature_output_path: Path to the feature documentation (for bidirectional linking)
        """
        # Load template
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Calculate test coverage statistics
        all_components = feature_doc.ui_components + feature_doc.api_components + feature_doc.db_components
        total_tests = sum(1 for c in all_components if c.test_sections)
        test_coverage_pct = (total_tests / len(all_components) * 100) if all_components else 0
        
        # Count test cases by layer
        ui_test_count = sum(1 for c in feature_doc.ui_components if c.test_sections)
        api_test_count = sum(1 for c in feature_doc.api_components if c.test_sections)
        db_test_count = sum(1 for c in feature_doc.db_components if c.test_sections)
        
        # Build testing content
        ui_testing = self._format_testing_sections(feature_doc.ui_components, 'UI')
        api_testing = self._format_testing_sections(feature_doc.api_components, 'API')
        db_testing = self._format_testing_sections(feature_doc.db_components, 'Database')
        
        # Build traceability section
        traceability = self._format_traceability(all_components)
        
        # Calculate relative path to feature doc
        relative_feature_path = self._get_relative_path(output_path, feature_output_path)
        
        # Replace placeholders
        content = template
        replacements = {
            '{FEATURE_NAME}': feature_doc.feature_name,
            '{DOMAIN}': feature_doc.domain,
            '{DATE}': datetime.now().strftime('%Y-%m-%d'),
            '{TEST_COVERAGE_PERCENTAGE}': f"{test_coverage_pct:.1f}",
            '{UI_TEST_COUNT}': str(ui_test_count),
            '{API_TEST_COUNT}': str(api_test_count),
            '{DB_TEST_COUNT}': str(db_test_count),
            '{UI_TEST_CASE_COUNT}': str(ui_test_count),  # Simplified - would count actual test cases in real implementation
            '{API_TEST_CASE_COUNT}': str(api_test_count),
            '{DB_TEST_CASE_COUNT}': str(db_test_count),
            '{INTEGRATION_TEST_COUNT}': '0',  # Placeholder
            '{CRITICAL_TEST_COUNT}': '0',  # Placeholder
            '{REGRESSION_TEST_COUNT}': '0',  # Placeholder
            '{PERFORMANCE_TEST_COUNT}': '0',  # Placeholder
            '{SECURITY_TEST_COUNT}': '0',  # Placeholder
            '{UI_REPO}': ', '.join(set(c.repository for c in feature_doc.ui_components)),
            '{API_REPO}': ', '.join(set(c.repository for c in feature_doc.api_components)),
            '{DB_REPO}': ', '.join(set(c.repository for c in feature_doc.db_components)),
            '{FOR_EACH_UI_COMPONENT}': traceability,
            '{FOR_EACH_API_COMPONENT}': '',
            '{FOR_EACH_DB_COMPONENT}': '',
            '../features/{FEATURE_NAME}.md': relative_feature_path,
        }
        
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Generated testing documentation: {output_path}")
    
    def _format_testing_sections(self, components: List[ComponentInfo], layer: str) -> str:
        """Format testing sections for template."""
        if not components:
            return "*No test information available*"
        
        lines = []
        for comp in components:
            if not comp.test_sections:
                continue
            
            lines.append(f"#### Component: [{comp.name}]({comp.doc_path})")
            lines.append(f"**Test File:** `{comp.source_file}`")
            lines.append("")
            
            for section_name, section_data in comp.test_sections.items():
                lines.append(f"##### {section_name}")
                lines.append(section_data['content'])
                lines.append("")
        
        return '\n'.join(lines) if lines else "*No test information available*"
    
    def _format_traceability(self, components: List[ComponentInfo]) -> str:
        """Format traceability section linking to component docs."""
        lines = []
        
        for comp in components:
            if comp.test_sections:
                lines.append(f"- [{comp.name}]({comp.doc_path}) → Testing sections extracted to this document")
        
        return '\n'.join(lines) if lines else "*No components with testing information*"
    
    def _get_relative_path(self, from_path: Path, to_path: Path) -> str:
        """Calculate relative path from one file to another."""
        try:
            return str(Path(to_path).relative_to(from_path.parent))
        except ValueError:
            # Files not in same tree, return absolute path
            return str(to_path)
    
    def _add_front_matter_field(self, content: str, field_name: str, field_value: str) -> str:
        """Add a field to YAML front matter.
        
        Args:
            content: Markdown content with front matter
            field_name: Name of the field to add
            field_value: Value of the field
            
        Returns:
            Updated markdown content
        """
        if not content.startswith('---\n'):
            return content
        
        # Find end of front matter
        end_match = re.search(r'\n---\n', content[4:])
        if not end_match:
            return content
        
        end_pos = 4 + end_match.start()
        front_matter = content[4:end_pos]
        rest = content[end_pos:]
        
        # Add new field before closing ---
        new_front_matter = f"{front_matter}\n{field_name}: {field_value}"
        
        return f"---\n{new_front_matter}{rest}"
    
    def _format_component_list(self, components: List[ComponentInfo]) -> str:
        """Format component list for template."""
        if not components:
            return "*No components found*"
        
        lines = []
        for comp in components:
            lines.append(f"#### [{comp.name}]({comp.doc_path})")
            lines.append(f"- **Type:** {comp.type}")
            lines.append(f"- **Location:** `{comp.source_file}`")
            lines.append(f"- **Purpose:** {comp.description}")
            lines.append(f"- **Status:** {comp.status}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _build_mermaid_diagram(self, feature_doc: FeatureDocumentation) -> str:
        """Build Mermaid diagram showing component relationships."""
        lines = ["```mermaid", "graph TB"]
        
        # Add nodes by layer
        for comp in feature_doc.ui_components:
            lines.append(f"    {comp.name}[{comp.name}]")
        
        for comp in feature_doc.api_components:
            lines.append(f"    {comp.name}[{comp.name}]")
        
        for comp in feature_doc.db_components:
            lines.append(f"    {comp.name}[({comp.name})]")
        
        # Add relationships
        for from_comp, to_comp, rel_type in feature_doc.relationships:
            label = rel_type.replace('_', ' ')
            lines.append(f"    {from_comp} -->|{label}| {to_comp}")
        
        lines.append("```")
        return '\n'.join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Aggregate and consolidate cross-repository documentation'
    )
    parser.add_argument(
        '--config',
        type=Path,
        required=True,
        help='Path to consolidation configuration file'
    )
    parser.add_argument(
        '--feature',
        type=str,
        help='Generate documentation for specific feature only'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('docs/features'),
        help='Output directory for feature documentation'
    )
    parser.add_argument(
        '--outputs',
        type=str,
        choices=['feature', 'testing', 'all'],
        default='all',
        help='Which documentation types to generate'
    )
    parser.add_argument(
        '--testing-output',
        type=Path,
        default=Path('docs/testing'),
        help='Output directory for testing documentation'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    with open(args.config, 'r') as f:
        config = json.load(f)
    
    # Initialize aggregator
    aggregator = DocumentationAggregator(config)
    
    # Collect documentation from all repositories
    all_components = []
    for repo_config in config['repositories']:
        components = aggregator.collect_documentation(repo_config)
        all_components.extend(components)
    
    print(f"\n📊 Total components collected: {len(all_components)}")
    
    # Group by feature
    features = aggregator.group_by_feature(all_components)
    
    print(f"📋 Features found: {len(features)}")
    for feature_name, components in features.items():
        print(f"   - {feature_name}: {len(components)} components")
    
    # Load templates
    feature_template_path = Path(config.get('featureTemplatePath', '.akr/templates/feature-consolidated.md'))
    testing_template_path = Path(config.get('testingTemplatePath', '.akr/templates/feature-testing-consolidated.md'))
    
    features_to_generate = [args.feature] if args.feature else features.keys()
    
    for feature_name in features_to_generate:
        if feature_name not in features:
            print(f"⚠️  Feature not found: {feature_name}")
            continue
        
        feature_components = features[feature_name]
        feature_doc = aggregator.synthesize_feature_documentation(feature_name, feature_components)
        
        feature_output_file = args.output / f"{feature_name}.md"
        testing_output_file = args.testing_output / f"{feature_name}_Testing.md"
        
        # Generate feature documentation
        if args.outputs in ['feature', 'all']:
            aggregator.generate_markdown(
                feature_doc, 
                feature_template_path, 
                feature_output_file,
                testing_output_file if args.outputs == 'all' else None
            )
        
        # Generate testing documentation
        if args.outputs in ['testing', 'all']:
            aggregator.generate_testing_documentation(
                feature_doc,
                testing_template_path,
                testing_output_file,
                feature_output_file
            )


if __name__ == '__main__':
    main()
