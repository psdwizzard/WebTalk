#!/usr/bin/env python3
"""
WebTalk Settings Desktop App
Beautiful desktop settings interface matching the Chrome extension aesthetic.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import threading
import requests
from typing import Dict, Any
import subprocess
import sys

class ModernFrame(tk.Frame):
    """Custom frame with gradient-like background"""
    def __init__(self, parent, bg_color="#8E2DE2", **kwargs):
        super().__init__(parent, bg=bg_color, **kwargs)

class ModernEntry(tk.Entry):
    """Custom entry with modern styling"""
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            font=("Segoe UI", 11),
            bg="#4A00E0",
            fg="white",
            insertbackground="white",
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightcolor="#FF4081",
            highlightbackground="#9CA3AF",
            **kwargs
        )

class WebTalkSettingsApp:
    def __init__(self):
        self.root = tk.Tk()
        self.config_file = "webtalk_config.json"
        self.server_url = "http://localhost:8000"
        
        # Default configuration
        self.config = {
            "compute_engine": "gpu",
            "model": "base",
            "microphone": "default",
            "server_port": 8000,
            "auth_key": "",
            "openai_api_key": ""
        }
        
        self.load_config()
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("WebTalk Server Settings")
        self.root.geometry("400x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#1F2937")  # Dark background
        
        # Center the window
        self.center_window()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (650 // 2)
        self.root.geometry(f"400x650+{x}+{y}")
        
    def create_widgets(self):
        """Create all the UI widgets with modern design"""
        # Main container with padding
        main_container = tk.Frame(self.root, bg="#1F2937")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Settings container with gradient-like background and rounded appearance
        self.settings_container = tk.Frame(
            main_container,
            bg="#8E2DE2",  # Purple gradient start
            relief="flat",
            bd=0
        )
        self.settings_container.pack(fill=tk.BOTH, expand=True)
        
        # Add padding inside the container
        content_frame = tk.Frame(self.settings_container, bg="#8E2DE2")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)
        
        # Header with icon and title
        self.create_header(content_frame)
        
        # Compute Engine Section
        self.create_compute_engine_section(content_frame)
        
        # Model Selector Section
        self.create_model_section(content_frame)
        
        # Microphone Selector Section
        self.create_microphone_section(content_frame)
        
        # Server Port Section
        self.create_port_section(content_frame)
        
        # Authentication Key Section
        self.create_auth_section(content_frame)
        
        # OpenAI API Key Section
        self.create_openai_section(content_frame)
        
        # Save Button
        self.create_save_button(content_frame)
        
        # Status/Alert Message
        self.create_status_section(content_frame)
        
    def create_header(self, parent):
        """Create the header with icon and title"""
        header_frame = tk.Frame(parent, bg="#8E2DE2")
        header_frame.pack(fill=tk.X, pady=(0, 24))
        
        # Icon (using emoji as placeholder for the settings icon)
        icon_label = tk.Label(
            header_frame,
            text="⚙️",
            font=("Segoe UI", 20),
            bg="#8E2DE2",
            fg="white"
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 12))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="WebTalk Server Settings",
            font=("Segoe UI", 18, "bold"),
            bg="#8E2DE2",
            fg="white"
        )
        title_label.pack(side=tk.LEFT)
        
    def create_input_group(self, parent, label_text, widget_type="entry", values=None, show_icon=True, icon="⚙️"):
        """Create a modern input group with label and styled input"""
        # Input group container
        group_frame = tk.Frame(parent, bg="#8E2DE2")
        group_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Label
        label = tk.Label(
            group_frame,
            text=label_text,
            font=("Segoe UI", 11, "normal"),
            bg="#8E2DE2",
            fg="#E5E7EB"
        )
        label.pack(anchor="w", pady=(0, 8))
        
        # Input container with icon
        input_container = tk.Frame(group_frame, bg="#8E2DE2")
        input_container.pack(fill=tk.X)
        
        if widget_type == "entry":
            # Entry field with modern styling
            entry = tk.Entry(
                input_container,
                font=("Segoe UI", 11),
                bg="#4A00E0",  # Darker purple for input background
                fg="white",
                insertbackground="white",
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightcolor="#FF4081",
                highlightbackground="#9CA3AF"
            )
            entry.pack(fill=tk.X, ipady=8, ipadx=12)
            return entry
            
        elif widget_type == "combobox":
            # Custom styled combobox
            style = ttk.Style()
            style.configure(
                "Modern.TCombobox",
                fieldbackground="#4A00E0",
                background="#4A00E0",
                foreground="white",
                arrowcolor="white",
                bordercolor="#9CA3AF",
                lightcolor="#4A00E0",
                darkcolor="#4A00E0",
                selectbackground="#FF4081",
                selectforeground="white"
            )
            
            combobox = ttk.Combobox(
                input_container,
                values=values or [],
                state="readonly",
                font=("Segoe UI", 11),
                style="Modern.TCombobox"
            )
            combobox.pack(fill=tk.X, ipady=4)
            return combobox
            
    def create_compute_engine_section(self, parent):
        """Create the compute engine toggle section"""
        # Section container
        section_frame = tk.Frame(parent, bg="#8E2DE2")
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Label
        label = tk.Label(
            section_frame,
            text="Compute Engine",
            font=("Segoe UI", 11, "normal"),
            bg="#8E2DE2",
            fg="#E5E7EB"
        )
        label.pack(anchor="w", pady=(0, 8))
        
        # Toggle container with modern styling
        toggle_container = tk.Frame(
            section_frame,
            bg="#4A00E0",
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightcolor="#9CA3AF",
            highlightbackground="#9CA3AF"
        )
        toggle_container.pack(fill=tk.X, ipady=8, ipadx=12)
        
        # GPU/CPU toggle using radiobuttons styled as toggle
        self.compute_var = tk.StringVar(value=self.config["compute_engine"])
        
        gpu_label = tk.Label(
            toggle_container,
            text="GPU",
            font=("Segoe UI", 11, "bold"),
            bg="#4A00E0",
            fg="white"
        )
        gpu_label.pack(side=tk.LEFT)
        
        # Toggle switch (simplified as radiobuttons for now)
        toggle_frame = tk.Frame(toggle_container, bg="#4A00E0")
        toggle_frame.pack(side=tk.RIGHT)
        
        cpu_label = tk.Label(
            toggle_container,
            text="CPU",
            font=("Segoe UI", 11, "bold"),
            bg="#4A00E0",
            fg="white"
        )
        cpu_label.pack(side=tk.RIGHT, padx=(20, 0))
        
        # Hidden radiobuttons for functionality
        self.gpu_radio = tk.Radiobutton(
            toggle_frame,
            variable=self.compute_var,
            value="gpu",
            bg="#4A00E0",
            fg="white",
            selectcolor="#FF4081",
            activebackground="#4A00E0"
        )
        self.gpu_radio.pack(side=tk.LEFT)
        
        self.cpu_radio = tk.Radiobutton(
            toggle_frame,
            variable=self.compute_var,
            value="cpu",
            bg="#4A00E0",
            fg="white",
            selectcolor="#FF4081",
            activebackground="#4A00E0"
        )
        self.cpu_radio.pack(side=tk.LEFT)
        
    def create_model_section(self, parent):
        """Create the model selector section"""
        self.model_var = tk.StringVar(value=self.config["model"])
        self.model_combo = self.create_input_group(
            parent,
            "Model Selector",
            "combobox",
            ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3", "turbo"],
            icon="🎛️"
        )
        self.model_combo.set(self.config["model"])
        
    def create_microphone_section(self, parent):
        """Create the microphone selector section"""
        self.mic_var = tk.StringVar(value=self.config["microphone"])
        self.mic_combo = self.create_input_group(
            parent,
            "Microphone Selector",
            "combobox",
            ["default", "Default Microphone", "Microphone 1 (USB)", "Microphone 2 (Built-in)"],
            icon="🎤"
        )
        self.mic_combo.set(self.config["microphone"])
        
    def create_port_section(self, parent):
        """Create the server port section"""
        self.port_var = tk.StringVar(value=str(self.config["server_port"]))
        self.port_entry = self.create_input_group(
            parent,
            "Server Port",
            "entry",
            icon="🔌"
        )
        self.port_entry.configure(textvariable=self.port_var)
        
    def create_auth_section(self, parent):
        """Create the authentication key section"""
        self.auth_var = tk.StringVar(value=self.config["auth_key"])
        self.auth_entry = self.create_input_group(
            parent,
            "Authentication Key (Optional)",
            "entry",
            icon="🔑"
        )
        self.auth_entry.configure(textvariable=self.auth_var, show="*" if self.config["auth_key"] else "")
        
    def create_openai_section(self, parent):
        """Create the OpenAI API key section"""
        # Section container
        section_frame = tk.Frame(parent, bg="#8E2DE2")
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Label
        label = tk.Label(
            section_frame,
            text="OpenAI API Key (Fallback)",
            font=("Segoe UI", 11, "normal"),
            bg="#8E2DE2",
            fg="#E5E7EB"
        )
        label.pack(anchor="w", pady=(0, 8))
        
        # Entry field
        self.openai_var = tk.StringVar(value=self.config["openai_api_key"])
        self.openai_entry = tk.Entry(
            section_frame,
            textvariable=self.openai_var,
            font=("Segoe UI", 11),
            bg="#4A00E0",
            fg="white",
            insertbackground="white",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightcolor="#FF4081",
            highlightbackground="#9CA3AF",
            show="*" if self.config["openai_api_key"] else ""
        )
        self.openai_entry.pack(fill=tk.X, ipady=8, ipadx=12)
        
        # Description
        desc_label = tk.Label(
            section_frame,
            text="Used if local hardware is insufficient.",
            font=("Segoe UI", 9),
            bg="#8E2DE2",
            fg="#D1D5DB"
        )
        desc_label.pack(anchor="w", pady=(8, 0))
        
    def create_save_button(self, parent):
        """Create the save button with modern styling"""
        button_frame = tk.Frame(parent, bg="#8E2DE2")
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.save_button = tk.Button(
            button_frame,
            text="💾 Save & Apply Settings",
            command=self.save_settings,
            font=("Segoe UI", 12, "bold"),
            bg="#FF4081",
            fg="white",
            activebackground="#F50057",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            pady=12
        )
        self.save_button.pack(fill=tk.X)
        
        # Hover effects (simplified)
        def on_enter(e):
            self.save_button.configure(bg="#F50057")
        def on_leave(e):
            self.save_button.configure(bg="#FF4081")
            
        self.save_button.bind("<Enter>", on_enter)
        self.save_button.bind("<Leave>", on_leave)
        
    def create_status_section(self, parent):
        """Create the status/alert message section"""
        self.status_label = tk.Label(
            parent,
            text="",
            font=("Segoe UI", 10),
            bg="#8E2DE2",
            fg="#D1D5DB"
        )
        self.status_label.pack(pady=(16, 0))
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
        except Exception as e:
            print(f"Error loading config: {e}")
            
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def save_settings(self):
        """Save all settings and update server"""
        try:
            # Update config with current values
            self.config["compute_engine"] = self.compute_var.get()
            self.config["model"] = self.model_combo.get()
            self.config["microphone"] = self.mic_combo.get()
            self.config["server_port"] = int(self.port_var.get())
            self.config["auth_key"] = self.auth_var.get()
            self.config["openai_api_key"] = self.openai_var.get()
            
            # Save to file
            self.save_config()
            
            # Try to update running server
            self.update_server_config()
            
            # Show restart alert
            self.status_label.config(
                text="⚠️ Restart server for changes to take effect.",
                fg="#F3F4F6"
            )
            
        except ValueError:
            messagebox.showerror("Error", "Server port must be a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            
    def update_server_config(self):
        """Send updated config to running server"""
        try:
            response = requests.post(
                f"{self.server_url}/config",
                json=self.config,
                timeout=5
            )
            if response.status_code == 200:
                self.status_label.config(
                    text="✅ Settings applied to running server!",
                    fg="#A7F3D0"
                )
            else:
                self.status_label.config(
                    text="⚠️ Settings saved (server will use on next restart)",
                    fg="#F3F4F6"
                )
        except requests.exceptions.RequestException:
            self.status_label.config(
                text="⚠️ Settings saved (server not running)",
                fg="#F3F4F6"
            )
            
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    app = WebTalkSettingsApp()
    app.run()

if __name__ == "__main__":
    main() 