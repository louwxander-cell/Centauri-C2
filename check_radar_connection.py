#!/usr/bin/env python3
"""
Quick Radar Connection Test
Tests connection to EchoGuard radar at configured IP
"""

import json
import socket
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def check_radar_connection():
    """Test radar connection"""
    
    # Load config
    config_path = Path(__file__).parent / "config" / "settings.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    radar_config = config.get('network', {}).get('radar', {})
    enabled = radar_config.get('enabled', False)
    host = radar_config.get('host', '192.168.1.25')
    port = radar_config.get('port', 29982)
    
    print("=" * 60)
    print("  EchoGuard Radar Connection Test")
    print("=" * 60)
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Enabled in config: {enabled}")
    print("=" * 60)
    print()
    
    if not enabled:
        print("❌ Radar is DISABLED in config/settings.json")
        print("   Set 'network.radar.enabled' to true to enable")
        return False
    
    # Test TCP connection
    print(f"Testing TCP connection to {host}:{port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((host, port))
        print(f"✅ SUCCESS: Connected to radar at {host}:{port}")
        sock.close()
        return True
    except socket.timeout:
        print(f"❌ TIMEOUT: No response from {host}:{port}")
        print("   - Check if radar is powered on")
        print("   - Verify network connection")
        return False
    except ConnectionRefusedError:
        print(f"❌ CONNECTION REFUSED: Radar at {host}:{port} refused connection")
        print("   - Check if radar software is running")
        print("   - Verify port number is correct")
        return False
    except OSError as e:
        print(f"❌ NETWORK ERROR: {e}")
        print("   - Check if IP address is correct")
        print("   - Verify you're on the same network")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = check_radar_connection()
    print()
    if success:
        print("✅ Radar is connected and ready")
    else:
        print("❌ Radar connection failed")
    print()
