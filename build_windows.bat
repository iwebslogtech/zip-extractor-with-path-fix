@echo off
cd /d "%~dp0"
python -m pip install --upgrade pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed --name "ZIP-Extractor-Path-Fix" app.py
echo.
echo Build complete. Check the dist folder.
pause
