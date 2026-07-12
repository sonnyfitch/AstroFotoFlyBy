@echo off
SET "LOG_FILE=%~dp0crash_log.txt"
SET "SIRIL_PY=%LocalAppData%\siril\venv\Scripts\python.exe"

echo [LOG] Initializing AstroFotoFlyBy Pipeline Diagnostics... > "%LOG_FILE%"
echo [LOG] Current Folder Path: %~dp0 >> "%LOG_FILE%"

IF EXIST "%SIRIL_PY%" (
    echo [LOG] Siril Python environment detected. >> "%LOG_FILE%"
    echo [LOG] Checking library dependencies...
    "%SIRIL_PY%" -m pip install -r "%~dp0requirements.txt" --quiet 2>> "%LOG_FILE%"
    
    echo [LOG] Launching Core Script Matrix...
    "%SIRIL_PY%" "%~dp0src\main.py" 2>> "%LOG_FILE%"
) ELSE (
    echo [LOG] Siril environment missing. Using standard system path... >> "%LOG_FILE%"
    echo [LOG] Checking library dependencies...
    python -m pip install -r "%~dp0requirements.txt" --quiet 2>> "%LOG_FILE%"
    
    echo [LOG] Launching Core Script Matrix...
    python "%~dp0src\main.py" 2>> "%LOG_FILE%"
)

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ PIPELINE CRASH DETECTED!
    echo An error occurred. The full tracking report has been saved to:
    echo ============================================================
    echo %LOG_FILE%
    echo ============================================================
    echo.
    pause
)
