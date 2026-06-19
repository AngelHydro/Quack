@echo off
REM Build a standalone Quack.exe with PyInstaller.
REM Double-click this file, or run it from a terminal.

echo Installing build dependencies...
python -m pip install --quiet --upgrade pillow pyinstaller
if errorlevel 1 goto :error

echo.
echo Building Quack.exe...
python -m PyInstaller --onefile --windowed --name Quack ^
    --icon icon.ico --collect-submodules quack run.py
if errorlevel 1 goto :error

echo.
echo Done. The executable is at: dist\Quack.exe
pause
exit /b 0

:error
echo.
echo Build failed. See the messages above.
pause
exit /b 1
