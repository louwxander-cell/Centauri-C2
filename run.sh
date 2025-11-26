#!/bin/bash
# TriAD C2 System Launcher

echo "============================================================"
echo "  TriAD Counter-UAS Command & Control System"
echo "============================================================"
echo ""

# Check Python version
python3 --version

echo ""
echo "Starting TriAD C2..."
echo ""

# Run the application
python3 main.py

echo ""
echo "TriAD C2 shutdown complete."
