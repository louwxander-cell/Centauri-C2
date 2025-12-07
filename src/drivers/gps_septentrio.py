"""
Septentrio Mosaic-H Production GPS Driver
Holybro H-RTK Mosaic-H dual-antenna GNSS receiver

Provides:
- Position (lat/lon/altitude) from GGA/RMC
- True heading from dual-antenna (HDT)
- Speed and track from VTG
- High precision attitude from PSAT,HPR (Septentrio proprietary)
"""

import serial
import time
import math
from typing import Optional
from .base import BaseDriver
from ..core.bus import SignalBus
from ..core.datamodels import GeoPosition


class SeptentrioMosaicDriver(BaseDriver):
    """
    Production driver for Septentrio Mosaic-H dual-antenna GPS.
    
    Features:
    - NMEA 0183 parsing
    - Dual-antenna heading (compass-less)
    - High update rates (up to 100 Hz)
    - Septentrio proprietary sentence support
    """
    
    def __init__(self, port: str, baudrate: int = 115200, parent=None):
        super().__init__("SeptentrioGPS", parent)
        self.signal_bus = SignalBus.instance()
        
        # Connection parameters
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        
        # Current GNSS data
        self.lat = None
        self.lon = None
        self.heading = None  # True heading from HDT or PSAT
        self.altitude = None
        self.speed_mps = None
        self.track = None  # Course over ground
        self.fix_quality = None
        
        # Septentrio-specific (from PSAT,HPR)
        self.pitch = None
        self.roll = None
        self.baseline_length = None
        
        # Statistics and monitoring
        self.sentence_count = 0
        self.heading_count = 0
        self.last_fix_time = None
        self.last_heading_time = None
        
        # Flags
        self.heading_available = False
        
    def run(self):
        """Main thread loop - reads and parses NMEA sentences"""
        print(f"[{self.name}] Starting Septentrio Mosaic-H driver")
        print(f"[{self.name}]   Port: {self.port}")
        print(f"[{self.name}]   Baud: {self.baudrate}")
        print(f"[{self.name}]   Waiting for dual-antenna heading lock...")
        
        while self._running:
            try:
                # Open serial port
                if not self.serial:
                    self._open_serial()
                
                # Read NMEA sentence
                line = self.serial.readline().decode('ascii', errors='ignore').strip()
                
                if line.startswith('$'):
                    self._parse_nmea(line)
                    self.sentence_count += 1
                    
                    # Emit position if we have valid fix
                    if self.lat and self.lon:
                        position = GeoPosition(
                            lat=self.lat,
                            lon=self.lon,
                            heading=self.heading if self.heading is not None else 0.0,
                            altitude_m=self.altitude if self.altitude else 0.0,
                            speed_mps=self.speed_mps if self.speed_mps else 0.0,
                            timestamp=time.time()
                        )
                        self.signal_bus.emit_ownship(position)
                        self.set_online(True)
                        self.last_fix_time = time.time()
                
                # Check for fix timeout (5 seconds)
                if self.last_fix_time and (time.time() - self.last_fix_time) > 5.0:
                    self.set_online(False)
                    self.emit_error("GPS fix lost (timeout)")
                    
            except serial.SerialException as e:
                self.emit_error(f"Serial error: {str(e)}")
                self.set_online(False)
                if self.serial:
                    self.serial.close()
                    self.serial = None
                time.sleep(5.0)  # Wait before retry
                
            except Exception as e:
                self.emit_error(f"Unexpected error: {str(e)}")
                time.sleep(1.0)
        
        # Cleanup
        if self.serial:
            self.serial.close()
        self.set_online(False)
        print(f"[{self.name}] GPS driver stopped")
    
    def _open_serial(self):
        """Open serial connection to GPS receiver"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1.0,
                write_timeout=1.0
            )
            print(f"[{self.name}] ✓ Serial port opened: {self.port} @ {self.baudrate} baud")
            
        except Exception as e:
            self.emit_error(f"Failed to open serial port {self.port}: {str(e)}")
            raise
    
    def _parse_nmea(self, sentence: str):
        """
        Parse NMEA sentence (standard and Septentrio-specific)
        
        Supported:
        - $GPGGA / $GNGGA - Position fix
        - $GPRMC / $GNRMC - Recommended minimum
        - $GPHDT / $GNHDT - True heading (dual-antenna)
        - $GPVTG / $GNVTG - Velocity and track
        - $PSAT,HPR - Septentrio heading/pitch/roll
        """
        try:
            # Handle Septentrio proprietary sentences
            if sentence.startswith('$PSAT'):
                self._parse_septentrio(sentence)
                return
            
            # Parse standard NMEA using simple parsing
            # (Using simple parsing instead of pynmea2 for reliability)
            parts = sentence.split(',')
            if not parts:
                return
            
            sentence_type = parts[0]
            
            # GGA - Position fix data
            if 'GGA' in sentence_type:
                self._parse_gga(parts)
            
            # RMC - Recommended minimum
            elif 'RMC' in sentence_type:
                self._parse_rmc(parts)
            
            # HDT - True heading (CRITICAL for dual-antenna)
            elif 'HDT' in sentence_type:
                self._parse_hdt(parts)
            
            # VTG - Velocity and track
            elif 'VTG' in sentence_type:
                self._parse_vtg(parts)
                
        except Exception as e:
            # Silently ignore parse errors (common with corrupt sentences)
            pass
    
    def _parse_gga(self, parts):
        """Parse $GPGGA sentence - Position fix"""
        try:
            if len(parts) < 10:
                return
            
            # Latitude
            if parts[2] and parts[3]:
                lat_str = parts[2]
                lat_deg = float(lat_str[:2])
                lat_min = float(lat_str[2:])
                self.lat = lat_deg + (lat_min / 60.0)
                if parts[3] == 'S':
                    self.lat = -self.lat
            
            # Longitude
            if parts[4] and parts[5]:
                lon_str = parts[4]
                lon_deg = float(lon_str[:3])
                lon_min = float(lon_str[3:])
                self.lon = lon_deg + (lon_min / 60.0)
                if parts[5] == 'W':
                    self.lon = -self.lon
            
            # Fix quality
            if parts[6]:
                self.fix_quality = int(parts[6])
            
            # Altitude
            if parts[9]:
                self.altitude = float(parts[9])
                
        except (ValueError, IndexError):
            pass
    
    def _parse_rmc(self, parts):
        """Parse $GPRMC sentence - Recommended minimum"""
        try:
            if len(parts) < 9:
                return
            
            # Latitude (if not already from GGA)
            if parts[3] and parts[4] and not self.lat:
                lat_str = parts[3]
                lat_deg = float(lat_str[:2])
                lat_min = float(lat_str[2:])
                self.lat = lat_deg + (lat_min / 60.0)
                if parts[4] == 'S':
                    self.lat = -self.lat
            
            # Longitude
            if parts[5] and parts[6] and not self.lon:
                lon_str = parts[5]
                lon_deg = float(lon_str[:3])
                lon_min = float(lon_str[3:])
                self.lon = lon_deg + (lon_min / 60.0)
                if parts[6] == 'W':
                    self.lon = -self.lon
            
            # Speed (knots to m/s)
            if parts[7]:
                speed_knots = float(parts[7])
                self.speed_mps = speed_knots * 0.514444
            
            # Track angle
            if parts[8]:
                self.track = float(parts[8])
                
        except (ValueError, IndexError):
            pass
    
    def _parse_hdt(self, parts):
        """Parse $GPHDT sentence - True heading (dual-antenna)"""
        try:
            if len(parts) < 2:
                return
            
            if parts[1]:
                self.heading = float(parts[1])
                self.heading_count += 1
                self.last_heading_time = time.time()
                
                # Log first heading lock
                if not self.heading_available:
                    self.heading_available = True
                    print(f"[{self.name}] ✓ Dual-antenna heading lock acquired: {self.heading:.1f}°")
                    
        except (ValueError, IndexError):
            pass
    
    def _parse_vtg(self, parts):
        """Parse $GPVTG sentence - Velocity and track"""
        try:
            if len(parts) < 8:
                return
            
            # True track (backup for heading if HDT not available)
            if parts[1]:
                self.track = float(parts[1])
                if self.heading is None:
                    self.heading = self.track
            
            # Speed (km/h to m/s)
            if parts[7]:
                speed_kmh = float(parts[7])
                self.speed_mps = speed_kmh / 3.6
                
        except (ValueError, IndexError):
            pass
    
    def _parse_septentrio(self, sentence: str):
        """
        Parse Septentrio proprietary sentences
        
        $PSAT,HPR - Heading, Pitch, Roll (high precision)
        Format: $PSAT,HPR,timestamp,heading,pitch,roll,baseline_length,mode*checksum
        """
        try:
            parts = sentence.split(',')
            
            if len(parts) < 2:
                return
            
            # PSAT,HPR - High precision heading/pitch/roll
            if parts[1] == 'HPR' and len(parts) >= 7:
                heading = float(parts[3])
                pitch = float(parts[4])
                roll = float(parts[5])
                baseline = float(parts[6].split('*')[0]) if parts[6] else None
                
                self.heading = heading
                self.pitch = pitch
                self.roll = roll
                self.baseline_length = baseline
                self.heading_count += 1
                self.last_heading_time = time.time()
                
                # Log first HPR lock
                if not self.heading_available:
                    self.heading_available = True
                    print(f"[{self.name}] ✓ Septentrio HPR lock: H={heading:.1f}° P={pitch:.1f}° R={roll:.1f}°")
                    if baseline:
                        print(f"[{self.name}]   Baseline: {baseline:.2f}m")
                    
        except (ValueError, IndexError):
            pass
    
    def get_latest_position(self) -> dict:
        """Get latest GPS position data for integration"""
        has_position = self.lat is not None and self.lon is not None
        
        return {
            'valid': has_position,
            'latitude': self.lat if self.lat is not None else 0.0,
            'longitude': self.lon if self.lon is not None else 0.0,
            'altitude': self.altitude if self.altitude is not None else 0.0,
            'heading': self.heading if self.heading is not None else 0.0,
            'speed_mps': self.speed_mps if self.speed_mps is not None else 0.0,
            'fix_quality': self.fix_quality,
            'heading_available': self.heading_available
        }
    
    def get_status(self) -> dict:
        """Get current GPS status for monitoring"""
        return {
            'online': self.online,
            'port': self.port,
            'position': (self.lat, self.lon) if self.lat and self.lon else None,
            'heading': self.heading,
            'altitude': self.altitude,
            'speed_mps': self.speed_mps,
            'fix_quality': self.fix_quality,
            'heading_available': self.heading_available,
            'sentence_count': self.sentence_count,
            'heading_count': self.heading_count,
            'pitch': self.pitch,
            'roll': self.roll,
            'baseline': self.baseline_length
        }
