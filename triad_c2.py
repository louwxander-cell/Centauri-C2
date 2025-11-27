#!/usr/bin/env python3
"""
TriAD C2 - Main Entry Point
Launches Orchestration Bridge + QML UI
"""

import sys
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QGuiApplication

# Import orchestration components
from orchestration.bridge import OrchestrationBridge
from engine.mock_engine_updated import MockEngine


def main():
    """Main application entry point"""
    
    # Create Qt application
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("TriAD")
    app.setApplicationName("TriAD C2")
    
    print("=" * 70)
    print("  TriAD C2 - Counter-UAS Command & Control")
    print("=" * 70)
    print("  Architecture: Engine → Orchestration → UI")
    print("  Engine: Mock (Python prototype)")
    print("  UI: Qt Quick (QML) GPU-accelerated")
    print("=" * 70)
    print()
    
    # Initialize engine (mock for now)
    print("[INIT] Starting mock engine...")
    engine = MockEngine()
    
    # Initialize orchestration bridge
    print("[INIT] Creating orchestration bridge...")
    bridge = OrchestrationBridge(engine)
    
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
