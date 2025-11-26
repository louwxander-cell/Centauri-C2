#!/usr/bin/env python3
"""
TriAD C2 Installation Verification Script
Checks all dependencies and project files
"""

import sys
import os

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.9+)")
        return False

def check_dependencies():
    """Check required Python packages"""
    print("\nChecking dependencies...")
    required = {
        'PyQt6': 'PyQt6',
        'pydantic': 'pydantic',
        'pyqtgraph': 'pyqtgraph',
        'numpy': 'numpy',
        'serial': 'pyserial'
    }
    
    all_ok = True
    for module, package in required.items():
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (missing)")
            all_ok = False
    
    return all_ok

def check_project_structure():
    """Check project files and directories"""
    print("\nChecking project structure...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'pyproject.toml',
        'README.md',
        'config/settings.json',
        'config/zones.geojson',
        'src/__init__.py',
        'src/core/bus.py',
        'src/core/datamodels.py',
        'src/core/fusion.py',
        'src/drivers/base.py',
        'src/drivers/radar.py',
        'src/drivers/rf.py',
        'src/drivers/gps.py',
        'src/drivers/rws.py',
        'src/ui/main_window.py',
        'src/ui/radar_scope.py',
        'src/ui/styles.py',
        'tests/test_fusion.py'
    ]
    
    all_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (missing)")
            all_ok = False
    
    return all_ok

def check_imports():
    """Check if main modules can be imported"""
    print("\nChecking module imports...")
    
    modules = [
        'src.core.bus',
        'src.core.datamodels',
        'src.core.fusion',
        'src.drivers.base',
        'src.drivers.radar',
        'src.ui.main_window'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except Exception as e:
            print(f"  ❌ {module} ({str(e)})")
            all_ok = False
    
    return all_ok

def main():
    """Run all verification checks"""
    print("=" * 70)
    print("TriAD C2 Installation Verification")
    print("=" * 70)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Module Imports", check_imports)
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
        if not result:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n🎉 All checks passed! System is ready to run.")
        print("\nTo start the application:")
        print("  python3 main.py")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please install missing dependencies:")
        print("  pip3 install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
