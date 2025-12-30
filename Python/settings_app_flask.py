#!/usr/bin/env python3
"""
WebTalk Settings Desktop App - Flask + PyWebView Version
Beautiful desktop settings interface using the original HTML design.
"""

import json
import threading
import time
from pathlib import Path
from typing import Dict, Any
import requests
import webview
from flask import Flask, render_template_string, request, jsonify
import ctypes
from ctypes import wintypes

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
IMAGES_DIR = PROJECT_ROOT / "Images"
CONFIG_FILE = PROJECT_ROOT / "webtalk_config.json"

class WebTalkSettingsApp:
    def __init__(self):
        self.config_file = CONFIG_FILE
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
        self.app = Flask(__name__)
        self.setup_routes()
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with self.config_file.open('r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
        except Exception as e:
            print(f"Error loading config: {e}")
            
    def save_config(self):
        """Save configuration to file"""
        try:
            with self.config_file.open('w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Serve the main settings page"""
            response = render_template_string(self.get_html_template(), config=self.config)
            resp = self.app.response_class(response)
            resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp
        
        @self.app.route('/desktalk')
        def desktalk():
            """Serve the DeskTalk recorder page"""
            response = render_template_string(self.get_desktalk_template(), config=self.config)
            resp = self.app.response_class(response)
            resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp
        
        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            """Get current configuration"""
            return jsonify(self.config)
        
        @self.app.route('/api/config', methods=['POST'])
        def save_settings():
            """Save settings from the UI"""
            try:
                data = request.get_json()
                
                # Update config with new values
                self.config.update({
                    "compute_engine": data.get("compute_engine", "gpu"),
                    "model": data.get("model", "base"),
                    "microphone": data.get("microphone", "default"),
                    "server_port": int(data.get("server_port", 8000)),
                    "auth_key": data.get("auth_key", ""),
                    "openai_api_key": data.get("openai_api_key", "")
                })
                
                # Save to file
                self.save_config()
                
                # Try to update running server
                server_status = self.update_server_config()
                
                return jsonify({
                    "success": True,
                    "message": "Settings saved successfully!",
                    "server_status": server_status
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": f"Error saving settings: {str(e)}"
                }), 500
        
        @self.app.route('/api/microphones', methods=['GET'])
        def get_microphones():
            """Get available microphones"""
            # This could be expanded to actually detect system microphones
            return jsonify([
                {"value": "default", "label": "Default Microphone"},
                {"value": "mic1", "label": "Microphone 1 (USB)"},
                {"value": "mic2", "label": "Microphone 2 (Built-in)"}
            ])
        
        @self.app.route('/WebTalk.png')
        def serve_logo():
            """Serve the WebTalk logo"""
            from flask import send_file
            logo_path = IMAGES_DIR / "WebTalk.png"
            if logo_path.exists():
                return send_file(logo_path, mimetype='image/png')
            else:
                return '', 404

        @self.app.route('/Robot.png')
        def serve_robot():
            """Serve the DeskTalk robot illustration"""
            from flask import send_file
            robot_path = IMAGES_DIR / "Robot.png"
            if robot_path.exists():
                return send_file(robot_path, mimetype='image/png')
            return '', 404
            
    def update_server_config(self):
        """Send updated config to running server"""
        try:
            response = requests.post(
                f"{self.server_url}/config",
                json=self.config,
                timeout=5
            )
            if response.status_code == 200:
                return "running"
            else:
                return "restart_needed"
        except requests.exceptions.RequestException:
            return "not_running"
    
    def get_html_template(self):
        """Return the HTML template with embedded CSS and JavaScript"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>WebTalk Server Settings</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Icons" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet"/>
                    <style>
        :root {
            --wt-bg: #0f172a;
            --wt-surface: #111c2e;
            --wt-panel: rgba(17, 24, 39, 0.85);
            --wt-panel-solid: #161f2f;
            --wt-border: rgba(148, 163, 184, 0.16);
            --wt-border-strong: rgba(148, 163, 184, 0.32);
            --wt-text: #e2e8f0;
            --wt-text-muted: rgba(226, 232, 240, 0.7);
            --wt-heading: #f8fafc;
            --wt-accent: #2563eb;
            --wt-accent-soft: #3b82f6;
            --wt-accent-deep: #1d4ed8;
            --wt-highlight: #10b981;
            --wt-highlight-soft: rgba(16, 185, 129, 0.18);
            --wt-danger: #f87171;
        }

        html {
            height: 100%;
        }
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 0;
            background: radial-gradient(circle at 20% 20%, #111c2e 0%, #0b1120 55%, #05070f 100%);
            color: var(--wt-text);
            overflow: hidden;
            height: 100%;
        }

        .settings-container {
            width: 100%;
            background: linear-gradient(160deg, rgba(15, 23, 42, 0.96) 0%, rgba(8, 11, 21, 0.96) 65%, rgba(5, 8, 15, 0.96) 100%);
            color: var(--wt-text);
            border-radius: 0;
            padding: 24px;
            box-sizing: border-box;
            height: 100vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .tab-container {
            display: flex;
            margin-bottom: 24px;
            background: rgba(15, 23, 42, 0.82);
            border-radius: 12px;
            padding: 6px;
            border: 1px solid var(--wt-border);
            box-shadow: 0 18px 40px rgba(8, 11, 21, 0.45);
        }
        .tab-button {
            flex: 1;
            padding: 14px 24px;
            border: none;
            background: transparent;
            color: var(--wt-text-muted);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            font-size: 1rem;
            text-align: center;
        }
        .tab-button.active {
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.85) 0%, rgba(16, 185, 129, 0.75) 100%);
            color: var(--wt-heading);
            box-shadow: 0 12px 28px rgba(37, 99, 235, 0.35);
            transform: translateY(-1px);
        }
        .tab-button:hover {
            background: rgba(37, 99, 235, 0.14);
            color: var(--wt-heading);
            transform: translateY(-1px);
        }

        .tab-content {
            display: none;
            flex: 1;
            flex-direction: column;
            min-height: 0;
            overflow: hidden;
        }

        .tab-content.active {
            display: flex;
        }

        .tab-content iframe {
            flex: 1;
            min-height: 0;
        }

        .input-group {
            margin-bottom: 20px;
        }
        .input-group label {
            display: block;
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 8px;
            color: var(--wt-text-muted);
        }
        .input-field, .select-field {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            background-color: rgba(15, 23, 42, 0.85);
            border: 1px solid var(--wt-border);
            color: var(--wt-text);
            font-size: 0.9rem;
            transition: background-color 0.3s, border-color 0.3s, box-shadow 0.3s;
            box-sizing: border-box;
            box-shadow: 0 10px 24px rgba(8, 11, 21, 0.35);
        }
        .input-field:focus, .select-field:focus {
            outline: none;
            background-color: rgba(15, 23, 42, 0.95);
            border-color: rgba(59, 130, 246, 0.6);
            box-shadow: 0 12px 28px rgba(37, 99, 235, 0.32);
        }
        .input-field::placeholder {
            color: var(--wt-text-muted);
        }
        .select-field option {
            color: #0f172a;
        }
        .btn {
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.3s, filter 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            border: none;
            width: 100%;
            letter-spacing: 0.01em;
        }
        .btn-primary {
            background: linear-gradient(135deg, var(--wt-accent) 0%, var(--wt-accent-soft) 48%, var(--wt-highlight) 100%);
            color: var(--wt-heading);
            box-shadow: 0 18px 38px rgba(37, 99, 235, 0.35);
        }
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 22px 42px rgba(37, 99, 235, 0.45);
            filter: brightness(1.05);
        }
        .btn-primary:active {
            transform: translateY(0);
            box-shadow: 0 12px 24px rgba(37, 99, 235, 0.32);
        }
        .alert-message {
            font-size: 0.8rem;
            color: var(--wt-text-muted);
            margin-top: 8px;
            text-align: center;
        }
        .header {
            display: flex;
            align-items: center;
            margin-bottom: 24px;
        }
        .header-icon {
            width: 32px;
            height: 32px;
            margin-right: 12px;
            background-image: url("WebTalk.png");
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
        }
        .header-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--wt-heading);
        }
        .icon-input-group {
            position: relative;
        }
        .icon-input-group .material-icons {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: rgba(226, 232, 240, 0.45);
            font-size: 1.25rem;
        }
        .icon-input-group .input-field,
        .icon-input-group .select-field {
            padding-left: 44px;
        }
        .toggle-switch-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 16px;
            border-radius: 12px;
            background-color: rgba(15, 23, 42, 0.85);
            border: 1px solid var(--wt-border);
            box-shadow: 0 12px 26px rgba(8, 11, 21, 0.4);
        }
        .toggle-switch {
            position: relative;
            display: inline-block;
            width: 52px;
            height: 28px;
        }
        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(59, 76, 105, 0.6);
            transition: .4s;
            border-radius: 28px;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 20px;
            width: 20px;
            left: 4px;
            bottom: 4px;
            background-color: var(--wt-heading);
            transition: .4s;
            border-radius: 50%;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.5);
        }
        input:checked + .slider {
            background: linear-gradient(135deg, var(--wt-accent) 0%, var(--wt-highlight) 100%);
            box-shadow: inset 0 0 14px rgba(37, 99, 235, 0.35);
        }
        input:focus + .slider {
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.35);
        }
        input:checked + .slider:before {
            transform: translateX(22px);
        }
        .toggle-label {
            color: var(--wt-text-muted);
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="settings-container">
        <div class="header">
            <div class="header-icon"></div>
            <h1 class="header-title">WebTalk Server Settings</h1>
        </div>
        
        <!-- Tab Navigation -->
        <div class="tab-container">
            <button class="tab-button active" type="button" data-tab="desktalk" onclick="switchTab('desktalk')">DeskTalk</button>
            <button class="tab-button" type="button" data-tab="settings" onclick="switchTab('settings')">Settings</button>
        </div>
        
        <!-- Settings Tab Content -->
        <div id="settings-tab" class="tab-content">
            <div class="input-group">
                <label for="compute-engine">Compute Engine</label>
                <div class="toggle-switch-container">
                    <span class="toggle-label">CPU</span>
                    <label class="toggle-switch">
                        <input id="compute-engine-toggle" type="checkbox" {{ 'checked' if config.compute_engine == 'gpu' else '' }}/>
                        <span class="slider round"></span>
                    </label>
                    <span class="toggle-label">GPU</span>
                </div>
            </div>
            
            <div class="input-group">
                <label for="model-selector">Model Selector</label>
                <div class="icon-input-group">
                    <span class="material-icons">tune</span>
                    <select class="select-field" id="model-selector">
                        <option value="tiny" {{ 'selected' if config.model == 'tiny' else '' }}>Tiny</option>
                        <option value="base" {{ 'selected' if config.model == 'base' else '' }}>Base</option>
                        <option value="small" {{ 'selected' if config.model == 'small' else '' }}>Small</option>
                        <option value="medium" {{ 'selected' if config.model == 'medium' else '' }}>Medium</option>
                        <option value="large" {{ 'selected' if config.model == 'large' else '' }}>Large</option>
                        <option value="large-v2" {{ 'selected' if config.model == 'large-v2' else '' }}>Large-v2</option>
                        <option value="large-v3" {{ 'selected' if config.model == 'large-v3' else '' }}>Large-v3</option>
                        <option value="turbo" {{ 'selected' if config.model == 'turbo' else '' }}>Turbo</option>
                    </select>
                </div>
            </div>
            
            <div class="input-group">
                <label for="microphone-selector">Microphone Selector</label>
                <div class="icon-input-group">
                    <span class="material-icons">mic</span>
                    <select class="select-field" id="microphone-selector">
                        <option value="default" {{ 'selected' if config.microphone == 'default' else '' }}>Default Microphone</option>
                        <option value="mic1" {{ 'selected' if config.microphone == 'mic1' else '' }}>Microphone 1 (USB)</option>
                        <option value="mic2" {{ 'selected' if config.microphone == 'mic2' else '' }}>Microphone 2 (Built-in)</option>
                    </select>
                </div>
            </div>
            
            <button class="btn btn-primary" id="save-apply-button">
                <span class="material-icons mr-2">save</span>
                Save & Apply Settings
            </button>
            
            <p class="alert-message" id="restart-alert" style="display: none;">
                <span class="material-icons text-sm mr-1 align-middle">warning</span>
                Restart server for changes to take effect.
            </p>
        </div>
        
        <!-- DeskTalk Tab Content -->
        <div id="desktalk-tab" class="tab-content">
            <iframe src="/desktalk?v=11" style="width: 100%; height: 100%; border: none; border-radius: 12px;"></iframe>
        </div>
    </div>

    <script>
        function switchTab(tabName) {
            console.log('Switching to tab:', tabName);
            
            // Hide all tab contents (remove active class)
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
                console.log('Hiding tab:', tab.id);
            });
            
            // Remove active class from all tab buttons
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected tab content (add active class)
            const targetTab = document.getElementById(tabName + '-tab');
            if (targetTab) {
                targetTab.classList.add('active');
                console.log('Showing tab:', targetTab.id);
            } else {
                console.error('Tab not found:', tabName + '-tab');
            }
            
            // Add active class to clicked button
            const targetButton = document.querySelector('.tab-button[data-tab="' + tabName + '"]');
            if (targetButton) {
                targetButton.classList.add('active');
            }
            console.log('Tab switch completed');
        }

        window.switchTab = switchTab;

        function initializeTabs() {
            console.log('Initializing tab interface');

            // Set up tab button click handlers
            const tabButtons = document.querySelectorAll('.tab-button');
            if (tabButtons.length) {
                tabButtons.forEach(btn => {
                    const target = btn.getAttribute('data-tab');
                    if (target) {
                        btn.addEventListener('click', () => switchTab(target));
                        btn.setAttribute('role', 'tab');
                    }
                });

                // Switch to the default tab (DeskTalk)
                const defaultTab = tabButtons[0].getAttribute('data-tab') || 'desktalk';
                switchTab(defaultTab);
                console.log('Default tab activated:', defaultTab);
            }
        }

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initializeTabs);
        } else {
            initializeTabs();
        }

        const saveButton = document.getElementById('save-apply-button');
        const restartAlert = document.getElementById('restart-alert');
        const inputs = document.querySelectorAll('.input-field, .select-field, #compute-engine-toggle');
        
        let initialValues = {};
        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                initialValues[input.id] = input.checked;
            } else {
                initialValues[input.id] = input.value;
            }
        });

        const checkForChanges = () => {
            let changed = false;
            inputs.forEach(input => {
                const currentValue = input.type === 'checkbox' ? input.checked : input.value;
                if (currentValue !== initialValues[input.id]) {
                    changed = true;
                }
            });
            return changed;
        };

        saveButton.addEventListener('click', async () => {
            try {
                const computeToggle = document.getElementById('compute-engine-toggle');
                const data = {
                    compute_engine: computeToggle.checked ? 'gpu' : 'cpu',
                    model: document.getElementById('model-selector').value,
                    microphone: document.getElementById('microphone-selector').value
                };
                
                console.log('Toggle checked:', computeToggle.checked);
                console.log('Compute engine:', data.compute_engine);
                console.log('Saving configuration:', data);

                const response = await fetch('/api/config', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                
                if (result.success) {
                    if (checkForChanges() || result.server_status !== 'running') {
                        restartAlert.style.display = 'block';
                        restartAlert.innerHTML = '<span class="material-icons text-sm mr-1 align-middle">warning</span> Restart server for changes to take effect.';
                    } else {
                        restartAlert.style.display = 'block';
                        restartAlert.innerHTML = '<span class="material-icons text-sm mr-1 align-middle">check_circle</span> Settings saved successfully!';
                        restartAlert.style.color = '#34D399';
                    }
                    
                    // Update initial values
                    inputs.forEach(input => {
                        if (input.type === 'checkbox') {
                            initialValues[input.id] = input.checked;
                        } else {
                            initialValues[input.id] = input.value;
                        }
                    });
                } else {
                    alert('Error saving settings: ' + result.message);
                }
            } catch (error) {
                alert('Error saving settings: ' + error.message);
            }
        });

        // Hide restart alert if no changes are made on subsequent clicks
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                if (!checkForChanges()) {
                    restartAlert.style.display = 'none';
                }
            });
        });

        // Handle compute engine toggle
        const computeToggle = document.getElementById('compute-engine-toggle');
        if (computeToggle) {
            computeToggle.addEventListener('change', () => {
                const selectedEngine = computeToggle.checked ? 'GPU' : 'CPU';
                console.log('Compute Engine set to:', selectedEngine);

                if (initialValues[computeToggle.id] !== computeToggle.checked) {
                    restartAlert.style.display = 'block';
                } else if (!checkForChanges()) {
                    restartAlert.style.display = 'none';
                }
            });
        }
</script>
</body>
</html>
        '''
    def get_desktalk_template(self):
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>DeskTalk Recorder</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet"/>
    <style>
        :root {
            --wt-bg: #0f172a;
            --wt-surface: rgba(17, 24, 39, 0.92);
            --wt-panel: rgba(15, 23, 42, 0.88);
            --wt-border: rgba(148, 163, 184, 0.18);
            --wt-border-strong: rgba(148, 163, 184, 0.28);
            --wt-text: #e2e8f0;
            --wt-text-muted: rgba(226, 232, 240, 0.68);
            --wt-heading: #f8fafc;
            --wt-accent: #2563eb;
            --wt-accent-soft: #3b82f6;
            --wt-accent-deep: #1d4ed8;
            --wt-highlight: #10b981;
            --wt-danger: #f87171;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html {
            height: 100%;
            overflow: hidden;
        }

        body {
            font-family: 'Roboto', sans-serif;
            background: radial-gradient(circle at 35% 15%, #111c2e 0%, #0b1324 55%, #050a18 100%);
            height: 100%;
            margin: 0;
            padding: 0;
            display: flex;
            align-items: stretch;
            justify-content: stretch;
            color: var(--wt-text);
            overflow: hidden;
        }

        .desk-container {
            position: relative;
            height: 100%;
            width: 100%;
            background: var(--wt-surface);
            border-radius: 0;
            padding: 8px;
            border: none;
            box-shadow: none;
            display: flex;
            flex-direction: column;
            gap: 8px;
            overflow: hidden;
            box-sizing: border-box;
        }

        .desk-header {
            text-align: center;
            margin-bottom: 0;
            flex-shrink: 0;
        }

        .desk-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--wt-heading);
            margin: 0;
        }

        .desk-subtitle {
            margin-top: 2px;
            font-size: 0.75rem;
            color: var(--wt-text-muted);
        }

        .desk-body {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 8px;
            min-height: 0;
        }

        .record-area {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 8px;
            flex-shrink: 0;
            padding: 8px;
        }

        .record-button {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            border: none;
            color: var(--wt-heading);
            font-size: 1.5rem;
            font-weight: 600;
            cursor: pointer;
            background: linear-gradient(135deg, var(--wt-accent) 0%, var(--wt-accent-soft) 55%, var(--wt-highlight) 100%);
            box-shadow: 0 15px 30px rgba(37, 99, 235, 0.42);
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }

        .record-button:hover {
            transform: scale(1.05);
            box-shadow: 0 34px 65px rgba(37, 99, 235, 0.5);
        }

        .record-button.recording {
            background: linear-gradient(135deg, var(--wt-accent-soft) 0%, var(--wt-accent-deep) 100%);
            animation: pulse 2.1s infinite;
        }

        .record-button.processing {
            background: linear-gradient(135deg, var(--wt-highlight) 0%, #0ea371 100%);
            box-shadow: 0 26px 48px rgba(16, 185, 129, 0.4);
            cursor: not-allowed;
        }

        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 28px 55px rgba(37, 99, 235, 0.4); }
            50% { transform: scale(1.07); box-shadow: 0 34px 70px rgba(59, 130, 246, 0.55); }
            100% { transform: scale(1); box-shadow: 0 28px 55px rgba(37, 99, 235, 0.4); }
        }

        .control-row {
            display: flex;
            gap: 12px;
            justify-content: center;
            width: min(280px, 100%);
        }

        .control-btn {
            flex: 1;
            min-width: 100px;
            border-radius: 14px;
            padding: 10px 14px;
            font-weight: 600;
            border: none;
            cursor: pointer;
            background: rgba(30, 41, 59, 0.82);
            color: var(--wt-text);
            box-shadow: 0 16px 34px rgba(5, 10, 18, 0.45);
            transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
        }

        .control-btn:hover {
            transform: translateY(-2px);
            background: rgba(37, 99, 235, 0.22);
            box-shadow: 0 20px 40px rgba(5, 10, 18, 0.5);
        }

        .control-btn.primary {
            background: linear-gradient(135deg, var(--wt-accent) 0%, var(--wt-highlight) 100%);
            color: var(--wt-heading);
        }

        .status-message {
            text-align: center;
            font-size: 0.8rem;
            color: var(--wt-text-muted);
            min-height: 18px;
        }

        .transcription-card {
            padding: 10px;
            border-radius: 12px;
            background: var(--wt-panel);
            border: 1px solid var(--wt-border);
            box-shadow: inset 0 0 0 1px rgba(59, 130, 246, 0.08);
            flex: 1;
            position: relative;
            display: flex;
            flex-direction: column;
            gap: 5px;
            overflow: hidden;
            min-height: 0;
        }

        .transcription-placeholder {
            text-align: center;
            font-style: italic;
            color: var(--wt-text-muted);
            margin: auto;
            padding: 0 12px;
        }

        .transcription-text {
            line-height: 1.6;
            font-size: 1rem;
            cursor: context-menu;
            flex: 1;
            overflow-y: auto;
            padding-right: 4px;
        }

        .hint {
            margin-top: auto;
            text-align: left;
            font-size: 0.8rem;
            color: var(--wt-text-muted);
            display: flex;
            flex-direction: row;
            align-items: flex-end;
            justify-content: space-between;
            gap: 12px;
            padding: 8px 6px 12px;
        }
        .hint .hint-text {
            align-self: flex-end;
        }
        .hint .robot-illustration {
            width: 150px;
            opacity: 0.95;
            pointer-events: none;
        }

        .alert {
            position: absolute;
            bottom: 20px;
            left: 20px;
            right: 20px;
            padding: 14px 16px;
            border-radius: 12px;
            font-size: 0.9rem;
            display: none;
            z-index: 100;
        }

        .alert.error {
            background: rgba(248, 113, 113, 0.12);
            border: 1px solid rgba(248, 113, 113, 0.4);
            color: var(--wt-danger);
        }

        .alert.success {
            background: rgba(16, 185, 129, 0.16);
            border: 1px solid rgba(16, 185, 129, 0.38);
            color: var(--wt-highlight);
        }

        @media (max-width: 520px) {
            .desk-container {
                padding: 28px 20px;
            }

            .control-row {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="desk-container">
        <div class="desk-header">
            <h1 class="desk-title">DeskTalk</h1>
            <p class="desk-subtitle">Desktop voice transcription companion</p>
        </div>

        <div class="desk-body">
            <div class="record-area">
                <button class="record-button" id="recordButton">●</button>
                <div class="control-row" id="controlRow" style="display: none;">
                    <button class="control-btn" id="stopButton">Stop</button>
                    <button class="control-btn primary" id="stopCopyButton">Stop & Copy</button>
                </div>
                <div class="status-message" id="statusMessage">Click the circle to start recording</div>
            </div>

            <div class="transcription-card" id="transcriptionCard">
                <div class="transcription-placeholder" id="transcriptionPlaceholder">
                    Your transcription will appear here.
                </div>
                <div class="transcription-text" id="transcriptionText" style="display: none;"></div>
                <div class="hint">
                    <div class="hint-text" style="flex: 1; text-align: left;">Right-click the text to copy</div>
                    <img src="/Robot.png" class="robot-illustration" alt="Robot holding microphone">
                </div>
            </div>
        </div>

        <div class="alert error" id="errorMessage"></div>
        <div class="alert success" id="successMessage"></div>
    </div>

    <script>
        (function() {
            const SERVER_URL = 'http://localhost:{{ config.server_port }}';

            class DeskTalkRecorder {
                constructor() {
                    this.isRecording = false;
                    this.mediaRecorder = null;
                    this.audioChunks = [];
                    this.shouldAutoCopy = false;
                    this.stream = null;

                    this.recordButton = document.getElementById('recordButton');
                    this.controlRow = document.getElementById('controlRow');
                    this.stopButton = document.getElementById('stopButton');
                    this.stopCopyButton = document.getElementById('stopCopyButton');
                    this.statusMessage = document.getElementById('statusMessage');
                    this.transcriptionPlaceholder = document.getElementById('transcriptionPlaceholder');
                    this.transcriptionText = document.getElementById('transcriptionText');
                    this.transcriptionCard = document.getElementById('transcriptionCard');
                    this.errorMessage = document.getElementById('errorMessage');
                    this.successMessage = document.getElementById('successMessage');

                    this.bindEvents();
                }

                bindEvents() {
                    this.recordButton.addEventListener('click', () => {
                        if (this.isRecording) {
                            this.stopRecording();
                        } else {
                            this.startRecording();
                        }
                    });

                    this.stopButton.addEventListener('click', () => this.stopRecording());
                    this.stopCopyButton.addEventListener('click', () => {
                        this.shouldAutoCopy = true;
                        this.stopRecording();
                    });

                    this.transcriptionCard.addEventListener('contextmenu', (event) => {
                        event.preventDefault();
                        if (this.transcriptionText.style.display === 'none') {
                            return;
                        }
                        this.copyTranscription();
                    });
                }


                updateStatus(message) {
                    this.statusMessage.textContent = message;
                }

                resetAlerts() {
                    this.errorMessage.style.display = 'none';
                    this.successMessage.style.display = 'none';
                }

                showError(message) {
                    this.errorMessage.textContent = message;
                    this.errorMessage.style.display = 'block';
                    this.successMessage.style.display = 'none';
                }

                showSuccess(message) {
                    this.successMessage.textContent = message;
                    this.successMessage.style.display = 'block';
                    this.errorMessage.style.display = 'none';
                }

                async startRecording() {
                    this.resetAlerts();
                    try {
                        if (!this.stream) {
                            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        }

                        this.audioChunks = [];
                        this.mediaRecorder = new MediaRecorder(this.stream, { mimeType: 'audio/webm' });

                        this.mediaRecorder.addEventListener('dataavailable', event => {
                            if (event.data.size > 0) {
                                this.audioChunks.push(event.data);
                            }
                        });

                        this.mediaRecorder.addEventListener('stop', () => {
                            this.processRecording();
                        });

                        this.mediaRecorder.start();
                        this.isRecording = true;
                        this.recordButton.classList.add('recording');
                        this.recordButton.textContent = '●';
                        this.updateStatus('Recording... speak naturally');
                        this.controlRow.style.display = 'flex';
                    } catch (error) {
                        this.showError(`Could not start recording: ${error.message}`);
                        this.updateStatus('Ready when you are');
                        if (this.stream) {
                            this.stream.getTracks().forEach(track => track.stop());
                            this.stream = null;
                        }
                    }
                }

                stopRecording() {
                    if (!this.isRecording || !this.mediaRecorder) {
                        return;
                    }

                    this.mediaRecorder.stop();
                    this.isRecording = false;
                    this.recordButton.classList.remove('recording');
                    this.recordButton.classList.add('processing');
                    this.recordButton.textContent = '…';
                    this.updateStatus('Processing audio...');
                    this.controlRow.style.display = 'none';
                }

                async processRecording() {
                    try {
                        const blob = new Blob(this.audioChunks, { type: 'audio/webm' });
                        if (blob.size === 0) {
                            throw new Error('No audio captured');
                        }

                        const formData = new FormData();
                        formData.append('audio', blob, 'desktop-recording.webm');

                        const response = await fetch(`${SERVER_URL}/transcribe`, {
                            method: 'POST',
                            body: formData
                        });

                        if (!response.ok) {
                            throw new Error(`Server responded with ${response.status}`);
                        }

                        const data = await response.json();
                        const text = (data && data.transcription) ? data.transcription.trim() : '';
                        this.displayTranscription(text || '[No speech detected]');
                        this.updateStatus('Transcription ready');

                        if (this.shouldAutoCopy) {
                            await this.copyTranscription();
                            this.shouldAutoCopy = false;
                        }
                    } catch (error) {
                        this.showError(`Transcription failed: ${error.message}`);
                        this.updateStatus('Ready when you are');
                    } finally {
                        this.recordButton.classList.remove('processing');
                        this.recordButton.textContent = '●';
                    }
                }

                displayTranscription(text) {
                    this.transcriptionPlaceholder.style.display = 'none';
                    this.transcriptionText.style.display = 'block';
                    this.transcriptionText.textContent = text;
                }

                async copyTranscription() {
                    if (this.transcriptionText.style.display === 'none') {
                        return;
                    }
                    try {
                        await navigator.clipboard.writeText(this.transcriptionText.textContent);
                        // Update the hint text instead of showing popup
                        const hintElement = document.querySelector('.hint');
                        if (hintElement) {
                            const textNode = hintElement.querySelector('.hint-text');
                            const originalText = textNode ? textNode.textContent : hintElement.textContent;
                            if (textNode) {
                                textNode.textContent = 'Copied to clipboard';
                            } else {
                                hintElement.textContent = 'Copied to clipboard';
                            }
                            hintElement.style.color = '#10b981'; // Green color
                            setTimeout(() => {
                                if (textNode) {
                                    textNode.textContent = originalText;
                                } else {
                                    hintElement.textContent = originalText;
                                }
                                hintElement.style.color = ''; // Reset color
                            }, 2000);
                        }
                    } catch (error) {
                        this.showError('Could not copy text automatically');
                    }
                }
            }

            window.addEventListener('DOMContentLoaded', () => new DeskTalkRecorder());
        })();
    </script>
</body>
</html>
"""


    def run(self):
        """Start the Flask app and create the webview window"""
        # Set application user model ID early to separate from Python
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WebTalk.SettingsApp.1.0")
            print("Early application ID set successfully!")
        except Exception as e:
            print(f"Could not set early application ID: {e}")
        
        # Start Flask in a separate thread
        flask_thread = threading.Thread(
            target=lambda: self.app.run(host='127.0.0.1', port=5555, debug=False, use_reloader=False),
            daemon=True
        )
        flask_thread.start()
        
        # Give Flask a moment to start
        time.sleep(2)
        
        print("Flask server started successfully!")
        print("Creating PyWebView window...")
        
        # Calculate window dimensions based on screen size
        # Target: 90% of screen height, with max of 950px (original design height)
        # Width stays fixed - content will adapt via flexbox
        MAX_HEIGHT = 950
        WINDOW_WIDTH = 550
        
        try:
            # Get screen dimensions using Windows API
            user32 = ctypes.windll.user32
            screen_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
            print(f"Detected screen height: {screen_height}px")
            
            # Calculate 90% of screen height, capped at MAX_HEIGHT
            target_height = min(int(screen_height * 0.9), MAX_HEIGHT)
            
            print(f"Window size: {WINDOW_WIDTH}x{target_height}")
        except Exception as e:
            print(f"Could not get screen dimensions, using defaults: {e}")
            target_height = MAX_HEIGHT
        
        # Create and start the webview window
        try:
            window = webview.create_window(
                'WebTalk Server Settings',
                'http://127.0.0.1:5555',
                width=WINDOW_WIDTH,
                height=target_height,
                resizable=True,
                shadow=True,
                on_top=False,  # Allow window to go behind other windows
                minimized=False,
                background_color='#0f172a',  # Match the app background
                js_api=None,
                text_select=False
            )
            
            # Set up dark title bar and icon after window is shown
            def set_window_properties():
                try:
                    from webview.platforms.winforms import BrowserView
                    import ctypes.wintypes
                    
                    # Get window handle
                    window_handle = BrowserView.instances[window.uid].Handle.ToInt32()
                    
                    # Set application user model ID to separate from Python
                    shell32 = ctypes.windll.shell32
                    try:
                        shell32.SetCurrentProcessExplicitAppUserModelID("WebTalk.SettingsApp.1.0")
                        print("Application ID set successfully!")
                    except:
                        pass
                    
                    # Set dark title bar
                    dwmapi = ctypes.windll.LoadLibrary("dwmapi")
                    dwmapi.DwmSetWindowAttribute(
                        window_handle,
                        20,  # DWMWA_USE_IMMERSIVE_DARK_MODE
                        ctypes.byref(ctypes.c_bool(True)),
                        ctypes.sizeof(ctypes.wintypes.BOOL),
                    )
                    print("Dark title bar applied successfully!")
                    
                    # Set custom icon
                    icon_path = IMAGES_DIR / "WebTalk.ico"
                    if icon_path.exists():
                        user32 = ctypes.windll.user32
                        
                        # Load icon with multiple sizes
                        hicon_small = user32.LoadImageW(
                            None, 
                            str(icon_path), 
                            1,  # IMAGE_ICON
                            16, 16,  # Small icon size
                            0x00000010  # LR_LOADFROMFILE
                        )
                        hicon_large = user32.LoadImageW(
                            None, 
                            str(icon_path), 
                            1,  # IMAGE_ICON
                            32, 32,  # Large icon size
                            0x00000010  # LR_LOADFROMFILE
                        )
                        
                        if hicon_small and hicon_large:
                            # Set window icons
                            user32.SendMessageW(window_handle, 0x0080, 0, hicon_small)  # WM_SETICON, ICON_SMALL
                            user32.SendMessageW(window_handle, 0x0080, 1, hicon_large)  # WM_SETICON, ICON_BIG
                            
                            # Set class icon for taskbar
                            user32.SetClassLongPtrW(window_handle, -14, hicon_small)  # GCL_HICONSM
                            user32.SetClassLongPtrW(window_handle, -34, hicon_large)  # GCL_HICON
                            
                            # Additional method: Set process icon
                            kernel32 = ctypes.windll.kernel32
                            process_handle = kernel32.GetCurrentProcess()
                            
                            # Force taskbar to update
                            user32.SetWindowPos(window_handle, 0, 0, 0, 0, 0, 0x0020 | 0x0004 | 0x0001)  # SWP_FRAMECHANGED | SWP_NOZORDER | SWP_NOSIZE
                            
                            print("Custom icon applied successfully!")
                        else:
                            print("Failed to load icon file")
                    else:
                        print(f"Icon file not found: {icon_path}")
                        
                except Exception as e:
                    print(f"Could not apply window properties: {e}")
            
            # Apply window properties when window is shown
            window.events.shown += set_window_properties
            
            print("Starting PyWebView...")
            webview.start(debug=False, private_mode=False)  # Disable debug to prevent DevTools window
            print("PyWebView window closed.")
        except Exception as e:
            print(f"Error starting webview: {e}")
            print("Flask server is running at http://127.0.0.1:5555")
            print("You can open this URL in your browser as a fallback.")
            # Keep the Flask server running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Settings app stopped.")

def main():
    """Main entry point"""
    app = WebTalkSettingsApp()
    app.run()

if __name__ == "__main__":
    main() 
