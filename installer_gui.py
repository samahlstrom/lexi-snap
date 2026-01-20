"""GUI Installer for Dict-to-Anki."""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import platform
import threading
import requests


class InstallerWizard:
    """Installation wizard with GUI."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dict-to-Anki Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # State
        self.current_step = 0
        self.is_windows = platform.system() == 'Windows'
        self.is_macos = platform.system() == 'Darwin'
        self.python_ok = False
        self.anki_ok = False
        self.ankiconnect_ok = False
        self.deps_ok = False
        self.service_ok = False
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"600x500+{x}+{y}")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components."""
        # Header
        header = tk.Frame(self.root, bg='#4CAF50', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="Dict-to-Anki Installer",
            font=('Arial', 20, 'bold'),
            bg='#4CAF50',
            fg='white'
        )
        title.pack(pady=20)
        
        # Content area
        self.content_frame = tk.Frame(self.root, padx=20, pady=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Button area
        button_frame = tk.Frame(self.root, padx=20, pady=10)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.back_btn = tk.Button(
            button_frame,
            text="Back",
            command=self.go_back,
            width=10,
            state=tk.DISABLED
        )
        self.back_btn.pack(side=tk.LEFT)
        
        self.next_btn = tk.Button(
            button_frame,
            text="Next",
            command=self.go_next,
            width=10,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold')
        )
        self.next_btn.pack(side=tk.RIGHT)
        
        self.cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.root.quit,
            width=10
        )
        self.cancel_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Show first step
        self.show_welcome()
        
    def clear_content(self):
        """Clear content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_welcome(self):
        """Show welcome screen."""
        self.clear_content()
        self.current_step = 0
        
        tk.Label(
            self.content_frame,
            text="Welcome to Dict-to-Anki!",
            font=('Arial', 16, 'bold')
        ).pack(pady=(20, 10))
        
        description = (
            "This wizard will help you install Dict-to-Anki, a tool that lets you "
            "create Anki flashcards from any selected text on your computer.\n\n"
            "Features:\n"
            "• Works system-wide (browsers, PDFs, documents)\n"
            "• Automatic dictionary definitions\n"
            "• Fast hotkey workflow\n"
            "• Integrates with Anki via AnkiConnect\n\n"
            "Click Next to begin the installation."
        )
        
        tk.Label(
            self.content_frame,
            text=description,
            font=('Arial', 10),
            justify=tk.LEFT,
            wraplength=550
        ).pack(pady=10)
        
        self.back_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL, text="Next")
        
    def show_prerequisites(self):
        """Check prerequisites."""
        self.clear_content()
        self.current_step = 1
        
        tk.Label(
            self.content_frame,
            text="Checking Prerequisites",
            font=('Arial', 16, 'bold')
        ).pack(pady=(20, 10))
        
        # Progress frame
        self.progress_frame = tk.Frame(self.content_frame)
        self.progress_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        self.next_btn.config(state=tk.DISABLED)
        self.back_btn.config(state=tk.NORMAL)
        
        # Start checking in background
        threading.Thread(target=self.check_prerequisites, daemon=True).start()
        
    def check_prerequisites(self):
        """Check all prerequisites."""
        checks = [
            ("Checking Python version...", self.check_python),
            ("Checking for Anki...", self.check_anki),
            ("Checking AnkiConnect add-on...", self.check_ankiconnect),
        ]
        
        for i, (message, check_func) in enumerate(checks):
            self.add_check_item(message, "checking")
            result = check_func()
            self.update_check_item(i, "pass" if result else "fail")
            
        # Enable next if all OK
        if self.python_ok and self.anki_ok and self.ankiconnect_ok:
            self.root.after(0, lambda: self.next_btn.config(state=tk.NORMAL))
        
    def add_check_item(self, message, status):
        """Add a check item to progress."""
        frame = tk.Frame(self.progress_frame)
        frame.pack(fill=tk.X, pady=5)
        
        if status == "checking":
            icon = "⏳"
        elif status == "pass":
            icon = "✓"
        else:
            icon = "✗"
            
        label = tk.Label(
            frame,
            text=f"{icon} {message}",
            font=('Arial', 10),
            anchor=tk.W
        )
        label.pack(side=tk.LEFT)
        
    def update_check_item(self, index, status):
        """Update a check item status."""
        frames = self.progress_frame.winfo_children()
        if index < len(frames):
            label = frames[index].winfo_children()[0]
            text = label.cget("text")
            
            if status == "pass":
                icon = "[OK]"
                color = "green"
            else:
                icon = "[FAIL]"
                color = "red"
                
            label.config(text=text.replace("⏳", icon), fg=color)
            
    def check_python(self):
        """Check Python version."""
        version = sys.version_info
        self.python_ok = version.major == 3 and version.minor >= 8
        return self.python_ok
        
    def check_anki(self):
        """Check if Anki is running."""
        try:
            response = requests.post(
                'http://localhost:8765',
                json={'action': 'version', 'version': 6},
                timeout=2
            )
            self.anki_ok = response.status_code == 200
        except:
            self.anki_ok = False
        return self.anki_ok
        
    def check_ankiconnect(self):
        """Check if AnkiConnect is installed."""
        if not self.anki_ok:
            self.ankiconnect_ok = False
            return False
            
        try:
            response = requests.post(
                'http://localhost:8765',
                json={'action': 'version', 'version': 6},
                timeout=2
            )
            result = response.json()
            self.ankiconnect_ok = result.get('result') is not None
        except:
            self.ankiconnect_ok = False
        return self.ankiconnect_ok
        
    def show_install_deps(self):
        """Install dependencies."""
        self.clear_content()
        self.current_step = 2
        
        tk.Label(
            self.content_frame,
            text="Installing Dependencies",
            font=('Arial', 16, 'bold')
        ).pack(pady=(20, 10))
        
        tk.Label(
            self.content_frame,
            text="Installing required Python packages...",
            font=('Arial', 10)
        ).pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.content_frame,
            mode='indeterminate',
            length=400
        )
        self.progress.pack(pady=20)
        self.progress.start()
        
        # Log area
        self.log_text = tk.Text(self.content_frame, height=15, width=70, font=('Courier', 8))
        self.log_text.pack(pady=10)
        
        scrollbar = tk.Scrollbar(self.content_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self.next_btn.config(state=tk.DISABLED)
        self.back_btn.config(state=tk.DISABLED)
        
        # Start installation
        threading.Thread(target=self.install_dependencies, daemon=True).start()
        
    def install_dependencies(self):
        """Install Python dependencies."""
        try:
            requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
            
            process = subprocess.Popen(
                [sys.executable, '-m', 'pip', 'install', '-r', requirements_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            for line in process.stdout:
                self.root.after(0, lambda l=line: self.log_text.insert(tk.END, l))
                self.root.after(0, lambda: self.log_text.see(tk.END))
                
            process.wait()
            self.deps_ok = process.returncode == 0
            
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.next_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.back_btn.config(state=tk.NORMAL))
            
            if self.deps_ok:
                self.root.after(0, lambda: self.log_text.insert(tk.END, "\n[OK] Installation complete!\n"))
            else:
                self.root.after(0, lambda: self.log_text.insert(tk.END, "\n[ERROR] Installation failed!\n"))
                
        except Exception as e:
            self.deps_ok = False
            self.root.after(0, lambda: messagebox.showerror("Error", f"Installation failed: {e}"))
            
    def show_setup_service(self):
        """Set up platform-specific service."""
        self.clear_content()
        self.current_step = 3
        
        tk.Label(
            self.content_frame,
            text="Setting Up Service",
            font=('Arial', 16, 'bold')
        ).pack(pady=(20, 10))
        
        if self.is_windows:
            self.setup_windows_service()
        else:
            self.setup_macos_service()
            
    def setup_windows_service(self):
        """Set up Windows hotkey service."""
        tk.Label(
            self.content_frame,
            text="The hotkey service will be set to auto-start with Windows.",
            font=('Arial', 10)
        ).pack(pady=10)
        
        tk.Label(
            self.content_frame,
            text="Note: You'll need to run this installer as Administrator for auto-start.",
            font=('Arial', 9, 'italic'),
            fg='gray'
        ).pack(pady=5)
        
        self.status_label = tk.Label(
            self.content_frame,
            text="Click Next to install the service...",
            font=('Arial', 10)
        )
        self.status_label.pack(pady=20)
        
        self.next_btn.config(state=tk.NORMAL)
        self.back_btn.config(state=tk.NORMAL)
        
    def setup_macos_service(self):
        """Set up macOS Automator service."""
        instructions = (
            "macOS requires manual setup:\n\n"
            "1. Open Automator (Applications → Automator)\n"
            "2. Create a new 'Quick Action'\n"
            "3. Set 'Workflow receives' to 'text' in 'any application'\n"
            "4. Add 'Run Shell Script' action\n"
            "5. Paste this command:\n"
        )
        
        tk.Label(
            self.content_frame,
            text=instructions,
            font=('Arial', 10),
            justify=tk.LEFT,
            wraplength=550
        ).pack(pady=10)
        
        command = f"{sys.executable} {os.path.join(os.path.dirname(__file__), 'main.py')} --stdin"
        
        command_text = tk.Text(self.content_frame, height=2, width=70, font=('Courier', 9))
        command_text.insert(1.0, command)
        command_text.config(state=tk.DISABLED)
        command_text.pack(pady=10)
        
        tk.Label(
            self.content_frame,
            text="6. Save as 'Send to Anki'\n7. Grant Accessibility permissions in System Settings",
            font=('Arial', 10),
            justify=tk.LEFT
        ).pack(pady=10)
        
        self.service_ok = True
        self.next_btn.config(state=tk.NORMAL)
        
    def show_complete(self):
        """Show completion screen."""
        self.clear_content()
        self.current_step = 4
        
        tk.Label(
            self.content_frame,
            text="Installation Complete!",
            font=('Arial', 16, 'bold'),
            fg='green'
        ).pack(pady=(20, 10))
        
        if self.is_windows:
            usage_text = (
                "Dict-to-Anki has been installed successfully!\n\n"
                "How to use:\n"
                "1. Make sure Anki is running\n"
                "2. Start the service: Open PowerShell as Administrator and run:\n"
                "   python platform_integration/windows_menu.py --start\n\n"
                "3. Highlight any word in any application\n"
                "4. Press Ctrl+Alt+D\n"
                "5. Select a deck and you're done!\n\n"
                "The service will auto-start with Windows if installed as Administrator."
            )
        else:
            usage_text = (
                "Dict-to-Anki has been installed successfully!\n\n"
                "How to use:\n"
                "1. Make sure Anki is running\n"
                "2. Complete the Automator setup (see previous screen)\n"
                "3. Highlight any word in any application\n"
                "4. Right-click → Services → Send to Anki\n"
                "5. Select a deck and you're done!"
            )
        
        tk.Label(
            self.content_frame,
            text=usage_text,
            font=('Arial', 10),
            justify=tk.LEFT,
            wraplength=550
        ).pack(pady=10)
        
        self.next_btn.config(text="Finish", command=self.root.quit)
        self.back_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.DISABLED)
        
    def go_next(self):
        """Go to next step."""
        if self.current_step == 0:
            self.show_prerequisites()
        elif self.current_step == 1:
            if not (self.python_ok and self.anki_ok and self.ankiconnect_ok):
                messagebox.showerror(
                    "Prerequisites Not Met",
                    "Please install missing prerequisites:\n\n" +
                    ("• Python 3.8+\n" if not self.python_ok else "") +
                    ("• Anki (must be running)\n" if not self.anki_ok else "") +
                    ("• AnkiConnect add-on (code: 2055492159)\n" if not self.ankiconnect_ok else "")
                )
                return
            self.show_install_deps()
        elif self.current_step == 2:
            if not self.deps_ok:
                messagebox.showerror("Error", "Dependency installation failed. Please try again.")
                return
            self.show_setup_service()
        elif self.current_step == 3:
            self.show_complete()
            
    def go_back(self):
        """Go to previous step."""
        if self.current_step == 1:
            self.show_welcome()
        elif self.current_step == 2:
            self.show_prerequisites()
        elif self.current_step == 3:
            self.show_install_deps()
            
    def run(self):
        """Run the installer."""
        self.root.mainloop()


if __name__ == '__main__':
    installer = InstallerWizard()
    installer.run()
