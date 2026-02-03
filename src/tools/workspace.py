"""
Workspace detection and management for AKR MCP Server.

This module provides workspace-aware functionality that allows the MCP server
to work with any application codebase (monorepo or multi-repo) by:
- Detecting the active VS Code workspace
- Loading project configuration from workspace root
- Mapping source files to documentation paths
- Supporting both monorepo and multi-repo structures
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)

# ==================== NEW CODE: FAST MODE FLAG ====================
FAST_MODE = os.getenv('AKR_FAST_MODE', 'false').lower() == 'true'
SKIP_WORKSPACE_SCAN = os.getenv('AKR_SKIP_WORKSPACE_SCAN', 'false').lower() == 'true'
# ==================================================================


class WorkspaceManager:
    """Manages workspace detection and configuration for the MCP server."""
    
    def __init__(self, skip_detection: bool = False):
        """
        Initialize workspace manager.
        
        Args:
            skip_detection: If True, skip workspace detection during init.
                           Useful for fast mode.
        """
        self.workspace_path: Optional[Path] = None
        self.workspace_config: Optional[Dict] = None
        self.skip_detection = skip_detection or SKIP_WORKSPACE_SCAN or FAST_MODE
        
        logger.info(f"WorkspaceManager initialized (skip_detection={self.skip_detection})")
        
        # Only detect if not in fast/skip mode
        if not self.skip_detection:
            self.workspace_path = self._detect_workspace()
            self.workspace_config = self._load_workspace_config()
    
    def _detect_workspace(self) -> Optional[Path]:
        """
        Detect the active VS Code workspace.
        
        Returns:
            Path to workspace root, or None if not detected.
        """
        logger.info("🔍 Detecting workspace...")
        
        try:
            # Method 1: Check VS Code environment variable
            vscode_workspace = os.getenv('VSCODE_WORKSPACE_FOLDER')
            if vscode_workspace:
                ws_path = Path(vscode_workspace)
                if ws_path.exists():
                    logger.info(f"✅ Workspace detected via VSCODE_WORKSPACE_FOLDER: {ws_path}")
                    return ws_path
            
            # Method 2: Check current working directory
            cwd = Path.cwd()
            if cwd.exists() and (cwd / '.git').exists():
                logger.info(f"✅ Workspace detected via CWD: {cwd}")
                return cwd
            
            # Method 3: Check parent directories for .git
            current = Path.cwd()
            for _ in range(5):  # Check up to 5 levels
                if (current / '.git').exists():
                    logger.info(f"✅ Workspace detected via git search: {current}")
                    return current
                current = current.parent
            
            logger.warning("⚠️ Could not detect workspace")
            return None
            
        except Exception as e:
            logger.error(f"❌ Workspace detection error: {e}")
            return None
    
    def _load_workspace_config(self) -> Optional[Dict]:
        """
        Load workspace configuration from akr-config.json or .akr-config.json.
        
        Returns:
            Configuration dictionary, or None if not found.
        """
        if self.workspace_path is None:
            return None
        
        logger.info(f"📋 Loading workspace config from {self.workspace_path}")
        
        try:
            import json
            
            # Try different config file names
            config_names = ['akr-config.json', '.akr-config.json', 'config.json']
            
            for config_name in config_names:
                config_path = self.workspace_path / config_name
                
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    logger.info(f"✅ Config loaded: {config_path}")
                    return config
            
            logger.warning(f"⚠️ No config file found in {self.workspace_path}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error loading config: {e}")
            return None
    
    def detect_workspace(self) -> Optional[Path]:
        """
        Public method to detect workspace (lazy load if needed).
        
        Returns:
            Path to workspace root, or None if not detected.
        """
        # If already detected, return cached value
        if self.workspace_path is not None:
            return self.workspace_path
        
        # If in skip mode and not yet detected, skip now
        if self.skip_detection:
            logger.info("⚡ Workspace detection skipped (fast mode)")
            return None
        
        # Otherwise, detect now
        self.workspace_path = self._detect_workspace()
        return self.workspace_path
    
    def load_workspace_config(self, workspace_path: Optional[Path] = None) -> Dict:
        """
        Load workspace configuration (lazy load if needed).
        
        Args:
            workspace_path: Optional path to workspace. If not provided,
                           uses detected workspace.
        
        Returns:
            Configuration dictionary.
        """
        # If workspace path provided, use it
        if workspace_path is not None:
            self.workspace_path = workspace_path
            self.workspace_config = self._load_workspace_config()
            return self.workspace_config or {}
        
        # If already loaded, return cached value
        if self.workspace_config is not None:
            return self.workspace_config
        
        # If in skip mode, return empty config
        if self.skip_detection:
            logger.info("⚡ Config loading skipped (fast mode)")
            return {}
        
        # Otherwise, detect workspace and load config
        if self.workspace_path is None:
            self.workspace_path = self.detect_workspace()
        
        self.workspace_config = self._load_workspace_config()
        return self.workspace_config or {}
    
    def get_workspace_path(self) -> Optional[Path]:
        """Get cached workspace path without triggering detection."""
        return self.workspace_path
    
    def get_workspace_config(self) -> Optional[Dict]:
        """Get cached workspace config without triggering load."""
        return self.workspace_config


# ==================== NEW CODE: FACTORY FUNCTION ====================
def create_workspace_manager(
    load_config: bool = False,
    skip_detection: bool = False
) -> WorkspaceManager:
    """
    Create a workspace manager instance.
    
    Args:
        load_config: If True, load workspace config immediately.
                    If False (default), load on first access (lazy).
        skip_detection: If True, skip workspace detection entirely.
                       Useful for fast mode.
    
    Returns:
        WorkspaceManager instance.
    
    Example:
        # Fast mode: skip detection
        mgr = create_workspace_manager(load_config=False, skip_detection=True)
        
        # Normal mode: lazy load config
        mgr = create_workspace_manager(load_config=False, skip_detection=False)
        config = mgr.load_workspace_config()  # Loads on first access
    """
    skip = skip_detection or SKIP_WORKSPACE_SCAN or FAST_MODE
    
    logger.info(f"Creating WorkspaceManager (load_config={load_config}, skip_detection={skip})")
    
    mgr = WorkspaceManager(skip_detection=skip)
    
    if load_config and not skip:
        mgr.load_workspace_config()
    
    return mgr
# =====================================================================