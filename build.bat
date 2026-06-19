@echo off
REM Build a standalone Quack.exe with PyInstaller.
REM This is only for REBUILDING from source and requires Python.
REM If you just want to RUN Quack, download Quack.exe from the Releases page
REM (no Python needed): https://github.com/AngelHydro/Quack/releases

where python >NUL 2>&1
if errorlevel 1 (
    echo Python was not found on this PC.
    echo.
    echo build.bat only builds the app from source, which needs Python.
    echo If you simply want to RUN Quack, no build is needed:
    echo   download Quack.exe from https://github.com/AngelHydro/Quack/releases
    echo.
    echo To build here, install Python first: https://www.python.org/downloads/
    echo (tick "Add python.exe to PATH" during installation^), then run build.bat again.
    pause
    exit /b 1
)

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
