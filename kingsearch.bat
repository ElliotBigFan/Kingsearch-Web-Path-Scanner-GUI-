@echo off
setlocal

REM Lấy thư mục chứa file .bat (project folder)
cd /d "%~dp0"
echo [*] Working directory: %CD%

REM Kiểm tra requirements.txt
if not exist "requirements.txt" (
    echo [!] requirements.txt not found in %CD%
    goto end
)

REM Chọn python (mặc định là 'python' đã cài sẵn trên máy)
set "PYTHON=python"

echo [*] Using Python: %PYTHON%
echo [*] Installing dependencies from requirements.txt ...
%PYTHON% -m pip install --user -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [!] pip install failed with exit code %errorlevel%
    goto end
)

echo [*] Starting WebPathScan GUI (gui.py) ...
%PYTHON% gui.py
if errorlevel 1 (
    echo [!] gui.py exited with code %errorlevel%
    goto end
)

echo [*] Program finished successfully.

:end
echo.
pause
endlocal
