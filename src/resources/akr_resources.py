"""
AKR Resource Manager

Provides resource discovery, categorization, and content serving for AKR
documentation files. Supports charters, templates, and guides.

Resources are served via MCP resource protocol with URIs following the pattern:
    akr://<category>/<filename>

Examples:
    akr://charter/AKR_CHARTER_BACKEND.md
    akr://template/standard_service_template.md
    akr://guide/Backend_Service_Documentation_Developer_Guide.md
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

logger = logging.getLogger("akr-mcp-server.resources")

# ==================== NEW CODE: FAST MODE FLAG ====================
FAST_MODE = os.getenv('AKR_FAST_MODE', 'false').lower() == 'true'
# ==================================================================


class ResourceCategory(Enum):
    """Categories for AKR resources."""
    CHARTER = "charter"
    TEMPLATE = "template"
    GUIDE = "guide"


@dataclass
class AKRResource:
    """Represents a single AKR resource file."""
    category: ResourceCategory
    filename: str
    name: str
    description: str
    path: Path
    content: Optional[str] = None
    
    def load_content(self) -> str:
        """Load resource content from file."""
        if self.content is None:
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    self.content = f.read()
            except Exception as e:
                logger.error(f"Error loading {self.path}: {e}")
                self.content = f"Error: Could not load resource: {e}"
        return self.content


class AKRResourceManager:
    """
    Manages AKR resources (charters, templates, guides).
    
    Implements lazy loading: resources are discovered on first access,
    not at initialization.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize resource manager.
        
        Args:
            base_path: Base path for AKR resources. Defaults to ./akr_content
        """
        self.base_path = base_path or Path(__file__).parent.parent.parent / "akr_content"
        
        # ==================== NEW CODE: LAZY LOADING CACHES ====================
        # Don't scan directories until resources are requested
        self._charters: Optional[List[AKRResource]] = None
        self._templates: Optional[List[AKRResource]] = None
        self._guides: Optional[List[AKRResource]] = None
        self._resource_cache: Dict[str, str] = {}
        # =====================================================================
        
        logger.info(f"AKRResourceManager initialized at {self.base_path}")
        logger.info(f"Fast mode: {FAST_MODE} (resources loaded on first access)")
    
    # ==================== NEW CODE: LAZY DISCOVERY METHODS ====================
    def _discover_charters(self) -> List[AKRResource]:
        """Discover charter files (lazy load on first call)."""
        if self._charters is not None:
            return self._charters
        
        logger.info("📖 Discovering charter files...")
        self._charters = []
        charter_dir = self.base_path / "charters"
        
        if not charter_dir.exists():
            logger.warning(f"Charter directory not found: {charter_dir}")
            return self._charters
        
        try:
            for charter_file in charter_dir.glob("*.md"):
                if charter_file.name.startswith("."):
                    continue
                
                resource = AKRResource(
                    category=ResourceCategory.CHARTER,
                    filename=charter_file.name,
                    name=charter_file.stem,
                    description=f"AKR Charter: {charter_file.stem}",
                    path=charter_file
                )
                self._charters.append(resource)
                logger.debug(f"  ✓ Found charter: {charter_file.name}")
            
            logger.info(f"✅ Discovered {len(self._charters)} charters")
        
        except Exception as e:
            logger.error(f"Error discovering charters: {e}")
        
        return self._charters
    
    def _discover_templates(self) -> List[AKRResource]:
        """Discover template files (lazy load on first call)."""
        if self._templates is not None:
            return self._templates
        
        logger.info("📋 Discovering template files...")
        self._templates = []
        template_dir = self.base_path / "templates"
        
        if not template_dir.exists():
            logger.warning(f"Template directory not found: {template_dir}")
            return self._templates
        
        try:
            for template_file in template_dir.glob("*.md"):
                if template_file.name.startswith("."):
                    continue
                
                resource = AKRResource(
                    category=ResourceCategory.TEMPLATE,
                    filename=template_file.name,
                    name=template_file.stem,
                    description=f"AKR Template: {template_file.stem}",
                    path=template_file
                )
                self._templates.append(resource)
                logger.debug(f"  ✓ Found template: {template_file.name}")
            
            logger.info(f"✅ Discovered {len(self._templates)} templates")
        
        except Exception as e:
            logger.error(f"Error discovering templates: {e}")
        
        return self._templates
    
    def _discover_guides(self) -> List[AKRResource]:
        """Discover guide files (lazy load on first call)."""
        if self._guides is not None:
            return self._guides
        
        logger.info("📚 Discovering guide files...")
        self._guides = []
        guide_dir = self.base_path / "guides"
        
        if not guide_dir.exists():
            logger.warning(f"Guide directory not found: {guide_dir}")
            return self._guides
        
        try:
            for guide_file in guide_dir.glob("*.md"):
                if guide_file.name.startswith("."):
                    continue
                
                resource = AKRResource(
                    category=ResourceCategory.GUIDE,
                    filename=guide_file.name,
                    name=guide_file.stem,
                    description=f"Developer Guide: {guide_file.stem}",
                    path=guide_file
                )
                self._guides.append(resource)
                logger.debug(f"  ✓ Found guide: {guide_file.name}")
            
            logger.info(f"✅ Discovered {len(self._guides)} guides")
        
        except Exception as e:
            logger.error(f"Error discovering guides: {e}")
        
        return self._guides
    # =====================================================================
    
    def list_charters(self) -> List[AKRResource]:
        """List all available charter resources."""
        return self._discover_charters()
    
    def list_templates(self) -> List[AKRResource]:
        """List all available template resources."""
        return self._discover_templates()

    def resolve_template_filename(self, template_name: str) -> tuple[Optional[str], List[str]]:
        """Resolve a user-provided template name to a concrete filename.

        Supports:
        - Exact filename match
        - Case-insensitive match
        - Name without .md extension
        - Simple aliases (e.g., "lean", "standard", "ui")
        - Partial stem match when unambiguous

        Returns:
            (resolved_filename, matches)
            - resolved_filename is None when no match or ambiguous
            - matches contains candidate filenames when ambiguous
        """
        if not template_name:
            return None, []

        raw = template_name.strip()
        if raw.startswith("akr://template/"):
            raw = raw.split("akr://template/", 1)[1]

        available = [t.filename for t in self.list_templates()]
        if not available:
            return None, []

        if raw in available:
            return raw, [raw]

        lowered = raw.lower()
        lower_map = {name.lower(): name for name in available}
        if lowered in lower_map:
            match = lower_map[lowered]
            return match, [match]

        def normalize(value: str) -> str:
            cleaned = value.strip().lower()
            if cleaned.startswith("akr://template/"):
                cleaned = cleaned.split("akr://template/", 1)[1]
            if cleaned.endswith(".md"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.replace("-", "_").replace(" ", "_")
            while "__" in cleaned:
                cleaned = cleaned.replace("__", "_")
            return cleaned

        normalized_input = normalize(raw)
        alias_map = {
            "lean": "lean_baseline_service_template.md",
            "baseline": "lean_baseline_service_template.md",
            "lean_baseline": "lean_baseline_service_template.md",
            "standard": "standard_service_template.md",
            "comprehensive": "comprehensive_service_template.md",
            "minimal": "minimal_service_template.md",
            "ui": "ui_component_template.md",
            "ui_component": "ui_component_template.md",
            "table": "table_doc_template.md",
            "database": "table_doc_template.md",
        }
        if normalized_input in alias_map:
            candidate = alias_map[normalized_input]
            if candidate in available:
                return candidate, [candidate]

        stem_map: Dict[str, List[str]] = {}
        for filename in available:
            stem_key = normalize(Path(filename).stem)
            stem_map.setdefault(stem_key, []).append(filename)

        if normalized_input in stem_map:
            matches = stem_map[normalized_input]
            if len(matches) == 1:
                return matches[0], matches
            return None, matches

        partial_matches = [
            name for name in available
            if normalized_input and normalized_input in normalize(Path(name).stem)
        ]
        if len(partial_matches) == 1:
            return partial_matches[0], partial_matches
        if len(partial_matches) > 1:
            return None, partial_matches

        return None, []
    
    def list_guides(self) -> List[AKRResource]:
        """List all available guide resources."""
        return self._discover_guides()
    
    def get_resource_content(self, category: str, filename: str) -> Optional[str]:
        """
        Get resource content by category and filename.
        
        Args:
            category: Resource category (charter, template, guide)
            filename: Filename (e.g., "AKR_CHARTER_BACKEND.md")
        
        Returns:
            Resource content, or None if not found.
        """
        # Check cache first
        cache_key = f"{category}:{filename}"
        if cache_key in self._resource_cache:
            return self._resource_cache[cache_key]
        
        try:
            if category == "charter":
                resources = self.list_charters()
            elif category == "template":
                resources = self.list_templates()
            elif category == "guide":
                resources = self.list_guides()
            else:
                logger.warning(f"Unknown resource category: {category}")
                return None
            
            # Find resource by filename
            for resource in resources:
                if resource.filename == filename:
                    content = resource.load_content()
                    self._resource_cache[cache_key] = content
                    return content
            
            logger.warning(f"Resource not found: {category}/{filename}")
            return None
        
        except Exception as e:
            logger.error(f"Error getting resource {category}/{filename}: {e}")
            return None
    
    def get_charter(self, domain: str) -> Optional[AKRResource]:
        """
        Get charter by domain (ui, backend, database).
        
        Args:
            domain: Domain name (ui, backend, database)
        
        Returns:
            Charter resource, or None if not found.
        """
        domain_lower = domain.lower()
        
        # Map domain to charter filename
        charter_map = {
            "ui": "AKR_CHARTER_UI.md",
            "backend": "AKR_CHARTER_BACKEND.md",
            "database": "AKR_CHARTER_DB.md",
            "api": "AKR_CHARTER_BACKEND.md",
            "db": "AKR_CHARTER_DB.md"
        }
        
        filename = charter_map.get(domain_lower)
        if not filename:
            logger.warning(f"No charter found for domain: {domain}")
            return None
        
        for charter in self.list_charters():
            if charter.filename == filename:
                return charter
        
        return None
    
    # ==================== PHASE 5: ASYNC INITIALIZATION ====================
    async def async_init(self) -> None:
        """
        Async background initialization for resource discovery.
        
        Performs resource discovery in thread pool to avoid blocking event loop.
        Useful for server startup to warm up the lazy caches without blocking.
        
        Example:
            # In server startup
            resource_mgr = create_resource_manager()
            await resource_mgr.async_init()  # Discover templates in background
        """
        loop = asyncio.get_event_loop()
        
        # Discovery happens in thread pool
        logger.info("🚀 Starting async resource discovery...")
        
        # Discover all resource types concurrently
        await asyncio.gather(
            loop.run_in_executor(None, self.list_charters),
            loop.run_in_executor(None, self.list_templates),
            loop.run_in_executor(None, self.list_guides),
        )
        
        logger.info(
            f"✅ Async resource discovery complete: "
            f"{len(self._charters or [])} charters, "
            f"{len(self._templates or [])} templates, "
            f"{len(self._guides or [])} guides"
        )
    # ================================================================


# ==================== NEW CODE: FACTORY FUNCTION ====================
# ==================== PHASE 5: ASYNC INITIALIZATION ====================
def create_resource_manager(base_path: Optional[Path] = None) -> AKRResourceManager:
    """
    Create and return a resource manager instance.
    
    Args:
        base_path: Optional base path for AKR resources.
                  Defaults to ./akr_content
    
    Returns:
        Initialized AKRResourceManager instance.
    
    Note:
        Resources are NOT discovered at initialization time.
        Discovery happens lazily on first access.
        This keeps startup fast even in large repositories.
    
    Example:
        mgr = create_resource_manager()
        # Server starts instantly
        charters = mgr.list_charters()  # Discovery happens here
    """
    logger.info("Creating AKRResourceManager (lazy loading enabled)")
    return AKRResourceManager(base_path=base_path)
# =====================================================================