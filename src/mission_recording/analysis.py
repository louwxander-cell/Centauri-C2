"""
Mission Analysis Tools
Statistical analysis and reporting for recorded missions
"""
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
import statistics

from .recorder import MissionRecording, EventType


class MissionAnalyzer:
    """
    Analyze recorded missions for patterns, statistics, and insights
    """
    
    def __init__(self, recording: MissionRecording):
        self.recording = recording
        
    def generate_summary(self) -> Dict:
        """
        Generate comprehensive mission summary
        
        Returns:
            Dictionary with mission statistics
        """
        summary = {
            'mission_id': self.recording.metadata.mission_id,
            'duration_seconds': self.recording.get_duration(),
            'total_events': len(self.recording.events),
            'total_unique_tracks': self.recording.metadata.total_tracks,
            'max_concurrent_tracks': self.recording.metadata.max_tracks_concurrent,
            'track_statistics': self._analyze_tracks(),
            'event_statistics': self._analyze_events(),
            'threat_statistics': self._analyze_threats(),
            'operator_actions': self._analyze_operator_actions()
        }
        
        return summary
    
    def _analyze_tracks(self) -> Dict:
        """Analyze track data"""
        track_updates = self.recording.get_events_by_type(EventType.TRACK_UPDATE)
        
        if not track_updates:
            return {'error': 'No track data'}
        
        # Extract all tracks
        all_tracks = []
        for event in track_updates:
            tracks = event.data.get('tracks', [])
            all_tracks.extend(tracks)
        
        if not all_tracks:
            return {'error': 'No track data'}
        
        # Count by type
        types = [t.get('type') for t in all_tracks if t.get('type')]
        type_counts = Counter(types)
        
        # Range statistics
        ranges = [t.get('range_m') for t in all_tracks if t.get('range_m') is not None]
        range_stats = {
            'min': min(ranges) if ranges else 0,
            'max': max(ranges) if ranges else 0,
            'mean': statistics.mean(ranges) if ranges else 0,
            'median': statistics.median(ranges) if ranges else 0
        }
        
        # Confidence statistics
        confidences = [t.get('confidence') for t in all_tracks if t.get('confidence') is not None]
        confidence_stats = {
            'min': min(confidences) if confidences else 0,
            'max': max(confidences) if confidences else 0,
            'mean': statistics.mean(confidences) if confidences else 0
        }
        
        return {
            'total_observations': len(all_tracks),
            'type_distribution': dict(type_counts),
            'range_statistics_m': range_stats,
            'confidence_statistics': confidence_stats
        }
    
    def _analyze_events(self) -> Dict:
        """Analyze event distribution"""
        event_types = [e.event_type for e in self.recording.events]
        event_counts = Counter(event_types)
        
        return {
            'total_events': len(self.recording.events),
            'event_type_distribution': dict(event_counts),
            'events_per_second': len(self.recording.events) / max(self.recording.get_duration(), 1)
        }
    
    def _analyze_threats(self) -> Dict:
        """Analyze threat patterns"""
        track_updates = self.recording.get_events_by_type(EventType.TRACK_UPDATE)
        
        # Track threat levels over time
        threat_timeline = []
        critical_count = 0
        high_count = 0
        
        for event in track_updates:
            tracks = event.data.get('tracks', [])
            
            # Count by threat level (based on threat_priority score)
            critical = sum(1 for t in tracks if t.get('threat_priority', 0) > 0.8)
            high = sum(1 for t in tracks if 0.5 < t.get('threat_priority', 0) <= 0.8)
            
            threat_timeline.append({
                'time': event.mission_time,
                'critical': critical,
                'high': high,
                'total': len(tracks)
            })
            
            critical_count = max(critical_count, critical)
            high_count = max(high_count, high)
        
        return {
            'max_critical_threats': critical_count,
            'max_high_threats': high_count,
            'threat_timeline': threat_timeline
        }
    
    def _analyze_operator_actions(self) -> Dict:
        """Analyze operator behavior"""
        selections = self.recording.get_events_by_type(EventType.OPERATOR_SELECT)
        actions = self.recording.get_events_by_type(EventType.OPERATOR_ACTION)
        
        # Selection statistics
        selected_tracks = [e.data.get('track_id') for e in selections]
        selection_counts = Counter(selected_tracks)
        
        return {
            'total_selections': len(selections),
            'total_actions': len(actions),
            'unique_tracks_selected': len(set(selected_tracks)),
            'most_selected_track': selection_counts.most_common(1)[0] if selection_counts else None
        }
    
    def get_track_timeline(self, track_id: int) -> List[Dict]:
        """
        Get complete timeline for a specific track
        
        Args:
            track_id: Track ID to analyze
            
        Returns:
            List of track observations over time
        """
        track_updates = self.recording.get_events_by_type(EventType.TRACK_UPDATE)
        
        timeline = []
        for event in track_updates:
            tracks = event.data.get('tracks', [])
            for track in tracks:
                if track.get('id') == track_id:
                    timeline.append({
                        'mission_time': event.mission_time,
                        'track_data': track
                    })
                    break
        
        return timeline
    
    def get_engagement_opportunities(self, threat_threshold: float = 0.7) -> List[Dict]:
        """
        Identify engagement opportunities (high-threat periods)
        
        Args:
            threat_threshold: Minimum threat priority to count
            
        Returns:
            List of engagement opportunities
        """
        track_updates = self.recording.get_events_by_type(EventType.TRACK_UPDATE)
        
        opportunities = []
        
        for event in track_updates:
            tracks = event.data.get('tracks', [])
            high_threats = [
                t for t in tracks 
                if t.get('threat_priority', 0) >= threat_threshold
            ]
            
            if high_threats:
                opportunities.append({
                    'mission_time': event.mission_time,
                    'threat_count': len(high_threats),
                    'tracks': high_threats
                })
        
        return opportunities
    
    def print_summary(self):
        """Print formatted mission summary"""
        summary = self.generate_summary()
        
        print("=" * 80)
        print(f"MISSION ANALYSIS: {summary['mission_id']}")
        print("=" * 80)
        print()
        
        # Basic stats
        duration_str = self._format_time(summary['duration_seconds'])
        print(f"Duration: {duration_str}")
        print(f"Total Events: {summary['total_events']}")
        print(f"Unique Tracks: {summary['total_unique_tracks']}")
        print(f"Max Concurrent Tracks: {summary['max_concurrent_tracks']}")
        print()
        
        # Track statistics
        print("-" * 80)
        print("TRACK STATISTICS")
        print("-" * 80)
        track_stats = summary['track_statistics']
        print(f"Total Observations: {track_stats.get('total_observations', 0)}")
        
        if 'type_distribution' in track_stats:
            print("\nType Distribution:")
            for track_type, count in track_stats['type_distribution'].items():
                print(f"  {track_type}: {count}")
        
        if 'range_statistics_m' in track_stats:
            range_stats = track_stats['range_statistics_m']
            print(f"\nRange Statistics (m):")
            print(f"  Min: {range_stats['min']:.1f}")
            print(f"  Max: {range_stats['max']:.1f}")
            print(f"  Mean: {range_stats['mean']:.1f}")
            print(f"  Median: {range_stats['median']:.1f}")
        
        print()
        
        # Threat statistics
        print("-" * 80)
        print("THREAT ANALYSIS")
        print("-" * 80)
        threat_stats = summary['threat_statistics']
        print(f"Max Critical Threats: {threat_stats.get('max_critical_threats', 0)}")
        print(f"Max High Threats: {threat_stats.get('max_high_threats', 0)}")
        print()
        
        # Operator actions
        print("-" * 80)
        print("OPERATOR ACTIONS")
        print("-" * 80)
        op_stats = summary['operator_actions']
        print(f"Total Selections: {op_stats.get('total_selections', 0)}")
        print(f"Total Actions: {op_stats.get('total_actions', 0)}")
        print(f"Unique Tracks Selected: {op_stats.get('unique_tracks_selected', 0)}")
        print()
        
        print("=" * 80)
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
