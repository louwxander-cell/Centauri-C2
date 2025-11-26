#!/usr/bin/env python3
"""
TriAD Counter-UAS C2 System
Main application entry point
"""

import sys
import signal
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from src.core.bus import SignalBus
from src.drivers.radar import RadarDriver
from src.drivers.rf import RFDriver
from src.drivers.gps import GPSDriver
from src.drivers.rws import RWSDriver
from src.ui.main_window_modern import ModernMainWindow


class TriADApplication:
    """Main application controller"""
    
    def __init__(self):
        """Initialize the TriAD C2 application"""
        self._print_banner()
        
        # Initialize Qt application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("TriAD C2")
        
        # Initialize signal bus
        self.signal_bus = SignalBus.instance()
        
        # Initialize drivers
        self.radar_driver = RadarDriver()
        self.rf_driver = RFDriver()
        self.gps_driver = GPSDriver()
        self.rws_driver = RWSDriver()
        
        # Initialize main window
        self.main_window = ModernMainWindow()
        
        # Connect shutdown signal
        self.signal_bus.sig_shutdown.connect(self.shutdown)
        
        # Setup signal handler for Ctrl+C
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Timer to allow Python to process signals
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(100)
    
    def _print_banner(self):
        """Print startup banner"""
        banner_path = os.path.join(os.path.dirname(__file__), 'BANNER.txt')
        try:
            with open(banner_path, 'r') as f:
                print(f.read())
        except FileNotFoundError:
            # Fallback if banner file not found
            print("=" * 71)
            print("TriAD Counter-UAS Command & Control System")
            print("=" * 71)
        
    def _signal_handler(self, signum, frame):
        """Handle system signals (Ctrl+C)"""
        print("\n[Main] Interrupt received, shutting down...")
        self.shutdown()
        sys.exit(0)
    
    def start(self):
        """Start all drivers and show main window"""
        print("\n[Main] Starting drivers...")
        
        # Start all drivers
        self.radar_driver.start_driver()
        self.rf_driver.start_driver()
        self.gps_driver.start_driver()
        self.rws_driver.start_driver()
        
        print("[Main] All drivers started")
        
        # Show main window
        self.main_window.show()
        print("[Main] Main window displayed")
        print("\n[Main] System operational - Ready for mission")
        print("-" * 60)
        
        # Run application event loop
        return self.app.exec()
    
    def shutdown(self):
        """Shutdown all drivers and cleanup"""
        print("\n[Main] Initiating shutdown sequence...")
        
        # Stop all drivers
        drivers = [
            self.radar_driver,
            self.rf_driver,
            self.gps_driver,
            self.rws_driver
        ]
        
        for driver in drivers:
            if driver.is_running():
                print(f"[Main] Stopping {driver.name}...")
                driver.stop_driver()
        
        print("[Main] All drivers stopped")
        print("[Main] Shutdown complete")
        print("=" * 60)


def main():
    """Main entry point"""
    try:
        app = TriADApplication()
        sys.exit(app.start())
    except KeyboardInterrupt:
        print("\n[Main] Keyboard interrupt received")
        sys.exit(0)
    except Exception as e:
        print(f"\n[Main] FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
