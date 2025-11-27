#!/usr/bin/env python3
"""
Gunner Interface - Track Streaming Service
Broadcasts track data to gunner stations at 10 Hz via UDP
Receives gunner status feedback
"""

import socket
import struct
import json
import time
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class EffectorRecommendation:
    """Effector recommendation based on target range"""
    effector: str  # "CRx-30", "CRx-40", "OUT_OF_RANGE", "TOO_CLOSE"
    reason: str    # e.g., "RANGE_680M_LONG_RANGE"


@dataclass
class TrackUpdate:
    """Single track update for gunner"""
    # Identity
    track_id: int
    
    # Position (vehicle-relative: 0° = forward)
    azimuth_deg: float
    elevation_deg: float
    range_m: float
    
    # Velocity
    velocity_x_mps: float
    velocity_y_mps: float
    velocity_z_mps: float
    speed_mps: float
    heading_deg: float
    
    # Classification
    type: str  # UAV, BIRD, UNKNOWN
    confidence: float
    source: str  # RADAR, RF, FUSED
    
    # Track quality
    track_age_sec: float
    num_updates: int
    
    # Priority & recommendation
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    recommended_effector: str
    recommendation_reason: str
    
    # RF intelligence (optional)
    aircraft_model: Optional[str] = None
    pilot_latitude: Optional[float] = None
    pilot_longitude: Optional[float] = None
    
    # Timestamp
    timestamp_ns: int = 0


@dataclass
class TracksSnapshot:
    """Complete track picture sent at 10 Hz"""
    tracks: List[TrackUpdate]
    
    # System status
    radar_online: bool
    rf_online: bool
    total_tracks: int
    
    # Ownship (for coordinate context)
    ownship_lat: float
    ownship_lon: float
    ownship_heading: float
    
    # Timestamp
    timestamp_ns: int


@dataclass
class GunnerStatus:
    """Status feedback from gunner station"""
    station_id: str  # "GUNNER_1", "GUNNER_2", etc.
    
    # Current engagement
    cued_track_id: int  # -1 if none
    visual_lock: bool
    ready_to_fire: bool
    
    # RWS position
    rws_azimuth_deg: float
    rws_elevation_deg: float
    
    # Weapon status
    selected_weapon: str  # "CRx-30", "CRx-40", or ""
    rounds_remaining: int
    weapon_armed: bool
    
    # Operator
    operator_id: str
    
    # Timestamp
    timestamp_ns: int
    last_seen: float = 0.0  # Set by receiver


class EffectorRecommendationEngine:
    """
    Calculates effector recommendation based on target range
    
    CRx-30 (30mm cannon): 250m - 1000m (optimal 400-1000m)
    CRx-40 (40mm grenade): 50m - 250m (optimal 100-250m)
    """
    
    @staticmethod
    def get_recommendation(range_m: float) -> EffectorRecommendation:
        """Calculate effector recommendation"""
        
        # Out of effective range
        if range_m > 1000:
            return EffectorRecommendation(
                effector="OUT_OF_RANGE",
                reason=f"RANGE_{int(range_m)}M_TOO_FAR"
            )
        
        # Danger close
        if range_m < 50:
            return EffectorRecommendation(
                effector="TOO_CLOSE",
                reason=f"RANGE_{int(range_m)}M_DANGER_CLOSE"
            )
        
        # CRx-40 optimal range (100-250m)
        if 100 <= range_m <= 250:
            return EffectorRecommendation(
                effector="CRx-40",
                reason=f"RANGE_{int(range_m)}M_OPTIMAL_40MM"
            )
        
        # CRx-40 acceptable range (50-100m)
        if 50 <= range_m < 100:
            return EffectorRecommendation(
                effector="CRx-40",
                reason=f"RANGE_{int(range_m)}M_USE_40MM"
            )
        
        # Transition zone (250-400m) - prefer CRx-30 for accuracy
        if 250 < range_m < 400:
            return EffectorRecommendation(
                effector="CRx-30",
                reason=f"RANGE_{int(range_m)}M_TRANSITION_USE_30MM"
            )
        
        # CRx-30 optimal range (400-1000m)
        if 400 <= range_m <= 1000:
            return EffectorRecommendation(
                effector="CRx-30",
                reason=f"RANGE_{int(range_m)}M_LONG_RANGE"
            )
        
        # Fallback
        return EffectorRecommendation(
            effector="UNKNOWN",
            reason=f"RANGE_{int(range_m)}M_UNDETERMINED"
        )


class GunnerInterfaceService:
    """
    Main service for gunner interface
    - Streams tracks via UDP broadcast @ 10 Hz
    - Receives gunner status via UDP
    - Manages gunner station registry
    """
    
    def __init__(
        self,
        track_stream_port: int = 5100,
        status_receive_port: int = 5101,
        broadcast_address: str = "192.168.10.255",
        update_rate_hz: float = 10.0
    ):
        self.track_stream_port = track_stream_port
        self.status_receive_port = status_receive_port
        self.broadcast_address = broadcast_address
        self.update_rate_hz = update_rate_hz
        self.update_interval = 1.0 / update_rate_hz
        
        # Sockets
        self.stream_socket = None
        self.status_socket = None
        
        # Gunner registry
        self.gunner_stations: Dict[str, GunnerStatus] = {}
        self.gunner_lock = threading.Lock()
        
        # Callbacks
        self.on_gunner_status_callback: Optional[Callable[[GunnerStatus], None]] = None
        
        # Threading
        self.running = False
        self.stream_thread = None
        self.status_thread = None
        
        # Engagement control (operator-initiated)
        self.streaming_enabled = False
        self.engaged_track_id: Optional[int] = None
        self.engagement_start_time: Optional[float] = None
        
        # Data source (set externally)
        self.get_tracks_snapshot: Optional[Callable[[], TracksSnapshot]] = None
        
        print(f"[GUNNER INTERFACE] Initialized")
        print(f"  Track stream: UDP broadcast to {broadcast_address}:{track_stream_port}")
        print(f"  Status receive: UDP listen on port {status_receive_port}")
        print(f"  Update rate: {update_rate_hz} Hz")
    
    def start(self):
        """Start the gunner interface service"""
        if self.running:
            print("[GUNNER INTERFACE] Already running")
            return
        
        self.running = True
        
        # Set up sockets
        self._setup_stream_socket()
        self._setup_status_socket()
        
        # Start threads
        self.stream_thread = threading.Thread(
            target=self._stream_loop,
            name="GunnerTrackStream",
            daemon=True
        )
        self.stream_thread.start()
        
        self.status_thread = threading.Thread(
            target=self._status_receive_loop,
            name="GunnerStatusReceive",
            daemon=True
        )
        self.status_thread.start()
        
        print("[GUNNER INTERFACE] ✓ Service started")
    
    def stop(self):
        """Stop the gunner interface service"""
        print("[GUNNER INTERFACE] Stopping...")
        self.running = False
        
        if self.stream_thread:
            self.stream_thread.join(timeout=2.0)
        if self.status_thread:
            self.status_thread.join(timeout=2.0)
        
        if self.stream_socket:
            self.stream_socket.close()
        if self.status_socket:
            self.status_socket.close()
        
        print("[GUNNER INTERFACE] ✓ Stopped")
    
    def _setup_stream_socket(self):
        """Set up UDP broadcast socket for track streaming"""
        try:
            self.stream_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.stream_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            print(f"[GUNNER INTERFACE] ✓ Track stream socket ready")
        except Exception as e:
            print(f"[GUNNER INTERFACE] ✗ Stream socket error: {e}")
            raise
    
    def _setup_status_socket(self):
        """Set up UDP socket for receiving gunner status"""
        try:
            self.status_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.status_socket.bind(('0.0.0.0', self.status_receive_port))
            self.status_socket.settimeout(1.0)  # 1 second timeout for clean shutdown
            print(f"[GUNNER INTERFACE] ✓ Status receive socket ready on port {self.status_receive_port}")
        except Exception as e:
            print(f"[GUNNER INTERFACE] ✗ Status socket error: {e}")
            raise
    
    def engage_track(self, track_id: int, operator_id: str = "OPERATOR") -> bool:
        """
        Operator engages a specific track
        Begin streaming ONLY this track to gunners
        """
        self.engaged_track_id = track_id
        self.streaming_enabled = True
        self.engagement_start_time = time.time()
        
        print(f"[GUNNER INTERFACE] ✓ Track {track_id} ENGAGED by {operator_id}")
        print(f"[GUNNER INTERFACE]   Streaming to gunners started")
        return True
    
    def disengage_track(self) -> bool:
        """
        Operator cancels engagement
        Stop streaming to gunners
        """
        if self.engaged_track_id:
            print(f"[GUNNER INTERFACE] ✗ Track {self.engaged_track_id} DISENGAGED")
            self.engaged_track_id = None
            self.streaming_enabled = False
            self.engagement_start_time = None
            return True
        return False
    
    def switch_engaged_track(self, new_track_id: int) -> bool:
        """Switch to different track without disengaging"""
        old_track = self.engaged_track_id
        self.engaged_track_id = new_track_id
        self.engagement_start_time = time.time()
        print(f"[GUNNER INTERFACE] ↔ Switched from Track {old_track} to Track {new_track_id}")
        return True
    
    def is_engaged(self) -> bool:
        """Check if track is currently engaged"""
        return self.streaming_enabled and self.engaged_track_id is not None
    
    def get_engaged_track_id(self) -> Optional[int]:
        """Get currently engaged track ID"""
        return self.engaged_track_id if self.is_engaged() else None
    
    def _stream_loop(self):
        """Main loop for streaming tracks @ 10 Hz (ONLY if engaged)"""
        print("[GUNNER INTERFACE] Track streaming service started")
        print("[GUNNER INTERFACE] Waiting for operator engagement...")
        
        iteration = 0
        while self.running:
            loop_start = time.time()
            
            try:
                # Only stream if track is engaged
                if self.streaming_enabled and self.engaged_track_id and self.get_tracks_snapshot:
                    snapshot = self.get_tracks_snapshot()
                    
                    # Find engaged track
                    engaged_track = next(
                        (t for t in snapshot.tracks if t.track_id == self.engaged_track_id),
                        None
                    )
                    
                    if engaged_track:
                        # Stream ONLY the engaged track
                        single_track_snapshot = TracksSnapshot(
                            tracks=[engaged_track],
                            radar_online=snapshot.radar_online,
                            rf_online=snapshot.rf_online,
                            total_tracks=1,  # Only one track streamed
                            ownship_lat=snapshot.ownship_lat,
                            ownship_lon=snapshot.ownship_lon,
                            ownship_heading=snapshot.ownship_heading,
                            timestamp_ns=snapshot.timestamp_ns
                        )
                        
                        # Broadcast engaged track
                        self._broadcast_tracks(single_track_snapshot)
                        
                        # Log periodically
                        if iteration % 50 == 0:  # Every 5 seconds at 10 Hz
                            engagement_duration = time.time() - self.engagement_start_time
                            print(f"[GUNNER STREAM] Streaming Track {self.engaged_track_id} "
                                  f"({engagement_duration:.1f}s)")
                    else:
                        # Engaged track lost!
                        print(f"[GUNNER STREAM] ⚠️  Track {self.engaged_track_id} LOST from sensors")
                        print(f"[GUNNER STREAM]   Stopping stream")
                        self.disengage_track()
                
                iteration += 1
                
                # Maintain 10 Hz rate
                elapsed = time.time() - loop_start
                sleep_time = max(0, self.update_interval - elapsed)
                time.sleep(sleep_time)
                
            except Exception as e:
                print(f"[GUNNER STREAM] Error in stream loop: {e}")
                time.sleep(0.1)
        
        print("[GUNNER INTERFACE] Track streaming service stopped")
    
    def _broadcast_tracks(self, snapshot: TracksSnapshot):
        """Broadcast tracks snapshot via UDP"""
        try:
            # Convert to JSON (simple for now, can use protobuf later)
            data = {
                'tracks': [asdict(t) for t in snapshot.tracks],
                'radar_online': snapshot.radar_online,
                'rf_online': snapshot.rf_online,
                'total_tracks': snapshot.total_tracks,
                'ownship_lat': snapshot.ownship_lat,
                'ownship_lon': snapshot.ownship_lon,
                'ownship_heading': snapshot.ownship_heading,
                'timestamp_ns': snapshot.timestamp_ns
            }
            
            message = json.dumps(data).encode('utf-8')
            
            # Broadcast to all gunners
            self.stream_socket.sendto(
                message,
                (self.broadcast_address, self.track_stream_port)
            )
            
        except Exception as e:
            print(f"[GUNNER STREAM] Broadcast error: {e}")
    
    def _status_receive_loop(self):
        """Main loop for receiving gunner status"""
        print("[GUNNER INTERFACE] Status receiver started")
        
        while self.running:
            try:
                # Receive status message
                data, address = self.status_socket.recvfrom(4096)
                
                # Parse JSON
                status_dict = json.loads(data.decode('utf-8'))
                
                # Create GunnerStatus object
                status = GunnerStatus(**status_dict)
                status.last_seen = time.time()
                
                # Update registry
                self._update_gunner_status(status)
                
                # Callback
                if self.on_gunner_status_callback:
                    self.on_gunner_status_callback(status)
                
            except socket.timeout:
                # Normal timeout, continue
                continue
            except Exception as e:
                if self.running:  # Only log if not shutting down
                    print(f"[GUNNER STATUS] Receive error: {e}")
        
        print("[GUNNER INTERFACE] Status receiver stopped")
    
    def _update_gunner_status(self, status: GunnerStatus):
        """Update gunner station registry"""
        with self.gunner_lock:
            # New or updated gunner
            if status.station_id not in self.gunner_stations:
                print(f"[GUNNER REGISTRY] ✓ New gunner registered: {status.station_id}")
            
            self.gunner_stations[status.station_id] = status
            
            # Log important events
            if status.visual_lock:
                print(f"[GUNNER STATUS] {status.station_id}: VISUAL LOCK on Track {status.cued_track_id}")
            if status.cued_track_id != -1 and status.cued_track_id != getattr(
                self.gunner_stations.get(status.station_id, None), 'cued_track_id', -1
            ):
                print(f"[GUNNER STATUS] {status.station_id}: CUED Track {status.cued_track_id} "
                      f"(Weapon: {status.selected_weapon})")
    
    def get_gunner_status(self, station_id: str) -> Optional[GunnerStatus]:
        """Get status for specific gunner station"""
        with self.gunner_lock:
            return self.gunner_stations.get(station_id)
    
    def get_all_gunner_statuses(self) -> Dict[str, GunnerStatus]:
        """Get all gunner statuses"""
        with self.gunner_lock:
            return self.gunner_stations.copy()
    
    def cleanup_stale_gunners(self, timeout_sec: float = 10.0):
        """Remove gunner stations that haven't reported in timeout_sec"""
        with self.gunner_lock:
            current_time = time.time()
            stale = [
                station_id
                for station_id, status in self.gunner_stations.items()
                if current_time - status.last_seen > timeout_sec
            ]
            
            for station_id in stale:
                print(f"[GUNNER REGISTRY] ✗ Removing stale gunner: {station_id}")
                del self.gunner_stations[station_id]


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("  TriAD Gunner Interface Service - Standalone Test")
    print("=" * 70)
    print()
    
    # Create service
    service = GunnerInterfaceService(
        track_stream_port=5100,
        status_receive_port=5101,
        broadcast_address="255.255.255.255",  # Global broadcast for testing
        update_rate_hz=10.0
    )
    
    # Mock data source
    def get_mock_tracks():
        """Generate mock tracks for testing"""
        recommendation = EffectorRecommendationEngine.get_recommendation(680.0)
        
        track = TrackUpdate(
            track_id=2001,
            azimuth_deg=245.0,
            elevation_deg=14.0,
            range_m=680.0,
            velocity_x_mps=10.5,
            velocity_y_mps=5.2,
            velocity_z_mps=-1.0,
            speed_mps=12.0,
            heading_deg=270.0,
            type="UAV",
            confidence=0.89,
            source="FUSED",
            track_age_sec=5.3,
            num_updates=53,
            priority="HIGH",
            recommended_effector=recommendation.effector,
            recommendation_reason=recommendation.reason,
            aircraft_model="DJI Mavic 3",
            pilot_latitude=-25.847,
            pilot_longitude=28.185,
            timestamp_ns=time.time_ns()
        )
        
        return TracksSnapshot(
            tracks=[track],
            radar_online=True,
            rf_online=True,
            total_tracks=1,
            ownship_lat=-25.841105,
            ownship_lon=28.180340,
            ownship_heading=90.0,
            timestamp_ns=time.time_ns()
        )
    
    service.get_tracks_snapshot = get_mock_tracks
    
    # Callback for gunner status
    def on_gunner_status(status: GunnerStatus):
        print(f"\n[CALLBACK] Gunner status received:")
        print(f"  Station: {status.station_id}")
        print(f"  Cued Track: {status.cued_track_id}")
        print(f"  Visual Lock: {status.visual_lock}")
        print(f"  Weapon: {status.selected_weapon}")
        print()
    
    service.on_gunner_status_callback = on_gunner_status
    
    # Start service
    service.start()
    
    print()
    print("Service running. Press Ctrl+C to stop.")
    print("Listening for gunner status on UDP port 5101")
    print("Broadcasting tracks on UDP port 5100")
    print()
    
    try:
        while True:
            time.sleep(1)
            # Cleanup stale gunners every second
            service.cleanup_stale_gunners(timeout_sec=10.0)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        service.stop()
        print("Stopped.")
