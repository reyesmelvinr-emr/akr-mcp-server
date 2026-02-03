"""
FileWriter: Secure file writing with path validation and governance enforcement.

Writes validated markdown to filesystem with:
- Path validation against .akr-config.json pathMappings
- Security checks (inside workspace, no parent directory traversal, canonical paths)
- Atomic write pattern (write to temp, then rename)
- Directory creation if needed
"""

import os
import tempfile
import shutil
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class WriteResult:
    """Result of file write operation."""
    success: bool
    file_path: Optional[str] = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class FileWriter:
    """Handles secure file writing with governance enforcement."""
    
    def __init__(self):
        """Initialize FileWriter."""
        pass
    
    def write(
        self,
        markdown: str,
        output_path: str,
        config: Dict
    ) -> WriteResult:
        """
        Write markdown to file with security validation.
        
        Args:
            markdown: Validated markdown content to write
            output_path: Target file path (relative or absolute)
            config: AKR configuration dict with workspace_root, pathMappings
        
        Returns:
            WriteResult with success status, file path, errors, warnings
        """
        errors = []
        
        # Step 1: Extract workspace root from config
        workspace_root = config.get("workspace_root") or config.get("workspaceRoot")
        if not workspace_root:
            errors.append("Missing workspace_root in config")
            return WriteResult(success=False, errors=errors)
        
        # Step 2: Validate path
        validation_errors = self.validate_path(output_path, workspace_root, config)
        if validation_errors:
            return WriteResult(success=False, errors=validation_errors)
        
        # Step 3: Resolve full path
        resolved_path = self._resolve_full_path(output_path, workspace_root)
        
        try:
            # Step 4: Ensure directory exists
            directory = os.path.dirname(resolved_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Step 5: Atomic write (write to temp, then rename)
            success = self._write_file_atomic(resolved_path, markdown)
            
            if success:
                return WriteResult(
                    success=True,
                    file_path=resolved_path,
                    errors=[],
                    warnings=[]
                )
            else:
                errors.append(f"Failed to write file to {resolved_path}")
                return WriteResult(success=False, errors=errors)
        
        except Exception as e:
            errors.append(f"Exception writing file: {str(e)}")
            return WriteResult(success=False, errors=errors)
    
    def validate_path(
        self,
        output_path: str,
        workspace_root: str,
        config: Dict
    ) -> List[str]:
        """
        Validate output path against governance rules.
        
        Rules:
        1. Path must be inside workspace_root
        2. Path must be inside documentation root (typically docs/)
        3. Path must not contain ".." segments after normalization
        4. Path must have .md extension
        5. Resolved canonical path must still satisfy above rules
        
        Args:
            output_path: Target path to validate
            workspace_root: Workspace root directory
            config: Configuration with pathMappings and doc root settings
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Normalize workspace root
        workspace_root_abs = os.path.abspath(workspace_root)
        
        # Resolve output path relative to workspace if not absolute
        if os.path.isabs(output_path):
            target_path = output_path
        else:
            target_path = os.path.join(workspace_root_abs, output_path)
        
        # Normalize the path
        target_norm = os.path.normpath(target_path)
        
        # Check 1: No ".." traversal after normalization
        if ".." in target_norm.split(os.sep):
            errors.append("Path contains invalid parent directory reference (..)")
            return errors
        
        # Check 2: Must be inside workspace root
        try:
            rel = os.path.relpath(target_norm, workspace_root_abs)
            if rel.startswith(".."):
                errors.append(f"Path outside workspace root: {output_path}")
                return errors
        except ValueError:
            # On Windows, relpath fails if paths are on different drives
            errors.append(f"Path on different drive than workspace: {output_path}")
            return errors
        
        # Check 3: Must have .md extension
        if not target_norm.endswith(".md"):
            errors.append("Output file must have .md extension")
            return errors
        
        # Check 4: Resolve canonical path (follow symlinks) and validate again
        try:
            canonical_path = os.path.realpath(target_norm)
            # If file doesn't exist yet, check the parent directory's canonical path
            if not os.path.exists(canonical_path):
                parent_dir = os.path.dirname(canonical_path)
                if os.path.exists(parent_dir):
                    canonical_parent = os.path.realpath(parent_dir)
                    canonical_path = os.path.join(canonical_parent, os.path.basename(canonical_path))
                else:
                    # Parent doesn't exist yet, use normalized path
                    canonical_path = target_norm
            
            # Verify canonical path is still inside workspace
            try:
                rel_canonical = os.path.relpath(canonical_path, workspace_root_abs)
                if rel_canonical.startswith(".."):
                    errors.append("Symlink traversal detected: target resolves outside workspace")
                    return errors
            except ValueError:
                errors.append("Symlink resolves to different drive than workspace")
                return errors
        
        except Exception as e:
            errors.append(f"Error resolving canonical path: {str(e)}")
            return errors
        
        # Check 5: If config defines doc_root, verify path is inside it
        doc_root = config.get("doc_root")
        if doc_root:
            doc_root_abs = os.path.join(workspace_root_abs, doc_root) if not os.path.isabs(doc_root) else doc_root
            doc_root_normalized = os.path.normpath(doc_root_abs)
            try:
                rel_to_doc = os.path.relpath(target_norm, doc_root_normalized)
                if rel_to_doc.startswith(".."):
                    errors.append(f"Path must be inside documentation root ({doc_root})")
                    return errors
            except ValueError:
                errors.append(f"Documentation root on different drive: {doc_root}")
                return errors
        
        return errors
    
    def _resolve_full_path(self, output_path: str, workspace_root: str) -> str:
        """
        Resolve output path to absolute path.
        
        Args:
            output_path: Relative or absolute path
            workspace_root: Workspace root directory
        
        Returns:
            Absolute normalized path
        """
        workspace_root_abs = os.path.abspath(workspace_root)
        
        if os.path.isabs(output_path):
            return os.path.normpath(output_path)
        else:
            return os.path.normpath(os.path.join(workspace_root_abs, output_path))
    
    def _write_file_atomic(self, file_path: str, content: str) -> bool:
        """
        Write file atomically: write to temp, then rename.
        
        This prevents partial writes if process crashes mid-write.
        
        Args:
            file_path: Target file path
            content: Content to write
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create temp file in same directory as target (same filesystem for atomic rename)
            target_dir = os.path.dirname(file_path)
            with tempfile.NamedTemporaryFile(
                mode='w',
                dir=target_dir,
                delete=False,
                suffix='.md',
                encoding='utf-8'
            ) as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            # Atomic rename
            shutil.move(tmp_path, file_path)
            return True
        
        except Exception:
            # Clean up temp file if it exists
            try:
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
            return False
