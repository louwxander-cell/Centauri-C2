#!/usr/bin/env python3
"""
Mock TriAD Engine - Simulates real-time sensor fusion
This is a Python prototype. Production version should be C++.
"""

import time
import random
import math

# For now, we'll use a simple dict-based approach until we compile protos
# In Phase 2, we'll add: import grpc, protobuf stubs, etc.

class MockEngine:
    """Simulates real-time tracking engine"""
    
    def __init__(self):
        self.tracks = []
        self.ownship = {
            'lat': -25.841105,
            'lon': 28.180340,
            'heading': 90.0
        }
        self.rws_state = {
            'azimuth': 0.0,
            'elevation': 0.0,
            'armed': False
        }
        self.system_mode = {
            'auto_track': True,
            'rf_silent': False,
            'optical_lock': False
        }
        self._init_tracks()
    
    def _init_tracks(self):
        """Initialize sample tracks"""
        statuses = ["CRITICAL", "HIGH", "MED", "FRIENDLY"]
        types = ["UAV", "UAV", "BIRD", "UAV"]
        sources = ["RADAR", "RF", "RADAR", "OPTICAL"]
        
        for i in range(4):
            self.tracks.append({
                'id': 101 + i,
                'type': types[i],
                'source': sources[i],
                'range_m': 800.0 + i * 400,
                'az_deg': 45.0 + i * 90,
                'el_deg': 10.0 + i * 5,
                'speed_mps': 8.0 + i * 3,
                'heading_deg': 90.0 + i * 45,
                'confidence': 0.65 + i * 0.08,
                'status': statuses[i]
            })
    
    def update_tracks(self):
        """Simulate track updates (sensor fusion)"""
        for track in self.tracks:
            # Simulate movement
            track['az_deg'] += random.uniform(-0.5, 0.5)
            if track['az_deg'] < 0:
                track['az_deg'] += 360
            if track['az_deg'] >= 360:
                track['az_deg'] -= 360
            
            track['range_m'] = max(500, track['range_m'] + random.uniform(-10, 10))
            track['confidence'] = min(0.95, max(0.5, track['confidence'] + random.uniform(-0.02, 0.02)))
    
    def get_tracks_snapshot(self):
        """Get current tracks snapshot"""
        return {
            'header': {
                'timestamp_ns': time.time_ns(),
                'source': 'MOCK_ENGINE'
            },
            'tracks': self.tracks.copy(),
            'max_range_m': 3000.0
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
        # Simulate RWS following selected track
        return {
            'header': {
                'timestamp_ns': time.time_ns(),
                'source': 'RWS_ENCODER'
            },
            **self.rws_state
        }
    
    def request_engage(self, track_id, operator_id, reason):
        """
        Safety-critical engage request handler
        In production C++ engine, this would check:
        - ROE rules
        - Track quality
        - Hardware interlocks
        - Operator permissions
        """
        track = next((t for t in self.tracks if t['id'] == track_id), None)
        
        if not track:
            return {
                'accepted': False,
                'message': f'Track {track_id} not found'
            }
        
        # Simulate safety checks
        if track['status'] == 'FRIENDLY':
            return {
                'accepted': False,
                'message': 'Cannot engage FRIENDLY track'
            }
        
        if track['confidence'] < 0.7:
            return {
                'accepted': False,
                'message': f'Track confidence too low: {track["confidence"]:.2f}'
            }
        
        if track['range_m'] > 2500:
            return {
                'accepted': False,
                'message': f'Track out of engagement range: {track["range_m"]:.0f}m'
            }
        
        # All checks passed
        print(f"[ENGINE] ENGAGE APPROVED: Track {track_id} by {operator_id} - {reason}")
        return {
            'accepted': True,
            'message': f'Engage authorized for track {track_id}'
        }
    
    def set_system_mode(self, auto_track=None, rf_silent=None, optical_lock=None):
        """Update system mode"""
        if auto_track is not None:
            self.system_mode['auto_track'] = auto_track
        if rf_silent is not None:
            self.system_mode['rf_silent'] = rf_silent
        if optical_lock is not None:
            self.system_mode['optical_lock'] = optical_lock
        
        print(f"[ENGINE] System mode updated: {self.system_mode}")
        return {
            'accepted': True,
            'message': 'System mode updated'
        }


def run_mock_engine(port=50051):
    """Run the mock engine as a simple streaming server"""
    engine = MockEngine()
    
    print("=" * 70)
    print("  TriAD Mock Engine - Starting")
    print("=" * 70)
    print(f"  Listening on: localhost:{port}")
    print(f"  Tracking: {len(engine.tracks)} simulated targets")
    print(f"  Update rate: 10 Hz")
    print("=" * 70)
    print()
    
    # For now, just run a simple update loop
    # In the full implementation, this would be a gRPC server
    try:
        iteration = 0
        while True:
            engine.update_tracks()
            
            if iteration % 10 == 0:  # Print every second
                snapshot = engine.get_tracks_snapshot()
                print(f"[{iteration//10}s] Tracks: {len(snapshot['tracks'])} | "
                      f"Example: ID{snapshot['tracks'][0]['id']} @ "
                      f"{snapshot['tracks'][0]['range_m']:.0f}m, "
                      f"{snapshot['tracks'][0]['az_deg']:.1f}°")
            
            time.sleep(0.1)  # 10 Hz update
            iteration += 1
            
    except KeyboardInterrupt:
        print("\n[ENGINE] Shutting down...")


if __name__ == "__main__":
    run_mock_engine()
