"""Unit tests for track fusion logic"""

import pytest
import time
from src.core.fusion import TrackFusion
from src.core.datamodels import Track, SensorSource, TargetType


class TestTrackFusion:
    """Test suite for track fusion"""
    
    def test_single_track_passthrough(self):
        """Test that single track passes through unchanged"""
        fusion = TrackFusion()
        
        track = Track(
            id=1,
            azimuth=45.0,
            elevation=10.0,
            range_m=500.0,
            type=TargetType.DRONE,
            confidence=0.8,
            source=SensorSource.RADAR
        )
        
        result = fusion.update_track(track)
        assert result.id == 1
        assert result.source == SensorSource.RADAR
    
    def test_track_correlation(self):
        """Test that close tracks from different sensors are fused"""
        fusion = TrackFusion(distance_threshold_m=100.0)
        
        # Radar track
        radar_track = Track(
            id=1,
            azimuth=45.0,
            elevation=10.0,
            range_m=500.0,
            type=TargetType.UNKNOWN,
            confidence=0.7,
            source=SensorSource.RADAR
        )
        
        # RF track at similar position
        rf_track = Track(
            id=100,
            azimuth=46.0,  # Close azimuth
            elevation=11.0,
            range_m=510.0,  # Close range
            type=TargetType.DRONE,
            confidence=0.9,
            source=SensorSource.RF
        )
        
        # First track
        result1 = fusion.update_track(radar_track)
        
        # Second track should fuse
        result2 = fusion.update_track(rf_track)
        
        # Should be fused
        assert result2.source == SensorSource.FUSED
        assert result2.confidence > 0.7  # Boosted confidence
        assert result2.type == TargetType.DRONE  # Higher confidence classification
    
    def test_no_correlation_different_positions(self):
        """Test that distant tracks are not fused"""
        fusion = TrackFusion(distance_threshold_m=50.0)
        
        # Radar track
        radar_track = Track(
            id=1,
            azimuth=0.0,
            elevation=10.0,
            range_m=500.0,
            type=TargetType.DRONE,
            confidence=0.8,
            source=SensorSource.RADAR
        )
        
        # RF track at very different position
        rf_track = Track(
            id=100,
            azimuth=180.0,  # Opposite direction
            elevation=10.0,
            range_m=500.0,
            type=TargetType.DRONE,
            confidence=0.9,
            source=SensorSource.RF
        )
        
        fusion.update_track(radar_track)
        result = fusion.update_track(rf_track)
        
        # Should NOT be fused
        assert result.source == SensorSource.RF
        assert len(fusion.tracks) == 2
    
    def test_stale_track_removal(self):
        """Test that old tracks are removed"""
        fusion = TrackFusion(timeout_sec=0.5)
        
        track = Track(
            id=1,
            azimuth=45.0,
            elevation=10.0,
            range_m=500.0,
            type=TargetType.DRONE,
            confidence=0.8,
            source=SensorSource.RADAR,
            timestamp=time.time() - 1.0  # 1 second old
        )
        
        fusion.update_track(track)
        
        # Should be removed as stale
        active_tracks = fusion.get_active_tracks()
        assert len(active_tracks) == 0
    
    def test_weighted_average_fusion(self):
        """Test that fusion uses weighted average"""
        fusion = TrackFusion(distance_threshold_m=100.0)
        
        # Low confidence radar track
        radar_track = Track(
            id=1,
            azimuth=40.0,
            elevation=10.0,
            range_m=500.0,
            type=TargetType.UNKNOWN,
            confidence=0.5,
            source=SensorSource.RADAR
        )
        
        # High confidence RF track
        rf_track = Track(
            id=100,
            azimuth=50.0,
            elevation=10.0,
            range_m=500.0,
            type=TargetType.DRONE,
            confidence=0.9,
            source=SensorSource.RF
        )
        
        fusion.update_track(radar_track)
        result = fusion.update_track(rf_track)
        
        # Fused azimuth should be closer to RF (higher confidence)
        assert result.source == SensorSource.FUSED
        assert 45.0 < result.azimuth < 50.0  # Weighted toward RF
    
    def test_clear_tracks(self):
        """Test clearing all tracks"""
        fusion = TrackFusion()
        
        track = Track(
            id=1,
            azimuth=45.0,
            elevation=10.0,
            range_m=500.0,
            type=TargetType.DRONE,
            confidence=0.8,
            source=SensorSource.RADAR
        )
        
        fusion.update_track(track)
        assert len(fusion.tracks) == 1
        
        fusion.clear()
        assert len(fusion.tracks) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
