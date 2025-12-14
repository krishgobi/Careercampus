@echo off
echo ====================================
echo Smart Campus Assistant Setup
echo ====================================
echo.

echo Step 1: Installing dependencies...
pip install -r requirements.txt
echo.

echo Step 2: Running migrations...
python manage.py makemigrations
python manage.py migrate
echo.

echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo To start the server, run:
echo     python manage.py runserver
echo.
echo Then open http://localhost:8000 in your browser
echo.
pause
