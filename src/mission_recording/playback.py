"""
Mission Playback Engine
Replays recorded missions with variable speed control
"""
import time
from typing import Optional, Callable, List
from enum import Enum

from .recorder import MissionRecording, MissionEvent, EventType


class PlaybackState(Enum):
    """Playback states"""
    STOPPED = "STOPPED"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"


class MissionPlayback:
    """
    Mission playback engine with speed control
    """
    
    def __init__(self, recording: MissionRecording):
        self.recording = recording
        self.state = PlaybackState.STOPPED
        
        # Playback control
        self.current_index = 0
        self.current_mission_time = 0.0
        self.playback_speed = 1.0  # 1.0 = real-time, 2.0 = 2x speed, 0.5 = half speed
        
        # Timing
        self.playback_start_time: Optional[float] = None
        self.pause_time: Optional[float] = None
        self.time_offset = 0.0  # For seek operations
        
        # Event callbacks
        self.callbacks = {
            'on_event': [],
            'on_state_change': [],
            'on_finish': []
        }
        
    def register_callback(self, callback_type: str, callback: Callable):
        """
        Register a callback function
        
        Args:
            callback_type: Type of callback ('on_event', 'on_state_change', 'on_finish')
            callback: Function to call
        """
        if callback_type not in self.callbacks:
            raise ValueError(f"Unknown callback type: {callback_type}")
        self.callbacks[callback_type].append(callback)
    
    def start(self, from_time: float = 0.0):
        """
        Start playback from a specific time
        
        Args:
            from_time: Mission time to start from (seconds)
        """
        if self.state == PlaybackState.PLAYING:
            return
        
        # Find starting index
        self.seek(from_time)
        
        self.state = PlaybackState.PLAYING
        self.playback_start_time = time.time()
        self.pause_time = None
        
        self._notify_state_change()
        print(f"[PLAYBACK] Started from {from_time:.1f}s at {self.playback_speed}x speed")
    
    def pause(self):
        """Pause playback"""
        if self.state != PlaybackState.PLAYING:
            return
        
        self.state = PlaybackState.PAUSED
        self.pause_time = time.time()
        
        self._notify_state_change()
        print(f"[PLAYBACK] Paused at {self.current_mission_time:.1f}s")
    
    def resume(self):
        """Resume playback"""
        if self.state != PlaybackState.PAUSED:
            return
        
        # Adjust timing to account for pause
        if self.pause_time and self.playback_start_time:
            pause_duration = time.time() - self.pause_time
            self.playback_start_time += pause_duration
        
        self.state = PlaybackState.PLAYING
        self.pause_time = None
        
        self._notify_state_change()
        print(f"[PLAYBACK] Resumed at {self.current_mission_time:.1f}s")
    
    def stop(self):
        """Stop playback"""
        self.state = PlaybackState.STOPPED
        self.current_index = 0
        self.current_mission_time = 0.0
        self.playback_start_time = None
        self.pause_time = None
        self.time_offset = 0.0
        
        self._notify_state_change()
        print("[PLAYBACK] Stopped")
    
    def seek(self, mission_time: float):
        """
        Seek to a specific mission time
        
        Args:
            mission_time: Time in seconds to seek to
        """
        # Find the event at or just before this time
        target_index = 0
        for i, event in enumerate(self.recording.events):
            if event.mission_time > mission_time:
                break
            target_index = i
        
        self.current_index = target_index
        self.current_mission_time = mission_time
        self.time_offset = mission_time
        
        # Reset timing if playing
        if self.state == PlaybackState.PLAYING:
            self.playback_start_time = time.time()
        
        print(f"[PLAYBACK] Seeked to {mission_time:.1f}s (event {target_index})")
    
    def set_speed(self, speed: float):
        """
        Set playback speed
        
        Args:
            speed: Playback speed multiplier (1.0 = real-time, 2.0 = 2x, etc.)
        """
        if speed <= 0:
            raise ValueError("Speed must be positive")
        
        # Adjust timing if currently playing
        if self.state == PlaybackState.PLAYING and self.playback_start_time:
            # Calculate current mission time
            elapsed = time.time() - self.playback_start_time
            self.current_mission_time = self.time_offset + (elapsed * self.playback_speed)
            
            # Reset start time and offset for new speed
            self.time_offset = self.current_mission_time
            self.playback_start_time = time.time()
        
        self.playback_speed = speed
        print(f"[PLAYBACK] Speed set to {speed}x")
    
    def update(self) -> List[MissionEvent]:
        """
        Update playback state and return new events
        Call this regularly (e.g., in a timer)
        
        Returns:
            List of events that occurred since last update
        """
        if self.state != PlaybackState.PLAYING:
            return []
        
        if self.playback_start_time is None:
            return []
        
        # Calculate current mission time
        elapsed_real_time = time.time() - self.playback_start_time
        target_mission_time = self.time_offset + (elapsed_real_time * self.playback_speed)
        
        # Find events between current time and target time
        new_events = []
        
        while self.current_index < len(self.recording.events):
            event = self.recording.events[self.current_index]
            
            if event.mission_time > target_mission_time:
                break
            
            new_events.append(event)
            self.current_index += 1
            self.current_mission_time = event.mission_time
            
            # Notify callbacks
            self._notify_event(event)
        
        # Check if finished
        if self.current_index >= len(self.recording.events):
            self._finish()
        
        return new_events
    
    def get_progress(self) -> float:
        """
        Get playback progress
        
        Returns:
            Progress as fraction 0.0 - 1.0
        """
        duration = self.recording.get_duration()
        if duration == 0:
            return 1.0
        return self.current_mission_time / duration
    
    def get_remaining_time(self) -> float:
        """
        Get remaining playback time in seconds (at current speed)
        
        Returns:
            Remaining time in seconds
        """
        duration = self.recording.get_duration()
        remaining_mission_time = duration - self.current_mission_time
        return remaining_mission_time / self.playback_speed
    
    def get_current_tracks(self) -> List[dict]:
        """
        Get current active tracks at playback position
        
        Returns:
            List of track dictionaries
        """
        # Find the most recent TRACK_UPDATE event
        for i in range(self.current_index - 1, -1, -1):
            event = self.recording.events[i]
            if event.event_type == EventType.TRACK_UPDATE.value:
                return event.data.get('tracks', [])
        return []
    
    def _finish(self):
        """Handle playback finish"""
        self.state = PlaybackState.FINISHED
        self._notify_state_change()
        
        # Call finish callbacks
        for callback in self.callbacks['on_finish']:
            callback()
        
        print("[PLAYBACK] Finished")
    
    def _notify_event(self, event: MissionEvent):
        """Notify event callbacks"""
        for callback in self.callbacks['on_event']:
            callback(event)
    
    def _notify_state_change(self):
        """Notify state change callbacks"""
        for callback in self.callbacks['on_state_change']:
            callback(self.state)


class PlaybackController:
    """
    High-level playback controller with common controls
    """
    
    def __init__(self, recording: MissionRecording):
        self.playback = MissionPlayback(recording)
        self.recording = recording
        
    def play(self):
        """Play from current position"""
        if self.playback.state == PlaybackState.PAUSED:
            self.playback.resume()
        else:
            self.playback.start(self.playback.current_mission_time)
    
    def pause(self):
        """Pause playback"""
        self.playback.pause()
    
    def stop(self):
        """Stop and reset"""
        self.playback.stop()
    
    def restart(self):
        """Restart from beginning"""
        self.playback.stop()
        self.playback.start(0.0)
    
    def skip_forward(self, seconds: float = 10.0):
        """Skip forward by N seconds"""
        new_time = min(
            self.playback.current_mission_time + seconds,
            self.recording.get_duration()
        )
        self.playback.seek(new_time)
    
    def skip_backward(self, seconds: float = 10.0):
        """Skip backward by N seconds"""
        new_time = max(0.0, self.playback.current_mission_time - seconds)
        self.playback.seek(new_time)
    
    def set_speed(self, speed: float):
        """Set playback speed (0.25x, 0.5x, 1x, 2x, 4x, etc.)"""
        self.playback.set_speed(speed)
    
    def speed_up(self):
        """Double the speed"""
        self.playback.set_speed(self.playback.playback_speed * 2.0)
    
    def slow_down(self):
        """Halve the speed"""
        self.playback.set_speed(self.playback.playback_speed / 2.0)
    
    def seek_percent(self, percent: float):
        """
        Seek to a percentage of the mission
        
        Args:
            percent: Percentage (0-100)
        """
        duration = self.recording.get_duration()
        target_time = (percent / 100.0) * duration
        self.playback.seek(target_time)
    
    def get_status(self) -> dict:
        """
        Get current playback status
        
        Returns:
            Status dictionary
        """
        return {
            'state': self.playback.state.value,
            'mission_time': self.playback.current_mission_time,
            'duration': self.recording.get_duration(),
            'progress_percent': self.playback.get_progress() * 100,
            'speed': self.playback.playback_speed,
            'remaining_seconds': self.playback.get_remaining_time(),
            'event_count': len(self.recording.events),
            'current_event_index': self.playback.current_index
        }
    
    def print_status(self):
        """Print current status"""
        status = self.get_status()
        duration_str = self._format_time(status['duration'])
        current_str = self._format_time(status['mission_time'])
        
        print(f"\n[PLAYBACK STATUS]")
        print(f"  State: {status['state']}")
        print(f"  Time: {current_str} / {duration_str}")
        print(f"  Progress: {status['progress_percent']:.1f}%")
        print(f"  Speed: {status['speed']}x")
        print(f"  Events: {status['current_event_index']} / {status['event_count']}")
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
