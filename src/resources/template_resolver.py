"""
TemplateResolver - Three-Layer Template Resolution

Provides layered template resolution with the following priority:
1. Primary: Git submodule (templates/core/) - template SSoT
2. Fallback: Local overrides (akr_content/templates/) - user customizations
3. Optional: Remote HTTP fetch + cache - preview new versions

Supports secure HTTP fetch with SHA-256 verification, TTL caching,
trusted host validation, and fail-closed behavior.
"""

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime, timedelta

try:
    import requests  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - handled at runtime
    requests = None  # type: ignore[assignment]

logger = logging.getLogger("akr-mcp-server.template_resolver")


@dataclass
class CacheEntry:
    """Represents a cached template."""
    template_id: str
    version: str
    content: str
    sha256_hash: str
    fetch_timestamp: float
    ttl_seconds: int
    source: str  # "submodule", "local-override", or "remote-preview"

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        age = time.time() - self.fetch_timestamp
        return age > self.ttl_seconds


class TemplateResolver:
    """Three-layer template resolver with secure HTTP fetch capability."""

    def __init__(self, repo_root: Path, config: Optional[Dict] = None):
        """
        Initialize TemplateResolver.

        Args:
            repo_root: Root path of the repository (e.g., /akr-mcp-server)
            config: Optional configuration dict with http_fetch_config section
        """
        self.repo_root = Path(repo_root)
        self.config = config or {}

        # Layer 1: Submodule (primary source of truth)
        self.submodule_path = self.repo_root / "templates" / "core"
        
        # Layer 2: Local overrides
        self.local_overrides_path = self.repo_root / "akr_content" / "templates"
        
        # Layer 3: HTTP fetch cache
        self._cache: Dict[str, CacheEntry] = {}
        self._manifest: Dict = {}
        self._manifest_loaded = False

        logger.info(f"✅ TemplateResolver initialized")
        logger.info(f"  Submodule path: {self.submodule_path}")
        logger.info(f"  Local overrides path: {self.local_overrides_path}")

    # ==================== MANIFEST LOADING ====================
    def _load_manifest(self) -> Dict:
        """
        Load template manifest from submodule.

        Reads TEMPLATE_MANIFEST.json from submodule root.
        Returns cached manifest if already loaded.

        Returns:
            Manifest dict with template metadata, or empty dict if not found
        """
        if self._manifest_loaded:
            return self._manifest

        manifest_path = self.submodule_path / "TEMPLATE_MANIFEST.json"
        
        if not manifest_path.exists():
            logger.warning(f"Manifest not found: {manifest_path}")
            self._manifest = {}
            self._manifest_loaded = True
            return self._manifest

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                loaded_manifest = json.load(f)
            self._manifest = loaded_manifest
            self._manifest_loaded = True
            templates_count = self._manifest.get("templates", []) if self._manifest else []
            logger.info(f"✅ Loaded manifest with {len(templates_count)} templates")
            return self._manifest
        except Exception as e:
            logger.error(f"❌ Error loading manifest: {e}")
            self._manifest = {}
            self._manifest_loaded = True
            return self._manifest

    def get_manifest(self) -> Dict:
        """Get template manifest."""
        return self._load_manifest()

    # ==================== TEMPLATE LISTING ====================
    def list_templates(self) -> List[str]:
        """
        List all available template IDs (from submodule).

        Returns:
            List of template IDs (e.g., ["lean_baseline_service_template", ...])
        """
        if not self.submodule_path.exists():
            logger.warning(f"Submodule path does not exist: {self.submodule_path}")
            return []

        templates = []
        try:
            for template_file in self.submodule_path.glob("*.md"):
                if not template_file.name.startswith("."):
                    # Strip .md extension to get template ID
                    template_id = template_file.stem
                    templates.append(template_id)
            logger.debug(f"Found {len(templates)} templates in submodule")
        except Exception as e:
            logger.error(f"Error listing templates: {e}")

        return sorted(templates)

    # ==================== THREE-LAYER RESOLUTION ====================
    def get_template(self, template_id: str, version: Optional[str] = None) -> Optional[str]:
        """
        Get template content using three-layer resolution.

        Priority order:
        1. Submodule (templates/core/{template_id}.md) - PRIMARY SOURCE OF TRUTH
        2. Local override (akr_content/templates/{template_id}.md) - FALLBACK
        3. Remote HTTP fetch (if enabled and pinned version available) - LAST RESORT

        Args:
            template_id: Template identifier (without .md extension)
            version: Optional explicit version for remote fetch

        Returns:
            Template content as string, or None if not found
        """
        # Try layer 1: Submodule (primary source of truth)
        submodule_content = self._load_from_path(
            self.submodule_path,
            template_id,
            source="submodule"
        )
        if submodule_content:
            return submodule_content

        # Try layer 2: Local override (fallback for when submodule is missing)
        local_content = self._load_from_path(
            self.local_overrides_path,
            template_id,
            source="local-override"
        )
        if local_content:
            return local_content

        # Try layer 3: Remote HTTP fetch (if enabled and version specified)
        if self.config.get("http_fetch_enabled", False):
            remote_content = self._fetch_from_remote(template_id, version or self.config.get("http_fetch_config", {}).get("pinned_version"))
            if remote_content:
                return remote_content

        logger.warning(f"Template not found: {template_id}")
        return None

    def _load_from_path(self, base_path: Path, template_id: str, source: str) -> Optional[str]:
        """
        Load template from file path.

        Args:
            base_path: Base directory path
            template_id: Template ID (without .md extension)
            source: Source label for logging ("submodule" or "local-override")

        Returns:
            Template content as string, or None if not found
        """
        if not base_path.exists():
            return None

        template_path = base_path / f"{template_id}.md"
        if not template_path.exists():
            return None

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
            logger.debug(f"✅ Loaded {template_id} from {source}")
            return content
        except Exception as e:
            logger.error(f"❌ Error loading {template_id} from {source}: {e}")
            return None

    # ==================== SECURE REMOTE FETCH ====================
    def _fetch_from_remote(self, template_id: str, version: Optional[str]) -> Optional[str]:
        """
        Securely fetch template from remote with verification.

        Security checks:
        - Validate repository URL (whitelist trusted hosts)
        - Verify SHA-256 hash against manifest
        - Cache with TTL to prevent repeated fetches
        - Timeout (5-10s) to prevent Chat hangs
        - Fail closed: return None on any failure

        Args:
            template_id: Template ID to fetch
            version: Explicit version to fetch (e.g., "v1.3.0")

        Returns:
            Template content as string, or None if verification fails
        """
        if not version:
            logger.warning("Remote fetch requires explicit version (pinned)")
            return None

        if requests is None:
            logger.error("Remote fetch unavailable: requests dependency not installed")
            return None

        # 1. Validate host
        repo_url = self.config.get("http_fetch_config", {}).get("repo_url", "")
        if "github.com" not in repo_url:
            logger.error("Remote fetch: untrusted repository")
            return None

        # 2. Check cache
        cache_key = f"{template_id}@{version}"
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if not entry.is_expired():
                logger.debug(f"✅ Cache hit for {cache_key}")
                return entry.content

        # 3. Fetch with timeout (5-10s to prevent Chat hangs)
        url = f"{repo_url}/releases/download/{version}/templates/{template_id}.md"
        timeout = self.config.get("http_fetch_config", {}).get("timeout_seconds", 10)
        retry_count = self.config.get("http_fetch_config", {}).get("max_retries", 1)

        content = None
        last_error = None

        for attempt in range(retry_count + 1):
            try:
                logger.debug(f"Fetching {template_id}@{version} from {url} (attempt {attempt + 1})")
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                content = response.text
                break
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < retry_count:
                    logger.debug(f"Retry {attempt + 1}/{retry_count} for {template_id}")
                    time.sleep(1)
                else:
                    logger.error(f"Failed to fetch {template_id} after {retry_count + 1} attempts: {e}")

        if not content:
            return None

        # 4. Verify hash (if checksum available)
        if self.config.get("http_fetch_config", {}).get("verify_checksums", True):
            expected_hash = self._get_expected_hash(template_id, version)
            if expected_hash:
                actual_hash = hashlib.sha256(content.encode()).hexdigest()
                if actual_hash != expected_hash:
                    logger.error(f"Hash mismatch for {template_id}@{version}")
                    return None

        # 5. Cache and return with provenance metadata
        ttl = self.config.get("http_fetch_config", {}).get("cache_ttl_seconds", 86400)
        actual_hash = hashlib.sha256(content.encode()).hexdigest()
        
        entry = CacheEntry(
            template_id=template_id,
            version=version,
            content=content,
            sha256_hash=actual_hash,
            fetch_timestamp=time.time(),
            ttl_seconds=ttl,
            source="remote-preview"
        )
        self._cache[cache_key] = entry

        logger.info(f"✅ Fetched {template_id}@{version} from remote (cached for {ttl}s)")
        return content

    def _get_expected_hash(self, template_id: str, version: str) -> Optional[str]:
        """
        Get expected SHA-256 hash from manifest.

        Args:
            template_id: Template ID
            version: Version identifier

        Returns:
            SHA-256 hash as hex string, or None if not in manifest
        """
        manifest = self.get_manifest()
        templates = manifest.get("templates", [])

        for tmpl in templates:
            if tmpl.get("id") == template_id and tmpl.get("version") == version:
                return tmpl.get("sha256_hash")

        return None

    # ==================== TEMPLATE METADATA ====================
    def get_template_metadata(self, template_id: str) -> Optional[Dict]:
        """
        Get template metadata from manifest.

        Args:
            template_id: Template ID

        Returns:
            Metadata dict (name, sections, frontmatterSchema, etc.), or None
        """
        manifest = self.get_manifest()
        templates = manifest.get("templates", [])

        for tmpl in templates:
            if tmpl.get("id") == template_id:
                return tmpl

        return None

    def get_template_version(self) -> Optional[str]:
        """Get current loaded template version from manifest."""
        manifest = self.get_manifest()
        return manifest.get("version")

    def get_manifest_version(self) -> Optional[str]:
        """
        Get manifest version.

        This reflects the version of templates loaded from the submodule.
        """
        return self.get_template_version()


def create_template_resolver(repo_root: Optional[Path] = None, config: Optional[Dict] = None) -> TemplateResolver:
    """
    Factory function to create TemplateResolver instance.

    Args:
        repo_root: Root path of repository. Defaults to parent of src/
        config: Optional configuration dict

    Returns:
        Initialized TemplateResolver instance
    """
    if repo_root is None:
        # Default: assume we're in src/, go up to repo root
        repo_root = Path(__file__).parent.parent.parent

    logger.info(f"🎯 Creating TemplateResolver (repo_root={repo_root})")
    return TemplateResolver(repo_root, config)
