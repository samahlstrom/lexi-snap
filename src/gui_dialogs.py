"""GUI dialogs and notifications for user interaction."""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional


class DeckSelectionDialog:
    """Dialog for selecting an Anki deck."""

    def __init__(self, decks: List[str], title="Select Anki Deck"):
        """
        Initialize deck selection dialog.

        Args:
            decks: List of available deck names
            title: Window title
        """
        self.result = None
        self.decks = decks
        self.title = title

    def show(self) -> Optional[str]:
        """
        Show the dialog and wait for user selection.

        Returns:
            Selected deck name, or None if cancelled
        """
        root = tk.Tk()
        root.title(self.title)
        root.geometry("400x500")
        root.resizable(True, True)
        
        # Always on top and focused
        root.attributes('-topmost', True)
        root.focus_force()

        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (400 // 2)
        y = (root.winfo_screenheight() // 2) - (500 // 2)
        root.geometry(f"400x500+{x}+{y}")

        # Title label
        title_label = tk.Label(
            root,
            text="Choose a deck for your vocabulary card:",
            font=('Arial', 11),
            pady=10
        )
        title_label.pack()

        # Search box
        search_var = tk.StringVar()
        search_var.trace('w', lambda *args: self._filter_decks(search_var, listbox))

        search_frame = tk.Frame(root)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        search_label = tk.Label(search_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=(0, 5))

        search_entry = tk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Listbox with scrollbar
        list_frame = tk.Frame(root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=('Arial', 10)
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=listbox.yview)

        # Populate listbox
        for deck in self.decks:
            listbox.insert(tk.END, deck)

        # Select first item by default
        if self.decks:
            listbox.select_set(0)
            listbox.activate(0)

        # Double-click to confirm
        listbox.bind('<Double-Button-1>', lambda e: self._confirm(root, listbox))

        # Enter key to confirm
        root.bind('<Return>', lambda e: self._confirm(root, listbox))

        # Escape key to cancel
        root.bind('<Escape>', lambda e: self._cancel(root))

        # Button frame
        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=lambda: self._cancel(root),
            width=10
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

        # Confirm button
        confirm_btn = tk.Button(
            button_frame,
            text="Add to Deck",
            command=lambda: self._confirm(root, listbox),
            width=15,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold')
        )
        confirm_btn.pack(side=tk.RIGHT, padx=5)

        # Focus search box
        search_entry.focus()

        # Start dialog
        root.mainloop()

        return self.result

    def _filter_decks(self, search_var, listbox):
        """Filter decks based on search text."""
        search_text = search_var.get().lower()
        listbox.delete(0, tk.END)

        for deck in self.decks:
            if search_text in deck.lower():
                listbox.insert(tk.END, deck)

        # Select first item if available
        if listbox.size() > 0:
            listbox.select_set(0)
            listbox.activate(0)

    def _confirm(self, root, listbox):
        """Confirm selection and close dialog."""
        selection = listbox.curselection()
        if selection:
            self.result = listbox.get(selection[0])
        root.destroy()

    def _cancel(self, root):
        """Cancel and close dialog."""
        self.result = None
        root.destroy()


def show_notification(title: str, message: str, duration: int = 3):
    """
    Show a desktop notification.

    Args:
        title: Notification title
        message: Notification message
        duration: Duration in seconds
    """
    import winsound
    
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name='Dict to Anki',
            timeout=duration
        )
        # Play a notification sound
        winsound.MessageBeep(winsound.MB_OK)
    except Exception as e:
        # Fallback: show simple message box
        print(f"{title}: {message}")
        try:
            winsound.MessageBeep(winsound.MB_OK)
        except:
            pass


def show_error_dialog(message: str, title="Error"):
    """
    Show an error dialog.

    Args:
        message: Error message
        title: Dialog title
    """
    root = tk.Tk()
    root.withdraw()  # Hide main window

    # Center the dialog
    root.update_idletasks()

    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.geometry("400x150")
    
    # Always on top and focused
    dialog.attributes('-topmost', True)
    dialog.focus_force()

    # Center dialog
    x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
    y = (dialog.winfo_screenheight() // 2) - (150 // 2)
    dialog.geometry(f"400x150+{x}+{y}")

    # Message
    msg_label = tk.Label(
        dialog,
        text=message,
        wraplength=350,
        font=('Arial', 10),
        pady=20
    )
    msg_label.pack()

    # OK button
    ok_btn = tk.Button(
        dialog,
        text="OK",
        command=lambda: [dialog.destroy(), root.destroy()],
        width=10
    )
    ok_btn.pack(pady=10)

    dialog.focus()
    root.mainloop()
