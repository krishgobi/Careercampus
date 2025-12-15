@echo off
echo ========================================
echo Question Paper System Debug Script
echo ========================================
echo.

echo [1/4] Running migrations...
python manage.py makemigrations
python manage.py migrate
echo.

echo [2/4] Checking database tables...
python manage.py dbshell < check_tables.sql
echo.

echo [3/4] Testing natural language parser...
python -c "from chatbot.nl_parser import parse_question_requirements; print('Test 1:', parse_question_requirements('10 two mark questions')); print('Test 2:', parse_question_requirements('5 five mark, 3 ten mark'))"
echo.

echo [4/4] Starting server...
echo Server will start on http://127.0.0.1:8000
echo Navigate to: http://127.0.0.1:8000/question-paper/
echo.
python manage.py runserver
