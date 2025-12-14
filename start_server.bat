@echo off
echo Testing Django server startup...
echo.
python manage.py check
echo.
echo If no errors above, starting server...
python manage.py runserver
