#!/usr/bin/env python3
"""
TriAD C2 QML Interface - Simplified Version
"""

import sys
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
        """Create sample tracks"""
        statuses = ["CRITICAL", "HIGH", "MED", "FRIENDLY"]
        types = ["UAV", "UAV", "BIRD", "UAV"]
        
        for i in range(4):
            track = Track(i + 101, self)
            track._type = types[i]
            track._status = statuses[i]
            track._range = 800 + i * 400
            track._azimuth = 45 + i * 90
            track._confidence = 0.65 + i * 0.08
            track._velocity = 8 + i * 3
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
        return {Qt.UserRole + 1: b'modelData'}
    
    @Property(int, constant=True)
    def count(self):
        return len(self._tracks)
    
    @Slot()
    def update_tracks(self):
        """Simulate track updates"""
        for track in self._tracks:
            track.azimuth = track.azimuth + random.uniform(-0.5, 0.5)
            if track.azimuth < 0:
                track.azimuth += 360
            if track.azimuth >= 360:
                track.azimuth -= 360
            
            track.range = max(500, track.range + random.uniform(-10, 10))
        
        self.dataChanged.emit(self.index(0), self.index(len(self._tracks) - 1), [Qt.DisplayRole])


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


def main():
    """Main application entry point"""
    
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("TriAD")
    app.setApplicationName("TriAD C2 QML")
    
    engine = QQmlApplicationEngine()
    
    # Create data models
    tracks_model = TracksModel()
    ownship = Ownship()
    system_mode = SystemMode()
    
    # Expose models to QML
    engine.rootContext().setContextProperty("tracksModel", tracks_model)
    engine.rootContext().setContextProperty("ownship", ownship)
    engine.rootContext().setContextProperty("systemMode", system_mode)
    engine.rootContext().setContextProperty("rwsState", None)
    
    # Load simplified QML
    qml_file = Path(__file__).parent / "qml" / "MainViewSimple.qml"
    print(f"Loading QML from: {qml_file}")
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    if not engine.rootObjects():
        print("ERROR: Failed to load QML file")
        return -1
    
    # Set up update timer
    update_timer = QTimer()
    update_timer.timeout.connect(tracks_model.update_tracks)
    update_timer.start(100)
    
    print("=" * 70)
    print("  TriAD C2 QML Interface - SIMPLIFIED VERSION")
    print("=" * 70)
    print("  Window should now be visible!")
    print("  - 4 sample tracks")
    print("  - Rotating radar indicator")
    print("  - Click tracks to select")
    print("  - Engage button activates when track selected")
    print("=" * 70)
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
