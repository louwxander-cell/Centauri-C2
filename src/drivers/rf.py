"""Mock BlueHalo RF sensor driver with realistic smooth movement"""

import time
import random
import math
from .base import BaseDriver
from ..core.bus import SignalBus
from ..core.datamodels import Track, SensorSource, TargetType


class RFDriver(BaseDriver):
    """
    Mock BlueHalo RF sensor driver.
    Simulates RF detections of drone control signals with smooth movement.
    In production, this would connect via REST/Socket API.
    """
    
    def __init__(self, parent=None):
        super().__init__("RFDriver", parent)
        self.signal_bus = SignalBus.instance()
        
        # Simulation parameters
        self.update_interval_ms = 200  # 5 Hz update rate (same as radar)
        
        # Initialize RF targets with smooth movement
        self.rf_targets = self._initialize_rf_targets()
        
    def _initialize_rf_targets(self):
        """Initialize RF targets with realistic flight patterns"""
        targets = []
        
        # RF Target 100: Slow approaching drone
        targets.append({
            'id': 100,
            'x': 1200.0,
            'y': -800.0,
            'vx': -8.0,
            'vy': 10.0,
            'pattern': 'straight',
            'max_speed': 15.0
        })
        
        # RF Target 101: Orbiting drone
        targets.append({
            'id': 101,
            'x': -600.0,
            'y': -1000.0,
            'vx': 12.0,
            'vy': 5.0,
            'pattern': 'orbit',
            'turn_rate': 0.02,
            'max_speed': 18.0
        })
        
        return targets
        
    def run(self):
        """Main thread loop - generates RF detections"""
        self.set_online(True)
        
        last_time = time.time()
        while self._running:
            try:
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time
                
                # Update and emit RF detections
                for target in self.rf_targets:
                    self._update_target_position(target, dt)
                    track = self._generate_rf_detection(target)
                    self.signal_bus.emit_track(track)
                
                time.sleep(self.update_interval_ms / 1000.0)
                
            except Exception as e:
                self.emit_error(f"Error in RF loop: {str(e)}")
                time.sleep(1.0)
        
        self.set_online(False)
    
    def _update_target_position(self, target: dict, dt: float):
        """Update target position with smooth movement"""
        # Update position
        target['x'] += target['vx'] * dt
        target['y'] += target['vy'] * dt
        
        # Apply flight pattern
        pattern = target['pattern']
        
        if pattern == 'orbit':
            # Smooth circular motion
            speed = math.sqrt(target['vx']**2 + target['vy']**2)
            if speed > 0:
                angle_change = target['turn_rate'] * dt
                cos_a = math.cos(angle_change)
                sin_a = math.sin(angle_change)
                
                new_vx = target['vx'] * cos_a - target['vy'] * sin_a
                new_vy = target['vx'] * sin_a + target['vy'] * cos_a
                
                target['vx'] = new_vx
                target['vy'] = new_vy
        
        # Keep targets in range
        max_range = 3000.0
        current_range = math.sqrt(target['x']**2 + target['y']**2)
        
        if current_range > max_range:
            target['vx'] = -target['vx'] * 0.8
            target['vy'] = -target['vy'] * 0.8
    
    def _generate_rf_detection(self, target: dict) -> Track:
        """
        Generate RF detection with realistic characteristics.
        RF sensors have good bearing accuracy but poor range accuracy.
        """
        # Calculate polar coordinates
        x = target['x']
        y = target['y']
        
        true_range = math.sqrt(x**2 + y**2)
        true_azimuth = math.degrees(math.atan2(x, y)) % 360
        
        # RF has good azimuth accuracy (±0.5 degree for very smooth movement)
        azimuth = (true_azimuth + random.uniform(-0.5, 0.5)) % 360
        
        # RF has stable elevation
        elevation = 5.0 + random.uniform(-0.3, 0.3)
        
        # RF has good range accuracy (±20m error for very smooth movement)
        range_m = true_range + random.uniform(-20, 20)
        range_m = max(range_m, 100)  # Minimum 100m
        
        # Calculate velocity
        vx = target['vx']
        vy = target['vy']
        velocity_mps = math.sqrt(vx**2 + vy**2)
        heading = math.degrees(math.atan2(vx, vy)) % 360
        
        # RF is very confident about drone classification (detects control signals)
        confidence = 0.90 + random.uniform(-0.03, 0.03)
        
        return Track(
            id=target['id'],
            azimuth=azimuth,
            elevation=elevation,
            range_m=range_m,
            type="UAV",  # RF specifically detects drones
            confidence=confidence,
            source=SensorSource.RF,
            velocity_mps=velocity_mps,
            heading=heading,
            timestamp=time.time()
        )
