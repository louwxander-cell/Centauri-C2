"""
Production BlueHalo SkyView DIVR MkII RF Driver
Connects via TLS socket and parses JSON detection messages
Applies GPS heading correction for vehicle-mounted sensor
"""

import ssl
import socket
import json
import time
import math
import hashlib
from typing import Optional, Dict
from pathlib import Path
from .base import BaseDriver
from ..core.bus import SignalBus
from ..core.datamodels import Track, SensorSource, TargetType, GeoPosition


class RFDriverProduction(BaseDriver):
    """
    Production BlueHalo SkyView DIVR MkII RF sensor driver.
    
    Key Features:
    - TLS 1.2 secure socket connection
    - JSON message parsing
    - Precision detections (lat/lon, pilot position, serial numbers)
    - Sector detections (45° bearing)
    - GPS heading correction for vehicle-mounted sensor
    - DIVR MKII sector alignment (22.5° offset from True North)
    """
    
    def __init__(self, host: str, port: int, cert_dir: str, parent=None):
        super().__init__("RFDriver", parent)
        self.signal_bus = SignalBus.instance()
        self.host = host
        self.port = port
        self.cert_dir = Path(cert_dir)
        self.ssl_sock = None
        self.buffer = b''
        
        # Current ownship position and heading
        self.ownship_lat = None
        self.ownship_lon = None
        self.ownship_heading = 0.0  # True heading from GPS
        
        # Connect to ownship position updates
        self.signal_bus.sig_ownship_updated.connect(self._on_ownship_updated)
        
        print(f"[{self.name}] Initialized for {host}:{port}")
        print(f"[{self.name}] Certificate directory: {cert_dir}")
    
    def run(self):
        """Main thread loop - maintains TLS connection and receives detections"""
        while self._running:
            try:
                # Connect to SkyView
                if not self.ssl_sock:
                    self._connect_tls()
                
                # Receive data
                data = self.ssl_sock.recv(8192)
                if not data:
                    print(f"[{self.name}] Connection closed by SkyView")
                    self.set_online(False)
                    self.ssl_sock.close()
                    self.ssl_sock = None
                    time.sleep(5.0)
                    continue
                
                self.set_online(True)
                self.buffer += data
                
                # Parse JSON messages (newline-delimited)
                self._parse_messages()
                
            except socket.timeout:
                continue
            except ConnectionRefusedError:
                self.emit_error(f"Connection refused to {self.host}:{self.port}")
                self.set_online(False)
                time.sleep(10.0)
            except ssl.SSLError as e:
                self.emit_error(f"SSL error: {str(e)}")
                self.set_online(False)
                if self.ssl_sock:
                    self.ssl_sock.close()
                    self.ssl_sock = None
                time.sleep(10.0)
            except Exception as e:
                self.emit_error(f"RF sensor error: {str(e)}")
                self.set_online(False)
                if self.ssl_sock:
                    self.ssl_sock.close()
                    self.ssl_sock = None
                time.sleep(5.0)
        
        self.set_online(False)
        if self.ssl_sock:
            self.ssl_sock.close()
    
    def _connect_tls(self):
        """Connect to SkyView via TLS"""
        try:
            print(f"[{self.name}] Connecting to {self.host}:{self.port} via TLS...")
            
            # Set up SSL context
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            
            # Load client certificate and key
            cert_file = self.cert_dir / 'ott.verustechnologygroup.com.cert.pem'
            key_file = self.cert_dir / 'ott.verustechnologygroup.com.key.pem'
            ca_file = self.cert_dir / 'ca-chain.cert.pem'
            
            if not cert_file.exists():
                raise FileNotFoundError(f"Certificate not found: {cert_file}")
            if not key_file.exists():
                raise FileNotFoundError(f"Key not found: {key_file}")
            if not ca_file.exists():
                raise FileNotFoundError(f"CA chain not found: {ca_file}")
            
            context.load_cert_chain(certfile=str(cert_file), keyfile=str(key_file))
            context.load_verify_locations(str(ca_file))
            
            # Create socket and wrap with SSL
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10.0)
            self.ssl_sock = context.wrap_socket(sock, server_hostname=self.host)
            self.ssl_sock.connect((self.host, self.port))
            
            print(f"[{self.name}] TLS connection established")
            
            # Enable detection messages
            command = '{"detectionStatusEnabled":true}\n'
            self.ssl_sock.sendall(command.encode('utf-8'))
            print(f"[{self.name}] Detection messages enabled")
            
        except Exception as e:
            self.emit_error(f"TLS connection failed: {str(e)}")
            raise
    
    def _on_ownship_updated(self, position: GeoPosition):
        """Update ownship position and heading"""
        self.ownship_lat = position.lat
        self.ownship_lon = position.lon
        if position.heading is not None:
            self.ownship_heading = position.heading
    
    def _parse_messages(self):
        """Parse JSON messages from buffer"""
        while b'\n' in self.buffer:
            line, self.buffer = self.buffer.split(b'\n', 1)
            
            if not line.strip():
                continue
            
            try:
                message = json.loads(line.decode('utf-8'))
                self._process_message(message)
            except json.JSONDecodeError as e:
                self.emit_error(f"JSON parse error: {str(e)}")
            except Exception as e:
                self.emit_error(f"Message processing error: {str(e)}")
    
    def _process_message(self, message: Dict):
        """Process a SkyView API message"""
        if 'DetectionPublication' not in message:
            return  # Not a detection message
        
        detection_pub = message['DetectionPublication']
        
        # Process omni detections (fact-of and precision)
        for detection in detection_pub.get('omniDetections', []):
            track = self._process_detection(detection, is_sector=False)
            if track:
                self.signal_bus.emit_track(track)
        
        # Process sector detections (45° bearing)
        for detection in detection_pub.get('sectorDetections', []):
            track = self._process_detection(detection, is_sector=True)
            if track:
                self.signal_bus.emit_track(track)
    
    def _process_detection(self, detection: Dict, is_sector: bool) -> Optional[Track]:
        """Process a single detection and convert to Track"""
        try:
            # Extract basic fields
            detection_id = detection.get('detectionId', '')
            detection_type = detection.get('detectionType', 'UNKNOWN')
            detection_label = detection.get('detectionLabel', 'Unknown')
            sector = detection.get('sector', 1)
            power = detection.get('power', 0.0)
            frequency = detection.get('frequency', 0)
            
            # Check if this is a precision detection
            aircraft_lat = detection.get('aircraftLatitude', 0)
            aircraft_lon = detection.get('aircraftLongitude', 0)
            aircraft_alt = detection.get('aircraftAltitude', 0)
            has_precision = (aircraft_lat != 0 or aircraft_lon != 0)
            
            # Extract RF-specific data
            serial = detection.get('serial')
            aircraft_model = detection.get('aircraftModel')
            pilot_lat = detection.get('pilotLatitude', 0) if detection.get('pilotLatitude') else None
            pilot_lon = detection.get('pilotLongitude', 0) if detection.get('pilotLongitude') else None
            
            # Generate track ID from detection ID (hash to integer)
            track_id = int(hashlib.md5(detection_id.encode()).hexdigest()[:8], 16) % 100000 + 100000
            
            # Calculate position
            if has_precision and self.ownship_lat and self.ownship_lon:
                # Precision detection - calculate Az/El/Range from lat/lon
                azimuth, elevation, range_m = self._calculate_relative_position(
                    aircraft_lat, aircraft_lon, aircraft_alt
                )
                confidence = 0.9  # High confidence for precision
            elif is_sector:
                # Sector detection - convert sector to azimuth
                # DIVR MKII: Sector 1 center = 22.5° from True North
                azimuth_true_north = (sector - 1) * 45.0 + 22.5
                
                # Apply GPS heading correction (vehicle-mounted)
                # Convert from True North to vehicle-relative
                azimuth = (azimuth_true_north - self.ownship_heading) % 360.0
                
                elevation = 0.0  # No elevation info for sector detections
                range_m = 3000.0  # Assume mid-range for sector detections
                confidence = 0.7  # Medium confidence for sector
            else:
                # Omni detection (fact-of only) - no location info
                # Skip these as they don't provide actionable data
                return None
            
            # Normalize confidence based on signal power
            # Higher power = higher confidence
            power_confidence = min(power / 100.0, 1.0) if power > 0 else 0.5
            confidence = (confidence + power_confidence) / 2.0
            
            # Create Track object
            track = Track(
                id=track_id,
                azimuth=azimuth,
                elevation=elevation,
                range_m=range_m,
                type=TargetType.DRONE,  # RF specifically detects drones
                confidence=confidence,
                source=SensorSource.RF,
                pilot_latitude=pilot_lat,
                pilot_longitude=pilot_lon,
                aircraft_model=aircraft_model,
                serial_number=serial,
                rf_frequency=frequency,
                rf_power=power,
                timestamp=time.time()
            )
            
            return track
            
        except Exception as e:
            self.emit_error(f"Detection processing error: {str(e)}")
            return None
    
    def _calculate_relative_position(self, target_lat: float, target_lon: float, 
                                    target_alt: float) -> tuple:
        """
        Calculate vehicle-relative azimuth, elevation, and range from lat/lon.
        Returns: (azimuth, elevation, range_m)
        """
        if not self.ownship_lat or not self.ownship_lon:
            return (0.0, 0.0, 1000.0)
        
        # Convert to radians
        lat1 = math.radians(self.ownship_lat)
        lon1 = math.radians(self.ownship_lon)
        lat2 = math.radians(target_lat)
        lon2 = math.radians(target_lon)
        
        # Calculate bearing (True North reference)
        dlon = lon2 - lon1
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        bearing_true_north = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0
        
        # Convert to vehicle-relative azimuth
        azimuth = (bearing_true_north - self.ownship_heading) % 360.0
        
        # Calculate horizontal distance (Haversine formula)
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        earth_radius = 6371000  # meters
        horizontal_range = earth_radius * c
        
        # Calculate elevation angle
        # Assume ownship altitude is 0 for simplicity (or get from GPS)
        elevation = math.degrees(math.atan2(target_alt, horizontal_range))
        
        # Calculate slant range
        range_m = math.sqrt(horizontal_range**2 + target_alt**2)
        
        return (azimuth, elevation, range_m)
