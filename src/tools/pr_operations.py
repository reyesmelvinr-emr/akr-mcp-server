"""
Pull Request Operations Module

Handles GitHub Pull Request creation for documentation changes.
Uses GitHub CLI (gh) for PR operations.
"""

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger("akr-mcp-server.tools.pr_operations")


@dataclass
class PRInfo:
    """Information about a created Pull Request."""
    number: int
    url: str
    title: str
    branch: str
    base_branch: str
    draft: bool


class PRManager:
    """
    Manages Pull Request operations for documentation changes.
    
    Uses GitHub CLI (gh) which must be installed and authenticated.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize PR manager.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
    
    def _run_gh(self, *args) -> subprocess.CompletedProcess:
        """Run a GitHub CLI command."""
        cmd = ["gh"] + list(args)
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.repo_path
        )
    
    def _run_git(self, *args) -> subprocess.CompletedProcess:
        """Run a git command."""
        cmd = ["git"] + list(args)
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.repo_path
        )
    
    def is_gh_available(self) -> bool:
        """Check if GitHub CLI is available."""
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def is_gh_authenticated(self) -> bool:
        """Check if GitHub CLI is authenticated."""
        result = self._run_gh("auth", "status")
        return result.returncode == 0
    
    def get_current_branch(self) -> str:
        """Get current branch name."""
        result = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        return result.stdout.strip() if result.returncode == 0 else ""
    
    def get_main_branch(self) -> str:
        """Detect the main branch name."""
        result = self._run_git("symbolic-ref", "refs/remotes/origin/HEAD")
        if result.returncode == 0:
            return result.stdout.strip().replace("refs/remotes/origin/", "")
        
        # Fallback: check for main or master
        result = self._run_git("branch", "-r")
        if result.returncode == 0:
            if "origin/main" in result.stdout:
                return "main"
            elif "origin/master" in result.stdout:
                return "master"
        
        return "main"
    
    def push_branch(self, branch_name: Optional[str] = None) -> bool:
        """
        Push branch to remote.
        
        Args:
            branch_name: Branch to push (current if None)
            
        Returns:
            True if successful
        """
        if branch_name:
            result = self._run_git("push", "-u", "origin", branch_name)
        else:
            result = self._run_git("push", "-u", "origin", "HEAD")
        
        if result.returncode == 0:
            logger.info(f"Pushed branch to remote")
            return True
        else:
            logger.error(f"Push failed: {result.stderr}")
            return False
    
    def create_pr(
        self,
        title: str,
        body: str,
        base_branch: Optional[str] = None,
        draft: bool = False,
        labels: Optional[list[str]] = None
    ) -> dict:
        """
        Create a Pull Request.
        
        Args:
            title: PR title
            body: PR description
            base_branch: Target branch (main if None)
            draft: Create as draft PR
            labels: Labels to apply
            
        Returns:
            Dictionary with PR information
        """
        # Check prerequisites
        if not self.is_gh_available():
            return {
                "success": False,
                "error": "GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/",
                "action_needed": "install_gh"
            }
        
        if not self.is_gh_authenticated():
            return {
                "success": False,
                "error": "GitHub CLI is not authenticated. Run 'gh auth login' to authenticate.",
                "action_needed": "auth_gh"
            }
        
        current_branch = self.get_current_branch()
        if not base_branch:
            base_branch = self.get_main_branch()
        
        # Ensure we're not on the base branch
        if current_branch == base_branch:
            return {
                "success": False,
                "error": f"Cannot create PR from {base_branch} to {base_branch}. Switch to a feature branch first.",
                "current_branch": current_branch
            }
        
        # Push current branch
        if not self.push_branch():
            return {
                "success": False,
                "error": "Failed to push branch to remote"
            }
        
        # Build PR command
        cmd_args = [
            "pr", "create",
            "--title", title,
            "--body", body,
            "--base", base_branch
        ]
        
        if draft:
            cmd_args.append("--draft")
        
        if labels:
            for label in labels:
                cmd_args.extend(["--label", label])
        
        # Create PR
        result = self._run_gh(*cmd_args)
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Failed to create PR: {result.stderr}",
                "branch": current_branch,
                "base": base_branch
            }
        
        # Parse PR URL from output
        pr_url = result.stdout.strip()
        pr_number = self._extract_pr_number(pr_url)
        
        logger.info(f"Created PR #{pr_number}: {pr_url}")
        
        return {
            "success": True,
            "pr_number": pr_number,
            "pr_url": pr_url,
            "title": title,
            "branch": current_branch,
            "base_branch": base_branch,
            "draft": draft,
            "labels": labels or [],
            "message": f"Pull Request #{pr_number} created successfully"
        }
    
    def _extract_pr_number(self, pr_url: str) -> int:
        """Extract PR number from URL."""
        try:
            return int(pr_url.rstrip('/').split('/')[-1])
        except (ValueError, IndexError):
            return 0
    
    def get_pr_status(self, pr_number: int) -> dict:
        """
        Get status of a Pull Request.
        
        Args:
            pr_number: PR number to check
            
        Returns:
            Dictionary with PR status
        """
        result = self._run_gh(
            "pr", "view", str(pr_number),
            "--json", "number,title,state,url,mergeable,reviews,statusCheckRollup"
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Failed to get PR status: {result.stderr}"
            }
        
        import json
        try:
            pr_data = json.loads(result.stdout)
            return {
                "success": True,
                **pr_data
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Failed to parse PR data"
            }
    
    def list_open_prs(self, documentation_only: bool = False) -> dict:
        """
        List open Pull Requests.
        
        Args:
            documentation_only: Filter to documentation PRs only
            
        Returns:
            Dictionary with list of PRs
        """
        cmd_args = [
            "pr", "list",
            "--json", "number,title,headRefName,url,createdAt,author"
        ]
        
        if documentation_only:
            cmd_args.extend(["--label", "documentation"])
        
        result = self._run_gh(*cmd_args)
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Failed to list PRs: {result.stderr}"
            }
        
        import json
        try:
            prs = json.loads(result.stdout)
            
            # Filter for documentation branches if requested
            if documentation_only and not any("--label" in arg for arg in cmd_args):
                prs = [pr for pr in prs if pr.get("headRefName", "").startswith("docs/")]
            
            return {
                "success": True,
                "count": len(prs),
                "pull_requests": prs
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Failed to parse PR list"
            }


def create_documentation_pr(
    repo_path: str,
    title: str,
    description: str,
    files_documented: list[str],
    component_types: Optional[list[str]] = None,
    draft: bool = True,
    base_branch: Optional[str] = None
) -> dict:
    """
    Create a Pull Request for documentation changes.
    
    Args:
        repo_path: Path to the repository
        title: PR title
        description: PR description
        files_documented: List of files that were documented
        component_types: Types of components documented
        draft: Create as draft PR (recommended)
        base_branch: Target branch (main if None)
        
    Returns:
        Dictionary with PR information
    """
    manager = PRManager(repo_path)
    
    # Build comprehensive PR body
    body = _generate_pr_body(
        description=description,
        files_documented=files_documented,
        component_types=component_types or []
    )
    
    # Add documentation label
    labels = ["documentation", "ai-generated"]
    
    return manager.create_pr(
        title=title,
        body=body,
        base_branch=base_branch,
        draft=draft,
        labels=labels
    )


def _generate_pr_body(
    description: str,
    files_documented: list[str],
    component_types: list[str]
) -> str:
    """Generate a comprehensive PR body."""
    
    files_list = "\n".join(f"- `{f}`" for f in files_documented)
    types_list = ", ".join(component_types) if component_types else "Various"
    
    return f"""## 🤖 AI-Generated Documentation

{description}

### Files Documented
{files_list}

### Component Types
{types_list}

### Review Checklist
Please review the following before merging:

- [ ] **Accuracy**: Technical details are correct
- [ ] **Completeness**: All important aspects are documented
- [ ] **Business Context**: Add any missing business logic explanations
- [ ] **Examples**: Code examples are accurate and helpful
- [ ] **Links**: Related documentation links are correct

### AI Markers
- 🤖 Sections marked with this emoji are AI-generated
- ❓ Sections marked with this emoji need human input

### Generated By
AKR MCP Documentation Server

---
*This PR was created automatically. Please review carefully before merging.*
"""


def check_documentation_pr_requirements(repo_path: str) -> dict:
    """
    Check if all requirements are met for creating a documentation PR.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Dictionary with requirement status
    """
    manager = PRManager(repo_path)
    
    requirements = {
        "gh_installed": manager.is_gh_available(),
        "gh_authenticated": False,
        "on_feature_branch": False,
        "has_uncommitted_changes": False,
        "current_branch": "",
        "main_branch": "",
        "ready_for_pr": False,
        "issues": []
    }
    
    if requirements["gh_installed"]:
        requirements["gh_authenticated"] = manager.is_gh_authenticated()
    else:
        requirements["issues"].append("GitHub CLI (gh) is not installed")
    
    if not requirements["gh_authenticated"] and requirements["gh_installed"]:
        requirements["issues"].append("GitHub CLI is not authenticated")
    
    current_branch = manager.get_current_branch()
    main_branch = manager.get_main_branch()
    requirements["current_branch"] = current_branch
    requirements["main_branch"] = main_branch
    
    if current_branch == main_branch:
        requirements["issues"].append(f"Currently on {main_branch} branch - switch to a feature branch first")
    else:
        requirements["on_feature_branch"] = True
    
    # Check for uncommitted changes
    result = manager._run_git("status", "--porcelain")
    if result.stdout.strip():
        requirements["has_uncommitted_changes"] = True
        requirements["issues"].append("There are uncommitted changes")
    
    # Determine if ready
    requirements["ready_for_pr"] = (
        requirements["gh_installed"] and
        requirements["gh_authenticated"] and
        requirements["on_feature_branch"] and
        not requirements["has_uncommitted_changes"]
    )
    
    return requirements
