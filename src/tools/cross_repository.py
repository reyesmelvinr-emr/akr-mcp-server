"""
Cross-Repository Documentation Consolidation Module

Handles cloning, scanning, and consolidating documentation from multiple repositories.
Implements branch management strategy: reads from main/stable branches only.
"""

import asyncio
import datetime
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class CrossRepositoryManager:
    """Manages cross-repository documentation consolidation.
    
    Key Features:
    - Clones/updates component repositories (main branch only)
    - Collects documentation by feature tags
    - Maps relationships between components
    - Generates consolidated feature documentation
    - Creates feature branches for review (never commits to main)
    - Creates pull requests with auto-assigned reviewers
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize cross-repository manager.
        
        Args:
            config: Configuration dictionary with crossRepository settings
        """
        self.config = config
        self.cross_repo_config = config.get('crossRepository', {})
        
        # Cache configuration
        cache_dir = self.cross_repo_config.get('cache', {}).get('directory', '~/.akr/repos')
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Related repositories
        self.repositories = self.cross_repo_config.get('relatedRepositories', [])
        
        # Consolidation configuration
        self.consolidation_config = self.cross_repo_config.get('consolidation', {})
        
        # Tag registry
        self.tag_registry = self._load_tag_registry()
        
        logger.info(f"Initialized CrossRepositoryManager with {len(self.repositories)} repositories")
    
    def _load_tag_registry(self) -> Dict[str, Any]:
        """Load tag registry for feature validation."""
        try:
            registry_path = self.cross_repo_config.get('tagRegistry', {}).get('path', '.akr/tags/tag-registry.json')
            registry_file = Path(registry_path)
            
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Tag registry not found: {registry_file}")
                return {'registry': {'features': {}}}
        except Exception as e:
            logger.error(f"Failed to load tag registry: {e}")
            return {'registry': {'features': {}}}
    
    def clone_or_update_repositories(self) -> None:
        """Clone or update all related repositories to cache directory.
        
        CRITICAL: Only clones/updates the SPECIFIED BRANCH from configuration.
        Feature branches are intentionally excluded to ensure consolidated 
        documentation reflects approved, production-ready content only.
        """
        logger.info("Updating related repositories...")
        
        for repo in self.repositories:
            if not repo.get('enabled', True):
                logger.info(f"Skipping disabled repository: {repo['name']}")
                continue
            
            repo_name = repo['name']
            branch = repo['branch']  # Explicit branch from config (main/master)
            repo_path = self.cache_dir / repo_name
            
            logger.info(f"Processing {repo_name} (target branch: {branch})")
            
            try:
                if repo_path.exists():
                    # Verify current branch matches config
                    current_branch = self._get_current_branch(repo_path)
                    if current_branch != branch:
                        logger.warning(
                            f"{repo_name}: Switching from {current_branch} to {branch}"
                        )
                        self._git_checkout(repo_path, branch)
                    
                    # Update existing repo to latest on specified branch
                    self._git_pull(repo_path, branch)
                    logger.info(f"✓ {repo_name}: Updated to latest on {branch}")
                else:
                    # Clone new repo with ONLY specified branch (single-branch clone)
                    self._git_clone_single_branch(repo['url'], repo_path, branch)
                    logger.info(f"✓ {repo_name}: Cloned {branch} branch")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to update {repo_name}: {e}")
                raise
    
    def _git_clone_single_branch(self, url: str, path: Path, branch: str) -> None:
        """Clone repository with only the specified branch.
        
        Uses --single-branch and --depth 1 for performance:
        - Only fetches target branch (not all branches)
        - Shallow clone (only latest commit)
        - 80-90% faster, 95% less disk space
        
        Args:
            url: Repository URL
            path: Local path for clone
            branch: Target branch name
        """
        logger.info(f"Cloning {url} (branch: {branch}) to {path}")
        
        subprocess.run([
            'git', 'clone',
            '--single-branch',  # Only fetch specified branch
            '--branch', branch,  # Target branch
            '--depth', '1',      # Shallow clone
            url, str(path)
        ], check=True, capture_output=True, text=True)
        
        logger.info(f"✓ Cloned {url} successfully")
    
    def _get_current_branch(self, repo_path: Path) -> str:
        """Get currently checked out branch.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Current branch name
        """
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    
    def _git_checkout(self, repo_path: Path, branch: str) -> None:
        """Switch to specified branch.
        
        Args:
            repo_path: Path to repository
            branch: Target branch name
        """
        subprocess.run(
            ['git', 'checkout', branch],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Checked out branch: {branch}")
    
    def _git_pull(self, repo_path: Path, branch: str) -> None:
        """Pull latest changes from specified branch.
        
        Args:
            repo_path: Path to repository
            branch: Target branch name
        """
        subprocess.run(
            ['git', 'pull', 'origin', branch],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
    
    def detect_changes(self, since: str, author: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Detect which features were affected by recent changes.
        
        Only scans the configured branch (main/master) for changes.
        Feature branch commits are intentionally excluded.
        
        Args:
            since: Time reference (e.g., 'yesterday', '7d', '2026-01-10')
            author: Optional author email filter
            
        Returns:
            Dictionary mapping feature names to lists of changes
        """
        logger.info(f"Detecting changes since: {since}")
        affected_features = {}
        
        for repo in self.repositories:
            if not repo.get('enabled', True):
                continue
                
            repo_name = repo['name']
            repo_path = self.cache_dir / repo_name
            
            if not repo_path.exists():
                logger.warning(f"Repository not cloned: {repo_name}")
                continue
            
            try:
                changes = self._get_git_changes(repo_path, since, author)
                
                for changed_file, change_info in changes.items():
                    feature = self._extract_feature_from_file(repo_path / changed_file)
                    if feature:
                        if feature not in affected_features:
                            affected_features[feature] = []
                        affected_features[feature].append({
                            'repository': repo_name,
                            'layer': repo['layer'],
                            'file': changed_file,
                            'timestamp': change_info['timestamp'],
                            'author': change_info['author']
                        })
            except Exception as e:
                logger.error(f"Failed to detect changes in {repo_name}: {e}")
        
        logger.info(f"Found {len(affected_features)} affected features")
        return affected_features
    
    def _get_git_changes(self, repo_path: Path, since: str, author: Optional[str] = None) -> Dict[str, Dict[str, str]]:
        """Get changed files from git log.
        
        Args:
            repo_path: Path to repository
            since: Time reference
            author: Optional author filter
            
        Returns:
            Dictionary mapping file paths to change information
        """
        cmd = [
            'git', 'log',
            f'--since={since}',
            '--name-only',
            '--format=%H|%an|%ae|%ad|%s'
        ]
        
        if author:
            cmd.append(f'--author={author}')
        
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        changes = {}
        current_commit = None
        
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                # Commit info line
                parts = line.split('|')
                current_commit = {
                    'sha': parts[0],
                    'author': parts[1],
                    'email': parts[2],
                    'timestamp': parts[3],
                    'message': parts[4] if len(parts) > 4 else ''
                }
            elif line and current_commit and not line.startswith(' '):
                # File path line
                changes[line] = {
                    'timestamp': current_commit['timestamp'],
                    'author': current_commit['email']
                }
        
        return changes
    
    def _extract_feature_from_file(self, file_path: Path) -> Optional[str]:
        """Extract feature tag from documentation file's YAML front matter.
        
        Args:
            file_path: Path to documentation file
            
        Returns:
            Feature name or None
        """
        if not file_path.exists() or not file_path.suffix == '.md':
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract YAML front matter
            if content.startswith('---'):
                end_idx = content.find('---', 3)
                if end_idx > 0:
                    front_matter = content[3:end_idx]
                    for line in front_matter.split('\n'):
                        if line.startswith('feature:'):
                            return line.split(':', 1)[1].strip()
        except Exception as e:
            logger.error(f"Failed to extract feature from {file_path}: {e}")
        
        return None
    
    def consolidate_feature(self, feature_name: str) -> Dict[str, Any]:
        """Generate consolidated documentation for a feature.
        
        Creates feature branch in aggregator repo for team review
        before publishing to main branch.
        
        Args:
            feature_name: Name of feature to consolidate
            
        Returns:
            Dictionary with keys:
                - feature_branch: Name of created feature branch
                - output_file: Path to generated documentation  
                - pr_url: URL of created pull request (if autoCreatePR enabled)
                - component_count: Number of components consolidated
        """
        logger.info(f"Consolidating feature: {feature_name}")
        
        # Step 1: Collect components from source repos (main branch only)
        logger.info(f"Collecting components for {feature_name}...")
        components = self._collect_components_by_feature(feature_name)
        
        if not components:
            raise ValueError(f"No components found for feature: {feature_name}")
        
        # Step 2: Map relationships
        logger.info("Mapping relationships...")
        relationships = self._map_relationships(components)
        
        # Step 3: Generate diagram
        logger.info("Generating architecture diagram...")
        diagram = self._generate_mermaid_diagram(components, relationships)
        
        # Step 4: Load template
        template = self._load_template()
        
        # Step 5: Create feature branch in aggregator repo (NOT main)
        feature_branch = self._create_consolidation_branch(feature_name)
        logger.info(f"Created feature branch: {feature_branch}")
        
        # Step 6: Synthesize documentation
        output_path = Path(self.consolidation_config.get('outputPath', 'docs/features/'))
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / f"{feature_name}.md"
        
        output = self._synthesize_documentation(
            template, 
            feature_name, 
            components, 
            relationships, 
            diagram
        )
        
        # Step 7: Write to output file
        output_file.write_text(output, encoding='utf-8')
        logger.info(f"Generated: {output_file}")
        
        # Step 8: Commit to feature branch
        self._commit_consolidated_docs(feature_branch, feature_name, output_file)
        
        # Step 9: Push feature branch
        self._push_branch(feature_branch)
        
        # Step 10: Create pull request (if configured)
        pr_url = None
        output_branch_config = self.consolidation_config.get('outputBranch', {})
        if output_branch_config.get('autoCreatePR', True):
            pr_url = self._create_pull_request(feature_branch, feature_name, components)
            logger.info(f"Created PR: {pr_url}")
        
        return {
            'feature_branch': feature_branch,
            'output_file': str(output_file),
            'pr_url': pr_url,
            'component_count': len(components)
        }
    
    def _collect_components_by_feature(self, feature_name: str) -> List[Dict[str, Any]]:
        """Collect all components tagged with specified feature.
        
        Args:
            feature_name: Feature to search for
            
        Returns:
            List of component dictionaries with metadata
        """
        components = []
        
        for repo in self.repositories:
            if not repo.get('enabled', True):
                continue
            
            repo_name = repo['name']
            repo_path = self.cache_dir / repo_name
            docs_path = repo_path / repo.get('docsPath', 'docs/')
            
            if not docs_path.exists():
                continue
            
            # Scan all .md files in docs directory
            for md_file in docs_path.rglob('*.md'):
                feature = self._extract_feature_from_file(md_file)
                if feature == feature_name:
                    components.append({
                        'name': md_file.stem,
                        'path': str(md_file),
                        'repository': repo_name,
                        'layer': repo['layer'],
                        'feature': feature_name
                    })
        
        logger.info(f"Collected {len(components)} components for feature: {feature_name}")
        return components
    
    def _map_relationships(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map relationships between components.
        
        Args:
            components: List of component dictionaries
            
        Returns:
            List of relationship dictionaries
        """
        # Simplified relationship mapping - can be enhanced
        relationships = []
        
        # Group by layer
        by_layer = {}
        for comp in components:
            layer = comp['layer']
            if layer not in by_layer:
                by_layer[layer] = []
            by_layer[layer].append(comp)
        
        # Infer UI → API relationships
        if 'UI' in by_layer and 'API' in by_layer:
            for ui_comp in by_layer['UI']:
                for api_comp in by_layer['API']:
                    relationships.append({
                        'source': ui_comp['name'],
                        'target': api_comp['name'],
                        'type': 'calls'
                    })
        
        # Infer API → Database relationships
        if 'API' in by_layer and 'Database' in by_layer:
            for api_comp in by_layer['API']:
                for db_comp in by_layer['Database']:
                    relationships.append({
                        'source': api_comp['name'],
                        'target': db_comp['name'],
                        'type': 'queries'
                    })
        
        return relationships
    
    def _generate_mermaid_diagram(self, components: List[Dict[str, Any]], 
                                  relationships: List[Dict[str, Any]]) -> str:
        """Generate Mermaid diagram from components and relationships.
        
        Args:
            components: List of component dictionaries
            relationships: List of relationship dictionaries
            
        Returns:
            Mermaid diagram as string
        """
        lines = ["```mermaid", "graph TD"]
        
        # Add nodes
        for comp in components:
            node_id = comp['name'].replace(' ', '_')
            lines.append(f"    {node_id}[{comp['name']}]")
        
        # Add edges
        for rel in relationships:
            source = rel['source'].replace(' ', '_')
            target = rel['target'].replace(' ', '_')
            rel_type = rel['type']
            lines.append(f"    {source} -->|{rel_type}| {target}")
        
        lines.append("```")
        return '\n'.join(lines)
    
    def _load_template(self) -> str:
        """Load consolidation template.
        
        Returns:
            Template content
        """
        template_path = self.consolidation_config.get('templatePath', 
                                                      '.akr/templates/feature-consolidated.md')
        template_file = Path(template_path)
        
        if template_file.exists():
            return template_file.read_text(encoding='utf-8')
        else:
            # Return basic template
            return """# {feature_name}

## Overview

{description}

## Components

{components}

## Architecture

{diagram}

## Relationships

{relationships}
"""
    
    def _synthesize_documentation(self, template: str, feature_name: str,
                                  components: List[Dict[str, Any]],
                                  relationships: List[Dict[str, Any]],
                                  diagram: str) -> str:
        """Synthesize consolidated documentation.
        
        Args:
            template: Documentation template
            feature_name: Feature name
            components: List of components
            relationships: List of relationships
            diagram: Mermaid diagram
            
        Returns:
            Synthesized documentation
        """
        # Build components section
        components_md = []
        for comp in components:
            components_md.append(f"### {comp['name']} ({comp['layer']})\n")
            components_md.append(f"**Repository:** {comp['repository']}\n")
        
        # Build relationships section
        relationships_md = []
        for rel in relationships:
            relationships_md.append(f"- {rel['source']} {rel['type']} {rel['target']}")
        
        # Fill template
        output = template.format(
            feature_name=feature_name,
            description=f"Feature documentation for {feature_name}",
            components='\n'.join(components_md),
            diagram=diagram,
            relationships='\n'.join(relationships_md)
        )
        
        return output
    
    def _create_consolidation_branch(self, feature_name: str) -> str:
        """Create feature branch for consolidated documentation.
        
        Never commits directly to main - always creates feature branch
        for team review before merge.
        
        Args:
            feature_name: Name of feature
            
        Returns:
            Branch name
        """
        # Get branch naming pattern from config
        output_branch_config = self.consolidation_config.get('outputBranch', {})
        pattern = output_branch_config.get('namePattern', 'docs/consolidate-{feature}-{date}')
        
        # Generate branch name
        timestamp = datetime.datetime.now().strftime('%Y%m%d')
        branch_name = pattern.format(
            feature=feature_name.lower().replace(' ', '-'),
            date=timestamp,
            timestamp=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        )
        
        # Ensure we're on main branch first
        feature_repo_path = Path.cwd()  # Current working directory (feature repo)
        
        try:
            self._git_checkout(feature_repo_path, 'main')
            self._git_pull(feature_repo_path, 'main')
        except subprocess.CalledProcessError:
            logger.warning("Could not update main branch, proceeding with current state")
        
        # Create new feature branch from main
        subprocess.run(
            ['git', 'checkout', '-b', branch_name],
            cwd=feature_repo_path,
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.info(f"Created branch {branch_name} from main")
        return branch_name
    
    def _commit_consolidated_docs(self, branch: str, feature: str, file_path: Path) -> None:
        """Commit consolidated documentation to feature branch.
        
        Args:
            branch: Feature branch name
            feature: Feature name
            file_path: Path to generated documentation
        """
        feature_repo_path = Path.cwd()
        
        # Stage the generated file
        subprocess.run(
            ['git', 'add', str(file_path)],
            cwd=feature_repo_path,
            check=True,
            capture_output=True,
            text=True
        )
        
        # Commit with descriptive message
        commit_message = (
            f"docs: consolidate {feature} feature documentation\n\n"
            f"Auto-generated from component repositories:\n"
            f"- Component repos (main branch only)\n\n"
            f"Please review for accuracy before merging."
        )
        
        subprocess.run(
            ['git', 'commit', '-m', commit_message],
            cwd=feature_repo_path,
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.info(f"Committed {file_path} to branch {branch}")
    
    def _push_branch(self, branch: str) -> None:
        """Push feature branch to remote.
        
        Args:
            branch: Branch name
        """
        feature_repo_path = Path.cwd()
        
        subprocess.run(
            ['git', 'push', 'origin', branch],
            cwd=feature_repo_path,
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.info(f"Pushed branch {branch} to origin")
    
    def _create_pull_request(self, branch: str, feature: str, 
                            components: List[Dict[str, Any]]) -> str:
        """Create pull request for consolidated documentation.
        
        Args:
            branch: Feature branch name
            feature: Feature name
            components: List of components
            
        Returns:
            PR URL
        """
        output_branch_config = self.consolidation_config.get('outputBranch', {})
        
        # Build component list for PR body
        component_list = '\n'.join([
            f"- {c['layer']}: {c['name']}"
            for c in components
        ])
        
        # Build PR title and body
        pr_title = f"Update {feature} feature documentation"
        pr_body = (
            f"## Consolidated Feature Documentation\n\n"
            f"**Feature:** {feature}\n"
            f"**Source:** Component repositories (main branch)\n\n"
            f"### Components Included\n"
            f"{component_list}\n\n"
            f"### Changes\n"
            f"- Consolidated documentation from latest component docs\n"
            f"- Generated architecture diagrams\n"
            f"- Updated relationship mappings\n\n"
            f"### Review Checklist\n"
            f"- [ ] Technical accuracy verified\n"
            f"- [ ] All components properly documented\n"
            f"- [ ] Diagrams render correctly\n"
            f"- [ ] Human-required sections identified\n\n"
            f"**Auto-generated by AKR MCP Server**"
        )
        
        # Create PR using GitHub CLI
        try:
            result = subprocess.run(
                [
                    'gh', 'pr', 'create',
                    '--title', pr_title,
                    '--body', pr_body,
                    '--base', 'main',
                    '--head', branch,
                    '--label', ','.join(output_branch_config.get('prLabels', ['documentation', 'auto-generated'])),
                    '--reviewer', ','.join(output_branch_config.get('prReviewers', []))
                ],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
                check=True
            )
            
            # Extract PR URL from output
            pr_url = result.stdout.strip()
            return pr_url
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create PR: {e.stderr}")
            return None
    
    def log_repository_states(self) -> None:
        """Log repository states for monitoring and validation."""
        logger.info("Repository states for consolidation:")
        
        for repo in self.repositories:
            if not repo.get('enabled', True):
                continue
            
            repo_name = repo['name']
            repo_path = self.cache_dir / repo_name
            branch = repo['branch']
            
            if not repo_path.exists():
                logger.info(f"  {repo_name}: NOT CLONED")
                continue
            
            try:
                # Get current branch
                current_branch = self._get_current_branch(repo_path)
                
                # Get latest commit
                result = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                commit_sha = result.stdout.strip()[:7]
                
                # Get commit date
                result = subprocess.run(
                    ['git', 'log', '-1', '--format=%cd', '--date=relative'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                commit_date = result.stdout.strip()
                
                logger.info(
                    f"  {repo_name}: "
                    f"branch={current_branch} (expected={branch}), "
                    f"commit={commit_sha}, "
                    f"updated={commit_date}"
                )
            except Exception as e:
                logger.error(f"  {repo_name}: ERROR - {e}")
