# TriAD C2 - Windows Setup Guide

**Quick guide to run TriAD C2 on a Windows laptop**

---

## 📋 Prerequisites

You'll need to install these on your Windows laptop:

1. **Git** (to download the code)
2. **Python 3.11+** (to run the application)
3. **Visual Studio C++ Build Tools** (for some Python packages)

---

## 🚀 Step-by-Step Installation

### **Step 1: Install Git for Windows**

1. Download Git from: https://git-scm.com/download/win
2. Run the installer (use default options)
3. Verify installation:
   ```cmd
   git --version
   ```

---

### **Step 2: Install Python**

1. Download Python 3.11 or 3.12 from: https://www.python.org/downloads/windows/
2. **IMPORTANT:** During installation:
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install pip"
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

---

### **Step 3: Clone the Repository**

1. Open **Command Prompt** or **PowerShell**
2. Navigate to where you want the project:
   ```cmd
   cd C:\Users\YourUsername\Documents
   ```
3. Clone the repository:
   ```cmd
   git clone https://github.com/louwxander-cell/Centauri-C2.git
   ```
4. Enter the project folder:
   ```cmd
   cd Centauri-C2
   ```

---

### **Step 4: Install Python Dependencies**

```cmd
pip install -r requirements.txt
```

This will install:
- PySide6 (Qt for Python)
- pyserial (GPS communication)
- numpy (math operations)
- Other required packages

**If you get errors about C++ compilation:**

Install Visual Studio Build Tools:
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++"
3. Retry: `pip install -r requirements.txt`

---

### **Step 5: Configure for Windows**

The application should work out of the box, but you may need to adjust:

#### **GPS Configuration** (if using GPS)

Edit `config/settings.json`:

```json
{
  "gps": {
    "enabled": true,
    "port": "COM3",  // ← Windows uses COM ports (COM3, COM4, etc.)
    "baudrate": 115200
  }
}
```

**To find your GPS COM port:**
1. Open **Device Manager**
2. Expand **Ports (COM & LPT)**
3. Look for your GPS device (e.g., "USB Serial Port (COM3)")

---

### **Step 6: Run the Application**

#### **Method 1: Using Command Prompt**

```cmd
python triad_c2.py
```

#### **Method 2: Using PowerShell**

```powershell
python triad_c2.py
```

#### **Method 3: Double-click (after first time setup)**

Create a file named `run_c2.bat` with this content:
```batch
@echo off
cd /d %~dp0
python triad_c2.py
pause
```

Then just double-click `run_c2.bat` to run!

---

## 🔧 Troubleshooting

### **Problem: "python is not recognized"**

**Solution:**
1. Close and reopen Command Prompt
2. If still not working, manually add Python to PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" variable
   - Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python311`
   - Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\Scripts`

---

### **Problem: "No module named 'PySide6'"**

**Solution:**
```cmd
pip install PySide6
```

Or install all dependencies:
```cmd
pip install -r requirements.txt
```

---

### **Problem: GPS not detected**

**Solution:**

1. Check COM port in Device Manager
2. Update `config/settings.json` with correct COM port
3. Install GPS drivers if needed
4. Verify GPS is connected:
   ```cmd
   python diagnose_gps.py COM3 115200
   ```

---

### **Problem: Radar/RF not connecting**

**Solution:**

1. Check Windows Firewall:
   - Allow Python through firewall
   - Allow incoming connections on required ports

2. Check network configuration:
   ```cmd
   ipconfig
   ping <radar_ip>
   ```

3. Update `config/settings.json` with correct IPs

---

### **Problem: Application crashes on startup**

**Solution:**

1. Check Python version:
   ```cmd
   python --version
   ```
   (Should be 3.11 or higher)

2. Reinstall dependencies:
   ```cmd
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   ```

3. Check for error messages in console

---

## 📁 Windows File Paths

Windows uses different paths than Mac/Linux:

| Component | Mac Path | Windows Path |
|-----------|----------|--------------|
| GPS Port | `/dev/tty.usbmodem38382103` | `COM3` or `COM4` |
| Config | `config/settings.json` | `config\settings.json` |
| Logs | `logs/` | `logs\` |

Python handles both `/` and `\` in paths, so the code should work as-is.

---

## 🎯 Quick Start Checklist

After installation, verify everything works:

- [ ] Git installed: `git --version`
- [ ] Python installed: `python --version`
- [ ] Code cloned: `cd Centauri-C2`
- [ ] Dependencies installed: `pip list | findstr PySide6`
- [ ] GPS configured (if applicable): Check `config/settings.json`
- [ ] Application runs: `python triad_c2.py`

---

## 🔌 Hardware Connections on Windows

### **GPS (Septentrio Mosaic-H)**

1. Connect GPS via USB
2. Windows will install drivers automatically
3. Check Device Manager for COM port
4. Update `config/settings.json`:
   ```json
   "port": "COM3"
   ```

### **Radar (Echodyne EchoGuard)**

1. Connect via Ethernet
2. Configure network adapter:
   - Open **Network Connections**
   - Right-click adapter → **Properties**
   - Set static IP in same subnet as radar
   - Example: PC = `192.168.1.50`, Radar = `192.168.1.100`

3. Test connectivity:
   ```cmd
   ping 192.168.1.100
   ```

4. Update `config/settings.json`:
   ```json
   "radar": {
     "host": "192.168.1.100",
     "port": 23000
   }
   ```

### **RF Sensor (BlueHalo)**

1. Connect via Ethernet or Wi-Fi
2. Ensure certificates are in correct path:
   ```
   Integration docs\Bluehalo_2025-11-25_1912\ott\
   ```

3. Update `config/settings.json` with correct host/port

---

## 📊 Performance on Windows

### **Expected Performance:**
- UI: 60 FPS (same as Mac)
- Updates: 10 Hz (same as Mac)
- Memory: ~200-300 MB

### **If Performance is Slow:**

1. Close other applications
2. Check Task Manager for CPU/RAM usage
3. Update graphics drivers
4. Consider using Windows 11 (better Qt support)

---

## 🔐 Windows Security

### **Antivirus/Firewall**

You may need to:

1. **Allow Python in Windows Defender:**
   - Windows Security → Virus & threat protection
   - Exclusions → Add folder
   - Add: `C:\Users\YourUsername\Documents\Centauri-C2`

2. **Allow network access:**
   - Windows Defender Firewall → Allow an app
   - Add: Python (python.exe)
   - Allow both Private and Public networks

---

## 📦 Alternative: Using Virtual Environment (Recommended)

For cleaner installation:

```cmd
# Create virtual environment
python -m venv c2_env

# Activate it
c2_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python triad_c2.py

# Deactivate when done
deactivate
```

**Benefits:**
- Isolated from system Python
- No conflicts with other projects
- Easy to delete/reinstall

---

## 🎬 Quick Demo - First Run

**Complete first-time setup:**

```cmd
# 1. Open Command Prompt as Administrator
Win + X → Command Prompt (Admin)

# 2. Navigate to Documents folder
cd C:\Users\%USERNAME%\Documents

# 3. Clone repository
git clone https://github.com/louwxander-cell/Centauri-C2.git

# 4. Enter folder
cd Centauri-C2

# 5. Install dependencies
pip install -r requirements.txt

# 6. Run application
python triad_c2.py
```

**You should see:**
```
TriAD C2 - Starting...
[Bridge] Initializing orchestration layer
[MockEngine] Starting simulated tracks
[UI] Launching Qt interface
System running at http://localhost:5100
```

**Application window opens with simulated drone tracks!**

---

## 🌐 Remote Access (Optional)

To access C2 from another computer on network:

1. Find Windows laptop IP:
   ```cmd
   ipconfig
   ```

2. Note IPv4 address (e.g., `192.168.0.50`)

3. From another computer, browse to:
   ```
   http://192.168.0.50:5100
   ```

4. **Important:** Allow through firewall (see above)

---

## 📞 Support & Resources

### **If You Get Stuck:**

1. **Check Python version:**
   ```cmd
   python --version
   ```
   Must be 3.11+

2. **Check PySide6 installation:**
   ```cmd
   python -c "import PySide6; print(PySide6.__version__)"
   ```

3. **View error messages:** Run from Command Prompt to see full output

4. **Check requirements:**
   ```cmd
   pip check
   ```

### **Useful Windows Commands:**

```cmd
# List COM ports
mode

# Check Python packages
pip list

# Update all packages
pip install --upgrade -r requirements.txt

# Test GPS connection
python diagnose_gps.py COM3 115200

# Test radar connection
python test_radar_connection.py 192.168.1.100 23000
```

---

## ✅ Success Checklist

After setup, you should be able to:

- [x] Run `python triad_c2.py` without errors
- [x] See the Qt UI window open
- [x] See simulated drone tracks moving
- [x] Click on tracks to select them
- [x] See the tactical radar display
- [x] GPS shows position (if hardware connected)
- [x] Radar shows tracks (if hardware connected)

---

## 🎉 You're Ready!

Your Windows laptop is now set up to run TriAD C2!

**Next steps:**
1. Connect your sensors (GPS, radar, RF)
2. Update `config/settings.json` with correct ports/IPs
3. Run diagnostic scripts to verify connections
4. Launch the full system!

**Commands to bookmark:**
```cmd
# Run C2
python triad_c2.py

# Check GPS
python diagnose_gps.py COM3 115200

# Check Radar
python test_radar_connection.py 192.168.1.100 23000

# Pull latest updates
git pull origin main
```

---

*Happy tracking!* 🚀
