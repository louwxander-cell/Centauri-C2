#!/usr/bin/env python3
"""
TriAD C2 - Main Entry Point
Launches Orchestration Bridge + QML UI
With EchoGuard Radar Integration
"""

import sys
import os
import json
import glob
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QGuiApplication

# Windows-specific: Console I/O is much slower than macOS
# This causes jitter when printing frequently
WINDOWS_MODE = sys.platform == 'win32'

# Import orchestration components
from orchestration.bridge import OrchestrationBridge
from engine.mock_engine_updated import MockEngine

# Import GPS driver
from src.drivers.gps_septentrio import SeptentrioMosaicDriver

# Import Radar controller
from src.drivers.radar_controller import RadarController


def main():
    """Main application entry point"""
    
    # Create Qt application
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("TriAD")
    app.setApplicationName("TriAD C2")
    
    print("=" * 70)
    print("  TriAD C2 - Counter-UAS Command & Control")
    print("=" * 70)
    print("  Architecture: Engine -> Orchestration -> UI")
    print("  Engine: Mock (Python prototype)")
    print("  UI: Qt Quick (QML) GPU-accelerated")
    print("=" * 70)
    print()
    
    # Initialize engine (mock for now)
    print("[INIT] Starting mock engine...")
    engine = MockEngine()
    
    # Initialize GPS (if enabled)
    gps_driver = None
    try:
        config_path = Path(__file__).parent / "config" / "settings.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if config.get('gps', {}).get('enabled', False):
            print("[INIT] Initializing GPS...")
            
            # Determine port (try to find actual device)
            port_pattern = config['gps'].get('port', '/dev/tty.usbmodem*')
            baudrate = config['gps'].get('baudrate', 115200)
            
            # Try to find matching port
            matching_ports = glob.glob(port_pattern)
            if matching_ports:
                port = matching_ports[0]
            else:
                # Fallback to Linux port if on Linux
                port = config['gps'].get('port_linux', '/dev/ttyACM0')
            
            print(f"[INIT]   Model: Septentrio Mosaic-H")
            print(f"[INIT]   Port: {port}")
            print(f"[INIT]   Baud: {baudrate}")
            
            try:
                gps_driver = SeptentrioMosaicDriver(port=port, baudrate=baudrate)
                gps_driver.start_driver()  # Use start_driver() not start()
                print(f"[INIT] ✓ GPS driver started")
            except Exception as e:
                print(f"[INIT] ✗ GPS initialization failed: {e}")
                print(f"[INIT]   Continuing without GPS...")
                gps_driver = None
        else:
            print("[INIT] GPS disabled in configuration")
    except Exception as e:
        print(f"[INIT] GPS configuration error: {e}")
        print(f"[INIT]   Continuing without GPS...")
    
    # Initialize radar controller
    # Note: Radar initialization is now handled separately to avoid UI jitter
    # Run radar control script separately or enable here after testing
    radar_controller = None
    radar_enabled = config.get('network', {}).get('radar', {}).get('enabled', False)
    
    if radar_enabled:
        try:
            radar_config = config.get('network', {}).get('radar', {})
            radar_host = radar_config.get('host', '192.168.1.25')
            radar_port = radar_config.get('port', 29982)
            
            print(f"[INIT] Initializing EchoGuard radar at {radar_host}...")
            radar_controller = RadarController(radar_host)
            
            if radar_controller.connect():
                print(f"[INIT] Connected to radar command port")
                if radar_controller.initialize_radar():
                    print(f"[INIT] Radar initialized")
                    radar_settings = {
                        'operation_mode': 1,  # UAS mode
                        'search_az_min': -60,
                        'search_az_max': 60,
                        'search_el_min': -40,
                        'search_el_max': 40
                    }
                    radar_controller.configure_radar(radar_settings)
                    if radar_controller.start_radar():
                        print(f"[INIT] Radar started - streaming on port {radar_port}")
                    else:
                        print(f"[INIT] WARNING: Failed to start radar")
                else:
                    print(f"[INIT] WARNING: Radar initialization failed")
            else:
                print(f"[INIT] WARNING: Could not connect to radar at {radar_host}")
                radar_controller = None
        except Exception as e:
            print(f"[INIT] Radar error: {e}")
            print(f"[INIT]   Continuing without radar control...")
            radar_controller = None
    else:
        print(f"[INIT] Radar control disabled in config (set radar.enabled=true to enable)")
    
    # Initialize orchestration bridge
    print("[INIT] Creating orchestration bridge...")
    bridge = OrchestrationBridge(engine, gps_driver=gps_driver)
    
    # Create QML engine
    qml_engine = QQmlApplicationEngine()
    
    # Expose models to QML
    print("[INIT] Exposing data models to QML...")
    qml_engine.rootContext().setContextProperty("tracksModel", bridge.tracks_model)
    qml_engine.rootContext().setContextProperty("ownship", bridge.ownship)
    qml_engine.rootContext().setContextProperty("systemMode", bridge.system_mode)
    qml_engine.rootContext().setContextProperty("bridge", bridge)
    qml_engine.rootContext().setContextProperty("engine", engine)  # For test scenario controls
    
    # Set import path
    ui_dir = Path(__file__).parent / "ui"
    qml_engine.addImportPath(str(ui_dir))
    
    # Load main QML
    qml_file = ui_dir / "Main.qml"
    print(f"[INIT] Loading QML from: {qml_file}")
    qml_engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    if not qml_engine.rootObjects():
        print("[ERROR] Failed to load QML file")
        return -1
    
    print()
    print("=" * 70)
    print("  TriAD C2 - RUNNING")
    print("=" * 70)
    print("  Track updates: 10 Hz")
    print("  GPU-accelerated rendering")
    print("  Window should now be visible")
    print("=" * 70)
    print()
    print("[INFO] Click tracks to select")
    print("[INFO] Selected track enables ENGAGE button")
    print("[INFO] Engage button sends request to Engine for safety validation")
    print()
    
    # Run event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
