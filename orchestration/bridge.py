#!/usr/bin/env python3
"""
TriAD Orchestration Bridge
Connects Engine (data source) to QML UI (visualization)
"""

import sys
from pathlib import Path
from PySide6.QtCore import (
    QObject, QAbstractListModel, QModelIndex, Qt,
    Property, Signal, Slot, QTimer
)

# Add parent directory for engine imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine.mock_engine_updated import MockEngine
from orchestration.gunner_interface import (
    GunnerInterfaceService, EffectorRecommendationEngine,
    TrackUpdate, TracksSnapshot, GunnerStatus
)


class Track(QObject):
    """Single track data model for QML"""
    
    dataChanged = Signal()
    
    def __init__(self, track_data, parent=None):
        super().__init__(parent)
        self._data = track_data
    
    def update(self, track_data):
        """Update track data"""
        self._data = track_data
        self.dataChanged.emit()
    
    @Property(int, notify=dataChanged)
    def id(self):
        return self._data.get('id', 0)
    
    @Property(str, notify=dataChanged)
    def type(self):
        return self._data.get('type', 'UNKNOWN')
    
    @Property(str, notify=dataChanged)
    def classification(self):
        return self._data.get('classification', 'UNDECLARED')
    
    @Property(str, notify=dataChanged)
    def source(self):
        return self._data.get('source', 'UNKNOWN')
    
    @Property(float, notify=dataChanged)
    def range(self):
        return self._data.get('range_m', 0.0)
    
    @Property(float, notify=dataChanged)
    def azimuth(self):
        return self._data.get('az_deg', 0.0)
    
    @Property(float, notify=dataChanged)
    def elevation(self):
        return self._data.get('el_deg', 0.0)
    
    @Property(float, notify=dataChanged)
    def speed(self):
        return self._data.get('speed_mps', 0.0)
    
    @Property(float, notify=dataChanged)
    def heading(self):
        return self._data.get('heading_deg', 0.0)
    
    @Property(float, notify=dataChanged)
    def confidence(self):
        return self._data.get('confidence', 0.0)
    
    @Property(str, notify=dataChanged)
    def status(self):
        return self._data.get('status', 'UNKNOWN')
    
    @Property(float, notify=dataChanged)
    def velocity_x(self):
        return self._data.get('velocity_x_mps', 0.0)
    
    @Property(float, notify=dataChanged)
    def velocity_y(self):
        return self._data.get('velocity_y_mps', 0.0)
    
    @Property(str, notify=dataChanged)
    def aircraft_model(self):
        return self._data.get('aircraft_model', '')
    
    @Property(float, notify=dataChanged)
    def pilot_lat(self):
        return self._data.get('pilot_lat', 0.0)
    
    @Property(float, notify=dataChanged)
    def pilot_lon(self):
        return self._data.get('pilot_lon', 0.0)
    
    @Property(int, notify=dataChanged)
    def frequency(self):
        return self._data.get('frequency', 0)
    
    @Property('QVariantList', notify=dataChanged)
    def tail(self):
        return self._data.get('tail', [])
    
    @Property(float, notify=dataChanged)
    def threat_priority(self):
        return self._data.get('threat_priority', 0.0)


class TracksModel(QAbstractListModel):
    """QML-compatible model for track list"""
    
    countChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tracks = []
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._tracks)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._tracks):
            return None
        
        track = self._tracks[index.row()]
        if role == Qt.DisplayRole or role == Qt.UserRole + 1:
            return track
        
        return None
    
    def roleNames(self):
        return {Qt.UserRole + 1: b'modelData'}
    
    @Property(int, notify=countChanged)
    def count(self):
        return len(self._tracks)
    
    def update_tracks(self, tracks_data):
        """Update tracks from engine snapshot - stable order by ID"""
        # Build dict of existing tracks by ID for preservation
        old_tracks_dict = {t.id: t for t in self._tracks}
        
        # Track if count changed
        current_count = len(self._tracks)
        
        # Update existing or create new tracks
        new_tracks = []
        for track_data in tracks_data:
            track_id = track_data['id']
            if track_id in old_tracks_dict:
                # Update existing track - Property signals will notify QML
                old_tracks_dict[track_id].update(track_data)
                new_tracks.append(old_tracks_dict[track_id])
            else:
                # New track
                new_tracks.append(Track(track_data, self))
        
        # Keep tracks in stable order by ID (no sorting here)
        # This prevents tracks from "bouncing" on the tactical display
        # The CustomTrackList will handle sorting in QML layer
        new_tracks.sort(key=lambda t: t.id)
        
        # Update the list
        self._tracks = new_tracks
        
        # Only emit model reset on count change (scenario switch)
        new_count = len(self._tracks)
        if new_count != current_count:
            self.beginResetModel()
            self.endResetModel()
            self.countChanged.emit()


class Ownship(QObject):
    """Ownship position data for QML"""
    
    dataChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._lat = 0.0
        self._lon = 0.0
        self._alt = 0.0
        self._heading = 0.0
    
    def update(self, ownship_data):
        """Update from engine"""
        self._lat = ownship_data.get('lat', 0.0)
        self._lon = ownship_data.get('lon', 0.0)
        self._alt = ownship_data.get('alt', 0.0)
        self._heading = ownship_data.get('heading', 0.0)
        self.dataChanged.emit()
    
    def set_position(self, lat, lon, alt, heading):
        """Update ownship position from GPS"""
        self._lat = lat
        self._lon = lon
        self._alt = alt
        self._heading = heading
        self.dataChanged.emit()
    
    @Property(float, notify=dataChanged)
    def lat(self):
        return self._lat
    
    @Property(float, notify=dataChanged)
    def lon(self):
        return self._lon
    
    @Property(float, notify=dataChanged)
    def alt(self):
        return self._alt
    
    @Property(float, notify=dataChanged)
    def heading(self):
        return self._heading


class SystemStatus(QObject):
    """
    System status for sensor health monitoring in QML
    
    Status values:
    - "offline": Sensor disabled or not available
    - "standby": Sensor enabled but not connected
    - "online": Sensor connected and operational
    """
    
    statusChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._gps_status = "offline"
        self._radar_status = "offline"
        self._rf_status = "offline"
        self._gunner_status = "offline"
    
    @Property(str, notify=statusChanged)
    def gpsStatus(self):
        return self._gps_status
    
    @gpsStatus.setter
    def gpsStatus(self, value):
        if self._gps_status != value:
            self._gps_status = value
            self.statusChanged.emit()
    
    @Property(str, notify=statusChanged)
    def radarStatus(self):
        return self._radar_status
    
    @radarStatus.setter
    def radarStatus(self, value):
        if self._radar_status != value:
            self._radar_status = value
            self.statusChanged.emit()
    
    @Property(str, notify=statusChanged)
    def rfStatus(self):
        return self._rf_status
    
    @rfStatus.setter
    def rfStatus(self, value):
        if self._rf_status != value:
            self._rf_status = value
            self.statusChanged.emit()
    
    @Property(str, notify=statusChanged)
    def gunnerStatus(self):
        return self._gunner_status
    
    @gunnerStatus.setter
    def gunnerStatus(self, value):
        if self._gunner_status != value:
            self._gunner_status = value
            self.statusChanged.emit()


class SystemMode(QObject):
    """System mode settings for QML"""
    
    dataChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._auto_track = True
        self._rf_silent = False
        self._optical_lock = False
    
    @Property(bool, notify=dataChanged)
    def autoTrack(self):
        return self._auto_track
    
    @autoTrack.setter
    def autoTrack(self, value):
        if self._auto_track != value:
            self._auto_track = value
            self.dataChanged.emit()
    
    @Property(bool, notify=dataChanged)
    def rfSilent(self):
        return self._rf_silent
    
    @rfSilent.setter
    def rfSilent(self, value):
        if self._rf_silent != value:
            self._rf_silent = value
            self.dataChanged.emit()
    
    @Property(bool, notify=dataChanged)
    def opticalLock(self):
        return self._optical_lock
    
    @opticalLock.setter
    def opticalLock(self, value):
        if self._optical_lock != value:
            self._optical_lock = value
            self.dataChanged.emit()


class OrchestrationBridge(QObject):
    """
    Main bridge between Engine and UI
    Responsibilities:
    - Subscribe to engine telemetry
    - Map to QML models
    - Forward UI commands to engine
    - Stream tracks to gunner stations
    """
    
    def __init__(self, engine, parent=None, enable_gunner_interface=True, gps_driver=None, radar_driver=None, rf_driver=None, 
                 gps_enabled=False, radar_enabled=False, rf_enabled=False):
        super().__init__(parent)
        self.engine = engine
        self.gps_driver = gps_driver
        self.radar_driver = radar_driver
        self.rf_driver = rf_driver
        
        # Track which sensors are enabled in config
        self.gps_enabled = gps_enabled
        self.radar_enabled = radar_enabled
        self.rf_enabled = rf_enabled
        
        # Create QML models
        self.tracks_model = TracksModel(self)
        self.ownship = Ownship(self)
        self.system_mode = SystemMode(self)
        self.system_status = SystemStatus(self)
        
        # Initialize status based on enabled state
        if self.radar_enabled:
            self.system_status.radarStatus = "standby"  # Enabled but not yet connected
        if self.gps_enabled:
            self.system_status.gpsStatus = "standby"
        if self.rf_enabled:
            self.system_status.rfStatus = "standby"
        
        # Gunner interface service
        self.gunner_interface = None
        if enable_gunner_interface:
            self.gunner_interface = GunnerInterfaceService(
                track_stream_port=5100,
                status_receive_port=5101,
                broadcast_address="192.168.10.255",
                update_rate_hz=10.0
            )
            self.gunner_interface.get_tracks_snapshot = self._build_tracks_snapshot
            self.gunner_interface.on_gunner_status_callback = self._on_gunner_status
            self.gunner_interface.start()
            print("[BRIDGE] Gunner interface enabled (waiting for engagement)")
        
        # Engagement state
        self.engaged_track_id_value = -1
        self.highest_priority_track_id_value = -1
        
        # Track history for range-rate calculation
        self.track_history = {}  # {track_id: {'prev_range': float, 'prev_time': float, 'range_rate': float}}
        
        # Track tails (position history for visualization)
        self.track_tails = {}  # {track_id: [{'az': float, 'el': float, 'range': float, 'time': float}, ...]}
        self.track_tail_duration = 15.0  # seconds
        
        # Set up update timer (simulates telemetry stream)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_from_engine)
        # 30 Hz for high-performance systems with threaded rendering
        self.update_timer.start(33)  # 30 Hz (33ms interval)
        
        # Set up status monitoring timer
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._update_system_status)
        self.status_timer.start(1000)  # 1 Hz status check
    
    def _update_from_engine(self):
        """Pull updates from engine and push to QML models"""
        # Update ownship position from GPS (if available)
        if self.gps_driver:
            gps_data = self.gps_driver.get_latest_position()
            if gps_data and gps_data.get('valid', False):
                self.ownship.set_position(
                    gps_data.get('latitude', 0.0),
                    gps_data.get('longitude', 0.0),
                    gps_data.get('altitude', 0.0),
                    gps_data.get('heading', 0.0)
                )
        
        # Update engine state (sensor fusion, track updates)
        self.engine.update()
        
        # Clean up old tracks from history (tracks not seen in last 10 seconds)
        import time
        current_time = time.time()
        stale_tracks = [tid for tid, data in self.track_history.items() 
                       if current_time - data['prev_time'] > 10.0]
        for tid in stale_tracks:
            del self.track_history[tid]
        
        # Get tracks snapshot
        snapshot = self.engine.get_tracks_snapshot()
        
        # Update track tails and clean old positions, calculate threat priority
        active_track_ids = set()
        for track in snapshot['tracks']:
            track_id = track.get('id')
            active_track_ids.add(track_id)
            
            # Add current position to tail
            if track_id not in self.track_tails:
                self.track_tails[track_id] = []
            
            # Append current position
            self.track_tails[track_id].append({
                'az': track.get('azimuth_deg', 0.0),
                'el': track.get('elevation_deg', 0.0),
                'range': track.get('range_m', 0.0),
                'time': current_time
            })
            
            # Remove positions older than tail duration
            self.track_tails[track_id] = [
                pos for pos in self.track_tails[track_id]
                if current_time - pos['time'] <= self.track_tail_duration
            ]
            
            # Add tail to track data
            track['tail'] = self.track_tails[track_id]
            
            # Calculate and add threat priority score for sorting
            track['threat_priority'] = self._calculate_threat_priority_score(track)
        
        # Remove tails for tracks that no longer exist
        stale_tail_ids = set(self.track_tails.keys()) - active_track_ids
        for tid in stale_tail_ids:
            del self.track_tails[tid]
        
        # Debug: Print track count occasionally (disabled on Windows for performance)
        # Windows console I/O is much slower than macOS and causes jitter
        import sys
        if sys.platform != 'win32':  # Only print on macOS/Linux
            if hasattr(self, '_debug_counter'):
                self._debug_counter += 1
            else:
                self._debug_counter = 0
            
            if self._debug_counter % 50 == 0:  # Every 5 seconds
                print(f"[BRIDGE] Updating UI with {len(snapshot['tracks'])} tracks")
                if len(snapshot['tracks']) > 0:
                    first_track = snapshot['tracks'][0]
                    print(f"[BRIDGE] First track: ID={first_track.get('id')}, Range={first_track.get('range_m'):.0f}m")
        
        self.tracks_model.update_tracks(snapshot['tracks'])
        
        # Get ownship
        ownship_data = self.engine.get_ownship()
        self.ownship.update(ownship_data)
    
    def _update_system_status(self):
        """Update system status from drivers using three-state logic"""
        # GPS Status: offline / standby / online
        if not self.gps_enabled:
            self.system_status.gpsStatus = "offline"
        elif self.gps_driver and hasattr(self.gps_driver, 'is_online') and self.gps_driver.is_online():
            self.system_status.gpsStatus = "online"
        elif self.gps_enabled:
            self.system_status.gpsStatus = "standby"
        
        # Radar Status: offline / idle / online
        # offline = not enabled or not connected
        # idle = connected but not streaming
        # online = connected and streaming
        if not self.radar_enabled:
            self.system_status.radarStatus = "offline"
        elif self.radar_driver and hasattr(self.radar_driver, 'is_online') and self.radar_driver.is_online():
            # Check if radar is actually streaming by querying state
            try:
                status = self.radar_driver.get_status()
                state = status.get('state', '')
                # If in SWT or SEARCH state, it's streaming (online)
                # If in STANDBY state, it's idle
                if 'SWT' in state or 'SEARCH' in state:
                    self.system_status.radarStatus = "online"
                else:
                    self.system_status.radarStatus = "idle"
            except:
                # If we can't get status, assume idle (connected but unknown state)
                self.system_status.radarStatus = "idle"
        elif self.radar_enabled:
            self.system_status.radarStatus = "standby"
        
        # RF Status: offline / standby / online
        if not self.rf_enabled:
            self.system_status.rfStatus = "offline"
        elif self.rf_driver and hasattr(self.rf_driver, 'is_online') and self.rf_driver.is_online():
            self.system_status.rfStatus = "online"
        elif self.rf_enabled:
            self.system_status.rfStatus = "standby"
        
        # Gunner Status: offline / standby / online
        if not self.gunner_interface:
            self.system_status.gunnerStatus = "offline"
        else:
            import time
            current_time = time.time()
            # Check if any gunner station has been seen in last 5 seconds
            active_gunners = [
                station_id for station_id, status in self.gunner_interface.gunner_stations.items()
                if hasattr(status, 'last_seen') and (current_time - status.last_seen) < 5.0
            ]
            if len(active_gunners) > 0:
                self.system_status.gunnerStatus = "online"
            else:
                self.system_status.gunnerStatus = "offline"  # No gunner stations connected
    
    @Slot(int, str, str, result=dict)
    def request_engage(self, track_id, operator_id, reason):
        """Forward engage request to engine"""
        print(f"[BRIDGE] Forwarding engage request: Track {track_id}")
        response = self.engine.request_engage(track_id, operator_id, reason)
        return response
    
    @Slot(bool, bool, bool, result=dict)
    def set_system_mode(self, auto_track, rf_silent, optical_lock):
        """Forward system mode change to engine"""
        print(f"[BRIDGE] Forwarding mode change: auto={auto_track}, rf={rf_silent}, optical={optical_lock}")
        response = self.engine.set_system_mode(auto_track, rf_silent, optical_lock)
        return response
    
    @Slot(result=bool)
    def connect_radar(self):
        """Connect to radar (does not start streaming)"""
        print("[BRIDGE] Radar connect requested")
        
        if not self.radar_enabled:
            print("[BRIDGE] ERROR: Radar not enabled in config")
            return False
        
        if not self.radar_driver:
            print("[BRIDGE] ERROR: No radar driver available")
            return False
        
        try:
            import time
            start_time = time.time()
            
            # Connect to radar command port
            if self.radar_driver.connect():
                connect_time = time.time() - start_time
                print(f"[BRIDGE] Connected to radar command port ({connect_time:.2f}s)")
                
                # Initialize radar
                init_start = time.time()
                if self.radar_driver.initialize_radar():
                    init_time = time.time() - init_start
                    print(f"[BRIDGE] Radar initialized - now in IDLE state ({init_time:.2f}s)")
                    
                    # Load and apply saved configuration
                    config_start = time.time()
                    saved_config = self._load_radar_config_from_file()
                    print(f"[BRIDGE] Applying saved configuration: Az {saved_config.get('search_az_min')}/{saved_config.get('search_az_max')}")
                    
                    radar_settings = {
                        'operation_mode': saved_config.get('operation_mode', 1),
                        'search_az_min': saved_config.get('search_az_min', -60),
                        'search_az_max': saved_config.get('search_az_max', 60),
                        'search_el_min': saved_config.get('search_el_min', -40),
                        'search_el_max': saved_config.get('search_el_max', 40),
                        'track_az_min': saved_config.get('track_az_min', -60),
                        'track_az_max': saved_config.get('track_az_max', 60),
                        'track_el_min': saved_config.get('track_el_min', -40),
                        'track_el_max': saved_config.get('track_el_max', 40),
                        'range_min': saved_config.get('range_min', 21),
                        'range_max': saved_config.get('range_max', 500),
                        'platform_heading': saved_config.get('heading', 30.0),
                        'platform_pitch': saved_config.get('pitch', 19.8),
                        'platform_roll': saved_config.get('roll', -0.3)
                    }
                    self.radar_driver.configure_radar(radar_settings)
                    config_time = time.time() - config_start
                    total_time = time.time() - start_time
                    print(f"[BRIDGE] [OK] Radar connected and configured (IDLE state) - Config: {config_time:.2f}s, Total: {total_time:.2f}s")
                    self._update_system_status()
                    return True
                else:
                    print("[BRIDGE] ERROR: Radar initialization failed")
                    self.radar_driver.disconnect()
                    return False
            else:
                print("[BRIDGE] ERROR: Could not connect to radar")
                return False
                
        except Exception as e:
            print(f"[BRIDGE] ERROR: Radar connection failed: {e}")
            return False
    
    @Slot(result=bool)
    def start_radar(self):
        """Start radar streaming (must be connected first)"""
        print("[BRIDGE] Radar start requested")
        
        if not self.radar_driver:
            print("[BRIDGE] ERROR: No radar driver available")
            return False
        
        if not self.radar_driver.is_online():
            print("[BRIDGE] ERROR: Radar not connected")
            return False
        
        try:
            # Configuration must be set BEFORE starting (radar doesn't accept config changes while streaming)
            saved_config = self._load_radar_config_from_file()
            print(f"[BRIDGE] Re-applying configuration before start: Az {saved_config.get('search_az_min')}/{saved_config.get('search_az_max')}")
            
            # Re-apply saved configuration (in case it was changed while in IDLE state)
            radar_settings = {
                'operation_mode': saved_config.get('operation_mode', 1),
                'search_az_min': saved_config.get('search_az_min', -60),
                'search_az_max': saved_config.get('search_az_max', 60),
                'search_el_min': saved_config.get('search_el_min', -40),
                'search_el_max': saved_config.get('search_el_max', 40),
                'track_az_min': saved_config.get('track_az_min', -60),
                'track_az_max': saved_config.get('track_az_max', 60),
                'track_el_min': saved_config.get('track_el_min', -40),
                'track_el_max': saved_config.get('track_el_max', 40),
                'range_min': saved_config.get('range_min', 21),
                'range_max': saved_config.get('range_max', 500),
                'platform_heading': saved_config.get('heading', 30.0),
                'platform_pitch': saved_config.get('pitch', 19.8),
                'platform_roll': saved_config.get('roll', -0.3)
            }
            self.radar_driver.configure_radar(radar_settings)
            
            # Now start streaming with the configured FOV
            if self.radar_driver.start_radar():
                print("[BRIDGE] [OK] Radar started and streaming (LIVE state)")
                self._update_system_status()
                return True
            else:
                print("[BRIDGE] ERROR: Failed to start radar")
                return False
                
        except Exception as e:
            print(f"[BRIDGE] ERROR: Radar start failed: {e}")
            return False
    
    @Slot(result=bool)
    def stop_radar(self):
        """Stop radar streaming (remains connected)"""
        print("[BRIDGE] Radar stop requested")
        
        if not self.radar_driver:
            print("[BRIDGE] ERROR: No radar driver available")
            return False
        
        try:
            if hasattr(self.radar_driver, 'stop_radar'):
                self.radar_driver.stop_radar()
                print("[BRIDGE] [OK] Radar stopped (IDLE state)")
                self._update_system_status()
                return True
            else:
                print("[BRIDGE] ERROR: Radar driver does not support stop")
                return False
                
        except Exception as e:
            print(f"[BRIDGE] ERROR: Radar stop failed: {e}")
            return False
    
    @Slot(result=bool)
    def disconnect_radar(self):
        """Disconnect from radar"""
        print("[BRIDGE] Radar disconnect requested")
        
        if not self.radar_driver:
            print("[BRIDGE] ERROR: No radar driver available")
            return False
        
        try:
            # Stop radar
            if hasattr(self.radar_driver, 'stop_radar'):
                self.radar_driver.stop_radar()
            
            # Disconnect
            self.radar_driver.disconnect()
            print("[BRIDGE] [OK] Radar disconnected")
            self._update_system_status()  # Update status immediately
            return True
            
        except Exception as e:
            print(f"[BRIDGE] ERROR: Radar disconnect failed: {e}")
            return False
    
    @Slot('QVariantMap', result=bool)
    def configure_radar(self, config):
        """
        Configure radar parameters
        
        Args:
            config: Dictionary with radar configuration parameters
            
        Returns:
            True if configuration successful
        """
        print("[BRIDGE] Radar configuration requested")
        
        # Always save configuration to file first
        self._save_radar_config_to_file(config)
        print("[BRIDGE] Configuration saved to file")
        
        # If radar offline, just save and return success
        if not self.radar_driver or not self.radar_driver.is_online():
            print("[BRIDGE] Radar offline - configuration saved")
            return True
        
        # Check if radar is streaming - cannot configure while streaming
        try:
            status = self.radar_driver.get_status()
            state = status.get('state', '')
            if 'SWT' in state or 'SEARCH' in state:
                print("[BRIDGE] WARNING: Cannot configure while streaming - Stop radar first")
                print("[BRIDGE] Configuration saved to file and will apply on next Start")
                return True  # Return success since config is saved
        except:
            pass  # If we can't get status, try to configure anyway
        
        try:
            # Convert QVariantMap to Python dict
            config_dict = {
                'operation_mode': 1,  # UAS mode
                'search_az_min': int(config.get('search_az_min', -60)),
                'search_az_max': int(config.get('search_az_max', 60)),
                'search_el_min': int(config.get('search_el_min', -40)),
                'search_el_max': int(config.get('search_el_max', 40)),
                'track_az_min': int(config.get('track_az_min', -60)),
                'track_az_max': int(config.get('track_az_max', 60)),
                'track_el_min': int(config.get('track_el_min', -40)),
                'track_el_max': int(config.get('track_el_max', 40)),
            }
            
            # Add platform orientation if provided
            if 'heading' in config:
                config_dict['platform_heading'] = float(config['heading'])
            if 'pitch' in config:
                config_dict['platform_pitch'] = float(config['pitch'])
            if 'roll' in config:
                config_dict['platform_roll'] = float(config['roll'])
            
            print(f"[BRIDGE] Applying configuration: {config_dict}")
            
            # Apply configuration to radar
            success = self.radar_driver.configure_radar(config_dict)
            
            if success:
                print("[BRIDGE] [OK] Radar configuration applied to online radar")
            else:
                print("[BRIDGE] WARNING: Radar configuration failed")
            
            return success
            
        except Exception as e:
            print(f"[BRIDGE] ERROR: Radar configuration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_radar_config_from_file(self):
        """Load radar configuration from file"""
        import json
        import os
        
        config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'radar_config.json')
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    print(f"[BRIDGE] Loaded configuration from {config_file}")
                    return config
        except Exception as e:
            print(f"[BRIDGE] ERROR: Failed to load config file: {e}")
        
        # Return defaults if file doesn't exist or can't be loaded
        return {
            'label': 'R1',
            'ipv4_address': '192.168.1.25',
            'product_mode': 'EchoGuard',
            'mission_set': 'cUAS',
            'latitude': -25.848810,
            'longitude': 28.997978,
            'altitude': 1.4,
            'heading': 30.0,
            'pitch': 19.8,
            'roll': -0.3,
            'range_min': 21,
            'range_max': 500,
            'search_az_min': -60,
            'search_az_max': 60,
            'search_el_min': -40,
            'search_el_max': 40,
            'track_az_min': -60,
            'track_az_max': 60,
            'track_el_min': -40,
            'track_el_max': 40,
            'freq_channel': 0
        }
    
    def _save_radar_config_to_file(self, config):
        """Save radar configuration to file"""
        import json
        import os
        
        config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        config_file = os.path.join(config_dir, 'radar_config.json')
        
        try:
            # Create config directory if it doesn't exist
            os.makedirs(config_dir, exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"[BRIDGE] Saved configuration to {config_file}")
            return True
        except Exception as e:
            print(f"[BRIDGE] ERROR: Failed to save config file: {e}")
            return False
    
    @Slot(result='QVariantMap')
    def get_radar_config(self):
        """
        Get current radar configuration
        
        Returns:
            Dictionary with current radar configuration
        """
        print("[BRIDGE] Querying radar configuration...")
        
        # Always load from file (persisted configuration)
        # This is the source of truth for configuration
        config = self._load_radar_config_from_file()
        print("[BRIDGE] Loaded configuration from file")
        
        # Update IP address if radar driver exists
        if self.radar_driver:
            config['ipv4_address'] = self.radar_driver.host
        
        return config
    
    @Slot(result='QVariantMap')
    def verify_radar_config(self):
        """
        Verify that saved configuration matches actual radar settings
        
        Returns:
            Dictionary with verification results
        """
        print("[BRIDGE] Verifying radar configuration...")
        
        result = {
            'synced': False,
            'differences': [],
            'radar_values': {},
            'saved_values': {}
        }
        
        # Can only verify if radar is online
        if not self.radar_driver or not self.radar_driver.is_online():
            print("[BRIDGE] Cannot verify - radar offline")
            result['error'] = "Radar offline"
            return result
        
        try:
            # Get saved configuration
            saved_config = self._load_radar_config_from_file()
            
            # Query actual radar configuration
            radar_config = self.radar_driver.get_configuration()
            
            if not radar_config:
                print("[BRIDGE] WARNING: Cannot verify while streaming - radar doesn't allow FOV queries")
                print("[BRIDGE] Configuration is saved and was applied before streaming started")
                result['error'] = "Cannot verify while streaming"
                result['synced'] = True  # Assume synced since we applied config before start
                print(f"[BRIDGE] Returning result: synced={result['synced']}, error={result.get('error')}")
                return result
            
            # Compare FOV settings
            fov_params = ['search_az_min', 'search_az_max', 'search_el_min', 'search_el_max',
                         'track_az_min', 'track_az_max', 'track_el_min', 'track_el_max']
            
            differences = []
            for param in fov_params:
                if param in radar_config and param in saved_config:
                    radar_val = radar_config[param]
                    saved_val = saved_config[param]
                    result['radar_values'][param] = radar_val
                    result['saved_values'][param] = saved_val
                    
                    if radar_val != saved_val:
                        differences.append({
                            'parameter': param,
                            'saved': saved_val,
                            'radar': radar_val
                        })
            
            result['differences'] = differences
            result['synced'] = len(differences) == 0
            
            if result['synced']:
                print("[BRIDGE] [OK] Configuration synced with radar")
            else:
                print(f"[BRIDGE] WARNING: Configuration out of sync: {len(differences)} differences")
                for diff in differences:
                    print(f"  - {diff['parameter']}: saved={diff['saved']}, radar={diff['radar']}")
            
            return result
            
        except Exception as e:
            print(f"[BRIDGE] ERROR: Verification failed: {e}")
            result['error'] = str(e)
            return result
    
    def _build_tracks_snapshot(self) -> TracksSnapshot:
        """Build tracks snapshot for gunner interface"""
        import time
        
        # Get current tracks from engine
        engine_snapshot = self.engine.get_tracks_snapshot()
        ownship_data = self.engine.get_ownship()
        
        # Convert to gunner interface format
        track_updates = []
        for track_data in engine_snapshot['tracks']:
            # Get effector recommendation
            recommendation = EffectorRecommendationEngine.get_recommendation(
                track_data.get('range_m', 0.0)
            )
            
            track_update = TrackUpdate(
                track_id=track_data['id'],
                azimuth_deg=track_data.get('azimuth_deg', 0.0),
                elevation_deg=track_data.get('elevation_deg', 0.0),
                range_m=track_data.get('range_m', 0.0),
                velocity_x_mps=track_data.get('velocity_x_mps', 0.0),
                velocity_y_mps=track_data.get('velocity_y_mps', 0.0),
                velocity_z_mps=track_data.get('velocity_z_mps', 0.0),
                speed_mps=(track_data.get('velocity_x_mps', 0.0)**2 + 
                          track_data.get('velocity_y_mps', 0.0)**2 + 
                          track_data.get('velocity_z_mps', 0.0)**2)**0.5,
                heading_deg=track_data.get('heading_deg', 0.0),
                type=track_data.get('type', 'UNKNOWN'),
                confidence=track_data.get('confidence', 0.0),
                source=track_data.get('source', 'UNKNOWN'),
                track_age_sec=track_data.get('lifetime_sec', 0.0),
                num_updates=track_data.get('num_associated_meas', 0),
                priority=self._calculate_priority(track_data),
                recommended_effector=recommendation.effector,
                recommendation_reason=recommendation.reason,
                aircraft_model=track_data.get('aircraft_model'),
                pilot_latitude=track_data.get('pilot_latitude'),
                pilot_longitude=track_data.get('pilot_longitude'),
                timestamp_ns=time.time_ns()
            )
            track_updates.append(track_update)
        
        snapshot = TracksSnapshot(
            tracks=track_updates,
            radar_online=(self.system_status.radarStatus == "online"),
            rf_online=(self.system_status.rfStatus == "online"),
            total_tracks=len(track_updates),
            ownship_lat=ownship_data.get('lat', 0.0),
            ownship_lon=ownship_data.get('lon', 0.0),
            ownship_heading=ownship_data.get('heading', 0.0),
            timestamp_ns=time.time_ns()
        )
        
        return snapshot
    
    def _calculate_priority(self, track_data):
        """Calculate track priority (CRITICAL, HIGH, MEDIUM, LOW)"""
        range_m = track_data.get('range_m', 9999)
        confidence = track_data.get('confidence', 0.0)
        track_type = track_data.get('type', 'UNKNOWN')
        source = track_data.get('source', 'UNKNOWN')
        
        # Range score (closer = higher)
        range_score = 1.0 - min(1.0, range_m / 3000.0)
        
        # Confidence score
        confidence_score = confidence
        
        # Type bonus
        type_bonus = 0.2 if track_type == "UAV" else 0.0
        
        # Fused bonus
        fused_bonus = 0.1 if source == "FUSED" else 0.0
        
        # Calculate total priority score
        priority_score = (range_score + confidence_score + type_bonus + fused_bonus) / 2.2
        
        if priority_score > 0.8:
            return "CRITICAL"
        elif priority_score > 0.6:
            return "HIGH"
        elif priority_score > 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_threat_priority_score(self, track_data) -> float:
        """
        HYBRID THREAT PRIORITIZATION ALGORITHM
        
        Uses tiered approach:
        1. Immediate threat detection (flags for operator attention)
        2. Filter non-threats
        3. Physics-based weighted scoring
        4. Context multipliers
        
        Returns: Score 0.0-1.0 (higher = more dangerous)
        """
        import math
        
        # Extract track data
        range_m = track_data.get('range_m', 9999)
        confidence = track_data.get('confidence', 0.0)
        track_type = track_data.get('type', 'UNKNOWN')
        source = track_data.get('source', 'UNKNOWN')
        classification = track_data.get('classification', None)  # Multiclass classifier result
        
        # Velocity components (3D)
        velocity_x = track_data.get('velocity_x_mps', 0.0)
        velocity_y = track_data.get('velocity_y_mps', 0.0)
        velocity_z = track_data.get('velocity_z_mps', 0.0)
        
        # Additional factors
        elevation_deg = track_data.get('elevation_deg', 15.0)
        track_age = track_data.get('lifetime_sec', 0.0)
        azimuth_deg = track_data.get('azimuth_deg', 0.0)
        
        # ═══════════════════════════════════════════════════════
        # TIER 1: IMMEDIATE THREAT DETECTION
        # ═══════════════════════════════════════════════════════
        is_immediate = self._is_immediate_threat(range_m, track_type, confidence)
        
        # ═══════════════════════════════════════════════════════
        # TIER 2: FILTER NON-THREATS (Only UAV classes and PLANE)
        # ═══════════════════════════════════════════════════════
        if self._should_ignore_track(track_type, confidence, range_m, classification):
            return 0.0
        
        # ═══════════════════════════════════════════════════════
        # TIER 3: HYBRID GRID + TAU (TCAS-Inspired)
        # ═══════════════════════════════════════════════════════
        
        # HYBRID APPROACH: Threat zones + Tau calculation
        # Combines clear operator zones with proven TCAS tau logic
        
        import time
        current_time = time.time()
        track_id = track_data.get('id')
        
        # 1. CALCULATE RANGE RATE from actual measurements (unchanged)
        if track_id in self.track_history:
            prev_data = self.track_history[track_id]
            prev_range = prev_data['prev_range']
            prev_time = prev_data['prev_time']
            
            delta_time = current_time - prev_time
            
            if delta_time > 0.05:  # At least 50ms elapsed
                delta_range = range_m - prev_range
                range_rate = delta_range / delta_time  # m/s
                
                # Smooth range rate with exponential moving average
                prev_rate = prev_data.get('range_rate', range_rate)
                alpha = 0.5  # Smoothing factor - responsive to speed changes (50/50 mix)
                range_rate = alpha * range_rate + (1 - alpha) * prev_rate
                
                self.track_history[track_id] = {
                    'prev_range': range_m,
                    'prev_time': current_time,
                    'range_rate': range_rate,
                    'prev_score': prev_data.get('prev_score', None)
                }
            else:
                range_rate = prev_data.get('range_rate', 0.0)
        else:
            # First time seeing this track - use range as primary
            self.track_history[track_id] = {
                'prev_range': range_m,
                'prev_time': current_time,
                'range_rate': 0.0
            }
            range_rate = 0.0
        
        # 2. DETERMINE THREAT ZONE (Grid-based)
        if range_m < 150:
            threat_zone = "CRITICAL"
            zone_base_score = 1.0
        elif range_m < 400:
            threat_zone = "HIGH"
            zone_base_score = 0.75
        elif range_m < 800:
            threat_zone = "MEDIUM"
            zone_base_score = 0.50
        elif range_m < 1500:
            threat_zone = "LOW"
            zone_base_score = 0.25
        else:
            threat_zone = "DISTANT"
            zone_base_score = 0.10
        
        # 3. CALCULATE TAU (Time to Closest Approach - TCAS Method)
        if range_rate < -0.5:  # Approaching (with small threshold for noise)
            closing_speed = abs(range_rate)
            tau = range_m / closing_speed  # Time to collision (seconds)
            is_approaching = True
            
            # Tau-based threat modifier (TCAS-inspired thresholds) - MORE AGGRESSIVE
            if tau < 15:
                tau_modifier = 1.0    # Resolution Advisory level - CRITICAL
            elif tau < 25:
                tau_modifier = 0.95   # High urgency (was 0.90)
            elif tau < 35:
                tau_modifier = 0.85   # Traffic Advisory level (was 0.75)
            elif tau < 60:
                tau_modifier = 0.65   # Medium urgency (was 0.50)
            elif tau < 120:
                tau_modifier = 0.40   # Low urgency (was 0.25)
            else:
                tau_modifier = 0.15   # Distant future (was 0.10)
                
        elif range_rate > 0.5:  # Receding
            tau = float('inf')
            closing_speed = 0.0
            is_approaching = False
            tau_modifier = 0.02  # Very low threat (was 0.05) - receding is not a threat
        else:  # Hovering/stationary
            tau = float('inf')
            closing_speed = 0.0
            is_approaching = False
            tau_modifier = 0.50  # Higher threat if hovering close (was 0.30)
        
        # 4. EXPONENTIAL RANGE PROXIMITY (Continuous distance emphasis)
        # MUCH STEEPER CURVE - close tracks dominate
        range_proximity = math.exp(-range_m / 300.0)  # e^(-r/300) - AGGRESSIVE proximity emphasis
        # At 0m: 1.0, At 150m: 0.61, At 300m: 0.37, At 600m: 0.14, At 900m: 0.05
        
        # Debug: print(f"[TAU] T{track_id}: Zone={threat_zone}, R={range_m:.0f}m, Rate={range_rate:.1f}m/s, "
        #       f"Tau={tau:.1f}s, ZoneScore={zone_base_score:.2f}, TauMod={tau_modifier:.2f}, Prox={range_proximity:.2f}")
        
        # 5. TRACK CONFIDENCE & STABILITY
        confidence_factor = confidence
        
        # Track age bonus (older tracks are more reliable)
        if track_age > 10.0:
            stability_bonus = 0.15
        elif track_age > 5.0:
            stability_bonus = 0.08
        else:
            stability_bonus = 0.0
        
        # 7. TYPE FACTOR
        type_factors = {
            'UAV': 1.0,
            'UNKNOWN': 0.5,
            'BIRD': 0.0,  # Birds filtered out anyway
            'CLUTTER': 0.0
        }
        type_factor = type_factors.get(track_type, 0.3)
        
        # 8. SOURCE QUALITY FACTOR
        source_factors = {
            'FUSED': 1.0,
            'RADAR': 0.8,
            'RF': 0.6
        }
        source_factor = source_factors.get(source, 0.5)
        
        # ═══════════════════════════════════════════════════════
        # WEIGHTED COMBINATION (Hybrid Grid + Tau + Proximity)
        # ═══════════════════════════════════════════════════════
        # Priority: Zone framework + Tau urgency + Distance emphasis + Confidence
        
        # STEP 1: Calculate base threat from zone and tau
        base_threat = zone_base_score * tau_modifier
        
        # STEP 2: Weight with proximity, confidence and other factors
        # REBALANCED: More weight on approaching speed (tau) and proximity
        base_score = (
            base_threat * 0.45 +            # Zone × Tau (approaching speed) - INCREASED from 0.30
            range_proximity * 0.40 +        # Direct distance emphasis - REDUCED from 0.50
            confidence_factor * 0.10 +      # Confidence gating - REDUCED from 0.12
            type_factor * 0.04 +            # Classification bonus - REDUCED from 0.06
            source_factor * 0.01            # Sensor quality - REDUCED from 0.02
        )
        
        # STEP 3: Add stability bonus
        base_score = min(1.0, base_score + stability_bonus)
        
        # STEP 4: First-update handling (no range rate yet)
        if range_rate == 0.0 and range_m < 300:
            # First update - use zone score only for close tracks
            base_score = max(base_score, zone_base_score * 0.6)
        
        tier = threat_zone
        
        # Debug: print(f"      [{tier}] Score={base_score:.3f}, Tau={tau:.1f}s, BaseThreat={base_threat:.2f}, Prox={range_proximity:.2f}")
        
        # ═══════════════════════════════════════════════════════
        # TIER 4: CONTEXT MULTIPLIERS
        # ═══════════════════════════════════════════════════════
        multiplier = 1.0
        
        # Immediate threat multiplier (flagged for urgent operator attention)
        if is_immediate:
            multiplier *= 1.5
        
        # FUSED track with RF intelligence multiplier
        if source == 'FUSED' and track_data.get('aircraft_model'):
            multiplier *= 1.2  # Higher confidence with model ID
        
        # RF pilot location proximity (if available)
        if track_data.get('pilot_latitude'):
            multiplier *= 1.15  # RF intelligence bonus
        
        # High closing speed threat
        if closing_speed > 30.0:  # Fast approach
            multiplier *= 1.1
        
        # Apply multiplier and clamp to [0, 1]
        final_score = min(1.0, base_score * multiplier)
        
        # ═══════════════════════════════════════════════════════
        # TEMPORAL SMOOTHING: Reduce jitter in threat scores
        # ═══════════════════════════════════════════════════════
        if track_id in self.track_history:
            prev_score = self.track_history[track_id].get('prev_score')
            if prev_score is not None:
                # Apply exponential moving average (40% new, 60% previous)
                # This prevents rapid score changes while staying responsive
                smoothing_alpha = 0.40
                final_score = smoothing_alpha * final_score + (1 - smoothing_alpha) * prev_score
            
            # Update stored score for next iteration
            self.track_history[track_id]['prev_score'] = final_score
        
        return final_score
    
    def _is_immediate_threat(self, range_m: float, track_type: str, confidence: float) -> bool:
        """
        Detect immediate threats requiring urgent operator attention.
        Does NOT trigger auto-engage (operator approval required).
        """
        # Very close UAV with high confidence
        if range_m < 200 and track_type == 'UAV' and confidence > 0.8:
            return True
        
        # Close unknown with very high confidence
        if range_m < 150 and track_type == 'UNKNOWN' and confidence > 0.9:
            return True
        
        return False
    
    def _should_ignore_track(self, track_type: str, confidence: float, range_m: float, classification: str = None) -> bool:
        """
        Filter out tracks that should not be prioritized.
        Only consider: UAV, UAV_MULTI_ROTOR, UAV_FIXED_WING, PLANE
        All other classifications are ignored.
        """
        # Use classification if available (multiclass classifier)
        if classification:
            allowed_classes = ['UAV', 'UAV_MULTI_ROTOR', 'UAV_FIXED_WING', 'PLANE']
            if classification not in allowed_classes:
                return True  # Ignore: WALKER, BIRD, VEHICLE, CLUTTER, UNDECLARED, etc.
        else:
            # Fallback to old type field
            if track_type == 'BIRD':
                return True
            if track_type == 'CLUTTER':
                return True
            if track_type == 'WALKER':
                return True
            if track_type == 'VEHICLE':
                return True
        
        # Ignore low confidence detections
        if confidence < 0.3:
            return True
        
        # Ignore very distant unknowns with low confidence
        if range_m > 2500 and track_type == 'UNKNOWN' and confidence < 0.6:
            return True
        
        return False
    
    @Slot(result=int)
    def get_highest_priority_track_id(self) -> int:
        """
        Get ID of highest priority track using hybrid algorithm.
        Filters are applied automatically (birds, low confidence, etc.)
        
        Uses hysteresis to prevent rapid switching between similar threats:
        - Current highest priority track gets 10% bonus
        - New track must be clearly better to replace current one
        """
        engine_snapshot = self.engine.get_tracks_snapshot()
        if not engine_snapshot['tracks']:
            return -1
        
        # Calculate priority for ALL tracks (algorithm handles filtering)
        best_track = None
        best_score = 0.0
        current_highest_id = self.highest_priority_track_id_value
        
        # Hysteresis factor: current highest priority gets a bonus to prevent thrashing
        HYSTERESIS_BONUS = 0.03  # 3% bonus to current highest priority - reactive with stability
        
        for track in engine_snapshot['tracks']:
            score = self._calculate_threat_priority_score(track)
            
            # Apply hysteresis: give current highest priority a bonus
            # This prevents rapid switching when scores are close
            if track['id'] == current_highest_id and score > 0.0:
                score *= (1.0 + HYSTERESIS_BONUS)
            
            if score > best_score:
                best_score = score
                best_track = track
        
        if best_track and best_score > 0.0:
            self.highest_priority_track_id_value = best_track['id']
            return best_track['id']
        
        return -1
    
    @Slot(int, str, result='QVariant')
    def engage_track(self, track_id: int, operator_id: str):
        """
        C2 operator engages a specific track
        Begin streaming ONLY this track to gunners
        """
        print(f"\n[BRIDGE] *** ENGAGE CALLED *** track_id={track_id}, operator={operator_id}")
        
        if not self.gunner_interface:
            print("[BRIDGE] ERROR: No gunner interface available")
            return {'success': False, 'message': 'Gunner interface not available'}
        
        # Validate track exists
        engine_snapshot = self.engine.get_tracks_snapshot()
        track = next((t for t in engine_snapshot['tracks'] if t['id'] == track_id), None)
        
        if not track:
            return {'success': False, 'message': f'Track {track_id} not found'}
        
        # Engage track
        self.gunner_interface.engage_track(track_id, operator_id)
        self.engaged_track_id_value = track_id
        
        print(f"[BRIDGE] [OK] ENGAGEMENT: Track {track_id} by {operator_id}")
        print(f"[BRIDGE]   Type: {track.get('type')}, Range: {track.get('range_m', 0):.0f}m")
        print(f"[BRIDGE]   Streaming to gunner stations...")
        
        return {
            'success': True,
            'message': f'Track {track_id} engaged'
        }
    
    @Slot(result='QVariant')
    def disengage_track(self):
        """
        C2 operator cancels current engagement
        Stop streaming to gunners
        """
        print(f"\n[BRIDGE] *** DISENGAGE CALLED *** currently engaged={self.engaged_track_id_value}")
        
        if not self.gunner_interface:
            print("[BRIDGE] ERROR: No gunner interface available")
            return {'success': False, 'message': 'Gunner interface not available'}
        
        if self.engaged_track_id_value != -1:
            self.gunner_interface.disengage_track()
            print(f"[BRIDGE] ✗ DISENGAGEMENT: Track {self.engaged_track_id_value}")
            self.engaged_track_id_value = -1
            
            return {'success': True, 'message': 'Engagement cancelled'}
        
        return {'success': False, 'message': 'No track currently engaged'}
    
    @Slot(result=int)
    def get_engaged_track_id(self) -> int:
        """Get currently engaged track ID"""
        return self.engaged_track_id_value
    
    @Slot(result=bool)
    def is_track_engaged(self) -> bool:
        """Check if a track is currently engaged"""
        return self.engaged_track_id_value != -1
    
    def _on_gunner_status(self, status: GunnerStatus):
        """Handle gunner status updates"""
        print(f"[BRIDGE] Gunner status: {status.station_id} - "
              f"Track {status.cued_track_id}, "
              f"Weapon: {status.selected_weapon}, "
              f"Visual: {status.visual_lock}")
        
        # TODO: Update UI to show gunner status
        # TODO: Log gunner actions
        # TODO: Coordinate multi-gunner assignments
