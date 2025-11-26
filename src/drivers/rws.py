"""Mock Remote Weapon Station (RWS) driver - UDP control interface"""

import time
import socket
from .base import BaseDriver
from ..core.bus import SignalBus


class RWSDriver(BaseDriver):
    """
    Mock Remote Weapon Station driver.
    Receives slew commands and simulates weapon pointing.
    In production, this would send UDP packets to port 5000.
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 5000, parent=None):
        super().__init__("RWSDriver", parent)
        self.signal_bus = SignalBus.instance()
        self.host = host
        self.port = port
        
        # Current RWS position
        self.current_azimuth = 0.0
        self.current_elevation = 0.0
        
        # Slew rate limits (degrees per second)
        self.max_slew_rate_az = 30.0
        self.max_slew_rate_el = 20.0
        
        # Mock UDP socket (not actually sending in mock mode)
        self.socket = None
        
    def run(self):
        """Main thread loop - listens for slew commands"""
        self.set_online(True)
        
        # Connect signal for slew commands
        self.signal_bus.sig_slew_command.connect(self._handle_slew_command)
        
        # In mock mode, just keep thread alive
        while self._running:
            time.sleep(0.1)
        
        self.set_online(False)
    
    def _handle_slew_command(self, target_azimuth: float, target_elevation: float):
        """
        Handle slew command from signal bus.
        In production, this would format and send UDP packet.
        """
        try:
            print(f"[{self.name}] Slew command received: Az={target_azimuth:.1f}°, El={target_elevation:.1f}°")
            
            # Calculate slew required
            delta_az = target_azimuth - self.current_azimuth
            delta_el = target_elevation - self.current_elevation
            
            # Normalize azimuth delta to [-180, 180]
            if delta_az > 180:
                delta_az -= 360
            elif delta_az < -180:
                delta_az += 360
            
            # Calculate slew time
            time_az = abs(delta_az) / self.max_slew_rate_az
            time_el = abs(delta_el) / self.max_slew_rate_el
            slew_time = max(time_az, time_el)
            
            print(f"[{self.name}] Slewing from Az={self.current_azimuth:.1f}° to {target_azimuth:.1f}° "
                  f"(ΔAz={delta_az:.1f}°, time={slew_time:.2f}s)")
            
            # In production, send UDP packet here:
            # packet = self._format_slew_packet(target_azimuth, target_elevation)
            # self.socket.sendto(packet, (self.host, self.port))
            
            # Update current position
            self.current_azimuth = target_azimuth
            self.current_elevation = target_elevation
            
        except Exception as e:
            self.emit_error(f"Error handling slew command: {str(e)}")
    
    def _format_slew_packet(self, azimuth: float, elevation: float) -> bytes:
        """
        Format slew command as binary UDP packet.
        This is a placeholder for actual RWS protocol.
        """
        # Example binary format (would match actual RWS protocol):
        # Header (4 bytes) + Azimuth (4 bytes float) + Elevation (4 bytes float)
        import struct
        header = b'SLEW'
        packet = header + struct.pack('ff', azimuth, elevation)
        return packet
    
    def stop_driver(self):
        """Stop driver and cleanup"""
        if self.socket:
            self.socket.close()
        super().stop_driver()
