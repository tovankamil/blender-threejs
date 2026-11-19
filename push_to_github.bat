@echo off
echo ========================================================
echo   Push 3D Cookie Shop to GitHub (tovankamil/blender-threejs)
echo ========================================================
echo.
echo Melakukan sinkronisasi commit dan push ke branch main...
echo.

git status

echo.
echo Menjalankan git push -u origin main...
echo (Jika muncul jendela login GitHub atau browser, silakan login/klik Authorize)
echo.

git push -u origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUKSES] Semua file berhasil di-push ke https://github.com/tovankamil/blender-threejs!
) else (
    echo [GAGAL] Git push belum berhasil. Pastikan Anda telah login ke akun GitHub Anda.
)
echo.
pause
