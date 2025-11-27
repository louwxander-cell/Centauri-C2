#!/usr/bin/env python3
"""
TriAD C2 QML Interface - Python Backend
Connects Qt Quick (QML) frontend to Python sensor fusion backend
"""

import sys
import os
import math
import random
from pathlib import Path

from PySide6.QtCore import (
    QObject, QAbstractListModel, QModelIndex, Qt, 
    Property, Signal, Slot, QTimer, QUrl
)
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QGuiApplication


class Track(QObject):
    """Single track data model"""
    
    dataChanged = Signal()
    
    def __init__(self, track_id, parent=None):
        super().__init__(parent)
        self._id = track_id
        self._type = "UAV"
        self._source = "RADAR"
        self._range = 1500.0
        self._azimuth = 45.0
        self._elevation = 10.0
        self._confidence = 0.85
        self._status = "MED"
        self._velocity = 12.5
        self._heading = 90.0
    
    @Property(int, notify=dataChanged)
    def id(self):
        return self._id
    
    @Property(str, notify=dataChanged)
    def type(self):
        return self._type
    
    @Property(str, notify=dataChanged)
    def source(self):
        return self._source
    
    @Property(float, notify=dataChanged)
    def range(self):
        return self._range
    
    @range.setter
    def range(self, value):
        if self._range != value:
            self._range = value
            self.dataChanged.emit()
    
    @Property(float, notify=dataChanged)
    def azimuth(self):
        return self._azimuth
    
    @azimuth.setter
    def azimuth(self, value):
        if self._azimuth != value:
            self._azimuth = value
            self.dataChanged.emit()
    
    @Property(float, notify=dataChanged)
    def elevation(self):
        return self._elevation
    
    @Property(float, notify=dataChanged)
    def confidence(self):
        return self._confidence
    
    @Property(str, notify=dataChanged)
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        if self._status != value:
            self._status = value
            self.dataChanged.emit()
    
    @Property(float, notify=dataChanged)
    def velocity(self):
        return self._velocity
    
    @Property(float, notify=dataChanged)
    def heading(self):
        return self._heading


class TracksModel(QAbstractListModel):
    """List model for active tracks"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tracks = []
        self._create_sample_tracks()
    
    def _create_sample_tracks(self):
        """Create sample tracks for demonstration"""
        statuses = ["CRITICAL", "HIGH", "MED", "FRIENDLY"]
        types = ["UAV", "UAV", "BIRD", "UAV"]
        sources = ["RADAR", "RF", "RADAR", "RADAR"]
        
        for i in range(4):
            track = Track(i + 101, self)
            track._type = types[i]
            track._source = sources[i]
            track._status = statuses[i]
            track._range = 800 + i * 400
            track._azimuth = 45 + i * 90
            track._confidence = 0.65 + i * 0.08
            track._velocity = 8 + i * 3
            track._heading = 30 + i * 80
            self._tracks.append(track)
    
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
        return {
            Qt.UserRole + 1: b'modelData'
        }
    
    @Slot()
    def update_tracks(self):
        """Simulate track updates"""
        for track in self._tracks:
            # Animate positions slightly
            track.azimuth = track.azimuth + random.uniform(-0.5, 0.5)
            if track.azimuth < 0:
                track.azimuth += 360
            if track.azimuth >= 360:
                track.azimuth -= 360
            
            track.range = max(500, track.range + random.uniform(-10, 10))
        
        # Emit data changed
        self.dataChanged.emit(
            self.index(0), 
            self.index(len(self._tracks) - 1),
            [Qt.DisplayRole]
        )


class Ownship(QObject):
    """Ownship position data"""
    
    dataChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._lat = -25.841105
        self._lon = 28.180340
        self._heading = 90.0
    
    @Property(float, notify=dataChanged)
    def lat(self):
        return self._lat
    
    @Property(float, notify=dataChanged)
    def lon(self):
        return self._lon
    
    @Property(float, notify=dataChanged)
    def heading(self):
        return self._heading


class SystemMode(QObject):
    """System mode settings"""
    
    dataChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._auto_track = True
        self._rf_silent = False
        self._optical_lock = False
    
    @Property(bool, notify=dataChanged)
    def autoTrack(self):
        return self._auto_track
    
    @Property(bool, notify=dataChanged)
    def rfSilent(self):
        return self._rf_silent
    
    @Property(bool, notify=dataChanged)
    def opticalLock(self):
        return self._optical_lock


class RWSState(QObject):
    """Remote Weapon Station state"""
    
    dataChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._azimuth = 0.0
        self._elevation = 0.0
    
    @Property(float, notify=dataChanged)
    def azimuth(self):
        return self._azimuth
    
    @Property(float, notify=dataChanged)
    def elevation(self):
        return self._elevation


def main():
    """Main application entry point"""
    
    # Set up application
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("TriAD")
    app.setApplicationName("TriAD C2 QML")
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Create data models
    tracks_model = TracksModel()
    ownship = Ownship()
    system_mode = SystemMode()
    rws_state = RWSState()
    
    # Expose models to QML
    engine.rootContext().setContextProperty("tracksModel", tracks_model)
    engine.rootContext().setContextProperty("ownship", ownship)
    engine.rootContext().setContextProperty("systemMode", system_mode)
    engine.rootContext().setContextProperty("rwsState", rws_state)
    
    # Set import path
    qml_dir = Path(__file__).parent / "qml"
    engine.addImportPath(str(qml_dir))
    
    # Load main QML file
    qml_file = qml_dir / "MainView.qml"
    print(f"[DEBUG] Loading QML from: {qml_file}", flush=True)
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    print("[DEBUG] QML loaded, checking root objects...", flush=True)
    if not engine.rootObjects():
        print("Error: Failed to load QML file")
        return -1
    
    print("[DEBUG] Got root objects", flush=True)
    # Window visibility is already set in QML with visible: true
    # No need to manually show/raise - QML handles it
    print("[DEBUG] Window created and visible", flush=True)
    
    # Set up update timer (simulate sensor data updates)
    update_timer = QTimer()
    update_timer.timeout.connect(tracks_model.update_tracks)
    update_timer.start(100)  # Update every 100ms
    
    print("=" * 70, flush=True)
    print("  TriAD C2 QML Interface - Running", flush=True)
    print("=" * 70, flush=True)
    print("  - Track updates: 10 Hz", flush=True)
    print("  - GPU-accelerated rendering", flush=True)
    print("  - Press ESC to deselect tracks", flush=True)
    print("  - Long-press Engage button for armed sequence", flush=True)
    print("=" * 70, flush=True)
    print("[DEBUG] Starting event loop...", flush=True)
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
