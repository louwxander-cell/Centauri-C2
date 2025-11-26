# Offline Maps - Setup Guide

## 📍 **Default Location**

The system is configured for:
- **Location**: Pretoria, South Africa
- **Coordinates**: `-25.841105, 28.180340`
- **Coverage**: 50 km radius
- **Zoom Levels**: 10-14 (Regional to Street view)

---

## 🗺️ **Download Map Tiles**

### **Step 1: Run the Downloader**

```bash
python3 download_maps.py
```

**What it does:**
- Downloads OpenStreetMap tiles for the specified area
- Caches tiles in `map_cache/` directory
- Downloads 5 zoom levels (10, 11, 12, 13, 14)
- Takes approximately 10-30 minutes

**Zoom Levels:**
- **Zoom 10**: Regional view (~10 km per tile)
- **Zoom 11**: City view (~5 km per tile)
- **Zoom 12**: District view (~2.5 km per tile)
- **Zoom 13**: Neighborhood view (~1.2 km per tile)
- **Zoom 14**: Street view (~600 m per tile)

### **Step 2: Wait for Download**

The downloader will:
1. Calculate tile bounds for 50 km radius
2. Download tiles for each zoom level
3. Skip already cached tiles
4. Show progress for each zoom level

**Example Output:**
```
[MapDownloader] Downloading map tiles for area:
  Center: -25.841105, 28.180340
  Radius: 50 km
  Zoom levels: [10, 11, 12, 13, 14]

  Zoom 10: 12 tiles (1234-1245, 2345-2356)
    Downloaded: 10/1234/2345
    Zoom 10 complete: 12 new, 0 cached

  Zoom 11: 48 tiles (2468-2490, 4690-4712)
    ...

[MapDownloader] Download complete!
  Total tiles: ~500
  Downloaded: 500
  Cached: 0
  Cache directory: /path/to/map_cache
```

---

## 🎯 **Using Offline Maps**

### **In the GUI**

The map widget will automatically:
- Load cached tiles from `map_cache/`
- Display ownship position (cyan circle)
- Show tracks (colored triangles)
- Display pilot positions (yellow stars)
- Allow pan (click and drag)
- Allow zoom (mouse wheel)

### **Map Controls**

**Pan:**
- Click and drag with left mouse button

**Zoom:**
- Mouse wheel up = Zoom in
- Mouse wheel down = Zoom out
- Range: Zoom 1-18 (limited by cached tiles)

**Center on Ownship:**
- Map automatically centers on ownship position
- Updates in real-time as vehicle moves

---

## 📦 **Map Cache Structure**

```
map_cache/
├── 10/
│   ├── 1234/
│   │   ├── 2345.png
│   │   ├── 2346.png
│   │   └── ...
│   └── 1235/
│       └── ...
├── 11/
│   └── ...
├── 12/
│   └── ...
├── 13/
│   └── ...
└── 14/
    └── ...
```

**Tile Naming:**
- `{zoom}/{x}/{y}.png`
- Example: `13/5678/3456.png`

---

## 🌍 **Changing Default Location**

To download maps for a different area:

### **Option 1: Edit download_maps.py**

```python
# In download_maps.py, change these values:
center_lat = -25.841105  # Your latitude
center_lon = 28.180340   # Your longitude
radius_km = 50.0         # Coverage radius
```

### **Option 2: Use Downloader Directly**

```python
from src.ui.map_tile_downloader import MapTileDownloader

downloader = MapTileDownloader(cache_dir="map_cache")
downloader.download_area(
    center_lat=-25.841105,
    center_lon=28.180340,
    radius_km=50.0,
    zoom_levels=[10, 11, 12, 13, 14],
    delay_ms=100
)
```

---

## 📊 **Tile Count Estimates**

For a 50 km radius:

| Zoom | Tiles | Size (approx) |
|------|-------|---------------|
| 10   | ~12   | 300 KB        |
| 11   | ~48   | 1.2 MB        |
| 12   | ~192  | 4.8 MB        |
| 13   | ~768  | 19 MB         |
| 14   | ~3072 | 77 MB         |
| **Total** | **~4092** | **~102 MB** |

**Note:** Actual counts vary based on area shape and coverage.

---

## 🚀 **Features**

### **Offline Operation**
✅ No internet required after download  
✅ Fast tile loading from local cache  
✅ Works in remote/tactical environments  

### **Real-Time Overlays**
✅ Ownship position (cyan circle + heading)  
✅ Track positions (colored triangles)  
✅ Pilot positions (yellow stars)  
✅ Track-to-pilot lines (dashed yellow)  

### **Interactive**
✅ Pan with mouse drag  
✅ Zoom with mouse wheel  
✅ Auto-center on ownship  
✅ Scale bar and coordinates  

---

## ⚙️ **Configuration**

### **Map Widget Settings**

```python
# In map_widget.py
map_widget = OfflineMapWidget(
    cache_dir="map_cache",           # Tile cache directory
    center_lat=-25.841105,           # Initial center
    center_lon=28.180340,
)

# Set ownship position
map_widget.set_ownship(
    lat=-25.841105,
    lon=28.180340,
    heading=90.0  # degrees
)

# Update track
map_widget.update_track(track)
```

---

## 🔧 **Troubleshooting**

### **Tiles Not Displaying**

**Problem:** Map shows gray squares instead of tiles

**Solutions:**
1. Check if tiles were downloaded:
   ```bash
   ls -la map_cache/13/
   ```
2. Re-run downloader:
   ```bash
   python3 download_maps.py
   ```
3. Check zoom level is within cached range (10-14)

### **Download Fails**

**Problem:** Download script errors or times out

**Solutions:**
1. Check internet connection
2. Reduce zoom levels (download fewer):
   ```python
   zoom_levels=[12, 13]  # Just 2 levels
   ```
3. Increase delay between requests:
   ```python
   delay_ms=200  # 200ms instead of 100ms
   ```

### **Slow Performance**

**Problem:** Map is slow to pan/zoom

**Solutions:**
1. Reduce zoom level (fewer tiles to load)
2. Clear tile cache and re-download:
   ```bash
   rm -rf map_cache/
   python3 download_maps.py
   ```
3. Increase tile cache size in memory

---

## 📝 **OpenStreetMap Attribution**

This system uses OpenStreetMap tiles:

**License:** Open Database License (ODbL)  
**Attribution:** © OpenStreetMap contributors  
**Tile Server:** https://tile.openstreetmap.org  

**Usage Policy:**
- Tiles are cached for offline use
- Delay between requests (100ms) to be respectful
- For production, consider running your own tile server

**More Info:**
- https://www.openstreetmap.org/copyright
- https://operations.osmfoundation.org/policies/tiles/

---

## 🎯 **Best Practices**

### **For Operators**
1. **Download maps before deployment**
2. **Test offline mode** before going to field
3. **Verify coverage area** matches mission area
4. **Keep cache directory** backed up

### **For Administrators**
1. **Download multiple areas** if operating in different locations
2. **Update maps periodically** (monthly/quarterly)
3. **Monitor cache size** (can grow large)
4. **Consider tile server** for large deployments

---

## 🚀 **Quick Start**

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Download maps (one-time)
python3 download_maps.py

# 3. Run C2 system
python3 main.py

# 4. Maps will load automatically in center panel
```

---

## 📊 **Summary**

✅ **Offline maps** for tactical operations  
✅ **50 km coverage** around Pretoria  
✅ **5 zoom levels** (regional to street)  
✅ **Real-time overlays** (ownship, tracks, pilots)  
✅ **Interactive** (pan, zoom)  
✅ **~102 MB** total cache size  
✅ **OpenStreetMap** tiles (free, open source)  

**Ready for offline tactical operations! 🗺️**

---

*Map System Date: November 25, 2024*  
*Status: ✅ Offline Maps Ready*
