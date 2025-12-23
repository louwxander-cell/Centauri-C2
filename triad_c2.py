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
    
    # Windows-specific: Optimize Qt rendering for high-performance GPU
    if sys.platform == 'win32':
        # Use threaded render loop for powerful GPUs (better performance)
        os.environ['QSG_RENDER_LOOP'] = 'threaded'
        # Enable GPU rasterization for smoother rendering
        os.environ['QT_OPENGL'] = 'desktop'
        # Disable VSync to allow higher frame rates
        os.environ['QSG_INFO'] = '1'  # Enable debug info to verify settings
    
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
    
    # Initialize radar controller (but don't connect yet - operator will connect via UI)
    radar_controller = None
    radar_enabled = config.get('network', {}).get('radar', {}).get('enabled', False)
    
    if radar_enabled:
        try:
            radar_config = config.get('network', {}).get('radar', {})
            radar_host = radar_config.get('host', '192.168.1.25')
            radar_port = radar_config.get('command_port', 23)  # Command port is 23, NOT 29982 (tracks port)
            
            print(f"[INIT] EchoGuard radar command port at {radar_host}:{radar_port}")
            print(f"[INIT]   Status: STANDBY (click orange indicator to connect)")
            radar_controller = RadarController(radar_host, port=radar_port)
            
        except Exception as e:
            print(f"[INIT] Radar error: {e}")
            print(f"[INIT]   Continuing without radar control...")
            radar_controller = None
    else:
        print(f"[INIT] Radar control disabled in config (set radar.enabled=true to enable)")
    
    # Initialize orchestration bridge
    print("[INIT] Creating orchestration bridge...")
    bridge = OrchestrationBridge(
        engine, 
        gps_driver=gps_driver, 
        radar_driver=radar_controller,
        gps_enabled=config.get('gps', {}).get('enabled', False),
        radar_enabled=radar_enabled,
        rf_enabled=False  # RF sensor not yet implemented
    )
    
    # Create QML engine
    qml_engine = QQmlApplicationEngine()
    
    # Expose models to QML
    print("[INIT] Exposing data models to QML...")
    qml_engine.rootContext().setContextProperty("tracksModel", bridge.tracks_model)
    qml_engine.rootContext().setContextProperty("ownship", bridge.ownship)
    qml_engine.rootContext().setContextProperty("systemMode", bridge.system_mode)
    qml_engine.rootContext().setContextProperty("systemStatus", bridge.system_status)
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
