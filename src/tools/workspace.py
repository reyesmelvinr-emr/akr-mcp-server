"""
Workspace detection and management for AKR MCP Server.

This module provides workspace-aware functionality that allows the MCP server
to work with any application codebase (monorepo or multi-repo) by:
- Detecting the active VS Code workspace
- Loading project configuration from workspace root
- Mapping source files to documentation paths
- Supporting both monorepo and multi-repo structures
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import fnmatch

logger = logging.getLogger(__name__)


class WorkspaceManager:
    """Manages workspace detection and configuration for the MCP server."""
    
    def __init__(self):
        """Initialize workspace manager."""
        self.workspace_root: Optional[Path] = None
        self.config: Optional[Dict] = None
        self.repository_type: Optional[str] = None
        self.packages: List[str] = []
        
    def detect_workspace(self) -> Path:
        """
        Detect the active VS Code workspace.
        
        Returns:
            Path: The detected workspace root directory
            
        Raises:
            FileNotFoundError: If workspace cannot be detected
        """
        # Method 1: Check VSCODE_WORKSPACE_FOLDER environment variable (set by VS Code)
        workspace_env = os.getenv("VSCODE_WORKSPACE_FOLDER")
        if workspace_env:
            workspace_path = Path(workspace_env)
            if workspace_path.exists():
                logger.info(f"Detected workspace from environment: {workspace_path}")
                self.workspace_root = workspace_path
                return workspace_path
        
        # Method 2: Use current working directory as fallback
        cwd = Path.cwd()
        logger.info(f"Using current working directory as workspace: {cwd}")
        self.workspace_root = cwd
        return cwd
    
    def load_workspace_config(self, workspace_path: Optional[Path] = None) -> Dict:
        """
        Load .akr-config.json from workspace root.
        
        Args:
            workspace_path: Optional workspace path (uses detected workspace if not provided)
            
        Returns:
            Dict: Loaded configuration
            
        Raises:
            FileNotFoundError: If .akr-config.json not found
            json.JSONDecodeError: If configuration file is invalid JSON
        """
        if workspace_path is None:
            if self.workspace_root is None:
                self.detect_workspace()
            workspace_path = self.workspace_root
        
        config_path = workspace_path / ".akr-config.json"
        
        if not config_path.exists():
            error_msg = (
                f"No .akr-config.json found in workspace: {workspace_path}\n"
                f"Run setup script in your application repository first:\n"
                f"  cd {workspace_path}\n"
                f"  ./setup.ps1 --configure-repo"
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
                self.config = config
                self._analyze_repository_structure(config)
                return config
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {config_path}: {e}")
            raise
    
    def _analyze_repository_structure(self, config: Dict) -> None:
        """
        Analyze repository structure from configuration.
        
        Args:
            config: Loaded configuration dictionary
        """
        # Check explicit repository type
        repo_info = config.get("repository", {})
        self.repository_type = repo_info.get("type", "standard")
        
        # For monorepos, identify packages
        if self.repository_type == "monorepo":
            self.packages = repo_info.get("packages", [])
            logger.info(f"Detected monorepo with packages: {self.packages}")
            
            # Auto-detect packages if not specified
            if not self.packages and self.workspace_root:
                self.packages = self._detect_packages()
        
        # Auto-detect if type not specified
        if self.repository_type == "standard" and self.workspace_root:
            detected_type = self._detect_repository_type()
            if detected_type != "standard":
                self.repository_type = detected_type
                logger.info(f"Auto-detected repository type: {detected_type}")
    
    def _detect_repository_type(self) -> str:
        """
        Auto-detect repository type by checking for common monorepo patterns.
        
        Returns:
            str: "monorepo" or "standard"
        """
        if not self.workspace_root:
            return "standard"
        
        # Check for packages/ directory (common monorepo pattern)
        packages_dir = self.workspace_root / "packages"
        if packages_dir.exists() and packages_dir.is_dir():
            return "monorepo"
        
        # Check for apps/ directory (alternative monorepo pattern)
        apps_dir = self.workspace_root / "apps"
        if apps_dir.exists() and apps_dir.is_dir():
            return "monorepo"
        
        return "standard"
    
    def _detect_packages(self) -> List[str]:
        """
        Auto-detect package names in a monorepo.
        
        Returns:
            List[str]: List of package names
        """
        packages = []
        
        if not self.workspace_root:
            return packages
        
        # Check packages/ directory
        packages_dir = self.workspace_root / "packages"
        if packages_dir.exists() and packages_dir.is_dir():
            packages = [d.name for d in packages_dir.iterdir() if d.is_dir()]
            logger.info(f"Auto-detected packages: {packages}")
            return packages
        
        # Check apps/ directory
        apps_dir = self.workspace_root / "apps"
        if apps_dir.exists() and apps_dir.is_dir():
            packages = [d.name for d in apps_dir.iterdir() if d.is_dir()]
            logger.info(f"Auto-detected apps: {packages}")
            return packages
        
        return packages
    
    def get_output_path(self, source_file: str) -> Optional[Path]:
        """
        Map source file to documentation output path using configuration.
        
        Args:
            source_file: Relative or absolute path to source file
            
        Returns:
            Optional[Path]: Absolute path to documentation output file, or None if no mapping found
        """
        if not self.config or not self.workspace_root:
            logger.warning("Configuration or workspace root not loaded")
            return None
        
        # Convert to Path and make relative to workspace
        source_path = Path(source_file)
        if source_path.is_absolute():
            try:
                source_path = source_path.relative_to(self.workspace_root)
            except ValueError:
                logger.warning(f"Source file {source_file} is outside workspace {self.workspace_root}")
                return None
        
        # Get path mappings from config
        doc_config = self.config.get("documentation", {})
        path_mappings = doc_config.get("pathMappings", {})
        
        # Find matching pattern
        for pattern, output_template in path_mappings.items():
            if self._matches_pattern(source_path, pattern):
                # Replace {name} with file stem (name without extension)
                output_path_str = output_template.replace("{name}", source_path.stem)
                output_path = self.workspace_root / output_path_str
                logger.info(f"Mapped {source_file} → {output_path}")
                return output_path
        
        # Fallback: docs/{filename}.md
        fallback_output = self.workspace_root / "docs" / f"{source_path.stem}.md"
        logger.info(f"Using fallback mapping: {source_file} → {fallback_output}")
        return fallback_output
    
    def _matches_pattern(self, path: Path, pattern: str) -> bool:
        """
        Check if path matches glob pattern.
        
        Args:
            path: Path to check
            pattern: Glob pattern
            
        Returns:
            bool: True if path matches pattern
        """
        # Convert path to string with forward slashes for consistent matching
        path_str = str(path).replace('\\', '/')
        
        # Use fnmatch for glob pattern matching
        return fnmatch.fnmatch(path_str, pattern)
    
    def get_package_for_file(self, file_path: str) -> Optional[str]:
        """
        Determine which package a file belongs to (for monorepos).
        
        Args:
            file_path: Relative or absolute path to file
            
        Returns:
            Optional[str]: Package name, or None if not in a package
        """
        if self.repository_type != "monorepo" or not self.packages:
            return None
        
        # Convert to relative path
        path = Path(file_path)
        if path.is_absolute() and self.workspace_root:
            try:
                path = path.relative_to(self.workspace_root)
            except ValueError:
                return None
        
        path_str = str(path).replace('\\', '/')
        
        # Check if file is in any package
        for package in self.packages:
            if path_str.startswith(f"packages/{package}/") or path_str.startswith(f"apps/{package}/"):
                logger.debug(f"File {file_path} belongs to package: {package}")
                return package
        
        return None
    
    def get_package_templates(self, package_name: str) -> Optional[List[str]]:
        """
        Get configured templates for a specific package (for monorepos).
        
        Args:
            package_name: Name of the package
            
        Returns:
            Optional[List[str]]: List of template names, or None if not configured
        """
        if not self.config:
            return None
        
        template_config = self.config.get("templates", {})
        package_templates = template_config.get("packageTemplates", {})
        
        return package_templates.get(package_name)
    
    def get_workspace_info(self) -> Dict:
        """
        Get workspace information summary.
        
        Returns:
            Dict: Workspace information
        """
        return {
            "workspace_root": str(self.workspace_root) if self.workspace_root else None,
            "repository_type": self.repository_type,
            "packages": self.packages,
            "config_loaded": self.config is not None,
            "config_file": str(self.workspace_root / ".akr-config.json") if self.workspace_root else None
        }


def create_workspace_manager() -> WorkspaceManager:
    """
    Create and initialize a workspace manager.
    
    Returns:
        WorkspaceManager: Initialized workspace manager
    """
    manager = WorkspaceManager()
    try:
        manager.detect_workspace()
        manager.load_workspace_config()
        logger.info(f"Workspace manager initialized for: {manager.workspace_root}")
    except FileNotFoundError as e:
        logger.warning(f"Workspace manager initialized without config: {e}")
    except Exception as e:
        logger.error(f"Error initializing workspace manager: {e}")
    
    return manager
