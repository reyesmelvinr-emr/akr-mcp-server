#!/usr/bin/env python3
"""
Interactive Scaffolding Guide for AKR Documentation

Walks users through their documentation plan batch-by-batch,
auto-running the scaffold task with correct inputs for each batch.

Usage:
    python interactive_scaffolding_guide.py [--workspace-root <path>]

Expected workflow:
    1. User creates documentation plan (Step 5)
    2. User provides plan in JSON format via input
    3. Script displays each batch and asks to scaffold
    4. Script auto-runs scaffold task via subprocess
    5. User can skip, retry, or proceed to next batch
"""

import json
import os
import subprocess
import sys
import io
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure stdout to use UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class ScaffoldingGuide:
    """Interactive guide for batch scaffolding documentation."""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.batches: List[Dict[str, Any]] = []
        self.scaffolded_files: List[str] = []
        self.current_batch_index = 0

    def load_plan_from_input(self) -> bool:
        """
        Prompt user for documentation plan in JSON format.
        
        Expected format:
        {
            "batches": [
                {
                    "name": "Data Layer Foundation",
                    "module_name": "TrainingTrackerEntities",
                    "files": ["Domain/Entities/User.cs", "Domain/Entities/Course.cs"]
                }
            ]
        }
        """
        print("\n" + "=" * 70)
        print("AKR INTERACTIVE SCAFFOLDING GUIDE")
        print("=" * 70)
        print("\nProvide your documentation plan in JSON format.")
        print("Format: { \"batches\": [ { \"name\": \"\", \"module_name\": \"\", \"files\": [] } ] }")
        print("\nPaste your plan (type END on a new line when done):\n")

        lines = []
        while True:
            try:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            except EOFError:
                break

        plan_str = "\n".join(lines)

        try:
            plan = json.loads(plan_str)
            self.batches = plan.get("batches", [])
            return len(self.batches) > 0
        except json.JSONDecodeError as e:
            print(f"\n❌ Invalid JSON: {e}")
            return False

    def load_plan_from_json_file(self, filepath: str) -> bool:
        """Load plan from a JSON file."""
        try:
            with open(filepath) as f:
                plan = json.load(f)
                self.batches = plan.get("batches", [])
                return len(self.batches) > 0
        except Exception as e:
            print(f"❌ Failed to load plan file: {e}")
            return False

    def display_batch(self, index: int) -> bool:
        """Display batch information and return True if batch exists."""
        if index >= len(self.batches):
            return False

        batch = self.batches[index]
        print(f"\n{'─' * 70}")
        print(f"📦 BATCH {index + 1} of {len(self.batches)}: {batch.get('name', 'Unnamed')}")
        print(f"{'─' * 70}")
        print(f"Module Name: {batch.get('module_name', 'N/A')}")
        print(f"Files ({len(batch.get('files', []))} files):")
        for file in batch.get("files", []):
            print(f"  ├─ {file}")

        return True

    def scaffold_batch(self, index: int) -> bool:
        """
        Run the scaffold task for the given batch.
        
        This calls the AKR scaffold task with the batch's inputs.
        """
        if index >= len(self.batches):
            return False

        batch = self.batches[index]
        module_name = batch.get("module_name", "UnnamedModule")
        source_files = ", ".join(batch.get("files", []))

        if not source_files:
            print(f"⚠️  No files in batch. Skipping.")
            return False

        print(f"\n🔨 Scaffolding...")
        print(f"   Module: {module_name}")
        print(f"   Files: {source_files}")
        print(f"   Workspace: {self.workspace_root}")

        try:
            # Get the AKR scripts directory (this script's parent directory)
            script_dir = Path(__file__).parent
            scaffold_script = script_dir / "scaffold_documentation.py"
            print(f"   Script: {scaffold_script}")
            
            # Call the scaffold task via PowerShell (Windows) or bash (Linux/Mac)
            if sys.platform == "win32":
                cmd = [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f'[Console]::OutputEncoding = [System.Text.Encoding]::UTF8 ; '
                    f'cd "{self.workspace_root}" ; '
                    f'python "{scaffold_script}" '
                    f'--module-name "{module_name}" '
                    f'--source-files "{source_files}" '
                    f'--workspace-root "{self.workspace_root}"'
                ]
            else:
                cmd = [
                    "bash",
                    "-c",
                    f'cd "{self.workspace_root}" && '
                    f'python "{scaffold_script}" '
                    f'--module-name "{module_name}" '
                    f'--source-files "{source_files}" '
                    f'--workspace-root "{self.workspace_root}"'
                ]

            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)

            if result.returncode == 0:
                print(f"✅ Scaffolding complete!")
                if result.stdout:
                    print(result.stdout)

                    # Extract output file path from stdout if available
                    for line in result.stdout.split("\n"):
                        if "docs/" in line and ".md" in line:
                            self.scaffolded_files.append(line.strip())

                return True
            else:
                print(f"❌ Scaffolding failed! (exit code: {result.returncode})")
                if result.stdout:
                    print(f"Output:\n{result.stdout}")
                if result.stderr:
                    print(f"Error:\n{result.stderr}")
                if not result.stdout and not result.stderr:
                    print(f"No output captured. Command: {' '.join(cmd)}")
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ Scaffolding timed out (60 seconds).")
            return False
        except Exception as e:
            print(f"❌ Failed to run scaffold task: {e}")
            return False

    def prompt_batch_action(self) -> str:
        """Prompt user for action on current batch."""
        print(f"\nWhat would you like to do?")
        print(f"  [y]es - Scaffold this batch")
        print(f"  [s]kip - Skip this batch (do it manually later)")
        print(f"  [r]etry - Retry scaffolding this batch")
        print(f"  [q]uit - Quit the guide")

        while True:
            choice = input("Your choice (y/s/r/q): ").strip().lower()
            if choice in ["y", "s", "r", "q"]:
                return choice
            print("Invalid choice. Please enter y, s, r, or q.")

    def run_interactive_loop(self) -> None:
        """Main interactive loop for scaffolding batches."""
        print(f"\n✓ Loaded {len(self.batches)} batches")
        print(f"✓ Ready to scaffold\n")

        while self.current_batch_index < len(self.batches):
            # Display current batch
            if not self.display_batch(self.current_batch_index):
                break

            # Ask user what to do
            action = self.prompt_batch_action()

            if action == "y":
                # Scaffold this batch
                success = self.scaffold_batch(self.current_batch_index)
                if success:
                    print(f"✓ Batch {self.current_batch_index + 1} scaffolded successfully!")
                    self.current_batch_index += 1
                else:
                    # Let user retry or skip
                    retry = input("\nRetry scaffolding? ([y]es/[n]o/[s]kip): ").strip().lower()
                    if retry == "y":
                        continue
                    elif retry == "s":
                        print(f"⊘ Skipping batch {self.current_batch_index + 1}")
                        self.current_batch_index += 1
                    else:
                        print(f"❌ Batch {self.current_batch_index + 1} not scaffolded")
                        self.current_batch_index += 1

            elif action == "s":
                # Skip this batch
                print(f"⊘ Skipping batch {self.current_batch_index + 1}")
                self.current_batch_index += 1

            elif action == "r":
                # Retry - stay on current batch
                continue

            elif action == "q":
                # Quit
                print(f"\n⊘ Exiting scaffolding guide")
                break

        # Summary
        self.print_summary()

    def print_summary(self) -> None:
        """Print summary of scaffolding session."""
        print(f"\n{'=' * 70}")
        print(f"SCAFFOLDING SUMMARY")
        print(f"{'=' * 70}")
        print(f"✓ Batches processed: {self.current_batch_index}/{len(self.batches)}")
        print(f"✓ Files scaffolded: {len(self.scaffolded_files)}")

        if self.scaffolded_files:
            print(f"\nDocumentation created:")
            for file in self.scaffolded_files:
                print(f"  ✓ {file}")

        if self.current_batch_index < len(self.batches):
            remaining = len(self.batches) - self.current_batch_index
            print(f"\n⚠️  {remaining} batch(es) not yet scaffolded")
            print(f"Run this guide again to continue.\n")
        else:
            print(f"\n✅ All batches scaffolded!")
            print(f"Next step: Fill in documentation with Copilot\n")


def main():
    """Main entry point."""
    # Get workspace root from environment or command line
    workspace_root = os.getenv("VSCODE_WORKSPACE_FOLDER")

    if not workspace_root:
        if len(sys.argv) > 1:
            workspace_root = sys.argv[1]
        else:
            workspace_root = os.getcwd()

    guide = ScaffoldingGuide(workspace_root)

    # Try to load plan from file first (for future integration with VS Code)
    plan_file = Path(workspace_root) / ".akr-scaffolding-plan.json"
    if plan_file.exists():
        print(f"Found scaffolding plan at {plan_file}")
        if guide.load_plan_from_json_file(str(plan_file)):
            guide.run_interactive_loop()
        else:
            print("Failed to load plan. Please provide it manually.")
            if guide.load_plan_from_input():
                guide.run_interactive_loop()
    else:
        # Ask user to provide plan interactively
        if guide.load_plan_from_input():
            guide.run_interactive_loop()
        else:
            print("\n❌ Failed to load documentation plan. Exiting.")
            sys.exit(1)


if __name__ == "__main__":
    main()
