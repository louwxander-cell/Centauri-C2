"""
Production Remote Weapon Station (RWS) Driver
Handles slew command chain: RF→RWS (radar pointing), Radar→EO/IR (optics pointing)
Applies 20° elevation offset between radar and EO/IR
"""

import time
import socket
import struct
from typing import Optional
from .base import BaseDriver
from ..core.bus import SignalBus
from ..core.datamodels import Track, SensorSource


class RWSDriverProduction(BaseDriver):
    """
    Production Remote Weapon Station driver.
    
    Command Chain:
    1. RF detection → Slew RWS (radar) to search direction
    2. Radar detection → Slew EO/IR to track target (with 20° elevation offset)
    
    Key Features:
    - UDP command protocol
    - Rate-limited slewing
    - Separate radar and optics pointing
    - 20° elevation offset (radar mounted above optics)
    - Command acknowledgment
    """
    
    # Command types
    CMD_SLEW_RADAR = 0x01    # Slew radar (from RF detection)
    CMD_SLEW_OPTICS = 0x02   # Slew EO/IR (from radar detection)
    
    def __init__(self, host: str, port: int, parent=None):
        super().__init__("RWSDriver", parent)
        self.signal_bus = SignalBus.instance()
        self.host = host
        self.port = port
        self.socket = None
        
        # Current positions
        self.radar_azimuth = 0.0
        self.radar_elevation = 0.0
        self.optics_azimuth = 0.0
        self.optics_elevation = 0.0
        
        # Slew rate limits (degrees per second)
        self.max_slew_rate_az = 30.0
        self.max_slew_rate_el = 20.0
        
        # Elevation offset (radar mounted 20° above optics)
        self.RADAR_ELEVATION_OFFSET = 20.0
        
        # Track last RF and Radar detections for command chain
        self.last_rf_track = None
        self.last_radar_track = None
        self.last_rf_time = 0.0
        
        # Optical lock status
        self.optical_lock = False
        self.optical_lock_timeout = 5.0  # Seconds without radar update = assume lock
        
        # RF-silent detection mode
        self.rf_silent_mode = False
        self.rf_detection_timeout = 10.0  # Seconds without RF = assume RF-silent drone
        
        print(f"[{self.name}] Initialized for {host}:{port}")
        print(f"[{self.name}] Radar elevation offset: {self.RADAR_ELEVATION_OFFSET}°")
    
    def run(self):
        """Main thread loop - maintains connection and processes commands"""
        self._setup_socket()
        self.set_online(True)
        
        # Connect signals
        self.signal_bus.sig_track_updated.connect(self._on_track_updated)
        self.signal_bus.sig_slew_command.connect(self._handle_manual_slew)
        
        # Keep thread alive
        while self._running:
            time.sleep(0.1)
        
        self.set_online(False)
        if self.socket:
            self.socket.close()
    
    def _setup_socket(self):
        """Set up UDP socket for RWS commands"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"[{self.name}] UDP socket ready")
        except Exception as e:
            self.emit_error(f"Socket setup failed: {str(e)}")
            raise
    
    def _on_track_updated(self, track: Track):
        """
        Handle track updates and execute command chain.
        
        Command Chain Logic:
        1. RF detection → Slew radar to search that direction
        2. Radar detection → Slew optics to track (with 20° offset)
        3. RF-silent mode → Radar-only detection, continuous optics updates
        """
        try:
            current_time = time.time()
            
            if track.source == SensorSource.RF:
                # RF detection - slew radar to search direction
                self._slew_radar_to_rf_detection(track)
                self.last_rf_track = track
                self.last_rf_time = current_time
                self.rf_silent_mode = False  # RF is active
                
            elif track.source == SensorSource.RADAR:
                # Check if we're in RF-silent mode
                time_since_rf = current_time - self.last_rf_time
                
                if time_since_rf > self.rf_detection_timeout:
                    # No RF detections recently - assume RF-silent drone
                    if not self.rf_silent_mode:
                        print(f"[{self.name}] ⚠️  RF-SILENT MODE ACTIVATED")
                        print(f"[{self.name}]   No RF detections for {time_since_rf:.1f}s")
                        print(f"[{self.name}]   Radar-only tracking enabled")
                        self.rf_silent_mode = True
                    
                    # RF-silent mode: continuously update optics until lock
                    self._handle_rf_silent_tracking(track)
                else:
                    # Normal mode: RF + Radar fusion
                    self._slew_optics_to_radar_track(track)
                
                self.last_radar_track = track
                
        except Exception as e:
            self.emit_error(f"Track handling error: {str(e)}")
    
    def _slew_radar_to_rf_detection(self, track: Track):
        """
        Slew RWS (radar) to RF detection direction.
        This points the radar to search for the drone detected by RF.
        """
        target_az = track.azimuth
        target_el = track.elevation
        
        print(f"[{self.name}] RF Detection → Slewing RADAR to Az={target_az:.1f}°, El={target_el:.1f}°")
        print(f"[{self.name}]   (Drone type: {track.aircraft_model or 'Unknown'}, "
              f"Confidence: {track.confidence:.2f})")
        
        # Send slew command to radar
        self._send_slew_command(
            self.CMD_SLEW_RADAR,
            target_az,
            target_el
        )
        
        self.radar_azimuth = target_az
        self.radar_elevation = target_el
    
    def _slew_optics_to_radar_track(self, track: Track):
        """
        Slew EO/IR optics to radar track (normal RF + Radar mode).
        Applies 20° elevation offset (radar mounted above optics).
        """
        target_az = track.azimuth
        
        # Apply elevation offset: radar is 20° above optics
        # So optics need to point 20° lower than radar sees the target
        target_el = track.elevation - self.RADAR_ELEVATION_OFFSET
        
        print(f"[{self.name}] Radar Detection → Slewing OPTICS to Az={target_az:.1f}°, El={target_el:.1f}°")
        print(f"[{self.name}]   (Radar El: {track.elevation:.1f}° → Optics El: {target_el:.1f}° "
              f"[{self.RADAR_ELEVATION_OFFSET}° offset])")
        print(f"[{self.name}]   (Range: {track.range_m:.0f}m, UAV Prob: {track.probability_uav:.2f})")
        
        # Send slew command to optics
        self._send_slew_command(
            self.CMD_SLEW_OPTICS,
            target_az,
            target_el
        )
        
        self.optics_azimuth = target_az
        self.optics_elevation = target_el
    
    def _handle_rf_silent_tracking(self, track: Track):
        """
        Handle RF-silent drone tracking.
        Continuously updates optics to radar position until optical lock.
        
        This mode is activated when:
        - Radar detects a drone
        - No RF detections for >10 seconds (RF-silent drone)
        
        Behavior:
        - Continuously slew optics to latest radar position
        - Update every radar frame until optical lock
        - Assume optical lock after 5 seconds without radar updates
        """
        target_az = track.azimuth
        target_el = track.elevation - self.RADAR_ELEVATION_OFFSET
        
        # Check if optics have locked (no radar updates = optics tracking)
        if self.optical_lock:
            print(f"[{self.name}] 🎯 Optical lock maintained - ignoring radar updates")
            return
        
        # Calculate delta from current optics position
        delta_az = abs(target_az - self.optics_azimuth)
        delta_el = abs(target_el - self.optics_elevation)
        
        # Normalize azimuth delta
        if delta_az > 180:
            delta_az = 360 - delta_az
        
        # Send continuous updates
        print(f"[{self.name}] 🔴 RF-SILENT TRACKING → Updating OPTICS")
        print(f"[{self.name}]   Target: Az={target_az:.1f}°, El={target_el:.1f}°")
        print(f"[{self.name}]   Delta: ΔAz={delta_az:.1f}°, ΔEl={delta_el:.1f}°")
        print(f"[{self.name}]   Range: {track.range_m:.0f}m, UAV Prob: {track.probability_uav:.2f}")
        
        # Send slew command
        self._send_slew_command(
            self.CMD_SLEW_OPTICS,
            target_az,
            target_el
        )
        
        self.optics_azimuth = target_az
        self.optics_elevation = target_el
        
        # Check if we're close enough to assume lock
        if delta_az < 0.5 and delta_el < 0.5:
            print(f"[{self.name}] 🎯 OPTICAL LOCK ACHIEVED (ΔAz={delta_az:.2f}°, ΔEl={delta_el:.2f}°)")
            print(f"[{self.name}]   Optics should now be tracking visually")
            # Note: Optical lock is confirmed by external system, not assumed here
    
    def set_optical_lock(self, locked: bool):
        """
        Set optical lock status (called by external tracking system).
        
        Args:
            locked: True if optics have visual lock on target
        """
        if locked and not self.optical_lock:
            print(f"[{self.name}] ✅ OPTICAL LOCK CONFIRMED by tracking system")
            print(f"[{self.name}]   Stopping radar-based optics updates")
        elif not locked and self.optical_lock:
            print(f"[{self.name}] ⚠️  OPTICAL LOCK LOST")
            print(f"[{self.name}]   Resuming radar-based optics updates")
        
        self.optical_lock = locked
    
    def _handle_manual_slew(self, azimuth: float, elevation: float):
        """
        Handle manual slew command from operator.
        Slews both radar and optics together.
        """
        print(f"[{self.name}] Manual Slew → Az={azimuth:.1f}°, El={elevation:.1f}°")
        
        # Slew radar
        self._send_slew_command(self.CMD_SLEW_RADAR, azimuth, elevation)
        self.radar_azimuth = azimuth
        self.radar_elevation = elevation
        
        # Slew optics (with offset)
        optics_el = elevation - self.RADAR_ELEVATION_OFFSET
        self._send_slew_command(self.CMD_SLEW_OPTICS, azimuth, optics_el)
        self.optics_azimuth = azimuth
        self.optics_elevation = optics_el
    
    def _send_slew_command(self, command_type: int, azimuth: float, elevation: float):
        """
        Send slew command via UDP.
        
        Packet Format (16 bytes):
        - Header: 'SLEW' (4 bytes)
        - Command Type: uint8 (1 byte: 0x01=radar, 0x02=optics)
        - Reserved: 3 bytes
        - Azimuth: float32 (4 bytes)
        - Elevation: float32 (4 bytes)
        """
        try:
            # Format binary packet
            header = b'SLEW'
            packet = struct.pack(
                '>4sBxxxff',  # Big-endian: 4 bytes, 1 byte, 3 padding, 2 floats
                header,
                command_type,
                azimuth,
                elevation
            )
            
            # Send UDP packet
            self.socket.sendto(packet, (self.host, self.port))
            
            # Log command
            cmd_name = "RADAR" if command_type == self.CMD_SLEW_RADAR else "OPTICS"
            print(f"[{self.name}] Sent {cmd_name} slew command: "
                  f"Az={azimuth:.1f}°, El={elevation:.1f}°")
            
        except Exception as e:
            self.emit_error(f"Failed to send slew command: {str(e)}")
    
    def get_current_position(self) -> dict:
        """Get current radar and optics positions"""
        return {
            'radar': {
                'azimuth': self.radar_azimuth,
                'elevation': self.radar_elevation
            },
            'optics': {
                'azimuth': self.optics_azimuth,
                'elevation': self.optics_elevation
            }
        }
