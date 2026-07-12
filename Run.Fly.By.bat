@echo off
cd /d "%~dp0"

SET "LOG_FILE=%~dp0crash_log.txt"
SET "SIRIL_PY=%LocalAppData%\siril\venv\Scripts\python.exe"

echo === ASTROFOTOFLYBY SYSTEM RUN LOG === > "%LOG_FILE%"

:: SMART PATH SEARCH: Find main.py whether it is in src/ or double-nested src/src/
SET "MAIN_PATH="
IF EXIST "%~dp0src\main.py" SET "MAIN_PATH=%~dp0src\main.py"
IF EXIST "%~dp0src\src\main.py" SET "MAIN_PATH=%~dp0src\src\main.py"

IF "%MAIN_PATH%"=="" (
    echo [ERROR] Could not find main.py inside src/ or src/src/. >> "%LOG_FILE%"
    echo ❌ ERROR: main.py is missing from your src directory structure!
    pause
    exit /b
)

IF EXIST "%SIRIL_PY%" (
    echo [LOG] Initializing local Siril Python environment pipeline...
    "%SIRIL_PY%" -m pip install -r "%~dp0requirements.txt" --quiet 2>> "%LOG_FILE%"
    
    echo [LOG] Launching Core Script Matrix...
    "%SIRIL_PY%" "%MAIN_PATH%" 2>> "%LOG_FILE%"
) ELSE (
    echo [LOG] Siril core not located. Using system global PATH...
    python -m pip install -r "%~dp0requirements.txt" --quiet 2>> "%LOG_FILE%"
    
    echo [LOG] Launching Core Script Matrix...
    python "%MAIN_PATH%" 2>> "%LOG_FILE%"
)

echo.
echo ============================================================
echo   Pipeline thread halted. Execution tracking completed.
echo   Check 'crash_log.txt' if script errors occurred.
echo ============================================================
echo.
pause
