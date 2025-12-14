# Smart Campus Assistant - Quick Start Guide

## Prerequisites
- Python 3.8+ installed
- pip package manager

## Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Admin User (Optional)
```bash
python manage.py createsuperuser
```

### 4. Start the Server
```bash
python manage.py runserver
```

### 5. Access the Application
Open your browser and navigate to:
- **Main Application**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/

## Usage

### Upload Documents
1. Navigate to the home page
2. Drag & drop or click to browse files (PDF, DOCX, PPTX)
3. Click "Upload Files" button
4. Wait for processing to complete

### Chat with AI
1. Click "AI Chatbot" in the sidebar
2. Select a document from the dropdown
3. Type your question and press Enter
4. AI will respond based on document content

### Manage Chats
- **Rename**: Click edit icon next to chat
- **Download PDF**: Click download icon
- **Delete**: Click trash icon

## Troubleshooting

### ModuleNotFoundError
- Run: `pip install -r requirements.txt`

### API Key Errors
- Check `.env` file contains valid API keys
- Ensure `python-dotenv` is installed

### Database Errors
- Delete `db.sqlite3` and run migrations again:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

### Static Files Not Loading
- Run: `python manage.py collectstatic`

## API Keys
Your API keys are configured in `.env`:
- Groq API (for LLM responses)
- Gemini API (for embeddings)

## Notes
- First document upload may take longer (embedding generation)
- Internet required for API calls
- Keep chat sessions short for better performance
