@echo off
echo ========================================================
echo   Cookie Shop 3D - Local Web Server (Three.js)
echo ========================================================
echo.
echo Menjalankan local HTTP server pada port 8080...
echo.

set PYTHON_BIN="C:\Program Files\Blender Foundation\Blender 5.3\5.3\python\bin\python.exe"

start "" http://localhost:8080/index.html

if exist %PYTHON_BIN% (
    %PYTHON_BIN% -m http.server 8080
) else (
    python -m http.server 8080
)

pause
