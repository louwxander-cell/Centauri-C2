"""
Production Echodyne Echoguard Radar Driver
Connects via TCP and parses binary track packets
Coordinates are vehicle-relative (0° = forward)
"""

import socket
import struct
import time
import math
from typing import Optional
from .base import BaseDriver
from ..core.bus import SignalBus
from ..core.datamodels import Track, SensorSource, TargetType


class RadarDriverProduction(BaseDriver):
    """
    Production Echodyne Echoguard radar driver.
    
    Key Features:
    - TCP connection to radar
    - Binary packet parsing (BNET protocol)
    - Vehicle-relative coordinates (0° = forward)
    - UAV probability classification
    - Automatic track timeout handling
    """
    
    def __init__(self, host: str, port: int, parent=None):
        super().__init__("RadarDriver", parent)
        self.signal_bus = SignalBus.instance()
        self.host = host
        self.port = port
        self.socket = None
        self.buffer = b''
        
        # Track header format (28 bytes)
        self.header_format = '<12sIIIIIII'
        self.header_size = struct.calcsize(self.header_format)
        
        # Track data format (248 bytes per track)
        self.track_format = '<'
        self.track_format += 'II'      # ID, state
        self.track_format += 'fff'     # azest, elest, rest
        self.track_format += 'fff'     # xest, yest, zest
        self.track_format += 'fff'     # velxest, velyest, velzest
        self.track_format += 'III'     # assocMeas_id_main[3]
        self.track_format += 'fff'     # assocMeas_chi2_main[3]
        self.track_format += 'ii'      # TOCA_days, TOCA_ms
        self.track_format += 'f'       # DOCA
        self.track_format += 'f'       # lifetime
        self.track_format += 'II'      # lastUpdateTime_days, lastUpdateTime_ms
        self.track_format += 'II'      # lastAssociatedDataTime_days, lastAssociatedDataTime_ms
        self.track_format += 'II'      # acquiredTime_days, acquiredTime_ms
        self.track_format += 'f'       # estConfidence
        self.track_format += 'I'       # numAssocMeasurements
        self.track_format += 'f'       # estRCS
        self.track_format += 'ff'      # probabilityOther, probabilityUAV
        self.track_size = struct.calcsize(self.track_format)
        
        print(f"[{self.name}] Initialized for {host}:{port}")
        print(f"[{self.name}] Header size: {self.header_size} bytes")
        print(f"[{self.name}] Track size: {self.track_size} bytes")
    
    def run(self):
        """Main thread loop - connects and receives radar data"""
        while self._running:
            try:
                # Connect to radar
                if not self.socket:
                    self._connect()
                
                # Receive data
                data = self.socket.recv(4096)
                if not data:
                    print(f"[{self.name}] Connection closed by radar")
                    self.set_online(False)
                    self.socket.close()
                    self.socket = None
                    time.sleep(5.0)
                    continue
                
                self.set_online(True)
                self.buffer += data
                
                # Parse packets from buffer
                self._parse_packets()
                
            except socket.timeout:
                continue
            except ConnectionRefusedError:
                self.emit_error(f"Connection refused to {self.host}:{self.port}")
                self.set_online(False)
                time.sleep(10.0)
            except Exception as e:
                self.emit_error(f"Radar error: {str(e)}")
                self.set_online(False)
                if self.socket:
                    self.socket.close()
                    self.socket = None
                time.sleep(5.0)
        
        self.set_online(False)
        if self.socket:
            self.socket.close()
    
    def _connect(self):
        """Connect to radar TCP server"""
        try:
            print(f"[{self.name}] Connecting to {self.host}:{self.port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.host, self.port))
            print(f"[{self.name}] Connected successfully")
        except Exception as e:
            self.emit_error(f"Connection failed: {str(e)}")
            raise
    
    def _parse_packets(self):
        """Parse track packets from buffer"""
        while len(self.buffer) >= self.header_size:
            # Parse header
            header_data = self.buffer[:self.header_size]
            header = struct.unpack(self.header_format, header_data)
            
            packet_tag = header[0].decode('ascii', errors='ignore')
            packet_size = header[1]
            n_tracks = header[2]
            sys_time_days = header[3]
            sys_time_ms = header[4]
            
            # Validate packet tag
            if not packet_tag.startswith('<track'):
                # Invalid packet, try to resync
                self.buffer = self.buffer[1:]
                continue
            
            # Check if we have the full packet
            if len(self.buffer) < packet_size:
                break  # Wait for more data
            
            # Extract packet data
            packet_data = self.buffer[self.header_size:packet_size]
            self.buffer = self.buffer[packet_size:]
            
            # Parse tracks
            offset = 0
            for i in range(n_tracks):
                if offset + self.track_size > len(packet_data):
                    break
                
                track_data = packet_data[offset:offset + self.track_size]
                track = self._parse_track(track_data, sys_time_days, sys_time_ms)
                
                if track:
                    self.signal_bus.emit_track(track)
                
                offset += self.track_size
    
    def _parse_track(self, data: bytes, sys_time_days: int, sys_time_ms: int) -> Optional[Track]:
        """Parse a single track from binary data"""
        try:
            fields = struct.unpack(self.track_format, data)
            
            track_id = fields[0]
            state = fields[1]
            azimuth = fields[2]      # Azimuth (degrees, vehicle-relative)
            elevation = fields[3]    # Elevation (degrees)
            range_m = fields[4]      # Range (meters)
            x = fields[5]            # X position (meters)
            y = fields[6]            # Y position (meters)
            z = fields[7]            # Z position (meters)
            vx = fields[8]           # X velocity (m/s)
            vy = fields[9]           # Y velocity (m/s)
            vz = fields[10]          # Z velocity (m/s)
            lifetime = fields[20]    # Track lifetime (seconds)
            confidence = fields[27]  # Confidence
            rcs = fields[29]         # RCS (m²)
            prob_other = fields[30]  # Probability other
            prob_uav = fields[31]    # Probability UAV
            
            # Normalize azimuth to 0-360
            azimuth = azimuth % 360.0
            if azimuth < 0:
                azimuth += 360.0
            
            # Calculate velocity magnitude
            velocity = math.sqrt(vx**2 + vy**2 + vz**2)
            
            # Calculate heading from velocity
            heading = None
            if abs(vx) > 0.1 or abs(vy) > 0.1:
                heading = (math.degrees(math.atan2(vy, vx)) + 90.0) % 360.0
            
            # Classify target based on UAV probability
            target_type = TargetType.UNKNOWN
            if prob_uav > 0.7:
                target_type = TargetType.DRONE
            elif prob_uav < 0.3 and prob_other > 0.7:
                target_type = TargetType.BIRD
            
            # Normalize confidence (radar gives raw values, normalize to 0-1)
            # Typical confidence range is 0-100, so divide by 100
            normalized_confidence = min(confidence / 100.0, 1.0)
            
            # Create Track object
            track = Track(
                id=track_id,
                azimuth=azimuth,
                elevation=elevation,
                range_m=range_m,
                type=target_type,
                confidence=normalized_confidence,
                source=SensorSource.RADAR,
                velocity_mps=velocity,
                heading=heading,
                rcs=rcs,
                probability_uav=prob_uav,
                timestamp=time.time()
            )
            
            return track
            
        except Exception as e:
            self.emit_error(f"Track parsing error: {str(e)}")
            return None
