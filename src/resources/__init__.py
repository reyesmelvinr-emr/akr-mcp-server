"""
AKR Resources Module

This module provides MCP resource handling for AKR documentation files.
Resources are organized by category: charters, templates, and guides.
"""

from .akr_resources import (
    AKRResourceManager,
    ResourceCategory,
    AKRResource,
    create_resource_manager,
)

__all__ = [
    "AKRResourceManager",
    "ResourceCategory",
    "AKRResource",
    "create_resource_manager",
]
