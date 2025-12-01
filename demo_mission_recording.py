#!/usr/bin/env python3
"""
Demo: Mission Recording & Playback System
Shows recording, playback with speed control, and analysis
"""

import time
import math
from src.mission_recording import (
    MissionRecorder,
    PlaybackController,
    MissionAnalyzer,
    EventType
)


def simulate_mission(recorder: MissionRecorder, duration: float = 30.0):
    """
    Simulate a realistic mission with multiple tracks
    
    Args:
        recorder: MissionRecorder instance
        duration: Mission duration in seconds
    """
    print(f"\n[DEMO] Simulating {duration}s mission...")
    
    start_time = time.time()
    update_interval = 0.1  # 10 Hz
    
    # Track pool
    tracks = {}
    next_track_id = 1000
    
    # Spawn new tracks occasionally
    spawn_timer = 0.0
    
    while (time.time() - start_time) < duration:
        elapsed = time.time() - start_time
        
        # Spawn new tracks
        spawn_timer += update_interval
        if spawn_timer > 3.0 and len(tracks) < 8:  # Max 8 tracks
            spawn_timer = 0.0
            
            # Create new track
            track_id = next_track_id
            next_track_id += 1
            
            tracks[track_id] = {
                'id': track_id,
                'type': 'UAV' if track_id % 3 != 0 else 'UNKNOWN',
                'range_m': 1000.0 + (track_id % 500),
                'azimuth_deg': (track_id * 30) % 360,
                'elevation_deg': 10.0 + (track_id % 20),
                'velocity_x_mps': -5.0 + (track_id % 10),
                'velocity_y_mps': -10.0 - (track_id % 15),
                'velocity_z_mps': 0.0,
                'confidence': 0.7 + (track_id % 3) * 0.1,
                'source': 'FUSED' if track_id % 2 == 0 else 'RADAR'
            }
        
        # Update existing tracks
        tracks_to_remove = []
        for track_id, track in tracks.items():
            # Move closer
            track['range_m'] -= abs(track['velocity_y_mps']) * update_interval
            
            # Update threat priority (simple calculation)
            range_factor = math.exp(-track['range_m'] / 400.0)
            track['threat_priority'] = range_factor * track['confidence']
            
            # Remove if too close or too far
            if track['range_m'] < 50 or track['range_m'] > 2000:
                tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del tracks[track_id]
        
        # Record current tracks
        track_list = list(tracks.values())
        recorder.record_tracks(track_list)
        
        # Simulate operator selections
        if len(track_list) > 0 and elapsed > 5.0 and int(elapsed) % 5 == 0:
            # Select highest priority track
            highest = max(track_list, key=lambda t: t['threat_priority'])
            recorder.record_operator_selection(highest['id'])
        
        # Simulate alerts for high threats
        high_threats = [t for t in track_list if t['threat_priority'] > 0.7]
        if high_threats and int(elapsed) % 10 == 0:
            recorder.record_alert(
                'HIGH',
                f"{len(high_threats)} high-priority threats detected",
                {'threat_count': len(high_threats)}
            )
        
        time.sleep(update_interval)
    
    print(f"[DEMO] Mission simulation complete")


def demo_recording():
    """Demonstrate mission recording"""
    print("=" * 80)
    print("DEMO: MISSION RECORDING")
    print("=" * 80)
    
    # Create recorder
    recorder = MissionRecorder(output_dir="demo_missions")
    
    # Start recording
    mission_id = recorder.start_recording(
        scenario_name="Demo Scenario",
        operator_id="demo_operator",
        notes="Demonstration of mission recording system"
    )
    
    # Simulate mission
    simulate_mission(recorder, duration=20.0)
    
    # Stop recording and save
    file_path = recorder.stop_recording()
    
    return file_path


def demo_playback(file_path: str):
    """Demonstrate mission playback"""
    print("\n" + "=" * 80)
    print("DEMO: MISSION PLAYBACK")
    print("=" * 80)
    
    # Load recording
    recording = MissionRecorder.load_recording(file_path)
    
    # Create playback controller
    controller = PlaybackController(recording)
    
    # Register event callback
    def on_event(event):
        if event.event_type == EventType.TRACK_UPDATE.value:
            track_count = event.data.get('count', 0)
            print(f"  [{event.mission_time:.1f}s] {track_count} tracks")
        elif event.event_type == EventType.ALERT.value:
            print(f"  [{event.mission_time:.1f}s] ⚠️ ALERT: {event.data.get('message')}")
        elif event.event_type == EventType.OPERATOR_SELECT.value:
            print(f"  [{event.mission_time:.1f}s] Operator selected track {event.data.get('track_id')}")
    
    controller.playback.register_callback('on_event', on_event)
    
    # Play at 2x speed
    print("\n[PLAYBACK] Playing at 2x speed...")
    controller.set_speed(2.0)
    controller.play()
    
    # Update loop
    while controller.playback.state.value != 'FINISHED':
        controller.playback.update()
        time.sleep(0.05)  # 20 Hz update rate
    
    print("\n[PLAYBACK] Playback complete")
    
    # Show final status
    controller.print_status()
    
    return recording


def demo_analysis(recording):
    """Demonstrate mission analysis"""
    print("\n" + "=" * 80)
    print("DEMO: MISSION ANALYSIS")
    print("=" * 80)
    
    # Create analyzer
    analyzer = MissionAnalyzer(recording)
    
    # Print summary
    analyzer.print_summary()
    
    # Get engagement opportunities
    print("\n" + "=" * 80)
    print("ENGAGEMENT OPPORTUNITIES (threat >= 0.7)")
    print("=" * 80)
    
    opportunities = analyzer.get_engagement_opportunities(threat_threshold=0.7)
    
    for i, opp in enumerate(opportunities[:10], 1):  # Show first 10
        time_str = f"{int(opp['mission_time']//60):02d}:{int(opp['mission_time']%60):02d}"
        print(f"{i}. Time {time_str} - {opp['threat_count']} high threats")


def demo_export(file_path: str):
    """Demonstrate export functionality"""
    print("\n" + "=" * 80)
    print("DEMO: EXPORT")
    print("=" * 80)
    
    # Load recording
    recording = MissionRecorder.load_recording(file_path)
    
    # Export to JSON
    json_path = "demo_missions/demo_export.json"
    MissionRecorder.export_to_json(recording, json_path)
    print(f"✓ Exported to JSON: {json_path}")
    
    # Export tracks to CSV
    csv_path = "demo_missions/demo_tracks.csv"
    MissionRecorder.export_tracks_to_csv(recording, csv_path)
    print(f"✓ Exported tracks to CSV: {csv_path}")


def main():
    """Run complete demo"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "MISSION RECORDING SYSTEM DEMO" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # 1. Record a mission
    file_path = demo_recording()
    
    # 2. Play it back
    recording = demo_playback(file_path)
    
    # 3. Analyze it
    demo_analysis(recording)
    
    # 4. Export it
    demo_export(file_path)
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE!")
    print("=" * 80)
    print(f"\nRecording saved to: {file_path}")
    print("You can now:")
    print("  1. Load and replay this mission")
    print("  2. Analyze track patterns")
    print("  3. Export data for external tools")
    print("  4. Use for training operators")
    print("\nIntegration into bridge.py is straightforward!")
    print("=" * 80)


if __name__ == '__main__':
    main()
