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


def get_service_script():
    """Get the path to the hotkey service script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, 'windows_hotkey_service.py')


def is_service_running():
    """Check if the hotkey service is running."""
    try:
        import psutil
        script_name = 'windows_hotkey_service.py'
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and script_name in ' '.join(cmdline):
                    return True, proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return False, None
    except ImportError:
        print("WARNING: psutil not installed, cannot check service status")
        return False, None


def start_service(background=True):
    """Start the hotkey service."""
    running, pid = is_service_running()
    
    if running:
        print(f"Service is already running (PID: {pid})")
        return False
    
    service_script = get_service_script()
    python_exe = sys.executable
    
    try:
        if background:
            # Start in background with no console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE
            
            subprocess.Popen(
                [python_exe, service_script, '--background'],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            time.sleep(1)  # Give it time to start
            print("[OK] Hotkey service started in background")
            print("Press Ctrl+Alt+D on any selected text to send to Anki")
        else:
            # Start in foreground (for testing)
            print("Starting service in foreground (for testing)...")
            subprocess.run([python_exe, service_script])
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to start service: {e}")
        return False


def stop_service():
    """Stop the hotkey service."""
    try:
        import psutil
        
        running, pid = is_service_running()
        
        if not running:
            print("Service is not running")
            return False
        
        # Kill the process
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait(timeout=5)
        
        print("✓ Hotkey service stopped")
        return True
        
    except ImportError:
        print("ERROR: psutil not installed, cannot stop service")
        print("Please install requirements: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"ERROR: Failed to stop service: {e}")
        return False


def install_autostart():
    """Install the service to auto-start with Windows."""
    if not is_admin():
        print("ERROR: Administrator privileges required!")
        print("Please run this script as administrator.")
        return False
    
    try:
        import winreg
        
        service_script = get_service_script()
        python_exe = sys.executable
        
        # Create startup command
        startup_cmd = f'"{python_exe}" "{service_script}" --background'
        
        # Add to Windows startup registry
        key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'DictToAnkiHotkey', 0, winreg.REG_SZ, startup_cmd)
        winreg.CloseKey(key)
        
        print("✓ Auto-start installed successfully!")
        print("Service will start automatically when you log in to Windows")
        
        # Ask if user wants to start now
        print("\nStart the service now? (y/n): ", end='')
        response = input().strip().lower()
        if response == 'y':
            start_service(background=True)
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to install auto-start: {e}")
        return False


def uninstall_autostart():
    """Remove the service from Windows startup."""
    if not is_admin():
        print("ERROR: Administrator privileges required!")
        print("Please run this script as administrator.")
        return False
    
    try:
        import winreg
        
        key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        
        try:
            winreg.DeleteValue(key, 'DictToAnkiHotkey')
            print("✓ Auto-start removed successfully!")
        except FileNotFoundError:
            print("Auto-start was not installed")
        
        winreg.CloseKey(key)
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to uninstall auto-start: {e}")
        return False


def show_status():
    """Show current service status."""
    running, pid = is_service_running()
    
    print("Dict-to-Anki Hotkey Service Status")
    print("=" * 50)
    
    if running:
        print(f"Status: RUNNING (PID: {pid})")
        print("Hotkey: Ctrl + Alt + D")
        print("\nTo use: Select text and press Ctrl+Alt+D")
    else:
        print("Status: NOT RUNNING")
        print("\nTo start: python platform_integration/windows_menu.py --start")
    
    print("\nCommands:")
    print("  --start       Start the hotkey service")
    print("  --stop        Stop the hotkey service")
    print("  --restart     Restart the hotkey service")
    print("  --status      Show service status")
    print("  --install     Install auto-start (requires admin)")
    print("  --uninstall   Remove auto-start (requires admin)")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Dict-to-Anki Hotkey Service Manager')
    parser.add_argument(
        '--start',
        action='store_true',
        help='Start the hotkey service'
    )
    parser.add_argument(
        '--stop',
        action='store_true',
        help='Stop the hotkey service'
    )
    parser.add_argument(
        '--restart',
        action='store_true',
        help='Restart the hotkey service'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show service status'
    )
    parser.add_argument(
        '--install',
        action='store_true',
        help='Install auto-start with Windows (requires admin)'
    )
    parser.add_argument(
        '--uninstall',
        action='store_true',
        help='Remove auto-start (requires admin)'
    )
    parser.add_argument(
        '--foreground',
        action='store_true',
        help='Start service in foreground (for testing)'
    )

    args = parser.parse_args()

    if args.start:
        start_service(background=not args.foreground)
    elif args.stop:
        stop_service()
    elif args.restart:
        print("Restarting service...")
        stop_service()
        time.sleep(1)
        start_service(background=not args.foreground)
    elif args.status:
        show_status()
    elif args.install:
        install_autostart()
    elif args.uninstall:
        uninstall_autostart()
    else:
        show_status()
        print("\nFor help: python windows_menu.py --help")
