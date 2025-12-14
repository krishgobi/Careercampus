@echo off
REM Start server with virtual environment

echo Starting Kattral AI Server...
echo.

REM Check if virtual environment exists
if not exist .venv (
    echo [ERROR] Virtual environment not found!
    echo Please run setup_venv.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found!
    echo Please copy .env.example to .env and configure your API keys
    pause
)

REM Start Django server
echo Starting Django development server...
echo Server will be available at: http://127.0.0.1:8000/
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver
