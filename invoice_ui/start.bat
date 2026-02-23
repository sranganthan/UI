@echo off
REM Batch file to start the Invoice Generation Web UI

echo ========================================
echo Invoice Generation Web UI
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check if requirements are installed
echo Checking dependencies...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not installed with Python
    echo Please install pip or use: python -m ensurepip
    pause
    exit /b 1
)

python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting Flask application...
echo.
echo Access the application at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask application
python app.py

pause
