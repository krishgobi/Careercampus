# Virtual Environment Setup Guide for Kattral AI

## Quick Start

### Windows

1. **Create and setup virtual environment:**
   ```bash
   setup_venv.bat
   ```

2. **Configure environment variables:**
   ```bash
   copy .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the server:**
   ```bash
   start_server_venv.bat
   ```

### Manual Setup (All Platforms)

#### 1. Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials:
# - GEMINI_API_KEY
# - GROQ_API_KEY
# - SMTP credentials
```

#### 4. Setup Database

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 5. (Optional) Populate Models

```bash
python manage.py populate_models
```

#### 6. Run Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

---

## Virtual Environment Commands

### Activate

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### Deactivate

```bash
deactivate
```

### Check Active Environment

```bash
which python  # Linux/Mac
where python  # Windows
```

---

## Project Structure with .venv

```
p:\antigravity\
├── .venv/                    # Virtual environment (gitignored)
│   ├── Scripts/              # Windows executables
│   ├── Lib/                  # Installed packages
│   └── pyvenv.cfg
│
├── chatbot/                  # Main application
├── campus_assistant/         # Django project
├── media/                    # Uploaded files
├── .env                      # Environment variables (gitignored)
├── .env.example              # Example env file
├── requirements.txt          # Python dependencies
├── manage.py                 # Django management
├── setup_venv.bat            # Setup script
└── start_server_venv.bat     # Start script
```

---

## Troubleshooting

### Issue: "python: command not found"

**Solution:** Install Python 3.8+ from https://www.python.org/

### Issue: "pip: command not found"

**Solution:**
```bash
python -m ensurepip --upgrade
```

### Issue: Permission denied (Linux/Mac)

**Solution:**
```bash
chmod +x setup_venv.sh
```

### Issue: Module not found after activation

**Solution:**
```bash
# Ensure venv is activated (you should see (.venv) in prompt)
pip install -r requirements.txt
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use different port
python manage.py runserver 8001
```

---

## Benefits of .venv

✅ **Isolated Dependencies** - No conflicts with system Python  
✅ **Reproducible** - Same packages across all environments  
✅ **Clean** - Easy to delete and recreate  
✅ **Portable** - Works on any platform  
✅ **Safe** - Doesn't affect system Python

---

## Updating Dependencies

### Add New Package

```bash
# Activate venv first
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Update All Packages

```bash
pip install --upgrade -r requirements.txt
```

---

## Deployment Considerations

### Production Setup

1. Use `requirements/production.txt` for production-only packages
2. Set `DEBUG=False` in .env
3. Use proper WSGI server (gunicorn, uwsgi)
4. Configure static files serving

### Example Production Requirements

```txt
# requirements/production.txt
-r base.txt
gunicorn==21.2.0
whitenoise==6.6.0
psycopg2-binary==2.9.9  # PostgreSQL
```

---

## Git Configuration

Add to `.gitignore`:

```gitignore
# Virtual Environment
.venv/
venv/
ENV/

# Environment Variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Django
db.sqlite3
media/
staticfiles/
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `setup_venv.bat` | Create venv and install deps |
| `start_server_venv.bat` | Start server with venv |
| `.venv\Scripts\activate` | Activate venv (Windows) |
| `source .venv/bin/activate` | Activate venv (Linux/Mac) |
| `deactivate` | Deactivate venv |
| `pip list` | Show installed packages |
| `pip freeze` | Export dependencies |

---

## Next Steps

1. ✅ Run `setup_venv.bat`
2. ✅ Configure `.env` file
3. ✅ Run `start_server_venv.bat`
4. ✅ Visit http://127.0.0.1:8000/
5. ✅ Start developing!
