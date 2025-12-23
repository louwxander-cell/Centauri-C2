# Track Classification Colors - Quick Reference

## Color Palette (RadarUI Standard)

```
🔴 UAV               #DC143C  Crimson Red
🔴 UAV Multi-Rotor   #8B0000  Dark Red
🟠 UAV Fixed-Wing    #FF8C00  Dark Orange
🔵 Walker            #4169E1  Royal Blue
🟡 Plane             #FFD700  Gold
🔷 Bird              #00CED1  Dark Turquoise
🟣 Vehicle           #9370DB  Medium Purple
⚫ Clutter           #808080  Gray
⚪ Undeclared        #D3D3D3  Light Gray
```

## RGB Values

| Class | Hex | RGB |
|-------|-----|-----|
| UAV | #DC143C | rgb(220, 20, 60) |
| UAV Multi-Rotor | #8B0000 | rgb(139, 0, 0) |
| UAV Fixed-Wing | #FF8C00 | rgb(255, 140, 0) |
| Walker | #4169E1 | rgb(65, 105, 225) |
| Plane | #FFD700 | rgb(255, 215, 0) |
| Bird | #00CED1 | rgb(0, 206, 209) |
| Vehicle | #9370DB | rgb(147, 112, 219) |
| Clutter | #808080 | rgb(128, 128, 128) |
| Undeclared | #D3D3D3 | rgb(211, 211, 211) |

## Usage in Code

### JavaScript/QML
```javascript
property var trackClassColors: ({
    "UAV": "#DC143C",
    "UAV_MULTI_ROTOR": "#8B0000",
    "UAV_FIXED_WING": "#FF8C00",
    "WALKER": "#4169E1",
    "PLANE": "#FFD700",
    "BIRD": "#00CED1",
    "VEHICLE": "#9370DB",
    "CLUTTER": "#808080",
    "UNDECLARED": "#D3D3D3"
})
```

### CSS
```css
.uav { color: #DC143C; }
.uav-multi-rotor { color: #8B0000; }
.uav-fixed-wing { color: #FF8C00; }
.walker { color: #4169E1; }
.plane { color: #FFD700; }
.bird { color: #00CED1; }
.vehicle { color: #9370DB; }
.clutter { color: #808080; }
.undeclared { color: #D3D3D3; }
```

## Color Naming

Standard web color names used:
- **Crimson** - Deep red
- **DarkRed** - Very dark red
- **DarkOrange** - Deep orange
- **RoyalBlue** - Bright blue
- **Gold** - Metallic yellow
- **DarkTurquoise** - Deep cyan
- **MediumPurple** - Soft purple
- **Gray** - Neutral gray
- **LightGray** - Pale gray
