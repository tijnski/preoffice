#!/usr/bin/env python3
"""
PrePanda Helper - Floating AI Assistant Widget
A standalone floating window that appears as an overlay, similar to Clippy.
Runs independently of PreOffice but communicates via a simple file-based protocol.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import json
import threading
import time

# Configuration
CONFIG_DIR = os.path.expanduser("~/Library/Application Support/PrePanda")
COMMAND_FILE = os.path.join(CONFIG_DIR, "command.json")
RESPONSE_FILE = os.path.join(CONFIG_DIR, "response.json")

class PrePandaHelper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PrePanda")

        # Make it a floating overlay window
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-alpha', 0.95)  # Slightly transparent
        self.root.overrideredirect(False)  # Keep title bar for now

        # Set window size and position (bottom-right corner)
        window_width = 280
        window_height = 350
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - window_width - 50
        y = screen_height - window_height - 100
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Configure style
        self.root.configure(bg='#ffffff')

        # Create UI
        self.create_ui()

        # Ensure config directory exists
        os.makedirs(CONFIG_DIR, exist_ok=True)

        # Start command listener
        self.running = True
        self.listener_thread = threading.Thread(target=self.listen_for_commands, daemon=True)
        self.listener_thread.start()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_ui(self):
        """Create the helper UI."""
        # Main frame with padding
        main_frame = tk.Frame(self.root, bg='#ffffff', padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Panda emoji/image at top
        panda_label = tk.Label(
            main_frame,
            text="🐼",
            font=('Arial', 72),
            bg='#ffffff'
        )
        panda_label.pack(pady=(0, 10))

        # Title
        title_label = tk.Label(
            main_frame,
            text="PrePanda AI",
            font=('Helvetica', 18, 'bold'),
            bg='#ffffff',
            fg='#333333'
        )
        title_label.pack()

        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text="Your AI Writing Assistant",
            font=('Helvetica', 11),
            bg='#ffffff',
            fg='#666666'
        )
        subtitle_label.pack(pady=(0, 15))

        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#ffffff')
        buttons_frame.pack(fill=tk.X, pady=5)

        # Style for buttons
        button_style = {
            'font': ('Helvetica', 12),
            'bg': '#4A90D9',
            'fg': 'white',
            'activebackground': '#357ABD',
            'activeforeground': 'white',
            'relief': 'flat',
            'cursor': 'hand2',
            'width': 20,
            'pady': 8
        }

        # Quick action buttons
        ask_btn = tk.Button(
            buttons_frame,
            text="💬 Ask PrePanda",
            command=self.show_ask_dialog,
            **button_style
        )
        ask_btn.pack(fill=tk.X, pady=3)

        improve_btn = tk.Button(
            buttons_frame,
            text="✨ Improve Writing",
            command=lambda: self.send_command("improve"),
            **button_style
        )
        improve_btn.pack(fill=tk.X, pady=3)

        proofread_btn = tk.Button(
            buttons_frame,
            text="📝 Proofread",
            command=lambda: self.send_command("proofread"),
            **button_style
        )
        proofread_btn.pack(fill=tk.X, pady=3)

        # Help text
        help_label = tk.Label(
            main_frame,
            text="Select text in PreOffice first,\nthen click an action above.",
            font=('Helvetica', 10),
            bg='#ffffff',
            fg='#888888',
            justify=tk.CENTER
        )
        help_label.pack(pady=(15, 0))

    def show_ask_dialog(self):
        """Show a dialog to ask PrePanda a question."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ask PrePanda")
        dialog.geometry("400x200")
        dialog.attributes('-topmost', True)
        dialog.configure(bg='#ffffff')

        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()

        frame = tk.Frame(dialog, bg='#ffffff', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        label = tk.Label(
            frame,
            text="What would you like help with?",
            font=('Helvetica', 12),
            bg='#ffffff'
        )
        label.pack(anchor=tk.W)

        # Text entry
        text_entry = tk.Text(frame, height=4, font=('Helvetica', 12))
        text_entry.pack(fill=tk.X, pady=10)
        text_entry.focus_set()

        def submit():
            question = text_entry.get("1.0", tk.END).strip()
            if question:
                self.send_command("ask", question)
                dialog.destroy()

        submit_btn = tk.Button(
            frame,
            text="Ask",
            command=submit,
            font=('Helvetica', 12),
            bg='#4A90D9',
            fg='white',
            relief='flat',
            padx=20,
            pady=5
        )
        submit_btn.pack(pady=5)

        # Bind Enter key
        dialog.bind('<Return>', lambda e: submit())

    def send_command(self, action, data=None):
        """Send a command to PreOffice."""
        command = {
            "action": action,
            "data": data,
            "timestamp": time.time()
        }
        try:
            with open(COMMAND_FILE, 'w') as f:
                json.dump(command, f)
            # Show feedback
            self.show_notification(f"Sent '{action}' command to PreOffice")
        except Exception as e:
            messagebox.showerror("Error", f"Could not send command: {e}")

    def show_notification(self, message):
        """Show a brief notification."""
        # Create a temporary label that fades out
        notif = tk.Toplevel(self.root)
        notif.overrideredirect(True)
        notif.attributes('-topmost', True)

        # Position near the main window
        x = self.root.winfo_x() + 20
        y = self.root.winfo_y() + self.root.winfo_height() - 50
        notif.geometry(f"+{x}+{y}")

        label = tk.Label(
            notif,
            text=message,
            font=('Helvetica', 11),
            bg='#333333',
            fg='white',
            padx=15,
            pady=8
        )
        label.pack()

        # Auto-close after 2 seconds
        notif.after(2000, notif.destroy)

    def listen_for_commands(self):
        """Listen for responses from PreOffice."""
        while self.running:
            try:
                if os.path.exists(RESPONSE_FILE):
                    with open(RESPONSE_FILE, 'r') as f:
                        response = json.load(f)
                    os.remove(RESPONSE_FILE)

                    # Handle response in main thread
                    self.root.after(0, lambda r=response: self.handle_response(r))
            except Exception:
                pass
            time.sleep(0.5)

    def handle_response(self, response):
        """Handle a response from PreOffice."""
        if response.get("type") == "result":
            # Show result in a dialog
            result_dialog = tk.Toplevel(self.root)
            result_dialog.title("PrePanda Result")
            result_dialog.geometry("500x400")
            result_dialog.attributes('-topmost', True)

            text = tk.Text(result_dialog, wrap=tk.WORD, font=('Helvetica', 12))
            text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text.insert("1.0", response.get("content", ""))
            text.config(state=tk.DISABLED)

    def on_close(self):
        """Handle window close - minimize to background instead of quitting."""
        self.root.withdraw()  # Hide window
        # Show again after a delay (for demo) or via system tray
        self.root.after(3000, self.root.deiconify)

    def run(self):
        """Run the helper application."""
        self.root.mainloop()
        self.running = False


def main():
    app = PrePandaHelper()
    app.run()


if __name__ == "__main__":
    main()
