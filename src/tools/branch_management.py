"""
Branch Management Module

Handles Git branch operations for MCP documentation writes.
Provides branch detection, creation, and switching functionality.
"""

import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger("akr-mcp-server.tools.branch_management")


class BranchStrategy(Enum):
    """Strategy for selecting documentation branch."""
    CREATE_NEW = "create_new"      # Create a new docs/timestamp branch
    USE_CURRENT = "use_current"    # Use the current branch (if not main)
    USE_EXISTING = "use_existing"  # Switch to a specified existing branch


@dataclass
class RepositoryContext:
    """Context information about a Git repository."""
    repo_path: str
    main_branch: str
    current_branch: str
    available_branches: list[str] = field(default_factory=list)
    has_uncommitted_changes: bool = False
    is_git_repo: bool = True
    remote_url: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "repoPath": self.repo_path,
            "mainBranch": self.main_branch,
            "currentBranch": self.current_branch,
            "availableBranches": self.available_branches,
            "hasUncommittedChanges": self.has_uncommitted_changes,
            "isGitRepo": self.is_git_repo,
            "remoteUrl": self.remote_url
        }


@dataclass
class BranchSelectionOptions:
    """Options for branch selection."""
    options: list[dict] = field(default_factory=list)
    recommended: str = "new"
    recommended_branch_name: str = ""
    
    def to_dict(self) -> dict:
        return {
            "options": self.options,
            "recommended": self.recommended,
            "recommendedBranchName": self.recommended_branch_name
        }


class BranchManager:
    """
    Manages Git branch operations for documentation writes.
    
    Ensures all documentation writes happen on feature branches,
    never directly on the main branch.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize branch manager for a repository.
        
        Args:
            repo_path: Path to the Git repository
        """
        self.repo_path = Path(repo_path)
    
    def _run_git(self, *args, check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command in the repository."""
        cmd = ["git"] + list(args)
        logger.debug(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.repo_path
        )
        
        if check and result.returncode != 0:
            logger.warning(f"Git command failed: {result.stderr}")
        
        return result
    
    def is_git_repository(self) -> bool:
        """Check if the path is a Git repository."""
        result = self._run_git("rev-parse", "--is-inside-work-tree", check=False)
        return result.returncode == 0 and result.stdout.strip() == "true"
    
    def get_current_branch(self) -> str:
        """Get the current branch name."""
        result = self._run_git("rev-parse", "--abbrev-ref", "HEAD", check=False)
        if result.returncode == 0:
            return result.stdout.strip()
        return "unknown"
    
    def get_main_branch(self) -> str:
        """
        Detect the main/default branch of the repository.
        
        Strategy:
        1. Check for 'main' branch
        2. Check for 'master' branch
        3. Check remote HEAD reference
        4. Fall back to 'main'
        """
        branches = self.list_branches()
        
        # Check common main branch names in order of preference
        for candidate in ['main', 'master', 'develop']:
            if candidate in branches:
                return candidate
        
        # Try to get remote HEAD
        result = self._run_git("symbolic-ref", "refs/remotes/origin/HEAD", check=False)
        if result.returncode == 0:
            # Parse refs/remotes/origin/main -> main
            ref = result.stdout.strip()
            if '/' in ref:
                return ref.split('/')[-1]
        
        return 'main'  # Default fallback
    
    def list_branches(self, include_remote: bool = False) -> list[str]:
        """
        List all branches in the repository.
        
        Args:
            include_remote: Include remote branches
            
        Returns:
            List of branch names
        """
        args = ["branch", "-l"]
        if include_remote:
            args.append("-a")
        
        result = self._run_git(*args, check=False)
        
        if result.returncode != 0:
            return []
        
        branches = []
        for line in result.stdout.strip().split('\n'):
            if line:
                # Remove leading *, spaces, and remote prefixes
                branch = line.strip().lstrip('* ')
                if branch.startswith('remotes/origin/'):
                    branch = branch[15:]  # Remove prefix
                if branch and not branch.startswith('HEAD'):
                    branches.append(branch)
        
        return list(set(branches))  # Deduplicate
    
    def has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes in the working directory."""
        result = self._run_git("status", "--porcelain", check=False)
        return bool(result.stdout.strip())
    
    def get_remote_url(self) -> Optional[str]:
        """Get the remote origin URL."""
        result = self._run_git("remote", "get-url", "origin", check=False)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    
    def get_repository_context(self) -> RepositoryContext:
        """
        Get complete context about the repository.
        
        Returns:
            RepositoryContext with all repository information
        """
        if not self.is_git_repository():
            return RepositoryContext(
                repo_path=str(self.repo_path),
                main_branch="main",
                current_branch="unknown",
                is_git_repo=False
            )
        
        return RepositoryContext(
            repo_path=str(self.repo_path),
            main_branch=self.get_main_branch(),
            current_branch=self.get_current_branch(),
            available_branches=self.list_branches(),
            has_uncommitted_changes=self.has_uncommitted_changes(),
            is_git_repo=True,
            remote_url=self.get_remote_url()
        )
    
    def generate_branch_name(self, prefix: str = "docs/", 
                            component_name: Optional[str] = None) -> str:
        """
        Generate a unique documentation branch name.
        
        Args:
            prefix: Branch name prefix (default: "docs/")
            component_name: Optional component name to include
            
        Returns:
            Generated branch name
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        if component_name:
            # Sanitize component name for branch
            safe_name = component_name.replace(" ", "-").replace("/", "-")
            safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '-')
            return f"{prefix}{safe_name}-{timestamp}"
        
        return f"{prefix}update-{timestamp}"
    
    def get_branch_selection_options(self, 
                                     component_name: Optional[str] = None,
                                     branch_prefix: str = "docs/") -> BranchSelectionOptions:
        """
        Get options for branch selection.
        
        Args:
            component_name: Optional component name for branch naming
            branch_prefix: Prefix for new documentation branches
            
        Returns:
            BranchSelectionOptions with available choices
        """
        context = self.get_repository_context()
        new_branch_name = self.generate_branch_name(branch_prefix, component_name)
        
        options = [
            {
                "id": "new",
                "label": "Create new documentation branch",
                "branch": new_branch_name,
                "description": "Isolated branch for documentation changes"
            },
            {
                "id": "current",
                "label": f"Use current branch ({context.current_branch})",
                "branch": context.current_branch,
                "description": "Add documentation to your current work"
            }
        ]
        
        # Add existing documentation branches as options
        doc_branches = [b for b in context.available_branches if b.startswith(branch_prefix)]
        for branch in doc_branches[:3]:  # Limit to 3
            options.append({
                "id": f"existing:{branch}",
                "label": f"Use existing: {branch}",
                "branch": branch,
                "description": "Continue work on existing documentation branch"
            })
        
        # Add custom option
        options.append({
            "id": "custom",
            "label": "Specify custom branch name",
            "branch": None,
            "description": "Enter your own branch name"
        })
        
        # Determine recommendation
        if context.current_branch == context.main_branch:
            # On main - strongly recommend new branch
            recommended = "new"
        elif context.current_branch.startswith(branch_prefix):
            # Already on a docs branch - recommend current
            recommended = "current"
        else:
            # On a feature branch - default to new for isolation
            recommended = "new"
        
        return BranchSelectionOptions(
            options=options,
            recommended=recommended,
            recommended_branch_name=new_branch_name
        )
    
    def branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists."""
        return branch_name in self.list_branches()
    
    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """
        Create a new branch.
        
        Args:
            branch_name: Name of branch to create
            checkout: Whether to checkout the branch after creation
            
        Returns:
            True if successful
        """
        if self.branch_exists(branch_name):
            logger.info(f"Branch {branch_name} already exists")
            if checkout:
                return self.checkout_branch(branch_name)
            return True
        
        # Create branch
        if checkout:
            result = self._run_git("checkout", "-b", branch_name, check=False)
        else:
            result = self._run_git("branch", branch_name, check=False)
        
        if result.returncode == 0:
            logger.info(f"Created branch: {branch_name}")
            return True
        else:
            logger.error(f"Failed to create branch: {result.stderr}")
            return False
    
    def checkout_branch(self, branch_name: str) -> bool:
        """
        Checkout an existing branch.
        
        Args:
            branch_name: Name of branch to checkout
            
        Returns:
            True if successful
        """
        result = self._run_git("checkout", branch_name, check=False)
        
        if result.returncode == 0:
            logger.info(f"Checked out branch: {branch_name}")
            return True
        else:
            logger.error(f"Failed to checkout branch: {result.stderr}")
            return False
    
    def ensure_on_branch(self, branch_name: str, create_if_missing: bool = True) -> bool:
        """
        Ensure we're on the specified branch, creating if needed.
        
        Args:
            branch_name: Target branch name
            create_if_missing: Create branch if it doesn't exist
            
        Returns:
            True if now on the target branch
        """
        current = self.get_current_branch()
        
        if current == branch_name:
            logger.debug(f"Already on branch: {branch_name}")
            return True
        
        if self.branch_exists(branch_name):
            return self.checkout_branch(branch_name)
        elif create_if_missing:
            return self.create_branch(branch_name, checkout=True)
        else:
            logger.error(f"Branch {branch_name} does not exist")
            return False
    
    def is_on_protected_branch(self, protected: Optional[list[str]] = None) -> bool:
        """
        Check if currently on a protected branch.
        
        Args:
            protected: List of protected branch names (default: main, master)
            
        Returns:
            True if on a protected branch
        """
        if protected is None:
            protected = ['main', 'master', 'develop']
        
        current = self.get_current_branch()
        return current in protected


def initialize_documentation_session(repo_path: str) -> dict:
    """
    Initialize a documentation session for a repository.
    
    Returns repository context and branch selection options.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Dictionary with context and options
    """
    manager = BranchManager(repo_path)
    context = manager.get_repository_context()
    options = manager.get_branch_selection_options()
    
    return {
        "context": context.to_dict(),
        "branchOptions": options.to_dict(),
        "warnings": _generate_warnings(context)
    }


def _generate_warnings(context: RepositoryContext) -> list[str]:
    """Generate warnings based on repository state."""
    warnings = []
    
    if not context.is_git_repo:
        warnings.append("⚠️ This directory is not a Git repository. Branch management will be limited.")
    
    if context.has_uncommitted_changes:
        warnings.append("⚠️ You have uncommitted changes. Consider committing or stashing before proceeding.")
    
    if context.current_branch == context.main_branch:
        warnings.append(f"⚠️ You're on the main branch ({context.main_branch}). Documentation will be created on a new branch.")
    
    return warnings


def select_documentation_branch(repo_path: str, 
                                 option: str,
                                 custom_branch: Optional[str] = None,
                                 component_name: Optional[str] = None) -> dict:
    """
    Select or create the branch for documentation changes.
    
    Args:
        repo_path: Path to the repository
        option: Selection option ("new", "current", "existing:name", "custom")
        custom_branch: Branch name if option is "custom"
        component_name: Component name for branch naming
        
    Returns:
        Dictionary with result information
    """
    manager = BranchManager(repo_path)
    
    if option == "new":
        branch_name = manager.generate_branch_name(component_name=component_name)
        success = manager.create_branch(branch_name, checkout=True)
    elif option == "current":
        branch_name = manager.get_current_branch()
        success = True
    elif option.startswith("existing:"):
        branch_name = option[9:]  # Remove "existing:" prefix
        success = manager.checkout_branch(branch_name)
    elif option == "custom":
        if not custom_branch:
            return {
                "success": False,
                "error": "Custom branch name is required",
                "branch": None
            }
        branch_name = custom_branch
        success = manager.ensure_on_branch(branch_name, create_if_missing=True)
    else:
        return {
            "success": False,
            "error": f"Unknown option: {option}",
            "branch": None
        }
    
    return {
        "success": success,
        "branch": branch_name if success else None,
        "previousBranch": manager.get_current_branch() if not success else None,
        "isNewBranch": option == "new" or (option == "custom" and not manager.branch_exists(custom_branch or "")),
        "error": None if success else "Failed to switch to branch"
    }
