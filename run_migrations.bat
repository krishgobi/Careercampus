@echo off
echo Running migrations for Question Paper feature...
python manage.py makemigrations
python manage.py migrate
echo.
echo Migrations complete!
pause
