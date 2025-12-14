# Quick Start - Smart Campus Assistant

## To Run the Application NOW:

1. Open a NEW Command Prompt
2. Navigate to the project:
   ```
   cd P:\antigravity
   ```

3. Run these commands ONE by ONE:
   ```
   python manage.py makemigrations chatbot
   python manage.py migrate
   python manage.py runserver
   ```

4. Open your browser to: **http://localhost:8000**

## If you get errors:

### "No module named 'django'"
Run: `pip install -r requirements.txt`

### Migration errors
Run:
```
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

### Any other errors
Share the error message and I'll help fix it!

## What to Test:
1. Upload a PDF/DOCX/PPTX file
2. Go to AI Chatbot
3. Select your uploaded document
4. Ask questions about it!
