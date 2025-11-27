# TriAD C2 Integration - Quick Checklist

## ✅ What I Need From You

### 🎯 Critical Information Required

#### 1. **Echodyne Radar**
- [ ] ICD document (PDF/Word)
- [ ] IP address and port number
- [ ] Sample message (copy/paste actual data)
- [ ] Coordinate system specification

#### 2. **BlueHalo RF Sensor**
- [ ] API documentation (PDF/URL)
- [ ] Base URL and authentication method
- [ ] Sample JSON response
- [ ] Update frequency

#### 3. **GPS/Compass**
- [ ] Device model/part number
- [ ] Serial port settings (baud rate, etc.)
- [ ] Sample NMEA sentences (copy/paste)
- [ ] Update rate

#### 4. **Gunner Station (RWS)**
- [ ] Control protocol specification
- [ ] IP address and port
- [ ] Sample command format
- [ ] Coordinate reference frame

#### 5. **Map Requirements**
- [ ] Preferred map provider (OSM, Mapbox, Google, offline?)
- [ ] Coverage area (lat/lon bounds)
- [ ] API key (if commercial provider)

---

## 📋 Quick Questions

### Network
1. What IP addresses for each sensor?
2. Same subnet or different networks?
3. Any firewalls or VLANs?

### Data Formats
1. Radar: Binary or JSON messages?
2. RF: REST polling or WebSocket streaming?
3. RWS: Binary or text commands?

### Coordinates
1. What reference frame for radar (true north, magnetic, vehicle body)?
2. GPS datum (WGS84 confirmed)?
3. RWS pointing reference (vehicle-relative or absolute)?

### Map
1. Online or offline maps?
2. Show track history trails?
3. Display geofencing zones?

---

## 🚀 What Happens Next

Once you provide the information above, I will:

1. ✅ **Fix the current enum bug** (already done)
2. 🔧 **Implement real radar driver** - Replace mock with TCP client
3. 🔧 **Implement real RF driver** - REST/WebSocket client
4. 🔧 **Implement real GPS driver** - Serial NMEA parser
5. 🔧 **Implement real RWS driver** - UDP/TCP command protocol
6. 🗺️ **Add map overlay** - GPS position + track display
7. 🎯 **Add coordinate transforms** - Proper reference frame conversions
8. 🛡️ **Add geofencing** - Enforce safe/restricted zones
9. 🧪 **Test with real hardware** - End-to-end validation

---

## 📄 Documents to Send

Please send me:
1. **All ICDs** (Interface Control Documents)
2. **API documentation** (URLs or PDFs)
3. **Sample data** (actual messages from sensors)
4. **Network diagram** (if available)
5. **Coordinate system specs** (reference frames)

You can:
- Email documents
- Share via secure file transfer
- Paste sample data directly
- Provide URLs to documentation

---

## ⏱️ Timeline Estimate

With complete documentation:
- **Radar integration**: 2-3 days
- **RF integration**: 2-3 days
- **GPS + Map**: 2-3 days
- **RWS integration**: 1-2 days
- **Testing**: 2-3 days

**Total**: ~2 weeks for full production integration

---

## 🔧 Current Status

✅ **Mock system working** (with enum fix applied)  
⏳ **Awaiting sensor specifications**  
📋 **Ready to implement production drivers**

---

*See INTEGRATION_REQUIREMENTS.md for detailed technical requirements*
