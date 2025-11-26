"""Abstract base class for all sensor drivers"""

from abc import ABCMeta, abstractmethod
from PyQt6.QtCore import QThread, pyqtSignal
from typing import Optional


class QThreadABCMeta(type(QThread), ABCMeta):
    """Metaclass that combines QThread and ABC metaclasses"""
    pass


class BaseDriver(QThread, metaclass=QThreadABCMeta):
    """
    Abstract base class for all sensor/hardware drivers.
    Runs in separate thread and communicates via signals.
    """
    
    # Status signals
    sig_status_changed = pyqtSignal(bool)  # Online/Offline
    sig_error = pyqtSignal(str)  # Error message
    
    def __init__(self, name: str, parent=None):
        """
        Args:
            name: Driver name for logging
            parent: Parent QObject
        """
        super().__init__(parent)
        self.name = name
        self._running = False
        self._online = False
        
    @abstractmethod
    def run(self):
        """Main thread loop - must be implemented by subclasses"""
        pass
    
    def start_driver(self):
        """Start the driver thread"""
        if not self._running:
            self._running = True
            self.start()
            print(f"[{self.name}] Driver started")
    
    def stop_driver(self):
        """Stop the driver thread gracefully"""
        if self._running:
            self._running = False
            self.wait(2000)  # Wait up to 2 seconds for thread to finish
            print(f"[{self.name}] Driver stopped")
    
    def is_running(self) -> bool:
        """Check if driver is running"""
        return self._running
    
    def is_online(self) -> bool:
        """Check if driver is online and operational"""
        return self._online
    
    def set_online(self, online: bool):
        """Update online status"""
        if self._online != online:
            self._online = online
            self.sig_status_changed.emit(online)
            status = "ONLINE" if online else "OFFLINE"
            print(f"[{self.name}] Status: {status}")
    
    def emit_error(self, error_msg: str):
        """Emit error signal"""
        print(f"[{self.name}] ERROR: {error_msg}")
        self.sig_error.emit(error_msg)
