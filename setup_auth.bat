@echo off
echo ========================================
echo Kattral AI - Authentication Setup
echo ========================================
echo.

echo Step 1: Running database migrations...
python manage.py migrate
echo.

echo Step 2: Creating Site object for allauth...
python manage.py shell -c "from django.contrib.sites.models import Site; Site.objects.update_or_create(id=1, defaults={'domain': '127.0.0.1:8000', 'name': 'Kattral AI'}); print('Site created successfully!')"
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start the server: python manage.py runserver
echo 2. Visit: http://127.0.0.1:8000/
echo 3. You should see the guest header with Sign In/Sign Up buttons
echo 4. Create an account or sign in with Google
echo.
echo Note: For Google OAuth to work, you need to configure it in Django admin:
echo - Go to http://127.0.0.1:8000/admin/
echo - Navigate to Social applications
echo - Add Google OAuth app with your credentials
echo.
pause
