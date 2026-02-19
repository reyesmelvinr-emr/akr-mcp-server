"""
Test script for AKR MCP Server

This script tests basic server functionality without needing
the full MCP client connection.
"""

import asyncio
import sys
from pathlib import Path

from server import (
    list_resources,
    read_resource,
    list_tools,
    call_tool,
    get_resource_manager,
    logger
)
from resources import ResourceCategory
from datetime import datetime


async def test_health_check():
    """Test the health_check tool."""
    print("\n" + "="*60)
    print("Testing health_check (non-verbose)")
    print("="*60)
    
    # Set start time for uptime calculation
    server_state["start_time"] = datetime.now()
    
    result = await health_check(verbose=False)
    print(result[0].text)
    
    print("\n" + "="*60)
    print("Testing health_check (verbose)")
    print("="*60)
    
    result = await health_check(verbose=True)
    print(result[0].text)


async def test_get_server_info():
    """Test the get_server_info tool."""
    print("\n" + "="*60)
    print("Testing get_server_info")
    print("="*60)
    
    result = await get_server_info()
    print(result[0].text)


async def test_list_resources():
    """Test the list_resources handler."""
    print("\n" + "="*60)
    print("Testing list_resources")
    print("="*60)
    
    resources = await list_resources()
    print(f"\nDiscovered {len(resources)} resources:\n")
    
    # Group by category for display (convert uri to string for comparison)
    charters = [r for r in resources if "charter" in str(r.uri)]
    templates = [r for r in resources if "template" in str(r.uri)]
    guides = [r for r in resources if "guide" in str(r.uri)]
    
    print("CHARTERS:")
    for r in charters:
        print(f"  - {r.uri}")
        print(f"    Name: {r.name}")
        desc = r.description or ""
        print(f"    Description: {desc[:60]}..." if len(desc) > 60 else f"    Description: {desc}")
    
    print("\nTEMPLATES:")
    for r in templates:
        print(f"  - {r.uri}")
    
    print("\nGUIDES:")
    for r in guides:
        print(f"  - {r.uri}")
    
    return resources


async def test_list_resource_templates():
    """Test the list_resource_templates handler."""
    print("\n" + "="*60)
    print("Testing list_resource_templates")
    print("="*60)
    
    templates = await list_resource_templates()
    print(f"\n{len(templates)} URI templates available:\n")
    
    for t in templates:
        print(f"  Template: {t.uriTemplate}")
        print(f"    Name: {t.name}")
        print(f"    Description: {t.description}")
        print()


async def test_read_resource():
    """Test the read_resource handler."""
    print("\n" + "="*60)
    print("Testing read_resource")
    print("="*60)
    
    # Test reading a charter
    uri = "akr://charter/AKR_CHARTER_BACKEND.md"
    print(f"\nReading: {uri}")
    
    content = await read_resource(uri)
    print(f"  Content length: {len(content)} characters")
    print(f"  First line: {content.split(chr(10))[0]}")
    
    # Test reading a template
    uri = "akr://template/standard_service_template.md"
    print(f"\nReading: {uri}")
    
    content = await read_resource(uri)
    print(f"  Content length: {len(content)} characters")
    print(f"  First line: {content.split(chr(10))[0]}")
    
    # Test reading a guide
    uri = "akr://guide/Backend_Service_Documentation_Developer_Guide.md"
    print(f"\nReading: {uri}")
    
    content = await read_resource(uri)
    print(f"  Content length: {len(content)} characters")
    print(f"  First line: {content.split(chr(10))[0]}")
    
    # Test error handling for non-existent resource
    print("\nTesting error handling for non-existent resource...")
    try:
        await read_resource("akr://charter/NONEXISTENT.md")
        print("  ERROR: Should have raised an exception!")
    except ValueError as e:
        print("  ✓ Correctly raised ValueError for non-existent resource")


async def test_resource_manager_direct():
    """Test the resource manager directly."""
    print("\n" + "="*60)
    print("Testing AKRResourceManager directly")
    print("="*60)
    
    # Test resource counts
    counts = resource_manager.get_resource_count()
    print(f"\nResource counts:")
    print(f"  Total: {counts['total']}")
    print(f"  Charters: {counts['charters']}")
    print(f"  Templates: {counts['templates']}")
    print(f"  Guides: {counts['guides']}")
    
    # Test filtering by category
    print("\nFiltering resources by category:")
    charters = resource_manager.list_resources(category=ResourceCategory.CHARTER)
    print(f"  Charters: {len(charters)}")
    
    templates = resource_manager.list_resources(category=ResourceCategory.TEMPLATE)
    print(f"  Templates: {len(templates)}")
    
    guides = resource_manager.list_resources(category=ResourceCategory.GUIDE)
    print(f"  Guides: {len(guides)}")
    
    # Test get_resource
    print("\nTesting get_resource:")
    resource = resource_manager.get_resource("akr://charter/AKR_CHARTER.md")
    if resource:
        print(f"  Got resource: {resource.name}")
        print(f"  Category: {resource.category.value}")
        print(f"  File size: {resource.metadata.get('size_bytes', 'N/A')} bytes")
    else:
        print("  ERROR: Resource not found!")


async def test_list_templates_tool():
    """Test the list_templates tool."""
    print("\n" + "="*60)
    print("Testing list_templates tool (all templates)")
    print("="*60)
    
    result = await handle_list_templates("all", verbose=False)
    # Just show first part to avoid too much output
    text = result[0].text
    print(f"\n{text[:1000]}...")
    print(f"\n  [Total output: {len(text)} characters]")
    
    print("\n" + "="*60)
    print("Testing list_templates tool (backend only)")
    print("="*60)
    
    result = await handle_list_templates("backend", verbose=False)
    text = result[0].text
    lines = text.split('\n')
    # Count templates
    template_count = text.count("###")
    print(f"\n  Found {template_count} backend templates")


async def test_suggest_template_tool():
    """Test the suggest_template tool."""
    print("\n" + "="*60)
    print("Testing suggest_template tool")
    print("="*60)
    
    test_files = [
        ("src/services/UserService.cs", "standard", "Backend"),
        ("components/Button.tsx", "standard", "UI"),
        ("database/Users.sql", "standard", "Database"),
        ("src/utils/Helper.py", "lean", "Backend"),
    ]
    
    for file_path, complexity, expected_type in test_files:
        print(f"\n  File: {file_path}")
        result = await handle_suggest_template(file_path, complexity)
        text = result[0].text
        
        # Extract recommended template name
        if "### " in text:
            template_name = text.split("### ")[1].split("\n")[0]
            print(f"  Suggested: {template_name}")
            
            # Check if correct type
            if expected_type.lower() in text.lower():
                print(f"  ✓ Correctly identified as {expected_type}")
            else:
                print(f"  ? Expected {expected_type} type")


async def main():
    """Run all tests."""
    print("\n" + "#"*60)
    print("# AKR MCP Server - Test Suite")
    print("#"*60)
    
    print(f"\nServer: {config['server']['name']}")
    print(f"Version: {config['server'].get('version', '0.1.0')}")
    
    # Run tests
    await test_health_check()
    await test_get_server_info()
    await test_list_resources()
    await test_list_resource_templates()
    await test_read_resource()
    await test_resource_manager_direct()
    await test_list_templates_tool()
    await test_suggest_template_tool()
    
    print("\n" + "#"*60)
    print("# All tests completed!")
    print("#"*60)


if __name__ == "__main__":
    asyncio.run(main())
