"""Windows hotkey service management."""

import os
import sys
import subprocess
import time
import ctypes


def is_admin():
    """Check if running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_executable_path():
    """Get the path to the executable or script."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return sys.executable
    else:
        # Running as script
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(script_dir, 'main.py')


def setup_context_menu():
    """
    Set up Windows context menu for selected text.
    Requires administrator privileges.
    """
    if not is_admin():
        print("ERROR: Administrator privileges required!")
        print("Please run this script as administrator.")
        return False

    try:
        exe_path = get_executable_path()

        # If it's a Python script, we need to call it with Python
        if exe_path.endswith('.py'):
            python_exe = sys.executable
            command = f'"{python_exe}" "{exe_path}"'
        else:
            command = f'"{exe_path}"'

        # Registry key path for context menu on selected text
        key_path = r'*\\shell\\SendToAnki'

        # Create main menu item
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, 'Send to Anki')
            winreg.SetValueEx(key, 'Icon', 0, winreg.REG_SZ, exe_path)

        # Create command subkey
        command_path = key_path + r'\\command'
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, command_path) as key:
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, command)

        print("✓ Context menu installed successfully!")
        print("Right-click on any selected text and choose 'Send to Anki'")
        return True

    except Exception as e:
        print(f"ERROR: Failed to setup context menu: {e}")
        return False


def remove_context_menu():
    """
    Remove Windows context menu.
    Requires administrator privileges.
    """
    if not is_admin():
        print("ERROR: Administrator privileges required!")
        print("Please run this script as administrator.")
        return False

    try:
        key_path = r'*\\shell\\SendToAnki'

        # Delete the registry key
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path + r'\\command')
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path)

        print("✓ Context menu removed successfully!")
        return True

    except FileNotFoundError:
        print("Context menu was not installed.")
        return False
    except Exception as e:
        print(f"ERROR: Failed to remove context menu: {e}")
        return False


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Manage Windows context menu')
    parser.add_argument(
        '--install',
        action='store_true',
        help='Install context menu (requires admin)'
    )
    parser.add_argument(
        '--uninstall',
        action='store_true',
        help='Remove context menu (requires admin)'
    )

    args = parser.parse_args()

    if args.install:
        setup_context_menu()
    elif args.uninstall:
        remove_context_menu()
    else:
        print("Usage:")
        print("  python windows_menu.py --install    (Install context menu)")
        print("  python windows_menu.py --uninstall  (Remove context menu)")
        print("\nNote: Requires administrator privileges")
