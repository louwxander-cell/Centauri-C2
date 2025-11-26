"""Mock Echodyne Radar driver - generates simulated track data with realistic flight patterns"""

import time
import math
import random
from .base import BaseDriver
from ..core.bus import SignalBus
from ..core.datamodels import Track, SensorSource, TargetType


class RadarDriver(BaseDriver):
    """
    Mock Echodyne Radar driver.
    Simulates multiple targets with realistic flight patterns.
    - Velocities: 5-30 m/s
    - Update rate: 5 Hz (200ms intervals)
    - Realistic maneuvers: straight lines, turns, orbits
    In production, this would connect to TCP port 23000 and parse binary/JSON data.
    """
    
    def __init__(self, parent=None):
        super().__init__("RadarDriver", parent)
        self.signal_bus = SignalBus.instance()
        
        # Simulation parameters
        self.update_interval_ms = 200  # 5 Hz update rate (realistic radar)
        self.num_targets = 5  # More targets for better demonstration
        self.targets = self._initialize_targets()
        
    def _initialize_targets(self):
        """Initialize simulated targets with realistic flight patterns"""
        targets = []
        
        # Target 1: Fast approaching drone (high threat) - realistic straight approach
        targets.append({
            'id': 1,
            'x': 1800.0,  # Start 1.8km away
            'y': 1800.0,
            'vx': -12.0,  # Approaching at 17 m/s (realistic drone speed)
            'vy': -12.0,
            'type': TargetType.UAV,
            'confidence': 0.92,
            'pattern': 'straight',
            'turn_rate': 0.0,
            'max_speed': 20.0
        })
        
        # Target 2: Medium speed orbiting drone - smooth circular pattern
        targets.append({
            'id': 2,
            'x': -1000.0,
            'y': 1000.0,
            'vx': 10.0,
            'vy': 0.0,
            'type': TargetType.UAV,
            'confidence': 0.85,
            'pattern': 'orbit',
            'turn_rate': 0.015,  # Slower, smoother turns (was 0.05)
            'max_speed': 15.0
        })
        
        # Target 3: Slow bird - gentle wandering
        targets.append({
            'id': 3,
            'x': 600.0,
            'y': -600.0,
            'vx': -6.0,
            'vy': 7.0,
            'type': TargetType.BIRD,
            'confidence': 0.75,
            'pattern': 'wander',
            'turn_rate': 0.01,  # Very gentle turns (was 0.02)
            'max_speed': 10.0
        })
        
        # Target 4: Fast drone with smooth evasive maneuvers
        targets.append({
            'id': 4,
            'x': -1500.0,
            'y': -1500.0,
            'vx': 18.0,
            'vy': 8.0,
            'type': TargetType.UAV,
            'confidence': 0.88,
            'pattern': 'evasive',
            'turn_rate': 0.02,  # Smoother evasive turns (was 0.08)
            'max_speed': 25.0
        })
        
        # Target 5: Unknown target, moderate speed - straight line
        targets.append({
            'id': 5,
            'x': 2200.0,
            'y': -600.0,
            'vx': -11.0,
            'vy': 13.0,
            'type': TargetType.UNKNOWN,
            'confidence': 0.65,
            'pattern': 'straight',
            'turn_rate': 0.0,
            'max_speed': 18.0
        })
        
        return targets
    
    def run(self):
        """Main thread loop - generates and emits simulated tracks"""
        self.set_online(True)
        
        last_time = time.time()
        while self._running:
            try:
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time
                
                # Update and generate tracks for each target
                for target in self.targets:
                    self._update_target_position(target, dt)
                    track = self._generate_track(target)
                    self.signal_bus.emit_track(track)
                
                # Sleep for update interval
                time.sleep(self.update_interval_ms / 1000.0)
                
            except Exception as e:
                self.emit_error(f"Error in radar loop: {str(e)}")
                time.sleep(1.0)
        
        self.set_online(False)
    
    def _update_target_position(self, target: dict, dt: float):
        """Update target position based on velocity and flight pattern"""
        # Update position
        target['x'] += target['vx'] * dt
        target['y'] += target['vy'] * dt
        
        # Apply flight pattern
        pattern = target['pattern']
        
        if pattern == 'orbit':
            # Circular orbit - apply centripetal acceleration
            speed = math.sqrt(target['vx']**2 + target['vy']**2)
            if speed > 0:
                # Rotate velocity vector
                angle_change = target['turn_rate'] * dt
                cos_a = math.cos(angle_change)
                sin_a = math.sin(angle_change)
                
                new_vx = target['vx'] * cos_a - target['vy'] * sin_a
                new_vy = target['vx'] * sin_a + target['vy'] * cos_a
                
                target['vx'] = new_vx
                target['vy'] = new_vy
        
        elif pattern == 'evasive':
            # Smooth evasive maneuvers (less sporadic)
            if random.random() < 0.02:  # 2% chance per update (was 5%)
                # Smaller random turn for smoother motion
                angle_change = random.uniform(-0.15, 0.15)  # ±8.6 degrees (was ±17)
                cos_a = math.cos(angle_change)
                sin_a = math.sin(angle_change)
                
                new_vx = target['vx'] * cos_a - target['vy'] * sin_a
                new_vy = target['vx'] * sin_a + target['vy'] * cos_a
                
                target['vx'] = new_vx
                target['vy'] = new_vy
        
        elif pattern == 'wander':
            # Gentle wandering motion
            if random.random() < 0.1:  # 10% chance per update
                # Small random turn
                angle_change = random.uniform(-0.1, 0.1)  # ±6 degrees
                cos_a = math.cos(angle_change)
                sin_a = math.sin(angle_change)
                
                new_vx = target['vx'] * cos_a - target['vy'] * sin_a
                new_vy = target['vx'] * sin_a + target['vy'] * cos_a
                
                target['vx'] = new_vx
                target['vy'] = new_vy
        
        # Straight pattern: no velocity changes
        
        # Keep targets in reasonable range (bounce off boundaries)
        max_range = 3000.0
        current_range = math.sqrt(target['x']**2 + target['y']**2)
        
        if current_range > max_range:
            # Reflect velocity toward center
            target['vx'] = -target['vx'] * 0.8
            target['vy'] = -target['vy'] * 0.8
    
    def _generate_track(self, target: dict) -> Track:
        """Generate a single track for a target"""
        # Calculate polar coordinates from Cartesian
        x = target['x']
        y = target['y']
        
        range_m = math.sqrt(x**2 + y**2)
        azimuth = math.degrees(math.atan2(x, y)) % 360
        
        # Elevation (simulate some variation)
        elevation = 5.0 + random.uniform(-2.0, 2.0)
        
        # Calculate velocity and heading
        vx = target['vx']
        vy = target['vy']
        velocity_mps = math.sqrt(vx**2 + vy**2)
        heading = math.degrees(math.atan2(vx, vy)) % 360
        
        # Add some noise to confidence
        confidence = target['confidence'] + random.uniform(-0.03, 0.03)
        confidence = max(0.0, min(1.0, confidence))
        
        # UAV probability (for drones)
        uav_prob = None
        if target['type'] == TargetType.UAV:
            uav_prob = 0.75 + random.uniform(-0.1, 0.15)
            uav_prob = max(0.0, min(1.0, uav_prob))
        elif target['type'] == TargetType.BIRD:
            uav_prob = 0.15 + random.uniform(-0.1, 0.1)
            uav_prob = max(0.0, min(1.0, uav_prob))
        
        return Track(
            id=target['id'],
            azimuth=azimuth,
            elevation=elevation,
            range_m=range_m,
            type=target['type'],
            confidence=confidence,
            source=SensorSource.RADAR,
            velocity_mps=velocity_mps,
            heading=heading,
            probability_uav=uav_prob,
            rcs=-20.0 + random.uniform(-5.0, 5.0),  # Simulated RCS
            timestamp=time.time()
        )
