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

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger("akr-mcp-server.resources")


class ResourceCategory(Enum):
    """Categories for AKR resources."""
    CHARTER = "charter"
    TEMPLATE = "template"
    GUIDE = "guide"
    
    @classmethod
    def from_folder(cls, folder_name: str) -> Optional["ResourceCategory"]:
        """Get category from folder name."""
        mapping = {
            "charters": cls.CHARTER,
            "templates": cls.TEMPLATE,
            "guides": cls.GUIDE
        }
        return mapping.get(folder_name.lower())
    
    @property
    def folder_name(self) -> str:
        """Get the folder name for this category."""
        mapping = {
            ResourceCategory.CHARTER: "charters",
            ResourceCategory.TEMPLATE: "templates",
            ResourceCategory.GUIDE: "guides"
        }
        return mapping[self]
    
    @property
    def description(self) -> str:
        """Get a human-readable description for this category."""
        descriptions = {
            ResourceCategory.CHARTER: "Documentation standards and requirements",
            ResourceCategory.TEMPLATE: "Documentation structure templates",
            ResourceCategory.GUIDE: "Developer guides and best practices"
        }
        return descriptions[self]


@dataclass
class AKRResource:
    """
    Represents a single AKR documentation resource.
    
    Attributes:
        uri: MCP resource URI (e.g., "akr://charter/AKR_CHARTER_BACKEND.md")
        name: Display name of the resource
        category: Resource category (charter, template, guide)
        file_path: Absolute path to the file
        description: Human-readable description
        mime_type: MIME type (always text/markdown for AKR files)
        metadata: Additional metadata like file size, modified date
    """
    uri: str
    name: str
    category: ResourceCategory
    file_path: Path
    description: str = ""
    mime_type: str = "text/markdown"
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize metadata if not provided."""
        if not self.metadata and self.file_path.exists():
            stat = self.file_path.stat()
            self.metadata = {
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": self.file_path.suffix
            }
    
    def read_content(self) -> str:
        """Read and return the file content."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Resource file not found: {self.file_path}")
        return self.file_path.read_text(encoding='utf-8')
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "uri": self.uri,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "mimeType": self.mime_type,
            "metadata": self.metadata
        }


class AKRResourceManager:
    """
    Manages discovery, categorization, and serving of AKR resources.
    
    This class handles:
    - Scanning the AKR content directory for markdown files
    - Categorizing resources by type (charter, template, guide)
    - Creating MCP-compatible resource URIs
    - Reading resource content on demand
    
    Usage:
        manager = AKRResourceManager("/path/to/akr_content")
        resources = manager.list_resources()
        content = manager.read_resource("akr://charter/AKR_CHARTER_BACKEND.md")
    """
    
    # File extensions to include as resources
    SUPPORTED_EXTENSIONS = {".md", ".markdown"}
    
    # Files to exclude from resource listing
    EXCLUDED_FILES = {".gitkeep", ".gitignore", "README.md"}
    
    def __init__(self, akr_content_path: str | Path):
        """
        Initialize the resource manager.
        
        Args:
            akr_content_path: Path to the akr_content directory
        """
        self.akr_content_path = Path(akr_content_path)
        self._resources_cache: dict[str, AKRResource] = {}
        self._last_scan: Optional[datetime] = None
        
        logger.info(f"AKRResourceManager initialized with path: {self.akr_content_path}")
        
        if not self.akr_content_path.exists():
            logger.warning(f"AKR content path does not exist: {self.akr_content_path}")
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included as a resource."""
        if file_path.name in self.EXCLUDED_FILES:
            return False
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return False
        if not file_path.is_file():
            return False
        return True
    
    def _create_uri(self, category: ResourceCategory, filename: str) -> str:
        """Create an MCP resource URI for a file."""
        return f"akr://{category.value}/{filename}"
    
    def _parse_uri(self, uri: str) -> tuple[Optional[ResourceCategory], Optional[str]]:
        """
        Parse an MCP resource URI into category and filename.
        
        Args:
            uri: Resource URI (e.g., "akr://charter/AKR_CHARTER_BACKEND.md")
            
        Returns:
            Tuple of (category, filename) or (None, None) if invalid
        """
        if not uri.startswith("akr://"):
            logger.warning(f"Invalid URI scheme: {uri}")
            return None, None
        
        try:
            # Remove "akr://" prefix
            path_part = uri[6:]
            parts = path_part.split("/", 1)
            
            if len(parts) != 2:
                logger.warning(f"Invalid URI format: {uri}")
                return None, None
            
            category_str, filename = parts
            category = None
            for cat in ResourceCategory:
                if cat.value == category_str:
                    category = cat
                    break
            
            if not category:
                logger.warning(f"Unknown category in URI: {category_str}")
                return None, None
            
            return category, filename
        except Exception as e:
            logger.error(f"Error parsing URI '{uri}': {e}")
            return None, None
    
    def _generate_description(self, file_path: Path, category: ResourceCategory) -> str:
        """Generate a description for a resource based on its name and category."""
        name = file_path.stem
        
        # Common description patterns
        descriptions = {
            # Charters
            "AKR_CHARTER": "Main AKR documentation charter with general standards",
            "AKR_CHARTER_BACKEND": "Backend service documentation requirements and standards",
            "AKR_CHARTER_DB": "Database documentation requirements and standards",
            "AKR_CHARTER_UI": "UI component documentation requirements and standards",
            
            # Templates
            "comprehensive_service_template": "Full-featured service documentation template with all sections",
            "standard_service_template": "Standard service documentation template for most use cases",
            "lean_baseline_service_template": "Minimal service documentation template for simple services",
            "minimal_service_template": "Ultra-minimal documentation template",
            "table_doc_template": "Database table documentation template",
            "ui_component_template": "UI component documentation template",
            
            # Guides
            "Backend_Service_Documentation_Developer_Guide": "Guide for documenting backend services",
            "Backend_Service_Documentation_Guide": "Backend service documentation overview",
            "Table_Documentation_Developer_Guide": "Guide for documenting database tables",
            "UI_Component_Documentation_Developer_Guide": "Guide for documenting UI components",
        }
        
        if name in descriptions:
            return descriptions[name]
        
        # Generate generic description based on category
        return f"{category.description}: {name.replace('_', ' ')}"
    
    def scan_resources(self, force: bool = False) -> dict[str, AKRResource]:
        """
        Scan the AKR content directory and discover all resources.
        
        Args:
            force: If True, force rescan even if cache is recent
            
        Returns:
            Dictionary mapping URIs to AKRResource objects
        """
        # Simple cache check - rescan if forced or first time
        if not force and self._resources_cache and self._last_scan:
            logger.debug("Using cached resources")
            return self._resources_cache
        
        logger.info("Scanning AKR content directory for resources...")
        resources = {}
        
        if not self.akr_content_path.exists():
            logger.warning(f"AKR content path does not exist: {self.akr_content_path}")
            return resources
        
        # Scan each category folder
        for category in ResourceCategory:
            folder_path = self.akr_content_path / category.folder_name
            
            if not folder_path.exists():
                logger.debug(f"Category folder does not exist: {folder_path}")
                continue
            
            for file_path in folder_path.iterdir():
                if not self._should_include_file(file_path):
                    continue
                
                uri = self._create_uri(category, file_path.name)
                description = self._generate_description(file_path, category)
                
                resource = AKRResource(
                    uri=uri,
                    name=file_path.stem.replace('_', ' '),
                    category=category,
                    file_path=file_path,
                    description=description
                )
                
                resources[uri] = resource
                logger.debug(f"Discovered resource: {uri}")
        
        self._resources_cache = resources
        self._last_scan = datetime.now()
        
        logger.info(f"Discovered {len(resources)} resources: "
                   f"{sum(1 for r in resources.values() if r.category == ResourceCategory.CHARTER)} charters, "
                   f"{sum(1 for r in resources.values() if r.category == ResourceCategory.TEMPLATE)} templates, "
                   f"{sum(1 for r in resources.values() if r.category == ResourceCategory.GUIDE)} guides")
        
        return resources
    
    def list_resources(self, category: Optional[ResourceCategory] = None) -> list[AKRResource]:
        """
        List all available resources, optionally filtered by category.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of AKRResource objects
        """
        resources = self.scan_resources()
        
        if category:
            return [r for r in resources.values() if r.category == category]
        
        return list(resources.values())
    
    def read_resource(self, uri: str) -> Optional[str]:
        """
        Read the content of a resource by URI.
        
        Args:
            uri: Resource URI (e.g., "akr://charter/AKR_CHARTER_BACKEND.md")
            
        Returns:
            Resource content as string, or None if not found
        """
        resources = self.scan_resources()
        
        if uri not in resources:
            logger.warning(f"Resource not found: {uri}")
            return None
        
        try:
            content = resources[uri].read_content()
            logger.debug(f"Read resource: {uri} ({len(content)} bytes)")
            return content
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            return None
    
    def get_resource(self, uri: str) -> Optional[AKRResource]:
        """
        Get a resource object by URI.
        
        Args:
            uri: Resource URI
            
        Returns:
            AKRResource object or None if not found
        """
        resources = self.scan_resources()
        return resources.get(uri)
    
    def get_resources_by_category(self) -> dict[str, list[AKRResource]]:
        """
        Get all resources grouped by category.
        
        Returns:
            Dictionary with category names as keys and lists of resources as values
        """
        result = {
            "charters": [],
            "templates": [],
            "guides": []
        }
        
        for resource in self.list_resources():
            result[resource.category.folder_name].append(resource)
        
        return result
    
    def get_resource_count(self) -> dict[str, int]:
        """
        Get count of resources by category.
        
        Returns:
            Dictionary with category names and counts
        """
        resources = self.scan_resources()
        return {
            "total": len(resources),
            "charters": sum(1 for r in resources.values() if r.category == ResourceCategory.CHARTER),
            "templates": sum(1 for r in resources.values() if r.category == ResourceCategory.TEMPLATE),
            "guides": sum(1 for r in resources.values() if r.category == ResourceCategory.GUIDE)
        }


# Convenience function for creating a resource manager with default path
def create_resource_manager(base_path: Optional[Path] = None) -> AKRResourceManager:
    """
    Create an AKRResourceManager with the default or specified path.
    
    Args:
        base_path: Optional base path. If not provided, uses the default
                   akr_content directory relative to this module.
                   
    Returns:
        Configured AKRResourceManager instance
    """
    if base_path is None:
        # Default: akr_content directory relative to src/resources
        base_path = Path(__file__).parent.parent.parent / "akr_content"
    
    return AKRResourceManager(base_path)
