#!/usr/bin/env python3
"""
Verification script for AKR global task configuration.

This script checks:
1. AKR_MCP_SERVER_PATH environment variable is set
2. Path exists and contains required scripts
3. VS Code user settings.json contains AKR tasks
4. Task definitions are valid and can be resolved

Run this script to troubleshoot AKR task availability issues.
"""

import json
import os
import platform
from pathlib import Path
from typing import List, Tuple, Dict, Any


class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{Colors.RESET}\n")


def print_success(text: str):
    """Print a success message."""
    print(f"{Colors.GREEN}✓{Colors.RESET} {text}")


def print_warning(text: str):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")


def print_error(text: str):
    """Print an error message."""
    print(f"{Colors.RED}✗{Colors.RESET} {text}")


def print_info(text: str, indent: int = 2):
    """Print an info message."""
    print(f"{' ' * indent}→ {text}")


def get_vscode_user_settings_path() -> Path:
    """Get the path to VS Code user settings.json based on OS."""
    system = platform.system()
    
    if system == "Windows":
        appdata = os.getenv("APPDATA")
        if not appdata:
            raise EnvironmentError("APPDATA environment variable not set")
        return Path(appdata) / "Code" / "User" / "settings.json"
    
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Code" / "User" / "settings.json"
    
    elif system == "Linux":
        config_home = os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        return Path(config_home) / "Code" / "User" / "settings.json"
    
    else:
        raise OSError(f"Unsupported operating system: {system}")


def check_environment_variable() -> Tuple[bool, str]:
    """Check if AKR_MCP_SERVER_PATH environment variable is set."""
    akr_path = os.getenv("AKR_MCP_SERVER_PATH")
    
    if akr_path:
        return True, akr_path
    else:
        return False, ""


def verify_akr_installation(path: str) -> Tuple[bool, List[str]]:
    """Verify the AKR installation at the given path."""
    issues = []
    akr_dir = Path(path)
    
    if not akr_dir.exists():
        issues.append(f"Path does not exist: {path}")
        return False, issues
    
    if not akr_dir.is_dir():
        issues.append(f"Path is not a directory: {path}")
        return False, issues
    
    # Check for required directories
    required_dirs = ["scripts", "src", "templates"]
    for dir_name in required_dirs:
        dir_path = akr_dir / dir_name
        if not dir_path.exists():
            issues.append(f"Missing required directory: {dir_name}")
    
    # Check for required scripts
    required_scripts = [
        "scripts/generate_and_write_documentation.py",
        "scripts/validation/validate_documentation.py",
        "scripts/validation/validate_traceability.py"
    ]
    
    for script in required_scripts:
        script_path = akr_dir / script
        if not script_path.exists():
            issues.append(f"Missing required script: {script}")
    
    return len(issues) == 0, issues


def check_vscode_settings() -> Tuple[bool, Dict[str, Any]]:
    """Check VS Code user settings for AKR tasks."""
    try:
        settings_path = get_vscode_user_settings_path()
        
        if not settings_path.exists():
            return False, {
                "error": "settings.json not found",
                "path": str(settings_path)
            }
        
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        tasks = settings.get("tasks.tasks", [])
        akr_tasks = [t for t in tasks if t.get("label", "").startswith("AKR:")]
        
        return True, {
            "path": str(settings_path),
            "total_tasks": len(tasks),
            "akr_tasks": len(akr_tasks),
            "task_labels": [t.get("label") for t in akr_tasks]
        }
    
    except json.JSONDecodeError as e:
        return False, {
            "error": f"Invalid JSON in settings.json: {e}",
            "path": str(settings_path)
        }
    
    except Exception as e:
        return False, {
            "error": str(e)
        }


def verify_task_definitions(settings_data: Dict[str, Any], akr_path: str) -> Tuple[bool, List[str]]:
    """Verify that task definitions reference valid script paths."""
    issues = []
    
    try:
        settings_path = Path(settings_data.get("path", ""))
        if not settings_path.exists():
            return False, ["Settings file not found"]
        
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        tasks = settings.get("tasks.tasks", [])
        akr_tasks = [t for t in tasks if t.get("label", "").startswith("AKR:")]
        
        akr_dir = Path(akr_path)
        
        for task in akr_tasks:
            label = task.get("label", "Unknown")
            args = task.get("args", [])
            
            # Find the script path (first arg should be the script)
            if args:
                script_ref = args[0]
                
                # Check if it uses the environment variable
                if "${env:AKR_MCP_SERVER_PATH}" not in script_ref:
                    issues.append(f"{label}: Does not use environment variable (uses: {script_ref})")
                    continue
                
                # Replace the variable and check if file exists
                script_path_str = script_ref.replace("${env:AKR_MCP_SERVER_PATH}", akr_path)
                script_path = Path(script_path_str)
                
                if not script_path.exists():
                    issues.append(f"{label}: Script not found: {script_path}")
    
    except Exception as e:
        issues.append(f"Error verifying task definitions: {e}")
    
    return len(issues) == 0, issues


def check_python_environment(akr_path: str) -> Tuple[bool, str]:
    """Check if Python virtual environment exists and is accessible."""
    akr_dir = Path(akr_path)
    venv_dir = akr_dir / "venv"
    
    if not venv_dir.exists():
        return False, "Virtual environment not found (venv/ directory)"
    
    # Check for Python executable
    if platform.system() == "Windows":
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        python_exe = venv_dir / "bin" / "python"
    
    if not python_exe.exists():
        return False, "Python executable not found in virtual environment"
    
    return True, str(python_exe)


def main():
    """Main verification function."""
    print_header("AKR Global Tasks - Verification Report")
    
    all_checks_passed = True
    
    # Check 1: Environment Variable
    print(f"{Colors.BOLD}Check 1: Environment Variable{Colors.RESET}")
    env_ok, akr_path = check_environment_variable()
    
    if env_ok:
        print_success(f"AKR_MCP_SERVER_PATH is set")
        print_info(f"Value: {akr_path}")
    else:
        print_error("AKR_MCP_SERVER_PATH is not set")
        print_info("Run: python scripts/setup_global_tasks.py")
        
        if platform.system() == "Windows":
            print_info("Or manually: setx AKR_MCP_SERVER_PATH \"C:\\path\\to\\akr-mcp-server\"")
        else:
            print_info("Or add to shell profile: export AKR_MCP_SERVER_PATH=\"/path/to/akr-mcp-server\"")
        
        all_checks_passed = False
        akr_path = ""  # Set empty for remaining checks
    
    # Check 2: AKR Installation
    print(f"\n{Colors.BOLD}Check 2: AKR Installation{Colors.RESET}")
    
    if akr_path:
        install_ok, install_issues = verify_akr_installation(akr_path)
        
        if install_ok:
            print_success("AKR installation is valid")
            print_info(f"Location: {akr_path}")
        else:
            print_error("AKR installation has issues:")
            for issue in install_issues:
                print_info(issue, indent=4)
            all_checks_passed = False
    else:
        print_warning("Skipping (environment variable not set)")
    
    # Check 3: Python Environment
    print(f"\n{Colors.BOLD}Check 3: Python Virtual Environment{Colors.RESET}")
    
    if akr_path:
        python_ok, python_result = check_python_environment(akr_path)
        
        if python_ok:
            print_success("Python virtual environment found")
            print_info(f"Python: {python_result}")
        else:
            print_error(python_result)
            print_info("Run setup.ps1 or create virtual environment manually")
            all_checks_passed = False
    else:
        print_warning("Skipping (environment variable not set)")
    
    # Check 4: VS Code Settings
    print(f"\n{Colors.BOLD}Check 4: VS Code User Settings{Colors.RESET}")
    
    settings_ok, settings_data = check_vscode_settings()
    
    if settings_ok:
        akr_count = settings_data.get("akr_tasks", 0)
        
        if akr_count > 0:
            print_success(f"Found {akr_count} AKR tasks in user settings")
            print_info(f"Settings file: {settings_data.get('path')}")
            print_info("Tasks configured:")
            for label in settings_data.get("task_labels", []):
                print_info(f"  • {label}", indent=4)
        else:
            print_error("No AKR tasks found in user settings")
            print_info(f"Settings file: {settings_data.get('path')}")
            print_info(f"Total tasks: {settings_data.get('total_tasks', 0)}")
            print_info("Run: python scripts/setup_global_tasks.py")
            all_checks_passed = False
    else:
        print_error("VS Code settings issue:")
        print_info(settings_data.get("error", "Unknown error"), indent=4)
        all_checks_passed = False
    
    # Check 5: Task Definitions
    print(f"\n{Colors.BOLD}Check 5: Task Definition Validation{Colors.RESET}")
    
    if settings_ok and akr_path:
        tasks_ok, task_issues = verify_task_definitions(settings_data, akr_path)
        
        if tasks_ok:
            print_success("All task definitions are valid")
            print_info("Tasks correctly reference environment variable")
            print_info("All script paths exist")
        else:
            print_error("Task definition issues found:")
            for issue in task_issues:
                print_info(issue, indent=4)
            all_checks_passed = False
    else:
        print_warning("Skipping (prerequisite checks failed)")
    
    # Final Summary
    print_header("Summary")
    
    if all_checks_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All checks passed!{Colors.RESET}")
        print("\nAKR tasks should be available in all VS Code workspaces.")
        print("\nTo use AKR tasks:")
        print("  1. Open any workspace (UI, API, database repos)")
        print("  2. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)")
        print("  3. Type 'Tasks: Run Task'")
        print("  4. Select any AKR task")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Some checks failed{Colors.RESET}")
        print("\nPlease address the issues above, then run this script again.")
        print("\nCommon fixes:")
        print("  • Run: python scripts/setup_global_tasks.py")
        print("  • Restart VS Code after setting environment variables")
        print("  • Verify akr-mcp-server installation is complete")
    
    print()
    
    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        exit(1)
