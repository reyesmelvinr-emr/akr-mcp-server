#!/usr/bin/env python3
"""
AKR Documentation Scaffolding Script

Auto-detects project type (backend/ui/database) and scaffolds documentation
files with appropriate templates and conventions.

Usage:
    python scaffold_documentation.py --module-name "Enrollment" [--source-files "file1.cs,file2.cs"]
    python scaffold_documentation.py --module-name "Button" --template "ui_component_template.md"
    python scaffold_documentation.py --module-name "Courses" --output-path "docs/tables/"
"""

import argparse
import json
import sys
import io
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

# Configure stdout to use UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class ProjectType:
    """Project type constants"""
    BACKEND = "backend"
    UI = "ui"
    DATABASE = "database"
    UNKNOWN = "unknown"


class TemplateConfig:
    """Template configuration for each project type"""
    
    CONFIGS = {
        ProjectType.BACKEND: {
            "default_template": "lean_baseline_service_template.md",
            "output_path": "docs/services/",
            "placeholder": "[SERVICE_NAME]",
            "file_extensions": [".cs", ".java", ".py", ".go"],
            "naming_suffix": "_doc.md",
            "examples": "Examples: EnrollmentService, CourseService, UserService"
        },
        ProjectType.UI: {
            "default_template": "ui_component_template.md",
            "output_path": "docs/components/",
            "placeholder": "[COMPONENT_NAME]",
            "file_extensions": [".tsx", ".ts", ".jsx", ".js", ".vue"],
            "naming_suffix": "_doc.md",
            "examples": "Examples: Button, CourseCard, useAuth"
        },
        ProjectType.DATABASE: {
            "default_template": "table_doc_template.md",
            "output_path": "docs/tables/",
            "placeholder": "[TABLE_NAME]",
            "file_extensions": [".sql"],
            "naming_suffix": ".md",
            "examples": "Examples: Enrollments, Courses, Users"
        }
    }


def find_workspace_root() -> Path:
    """Find the workspace root by looking for .akr-config.json or git root"""
    current = Path.cwd()
    
    # Check current directory and parents for markers
    for parent in [current] + list(current.parents):
        if (parent / ".akr-config.json").exists():
            return parent
        if (parent / ".git").exists():
            return parent
    
    return current


def detect_project_type(workspace_root: Path) -> str:
    """
    Auto-detect project type by checking .akr-config.json or file patterns
    
    Returns: ProjectType constant (backend/ui/database/unknown)
    """
    # Strategy 1: Read .akr-config.json
    config_path = workspace_root / ".akr-config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                # Check for explicit domain field (root level)
                if "domain" in config:
                    domain = config["domain"].lower()
                    if domain in [ProjectType.BACKEND, ProjectType.UI, ProjectType.DATABASE]:
                        return domain
                
                # Check for projectType field (root level)
                if "projectType" in config:
                    proj_type = config["projectType"].lower()
                    if proj_type in [ProjectType.BACKEND, ProjectType.UI, ProjectType.DATABASE]:
                        return proj_type
                
                # Check for nested project.type field
                if "project" in config and isinstance(config["project"], dict):
                    if "type" in config["project"]:
                        proj_type = config["project"]["type"].lower()
                        if proj_type in [ProjectType.BACKEND, ProjectType.UI, ProjectType.DATABASE]:
                            return proj_type
                    
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️  Warning: Could not read .akr-config.json: {e}")
    
    # Strategy 2: File pattern detection
    print("ℹ️  No domain specified in .akr-config.json, detecting from file patterns...")
    
    # Check for backend indicators
    if list(workspace_root.rglob("*.csproj")) or list(workspace_root.rglob("*.sln")):
        return ProjectType.BACKEND
    
    # Check for UI indicators
    package_json = workspace_root / "package.json"
    if package_json.exists():
        # Check if it's a UI project (has UI-like structure)
        # Require components or pages directory (not just public, which backend APIs might have)
        if (workspace_root / "src" / "components").exists() or \
           (workspace_root / "src" / "pages").exists():
            return ProjectType.UI
        # Otherwise might be backend Node.js, but we'll default to backend
        return ProjectType.BACKEND
    
    # Check for database indicators
    if list(workspace_root.rglob("*.sqlproj")):
        return ProjectType.DATABASE
    
    return ProjectType.UNKNOWN


def find_template_file(template_name: str) -> Optional[Path]:
    """Find template file in akr_content/templates/ directory"""
    searched_paths = []
    
    # Start from current location and search for templates directory
    current = Path(__file__).parent.parent
    template_path = current / "akr_content" / "templates" / template_name
    searched_paths.append(template_path)
    
    if template_path.exists():
        return template_path
    
    # Try relative to workspace root
    workspace_root = find_workspace_root()
    template_path = workspace_root / "akr_content" / "templates" / template_name
    searched_paths.append(template_path)
    if template_path.exists():
        return template_path
    
    # Try parent directories (in case we're in a project workspace, look for MCP server)
    for parent in workspace_root.parents:
        template_path = parent / "akr-mcp-server" / "akr_content" / "templates" / template_name
        searched_paths.append(template_path)
        if template_path.exists():
            return template_path
    
    # Store searched paths for error reporting
    find_template_file.searched_paths = searched_paths
    return None


def replace_placeholders(content: str, module_name: str, project_type: str, source_files: List[str]) -> str:
    """Replace template placeholders with actual values"""
    config = TemplateConfig.CONFIGS.get(project_type, {})
    placeholder = config.get("placeholder", "[SERVICE_NAME]")
    
    # Replace common placeholders
    content = content.replace(placeholder, module_name)
    content = content.replace("[SERVICE_NAME]", module_name)
    content = content.replace("[COMPONENT_NAME]", module_name)
    content = content.replace("[TABLE_NAME]", module_name)
    content = content.replace("[FEATURE_NAME]", module_name)
    
    # Replace placeholders with spaces
    content = content.replace("[Component Name]", module_name)
    content = content.replace("[Service Name]", module_name)
    content = content.replace("[Table Name]", module_name)
    
    # Replace camelCase/PascalCase placeholders
    content = content.replace("[ComponentName]", module_name)
    content = content.replace("[ServiceName]", module_name)
    content = content.replace("[TableName]", module_name)
    
    # Replace date placeholders
    today = datetime.now().strftime("%Y-%m-%d")
    content = content.replace("[YYYY-MM-DD]", today)
    content = content.replace("YYYY-MM-DD", today)
    
    # Replace domain placeholder with project type
    domain_map = {
        ProjectType.BACKEND: "Backend",
        ProjectType.UI: "UI",
        ProjectType.DATABASE: "Database"
    }
    content = content.replace("[DOMAIN]", domain_map.get(project_type, "Unknown"))
    
    # Add source files comment if provided
    if source_files:
        files_list = "\n".join(f"- {f}" for f in source_files)
        source_comment = f"\n<!-- Source files used for documentation:\n{files_list}\n-->\n"
        # Insert after front matter if it exists
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = f"---{parts[1]}---{source_comment}{parts[2]}"
        else:
            # No front matter, add comment at the top
            content = source_comment + content
    
    return content


def scaffold_documentation(
    module_name: str,
    template_name: Optional[str] = None,
    output_path: Optional[str] = None,
    source_files: Optional[List[str]] = None,
    workspace_root: Optional[Path] = None
) -> Tuple[bool, str]:
    """
    Main scaffolding logic
    
    Returns: (success: bool, message: str)
    """
    if workspace_root is None:
        workspace_root = find_workspace_root()
    else:
        # Validate provided workspace_root exists
        if not workspace_root.exists():
            return False, f"❌ Workspace root does not exist: {workspace_root}"
        if not workspace_root.is_dir():
            return False, f"❌ Workspace root is not a directory: {workspace_root}"
    
    # Detect project type
    project_type = detect_project_type(workspace_root)
    
    if project_type == ProjectType.UNKNOWN:
        return False, (
            "❌ Could not detect project type. Please:\n"
            "   1. Add 'domain' field to .akr-config.json (backend/ui/database), or\n"
            "   2. Use --template and --output-path flags to specify manually"
        )
    
    print(f"✅ Detected project type: {project_type}")
    
    # Get configuration for project type
    config = TemplateConfig.CONFIGS[project_type]
    
    # Use provided values or defaults (ensure we have non-None values)
    template_name = template_name if template_name is not None else config["default_template"]
    output_path = output_path if output_path is not None else config["output_path"]
    
    print(f"📄 Using template: {template_name}")
    
    # Find template file
    template_file = find_template_file(template_name)
    if template_file is None:
        error_msg = f"❌ Template not found: {template_name}"
        if hasattr(find_template_file, 'searched_paths'):
            searched = "\n   ".join(str(p) for p in find_template_file.searched_paths[:3])
            error_msg += f"\n   Searched in:\n   {searched}"
        return False, error_msg
    
    # Read template content
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except Exception as e:
        return False, f"❌ Error reading template: {e}"
    
    # Replace placeholders
    scaffolded_content = replace_placeholders(
        template_content,
        module_name,
        project_type,
        source_files or []
    )
    
    # Determine output file path
    output_dir = workspace_root / output_path
    output_dir.mkdir(parents=True, exist_ok=True)
    
    naming_suffix = config["naming_suffix"]
    output_file = output_dir / f"{module_name}{naming_suffix}"
    
    # Check if file already exists
    if output_file.exists():
        return False, f"⚠️  File already exists: {output_file}\n   Use a different module name or delete the existing file first."
    
    # Write scaffolded file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(scaffolded_content)
    except Exception as e:
        return False, f"❌ Error writing file: {e}"
    
    # Try to get relative path, fall back to absolute if not related
    try:
        display_path = output_file.relative_to(workspace_root)
    except ValueError:
        display_path = output_file
    
    return True, f"✅ Scaffolded documentation created: {display_path}"


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold AKR documentation with auto-detected project type",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect everything (backend project)
  python scaffold_documentation.py --module-name "Enrollment"
  
  # With source files
  python scaffold_documentation.py --module-name "Enrollment" \\
    --source-files "Domain/Services/IEnrollmentService.cs,Controllers/EnrollmentsController.cs"
  
  # Override template
  python scaffold_documentation.py --module-name "CourseService" \\
    --template "standard_service_template.md"
  
  # Override output path
  python scaffold_documentation.py --module-name "AdminService" \\
    --output-path "docs/admin/"
        """
    )
    
    parser.add_argument(
        "--module-name",
        required=True,
        help="Module name (e.g., Enrollment, Button, Courses)"
    )
    
    parser.add_argument(
        "--template",
        help="Template file to use (optional, auto-detected from project type)"
    )
    
    parser.add_argument(
        "--output-path",
        help="Output directory path (optional, auto-detected from project type)"
    )
    
    parser.add_argument(
        "--source-files",
        help="Comma-separated list of source files to document (optional)"
    )
    
    parser.add_argument(
        "--workspace-root",
        type=Path,
        help="Workspace root directory (optional, auto-detected)"
    )
    
    args = parser.parse_args()
    
    # Parse source files
    source_files = None
    if args.source_files:
        source_files = [f.strip() for f in args.source_files.split(",") if f.strip()]
    
    # Run scaffolding
    success, message = scaffold_documentation(
        module_name=args.module_name,
        template_name=args.template,
        output_path=args.output_path,
        source_files=source_files,
        workspace_root=args.workspace_root
    )
    
    print(f"\n{message}")
    
    if success:
        print("\n📝 Next steps:")
        print("   1. Review the scaffolded documentation file")
        print("   2. Open GitHub Copilot Chat and use a prompt like:")
        print(f'      "Generate AKR documentation for module \\"{args.module_name}\\" using the scaffolded file as a template."')
        print("   3. Enhance with business context (WHY fields)")
        print("   4. Run AKR validation tasks before committing")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
