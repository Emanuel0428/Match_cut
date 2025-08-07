@echo off
REM Start script for Match Cut application on Windows

echo Starting Match Cut application...

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

REM Start the application in development mode
echo Starting Match Cut application in development mode...
python app.py

REM Keep the window open if there's an error
if %errorlevel% neq 0 (
    echo Application exited with error code %errorlevel%
    pause
)
