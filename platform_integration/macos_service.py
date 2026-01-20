"""macOS Automator Service setup helper."""

import os
import sys
import plistlib
import shutil


def get_script_path():
    """Get the path to main.py."""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(script_dir, 'main.py')


def get_python_path():
    """Get the path to Python executable."""
    return sys.executable


def create_automator_workflow():
    """
    Create an Automator Quick Action workflow for macOS.

    Returns:
        Path to the created workflow, or None if failed
    """
    workflow_name = "Send to Anki.workflow"
    services_dir = os.path.expanduser("~/Library/Services")
    workflow_path = os.path.join(services_dir, workflow_name)

    # Create Services directory if it doesn't exist
    os.makedirs(services_dir, exist_ok=True)

    print(f"Creating Automator workflow at: {workflow_path}")
    print("\nNote: On macOS, you'll need to set this up manually through Automator.")
    print("\nInstructions:")
    print("=" * 70)
    print("1. Open Automator.app")
    print("2. Create a new 'Quick Action'")
    print("3. Configure workflow settings:")
    print("   - Workflow receives: 'text'")
    print("   - In: 'any application'")
    print("4. Add 'Run Shell Script' action")
    print("5. Set the shell script to:")
    print(f"\n   {get_python_path()} {get_script_path()} --stdin\n")
    print("6. Set 'Pass input' to 'to stdin'")
    print("7. Save as 'Send to Anki'")
    print("=" * 70)
    print("\nAfter creating the workflow:")
    print("1. Grant Accessibility permissions in System Settings")
    print("2. Right-click any selected text")
    print("3. Go to Services > Send to Anki")
    print("=" * 70)

    # Create a shell script helper that users can reference
    helper_script_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "macos_service_helper.sh"
    )

    with open(helper_script_path, 'w') as f:
        f.write(f"""#!/bin/bash
# macOS Service Helper Script for Dict-to-Anki
# This script is called by the Automator Quick Action

export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

{get_python_path()} {get_script_path()} --stdin
""")

    # Make it executable
    os.chmod(helper_script_path, 0o755)

    print(f"\n✓ Helper script created at: {helper_script_path}")
    print("You can use this path in the Automator 'Run Shell Script' action")

    return helper_script_path


def show_instructions():
    """Show detailed setup instructions for macOS."""
    print("\n" + "=" * 70)
    print("macOS Setup Instructions")
    print("=" * 70)
    print("\nOption 1: Automator Quick Action (Recommended)")
    print("-" * 70)
    print("1. Open Automator.app")
    print("2. Choose 'Quick Action' template")
    print("3. Set workflow settings:")
    print("   - Workflow receives: text")
    print("   - In: any application")
    print("4. Search for and add 'Run Shell Script' action")
    print("5. Configure the script:")
    print("   - Shell: /bin/bash")
    print("   - Pass input: to stdin")
    print(f"   - Script content:")
    print(f"     {get_python_path()} {get_script_path()} --stdin")
    print("6. Save as 'Send to Anki'")
    print("\n7. Grant permissions:")
    print("   - System Settings > Privacy & Security > Accessibility")
    print("   - Enable for 'Automator' or 'System Events'")
    print("\n8. Usage:")
    print("   - Highlight any text")
    print("   - Right-click > Services > Send to Anki")
    print("\n" + "=" * 70)
    print("\nOption 2: Keyboard Shortcut (Alternative)")
    print("-" * 70)
    print("After creating the Quick Action:")
    print("1. System Settings > Keyboard > Keyboard Shortcuts")
    print("2. Services > General")
    print("3. Find 'Send to Anki' and assign a shortcut (e.g., Cmd+Shift+A)")
    print("=" * 70)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='macOS Service setup helper')
    parser.add_argument(
        '--create-helper',
        action='store_true',
        help='Create helper script for Automator'
    )
    parser.add_argument(
        '--show-instructions',
        action='store_true',
        help='Show detailed setup instructions'
    )

    args = parser.parse_args()

    if args.create_helper:
        create_automator_workflow()
    elif args.show_instructions:
        show_instructions()
    else:
        print("macOS Service Setup")
        print("\nOptions:")
        print("  --create-helper       Create helper script")
        print("  --show-instructions   Show detailed setup guide")
        print("\nFor automatic setup, run:")
        print(f"  python3 {__file__} --create-helper")
