"""
Advanced Threat Assessment Module
Enhances base threat scoring with vector analysis, trajectory prediction, and swarm detection
"""
import math
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum


class ThreatLevel(Enum):
    """Clear threat classifications for operator awareness"""
    CRITICAL = "CRITICAL"      # <100m, immediate action required
    SEVERE = "SEVERE"          # 100-300m, engage recommended
    HIGH = "HIGH"              # 300-600m, track closely
    MEDIUM = "MEDIUM"          # 600-1000m, monitor
    LOW = "LOW"                # 1000-1500m, awareness
    MINIMAL = "MINIMAL"        # >1500m, distant


@dataclass
class ThreatConfig:
    """Configurable threat assessment parameters"""
    
    # Range zones (meters)
    critical_range: float = 100.0
    severe_range: float = 300.0
    high_range: float = 600.0
    medium_range: float = 1000.0
    low_range: float = 1500.0
    
    # Velocity thresholds (m/s)
    fast_approach_threshold: float = 30.0  # ~108 km/h
    slow_approach_threshold: float = 10.0  # ~36 km/h
    hovering_threshold: float = 2.0        # ~7 km/h
    
    # Elevation threat zones (degrees)
    ground_hugging_threshold: float = 5.0   # Very low altitude
    low_altitude_threshold: float = 15.0    # Low but not terrain-masking
    
    # Tau (time-to-impact) thresholds (seconds)
    tau_critical: float = 10.0
    tau_severe: float = 20.0
    tau_high: float = 35.0
    tau_medium: float = 60.0
    
    # Weights for multi-factor scoring
    weight_range_proximity: float = 0.35
    weight_velocity_threat: float = 0.25
    weight_approach_vector: float = 0.20
    weight_elevation_threat: float = 0.10
    weight_confidence: float = 0.10
    
    # Swarm detection
    swarm_radius: float = 200.0  # meters
    swarm_min_count: int = 3
    
    # Protection zone
    no_fire_radius: float = 50.0  # meters from ownship


@dataclass
class ThreatAssessment:
    """Complete threat assessment output"""
    track_id: int
    score: float  # 0.0 - 1.0
    level: ThreatLevel
    
    # Kinematic analysis
    range_m: float
    closing_speed: float  # m/s (negative = approaching)
    time_to_impact: Optional[float]  # seconds (None if not approaching)
    
    # Vector analysis
    approach_angle: float  # degrees (0 = head-on, 90 = perpendicular)
    collision_course: bool
    
    # Elevation
    elevation_deg: float
    elevation_threat_factor: float
    
    # Trajectory prediction
    predicted_position_10s: Tuple[float, float, float]  # (x, y, z)
    predicted_position_30s: Tuple[float, float, float]
    predicted_range_10s: float
    predicted_range_30s: float
    
    # Context
    is_part_of_swarm: bool
    swarm_id: Optional[int]
    confidence: float
    
    # Recommendations
    engage_recommended: bool
    urgency_message: str


class AdvancedThreatAssessor:
    """
    Advanced threat assessment with vector analysis, trajectory prediction, and swarm detection
    """
    
    def __init__(self, config: Optional[ThreatConfig] = None):
        self.config = config or ThreatConfig()
        self.track_history: Dict[int, List[Dict]] = {}  # Track ID -> history
        self.swarms: List[List[int]] = []  # Detected swarms (list of track IDs)
        
    def assess_threat(self, track_data: Dict, ownship_position: Tuple[float, float, float] = (0, 0, 0)) -> ThreatAssessment:
        """
        Comprehensive threat assessment for a single track
        
        Args:
            track_data: Track information dict
            ownship_position: (x, y, z) ownship position in local frame
            
        Returns:
            ThreatAssessment with complete analysis
        """
        track_id = track_data['id']
        
        # Extract track kinematics
        range_m = track_data.get('range_m', 9999.0)
        azimuth_deg = track_data.get('azimuth_deg', 0.0)
        elevation_deg = track_data.get('elevation_deg', 0.0)
        
        # Velocity (m/s)
        vx = track_data.get('velocity_x_mps', 0.0)
        vy = track_data.get('velocity_y_mps', 0.0)
        vz = track_data.get('velocity_z_mps', 0.0)
        
        confidence = track_data.get('confidence', 0.0)
        
        # ==============================================================
        # 1. KINEMATIC ANALYSIS
        # ==============================================================
        closing_speed, time_to_impact = self._calculate_closing_velocity(
            range_m, azimuth_deg, elevation_deg, vx, vy, vz
        )
        
        # ==============================================================
        # 2. VECTOR ANALYSIS
        # ==============================================================
        approach_angle, collision_course = self._analyze_approach_vector(
            range_m, azimuth_deg, elevation_deg, vx, vy, vz
        )
        
        # ==============================================================
        # 3. ELEVATION THREAT MODELING
        # ==============================================================
        elevation_threat_factor = self._calculate_elevation_threat(elevation_deg, range_m)
        
        # ==============================================================
        # 4. TRAJECTORY PREDICTION
        # ==============================================================
        pred_10s, pred_30s, pred_range_10s, pred_range_30s = self._predict_trajectory(
            range_m, azimuth_deg, elevation_deg, vx, vy, vz
        )
        
        # ==============================================================
        # 5. MULTI-FACTOR THREAT SCORE
        # ==============================================================
        
        # Range proximity factor (exponential decay)
        range_factor = math.exp(-range_m / 400.0)  # Decay constant = 400m
        
        # Velocity threat factor
        velocity_factor = self._calculate_velocity_threat(closing_speed, time_to_impact)
        
        # Approach vector factor
        vector_factor = self._calculate_vector_threat(approach_angle, collision_course)
        
        # Confidence factor
        confidence_factor = confidence
        
        # Weighted combination
        base_score = (
            self.config.weight_range_proximity * range_factor +
            self.config.weight_velocity_threat * velocity_factor +
            self.config.weight_approach_vector * vector_factor +
            self.config.weight_elevation_threat * elevation_threat_factor +
            self.config.weight_confidence * confidence_factor
        )
        
        # Clamp to [0, 1]
        threat_score = max(0.0, min(1.0, base_score))
        
        # ==============================================================
        # 6. THREAT LEVEL CLASSIFICATION
        # ==============================================================
        threat_level = self._classify_threat_level(range_m, threat_score, time_to_impact)
        
        # ==============================================================
        # 7. SWARM DETECTION (would need all tracks - placeholder for now)
        # ==============================================================
        is_part_of_swarm = False
        swarm_id = None
        
        # ==============================================================
        # 8. ENGAGEMENT RECOMMENDATIONS
        # ==============================================================
        engage_recommended, urgency_message = self._generate_recommendations(
            threat_level, time_to_impact, collision_course, range_m
        )
        
        return ThreatAssessment(
            track_id=track_id,
            score=threat_score,
            level=threat_level,
            range_m=range_m,
            closing_speed=closing_speed,
            time_to_impact=time_to_impact,
            approach_angle=approach_angle,
            collision_course=collision_course,
            elevation_deg=elevation_deg,
            elevation_threat_factor=elevation_threat_factor,
            predicted_position_10s=pred_10s,
            predicted_position_30s=pred_30s,
            predicted_range_10s=pred_range_10s,
            predicted_range_30s=pred_range_30s,
            is_part_of_swarm=is_part_of_swarm,
            swarm_id=swarm_id,
            confidence=confidence,
            engage_recommended=engage_recommended,
            urgency_message=urgency_message
        )
    
    def _calculate_closing_velocity(self, range_m: float, az_deg: float, el_deg: float,
                                    vx: float, vy: float, vz: float) -> Tuple[float, Optional[float]]:
        """
        Calculate closing velocity (range rate) and time to impact
        
        Returns:
            (closing_speed in m/s, time_to_impact in seconds or None)
            Negative closing_speed = approaching
        """
        # Convert spherical to Cartesian unit vector pointing TO target
        az_rad = math.radians(az_deg)
        el_rad = math.radians(el_deg)
        
        # Unit vector from ownship to target
        rx = math.cos(el_rad) * math.sin(az_rad)
        ry = math.cos(el_rad) * math.cos(az_rad)
        rz = math.sin(el_rad)
        
        # Velocity dot range unit vector = radial velocity component
        # Negative = approaching, Positive = receding
        closing_speed = -(vx * rx + vy * ry + vz * rz)
        
        # Time to impact (only if approaching)
        if closing_speed > 0.5:  # Approaching with meaningful speed
            time_to_impact = range_m / closing_speed
        else:
            time_to_impact = None
            
        return closing_speed, time_to_impact
    
    def _analyze_approach_vector(self, range_m: float, az_deg: float, el_deg: float,
                                 vx: float, vy: float, vz: float) -> Tuple[float, bool]:
        """
        Analyze approach vector to determine threat geometry
        
        Returns:
            (approach_angle in degrees, collision_course boolean)
            approach_angle: 0° = head-on, 90° = perpendicular, 180° = parallel
        """
        # Target position vector
        az_rad = math.radians(az_deg)
        el_rad = math.radians(el_deg)
        
        pos_x = range_m * math.cos(el_rad) * math.sin(az_rad)
        pos_y = range_m * math.cos(el_rad) * math.cos(az_rad)
        pos_z = range_m * math.sin(el_rad)
        
        # Velocity magnitude
        v_mag = math.sqrt(vx**2 + vy**2 + vz**2)
        
        if v_mag < 0.1:  # Stationary
            return 90.0, False  # Perpendicular (ambiguous)
        
        # Position magnitude
        r_mag = range_m
        
        # Angle between velocity and position vectors
        # cos(theta) = (v · r) / (|v| * |r|)
        dot_product = vx * pos_x + vy * pos_y + vz * pos_z
        cos_angle = dot_product / (v_mag * r_mag)
        cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp for numerical stability
        
        # Approach angle: 0° = directly toward ownship
        approach_angle = math.degrees(math.acos(-cos_angle))
        
        # Collision course if velocity points within 30° of ownship
        collision_course = approach_angle < 30.0
        
        return approach_angle, collision_course
    
    def _calculate_elevation_threat(self, elevation_deg: float, range_m: float) -> float:
        """
        Low-altitude threats are more dangerous (terrain masking, pop-up attacks)
        
        Returns threat factor 0.0 - 1.0
        """
        if elevation_deg < self.config.ground_hugging_threshold:
            # Ground-hugging: Maximum threat (terrain masking)
            base_threat = 1.0
        elif elevation_deg < self.config.low_altitude_threshold:
            # Low altitude: High threat
            base_threat = 0.7
        elif elevation_deg < 30.0:
            # Medium altitude
            base_threat = 0.4
        else:
            # High altitude: Lower threat (easier to track)
            base_threat = 0.2
        
        # Reduce threat for distant tracks
        if range_m > 1000:
            base_threat *= 0.5
            
        return base_threat
    
    def _calculate_velocity_threat(self, closing_speed: float, time_to_impact: Optional[float]) -> float:
        """
        Threat based on velocity and time-to-impact
        
        Returns threat factor 0.0 - 1.0
        """
        if time_to_impact is None or time_to_impact <= 0:
            # Not approaching or already past
            return 0.1
        
        # Tau-based threat (TCAS-inspired)
        if time_to_impact < self.config.tau_critical:
            tau_factor = 1.0
        elif time_to_impact < self.config.tau_severe:
            tau_factor = 0.85
        elif time_to_impact < self.config.tau_high:
            tau_factor = 0.65
        elif time_to_impact < self.config.tau_medium:
            tau_factor = 0.40
        else:
            tau_factor = 0.15
        
        # Speed factor
        if closing_speed > self.config.fast_approach_threshold:
            speed_factor = 1.0  # Very fast
        elif closing_speed > self.config.slow_approach_threshold:
            speed_factor = 0.7  # Moderate speed
        else:
            speed_factor = 0.4  # Slow approach
        
        # Combined
        velocity_threat = (tau_factor * 0.7 + speed_factor * 0.3)
        
        return velocity_threat
    
    def _calculate_vector_threat(self, approach_angle: float, collision_course: bool) -> float:
        """
        Threat based on approach geometry
        
        Returns threat factor 0.0 - 1.0
        """
        if collision_course:
            # Direct collision course: maximum threat
            return 1.0
        
        # Threat decreases with approach angle
        if approach_angle < 45:
            return 0.8  # Nearly head-on
        elif approach_angle < 90:
            return 0.5  # Quartering approach
        elif approach_angle < 135:
            return 0.2  # Crossing
        else:
            return 0.1  # Parallel or receding
    
    def _predict_trajectory(self, range_m: float, az_deg: float, el_deg: float,
                           vx: float, vy: float, vz: float) -> Tuple[
                               Tuple[float, float, float],  # 10s position
                               Tuple[float, float, float],  # 30s position
                               float,  # 10s range
                               float   # 30s range
                           ]:
        """
        Predict future position assuming constant velocity
        
        Returns positions and ranges at 10s and 30s
        """
        # Current position in Cartesian
        az_rad = math.radians(az_deg)
        el_rad = math.radians(el_deg)
        
        x0 = range_m * math.cos(el_rad) * math.sin(az_rad)
        y0 = range_m * math.cos(el_rad) * math.cos(az_rad)
        z0 = range_m * math.sin(el_rad)
        
        # Predict at 10s
        x_10 = x0 + vx * 10.0
        y_10 = y0 + vy * 10.0
        z_10 = z0 + vz * 10.0
        range_10 = math.sqrt(x_10**2 + y_10**2 + z_10**2)
        
        # Predict at 30s
        x_30 = x0 + vx * 30.0
        y_30 = y0 + vy * 30.0
        z_30 = z0 + vz * 30.0
        range_30 = math.sqrt(x_30**2 + y_30**2 + z_30**2)
        
        return (x_10, y_10, z_10), (x_30, y_30, z_30), range_10, range_30
    
    def _classify_threat_level(self, range_m: float, score: float, 
                               time_to_impact: Optional[float]) -> ThreatLevel:
        """
        Classify threat into actionable levels
        """
        # Critical override: very close or imminent impact
        if range_m < self.config.critical_range:
            return ThreatLevel.CRITICAL
        if time_to_impact and time_to_impact < 10.0:
            return ThreatLevel.CRITICAL
        
        # Score-based classification
        if score > 0.85:
            return ThreatLevel.CRITICAL
        elif score > 0.70:
            return ThreatLevel.SEVERE
        elif score > 0.50:
            return ThreatLevel.HIGH
        elif score > 0.30:
            return ThreatLevel.MEDIUM
        elif score > 0.15:
            return ThreatLevel.LOW
        else:
            return ThreatLevel.MINIMAL
    
    def _generate_recommendations(self, threat_level: ThreatLevel, 
                                  time_to_impact: Optional[float],
                                  collision_course: bool,
                                  range_m: float) -> Tuple[bool, str]:
        """
        Generate engagement recommendations and urgency messages
        
        Returns:
            (engage_recommended, urgency_message)
        """
        engage = False
        message = ""
        
        if threat_level == ThreatLevel.CRITICAL:
            engage = True
            if time_to_impact and time_to_impact < 15:
                message = f"⚠️ IMMEDIATE ACTION - Impact in {time_to_impact:.0f}s"
            else:
                message = f"⚠️ CRITICAL THREAT - {range_m:.0f}m"
        
        elif threat_level == ThreatLevel.SEVERE:
            engage = collision_course  # Recommend if on collision course
            message = f"🔴 ENGAGE RECOMMENDED - {range_m:.0f}m"
        
        elif threat_level == ThreatLevel.HIGH:
            message = f"🟠 HIGH THREAT - Track closely"
        
        elif threat_level == ThreatLevel.MEDIUM:
            message = f"🟡 MONITOR - {range_m:.0f}m"
        
        elif threat_level == ThreatLevel.LOW:
            message = f"🟢 LOW THREAT - Awareness"
        
        else:
            message = f"⚪ Distant - {range_m:.0f}m"
        
        return engage, message
    
    def detect_swarms(self, all_tracks: List[Dict]) -> List[List[int]]:
        """
        Detect coordinated swarm attacks (multiple tracks in proximity)
        
        Returns:
            List of swarms, each swarm is a list of track IDs
        """
        if len(all_tracks) < self.config.swarm_min_count:
            return []
        
        # Build position matrix
        positions = []
        track_ids = []
        for track in all_tracks:
            range_m = track.get('range_m', 9999)
            az_deg = track.get('azimuth_deg', 0)
            el_deg = track.get('elevation_deg', 0)
            
            # Convert to Cartesian
            az_rad = math.radians(az_deg)
            el_rad = math.radians(el_deg)
            x = range_m * math.cos(el_rad) * math.sin(az_rad)
            y = range_m * math.cos(el_rad) * math.cos(az_rad)
            z = range_m * math.sin(el_rad)
            
            positions.append([x, y, z])
            track_ids.append(track['id'])
        
        positions = np.array(positions)
        
        # Simple clustering: find groups within swarm_radius
        swarms = []
        assigned = set()
        
        for i, pos_i in enumerate(positions):
            if track_ids[i] in assigned:
                continue
                
            # Find nearby tracks
            swarm = [track_ids[i]]
            assigned.add(track_ids[i])
            
            for j, pos_j in enumerate(positions):
                if i == j or track_ids[j] in assigned:
                    continue
                
                # Distance between tracks
                dist = np.linalg.norm(pos_i - pos_j)
                if dist < self.config.swarm_radius:
                    swarm.append(track_ids[j])
                    assigned.add(track_ids[j])
            
            if len(swarm) >= self.config.swarm_min_count:
                swarms.append(swarm)
        
        self.swarms = swarms
        return swarms
