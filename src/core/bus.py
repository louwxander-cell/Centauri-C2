"""Central signal bus for inter-component communication"""

from PyQt6.QtCore import QObject, pyqtSignal
from typing import Optional
from .datamodels import Track, GeoPosition, SystemStatus


class SignalBus(QObject):
    """
    Singleton signal bus for system-wide event communication.
    All components emit and subscribe to signals through this central hub.
    """
    
    _instance: Optional['SignalBus'] = None
    
    # Core data signals
    sig_track_updated = pyqtSignal(object)  # Track object
    sig_track_removed = pyqtSignal(int)  # Track ID
    sig_ownship_updated = pyqtSignal(object)  # GeoPosition object
    sig_slew_command = pyqtSignal(float, float)  # Azimuth, Elevation
    sig_system_status = pyqtSignal(object)  # SystemStatus object
    
    # Driver status signals
    sig_radar_status = pyqtSignal(bool)  # Online/Offline
    sig_rf_status = pyqtSignal(bool)
    sig_gps_status = pyqtSignal(bool)
    sig_rws_status = pyqtSignal(bool)
    
    # UI interaction signals
    sig_track_selected = pyqtSignal(int)  # Track ID selected in UI
    sig_engage_requested = pyqtSignal(int)  # Track ID to engage
    
    # System control signals
    sig_shutdown = pyqtSignal()
    sig_emergency_stop = pyqtSignal()
    
    def __new__(cls):
        """Enforce singleton pattern"""
        if cls._instance is None:
            cls._instance = super(SignalBus, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the signal bus (only once)"""
        if hasattr(self, '_initialized'):
            return
        super().__init__()
        self._initialized = True
        print("[SignalBus] Initialized")
    
    @classmethod
    def instance(cls) -> 'SignalBus':
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def emit_track(self, track: Track):
        """Convenience method to emit track update"""
        self.sig_track_updated.emit(track)
    
    def emit_ownship(self, position: GeoPosition):
        """Convenience method to emit ownship position"""
        self.sig_ownship_updated.emit(position)
    
    def emit_slew(self, azimuth: float, elevation: float):
        """Convenience method to emit slew command"""
        self.sig_slew_command.emit(azimuth, elevation)
    
    def emit_status(self, status: SystemStatus):
        """Convenience method to emit system status"""
        self.sig_system_status.emit(status)
