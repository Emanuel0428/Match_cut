@echo off
REM Start script for Match Cut application in production mode on Windows

echo Starting Match Cut application in production mode...

REM Check if Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.8 or higher.
    pause
    exit /b
)

REM Check if virtual environment exists, create if not
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Check if gunicorn is installed
pip show gunicorn >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing gunicorn...
    pip install gunicorn
)

REM Start the application in production mode
echo Starting Match Cut application in production mode with Gunicorn...
gunicorn -c gunicorn_config.py app:app

REM Keep the window open if there's an error
if %errorlevel% neq 0 (
    echo Application exited with error code %errorlevel%
    pause
)
