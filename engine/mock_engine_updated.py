#!/usr/bin/env python3
"""
Mock TriAD Engine - Updated with Real Sensor Characteristics
Simulates: Echodyne Echoguard Radar + BlueHalo SkyView DIVR MkII RF
"""

import time
import random
import math
from typing import Dict, List, Optional
from PySide6.QtCore import QObject, Slot


class MockRadarSensor:
    """
    Simulates Echodyne Echoguard radar characteristics
    - Binary BNET protocol (TCP)
    - 248 bytes per track
    - Vehicle-relative coordinates
    - UAV probability classification
    """
    
    def __init__(self):
        self.tracks = {}
        self.next_track_id = 1001
        self.update_rate_hz = 10.0
        
    def generate_tracks(self) -> List[Dict]:
        """Generate radar tracks with Echoguard-specific fields"""
        tracks = []
        
        # Initialize persistent tracks if empty (4 tracks for normal operation)
        if not self.tracks:
            for i in range(4):
                track_id = 1000 + i
                self.tracks[track_id] = {
                    'id': track_id,
                    'first_detection': time.time_ns(),
                    'azimuth_deg': random.uniform(0, 360),
                    'range_m': random.uniform(500, 2500)
                }
        
        # Update all persistent tracks
        for track_id, track in list(self.tracks.items()):
            
            # Update position (small movement)
            track['azimuth_deg'] += random.uniform(-0.5, 0.5)
            if track['azimuth_deg'] < 0:
                track['azimuth_deg'] += 360
            if track['azimuth_deg'] >= 360:
                track['azimuth_deg'] -= 360
            
            track['range_m'] += random.uniform(-10, 10)
            track['range_m'] = max(500, min(3000, track['range_m']))
            
            # Echoguard-specific fields
            lifetime = (time.time_ns() - track['first_detection']) / 1e9
            
            az_deg = track['azimuth_deg']
            el_deg = track.get('elevation_deg', 15.0)
            speed = track.get('speed_mps', track.get('velocity_mps', 20.0))
            
            # Calculate velocity components from actual movement
            # Convert azimuth to radians and calculate x,y components
            # Azimuth 0 = North, 90 = East (standard navigation)
            az_rad = math.radians(az_deg)
            direction = track.get('direction', 1)  # 1 = away, -1 = toward
            
            # Calculate range rate (radial velocity)
            range_rate_mps = speed * direction  # Positive = moving away
            
            # Calculate velocity components in East-North frame
            # For approaching tracks, velocity points toward center (opposite of azimuth)
            # For departing tracks, velocity points away from center (same as azimuth)
            velocity_x_mps = range_rate_mps * math.sin(az_rad)  # East component
            velocity_y_mps = range_rate_mps * math.cos(az_rad)  # North component
            
            tracks.append({
                'id': track['id'],
                'azimuth_deg': az_deg,
                'az_deg': az_deg,  # UI compatibility
                'elevation_deg': el_deg,
                'el_deg': el_deg,  # UI compatibility
                'range_m': track['range_m'],
                'velocity_x_mps': velocity_x_mps,
                'velocity_y_mps': velocity_y_mps,
                'velocity_z_mps': 0.0,  # Simplified - no vertical motion
                'speed_mps': speed,  # UI compatibility
                'velocity_mps': speed,  # UI compatibility
                'heading_deg': random.uniform(0, 360),
                'type': 'UAV',
                'confidence': 0.75 + random.uniform(-0.1, 0.1),
                'source': 'RADAR',
                'status': 'TRACKING',
                # Radar-specific
                'rcs_m2': random.uniform(0.01, 0.1),  # Small UAV RCS
                'probability_uav': 0.85 + random.uniform(-0.1, 0.1),
                'probability_other': 0.15 + random.uniform(-0.1, 0.1),
                'num_associated_meas': random.randint(10, 50),
                'est_confidence': 0.8 + random.uniform(-0.1, 0.1),
                'lifetime_sec': lifetime,
                'last_update_ns': time.time_ns()
            })
        
        return tracks


class MockRFSensor:
    """
    Simulates BlueHalo SkyView DIVR MkII characteristics
    - TLS 1.2 JSON messages
    - Precision detections (lat/lon, pilot, serial)
    - Sector detections (45° sectors)
    - 22.5° sector offset from True North
    """
    
    SECTOR_WIDTH_DEG = 45.0
    SECTOR_OFFSET_DEG = 22.5  # DIVR MKII specific
    
    def __init__(self, ownship_lat: float = -25.841105, ownship_lon: float = 28.180340):
        self.ownship_lat = ownship_lat
        self.ownship_lon = ownship_lon
        self.ownship_heading = 90.0
        self.detections = {}
        self.next_detection_id = 2001
        
        # Simulated drone models
        self.drone_models = [
            "DJI Mavic 3",
            "DJI Phantom 4 Pro",
            "Autel EVO II",
            "DJI Mini 3"
        ]
    
    def generate_detections(self) -> List[Dict]:
        """Generate RF detections with SkyView-specific fields"""
        detections = []
        
        # Initialize persistent detections if empty (2 detections for normal operation)
        if not self.detections:
            for i in range(2):
                detection_id = 2000 + i
                detection_mode = random.choice(["PRECISION", "SECTOR"])
                
                self.detections[detection_id] = {
                    'id': detection_id,
                    'first_detection': time.time_ns(),
                    'mode': detection_mode,
                    'azimuth_deg': random.uniform(0, 360),
                    'model': random.choice(self.drone_models)
                }
        
        # Update all persistent detections
        for detection_id, det in list(self.detections.items()):
            # Slight azimuth drift for realism
            det['azimuth_deg'] += random.uniform(-0.3, 0.3)
            det['azimuth_deg'] %= 360
            
            # Apply 22.5° sector offset for DIVR MKII
            true_north_bearing = det['azimuth_deg']
            sensor_bearing = (true_north_bearing - self.SECTOR_OFFSET_DEG) % 360
            
            # Convert to vehicle-relative (0° = vehicle forward)
            vehicle_rel_azimuth = (sensor_bearing - self.ownship_heading) % 360
            
            if det['mode'] == "PRECISION":
                # Precision mode: lat/lon, pilot position, serial
                # Calculate drone position (simulated)
                range_m = random.uniform(1000, 3000)
                bearing_rad = math.radians(true_north_bearing)
                
                # Approximate lat/lon offset (good enough for mock)
                lat_offset = (range_m * math.cos(bearing_rad)) / 111320  # meters to degrees
                lon_offset = (range_m * math.sin(bearing_rad)) / (111320 * math.cos(math.radians(self.ownship_lat)))
                
                drone_lat = self.ownship_lat + lat_offset
                drone_lon = self.ownship_lon + lon_offset
                
                # Pilot is typically 100-500m from drone
                pilot_range = random.uniform(100, 500)
                pilot_bearing = random.uniform(0, 360)
                pilot_bearing_rad = math.radians(pilot_bearing)
                
                pilot_lat = drone_lat + (pilot_range * math.cos(pilot_bearing_rad)) / 111320
                pilot_lon = drone_lon + (pilot_range * math.sin(pilot_bearing_rad)) / (111320 * math.cos(math.radians(drone_lat)))
                
                el_deg = random.uniform(10, 30)
                freq_hz = random.choice([2412000000, 2437000000, 5745000000])
                
                detections.append({
                    'id': det['id'],
                    'azimuth_deg': vehicle_rel_azimuth,
                    'az_deg': vehicle_rel_azimuth,  # UI compatibility
                    'elevation_deg': el_deg,
                    'el_deg': el_deg,  # UI compatibility
                    'range_m': range_m,
                    'speed_mps': random.uniform(10, 30),  # UI compatibility
                    'velocity_mps': random.uniform(10, 30),  # UI compatibility
                    'heading_deg': random.uniform(0, 360),  # UI compatibility
                    'type': 'UAV',
                    'confidence': 0.9 + random.uniform(-0.05, 0.05),
                    'source': 'RF',
                    'status': 'TRACKING',  # UI compatibility
                    # RF-specific (precision mode)
                    'pilot_latitude': pilot_lat,
                    'pilot_longitude': pilot_lon,
                    'pilot_lat': pilot_lat,  # UI compatibility
                    'pilot_lon': pilot_lon,  # UI compatibility
                    'aircraft_model': det['model'],
                    'serial_number': f"SN{random.randint(100000, 999999)}",
                    'rf_frequency_hz': freq_hz,
                    'frequency': int(freq_hz / 1000000),  # UI compatibility (MHz)
                    'rf_power_dbm': random.uniform(-80, -40),
                    'detection_mode': 'PRECISION',
                    'last_update_ns': time.time_ns()
                })
            else:
                # Sector mode: 45° bearing sector (less precise)
                sector_num = int(true_north_bearing / self.SECTOR_WIDTH_DEG) + 1
                sector_center = (sector_num - 1) * self.SECTOR_WIDTH_DEG + self.SECTOR_WIDTH_DEG / 2
                
                freq_hz = random.choice([2412000000, 2437000000])
                
                detections.append({
                    'id': det['id'],
                    'azimuth_deg': vehicle_rel_azimuth,
                    'az_deg': vehicle_rel_azimuth,  # UI compatibility
                    'elevation_deg': 15.0,  # Default elevation for display
                    'el_deg': 15.0,  # UI compatibility
                    'range_m': 1500.0,  # Approximate range for display
                    'speed_mps': random.uniform(10, 20),  # UI compatibility
                    'velocity_mps': random.uniform(10, 20),  # UI compatibility
                    'heading_deg': random.uniform(0, 360),  # UI compatibility
                    'type': 'UNKNOWN',  # Less precise detection
                    'confidence': 0.7 + random.uniform(-0.1, 0.1),
                    'source': 'RF',
                    'status': 'TRACKING',  # UI compatibility
                    # RF-specific (sector mode)
                    'aircraft_model': det['model'],
                    'rf_frequency_hz': freq_hz,
                    'frequency': int(freq_hz / 1000000),  # UI compatibility (MHz)
                    'rf_power_dbm': random.uniform(-90, -50),
                    'detection_mode': 'SECTOR',
                    'sector_id': sector_num,
                    'last_update_ns': time.time_ns()
                })
        
        return detections
    
    def update_ownship(self, lat: float, lon: float, heading: float):
        """Update ownship position for coordinate conversion"""
        self.ownship_lat = lat
        self.ownship_lon = lon
        self.ownship_heading = heading


class MockEngine(QObject):
    """
    Updated mock engine with real sensor characteristics
    """
    
    def __init__(self):
        super().__init__()
        self.radar = MockRadarSensor()
        self.rf = MockRFSensor()
        
        # Test scenario configuration
        self.test_config = {
            'enabled': False,
            'scenario': None,  # Start disabled - no simulated tracks
            'static_tracks': [],
            'track_velocity_mps': (10, 50),  # Min/max velocity for moving tracks
        }
        
        self.ownship = {
            'lat': -25.841105,
            'lon': 28.180340,
            'heading': 90.0,
            'altitude_m': 1400.0,
            'ground_speed_mps': 0.0,
            'gps_satellites': 12,
            'gps_hdop': 1.1
        }
        
        self.rws_state = {
            'radar_azimuth_deg': 0.0,
            'radar_elevation_deg': 0.0,
            'optics_azimuth_deg': 0.0,
            'optics_elevation_deg': 0.0,  # 20° offset in real system
            'is_armed': False,
            'optical_lock': False,
            'locked_track_id': None,
            'is_slewing': False,
            'slew_progress': 0.0
        }
        
        self.system_mode = {
            'auto_track': True,
            'rf_silent': False,
            'optical_lock': False,
            'fusion_enabled': True,
            'track_timeout_sec': 5.0
        }
        
        self.fused_tracks = {}
        
    def update(self):
        """Main update loop - fuses sensor data"""
        # Check if using test scenario
        if self.test_config['enabled'] and self.test_config['static_tracks']:
            # Use predefined test tracks
            self._update_test_tracks()
            return
        
        # If test scenarios disabled, wait for real sensor data (none connected = no tracks)
        if not self.test_config['enabled']:
            # No simulation - would read from real sensors here
            # Since no sensors connected, tracks remain empty
            self.fused_tracks = {}
            return
        
        # Normal operation: use radar/RF sensors (for development/testing)
        # Get sensor data (normal operation)
        radar_tracks = self.radar.generate_tracks()
        rf_detections = self.rf.generate_detections()
        
        # Simple fusion: combine radar and RF
        # In production: Kalman filters, association, state estimation
        all_tracks = []
        
        # Add radar tracks
        for track in radar_tracks:
            all_tracks.append(track)
        
        # Add RF detections
        for det in rf_detections:
            # Check if can be fused with radar track
            fused = False
            for track in all_tracks:
                if track['source'] == 'RADAR':
                    # Simple association: if azimuth within 10° and range within 200m
                    az_diff = abs(track['azimuth_deg'] - det['azimuth_deg'])
                    if az_diff > 180:
                        az_diff = 360 - az_diff
                    
                    if det['detection_mode'] == 'PRECISION':
                        range_diff = abs(track['range_m'] - det['range_m'])
                        if az_diff < 10 and range_diff < 200:
                            # Fuse RF data into radar track
                            track['source'] = 'FUSED'
                            track['pilot_latitude'] = det.get('pilot_latitude')
                            track['pilot_longitude'] = det.get('pilot_longitude')
                            track['aircraft_model'] = det.get('aircraft_model')
                            track['serial_number'] = det.get('serial_number')
                            track['rf_frequency_hz'] = det.get('rf_frequency_hz')
                            track['rf_power_dbm'] = det.get('rf_power_dbm')
                            track['confidence'] = min(0.95, (track['confidence'] + det['confidence']) / 2 + 0.1)
                            fused = True
                            break
            
            if not fused:
                # Add as RF-only track
                all_tracks.append(det)
        
        self.fused_tracks = {t['id']: t for t in all_tracks}
        
        # Update ownship (simulate drift)
        self.ownship['heading'] += random.uniform(-0.5, 0.5)
        self.ownship['heading'] %= 360
        
        # Update RF sensor with new ownship
        self.rf.update_ownship(
            self.ownship['lat'],
            self.ownship['lon'],
            self.ownship['heading']
        )
    
    def _update_test_tracks(self):
        """Update test scenario tracks with realistic drone flight paths"""
        for track in self.test_config['static_tracks']:
            # Initialize movement parameters if not present
            if 'velocity_mps' not in track:
                track['velocity_mps'] = random.uniform(*self.test_config['track_velocity_mps'])
            if 'direction' not in track:
                track['direction'] = random.choice([-1, 1])
            if 'azimuth_drift' not in track:
                track['azimuth_drift'] = random.uniform(-0.1, 0.1)
            if 'heading_deg' not in track:
                track['heading_deg'] = track.get('azimuth_deg', 0)
            
            velocity_mps = track['velocity_mps']
            track['speed_mps'] = velocity_mps
            
            # Calculate movement per update (0.1s at 10 Hz)
            movement_m = velocity_mps * 0.1
            
            # Realistic movement pattern based on type
            track_type = track.get('type', 'UAV')
            
            if track_type == 'UAV':
                # UAVs: Smooth linear movement with gentle curves
                # Consistent direction with very gradual changes
                direction = track['direction']
                track['range_m'] += movement_m * direction
                
                # Very small, smooth azimuth drift (realistic drone flight)
                azimuth_drift = track['azimuth_drift']
                
                # Gradual drift adjustment (momentum-based)
                if random.random() < 0.005:  # 0.5% chance - very rare course adjustment
                    # Small adjustment to drift
                    azimuth_drift += random.uniform(-0.05, 0.05)
                    azimuth_drift = max(-0.3, min(0.3, azimuth_drift))  # Clamp to ±0.3°
                    track['azimuth_drift'] = azimuth_drift
                
                # Apply smooth drift
                track['azimuth_deg'] += azimuth_drift
                
                # Velocity varies slightly (wind, battery, etc.)
                if random.random() < 0.01:  # 1% chance
                    track['velocity_mps'] += random.uniform(-0.5, 0.5)
                    track['velocity_mps'] = max(10, min(50, track['velocity_mps']))
                    
            elif track_type == 'BIRD':
                # Birds: More dynamic but still smooth, circular patterns
                # Update range with variation
                direction = track['direction']
                range_variation = random.uniform(0.8, 1.2)
                track['range_m'] += movement_m * direction * range_variation
                
                # Smooth circular motion (like birds circling)
                azimuth_drift = track.get('azimuth_drift', 0.5)
                
                # Gradual changes in circular pattern
                if random.random() < 0.02:  # 2% chance
                    azimuth_drift += random.uniform(-0.2, 0.2)
                    azimuth_drift = max(-1.5, min(1.5, azimuth_drift))
                    track['azimuth_drift'] = azimuth_drift
                
                track['azimuth_deg'] += azimuth_drift
                
                # Speed variations for birds
                if random.random() < 0.05:  # 5% chance
                    track['velocity_mps'] += random.uniform(-2, 2)
                    track['velocity_mps'] = max(8, min(30, track['velocity_mps']))
                
            elif track_type == 'UNKNOWN':
                # Unknown: Moderate movement, somewhat predictable
                direction = track['direction']
                range_variation = random.uniform(0.9, 1.1)
                track['range_m'] += movement_m * direction * range_variation
                
                # Moderate drift
                azimuth_drift = track.get('azimuth_drift', 0)
                
                if random.random() < 0.01:  # 1% chance
                    azimuth_drift += random.uniform(-0.1, 0.1)
                    azimuth_drift = max(-0.5, min(0.5, azimuth_drift))
                    track['azimuth_drift'] = azimuth_drift
                
                track['azimuth_deg'] += azimuth_drift
            
            # Keep range in bounds and reverse direction with some randomness
            # Add variance so tracks don't all bounce at exact same ranges
            if track['range_m'] < 100:
                track['range_m'] = 100
                track['direction'] = 1  # Start moving away (increase range)
                # Occasionally change course to avoid repetitive patterns
                if random.random() < 0.3:
                    track['azimuth_drift'] = random.uniform(-0.5, 0.5)
            elif track['range_m'] > 3000:
                track['range_m'] = 3000
                track['direction'] = -1  # Start approaching (decrease range)
                # Occasionally change course
                if random.random() < 0.3:
                    track['azimuth_drift'] = random.uniform(-0.5, 0.5)
            
            # Occasional direction reversals for realistic behavior (loitering, patrol patterns)
            if random.random() < 0.001:  # 0.1% chance per update (~once every 100 seconds per track)
                track['direction'] *= -1  # Reverse direction
                if track_type == 'UAV':
                    # UAVs might change course when reversing
                    track['azimuth_drift'] = random.uniform(-0.3, 0.3)
            
            # Normalize azimuth
            track['azimuth_deg'] %= 360
            track['az_deg'] = track['azimuth_deg']  # Keep both fields in sync
            
            # Very gradual elevation changes
            if 'elevation_deg' in track:
                el_change = track.get('elevation_drift', random.uniform(-0.05, 0.05))
                
                # Occasional elevation drift adjustment
                if random.random() < 0.01:
                    el_change += random.uniform(-0.02, 0.02)
                    el_change = max(-0.1, min(0.1, el_change))
                    track['elevation_drift'] = el_change
                
                track['elevation_deg'] += el_change
                track['elevation_deg'] = max(5, min(45, track['elevation_deg']))
                track['el_deg'] = track['elevation_deg']
            
            # Calculate velocity components from actual movement
            az_rad = math.radians(track['azimuth_deg'])
            direction = track.get('direction', 1)
            speed = track.get('velocity_mps', track.get('speed_mps', 20.0))
            range_rate_mps = speed * direction
            
            track['velocity_x_mps'] = range_rate_mps * math.sin(az_rad)
            track['velocity_y_mps'] = range_rate_mps * math.cos(az_rad)
            track['velocity_z_mps'] = 0.0
        
        self.fused_tracks = {t['id']: t for t in self.test_config['static_tracks']}
    
    def get_tracks_snapshot(self):
        """Get current fused tracks"""
        radar_only = sum(1 for t in self.fused_tracks.values() if t['source'] == 'RADAR')
        rf_only = sum(1 for t in self.fused_tracks.values() if t['source'] == 'RF')
        fused = sum(1 for t in self.fused_tracks.values() if t['source'] == 'FUSED')
        
        return {
            'header': {
                'timestamp_ns': time.time_ns(),
                'source': 'FUSION_ENGINE'
            },
            'tracks': list(self.fused_tracks.values()),
            'max_range_m': 3000.0,
            'fused_count': fused,
            'radar_only_count': radar_only,
            'rf_only_count': rf_only
        }
    
    def get_ownship(self):
        """Get ownship state"""
        return {
            'header': {
                'timestamp_ns': time.time_ns(),
                'source': 'GPS'
            },
            **self.ownship
        }
    
    def get_rws_state(self):
        """Get RWS state"""
        return {
            'header': {
                'timestamp_ns': time.time_ns(),
                'source': 'RWS_ENCODER'
            },
            **self.rws_state
        }
    
    def get_command_chain_status(self):
        """Get command chain status"""
        return {
            'header': {
                'timestamp_ns': time.time_ns(),
                'source': 'ENGINE'
            },
            'rf_detect_active': len([t for t in self.fused_tracks.values() if 'RF' in t['source']]) > 0,
            'radar_slew_active': False,
            'radar_track_active': len([t for t in self.fused_tracks.values() if t['source'] == 'RADAR']) > 0,
            'optics_slew_active': False,
            'optical_lock_active': self.rws_state['optical_lock'],
            'tracking_target_id': self.rws_state.get('locked_track_id'),
            'chain_status': 'RADAR_TRACK' if len(self.fused_tracks) > 0 else 'IDLE'
        }
    
    def request_engage(self, track_id, operator_id, reason, force=False):
        """
        Safety-critical engage validation
        Based on real ROE requirements
        """
        track = self.fused_tracks.get(track_id)
        
        if not track:
            return {
                'accepted': False,
                'message': f'Track {track_id} not found',
                'failed_checks': ['TRACK_NOT_FOUND']
            }
        
        failed_checks = []
        
        # Safety checks
        if track['type'] == 'BIRD':
            failed_checks.append('TARGET_TYPE_BIRD')
        
        if track['type'] == 'CLUTTER':
            failed_checks.append('TARGET_TYPE_CLUTTER')
        
        if track['confidence'] < 0.7:
            failed_checks.append(f'CONFIDENCE_LOW:{track["confidence"]:.2f}')
        
        if track['range_m'] > 2500:
            failed_checks.append(f'RANGE_EXCEEDED:{track["range_m"]:.0f}m')
        
        if track['range_m'] < 100:
            failed_checks.append(f'RANGE_TOO_CLOSE:{track["range_m"]:.0f}m')
        
        # Additional checks for RF detections
        if track['source'] == 'RF' and track.get('detection_mode') == 'SECTOR':
            if not force:
                failed_checks.append('RF_SECTOR_MODE_NO_PRECISION')
        
        # Operator authorization check (simplified)
        if operator_id not in ['operator', 'admin', 'test']:
            failed_checks.append('OPERATOR_NOT_AUTHORIZED')
        
        if failed_checks and not force:
            return {
                'accepted': False,
                'message': f'Engage denied: {len(failed_checks)} safety checks failed',
                'failed_checks': failed_checks,
                'track_confidence': track['confidence'],
                'track_range_m': track['range_m'],
                'track_type': track['type']
            }
        
        # All checks passed
        print(f"[ENGINE] ✓ ENGAGE APPROVED: Track {track_id} by {operator_id}")
        print(f"[ENGINE]   Type: {track['type']}, Range: {track['range_m']:.0f}m, Confidence: {track['confidence']:.2f}")
        print(f"[ENGINE]   Source: {track['source']}, Reason: {reason}")
        
        return {
            'accepted': True,
            'message': f'Engage authorized for track {track_id}',
            'failed_checks': [],
            'track_confidence': track['confidence'],
            'track_range_m': track['range_m'],
            'track_type': track['type']
        }
    
    def set_system_mode(self, **kwargs):
        """Update system mode"""
        for key, value in kwargs.items():
            if key in self.system_mode:
                self.system_mode[key] = value
        
        print(f"[ENGINE] System mode updated: {self.system_mode}")
        return {
            'accepted': True,
            'message': 'System mode updated'
        }
    
    @Slot(str, result=dict)
    def load_test_scenario(self, scenario_name: str):
        """
        Load predefined test scenarios for UI testing
        
        Available scenarios:
        - 'scenario_2': Single Track Testing (1 static track at medium range)
        - 'scenario_3': Priority Algorithm Testing (5 tracks at various ranges)
        - 'scenario_4': Sensor Fusion Testing (2 FUSED tracks with RF intelligence)
        - 'scenario_5': Stress Testing (20+ tracks, all moving)
        - 'disable': Return to normal sensor operation
        """
        print(f"[ENGINE] Loading test scenario: {scenario_name}")
        
        if scenario_name == 'disable':
            self.test_config['enabled'] = False
            self.test_config['scenario'] = None
            self.test_config['static_tracks'] = []
            # Clear all tracks - waiting for real sensor data
            self.fused_tracks = {}
            print(f"[ENGINE] Test scenarios disabled - waiting for real sensor inputs (none connected)")
            return {'accepted': True, 'message': 'Scenarios disabled - no tracks'}
        
        self.test_config['enabled'] = True
        self.test_config['scenario'] = scenario_name
        # Clear all previous tracks when loading new scenario
        self.radar.tracks = {}
        self.rf.detections = {}
        self.fused_tracks = {}
        self.test_config['static_tracks'] = []
        
        if scenario_name == 'scenario_2':
            # Scenario 2: Single Track Testing
            # 1 static track at medium range for testing selection and engagement
            self.test_config['static_tracks'] = [
                {
                    'id': 5001,
                    'type': 'UAV',
                    'source': 'RADAR',
                    'azimuth_deg': 45.0,
                    'az_deg': 45.0,  # For UI compatibility
                    'elevation_deg': 15.0,
                    'el_deg': 15.0,  # For UI compatibility
                    'range_m': 1000.0,
                    'velocity_x_mps': 12.0,
                    'velocity_y_mps': 8.0,
                    'velocity_z_mps': 0.0,
                    'speed_mps': 25.0,
                    'velocity_mps': 25.0,
                    'heading_deg': 90.0,
                    'confidence': 0.85,
                    'status': 'TRACKING',
                    'rcs_m2': 0.05,
                    'probability_uav': 0.90,
                    'last_update_ns': time.time_ns(),
                    'direction': -1,  # Approaching
                }
            ]
            print(f"[ENGINE] Scenario 2: Single track at 1000m, moving at 25 m/s")
        
        elif scenario_name == 'scenario_3':
            # Scenario 3: Priority Algorithm Testing
            # Mix of UAVs, birds, and unknown tracks at various ranges
            # Velocities: 10-50 m/s
            self.test_config['static_tracks'] = [
                {
                    'id': 5010,
                    'type': 'UAV',
                    'source': 'RADAR',
                    'azimuth_deg': 30.0,
                    'az_deg': 30.0,
                    'elevation_deg': 18.0,
                    'el_deg': 18.0,
                    'range_m': 200.0,  # CRITICAL - closest
                    'velocity_x_mps': 15.0,
                    'velocity_y_mps': 10.0,
                    'speed_mps': 35.0,
                    'velocity_mps': 35.0,
                    'heading_deg': 90.0,
                    'confidence': 0.92,
                    'status': 'TRACKING',
                    'rcs_m2': 0.08,
                    'last_update_ns': time.time_ns(),
                    'direction': -1,
                },
                {
                    'id': 5011,
                    'type': 'UAV',
                    'source': 'FUSED',
                    'azimuth_deg': 75.0,
                    'az_deg': 75.0,
                    'elevation_deg': 12.0,
                    'el_deg': 12.0,
                    'range_m': 500.0,  # HIGH priority
                    'velocity_x_mps': 8.0,
                    'velocity_y_mps': 12.0,
                    'speed_mps': 20.0,
                    'velocity_mps': 20.0,
                    'heading_deg': 90.0,
                    'confidence': 0.88,
                    'status': 'TRACKING',
                    'aircraft_model': 'DJI Mavic 3',
                    'pilot_latitude': -25.840,
                    'pilot_longitude': 28.185,
                    'pilot_lon': 28.185,
                    'pilot_lat': -25.840,
                    'rf_frequency_hz': 2437000000,
                    'frequency': 2437,
                    'last_update_ns': time.time_ns(),
                    'direction': -1,
                },
                {
                    'id': 5012,
                    'type': 'BIRD',
                    'source': 'RADAR',
                    'azimuth_deg': 120.0,
                    'az_deg': 120.0,
                    'elevation_deg': 20.0,
                    'el_deg': 20.0,
                    'range_m': 1000.0,  # BIRD - lower priority
                    'velocity_x_mps': 12.0,
                    'velocity_y_mps': 8.0,
                    'speed_mps': 15.0,
                    'velocity_mps': 15.0,
                    'heading_deg': 135.0,
                    'confidence': 0.65,
                    'status': 'TRACKING',
                    'rcs_m2': 0.02,
                    'last_update_ns': time.time_ns(),
                    'direction': 1,
                },
                {
                    'id': 5013,
                    'type': 'UAV',
                    'source': 'RF',
                    'azimuth_deg': 180.0,
                    'az_deg': 180.0,
                    'elevation_deg': 25.0,
                    'el_deg': 25.0,
                    'range_m': 1500.0,  # MEDIUM-LOW priority
                    'velocity_x_mps': 10.0,
                    'velocity_y_mps': 10.0,
                    'speed_mps': 15.0,
                    'velocity_mps': 15.0,
                    'heading_deg': 90.0,
                    'confidence': 0.82,
                    'status': 'TRACKING',
                    'aircraft_model': 'DJI Phantom 4 Pro',
                    'pilot_latitude': -25.835,
                    'pilot_longitude': 28.190,
                    'pilot_lat': -25.835,
                    'pilot_lon': 28.190,
                    'rf_frequency_hz': 5745000000,
                    'frequency': 5745,
                    'detection_mode': 'PRECISION',
                    'last_update_ns': time.time_ns(),
                    'direction': -1,
                },
                {
                    'id': 5014,
                    'type': 'UNKNOWN',
                    'source': 'RADAR',
                    'azimuth_deg': 270.0,
                    'az_deg': 270.0,
                    'elevation_deg': 8.0,
                    'el_deg': 8.0,
                    'range_m': 2500.0,  # UNKNOWN - low confidence, far
                    'velocity_x_mps': 5.0,
                    'velocity_y_mps': 8.0,
                    'speed_mps': 10.0,
                    'velocity_mps': 10.0,
                    'heading_deg': 90.0,
                    'confidence': 0.55,
                    'status': 'TRACKING',
                    'rcs_m2': 0.03,
                    'last_update_ns': time.time_ns(),
                    'direction': 1,
                }
            ]
            print(f"[ENGINE] Scenario 3: 5 tracks - 3 UAVs, 1 BIRD, 1 UNKNOWN")
            print(f"[ENGINE]   Ranges: 200m-2500m, Velocities: 10-45 m/s")
            print(f"[ENGINE]   Colors: Red=UAV, Green=BIRD, Yellow=UNKNOWN")
        
        elif scenario_name == 'scenario_4':
            # Scenario 4: Sensor Fusion Testing
            # 2 FUSED tracks with complete RF intelligence
            self.test_config['static_tracks'] = [
                {
                    'id': 5020,
                    'type': 'UAV',
                    'source': 'FUSED',
                    'azimuth_deg': 60.0,
                    'az_deg': 60.0,
                    'elevation_deg': 15.0,
                    'el_deg': 15.0,
                    'range_m': 800.0,
                    'velocity_x_mps': 12.0,
                    'velocity_y_mps': 15.0,
                    'velocity_z_mps': 1.0,
                    'speed_mps': 30.0,
                    'velocity_mps': 30.0,
                    'heading_deg': 90.0,
                    'confidence': 0.94,
                    'status': 'TRACKING',
                    'rcs_m2': 0.07,
                    'probability_uav': 0.95,
                    # RF Intelligence
                    'pilot_latitude': -25.842105,
                    'pilot_longitude': 28.182340,
                    'pilot_lat': -25.842105,
                    'pilot_lon': 28.182340,
                    'aircraft_model': 'DJI Mavic 3',
                    'serial_number': 'SN123456',
                    'rf_frequency_hz': 2437000000,
                    'frequency': 2437,
                    'rf_power_dbm': -55.0,
                    'detection_mode': 'PRECISION',
                    'last_update_ns': time.time_ns(),
                    'direction': -1,
                },
                {
                    'id': 5021,
                    'type': 'UAV',
                    'source': 'FUSED',
                    'azimuth_deg': 150.0,
                    'az_deg': 150.0,
                    'elevation_deg': 22.0,
                    'el_deg': 22.0,
                    'range_m': 1200.0,
                    'velocity_x_mps': 18.0,
                    'velocity_y_mps': 10.0,
                    'velocity_z_mps': -0.5,
                    'speed_mps': 40.0,
                    'velocity_mps': 40.0,
                    'heading_deg': 90.0,
                    'confidence': 0.91,
                    'status': 'TRACKING',
                    'rcs_m2': 0.06,
                    'probability_uav': 0.92,
                    # RF Intelligence
                    'pilot_latitude': -25.838105,
                    'pilot_longitude': 28.185340,
                    'pilot_lat': -25.838105,
                    'pilot_lon': 28.185340,
                    'aircraft_model': 'Autel EVO II',
                    'serial_number': 'SN789012',
                    'rf_frequency_hz': 5745000000,
                    'frequency': 5745,
                    'rf_power_dbm': -62.0,
                    'detection_mode': 'PRECISION',
                    'last_update_ns': time.time_ns(),
                    'direction': 1,
                }
            ]
            print(f"[ENGINE] Scenario 4: 2 FUSED tracks with RF intelligence")
            print(f"[ENGINE]   Includes pilot location, aircraft model, serial numbers")
        
        elif scenario_name == 'scenario_5':
            # Scenario 5: Stress Testing
            # 20+ tracks, all moving at various velocities
            tracks = []
            for i in range(25):
                track_id = 5100 + i
                az = random.uniform(0, 360)
                el = random.uniform(5, 30)
                vel_mps = random.uniform(10, 50)
                
                # Weighted distribution: 50% UAV, 30% BIRD, 20% UNKNOWN
                type_choice = random.random()
                if type_choice < 0.5:
                    track_type = 'UAV'
                elif type_choice < 0.8:
                    track_type = 'BIRD'
                else:
                    track_type = 'UNKNOWN'
                
                tracks.append({
                    'id': track_id,
                    'type': track_type,
                    'source': random.choice(['RADAR', 'RF', 'FUSED', 'RADAR', 'RADAR']),
                    'azimuth_deg': az,
                    'az_deg': az,
                    'elevation_deg': el,
                    'el_deg': el,
                    'range_m': random.uniform(300, 2800),
                    'velocity_x_mps': random.uniform(-20, 20),
                    'velocity_y_mps': random.uniform(-20, 20),
                    'velocity_z_mps': random.uniform(-2, 2),
                    'speed_mps': vel_mps,
                    'velocity_mps': vel_mps,
                    'heading_deg': random.uniform(0, 360),
                    'confidence': random.uniform(0.65, 0.95),
                    'status': 'TRACKING',
                    'rcs_m2': random.uniform(0.02, 0.1),
                    'last_update_ns': time.time_ns(),
                    'direction': random.choice([-1, 1]),
                })
                
                # Add RF intelligence to FUSED and RF tracks
                if tracks[-1]['source'] in ['FUSED', 'RF']:
                    pilot_lat = -25.841105 + random.uniform(-0.01, 0.01)
                    pilot_lon = 28.180340 + random.uniform(-0.01, 0.01)
                    freq = random.choice([2437, 5745])
                    tracks[-1]['aircraft_model'] = random.choice(['DJI Mavic 3', 'DJI Phantom 4 Pro', 'Autel EVO II', 'DJI Mini 3'])
                    tracks[-1]['pilot_latitude'] = pilot_lat
                    tracks[-1]['pilot_longitude'] = pilot_lon
                    tracks[-1]['pilot_lat'] = pilot_lat
                    tracks[-1]['pilot_lon'] = pilot_lon
                    tracks[-1]['rf_frequency_hz'] = freq * 1000000
                    tracks[-1]['frequency'] = freq
            
            self.test_config['static_tracks'] = tracks
            print(f"[ENGINE] Scenario 5: 25 tracks for stress testing")
            print(f"[ENGINE]   Velocities: 10-50 m/s, mix of RADAR/RF/FUSED")
        
        else:
            print(f"[ENGINE] Unknown scenario: {scenario_name}")
            return {'accepted': False, 'message': f'Unknown scenario: {scenario_name}'}
        
        return {
            'accepted': True,
            'message': f'Scenario {scenario_name} loaded',
            'track_count': len(self.test_config['static_tracks'])
        }


def run_mock_engine(port=50051):
    """Run the updated mock engine"""
    engine = MockEngine()
    
    print("=" * 70)
    print("  TriAD Mock Engine - Updated with Real Sensor Specs")
    print("=" * 70)
    print("  Radar: Echodyne Echoguard (BNET protocol)")
    print("  RF: BlueHalo SkyView DIVR MkII (TLS/JSON)")
    print("  Fusion: Simple association + Kalman (planned)")
    print(f"  Listening on: localhost:{port}")
    print("=" * 70)
    print()
    
    try:
        iteration = 0
        while True:
            engine.update()
            
            if iteration % 10 == 0:
                snapshot = engine.get_tracks_snapshot()
                print(f"[{iteration//10}s] Tracks: {len(snapshot['tracks'])} "
                      f"(Fused:{snapshot['fused_count']}, "
                      f"Radar:{snapshot['radar_only_count']}, "
                      f"RF:{snapshot['rf_only_count']})")
                
                # Show example track details
                if snapshot['tracks']:
                    t = snapshot['tracks'][0]
                    print(f"       Example: ID{t['id']} {t['type']} @ {t['range_m']:.0f}m, {t['azimuth_deg']:.1f}° "
                          f"[{t['source']}] conf={t['confidence']:.2f}")
                    if t.get('aircraft_model'):
                        print(f"                Model: {t['aircraft_model']}")
            
            time.sleep(0.1)  # 10 Hz
            iteration += 1
            
    except KeyboardInterrupt:
        print("\n[ENGINE] Shutting down...")


if __name__ == "__main__":
    run_mock_engine()
