"""
Pytest configuration and fixtures for AKR MCP Server tests.

This module sets up the Python path to include the src/ directory
and configures pytest for the project.
"""

import sys
from pathlib import Path

# Add src directory to Python path so imports work correctly
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
