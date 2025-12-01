#!/usr/bin/env python3
"""
Demo: Advanced Threat Assessment
Shows vector analysis, trajectory prediction, and threat classification
"""

from src.threat_assessment import AdvancedThreatAssessor, ThreatConfig, ThreatLevel
import math


def print_separator():
    print("=" * 80)


def demo_threat_scenarios():
    """
    Demonstrate threat assessment on various tactical scenarios
    """
    
    # Initialize assessor with default config
    assessor = AdvancedThreatAssessor()
    
    print_separator()
    print("ADVANCED THREAT ASSESSMENT DEMONSTRATION")
    print_separator()
    print()
    
    # ======================================================================
    # SCENARIO 1: Close, fast-approaching UAV (CRITICAL)
    # ======================================================================
    print("SCENARIO 1: Close Fast-Approaching UAV")
    print("-" * 80)
    
    track1 = {
        'id': 1001,
        'range_m': 250.0,
        'azimuth_deg': 0.0,      # Dead ahead
        'elevation_deg': 5.0,     # Ground-hugging
        'velocity_x_mps': 0.0,
        'velocity_y_mps': -35.0,  # 126 km/h toward ownship
        'velocity_z_mps': 0.0,
        'confidence': 0.9
    }
    
    assessment = assessor.assess_threat(track1)
    print_threat_assessment(assessment)
    print()
    
    # ======================================================================
    # SCENARIO 2: Collision course UAV at medium range (SEVERE)
    # ======================================================================
    print("SCENARIO 2: Collision Course - Medium Range")
    print("-" * 80)
    
    track2 = {
        'id': 1002,
        'range_m': 500.0,
        'azimuth_deg': 45.0,
        'elevation_deg': 10.0,
        'velocity_x_mps': -15.0,  # Moving toward ownship
        'velocity_y_mps': -15.0,
        'velocity_z_mps': 0.0,
        'confidence': 0.85
    }
    
    assessment = assessor.assess_threat(track2)
    print_threat_assessment(assessment)
    print()
    
    # ======================================================================
    # SCENARIO 3: Hovering UAV at close range (HIGH)
    # ======================================================================
    print("SCENARIO 3: Hovering UAV - Close Range")
    print("-" * 80)
    
    track3 = {
        'id': 1003,
        'range_m': 400.0,
        'azimuth_deg': 90.0,
        'elevation_deg': 15.0,
        'velocity_x_mps': 0.5,   # Nearly stationary
        'velocity_y_mps': 0.3,
        'velocity_z_mps': 0.0,
        'confidence': 0.75
    }
    
    assessment = assessor.assess_threat(track3)
    print_threat_assessment(assessment)
    print()
    
    # ======================================================================
    # SCENARIO 4: Perpendicular crossing track (MEDIUM)
    # ======================================================================
    print("SCENARIO 4: Perpendicular Crossing")
    print("-" * 80)
    
    track4 = {
        'id': 1004,
        'range_m': 700.0,
        'azimuth_deg': 0.0,
        'elevation_deg': 20.0,
        'velocity_x_mps': 25.0,   # Crossing left to right
        'velocity_y_mps': 0.0,
        'velocity_z_mps': 0.0,
        'confidence': 0.70
    }
    
    assessment = assessor.assess_threat(track4)
    print_threat_assessment(assessment)
    print()
    
    # ======================================================================
    # SCENARIO 5: Receding track (LOW)
    # ======================================================================
    print("SCENARIO 5: Receding Track")
    print("-" * 80)
    
    track5 = {
        'id': 1005,
        'range_m': 800.0,
        'azimuth_deg': 180.0,  # Behind
        'elevation_deg': 25.0,
        'velocity_x_mps': 0.0,
        'velocity_y_mps': 20.0,  # Moving away
        'velocity_z_mps': 0.0,
        'confidence': 0.60
    }
    
    assessment = assessor.assess_threat(track5)
    print_threat_assessment(assessment)
    print()
    
    # ======================================================================
    # SCENARIO 6: Distant slow mover (MINIMAL)
    # ======================================================================
    print("SCENARIO 6: Distant Slow Mover")
    print("-" * 80)
    
    track6 = {
        'id': 1006,
        'range_m': 1800.0,
        'azimuth_deg': 30.0,
        'elevation_deg': 30.0,
        'velocity_x_mps': -2.0,
        'velocity_y_mps': -3.0,
        'velocity_z_mps': 0.0,
        'confidence': 0.50
    }
    
    assessment = assessor.assess_threat(track6)
    print_threat_assessment(assessment)
    print()
    
    # ======================================================================
    # SWARM DETECTION DEMO
    # ======================================================================
    print_separator()
    print("SWARM DETECTION")
    print_separator()
    
    swarm_tracks = [
        {'id': 2001, 'range_m': 600, 'azimuth_deg': 45, 'elevation_deg': 10},
        {'id': 2002, 'range_m': 650, 'azimuth_deg': 50, 'elevation_deg': 12},
        {'id': 2003, 'range_m': 580, 'azimuth_deg': 42, 'elevation_deg': 8},
        {'id': 2004, 'range_m': 1500, 'azimuth_deg': 180, 'elevation_deg': 20},  # Far away
    ]
    
    swarms = assessor.detect_swarms(swarm_tracks)
    
    if swarms:
        print(f"🚨 Detected {len(swarms)} swarm(s):")
        for i, swarm in enumerate(swarms, 1):
            print(f"   Swarm {i}: Track IDs {swarm} ({len(swarm)} threats)")
    else:
        print("No swarms detected")
    
    print()
    print_separator()


def print_threat_assessment(assessment):
    """Pretty print threat assessment"""
    
    # Header with threat level
    level_colors = {
        ThreatLevel.CRITICAL: "🔴",
        ThreatLevel.SEVERE: "🟠",
        ThreatLevel.HIGH: "🟡",
        ThreatLevel.MEDIUM: "🔵",
        ThreatLevel.LOW: "🟢",
        ThreatLevel.MINIMAL: "⚪"
    }
    
    icon = level_colors.get(assessment.level, "⚫")
    
    print(f"{icon} Track {assessment.track_id} - {assessment.level.value}")
    print(f"   Threat Score: {assessment.score:.3f}")
    print()
    
    # Kinematic Analysis
    print("   KINEMATIC ANALYSIS:")
    print(f"   • Range: {assessment.range_m:.1f}m")
    print(f"   • Closing Speed: {assessment.closing_speed:.1f} m/s ({assessment.closing_speed * 3.6:.1f} km/h)")
    
    if assessment.time_to_impact:
        print(f"   • Time to Impact: {assessment.time_to_impact:.1f}s ⚠️")
    else:
        print(f"   • Time to Impact: Not applicable (receding/stationary)")
    print()
    
    # Vector Analysis
    print("   VECTOR ANALYSIS:")
    print(f"   • Approach Angle: {assessment.approach_angle:.1f}° ", end="")
    if assessment.approach_angle < 30:
        print("(Head-on)")
    elif assessment.approach_angle < 90:
        print("(Quartering)")
    else:
        print("(Crossing/Parallel)")
    
    print(f"   • Collision Course: {'YES ⚠️' if assessment.collision_course else 'No'}")
    print()
    
    # Elevation
    print("   ELEVATION ANALYSIS:")
    print(f"   • Elevation: {assessment.elevation_deg:.1f}°")
    print(f"   • Elevation Threat Factor: {assessment.elevation_threat_factor:.2f}")
    print()
    
    # Trajectory Prediction
    print("   TRAJECTORY PREDICTION:")
    print(f"   • Predicted Range (10s): {assessment.predicted_range_10s:.1f}m")
    print(f"   • Predicted Range (30s): {assessment.predicted_range_30s:.1f}m")
    
    # Show if getting closer
    if assessment.predicted_range_10s < assessment.range_m:
        delta = assessment.range_m - assessment.predicted_range_10s
        print(f"   • ⚠️ Will be {delta:.0f}m CLOSER in 10s")
    print()
    
    # Recommendations
    print("   RECOMMENDATION:")
    print(f"   • Engage: {'YES ✓' if assessment.engage_recommended else 'NO'}")
    print(f"   • {assessment.urgency_message}")


if __name__ == '__main__':
    demo_threat_scenarios()
    
    print()
    print("=" * 80)
    print("Demo complete! This module can now be integrated into the bridge.")
    print("=" * 80)
