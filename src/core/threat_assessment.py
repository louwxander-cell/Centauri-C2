"""
Threat Prioritization Algorithm
Determines highest threat based on:
1. Distance (how close is it NOW)
2. Current trajectory (is it approaching NOW)
3. Capability to reach us (could it turn toward us)
4. Velocity (how fast can it get here)
"""

import math
from typing import List, Optional, Tuple
from .datamodels import Track


class ThreatAssessment:
    """
    Assess and prioritize threats based on multiple factors.
    
    Threat Score Factors:
    1. Distance (50%) - How close is it right now
    2. Current Direction (20%) - Is it approaching us now
    3. Capability (20%) - Time to reach us if it turns toward us
    4. Velocity (10%) - How fast is it moving
    """
    
    # Weight factors for threat calculation
    WEIGHT_DISTANCE = 0.50       # 50% - Distance is MOST critical
    WEIGHT_DIRECTION = 0.20      # 20% - Current trajectory
    WEIGHT_CAPABILITY = 0.20     # 20% - Potential to reach us
    WEIGHT_VELOCITY = 0.10       # 10% - Speed factor
    
    # Threat ranges (meters)
    CRITICAL_RANGE = 500.0       # < 500m = critical
    HIGH_RANGE = 1000.0          # < 1km = high
    MEDIUM_RANGE = 2000.0        # < 2km = medium
    LOW_RANGE = 5000.0           # < 5km = low
    
    @staticmethod
    def calculate_threat_score(track: Track, ownship_velocity: Tuple[float, float] = (0, 0)) -> float:
        """
        Calculate threat score for a track.
        
        Key Innovation: Considers both CURRENT threat (distance + direction) 
        and POTENTIAL threat (capability to reach us if it turns toward us).
        
        Args:
            track: Track to assess
            ownship_velocity: Ownship velocity (vx, vy) in m/s
        
        Returns:
            Threat score (0.0 - 1.0, higher = more threatening)
        """
        # 1. Distance score - How close is it RIGHT NOW
        distance_score = ThreatAssessment._calculate_distance_score(track.range_m)
        
        # 2. Direction score - Is it approaching us RIGHT NOW
        direction_score = ThreatAssessment._calculate_direction_score(track)
        
        # 3. Capability score - Time to reach us IF IT TURNS TOWARD US
        capability_score = ThreatAssessment._calculate_capability_score(track)
        
        # 4. Velocity score - How fast is it moving
        velocity_score = ThreatAssessment._calculate_velocity_score(track)
        
        # Filter by track type
        # BIRDS pose no threat - return 0
        if track.type == "BIRD":
            return 0.0
        
        # Weighted combination
        threat_score = (
            ThreatAssessment.WEIGHT_DISTANCE * distance_score +
            ThreatAssessment.WEIGHT_DIRECTION * direction_score +
            ThreatAssessment.WEIGHT_CAPABILITY * capability_score +
            ThreatAssessment.WEIGHT_VELOCITY * velocity_score
        )
        
        # Type-based adjustments
        if track.type == "UAV":
            # Confirmed drone = serious threat (boost)
            threat_score *= 1.3
        elif track.type == "UNKNOWN":
            # Unknown = reduced threat (80% reduction = 20% of calculated score)
            threat_score *= 0.20
        
        # Critical multipliers (only for drones)
        if track.type == "UAV":
            # Close AND approaching = immediate danger
            if distance_score > 0.85 and direction_score > 0.7:
                threat_score *= 1.25
            
            # Very close = always critical regardless of direction
            if track.range_m < 300:
                threat_score = max(threat_score, 0.95)
        
        # Clamp to 0-1
        return min(1.0, max(0.0, threat_score))
    
    @staticmethod
    def _calculate_distance_score(range_m: float) -> float:
        """
        Calculate distance threat score with exponential decay.
        Closer = much higher score (exponential, not linear).
        
        This heavily prioritizes close threats.
        """
        if range_m < 250:
            return 1.0  # Immediate critical threat
        elif range_m < 500:
            return 0.95  # Very close
        elif range_m < 750:
            return 0.85  # Close
        elif range_m < 1000:
            return 0.70  # Near
        elif range_m < 1500:
            return 0.50  # Medium
        elif range_m < 2000:
            return 0.30  # Far
        else:
            # Beyond 2km, exponential decay
            return max(0.0, 0.30 * math.exp(-(range_m - 2000) / 2000))
    
    @staticmethod
    def _calculate_direction_score(track: Track) -> float:
        """
        Calculate direction threat score.
        Is the drone heading toward us RIGHT NOW?
        
        1.0 = directly approaching
        0.5 = perpendicular
        0.0 = moving away
        """
        if not track.heading:
            return 0.5  # Unknown direction = medium threat
        
        # Calculate bearing from track to ownship (reciprocal of azimuth)
        bearing_to_ownship = (track.azimuth + 180) % 360
        
        # Calculate angle difference between track heading and bearing to us
        heading_diff = abs(track.heading - bearing_to_ownship)
        
        # Normalize to 0-180 degrees
        if heading_diff > 180:
            heading_diff = 360 - heading_diff
        
        # Convert to score:
        # 0° (heading toward us) = 1.0
        # 90° (perpendicular) = 0.5  
        # 180° (heading away) = 0.0
        direction_score = 1.0 - (heading_diff / 180.0)
        
        return direction_score
    
    @staticmethod
    def _calculate_capability_score(track: Track) -> float:
        """
        Calculate capability threat score.
        How quickly COULD it reach us if it turned toward us right now?
        
        This is the KEY to handling drones that might spot us and turn.
        Time to intercept = distance / velocity
        
        Lower time = higher threat
        """
        if not track.velocity_mps or track.velocity_mps < 1.0:
            return 0.3  # Stationary/slow = lower capability threat
        
        # Time to reach us if it turns toward us NOW (in seconds)
        time_to_intercept = track.range_m / track.velocity_mps
        
        # Convert to threat score
        # < 30 seconds = 1.0 (critical)
        # < 60 seconds = 0.8 (high)
        # < 120 seconds = 0.6 (medium)
        # < 180 seconds = 0.4 (low)
        # > 180 seconds = declining
        
        if time_to_intercept < 30:
            return 1.0
        elif time_to_intercept < 60:
            return 0.8
        elif time_to_intercept < 120:
            return 0.6
        elif time_to_intercept < 180:
            return 0.4
        else:
            # Exponential decay beyond 3 minutes
            return max(0.0, 0.4 * math.exp(-(time_to_intercept - 180) / 120))
    
    @staticmethod
    def _calculate_velocity_score(track: Track) -> float:
        """
        Calculate velocity threat score.
        Faster drones are more dangerous (can close distance quickly).
        
        Typical drone speeds: 5-25 m/s
        Racing drones: up to 40 m/s
        """
        if not track.velocity_mps:
            return 0.5  # Unknown velocity = medium threat
        
        # Normalize velocity to 0-1
        # 0 m/s = 0.0
        # 15 m/s (typical) = 0.5
        # 30 m/s (fast) = 1.0
        velocity_score = min(1.0, track.velocity_mps / 30.0)
        
        return velocity_score
    
    @staticmethod
    def get_threat_level(threat_score: float) -> str:
        """
        Get threat level string from score.
        
        Returns:
            "CRITICAL", "HIGH", "MEDIUM", "LOW", or "MINIMAL"
        """
        if threat_score >= 0.8:
            return "CRITICAL"
        elif threat_score >= 0.6:
            return "HIGH"
        elif threat_score >= 0.4:
            return "MEDIUM"
        elif threat_score >= 0.2:
            return "LOW"
        else:
            return "MINIMAL"
    
    @staticmethod
    def get_threat_color(threat_score: float) -> str:
        """
        Get color for threat level.
        
        Returns:
            Hex color string
        """
        if threat_score >= 0.8:
            return "#ef4444"  # Red - Critical
        elif threat_score >= 0.6:
            return "#f97316"  # Orange - High
        elif threat_score >= 0.4:
            return "#fbbf24"  # Yellow - Medium
        elif threat_score >= 0.2:
            return "#60a5fa"  # Blue - Low
        else:
            return "#9ca3af"  # Gray - Minimal
    
    @staticmethod
    def prioritize_tracks(tracks: List[Track], ownship_velocity: Tuple[float, float] = (0, 0)) -> List[Tuple[Track, float]]:
        """
        Prioritize tracks by threat level.
        
        Args:
            tracks: List of tracks to prioritize
            ownship_velocity: Ownship velocity (vx, vy)
        
        Returns:
            List of (track, threat_score) tuples, sorted by threat (highest first)
        """
        # Calculate threat scores
        track_scores = [
            (track, ThreatAssessment.calculate_threat_score(track, ownship_velocity))
            for track in tracks
        ]
        
        # Sort by threat score (descending)
        track_scores.sort(key=lambda x: x[1], reverse=True)
        
        return track_scores
    
    @staticmethod
    def get_highest_threat(tracks: List[Track], ownship_velocity: Tuple[float, float] = (0, 0)) -> Optional[Track]:
        """
        Get the highest threat track.
        
        Args:
            tracks: List of tracks
            ownship_velocity: Ownship velocity
        
        Returns:
            Highest threat track, or None if no tracks
        """
        if not tracks:
            return None
        
        prioritized = ThreatAssessment.prioritize_tracks(tracks, ownship_velocity)
        return prioritized[0][0] if prioritized else None
