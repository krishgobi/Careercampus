@echo off
echo ========================================
echo Question Paper System - Complete Setup
echo ========================================
echo.

echo Step 1: Running Database Migrations...
echo.
python manage.py makemigrations chatbot
echo.
python manage.py migrate chatbot
echo.

echo Step 2: Testing Natural Language Parser...
echo.
python -c "from chatbot.nl_parser import parse_question_requirements, validate_requirements; req = parse_question_requirements('10 two mark questions, 5 five mark questions'); print('Parsed:', req); valid, msg = validate_requirements(req); print('Valid:', valid, msg)"
echo.

echo Step 3: Checking Database Tables...
echo.
python manage.py dbshell < check_qp_tables.sql 2>nul || echo Database check skipped
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Start server: python manage.py runserver
echo 2. Visit: http://127.0.0.1:8000/question-paper/
echo 3. Test with: "10 two mark questions, 5 five mark questions"
echo.
pause
