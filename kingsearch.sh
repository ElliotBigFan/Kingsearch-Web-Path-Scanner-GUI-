#!/usr/bin/env bash
# kingsearch.sh
# Script: cài requirements rồi chạy gui.py (Linux / WSL)

set -e

# Lấy thư mục chứa script
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "[*] Working directory: $SCRIPT_DIR"

if [ ! -f "requirements.txt" ]; then
    echo "[!] requirements.txt not found in $SCRIPT_DIR"
    exit 1
fi

# Chọn python: ưu tiên python3, nếu không có thì dùng python
if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
else
    echo "[!] No 'python3' or 'python' found in PATH."
    exit 1
fi

echo "[*] Using Python: $PYTHON"
echo "[*] Installing Python dependencies from requirements.txt ..."
"$PYTHON" -m pip install --user -r requirements.txt --break-system-packages &> /dev/null

echo "[*] Starting WebPathScan GUI (gui.py) ..."
"$PYTHON" gui.py
