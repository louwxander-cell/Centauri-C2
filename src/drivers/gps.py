"""Mock GPS/Compass driver - simulates NMEA stream"""

import time
import math
from .base import BaseDriver
from ..core.bus import SignalBus
from ..core.datamodels import GeoPosition


class GPSDriver(BaseDriver):
    """
    Mock GPS/Compass driver.
    Simulates NMEA stream with ownship position and heading.
    In production, this would read from serial port (e.g., /dev/ttyUSB0).
    """
    
    def __init__(self, parent=None):
        super().__init__("GPSDriver", parent)
        self.signal_bus = SignalBus.instance()
        
        # Simulation parameters
        self.update_interval_ms = 1000  # 1 Hz update rate
        
        # Starting position (Pretoria, South Africa - default location)
        self.base_lat = -25.841105
        self.base_lon = 28.180340
        self.base_altitude = 1339.0  # meters MSL (Pretoria elevation)
        
        # Vehicle motion simulation
        self.speed_mps = 5.0  # 5 m/s (~11 mph)
        self.heading_rate = 0.5  # degrees per second
        
    def run(self):
        """Main thread loop - generates GPS position updates"""
        self.set_online(True)
        
        iteration = 0
        current_heading = 0.0
        
        while self._running:
            try:
                # Update heading (slow rotation)
                current_heading = (current_heading + self.heading_rate) % 360
                
                # Calculate position offset (vehicle moving in circle)
                # Convert to lat/lon offset (approximate)
                meters_per_degree_lat = 111320.0
                meters_per_degree_lon = 111320.0 * math.cos(math.radians(self.base_lat))
                
                radius_m = 100.0  # 100m radius circle
                angle_rad = math.radians(iteration * 0.5)
                
                offset_lat = (radius_m * math.sin(angle_rad)) / meters_per_degree_lat
                offset_lon = (radius_m * math.cos(angle_rad)) / meters_per_degree_lon
                
                position = GeoPosition(
                    lat=self.base_lat + offset_lat,
                    lon=self.base_lon + offset_lon,
                    heading=current_heading,
                    altitude_m=self.base_altitude,
                    speed_mps=self.speed_mps,
                    timestamp=time.time()
                )
                
                self.signal_bus.emit_ownship(position)
                
                time.sleep(self.update_interval_ms / 1000.0)
                iteration += 1
                
            except Exception as e:
                self.emit_error(f"Error in GPS loop: {str(e)}")
                time.sleep(1.0)
        
        self.set_online(False)
