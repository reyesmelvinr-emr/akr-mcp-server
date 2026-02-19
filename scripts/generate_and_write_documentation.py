#!/usr/bin/env python3
"""
AKR Unified Documentation Generation Script

Combines scaffolding + generation + writing in a single operation.
Auto-detects project type and generates complete template-based documentation.

Usage:
    python generate_and_write_documentation.py --module-name "Enrollment" --source-files "Domain/Services/IEnrollmentService.cs,Controllers/EnrollmentsController.cs"
    python generate_and_write_documentation.py --module-name "Button" --source-files "src/components/Button.tsx"
    python generate_and_write_documentation.py --module-name "Courses" --source-files "tables/Courses.sql" --component-type "table"
"""

import argparse
import asyncio
import json
import sys
import io
from pathlib import Path
from typing import List, Optional

# Configure stdout to use UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from server import _detect_project_type, _replace_placeholders
from resources import create_resource_manager
from tools.write_operations import write_documentation_async
from tools.operation_metrics import OperationMetrics
from tools.progress_tracker import ProgressTracker
from tools.code_analyzer import CodeAnalyzer


async def generate_and_write_documentation(
    component_name: str,
    source_files: List[str],
    workspace_root: Path,
    template: Optional[str] = None,
    output_path: Optional[str] = None,
    component_type: Optional[str] = None,
    overwrite: bool = False
) -> dict:
    """
    Main unified generation + writing logic
    
    Returns: Result dictionary with success status and messages
    """
    # Auto-detect project type if not specified
    if not component_type:
        project_type = _detect_project_type(workspace_root)
        if project_type == "unknown":
            return {
                "success": False,
                "error": "Could not detect project type",
                "guidance": (
                    "Please either:\n"
                    "   1. Add 'domain' field to .akr-config.json (backend/ui/database), or\n"
                    "   2. Use --component-type flag to specify manually"
                )
            }
        
        print(f"✅ Detected project type: {project_type}")
        
        # Map project type to component type
        type_map = {
            "backend": "service",
            "ui": "ui_component",
            "database": "table"
        }
        component_type = type_map.get(project_type, "service")
    else:
        # Derive project type from component type
        if component_type in ["service", "api"]:
            project_type = "backend"
        elif component_type in ["ui_component", "component"]:
            project_type = "ui"
        elif component_type == "table":
            project_type = "database"
        else:
            project_type = "backend"  # default
    
    print(f"📦 Component type: {component_type}")
    
    # Validate source files exist
    print(f"🔍 Validating source files...")
    if not source_files:
        return {
            "success": False,
            "error": "No source files provided",
            "guidance": "Provide at least one source file using --source-files flag"
        }
    
    missing_files = []
    wildcard_files = []
    valid_files = []
    
    for file_path in source_files:
        # Check for wildcards
        if '*' in file_path or '?' in file_path:
            wildcard_files.append(file_path)
            continue
        
        # Check if file exists
        full_path = workspace_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        elif not full_path.is_file():
            missing_files.append(f"{file_path} (is a directory, not a file)")
        else:
            valid_files.append(file_path)
            print(f"   ✅ {file_path}")
    
    # Report issues
    if wildcard_files:
        print()
        print(f"⚠️  Warning: Wildcard patterns are not supported:")
        for wf in wildcard_files:
            print(f"   ❌ {wf}")
        print()
        print("💡 Tip: Specify exact file paths instead of wildcards")
    
    if missing_files:
        print()
        return {
            "success": False,
            "error": f"Source file validation failed: {len(missing_files)} file(s) not found",
            "missingFiles": missing_files,
            "validFiles": valid_files,
            "guidance": (
                "Source files must exist and be relative to workspace root.\n\n"
                "Common issues:\n"
                "  • File path typo (check spelling and capitalization)\n"
                "  • Wrong folder structure (verify file location in workspace)\n"
                "  • Multiple classes in one file (e.g., CourseService defined in ICourseService.cs)\n"
                "  • Wildcard patterns not supported (use exact file paths)\n\n"
                f"Workspace root: {workspace_root}\n\n"
                "Example correct paths:\n"
                "  • Domain/Services/ICourseService.cs\n"
                "  • Controllers/CoursesController.cs\n"
                "  • Infrastructure/Persistence/EfCourseRepository.cs"
            )
        }
    
    if not valid_files and wildcard_files:
        return {
            "success": False,
            "error": "No valid source files (only wildcards provided)",
            "guidance": "Wildcard patterns are not supported. Please specify exact file paths."
        }
    
    print(f"✅ All {len(valid_files)} source file(s) validated")
    print()
    
    # Auto-select template if not specified
    if not template:
        template_map = {
            "backend": "lean_baseline_service_template.md",
            "ui": "ui_component_template.md",
            "database": "table_doc_template.md"
        }
        template = template_map.get(project_type, "lean_baseline_service_template.md")
    
    print(f"📄 Using template: {template}")
    
    # Validate template exists and get content
    try:
        rm = create_resource_manager()
        template_content = rm.get_resource_content("template", template)
        if not template_content:
            available_templates = [t.filename for t in rm.list_templates()]
            return {
                "success": False,
                "error": f"Template '{template}' not found in akr_content/templates/",
                "availableTemplates": available_templates,
                "hint": "Use one of the available templates or check that the template file exists"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to validate template: {str(e)}",
            "hint": "Check that akr_content/templates/ directory exists and contains templates"
        }
    
    # NEW: Code analysis and extraction
    print(f"🔍 Analyzing source files and extracting code structure...")
    
    # Load code_analysis config
    config_file = workspace_root / ".akr-config.json"
    code_analysis_config = {}
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                full_config = json.load(f)
                code_analysis_config = full_config.get('code_analysis', {})
        except Exception as e:
            print(f"⚠️  Warning: Could not load code_analysis config: {e}")
    
    # Fallback to global config.json if workspace config doesn't have code_analysis
    if not code_analysis_config:
        global_config_file = Path(__file__).parent.parent / "config.json"
        if global_config_file.exists():
            try:
                with open(global_config_file, 'r', encoding='utf-8') as f:
                    full_config = json.load(f)
                    code_analysis_config = full_config.get('code_analysis', {})
            except Exception as e:
                print(f"⚠️  Warning: Could not load global code_analysis config: {e}")
    
    # Perform code analysis if enabled
    populated_content = template_content
    if code_analysis_config.get('enabled', True):
        try:
            analyzer = CodeAnalyzer(config=code_analysis_config)
            
            # Convert source files to absolute paths for analyzer
            abs_source_files = [str(workspace_root / f) for f in valid_files]
            
            # Analyze files
            extracted_data_list = analyzer.analyze_files(abs_source_files, project_type)
            
            if extracted_data_list:
                print(f"✅ Extracted data from {len(extracted_data_list)} file(s)")
                
                # Populate template with extracted data
                populated_content = analyzer.populate_template(template_content, extracted_data_list)
                print(f"✅ Populated template with extracted code structure")
            else:
                print(f"⚠️  No data extracted - will use empty template")
        except Exception as e:
            print(f"⚠️  Code analysis failed: {e}")
            print(f"   Continuing with un-populated template...")
    else:
        print(f"ℹ️  Code analysis disabled in config")
    
    # Replace placeholders in template
    print(f"🔄 Replacing placeholders for '{component_name}'...")
    scaffolded_content = _replace_placeholders(
        populated_content,
        component_name,
        project_type,
        source_files
    )
    
    # Auto-determine output path if not specified
    if not output_path:
        output_path_map = {
            "backend": "docs/services/",
            "ui": "docs/components/",
            "database": "docs/tables/"
        }
        naming_suffix_map = {
            "backend": "_doc.md",
            "ui": "_doc.md",
            "database": ".md"
        }
        base_path = output_path_map.get(project_type, "docs/services/")
        naming_suffix = naming_suffix_map.get(project_type, "_doc.md")
        output_path = f"{base_path}{component_name}{naming_suffix}"
    
    print(f"📝 Output path: {output_path}")
    
    # Prepare for writing
    repo_path = str(workspace_root)
    
    # Load workspace config directly as dict (for enforcement settings)
    config_dict = {}
    config_file = workspace_root / ".akr-config.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
        except Exception as e:
            print(f"⚠️  Warning: Could not load .akr-config.json: {e}")
            config_dict = {}
    
    # Create operation metrics and progress tracker
    metrics = OperationMetrics(template_name=template)
    tracker = ProgressTracker(
        progress_token=None,
        send_progress=None,
        estimate_remaining=metrics.estimate_remaining_ms
    )
    
    # Use first source file as primary source_file for metadata
    primary_source_file = source_files[0] if source_files else f"src/{component_name}.cs"
    
    print(f"✍️  Writing documentation with enforcement validation...")
    
    # Write documentation with enforcement
    try:
        result = await write_documentation_async(
            repo_path=repo_path,
            content=scaffolded_content,
            source_file=primary_source_file,
            doc_path=output_path,
            template=template,
            component_type=component_type,
            overwrite=overwrite,
            config=config_dict,  # Pass loaded config from workspace
            telemetry_logger=None,
            progress_tracker=tracker,
            operation_metrics=metrics,
            workflow_tracker=None,
            duplicate_detector=None,
            force_workflow_bypass=True,  # This is unified workflow, not 2-step
            resource_manager=rm,
            session_cache=None,
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to write documentation: {str(e)}",
            "guidance": "Check that the workspace has proper .akr-config.json and permissions"
        }


def main():
    parser = argparse.ArgumentParser(
        description="Generate and write AKR documentation in one step (unified scaffold + generate + write)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Backend service with auto-detection
  python generate_and_write_documentation.py --module-name "Enrollment" \\
    --source-files "Domain/Services/IEnrollmentService.cs,Controllers/EnrollmentsController.cs"
  
  # UI component
  python generate_and_write_documentation.py --module-name "Button" \\
    --source-files "src/components/Button.tsx" \\
    --component-type "ui_component"
  
  # Database table
  python generate_and_write_documentation.py --module-name "Courses" \\
    --source-files "tables/Courses.sql" \\
    --component-type "table"
  
  # Override template and output path
  python generate_and_write_documentation.py --module-name "AuthService" \\
    --source-files "Domain/Services/AuthService.cs" \\
    --template "standard_service_template.md" \\
    --output-path "docs/auth/AuthService_doc.md"
        """
    )
    
    parser.add_argument(
        "--module-name",
        required=True,
        help="Module name (e.g., Enrollment, Button, Courses)"
    )
    
    parser.add_argument(
        "--source-files",
        required=True,
        help="Comma-separated list of source files to document"
    )
    
    parser.add_argument(
        "--component-type",
        choices=["service", "ui_component", "table", "api"],
        help="Component type (optional, auto-detected from project structure)"
    )
    
    parser.add_argument(
        "--template",
        help="Template file to use (optional, auto-selected based on component type)"
    )
    
    parser.add_argument(
        "--output-path",
        help="Output documentation path (optional, auto-determined based on project type)"
    )
    
    parser.add_argument(
        "--workspace-root",
        type=Path,
        help="Workspace root directory (optional, defaults to current directory)"
    )
    
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing documentation file if it exists"
    )
    
    args = parser.parse_args()
    
    # Parse source files
    source_files = [f.strip() for f in args.source_files.split(",") if f.strip()]
    
    # Determine workspace root
    workspace_root = args.workspace_root if args.workspace_root else Path.cwd()
    if not workspace_root.exists() or not workspace_root.is_dir():
        print(f"❌ Error: Workspace root does not exist or is not a directory: {workspace_root}")
        sys.exit(1)
    
    print(f"🚀 AKR Unified Documentation Generation")
    print(f"   Workspace: {workspace_root}")
    print(f"   Component: {args.module_name}")
    print(f"   Source files: {len(source_files)} file(s)")
    print()
    
    # Run async generation and writing
    result = asyncio.run(generate_and_write_documentation(
        component_name=args.module_name,
        source_files=source_files,
        workspace_root=workspace_root,
        template=args.template,
        output_path=args.output_path,
        component_type=args.component_type,
        overwrite=args.overwrite
    ))
    
    # Display results
    print()
    if result.get("success"):
        print("✅ SUCCESS!")
        print(f"   {result.get('message', 'Documentation generated and written')}")
        print()
        
        if result.get("fixesApplied"):
            print(f"   ⚙️  Applied {result['fixesApplied']} automatic fixes during enforcement")
        
        if result.get("violations"):
            print(f"   ⚠️  {len(result['violations'])} validation issues found:")
            for v in result["violations"][:3]:  # Show first 3
                print(f"      - {v.get('message', 'Unknown issue')}")
            if len(result["violations"]) > 3:
                print(f"      ... and {len(result['violations']) - 3} more")
        
        print()
        print("📝 Next steps:")
        print("   1. Review the generated documentation file")
        print("   2. Replace ❓ placeholders with actual content (Business Rules, What & Why, etc.)")
        print("   3. Run 'AKR: Validate Documentation (file)' to check compliance")
        print("   4. Commit to git when ready")
        
        sys.exit(0)
    else:
        print("❌ FAILED!")
        print(f"   {result.get('error', 'Unknown error occurred')}")
        
        # Print enforcement violations if available
        if result.get("violations"):
            print()
            print(f"⚠️  Enforcement violations ({len(result['violations'])} found):")
            for i, v in enumerate(result["violations"][:5], 1):
                if isinstance(v, dict):
                    v_type = v.get('type', 'unknown')
                    v_msg = v.get('message', 'Unknown violation')
                    v_line = v.get('line', '?')
                    print(f"   {i}. [{v_type}] Line {v_line}: {v_msg}")
                else:
                    print(f"   {i}. {v}")
            if len(result["violations"]) > 5:
                print(f"   ... and {len(result['violations']) - 5} more violations")
        
        if result.get("summary"):
            print()
            print(f"Summary: {result['summary']}")
        
        if result.get("guidance"):
            print()
            print("💡 Guidance:")
            guidance = result["guidance"]
            if isinstance(guidance, dict):
                for key, value in guidance.items():
                    print(f"   {key}:")
                    if isinstance(value, list):
                        for item in value:
                            print(f"      - {item}")
                    else:
                        print(f"      {value}")
            elif isinstance(guidance, str):
                for line in guidance.split("\n"):
                    print(f"   {line}")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
