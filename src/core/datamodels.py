"""Core data models for TriAD C2 system using Pydantic"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
import time


class TargetType(str, Enum):
    """Classification of detected targets"""
    UAV = "UAV"
    BIRD = "BIRD"
    UNKNOWN = "UNKNOWN"
    AIRCRAFT = "AIRCRAFT"
    CLUTTER = "CLUTTER"


class SensorSource(str, Enum):
    """Source sensor for detection"""
    RADAR = "RADAR"
    RF = "RF"
    FUSED = "FUSED"
    GPS = "GPS"


class Track(BaseModel):
    """Represents a tracked target in the system"""
    id: int = Field(..., description="Unique track identifier")
    azimuth: float = Field(..., ge=0.0, lt=360.0, description="Azimuth in degrees (0-360)")
    elevation: float = Field(..., ge=-90.0, le=90.0, description="Elevation in degrees")
    range_m: float = Field(..., gt=0.0, description="Range in meters")
    type: TargetType = Field(default=TargetType.UNKNOWN, description="Target classification")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Classification confidence")
    source: SensorSource = Field(..., description="Originating sensor")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp")
    velocity_mps: Optional[float] = Field(default=None, description="Velocity in m/s")
    heading: Optional[float] = Field(default=None, ge=0.0, lt=360.0, description="Target heading")
    
    # RF-specific fields (BlueHalo SkyView)
    pilot_latitude: Optional[float] = Field(default=None, description="Pilot position latitude")
    pilot_longitude: Optional[float] = Field(default=None, description="Pilot position longitude")
    aircraft_model: Optional[str] = Field(default=None, description="Aircraft model (e.g., 'Mavic Pro')")
    serial_number: Optional[str] = Field(default=None, description="Drone serial number")
    rf_frequency: Optional[int] = Field(default=None, description="RF frequency in Hz")
    rf_power: Optional[float] = Field(default=None, description="RF signal power")
    
    # Radar-specific fields (Echoguard)
    rcs: Optional[float] = Field(default=None, description="Radar cross-section in m²")
    probability_uav: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="UAV probability")
    
    model_config = ConfigDict(use_enum_values=True)
        
    def age(self) -> float:
        """Returns age of track in seconds"""
        return time.time() - self.timestamp
    
    def is_stale(self, timeout_sec: float = 5.0) -> bool:
        """Check if track has timed out"""
        return self.age() > timeout_sec


class GeoPosition(BaseModel):
    """Geographic position of ownship/vehicle"""
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude in degrees")
    lon: float = Field(..., ge=-180.0, le=180.0, description="Longitude in degrees")
    heading: float = Field(..., ge=0.0, lt=360.0, description="True heading in degrees")
    altitude_m: Optional[float] = Field(default=None, description="Altitude in meters MSL")
    speed_mps: Optional[float] = Field(default=None, ge=0.0, description="Ground speed in m/s")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp")
    
    model_config = ConfigDict(use_enum_values=True)


class SlewCommand(BaseModel):
    """Command to slew RWS to target"""
    azimuth: float = Field(..., ge=0.0, lt=360.0, description="Target azimuth")
    elevation: float = Field(..., ge=-90.0, le=90.0, description="Target elevation")
    track_id: Optional[int] = Field(default=None, description="Associated track ID")
    timestamp: float = Field(default_factory=time.time, description="Command timestamp")


class SystemStatus(BaseModel):
    """Overall system health status"""
    radar_online: bool = Field(default=False)
    rf_online: bool = Field(default=False)
    gps_online: bool = Field(default=False)
    rws_online: bool = Field(default=False)
    active_tracks: int = Field(default=0)
    last_update: float = Field(default_factory=time.time)
