"""
Jinja2 Template Renderer for AKR Documentation.

Provides Jinja2 environment setup, custom filters, template loading,
and rendering functions for service, component, and table contexts.

Key Components:
    - JinjaEnvironment: Configured Jinja2 environment with custom filters
    - TemplateRenderer: Main class for loading and rendering templates
    - render_service_template(): Render service documentation
    - render_component_template(): Render component documentation
    - render_table_template(): Render table documentation
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from jinja2 import Environment, FileSystemLoader, ChoiceLoader, DictLoader, TemplateNotFound

from .template_context import (
    ServiceTemplateContext, ComponentTemplateContext, TableTemplateContext
)


logger = logging.getLogger(__name__)


# ============================================================================
# CUSTOM FILTERS FOR JINJA2 TEMPLATES
# ============================================================================

def filter_yes_no(value: Any, yes_text: str = "Yes", no_text: str = "No") -> str:
    """
    Convert boolean to Yes/No display text.
    
    Usage in template: {{ is_critical | yes_no }}
    """
    if isinstance(value, bool):
        return yes_text if value else no_text
    return str(value) if value else no_text


def filter_required_nullable(required: bool, nullable: bool) -> str:
    """
    Convert boolean flags to required/nullable display text.
    
    Usage in template: {{ prop.required | required_nullable(column.nullable) }}
    """
    if required:
        return "Required"
    if nullable:
        return "Optional (nullable)"
    return "Optional"


def filter_title_case(value: str) -> str:
    """
    Convert snake_case or UPPER_CASE to Title Case.
    
    Usage in template: {{ 'user_profile' | title_case }}
    """
    # Handle snake_case
    if '_' in value:
        return ' '.join(word.capitalize() for word in value.split('_'))
    # Handle UPPER_CASE
    if value.isupper():
        return ' '.join(word.capitalize() for word in value.split('_'))
    # Already title case or needs no change
    return value


def filter_http_method_color(method: str) -> str:
    """
    Get HTML/Markdown color indicator for HTTP method.
    
    Usage in template: {{ route.method | http_method_color }}
    Returns: GET (blue), POST (green), PUT (orange), DELETE (red)
    """
    colors = {
        'GET': '🔵',
        'POST': '🟢',
        'PUT': '🟠',
        'DELETE': '🔴',
        'PATCH': '🟡',
        'HEAD': '⚫',
        'OPTIONS': '⚪'
    }
    return colors.get(method.upper(), method)


def filter_join_list(items: List[Any], separator: str = ", ", quote: bool = False) -> str:
    """
    Join a list of items with separator.
    
    Usage in template: {{ tags | join_list }}
    """
    if not items:
        return ""
    items_str = [f'"{item}"' if quote else str(item) for item in items]
    return separator.join(items_str)


def filter_code_block(value: str, language: str = "python") -> str:
    """
    Wrap text in markdown code block.
    
    Usage in template: {{ sql_expression | code_block('sql') }}
    """
    if not value:
        return ""
    return f"```{language}\n{value}\n```"


def filter_truncate_smart(value: str, length: int = 100) -> str:
    """
    Truncate text at word boundary.
    
    Usage in template: {{ description | truncate_smart(80) }}
    """
    if len(value) <= length:
        return value
    
    truncated = value[:length]
    # Find last space
    last_space = truncated.rfind(' ')
    if last_space > length * 0.7:  # If last space is reasonably close
        return value[:last_space] + "..."
    return truncated + "..."


def filter_default_if_empty(value: Any, default: str = "[Not yet defined]") -> str:
    """
    Return default text if value is empty.
    
    Usage in template: {{ description | default_if_empty('TBD') }}
    """
    if not value or (isinstance(value, str) and not value.strip()):
        return default
    return str(value)


# ============================================================================
# JINJA2 ENVIRONMENT SETUP
# ============================================================================

class JinjaEnvironment:
    """Configured Jinja2 environment with custom filters and settings."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern - one environment instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Jinja2 environment with custom configuration."""
        # Create environment with multiple loaders (filesystem + dict)
        # This allows both file-based and in-memory templates
        self.env = Environment(
            loader=ChoiceLoader([
                FileSystemLoader(self._get_template_dirs()),
                DictLoader({})  # Will be populated with built-in templates
            ]),
            autoescape=False,  # We're generating Markdown, not HTML
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # Register custom filters
        self.env.filters['yes_no'] = filter_yes_no
        self.env.filters['required_nullable'] = filter_required_nullable
        self.env.filters['title_case'] = filter_title_case
        self.env.filters['http_method_color'] = filter_http_method_color
        self.env.filters['join_list'] = filter_join_list
        self.env.filters['code_block'] = filter_code_block
        self.env.filters['truncate_smart'] = filter_truncate_smart
        self.env.filters['default_if_empty'] = filter_default_if_empty
        
        # Register global functions
        self.env.globals['len'] = len
        self.env.globals['range'] = range
        
        logger.info("Jinja2 environment initialized with custom filters")
    
    def _get_template_dirs(self) -> List[str]:
        """Get list of directories to search for templates."""
        dirs = []
        
        # Primary location: akr_content/templates/*.jinja2
        template_dir = Path(__file__).parent.parent.parent / "akr_content" / "templates"
        if template_dir.exists():
            dirs.append(str(template_dir))
        
        # Fallback: src/tools/templates/
        fallback_dir = Path(__file__).parent / "templates"
        if fallback_dir.exists():
            dirs.append(str(fallback_dir))
        
        logger.info(f"Template search directories: {dirs}")
        return dirs
    
    def get_environment(self) -> Environment:
        """Get the Jinja2 environment instance."""
        return self.env


# ============================================================================
# TEMPLATE RENDERER CLASS
# ============================================================================

class TemplateRenderer:
    """
    Main class for rendering documentation templates with extracted data.
    
    Handles:
    - Template loading from filesystem
    - Rendering with context data
    - Error handling and fallbacks
    - Output validation
    """
    
    def __init__(self):
        """Initialize renderer with Jinja2 environment."""
        self.jinja_env = JinjaEnvironment()
        self.env = self.jinja_env.get_environment()
    
    def render_service_template(
        self,
        context: ServiceTemplateContext,
        template_name: str = "lean_baseline_service_template.jinja2"
    ) -> str:
        """
        Render service documentation template using Jinja2.
        
        Args:
            context: ServiceTemplateContext with extracted service data
            template_name: Name of template file (default: lean_baseline_service_template.jinja2)
            
        Returns:
            Rendered markdown string
            
        Raises:
            TemplateNotFound: If template doesn't exist
            Exception: If rendering fails
        """
        logger.info(f"Rendering service template for {context.service_name}")
        
        try:
            template = self.env.get_template(template_name)
            
            # Convert context to dict for Jinja2
            context_dict = self._context_to_dict(context)
            
            rendered = template.render(context_dict)
            
            logger.info(
                f"Successfully rendered {context.service_name}: "
                f"{len(rendered)} characters"
            )
            
            return rendered
            
        except TemplateNotFound as e:
            logger.error(f"Template not found: {template_name}")
            raise
        except Exception as e:
            logger.error(f"Error rendering service template: {e}", exc_info=True)
            raise
    
    def render_component_template(
        self,
        context: ComponentTemplateContext,
        template_name: str = "component.jinja2"
    ) -> str:
        """
        Render component documentation template.
        
        Args:
            context: ComponentTemplateContext with extracted component data
            template_name: Name of template file (default: component.jinja2)
            
        Returns:
            Rendered markdown string
            
        Raises:
            TemplateNotFound: If template doesn't exist
            Exception: If rendering fails
        """
        logger.info(f"Rendering component template for {context.component_name}")
        
        try:
            template = self.env.get_template(template_name)
            context_dict = self._context_to_dict(context)
            rendered = template.render(context_dict)
            
            logger.info(
                f"Successfully rendered {context.component_name}: "
                f"{len(rendered)} characters"
            )
            
            return rendered
            
        except TemplateNotFound as e:
            logger.error(f"Template not found: {template_name}")
            raise
        except Exception as e:
            logger.error(f"Error rendering component template: {e}", exc_info=True)
            raise
    
    def render_table_template(
        self,
        context: TableTemplateContext,
        template_name: str = "table.jinja2"
    ) -> str:
        """
        Render table documentation template.
        
        Args:
            context: TableTemplateContext with extracted table data
            template_name: Name of template file (default: table.jinja2)
            
        Returns:
            Rendered markdown string
            
        Raises:
            TemplateNotFound: If template doesn't exist
            Exception: If rendering fails
        """
        logger.info(f"Rendering table template for {context.table_name}")
        
        try:
            template = self.env.get_template(template_name)
            context_dict = self._context_to_dict(context)
            rendered = template.render(context_dict)
            
            logger.info(
                f"Successfully rendered {context.table_name}: "
                f"{len(rendered)} characters"
            )
            
            return rendered
            
        except TemplateNotFound as e:
            logger.error(f"Template not found: {template_name}")
            raise
        except Exception as e:
            logger.error(f"Error rendering table template: {e}", exc_info=True)
            raise
    
    def _context_to_dict(self, context: Any) -> Dict[str, Any]:
        """
        Convert dataclass context to dictionary for Jinja2.
        
        Args:
            context: ServiceTemplateContext, ComponentTemplateContext, or TableTemplateContext
            
        Returns:
            Dictionary representation of context
        """
        from dataclasses import asdict
        return asdict(context)


# ============================================================================
# CONVENIENCE FUNCTIONS FOR DIRECT USE
# ============================================================================

def render_service_template(
    context: ServiceTemplateContext,
    template_name: str = "service.jinja2"
) -> str:
    """
    Render service template (convenience function).
    
    Args:
        context: ServiceTemplateContext
        template_name: Template file name
        
    Returns:
        Rendered markdown string
    """
    renderer = TemplateRenderer()
    return renderer.render_service_template(context, template_name)


def render_component_template(
    context: ComponentTemplateContext,
    template_name: str = "component.jinja2"
) -> str:
    """
    Render component template (convenience function).
    
    Args:
        context: ComponentTemplateContext
        template_name: Template file name
        
    Returns:
        Rendered markdown string
    """
    renderer = TemplateRenderer()
    return renderer.render_component_template(context, template_name)


def render_table_template(
    context: TableTemplateContext,
    template_name: str = "table.jinja2"
) -> str:
    """
    Render table template (convenience function).
    
    Args:
        context: TableTemplateContext
        template_name: Template file name
        
    Returns:
        Rendered markdown string
    """
    renderer = TemplateRenderer()
    return renderer.render_table_template(context, template_name)


def get_available_filters() -> Dict[str, str]:
    """
    Return list of available custom filters with descriptions.
    
    Useful for debugging and template authors.
    
    Returns:
        Dictionary of filter_name: description
    """
    return {
        'yes_no': 'Convert boolean to Yes/No text',
        'required_nullable': 'Convert required/nullable flags to text',
        'title_case': 'Convert snake_case/UPPER_CASE to Title Case',
        'http_method_color': 'Get emoji indicator for HTTP method',
        'join_list': 'Join list items with separator',
        'code_block': 'Wrap text in markdown code block',
        'truncate_smart': 'Truncate text at word boundary',
        'default_if_empty': 'Return default text if value is empty',
    }
