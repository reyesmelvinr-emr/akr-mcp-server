#!/usr/bin/env python3
"""
Setup script to configure AKR tasks globally for all VS Code workspaces.

This script:
1. Detects VS Code user settings location
2. Prompts for akr-mcp-server installation path
3. Sets AKR_MCP_SERVER_PATH environment variable
4. Merges AKR tasks into VS Code user settings.json
5. Backs up existing settings before modification
"""

import json
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional


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


def get_default_akr_path() -> Path:
    """Get default AKR MCP server path (current script's parent directory)."""
    return Path(__file__).parent.parent.resolve()


def prompt_for_akr_path() -> Path:
    """Prompt user for akr-mcp-server installation path."""
    default_path = get_default_akr_path()
    
    print("\n" + "="*70)
    print("AKR MCP Server - Global Task Setup")
    print("="*70)
    print("\nThis script will configure AKR tasks to be available in all VS Code workspaces.")
    print("\nPlease specify the akr-mcp-server installation directory.")
    print(f"Default: {default_path}")
    
    while True:
        user_input = input(f"\nEnter path (or press Enter for default): ").strip()
        
        if not user_input:
            path = default_path
        else:
            path = Path(user_input).resolve()
        
        # Validate path
        if not path.exists():
            print(f"❌ Error: Path does not exist: {path}")
            continue
        
        if not path.is_dir():
            print(f"❌ Error: Path is not a directory: {path}")
            continue
        
        # Check for expected structure
        scripts_dir = path / "scripts"
        if not scripts_dir.exists():
            print(f"❌ Error: Missing 'scripts' directory in: {path}")
            print("   Please ensure you're pointing to the akr-mcp-server root directory.")
            continue
        
        # Check for key scripts
        required_scripts = [
            "scripts/generate_and_write_documentation.py",
            "scripts/validation/validate_documentation.py"
        ]
        
        missing_scripts = [s for s in required_scripts if not (path / s).exists()]
        if missing_scripts:
            print(f"❌ Error: Missing required scripts:")
            for script in missing_scripts:
                print(f"   - {script}")
            print("   Please ensure this is a complete akr-mcp-server installation.")
            continue
        
        # Path is valid
        print(f"\n✓ Valid akr-mcp-server installation found: {path}")
        return path


def set_environment_variable(name: str, value: str) -> bool:
    """Set environment variable based on OS."""
    system = platform.system()
    
    print(f"\nSetting environment variable: {name}={value}")
    
    try:
        if system == "Windows":
            # Use setx to set user-level environment variable
            result = subprocess.run(
                ["setx", name, value],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print(f"✓ Environment variable set (user-level)")
                print(f"  Note: Restart VS Code for changes to take effect")
                # Also set in current process
                os.environ[name] = value
                return True
            else:
                print(f"❌ Failed to set environment variable: {result.stderr}")
                return False
        
        else:  # macOS and Linux
            # Detect shell
            shell = os.getenv("SHELL", "/bin/bash")
            shell_name = Path(shell).name
            
            # Determine profile file
            home = Path.home()
            if shell_name == "zsh":
                profile_file = home / ".zshrc"
            elif shell_name == "bash":
                profile_file = home / ".bashrc"
            else:
                profile_file = home / ".profile"
            
            # Check if variable already exists
            export_line = f'export {name}="{value}"'
            
            if profile_file.exists():
                content = profile_file.read_text()
                if name in content:
                    print(f"⚠️  Warning: {name} already exists in {profile_file}")
                    overwrite = input("Overwrite existing value? (y/N): ").strip().lower()
                    if overwrite != 'y':
                        print("Skipping environment variable update")
                        return True
                    
                    # Remove old lines
                    lines = [line for line in content.split('\n') if name not in line]
                    content = '\n'.join(lines)
                else:
                    content = content.rstrip('\n')
            else:
                content = ""
            
            # Append new export
            if content:
                content += '\n'
            content += f'\n# AKR MCP Server Path\n{export_line}\n'
            
            # Backup and write
            if profile_file.exists():
                backup = profile_file.with_suffix(profile_file.suffix + '.backup')
                shutil.copy(profile_file, backup)
                print(f"✓ Backed up {profile_file} to {backup}")
            
            profile_file.write_text(content)
            print(f"✓ Added to {profile_file}")
            print(f"  Run: source {profile_file}")
            print(f"  Or restart your terminal")
            
            # Set in current process
            os.environ[name] = value
            return True
    
    except Exception as e:
        print(f"❌ Error setting environment variable: {e}")
        return False


def load_task_template() -> Dict[str, Any]:
    """Load the user task template."""
    template_path = get_default_akr_path() / "templates" / "vscode_user_tasks_template.json"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Task template not found: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def merge_tasks_into_settings(settings_path: Path, task_template: Dict[str, Any]) -> bool:
    """Merge AKR tasks into VS Code user settings.json."""
    print(f"\nConfiguring VS Code user settings: {settings_path}")
    
    # Create parent directory if it doesn't exist
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing settings or create new
    if settings_path.exists():
        print(f"✓ Found existing settings.json")
        with open(settings_path, 'r', encoding='utf-8') as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError as e:
                print(f"❌ Error: Failed to parse existing settings.json: {e}")
                return False
        
        # Backup existing settings
        backup_path = settings_path.with_suffix('.json.backup')
        shutil.copy(settings_path, backup_path)
        print(f"✓ Backed up existing settings to {backup_path}")
    else:
        print(f"Creating new settings.json")
        settings = {}
    
    # Merge tasks
    existing_tasks = settings.get("tasks.tasks", [])
    akr_tasks = task_template.get("tasks", [])
    
    # Remove any existing AKR tasks (identified by label prefix)
    non_akr_tasks = [t for t in existing_tasks if not t.get("label", "").startswith("AKR:")]
    
    # Add new AKR tasks
    merged_tasks = non_akr_tasks + akr_tasks
    
    # Update settings
    settings["tasks.version"] = "2.0.0"
    settings["tasks.tasks"] = merged_tasks
    
    # Also add inputs if not present
    if "tasks.inputs" not in settings:
        settings["tasks.inputs"] = task_template.get("inputs", [])
    else:
        # Merge inputs (avoid duplicates by id)
        existing_input_ids = {inp.get("id") for inp in settings.get("tasks.inputs", [])}
        new_inputs = [inp for inp in task_template.get("inputs", []) if inp.get("id") not in existing_input_ids]
        settings["tasks.inputs"].extend(new_inputs)
    
    # Write updated settings
    try:
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
        
        print(f"✓ Successfully configured {len(akr_tasks)} AKR tasks")
        print(f"  Tasks are now available in all VS Code workspaces")
        return True
    
    except Exception as e:
        print(f"❌ Error writing settings.json: {e}")
        return False


def verify_setup() -> bool:
    """Verify the setup was successful."""
    print("\n" + "="*70)
    print("Verifying Setup")
    print("="*70)
    
    success = True
    
    # Check environment variable
    akr_path = os.getenv("AKR_MCP_SERVER_PATH")
    if akr_path:
        print(f"✓ AKR_MCP_SERVER_PATH: {akr_path}")
        
        # Verify path exists
        if Path(akr_path).exists():
            print(f"✓ Path exists and is accessible")
        else:
            print(f"❌ Path does not exist: {akr_path}")
            success = False
    else:
        print(f"❌ AKR_MCP_SERVER_PATH not set in current environment")
        print(f"   (This is expected on Windows - restart VS Code to load new env var)")
        # Don't mark as failure on Windows since setx requires restart
        if platform.system() != "Windows":
            success = False
    
    # Check settings.json
    try:
        settings_path = get_vscode_user_settings_path()
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            tasks = settings.get("tasks.tasks", [])
            akr_task_count = sum(1 for t in tasks if t.get("label", "").startswith("AKR:"))
            
            if akr_task_count > 0:
                print(f"✓ Found {akr_task_count} AKR tasks in user settings")
            else:
                print(f"❌ No AKR tasks found in user settings")
                success = False
        else:
            print(f"❌ Settings file not found: {settings_path}")
            success = False
    
    except Exception as e:
        print(f"❌ Error checking settings: {e}")
        success = False
    
    return success


def main():
    """Main setup function."""
    try:
        # Step 1: Prompt for AKR path
        akr_path = prompt_for_akr_path()
        
        # Step 2: Set environment variable
        success = set_environment_variable("AKR_MCP_SERVER_PATH", str(akr_path))
        if not success:
            print("\n❌ Failed to set environment variable")
            print("   Please set AKR_MCP_SERVER_PATH manually")
            return 1
        
        # Step 3: Load task template
        print("\nLoading task template...")
        task_template = load_task_template()
        print(f"✓ Loaded {len(task_template.get('tasks', []))} task definitions")
        
        # Step 4: Merge into settings
        settings_path = get_vscode_user_settings_path()
        success = merge_tasks_into_settings(settings_path, task_template)
        if not success:
            print("\n❌ Failed to configure VS Code settings")
            return 1
        
        # Step 5: Verify setup
        verify_setup()
        
        # Success message
        print("\n" + "="*70)
        print("✓ Setup Complete!")
        print("="*70)
        print("\nAKR tasks are now available in all VS Code workspaces.")
        print("\nNext steps:")
        print("  1. Restart VS Code to load environment variable")
        print("  2. Open any workspace (UI, API, database repos)")
        print("  3. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)")
        print("  4. Type 'Tasks: Run Task' and select any AKR task")
        print("\nAvailable tasks:")
        print("  • AKR: Generate and Write Documentation (Unified)")
        print("  • AKR: Validate Documentation (file)")
        print("  • AKR: Validate Documentation (changed files)")
        print("  • AKR: Validate Documentation (all in docs/)")
        print("  • AKR: Validate Traceability")
        print("  • AKR: Scan Write Bypasses")
        print("\nFor troubleshooting, run: python scripts/verify_global_tasks.py")
        print("="*70)
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        return 1
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
