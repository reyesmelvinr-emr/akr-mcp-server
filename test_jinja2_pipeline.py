#!/usr/bin/env python3
"""Test script for extraction and Jinja2 rendering pipeline."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tools.extractors.csharp_extractor import CSharpExtractor
from tools.code_analyzer import CodeAnalyzer
from tools.context_builder import build_service_context
from tools.template_renderer import TemplateRenderer

def main():
    """Test the extraction and rendering pipeline."""
    
    print("=" * 70)
    print("EXTRACTION & JINJA2 RENDERING PIPELINE TEST")
    print("=" * 70)
    
    # Test file paths
    training_workspace = Path(
        r"c:\Users\E1481541\OneDrive - Emerson\Documents\CDS - Team Hawkeye"
        r"\Training Test Workspace\training-tracker-backend"
    )
    
    controller_file = training_workspace / "TrainingTracker.Api" / "Controllers" / "CoursesController.cs"
    service_file = training_workspace / "TrainingTracker.Api" / "Domain" / "Services" / "ICourseService.cs"
    
    if not controller_file.exists():
        print(f"ERROR: Controller file not found: {controller_file}")
        return
    
    # Step 1: Extract data from controller
    print(f"\n[1] Extracting from {controller_file.name}...")
    extractor = CSharpExtractor()
    extracted_data = extractor.extract(controller_file)
    
    print(f"    ✓ Routes: {len(extracted_data.routes)}")
    for route in extracted_data.routes:
        print(f"      - {route.method} {route.path}")
    
    print(f"    ✓ Methods: {len(extracted_data.methods)}")
    print(f"    ✓ Dependencies: {len(extracted_data.dependencies)}")
    for dep in extracted_data.dependencies:
        print(f"      - {dep.name}: {dep.type}")
    
    print(f"    ✓ Validation rules: {len(extracted_data.validations)}")
    print(f"    ✓ Business rules: {len(extracted_data.business_rules)}")
    print(f"    ✓ Data operations: {len(extracted_data.data_operations)}")
    
    if extracted_data.extraction_errors:
        print(f"    ⚠️  Extraction errors:")
        for error in extracted_data.extraction_errors:
            print(f"       - {error}")
    
    # Step 2: Build template context
    print(f"\n[2] Building template context...")
    context = build_service_context(
        service_name="CourseService",
        extracted_data_list=[extracted_data],
        namespace="TrainingTracker.Api.Domain.Services",
        domain="Backend"
    )
    
    print(f"    ✓ Service name: {context.service_name}")
    print(f"    ✓ Endpoints: {len(context.endpoints)}")
    print(f"    ✓ Dependencies: {len(context.dependencies)}")
    print(f"    ✓ Validation rules: {len(context.validation_rules)}")
    print(f"    ✓ Business rules: {len(context.business_rules)}")
    print(f"    ✓ Data reads: {len(context.data_reads)}")
    print(f"    ✓ Data writes: {len(context.data_writes)}")
    
    # Step 3: Render template
    print(f"\n[3] Rendering Jinja2 template...")
    renderer = TemplateRenderer()
    try:
        rendered = renderer.render_service_template(
            context, 
            template_name="lean_baseline_service_template.jinja2"
        )
        
        print(f"    ✓ Template rendered successfully")
        print(f"    ✓ Output size: {len(rendered)} characters")
        
        # Count sections populated
        populated = 0
        if context.endpoints:
            populated += 1
        if context.dependencies:
            populated += 1
        if context.validation_rules:
            populated += 1
        if context.business_rules:
            populated += 1
        
        print(f"    ✓ Populated sections: {populated}/4")
        
        # Write output for inspection
        output_file = Path(__file__).parent / "test_output.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(rendered)
        print(f"    ✓ Output written to: {output_file}")
        
    except Exception as e:
        print(f"    ✗ Rendering failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE ✓")
    print("=" * 70)

if __name__ == '__main__':
    main()
