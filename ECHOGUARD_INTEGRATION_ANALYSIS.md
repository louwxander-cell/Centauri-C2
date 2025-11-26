# Echodyne EchoGuard Radar - Integration Analysis

## 📋 Documentation Review Summary

Based on the provided Echodyne EchoGuard documentation, here's what I've extracted:

---

## 🔍 Key Findings

### **Available Documentation**
✅ **ICD Document**: `ICD, EchoGuard, 700-0005-203_Rev05.pdf` (5 pages)  
✅ **Developer Manual**: `EchoGuard_Radar_Developer_Manual_SW16.4.0.pdf` (99 pages)  
✅ **User Manual**: `EchoGuard_INTL_User_Manual_English.pdf` (16 pages)  
✅ **BNET API Manual**: `BNET_11_1_5_Manual.pdf`  
✅ **API Headers**: Complete C/C++ header files with data structures  
✅ **Sample Data**: `900238_rev01_SW16.3_Sample_Data.zip` (268 MB)  
✅ **Linux Applications**: BNET example applications  
✅ **Windows API**: Complete API libraries and headers  

---

## 📊 Track Data Structure (From `daa_track.h`)

### **Track Header**
```c
typedef struct track_header {
    char        packet_tag[12];           // Packet identifier
    uint32_t    packetSize;               // Total packet size
    uint32_t    nTracks;                  // Number of tracks in packet
    uint32_t    sys_time_days;            // System time (days)
    uint32_t    sys_time_ms;              // System time (milliseconds)
    uint32_t    profile_atracker;         // Tracker profile
    uint32_t    profile_atracker_main;    // Main tracker profile
    uint32_t    packet_type;              // Packet type identifier
} track_header;
```

### **Track Data (Per Track)**
```c
typedef struct track_data {
    // Track Identification
    uint32_t    ID;                       // Unique track ID
    uint32_t    state;                    // Track state
    
    // Position (Spherical Coordinates)
    float       azest;                    // Azimuth estimate (degrees)
    float       elest;                    // Elevation estimate (degrees)
    float       rest;                     // Range estimate (meters)
    
    // Position (Cartesian Coordinates)
    float       xest;                     // X position (meters)
    float       yest;                     // Y position (meters)
    float       zest;                     // Z position (meters)
    
    // Velocity (Cartesian)
    float       velxest;                  // X velocity (m/s)
    float       velyest;                  // Y velocity (m/s)
    float       velzest;                  // Z velocity (m/s)
    
    // Association Data
    uint32_t    assocMeas_id_main[3];     // Associated measurement IDs
    float       assocMeas_chi2_main[3];   // Chi-squared values
    
    // Timing
    int32_t     TOCA_days;                // Time of closest approach (days)
    int32_t     TOCA_ms;                  // Time of closest approach (ms)
    float       DOCA;                     // Distance of closest approach
    float       lifetime;                 // Track lifetime (seconds)
    uint32_t    lastUpdateTime_days;      // Last update time (days)
    uint32_t    lastUpdateTime_ms;        // Last update time (ms)
    uint32_t    lastAssociatedDataTime_days;
    uint32_t    lastAssociatedDataTime_ms;
    uint32_t    acquiredTime_days;        // Track acquisition time (days)
    uint32_t    acquiredTime_ms;          // Track acquisition time (ms)
    
    // Classification
    float       estConfidence;            // Confidence estimate (0-1)
    uint32_t    numAssocMeasurements;     // Number of associated measurements
    float       estRCS;                   // Estimated RCS (m²)
    float       probabilityOther;         // Probability: other target
    float       probabilityUAV;           // Probability: UAV/drone
} track_data;
```

### **Constants**
```c
#define MAX_TRACKS                  128   // Maximum tracks per packet
#define MAX_MEASUREMENTS_2_TRK_MAIN 3     // Max measurements per track
```

---

## 🌐 Network Interface (From `bnet_interface.h`)

### **Connection Method**
The radar uses a **TCP-based interface** called "BNET" (Binary Network).

### **Key API Functions**
```cpp
class bnet_interface {
    // Connection
    void connect(const std::string& IP, 
                 unsigned short port,
                 const std::string& custom_directory, 
                 long timeout_ms = 5000);
    
    void disconnect(void);
    void reconnect(void);
    
    // Data Retrieval
    MESAK_Track get_track(void);          // Get track data
    MESAK_Status get_status(void);        // Get radar status
    MESAK_Detection get_detection(void);  // Get raw detections
    MESAK_Measurement get_meas(void);     // Get measurements
    
    // Commands
    std::pair<mesa_command_status_t, std::string> 
        send_command(const std::string& command);
    
    // Configuration
    void set_collect(mesa_data_t d_type, bool flag);
    void set_buffer_length(mesa_data_t d_type, std::size_t length);
};
```

### **Data Types Available**
- **Tracks**: Processed target tracks (what we need)
- **Detections**: Raw radar detections
- **Measurements**: Processed measurements
- **Status**: Radar system status
- **RV Map**: Range-Velocity map

---

## 🔧 Integration Requirements

### **What We Need to Know**
1. ✅ **Data Structure**: Fully documented in header files
2. ❓ **IP Address**: What is the radar's IP address?
3. ❓ **Port Number**: What port does the radar listen on?
4. ❓ **Coordinate System**: 
   - Is azimuth relative to true north, magnetic north, or radar boresight?
   - Is elevation relative to horizon or radar mounting angle?
   - What is the origin of the X/Y/Z Cartesian coordinates?
5. ❓ **Update Rate**: How often are track packets sent?
6. ❓ **Binary Protocol**: Need to understand the binary packet format

### **Coordinate System Questions**
From the data structure, we have:
- **Spherical**: `azest`, `elest`, `rest`
- **Cartesian**: `xest`, `yest`, `zest`

**Need to clarify:**
- Azimuth reference (0° = North? East? Radar boresight?)
- Elevation reference (0° = horizon? Radar mounting?)
- Cartesian origin (radar location? Fixed point?)
- Units confirmed (degrees, meters, m/s)

---

## 🎯 Classification Data

The radar provides **UAV probability**:
```c
float probabilityUAV;    // 0.0 to 1.0
float probabilityOther;  // 0.0 to 1.0
```

This is perfect for our `TargetType` classification!

**Mapping:**
- `probabilityUAV > 0.7` → `TargetType.DRONE`
- `probabilityUAV < 0.3` → `TargetType.BIRD` or `TargetType.UNKNOWN`
- `0.3 <= probabilityUAV <= 0.7` → `TargetType.UNKNOWN`

---

## 🐍 Python Integration Approach

### **Option 1: Use BNET C++ API via ctypes/cffi**
- Use the provided `libbnetinterface.dll` / `.so`
- Create Python bindings with `ctypes` or `cffi`
- Call C++ functions directly

**Pros:**
- Official API, fully supported
- All features available
- Handles binary protocol automatically

**Cons:**
- Requires C++ library compilation for Linux/Mac
- More complex Python bindings

### **Option 2: Reverse-engineer Binary Protocol**
- Connect via raw TCP socket
- Parse binary packets directly in Python
- Use `struct` module to unpack data

**Pros:**
- Pure Python, no dependencies
- Full control over data flow
- Easier to debug

**Cons:**
- Need to understand binary framing
- May miss some protocol details
- Not officially supported

### **Option 3: Use Sample Data to Understand Format**
- Extract `900238_rev01_SW16.3_Sample_Data.zip`
- Analyze saved binary data
- Reverse-engineer packet structure

**Recommended: Option 2 + Option 3**
1. Analyze sample data to understand binary format
2. Implement pure Python TCP client
3. Parse binary packets using `struct`

---

## 📦 Next Steps

### **Immediate Actions Needed:**

1. **Extract Sample Data**
   ```bash
   unzip "900238_rev01_SW16.3_Sample_Data.zip"
   ```
   Analyze the binary format of saved track data

2. **Answer Configuration Questions:**
   - [ ] Radar IP address: `_______________`
   - [ ] Radar port: `_______________` (likely 23000 or similar)
   - [ ] Coordinate reference frame
   - [ ] Update rate (Hz)

3. **Test Connection:**
   - Can you connect to the radar now?
   - Is it powered on and accessible?
   - What IP/port is it configured for?

4. **Analyze Binary Format:**
   - I'll extract and analyze the sample data
   - Determine packet framing and structure
   - Create Python parser

---

## 💡 Recommended Implementation

Based on the documentation, here's my recommended approach:

### **Phase 1: Analyze Sample Data** (Today)
- Extract sample data ZIP
- Analyze binary track packet format
- Understand packet framing (header, size, data)
- Create Python struct definitions

### **Phase 2: Implement TCP Client** (1-2 days)
- Create TCP socket connection
- Implement binary packet parser
- Map to our `Track` data model
- Handle coordinate transformations

### **Phase 3: Test with Live Radar** (1 day)
- Connect to actual radar
- Validate data parsing
- Tune coordinate transformations
- Verify track updates

---

## 🔍 Questions for You

1. **Network Configuration:**
   - What is the radar's IP address?
   - What port does it use for track data?
   - Is the radar on the same network as the C2 system?

2. **Coordinate System:**
   - Do you have documentation on the coordinate reference frame?
   - Is the radar mounted on a vehicle or fixed position?
   - What is the mounting orientation?

3. **Current Status:**
   - Is the radar powered on and accessible now?
   - Can you ping the radar IP?
   - Do you have access to the radar's web interface or configuration?

4. **Sample Data:**
   - Should I extract and analyze the 268 MB sample data file?
   - This will help me understand the binary format

---

## 📝 Summary

### **What We Know:**
✅ Complete C/C++ data structures  
✅ Track format with position, velocity, classification  
✅ UAV probability for target classification  
✅ TCP-based BNET interface  
✅ Sample data available for analysis  

### **What We Need:**
❓ Radar IP address and port  
❓ Coordinate system reference frame  
❓ Binary packet framing details  
❓ Live radar access for testing  

### **Next Action:**
**Please provide:**
1. Radar IP address and port
2. Coordinate system documentation (if available)
3. Permission to extract and analyze sample data
4. Confirm if radar is currently accessible

Once I have this information, I can implement the production radar driver in **1-2 days**.

---

*Analysis Date: November 25, 2024*  
*Status: Ready to implement pending network configuration*
