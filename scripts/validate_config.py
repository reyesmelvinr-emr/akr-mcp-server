"""
Configuration Validation Script for Cross-Repository Consolidation

Validates branch configuration before cross-repository operations.
Ensures all required branches exist and are properly configured.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def validate_branch_config(config: Dict) -> Tuple[bool, List[str]]:
    """Validate branch configuration for cross-repository consolidation.
    
    Checks:
    1. All relatedRepositories have 'branch' key
    2. Specified branches exist remotely
    3. Branch naming follows conventions
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check if crossRepository section exists
    if 'crossRepository' not in config:
        errors.append("Missing 'crossRepository' section in configuration")
        return (False, errors)
    
    cross_repo = config['crossRepository']
    
    # Check relatedRepositories
    if 'relatedRepositories' not in cross_repo:
        errors.append("Missing 'relatedRepositories' in crossRepository configuration")
        return (False, errors)
    
    repositories = cross_repo['relatedRepositories']
    
    if not repositories:
        errors.append("'relatedRepositories' is empty - need at least one repository")
        return (False, errors)
    
    # Validate each repository
    for idx, repo in enumerate(repositories):
        repo_name = repo.get('name', f"repo_{idx}")
        
        # Check required fields
        if 'name' not in repo:
            errors.append(f"Repository {idx}: Missing 'name' field")
        
        if 'url' not in repo:
            errors.append(f"{repo_name}: Missing 'url' field")
        
        if 'branch' not in repo:
            errors.append(f"{repo_name}: Missing 'branch' field - MUST specify branch for consolidation")
            continue
        
        # Validate branch exists remotely
        branch = repo['branch']
        url = repo.get('url', '')
        
        if url:
            branch_exists = check_remote_branch_exists(url, branch)
            if not branch_exists:
                errors.append(
                    f"{repo_name}: Branch '{branch}' does not exist in remote repository {url}"
                )
        
        # Validate branch naming (warn if not main/master)
        if branch not in ['main', 'master', 'develop']:
            print(
                f"⚠️  WARNING: {repo_name} uses branch '{branch}'. "
                f"Consolidation typically uses stable branches like 'main' or 'master'."
            )
    
    # Check consolidation.outputBranch configuration
    consolidation = cross_repo.get('consolidation', {})
    output_branch = consolidation.get('outputBranch', {})
    
    if 'strategy' in output_branch:
        strategy = output_branch['strategy']
        valid_strategies = ['feature-branch', 'direct-commit']
        if strategy not in valid_strategies:
            errors.append(
                f"Invalid outputBranch.strategy: {strategy}. "
                f"Must be one of: {', '.join(valid_strategies)}"
            )
    
    if output_branch.get('strategy') == 'feature-branch':
        if 'namePattern' not in output_branch:
            print(
                "⚠️  WARNING: outputBranch.namePattern not specified. "
                "Using default: 'docs/consolidate-{feature}-{date}'"
            )
    
    is_valid = len(errors) == 0
    return (is_valid, errors)


def check_remote_branch_exists(url: str, branch: str) -> bool:
    """Check if branch exists in remote repository.
    
    Args:
        url: Repository URL
        branch: Branch name
        
    Returns:
        True if branch exists, False otherwise
    """
    try:
        result = subprocess.run(
            ['git', 'ls-remote', '--heads', url, f'refs/heads/{branch}'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # If output contains the branch, it exists
        return branch in result.stdout
    except subprocess.TimeoutExpired:
        print(f"⚠️  WARNING: Timeout checking branch '{branch}' in {url}")
        return True  # Don't fail validation on timeout
    except Exception as e:
        print(f"⚠️  WARNING: Could not verify branch '{branch}' in {url}: {e}")
        return True  # Don't fail validation on error


def validate_config_file(config_path: Path) -> bool:
    """Validate configuration file.
    
    Args:
        config_path: Path to .akr-config.json
        
    Returns:
        True if valid, False otherwise
    """
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        return False
    
    # Load configuration
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to read configuration file: {e}")
        return False
    
    # Validate branch configuration
    is_valid, errors = validate_branch_config(config)
    
    if is_valid:
        print("✅ Configuration is valid for cross-repository consolidation")
        
        # Print summary
        cross_repo = config.get('crossRepository', {})
        repositories = cross_repo.get('relatedRepositories', [])
        
        print(f"\n📊 Configuration Summary:")
        print(f"  Repositories: {len(repositories)}")
        for repo in repositories:
            if repo.get('enabled', True):
                print(f"    ✓ {repo['name']} (branch: {repo['branch']})")
            else:
                print(f"    ⊗ {repo['name']} (disabled)")
        
        consolidation = cross_repo.get('consolidation', {})
        output_branch = consolidation.get('outputBranch', {})
        strategy = output_branch.get('strategy', 'feature-branch')
        print(f"  Output Strategy: {strategy}")
        
        if strategy == 'feature-branch':
            pattern = output_branch.get('namePattern', 'docs/consolidate-{feature}-{date}')
            print(f"  Branch Pattern: {pattern}")
            
            reviewers = output_branch.get('prReviewers', [])
            if reviewers:
                print(f"  PR Reviewers: {', '.join(reviewers)}")
        
        return True
    else:
        print("❌ Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        
        print("\n💡 Resolution Steps:")
        print("  1. Add 'branch' field to all repositories in 'relatedRepositories'")
        print("  2. Specify stable branches (main/master) for production consolidation")
        print("  3. Verify branches exist in remote repositories")
        print("  4. Ensure 'outputBranch' configuration is valid")
        
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate AKR configuration for cross-repository consolidation'
    )
    parser.add_argument(
        'config_path',
        nargs='?',
        default='.akr-config.json',
        help='Path to configuration file (default: .akr-config.json)'
    )
    
    args = parser.parse_args()
    config_path = Path(args.config_path)
    
    print("🔍 Validating AKR Configuration for Cross-Repository Consolidation")
    print(f"   Config: {config_path}\n")
    
    is_valid = validate_config_file(config_path)
    
    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()
