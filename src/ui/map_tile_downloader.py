"""
Offline Map Tile Downloader
Downloads OpenStreetMap tiles for offline use
"""

import os
import math
import requests
from pathlib import Path
from typing import Tuple
import time


class MapTileDownloader:
    """
    Download and cache map tiles for offline use.
    
    Uses OpenStreetMap tiles (free, open source).
    Downloads tiles at multiple zoom levels for a given area.
    """
    
    # OpenStreetMap tile server
    TILE_SERVER = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    
    # User agent (required by OSM)
    USER_AGENT = "TriAD-C2-System/1.0"
    
    def __init__(self, cache_dir: str = "map_cache"):
        """
        Initialize tile downloader.
        
        Args:
            cache_dir: Directory to store cached tiles
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Request headers
        self.headers = {
            'User-Agent': self.USER_AGENT
        }
    
    @staticmethod
    def lat_lon_to_tile(lat: float, lon: float, zoom: int) -> Tuple[int, int]:
        """
        Convert lat/lon to tile coordinates at given zoom level.
        
        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            zoom: Zoom level (0-19)
        
        Returns:
            (tile_x, tile_y)
        """
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        
        tile_x = int((lon + 180.0) / 360.0 * n)
        tile_y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        
        return (tile_x, tile_y)
    
    @staticmethod
    def tile_to_lat_lon(tile_x: int, tile_y: int, zoom: int) -> Tuple[float, float]:
        """
        Convert tile coordinates to lat/lon (top-left corner).
        
        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
            zoom: Zoom level
        
        Returns:
            (lat, lon)
        """
        n = 2.0 ** zoom
        
        lon = tile_x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_y / n)))
        lat = math.degrees(lat_rad)
        
        return (lat, lon)
    
    @staticmethod
    def calculate_tile_bounds(center_lat: float, center_lon: float, 
                            radius_km: float, zoom: int) -> Tuple[int, int, int, int]:
        """
        Calculate tile bounds for a circular area.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Radius in kilometers
            zoom: Zoom level
        
        Returns:
            (min_x, max_x, min_y, max_y)
        """
        # Convert radius to degrees (approximate)
        # 1 degree latitude ≈ 111 km
        # 1 degree longitude ≈ 111 km * cos(latitude)
        lat_offset = radius_km / 111.0
        lon_offset = radius_km / (111.0 * math.cos(math.radians(center_lat)))
        
        # Calculate corner coordinates
        north = center_lat + lat_offset
        south = center_lat - lat_offset
        east = center_lon + lon_offset
        west = center_lon - lon_offset
        
        # Convert to tile coordinates
        nw_x, nw_y = MapTileDownloader.lat_lon_to_tile(north, west, zoom)
        se_x, se_y = MapTileDownloader.lat_lon_to_tile(south, east, zoom)
        
        return (
            min(nw_x, se_x),
            max(nw_x, se_x),
            min(nw_y, se_y),
            max(nw_y, se_y)
        )
    
    def get_tile_path(self, zoom: int, tile_x: int, tile_y: int) -> Path:
        """Get local path for a tile"""
        return self.cache_dir / str(zoom) / str(tile_x) / f"{tile_y}.png"
    
    def tile_exists(self, zoom: int, tile_x: int, tile_y: int) -> bool:
        """Check if tile is already cached"""
        return self.get_tile_path(zoom, tile_x, tile_y).exists()
    
    def download_tile(self, zoom: int, tile_x: int, tile_y: int, 
                     force: bool = False) -> bool:
        """
        Download a single tile.
        
        Args:
            zoom: Zoom level
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
            force: Force re-download even if cached
        
        Returns:
            True if successful, False otherwise
        """
        tile_path = self.get_tile_path(zoom, tile_x, tile_y)
        
        # Skip if already cached
        if not force and tile_path.exists():
            return True
        
        # Create directory
        tile_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download tile
        url = self.TILE_SERVER.format(z=zoom, x=tile_x, y=tile_y)
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Save tile
            with open(tile_path, 'wb') as f:
                f.write(response.content)
            
            return True
            
        except Exception as e:
            print(f"[MapDownloader] Error downloading tile {zoom}/{tile_x}/{tile_y}: {e}")
            return False
    
    def download_area(self, center_lat: float, center_lon: float, 
                     radius_km: float, zoom_levels: list = None,
                     delay_ms: int = 100):
        """
        Download tiles for an area.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Radius in kilometers
            zoom_levels: List of zoom levels to download (default: [10, 11, 12, 13, 14])
            delay_ms: Delay between requests in milliseconds (be nice to OSM servers)
        """
        if zoom_levels is None:
            zoom_levels = [10, 11, 12, 13, 14]  # Good range for tactical view
        
        print(f"\n[MapDownloader] Downloading map tiles for area:")
        print(f"  Center: {center_lat:.6f}, {center_lon:.6f}")
        print(f"  Radius: {radius_km} km")
        print(f"  Zoom levels: {zoom_levels}")
        
        total_tiles = 0
        downloaded_tiles = 0
        skipped_tiles = 0
        
        for zoom in zoom_levels:
            min_x, max_x, min_y, max_y = self.calculate_tile_bounds(
                center_lat, center_lon, radius_km, zoom
            )
            
            tiles_at_zoom = (max_x - min_x + 1) * (max_y - min_y + 1)
            total_tiles += tiles_at_zoom
            
            print(f"\n  Zoom {zoom}: {tiles_at_zoom} tiles ({min_x}-{max_x}, {min_y}-{max_y})")
            
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    if self.tile_exists(zoom, x, y):
                        skipped_tiles += 1
                    else:
                        if self.download_tile(zoom, x, y):
                            downloaded_tiles += 1
                            print(f"    Downloaded: {zoom}/{x}/{y}", end='\r')
                        
                        # Be nice to OSM servers
                        time.sleep(delay_ms / 1000.0)
            
            print(f"    Zoom {zoom} complete: {downloaded_tiles} new, {skipped_tiles} cached")
        
        print(f"\n[MapDownloader] Download complete!")
        print(f"  Total tiles: {total_tiles}")
        print(f"  Downloaded: {downloaded_tiles}")
        print(f"  Cached: {skipped_tiles}")
        print(f"  Cache directory: {self.cache_dir.absolute()}")


def download_default_area():
    """Download tiles for default area (Pretoria, South Africa)"""
    downloader = MapTileDownloader(cache_dir="map_cache")
    
    # Default coordinates: Pretoria area
    center_lat = -25.841105
    center_lon = 28.180340
    radius_km = 50.0
    
    # Download tiles
    # Zoom levels:
    # 10 = Regional view (~10 km per tile)
    # 11 = City view (~5 km per tile)
    # 12 = District view (~2.5 km per tile)
    # 13 = Neighborhood view (~1.2 km per tile)
    # 14 = Street view (~600 m per tile)
    downloader.download_area(
        center_lat=center_lat,
        center_lon=center_lon,
        radius_km=radius_km,
        zoom_levels=[10, 11, 12, 13, 14],
        delay_ms=100  # 100ms delay between requests
    )


if __name__ == "__main__":
    print("=" * 70)
    print("TriAD C2 - Offline Map Tile Downloader")
    print("=" * 70)
    download_default_area()
