#!/usr/bin/env python3
"""
Configuration management for WebTalk Whisper API Server.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ServerConfig:
    """Manages server configuration settings."""
    
    def __init__(self, config_file: str = "webtalk_config.json"):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = Path(config_file)
        self.default_config = {
            "compute_engine": "cpu",  # "cpu" or "gpu"
            "model_selector": "tiny",  # whisper model size
            "microphone_selector": "default",  # microphone device
            "server_port": 9090,
            "auth_key": "",  # optional authentication key
            "openai_api_key": "",  # fallback API key
            "host": "127.0.0.1"
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default.
        
        Returns:
            Configuration dictionary
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged_config = self.default_config.copy()
                    merged_config.update(config)
                    logger.info(f"Configuration loaded from {self.config_file}")
                    return merged_config
            else:
                logger.info("No configuration file found, using defaults")
                return self.default_config.copy()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
            return self.default_config.copy()
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save (uses current config if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            config_to_save = config if config is not None else self.config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.config.update(updates)
            return self.save_config()
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config.copy() 