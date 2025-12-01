"""
Mission Recording System
Records all tracks, system events, and operator actions for playback and analysis
"""
import json
import gzip
import time
import pickle
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class EventType(Enum):
    """Types of mission events"""
    MISSION_START = "MISSION_START"
    MISSION_END = "MISSION_END"
    TRACK_UPDATE = "TRACK_UPDATE"
    TRACK_NEW = "TRACK_NEW"
    TRACK_LOST = "TRACK_LOST"
    OPERATOR_SELECT = "OPERATOR_SELECT"
    OPERATOR_ACTION = "OPERATOR_ACTION"
    SYSTEM_STATE = "SYSTEM_STATE"
    SCENARIO_LOAD = "SCENARIO_LOAD"
    SENSOR_STATUS = "SENSOR_STATUS"
    ALERT = "ALERT"


@dataclass
class MissionEvent:
    """Single event in mission timeline"""
    timestamp: float  # Unix timestamp
    mission_time: float  # Seconds since mission start
    event_type: EventType
    data: Dict[str, Any]
    
    def __post_init__(self):
        # Convert EventType to string for JSON serialization
        if isinstance(self.event_type, EventType):
            self.event_type = self.event_type.value


@dataclass
class MissionMetadata:
    """Mission recording metadata"""
    mission_id: str
    start_time: float  # Unix timestamp
    end_time: Optional[float] = None
    duration_seconds: Optional[float] = None
    
    # System info
    version: str = "1.0"
    system_name: str = "TriAD C2"
    
    # Mission info
    scenario_name: Optional[str] = None
    operator_id: Optional[str] = None
    notes: str = ""
    
    # Statistics
    total_events: int = 0
    total_tracks: int = 0
    max_tracks_concurrent: int = 0
    
    # File info
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    compressed: bool = True


@dataclass
class MissionRecording:
    """Complete mission recording"""
    metadata: MissionMetadata
    events: List[MissionEvent] = field(default_factory=list)
    
    def get_duration(self) -> float:
        """Get mission duration in seconds"""
        if self.metadata.end_time and self.metadata.start_time:
            return self.metadata.end_time - self.metadata.start_time
        return 0.0
    
    def get_event_count(self) -> int:
        """Get total number of events"""
        return len(self.events)
    
    def get_events_by_type(self, event_type: EventType) -> List[MissionEvent]:
        """Get all events of a specific type"""
        type_str = event_type.value if isinstance(event_type, EventType) else event_type
        return [e for e in self.events if e.event_type == type_str]
    
    def get_events_in_timerange(self, start_time: float, end_time: float) -> List[MissionEvent]:
        """Get events within a time range (mission time)"""
        return [e for e in self.events if start_time <= e.mission_time <= end_time]


class MissionRecorder:
    """
    Real-time mission recorder
    Records all tracks, events, and operator actions
    """
    
    def __init__(self, output_dir: str = "missions"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        self.recording: Optional[MissionRecording] = None
        self.is_recording: bool = False
        self.start_time: Optional[float] = None
        
        # Track statistics
        self.active_tracks: Dict[int, Dict] = {}
        self.max_concurrent_tracks: int = 0
        self.unique_track_ids: set = set()
        
    def start_recording(self, mission_id: Optional[str] = None, 
                       scenario_name: Optional[str] = None,
                       operator_id: Optional[str] = None,
                       notes: str = "") -> str:
        """
        Start a new mission recording
        
        Returns:
            mission_id string
        """
        if self.is_recording:
            raise RuntimeError("Already recording a mission. Stop current recording first.")
        
        # Generate mission ID if not provided
        if mission_id is None:
            mission_id = f"mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.start_time = time.time()
        
        # Create metadata
        metadata = MissionMetadata(
            mission_id=mission_id,
            start_time=self.start_time,
            scenario_name=scenario_name,
            operator_id=operator_id,
            notes=notes
        )
        
        # Create recording
        self.recording = MissionRecording(metadata=metadata)
        self.is_recording = True
        
        # Reset statistics
        self.active_tracks.clear()
        self.max_concurrent_tracks = 0
        self.unique_track_ids.clear()
        
        # Log mission start event
        self.record_event(
            EventType.MISSION_START,
            {
                'mission_id': mission_id,
                'scenario': scenario_name,
                'timestamp': self.start_time
            }
        )
        
        print(f"[RECORDER] Started recording mission: {mission_id}")
        return mission_id
    
    def stop_recording(self) -> Optional[str]:
        """
        Stop recording and save to file
        
        Returns:
            File path of saved recording
        """
        if not self.is_recording or self.recording is None:
            print("[RECORDER] No active recording to stop")
            return None
        
        end_time = time.time()
        
        # Update metadata
        self.recording.metadata.end_time = end_time
        self.recording.metadata.duration_seconds = end_time - self.start_time
        self.recording.metadata.total_events = len(self.recording.events)
        self.recording.metadata.total_tracks = len(self.unique_track_ids)
        self.recording.metadata.max_tracks_concurrent = self.max_concurrent_tracks
        
        # Record mission end event
        self.record_event(
            EventType.MISSION_END,
            {
                'duration_seconds': self.recording.metadata.duration_seconds,
                'total_events': self.recording.metadata.total_events,
                'total_tracks': self.recording.metadata.total_tracks
            }
        )
        
        # Save to file
        file_path = self._save_recording()
        
        print(f"[RECORDER] Stopped recording: {self.recording.metadata.mission_id}")
        print(f"[RECORDER] Duration: {self.recording.metadata.duration_seconds:.1f}s")
        print(f"[RECORDER] Events: {self.recording.metadata.total_events}")
        print(f"[RECORDER] Saved to: {file_path}")
        
        self.is_recording = False
        self.recording = None
        self.start_time = None
        
        return file_path
    
    def record_event(self, event_type: EventType, data: Dict[str, Any]):
        """
        Record a mission event
        
        Args:
            event_type: Type of event
            data: Event data dictionary
        """
        if not self.is_recording or self.recording is None:
            return
        
        current_time = time.time()
        mission_time = current_time - self.start_time
        
        event = MissionEvent(
            timestamp=current_time,
            mission_time=mission_time,
            event_type=event_type,
            data=data
        )
        
        self.recording.events.append(event)
    
    def record_tracks(self, tracks: List[Dict[str, Any]]):
        """
        Record current track snapshot
        
        Args:
            tracks: List of track dictionaries
        """
        if not self.is_recording:
            return
        
        # Update statistics
        current_track_ids = set()
        
        for track in tracks:
            track_id = track.get('id')
            if track_id is None:
                continue
            
            current_track_ids.add(track_id)
            self.unique_track_ids.add(track_id)
            
            # Check if new track
            if track_id not in self.active_tracks:
                self.record_event(
                    EventType.TRACK_NEW,
                    {
                        'track_id': track_id,
                        'type': track.get('type'),
                        'range_m': track.get('range_m'),
                        'confidence': track.get('confidence')
                    }
                )
            
            # Update active tracks
            self.active_tracks[track_id] = track
        
        # Detect lost tracks
        lost_tracks = set(self.active_tracks.keys()) - current_track_ids
        for track_id in lost_tracks:
            self.record_event(
                EventType.TRACK_LOST,
                {'track_id': track_id}
            )
            del self.active_tracks[track_id]
        
        # Update max concurrent
        self.max_concurrent_tracks = max(self.max_concurrent_tracks, len(current_track_ids))
        
        # Record track update snapshot
        self.record_event(
            EventType.TRACK_UPDATE,
            {
                'tracks': tracks,
                'count': len(tracks)
            }
        )
    
    def record_operator_selection(self, track_id: int):
        """Record operator track selection"""
        self.record_event(
            EventType.OPERATOR_SELECT,
            {'track_id': track_id}
        )
    
    def record_operator_action(self, action: str, data: Dict[str, Any]):
        """Record general operator action"""
        self.record_event(
            EventType.OPERATOR_ACTION,
            {'action': action, **data}
        )
    
    def record_system_state(self, state_data: Dict[str, Any]):
        """Record system state snapshot"""
        self.record_event(
            EventType.SYSTEM_STATE,
            state_data
        )
    
    def record_sensor_status(self, sensor_name: str, status: str, data: Dict[str, Any]):
        """Record sensor status change"""
        self.record_event(
            EventType.SENSOR_STATUS,
            {
                'sensor': sensor_name,
                'status': status,
                **data
            }
        )
    
    def record_alert(self, severity: str, message: str, data: Dict[str, Any]):
        """Record system alert"""
        self.record_event(
            EventType.ALERT,
            {
                'severity': severity,
                'message': message,
                **data
            }
        )
    
    def _save_recording(self) -> str:
        """
        Save recording to file
        
        Returns:
            File path
        """
        if self.recording is None:
            raise RuntimeError("No recording to save")
        
        mission_id = self.recording.metadata.mission_id
        
        # Save as compressed pickle (binary)
        file_path = self.output_dir / f"{mission_id}.mrec.gz"
        
        with gzip.open(file_path, 'wb') as f:
            pickle.dump(self.recording, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        # Update metadata
        self.recording.metadata.file_path = str(file_path)
        self.recording.metadata.file_size_bytes = file_path.stat().st_size
        
        return str(file_path)
    
    @staticmethod
    def load_recording(file_path: str) -> MissionRecording:
        """
        Load a mission recording from file
        
        Args:
            file_path: Path to .mrec.gz file
            
        Returns:
            MissionRecording object
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Recording file not found: {file_path}")
        
        with gzip.open(file_path, 'rb') as f:
            recording = pickle.load(f)
        
        print(f"[RECORDER] Loaded recording: {recording.metadata.mission_id}")
        print(f"[RECORDER] Duration: {recording.get_duration():.1f}s")
        print(f"[RECORDER] Events: {len(recording.events)}")
        
        return recording
    
    @staticmethod
    def export_to_json(recording: MissionRecording, output_path: str):
        """
        Export recording to JSON format
        
        Args:
            recording: MissionRecording to export
            output_path: Output JSON file path
        """
        output_path = Path(output_path)
        
        # Convert to dict (handle dataclasses)
        def convert_to_dict(obj):
            if hasattr(obj, '__dict__'):
                return {k: convert_to_dict(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [convert_to_dict(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: convert_to_dict(v) for k, v in obj.items()}
            elif isinstance(obj, Enum):
                return obj.value
            else:
                return obj
        
        data = {
            'metadata': asdict(recording.metadata),
            'events': [asdict(e) for e in recording.events]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"[RECORDER] Exported to JSON: {output_path}")
    
    @staticmethod
    def export_tracks_to_csv(recording: MissionRecording, output_path: str):
        """
        Export track data to CSV for analysis
        
        Args:
            recording: MissionRecording to export
            output_path: Output CSV file path
        """
        import csv
        
        output_path = Path(output_path)
        
        # Extract all track update events
        track_events = recording.get_events_by_type(EventType.TRACK_UPDATE)
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'mission_time', 'timestamp', 'track_id', 'type', 'range_m',
                'azimuth_deg', 'elevation_deg', 'velocity_x_mps', 'velocity_y_mps',
                'velocity_z_mps', 'confidence', 'threat_priority'
            ])
            
            # Data rows
            for event in track_events:
                tracks = event.data.get('tracks', [])
                for track in tracks:
                    writer.writerow([
                        event.mission_time,
                        event.timestamp,
                        track.get('id'),
                        track.get('type'),
                        track.get('range_m'),
                        track.get('azimuth_deg'),
                        track.get('elevation_deg'),
                        track.get('velocity_x_mps'),
                        track.get('velocity_y_mps'),
                        track.get('velocity_z_mps'),
                        track.get('confidence'),
                        track.get('threat_priority')
                    ])
        
        print(f"[RECORDER] Exported tracks to CSV: {output_path}")
