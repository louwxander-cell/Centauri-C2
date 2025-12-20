"""
Configuration management for TriAD C2 system
"""

import json
import os
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from settings.json
    
    Args:
        config_path: Optional path to config file. If None, uses default location.
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        # Default config path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_path = os.path.join(base_dir, 'config', 'settings.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Warning: Config file not found at {config_path}, using defaults")
        return get_default_config()
    except json.JSONDecodeError as e:
        print(f"Error parsing config file: {e}, using defaults")
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration
    
    Returns:
        Default configuration dictionary
    """
    return {
        "network": {
            "radar": {
                "protocol": "TCP",
                "host": "192.168.1.25",
                "port": 29982
            },
            "rws": {
                "protocol": "UDP",
                "host": "127.0.0.1",
                "port": 5000
            },
            "rf": {
                "protocol": "REST",
                "base_url": "http://127.0.0.1:8080/api"
            }
        },
        "gps": {
            "enabled": False,
            "driver": "production",
            "model": "septentrio_mosaic_h",
            "port": "COM3",
            "port_linux": "/dev/ttyACM0",
            "baudrate": 115200,
            "update_rate_hz": 5
        },
        "system": {
            "update_rate_hz": 10,
            "track_timeout_sec": 5.0,
            "fusion_distance_threshold_m": 50.0
        },
        "ui": {
            "theme": "tactical_dark",
            "refresh_rate_ms": 100
        }
    }
