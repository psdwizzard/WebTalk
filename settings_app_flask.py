#!/usr/bin/env python3
"""
WebTalk Settings Desktop App - Flask + PyWebView Version
Beautiful desktop settings interface using the original HTML design.
"""

import json
import os
import threading
import time
from typing import Dict, Any
import requests
import webview
from flask import Flask, render_template_string, request, jsonify
import ctypes
from ctypes import wintypes

class WebTalkSettingsApp:
    def __init__(self):
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
        self.app = Flask(__name__)
        self.setup_routes()
        
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
            
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Serve the main settings page"""
            return render_template_string(self.get_html_template(), config=self.config)
        
        @self.app.route('/desktalk')
        def desktalk():
            """Serve the DeskTalk recorder page"""
            return render_template_string(self.get_desktalk_template(), config=self.config)
        
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
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 0;
            background: #1F2937;
            overflow-x: hidden;
        }
        .settings-container {
            width: 100%;
            background: linear-gradient(135deg, #8E2DE2 0%, #4A00E0 100%);
            color: white;
            border-radius: 0;
            padding: 24px;
            box-sizing: border-box;
            min-height: 100vh;
        }
        
        /* Tab Styles */
        .tab-container {
            display: flex;
            margin-bottom: 24px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 6px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        .tab-button {
            flex: 1;
            padding: 14px 24px;
            border: none;
            background: transparent;
            color: rgba(255, 255, 255, 0.8);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            font-size: 1rem;
            text-align: center;
        }
        .tab-button.active {
            background: rgba(255, 255, 255, 0.3);
            color: white;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            transform: translateY(-1px);
        }
        .tab-button:hover {
            background: rgba(255, 255, 255, 0.25);
            color: white;
            transform: translateY(-1px);
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        .input-group label {
            display: block;
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 8px;
            color: rgba(255, 255, 255, 0.8);
        }
        .input-field, .select-field {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 0.875rem;
            transition: background-color 0.3s, border-color 0.3s;
            box-sizing: border-box;
        }
        .input-field:focus, .select-field:focus {
            outline: none;
            background-color: rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.4);
        }
        .input-field::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }
        .select-field option {
            color: #333;
        }
        .btn {
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 500;
            font-size: 0.875rem;
            cursor: pointer;
            transition: background-color 0.3s, transform 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            border: none;
            width: 100%;
        }
        .btn-primary {
            background-color: #FF4081;
            color: white;
        }
        .btn-primary:hover {
            background-color: #F50057;
            transform: translateY(-1px);
        }
        .alert-message {
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.7);
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
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23FFFFFF'%3E%3Cpath d='M12 2C11.45 2 11 2.45 11 3V6.08C7.76 6.57 5.25 9.24 5.04 12.5C5.01 12.98 4.63 13.38 4.15 13.42C3.66 13.45 3.27 13.08 3.24 12.6C3.07 9.72 5.03 7.16 7.82 6.33V3C7.82 2.45 8.27 2 8.82 2H9.18C9.73 2 10.18 2.45 10.18 3V5.54C10.79 5.42 11.4 5.35 12 5.35S13.21 5.42 13.82 5.54V3C13.82 2.45 14.27 2 14.82 2H15.18C15.73 2 16.18 2.45 16.18 3V6.33C18.97 7.16 20.93 9.72 20.76 12.6C20.73 13.08 20.34 13.45 19.85 13.42C19.37 13.38 18.99 12.98 18.96 12.5C18.75 9.24 16.24 6.57 13 6.08V3C13 2.45 12.55 2 12 2ZM12 7.35C14.68 7.35 16.91 9.45 17.03 12.12L17.05 12.5C17.07 12.8 16.92 13.08 16.67 13.26C16.41 13.44 16.09 13.44 15.83 13.26L15.47 13C15.06 12.72 14.53 12.78 14.19 13.11C13.85 13.45 13.79 13.98 14.07 14.39L14.33 14.74C14.51 15 14.51 15.31 14.33 15.57C14.15 15.83 13.84 15.91 13.57 15.79L13.05 15.57C12.7 15.41 12.35 15.41 12 15.57L11.43 15.79C11.16 15.91 10.85 15.83 10.67 15.57C10.49 15.31 10.49 15 10.67 14.74L10.93 14.39C11.21 13.98 11.15 13.45 10.81 13.11C10.47 12.78 9.94 12.72 9.53 13L9.17 13.26C8.91 13.44 8.59 13.44 8.33 13.26C8.08 13.08 7.93 12.8 7.95 12.5L7.97 12.12C8.09 9.45 10.32 7.35 13 7.35H12ZM6 15V19C6 20.1 6.9 21 8 21H16C17.1 21 18 20.1 18 19V15H16V19H8V15H6Z'/%3E%3C/svg%3E");
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
        }
        .header-title {
            font-size: 1.5rem;
            font-weight: 700;
        }
        .icon-input-group {
            position: relative;
        }
        .icon-input-group .material-icons {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: rgba(255, 255, 255, 0.6);
            font-size: 1.25rem;
        }
        .icon-input-group .input-field {
            padding-left: 44px;
        }
        .icon-input-group .select-field {
            padding-left: 44px;
        }
        .toggle-switch-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px;
            border-radius: 8px;
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .toggle-switch {
            position: relative;
            display: inline-block;
            width: 50px;
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
            background-color: rgba(255, 255, 255, 0.3);
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
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        input:checked + .slider {
            background-color: #FF4081;
        }
        input:focus + .slider {
            box-shadow: 0 0 1px #FF4081;
        }
        input:checked + .slider:before {
            transform: translateX(22px);
        }
        .toggle-label {
            color: rgba(255,255,255,0.9);
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
            <button class="tab-button active" onclick="switchTab('settings')">⚙️ Settings</button>
            <button class="tab-button" onclick="switchTab('desktalk')">🎤 DeskTalk</button>
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
            
            <div class="input-group">
                <label for="server-port">Server Port</label>
                <div class="icon-input-group">
                    <span class="material-icons">settings_ethernet</span>
                    <input class="input-field" id="server-port" placeholder="e.g., 8080" type="number" value="{{ config.server_port }}"/>
                </div>
            </div>
            
            <div class="input-group">
                <label for="auth-key">Authentication Key (Optional)</label>
                <div class="icon-input-group">
                    <span class="material-icons">vpn_key</span>
                    <input class="input-field" id="auth-key" placeholder="Enter a secure key" type="password" value="{{ config.auth_key }}"/>
                </div>
            </div>
            
            <div class="input-group">
                <label for="openai-api-key">OpenAI API Key (Fallback)</label>
                <div class="icon-input-group">
                    <span class="material-icons">api</span>
                    <input class="input-field" id="openai-api-key" placeholder="sk-..." type="text" value="{{ config.openai_api_key }}"/>
                </div>
                <p class="text-xs text-gray-300 mt-1 opacity-75">Used if local hardware is insufficient.</p>
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
        <div id="desktalk-tab" class="tab-content" style="display: none;">
            <iframe src="/desktalk" style="width: 100%; height: 70vh; border: none; border-radius: 12px;"></iframe>
        </div>
    </div>

    <script>
        function switchTab(tabName) {
            console.log('Switching to tab:', tabName);
            
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.style.display = 'none';
                console.log('Hiding tab:', tab.id);
            });
            
            // Remove active class from all tab buttons
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected tab content
            const targetTab = document.getElementById(tabName + '-tab');
            if (targetTab) {
                targetTab.style.display = 'block';
                console.log('Showing tab:', targetTab.id);
            } else {
                console.error('Tab not found:', tabName + '-tab');
            }
            
            // Add active class to clicked button
            event.target.classList.add('active');
            console.log('Tab switch completed');
        }

        // Initialize tabs on page load
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Page loaded, initializing tabs');
            
            // Ensure settings tab is visible by default
            const settingsTab = document.getElementById('settings-tab');
            const desktalkTab = document.getElementById('desktalk-tab');
            
            if (settingsTab) {
                settingsTab.style.display = 'block';
                console.log('Settings tab initialized');
            }
            
            if (desktalkTab) {
                desktalkTab.style.display = 'none';
                console.log('DeskTalk tab initialized');
            }
            
            // Ensure first tab button is active
            const firstTabButton = document.querySelector('.tab-button');
            if (firstTabButton) {
                firstTabButton.classList.add('active');
            }
        });

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
                    microphone: document.getElementById('microphone-selector').value,
                    server_port: parseInt(document.getElementById('server-port').value),
                    auth_key: document.getElementById('auth-key').value,
                    openai_api_key: document.getElementById('openai-api-key').value
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
                        restartAlert.style.color = '#A7F3D0';
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
        computeToggle.addEventListener('change', () => {
            const selectedEngine = computeToggle.checked ? 'GPU' : 'CPU';
            console.log('Compute Engine set to:', selectedEngine);
            
            if (initialValues[computeToggle.id] !== computeToggle.checked) {
                restartAlert.style.display = 'block';
            } else if (!checkForChanges()) {
                restartAlert.style.display = 'none';
            }
        });
    </script>
</body>
</html>
        '''
    
    def get_desktalk_template(self):
        """Return the DeskTalk recorder template with embedded CSS and JavaScript"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DeskTalk Recorder</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet"/>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #8E2DE2 0%, #4A00E0 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            padding: 20px;
        }

        .recorder-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
            max-width: 500px;
            width: 100%;
            text-align: center;
        }

        .header {
            margin-bottom: 30px;
        }

        .logo {
            font-size: 3rem;
            margin-bottom: 10px;
        }

        h1 {
            font-size: 2rem;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .subtitle {
            opacity: 0.8;
            font-size: 1rem;
        }

        .recording-area {
            margin: 30px 0;
        }

        .record-button {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: none;
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            font-size: 2rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(255, 107, 107, 0.4);
            margin-bottom: 20px;
        }

        .record-button:hover {
            transform: scale(1.05);
            box-shadow: 0 15px 40px rgba(255, 107, 107, 0.6);
        }

        .record-button.recording {
            background: linear-gradient(45deg, #ff4757, #c44569);
            animation: pulse 2s infinite;
        }

        .record-button.processing {
            background: linear-gradient(45deg, #ffa502, #ff6348);
            cursor: not-allowed;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        .controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin: 20px 0;
        }

        .control-btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .control-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }

        .control-btn.primary {
            background: linear-gradient(45deg, #5f27cd, #341f97);
        }

        .control-btn.primary:hover {
            background: linear-gradient(45deg, #6c5ce7, #5f27cd);
        }

        .status {
            margin: 20px 0;
            font-size: 1rem;
            opacity: 0.9;
        }

        .transcription-area {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            min-height: 100px;
            text-align: left;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .transcription-placeholder {
            opacity: 0.6;
            font-style: italic;
            text-align: center;
        }

        .transcription-text {
            line-height: 1.6;
            font-size: 1rem;
        }

        .copy-button {
            background: linear-gradient(45deg, #00d2d3, #54a0ff);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.3s ease;
            margin-top: 10px;
        }

        .copy-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 210, 211, 0.4);
        }

        .error {
            background: rgba(255, 107, 107, 0.2);
            border: 1px solid rgba(255, 107, 107, 0.5);
            color: #ff6b6b;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
        }

        .success {
            background: rgba(46, 213, 115, 0.2);
            border: 1px solid rgba(46, 213, 115, 0.5);
            color: #2ed573;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
        }

        .hidden {
            display: none;
        }

        .server-status {
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.1);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.8rem;
        }

        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #ff4757;
        }

        .status-indicator.connected {
            background: #2ed573;
        }
    </style>
</head>
<body>
    <div class="server-status">
        <div class="status-indicator" id="statusIndicator"></div>
        <span id="statusText">Checking server...</span>
    </div>

    <div class="recorder-container">
        <div class="header">
            <div class="logo">🎤</div>
            <h1>DeskTalk</h1>
            <p class="subtitle">Voice Transcription Assistant</p>
        </div>

        <div class="recording-area">
            <button class="record-button" id="recordButton">
                <span id="recordIcon">🎙️</span>
            </button>
            
            <div class="controls hidden" id="recordingControls">
                <button class="control-btn" id="stopButton">⏹️ Stop</button>
                <button class="control-btn primary" id="stopCopyButton">📋 Stop & Copy</button>
            </div>
        </div>

        <div class="status" id="statusMessage">Click the microphone to start recording</div>

        <div class="transcription-area">
            <div class="transcription-placeholder" id="transcriptionPlaceholder">
                Your transcription will appear here...
            </div>
            <div class="transcription-text hidden" id="transcriptionText"></div>
            <button class="copy-button hidden" id="copyButton">📋 Copy to Clipboard</button>
        </div>

        <div id="errorMessage" class="error hidden"></div>
        <div id="successMessage" class="success hidden"></div>
    </div>

    <script>
        class WebTalkRecorder {
            constructor() {
                this.isRecording = false;
                this.mediaRecorder = null;
                this.audioChunks = [];
                this.stream = null;
                this.shouldAutoCopy = false;
                this.serverUrl = 'http://localhost:{{ config.server_port }}';
                
                this.initializeElements();
                this.setupEventListeners();
                this.checkServerStatus();
            }

            initializeElements() {
                this.recordButton = document.getElementById('recordButton');
                this.recordIcon = document.getElementById('recordIcon');
                this.recordingControls = document.getElementById('recordingControls');
                this.stopButton = document.getElementById('stopButton');
                this.stopCopyButton = document.getElementById('stopCopyButton');
                this.statusMessage = document.getElementById('statusMessage');
                this.transcriptionPlaceholder = document.getElementById('transcriptionPlaceholder');
                this.transcriptionText = document.getElementById('transcriptionText');
                this.copyButton = document.getElementById('copyButton');
                this.errorMessage = document.getElementById('errorMessage');
                this.successMessage = document.getElementById('successMessage');
                this.statusIndicator = document.getElementById('statusIndicator');
                this.statusText = document.getElementById('statusText');
            }

            setupEventListeners() {
                this.recordButton.addEventListener('click', () => this.toggleRecording());
                this.stopButton.addEventListener('click', () => this.stopRecording());
                this.stopCopyButton.addEventListener('click', () => this.stopAndCopyRecording());
                this.copyButton.addEventListener('click', () => this.copyTranscription());
            }

            async checkServerStatus() {
                try {
                    const response = await fetch(this.serverUrl + '/health');
                    if (response.ok) {
                        this.statusIndicator.classList.add('connected');
                        this.statusText.textContent = 'Server connected';
                        return true;
                    }
                } catch (error) {
                    console.error('Server check failed:', error);
                }
                
                this.statusIndicator.classList.remove('connected');
                this.statusText.textContent = 'Server disconnected';
                return false;
            }

            async toggleRecording() {
                if (this.isRecording) {
                    this.stopRecording();
                } else {
                    await this.startRecording();
                }
            }

            async startRecording() {
                try {
                    // Check server status first
                    const serverOk = await this.checkServerStatus();
                    if (!serverOk) {
                        this.showError('Server is not available. Please check if the WebTalk server is running.');
                        return;
                    }

                    // Request microphone access
                    this.stream = await navigator.mediaDevices.getUserMedia({ 
                        audio: {
                            echoCancellation: true,
                            noiseSuppression: true,
                            autoGainControl: true
                        } 
                    });

                    // Setup MediaRecorder
                    this.mediaRecorder = new MediaRecorder(this.stream, {
                        mimeType: 'audio/webm;codecs=opus'
                    });

                    this.audioChunks = [];
                    this.mediaRecorder.ondataavailable = (event) => {
                        if (event.data.size > 0) {
                            this.audioChunks.push(event.data);
                        }
                    };

                    this.mediaRecorder.onstop = () => {
                        this.processRecording();
                    };

                    // Start recording
                    this.mediaRecorder.start();
                    this.isRecording = true;
                    this.updateUI('recording');
                    
                } catch (error) {
                    console.error('Error starting recording:', error);
                    this.showError('Failed to start recording. Please check microphone permissions.');
                }
            }

            stopRecording() {
                if (this.mediaRecorder && this.isRecording) {
                    this.mediaRecorder.stop();
                    this.isRecording = false;
                    
                    // Stop all tracks
                    if (this.stream) {
                        this.stream.getTracks().forEach(track => track.stop());
                    }
                    
                    this.updateUI('processing');
                }
            }

            stopAndCopyRecording() {
                this.shouldAutoCopy = true;
                this.stopRecording();
            }

            async processRecording() {
                try {
                    // Create audio blob
                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                    
                    if (audioBlob.size === 0) {
                        this.showError('No audio data recorded. Please try again.');
                        this.updateUI('idle');
                        return;
                    }

                    // Create form data
                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'recording.webm');

                    // Send to server
                    const response = await fetch(this.serverUrl + '/transcribe', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error(`Server error: ${response.status}`);
                    }

                    const result = await response.json();
                    
                    if (result.success && result.transcription) {
                        this.displayTranscription(result.transcription);
                        
                        if (this.shouldAutoCopy) {
                            await this.copyTranscription();
                            this.shouldAutoCopy = false;
                        }
                    } else {
                        this.showError('Transcription failed. Please try again.');
                    }

                } catch (error) {
                    console.error('Processing error:', error);
                    this.showError(`Failed to process recording: ${error.message}`);
                } finally {
                    this.updateUI('idle');
                }
            }

            displayTranscription(text) {
                this.transcriptionPlaceholder.classList.add('hidden');
                this.transcriptionText.classList.remove('hidden');
                this.copyButton.classList.remove('hidden');
                this.transcriptionText.textContent = text;
                this.statusMessage.textContent = 'Transcription complete!';
            }

            async copyTranscription() {
                try {
                    const text = this.transcriptionText.textContent;
                    await navigator.clipboard.writeText(text);
                    this.showSuccess('Transcription copied to clipboard!');
                } catch (error) {
                    console.error('Copy failed:', error);
                    this.showError('Failed to copy to clipboard. Please select and copy manually.');
                }
            }

            updateUI(state) {
                this.hideMessages();
                
                switch (state) {
                    case 'recording':
                        this.recordButton.classList.add('recording');
                        this.recordIcon.textContent = '⏸️';
                        this.recordingControls.classList.remove('hidden');
                        this.statusMessage.textContent = '🔴 Recording... Speak now!';
                        break;
                        
                    case 'processing':
                        this.recordButton.classList.remove('recording');
                        this.recordButton.classList.add('processing');
                        this.recordIcon.textContent = '⏳';
                        this.recordingControls.classList.add('hidden');
                        this.statusMessage.textContent = 'Processing transcription...';
                        break;
                        
                    case 'idle':
                    default:
                        this.recordButton.classList.remove('recording', 'processing');
                        this.recordIcon.textContent = '🎙️';
                        this.recordingControls.classList.add('hidden');
                        this.statusMessage.textContent = 'Click the microphone to start recording';
                        break;
                }
            }

            showError(message) {
                this.hideMessages();
                this.errorMessage.textContent = message;
                this.errorMessage.classList.remove('hidden');
            }

            showSuccess(message) {
                this.hideMessages();
                this.successMessage.textContent = message;
                this.successMessage.classList.remove('hidden');
                setTimeout(() => {
                    this.successMessage.classList.add('hidden');
                }, 3000);
            }

            hideMessages() {
                this.errorMessage.classList.add('hidden');
                this.successMessage.classList.add('hidden');
            }
        }

        // Initialize the recorder when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            new WebTalkRecorder();
        });
    </script>
</body>
</html>
        '''
    
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
        
        # Create and start the webview window
        try:
            window = webview.create_window(
                'WebTalk Server Settings',
                'http://127.0.0.1:5555',
                width=600,
                height=1000,
                resizable=True,
                shadow=True,
                on_top=False,  # Allow window to go behind other windows
                minimized=False,
                background_color='#1F2937'  # Match the app background
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
                    icon_path = os.path.join(os.path.dirname(__file__), 'ComfyUI_00803__C.ico')
                    if os.path.exists(icon_path):
                        user32 = ctypes.windll.user32
                        
                        # Load icon with multiple sizes
                        hicon_small = user32.LoadImageW(
                            None, 
                            icon_path, 
                            1,  # IMAGE_ICON
                            16, 16,  # Small icon size
                            0x00000010  # LR_LOADFROMFILE
                        )
                        hicon_large = user32.LoadImageW(
                            None, 
                            icon_path, 
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
            webview.start(debug=False)  # Disable debug to prevent DevTools window
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