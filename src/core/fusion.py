"""Track fusion logic for combining radar and RF sensor data"""

import math
from typing import Dict, List, Optional
from .datamodels import Track, SensorSource, TargetType
import time


class TrackFusion:
    """
    Fuses tracks from multiple sensors (Radar + RF) into consolidated tracks.
    Uses simple distance-based correlation.
    """
    
    def __init__(self, distance_threshold_m: float = 50.0, timeout_sec: float = 5.0):
        """
        Args:
            distance_threshold_m: Maximum distance for track correlation
            timeout_sec: Time before tracks are considered stale
        """
        self.distance_threshold = distance_threshold_m
        self.timeout_sec = timeout_sec
        self.tracks: Dict[int, Track] = {}  # Active fused tracks
        self._next_id = 1000  # Start fused track IDs at 1000
        
    def update_track(self, track: Track) -> Optional[Track]:
        """
        Process incoming track and attempt fusion.
        Returns fused track if correlation found, otherwise returns input track.
        """
        # Remove stale tracks first
        self._remove_stale_tracks()
        
        # If already a fused track, just update it
        if track.source == SensorSource.FUSED:
            self.tracks[track.id] = track
            return track
        
        # Try to correlate with existing tracks
        correlated_track = self._find_correlation(track)
        
        if correlated_track:
            # Fuse the tracks
            fused = self._fuse_tracks(correlated_track, track)
            self.tracks[fused.id] = fused
            return fused
        else:
            # No correlation, store as new track
            if track.id not in self.tracks:
                self.tracks[track.id] = track
            return track
    
    def _find_correlation(self, track: Track) -> Optional[Track]:
        """Find existing track that correlates with input track"""
        for existing_track in self.tracks.values():
            if existing_track.source == track.source:
                continue  # Don't correlate same sensor
            
            distance = self._calculate_distance(track, existing_track)
            if distance < self.distance_threshold:
                return existing_track
        
        return None
    
    def _calculate_distance(self, track1: Track, track2: Track) -> float:
        """
        Calculate 3D distance between two tracks using spherical coordinates.
        Simplified calculation assuming small distances.
        """
        # Convert to Cartesian coordinates
        r1, az1, el1 = track1.range_m, math.radians(track1.azimuth), math.radians(track1.elevation)
        r2, az2, el2 = track2.range_m, math.radians(track2.azimuth), math.radians(track2.elevation)
        
        x1 = r1 * math.cos(el1) * math.sin(az1)
        y1 = r1 * math.cos(el1) * math.cos(az1)
        z1 = r1 * math.sin(el1)
        
        x2 = r2 * math.cos(el2) * math.sin(az2)
        y2 = r2 * math.cos(el2) * math.cos(az2)
        z2 = r2 * math.sin(el2)
        
        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
        return distance
    
    def _fuse_tracks(self, track1: Track, track2: Track) -> Track:
        """
        Fuse two correlated tracks into a single track.
        Uses weighted average based on confidence.
        """
        # Weight by confidence
        w1 = track1.confidence
        w2 = track2.confidence
        total_weight = w1 + w2
        
        # Weighted average of position
        fused_range = (track1.range_m * w1 + track2.range_m * w2) / total_weight
        fused_azimuth = (track1.azimuth * w1 + track2.azimuth * w2) / total_weight
        fused_elevation = (track1.elevation * w1 + track2.elevation * w2) / total_weight
        
        # Use higher confidence classification
        fused_type = track1.type if track1.confidence > track2.confidence else track2.type
        fused_confidence = max(track1.confidence, track2.confidence) * 1.2  # Boost for multi-sensor
        fused_confidence = min(fused_confidence, 1.0)  # Cap at 1.0
        
        # Create fused track
        fused_id = track1.id if track1.source == SensorSource.FUSED else self._next_id
        if track1.source != SensorSource.FUSED:
            self._next_id += 1
        
        return Track(
            id=fused_id,
            azimuth=fused_azimuth,
            elevation=fused_elevation,
            range_m=fused_range,
            type=fused_type,
            confidence=fused_confidence,
            source=SensorSource.FUSED,
            timestamp=time.time(),
            velocity_mps=track1.velocity_mps or track2.velocity_mps,
            heading=track1.heading or track2.heading
        )
    
    def _remove_stale_tracks(self):
        """Remove tracks that have timed out"""
        current_time = time.time()
        stale_ids = [
            track_id for track_id, track in self.tracks.items()
            if (current_time - track.timestamp) > self.timeout_sec
        ]
        
        for track_id in stale_ids:
            del self.tracks[track_id]
    
    def get_active_tracks(self) -> List[Track]:
        """Get all active tracks"""
        self._remove_stale_tracks()
        return list(self.tracks.values())
    
    def clear(self):
        """Clear all tracks"""
        self.tracks.clear()
