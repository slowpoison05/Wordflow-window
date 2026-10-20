@echo off
setlocal
cd /d "%~dp0"
python -m pip install --upgrade pip
if errorlevel 1 goto :error
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto :error
python -m PyInstaller --noconfirm --clean --onefile --windowed --name WordFlow wordflow.py
if errorlevel 1 goto :error
echo.
echo Build complete: dist\WordFlow.exe
pause
exit /b 0
:error
echo.
echo Build failed. Check the error above and confirm Python is installed and on PATH.
pause
exit /b 1
