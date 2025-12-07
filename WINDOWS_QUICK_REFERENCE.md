# Windows Quick Reference Card

**Fast reference for running TriAD C2 on Windows**

---

## 🚀 Quick Start (First Time)

```cmd
# 1. Install Python 3.11+ from python.org (check "Add to PATH")
# 2. Install Git from git-scm.com

# 3. Clone and setup
cd C:\Users\%USERNAME%\Documents
git clone https://github.com/louwxander-cell/Centauri-C2.git
cd Centauri-C2
pip install -r requirements.txt

# 4. Run
python triad_c2.py
```

**Or just double-click:** `run_c2_windows.bat`

---

## 📝 Common Commands

```cmd
# Run application
python triad_c2.py

# Update from GitHub
git pull origin main

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check Python version
python --version

# List installed packages
pip list

# Find COM ports
mode
# Or check Device Manager → Ports (COM & LPT)
```

---

## 🔌 COM Port Configuration

**Finding GPS COM Port:**
1. Connect GPS via USB
2. Open **Device Manager** (`devmgmt.msc`)
3. Expand **Ports (COM & LPT)**
4. Note the COM number (e.g., COM3, COM4)

**Update config:**

Edit `config\settings.json`:
```json
{
  "gps": {
    "port": "COM3",  // ← Your COM port here
    "baudrate": 115200
  }
}
```

---

## 🌐 Network Configuration (Radar/RF)

**Check your IP:**
```cmd
ipconfig
```

**Ping radar:**
```cmd
ping 192.168.1.100
```

**Set static IP (if needed):**
1. Control Panel → Network Connections
2. Right-click adapter → Properties
3. IPv4 → Use the following IP address
4. Enter: IP, Subnet Mask, Gateway

**Update config:**

Edit `config\settings.json`:
```json
{
  "network": {
    "radar": {
      "host": "192.168.1.100",  // ← Radar IP
      "port": 23000
    }
  }
}
```

---

## 🧪 Diagnostic Commands

```cmd
# Test GPS
python diagnose_gps.py COM3 115200

# Test Radar
python test_radar_connection.py 192.168.1.100 23000

# Check GPS baseline
python check_gps_ownship.py

# Quick GPS status
python gps_quick_check.py COM3
```

---

## 🔥 Firewall Settings

**Allow Python through firewall:**

1. **Windows Security** → **Firewall & network protection**
2. **Allow an app through firewall**
3. **Change settings** → **Allow another app**
4. Browse to: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe`
5. Check both **Private** and **Public**

**Or run once as Administrator:**
```cmd
netsh advfirewall firewall add rule name="Python C2" dir=in action=allow program="C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
```

---

## 📂 Important File Locations

```
C:\Users\YourName\Documents\Centauri-C2\
├── config\settings.json          ← Main configuration
├── triad_c2.py                   ← Main application
├── run_c2_windows.bat            ← Quick launcher
├── requirements.txt              ← Dependencies
├── diagnose_gps.py               ← GPS diagnostic
├── test_radar_connection.py      ← Radar test
└── logs\                         ← Log files
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| **Python not found** | Add to PATH or reinstall with "Add to PATH" |
| **PySide6 error** | `pip install PySide6` |
| **GPS not detected** | Check Device Manager for COM port |
| **Radar won't connect** | Check firewall, ping radar IP |
| **Application crashes** | Run from cmd.exe to see error messages |
| **Slow performance** | Close other apps, update GPU drivers |

---

## 🔄 Update Procedure

**Get latest code:**
```cmd
cd C:\Users\%USERNAME%\Documents\Centauri-C2
git pull origin main
pip install -r requirements.txt --upgrade
```

---

## 🖥️ Typical Windows Paths

| Item | Path |
|------|------|
| **Python** | `C:\Users\YourName\AppData\Local\Programs\Python\Python311` |
| **Project** | `C:\Users\YourName\Documents\Centauri-C2` |
| **Config** | `config\settings.json` |
| **GPS Port** | `COM3` or `COM4` |
| **Logs** | `logs\triad_c2.log` |

---

## 📋 Pre-Flight Checklist

Before running with real hardware:

- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] Code cloned from GitHub
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] GPS COM port identified (if using GPS)
- [ ] Radar IP configured (if using radar)
- [ ] Firewall allows Python
- [ ] Tested with: `python triad_c2.py`

---

## 🎯 One-Line Commands

**Full setup:**
```cmd
cd C:\Users\%USERNAME%\Documents && git clone https://github.com/louwxander-cell/Centauri-C2.git && cd Centauri-C2 && pip install -r requirements.txt
```

**Daily use:**
```cmd
cd C:\Users\%USERNAME%\Documents\Centauri-C2 && python triad_c2.py
```

**Update and run:**
```cmd
cd C:\Users\%USERNAME%\Documents\Centauri-C2 && git pull && pip install -r requirements.txt --upgrade && python triad_c2.py
```

---

## 💡 Pro Tips

1. **Create desktop shortcut** to `run_c2_windows.bat` for one-click launch
2. **Use virtual environment** for isolation: `python -m venv c2_env`
3. **Check logs** in `logs\` folder if issues occur
4. **Run as Administrator** if permission errors occur
5. **Use Command Prompt** (not PowerShell) to avoid execution policy issues

---

## 📞 Quick Help

**Verify installation:**
```cmd
python --version          # Should be 3.11+
pip list | findstr PySide6  # Should show version
git --version              # Should show git version
```

**Test imports:**
```cmd
python -c "import PySide6; print('Qt OK')"
python -c "import serial; print('Serial OK')"
python -c "import numpy; print('NumPy OK')"
```

---

*Keep this file handy for quick reference!* 📌
