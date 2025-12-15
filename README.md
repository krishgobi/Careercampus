# கற்றல் AI (Kattral AI) - Smart Learning Platform

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Kattral AI** is an intelligent learning platform designed specifically for college students, featuring AI-powered chatbot, quiz generation, question paper generation/prediction, and comprehensive learning analytics.

---

## 🌟 Key Features

### 1. **AI Chatbot** 🤖
- Multi-model support (7 AI models: Gemini, Llama, Mixtral, Gemma, DistilGPT2)
- RAG-based contextual responses from uploaded documents
- Voice input and text-to-speech output
- Chat history with rename, export (PDF), and delete options
- Real-time document-aware conversations

### 2. **Quiz Generation** 📝
- Generate quizzes from uploaded documents
- Customizable question count
- Instant feedback with AI explanations
- Learning track for wrong answers
- Quiz analytics with performance charts

### 3. **Question Paper Generation** 📄
- **Important Questions:** Generate from document content
- **Prediction:** Predict questions from previous year papers
- Customizable mark distribution (2, 5, 10, 15 marks)
- Learn mode with AI-powered explanations
- Export to PDF

### 4. **Quiz Analytics** 📊
- Performance tracking with Chart.js visualizations
- Score distribution (doughnut chart)
- Performance timeline (line chart)
- Detailed quiz history table
- Pass/fail statistics

### 5. **AI Models Page** 🎯
- View all available AI models
- 5-star review system
- Model feedback and ratings
- Performance comparisons

### 6. **User Profile** 👤
- Activity tracking
- Quiz history
- Document management
- Profile customization

---

## 🛠️ Tech Stack

### **Frontend**
- HTML5, CSS3 (Grid, Flexbox, Animations)
- Vanilla JavaScript (ES6+)
- Chart.js (Analytics visualization)
- Web Speech API (Voice input/output)
- Font Awesome (Icons)

### **Backend**
- Python 3.8+
- Django 5.0 (MVT architecture)
- SQLite (Database)
- Django Allauth (Authentication)

### **AI/ML**
- **Groq API** - Fast LLM inference (Llama 3.1, 3.2, 3.3, Mixtral, Gemma)
- **Google Gemini API** - Advanced AI (Gemini 2.5 Flash)
- **DistilGPT2** - Local lightweight model (Hugging Face)
- **Sentence Transformers** - Text embeddings (all-MiniLM-L6-v2)
- **FAISS** - Vector similarity search

### **Document Processing**
- PyPDF2 (PDF extraction)
- python-docx (Word documents)
- python-pptx (PowerPoint)
- ReportLab (PDF generation)

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (optional)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd antigravity
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_django_secret_key_here
```

**Get API Keys:**
- Groq: https://console.groq.com/
- Gemini: https://makersuite.google.com/app/apikey

### Step 4: Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Load AI Models (Optional)
```bash
python manage.py loaddata chatbot/fixtures/ai_models.json
```

### Step 6: Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### Step 7: Start Development Server
```bash
python manage.py runserver
```

### Step 8: Access Application
- **Main App:** http://localhost:8000/
- **Admin Panel:** http://localhost:8000/admin/

---

## 🚀 Quick Start Guide

### Upload Documents
1. Navigate to the chat page
2. Click "Upload Document" button
3. Drag & drop or browse files (PDF, DOCX, PPTX)
4. Wait for processing (embeddings generation)

### Chat with AI
1. Select a document from dropdown
2. Choose an AI model
3. Type your question or use voice input
4. Get AI-powered responses based on document content

### Generate Quiz
1. Click "Quiz" button
2. Choose "Existing Documents" or "Upload New"
3. Select document and specify question count
4. Take quiz and get instant feedback
5. Review wrong answers with explanations

### Generate Question Paper
1. Navigate to "Question Papers"
2. Choose "Important Questions" or "Predict Paper"
3. Upload document/previous papers
4. Specify requirements (e.g., "2 two-marks, 5 five-marks")
5. Generate and export to PDF

### View Analytics
1. Navigate to "Quiz Analytics"
2. View performance statistics
3. Analyze score distribution chart
4. Track performance timeline
5. Review detailed quiz history

---

## 🔧 Advanced Features

### **RAG (Retrieval-Augmented Generation)**
Two implementations:
1. **API-based (Gemini):** Cloud embeddings for high accuracy
2. **Local (DistilGPT2):** On-device processing for privacy

**How it works:**
1. Document → Text extraction
2. Text → Chunks (500 chars, 50 overlap)
3. Chunks → Embeddings (768-dimensional vectors)
4. Embeddings → FAISS index
5. Query → Similar chunks retrieval
6. Chunks + Query → LLM → Contextual answer

### **Drag & Drop Implementation**
Custom JavaScript class handling:
- File validation
- Visual feedback (drag-over states)
- Multiple file support
- Progress indication
- Error handling

### **Question Prediction Algorithm**
1. Parse previous year papers
2. Extract all questions
3. Identify patterns and frequency
4. Use AI to predict likely questions
5. Rank by probability
6. Select top questions matching requirements

---

## 📁 Project Structure

```
antigravity/
├── chatbot/                    # Main Django app
│   ├── models.py              # Database models
│   ├── views.py               # View functions
│   ├── urls.py                # URL routing
│   ├── rag_service.py         # RAG implementation
│   ├── question_generator.py  # Question generation
│   ├── quiz_views.py          # Quiz & analytics
│   ├── question_paper_views.py # Question papers
│   ├── profile_views.py       # User profiles
│   ├── static/
│   │   ├── css/               # Stylesheets
│   │   │   ├── chatbot.css
│   │   │   ├── quiz-styles.css
│   │   │   ├── analytics.css
│   │   │   └── drag-drop.css
│   │   └── js/                # JavaScript files
│   │       ├── chatbot.js
│   │       ├── quiz.js
│   │       └── drag-drop.js
│   └── templates/             # HTML templates
│       ├── base.html
│       ├── chatbot.html
│       ├── quiz_analytics.html
│       ├── question_paper.html
│       └── learn_mode.html
├── campus_assistant/          # Django project settings
├── media/                     # Uploaded files
│   └── documents/
├── requirements.txt           # Python dependencies
├── manage.py                  # Django CLI
├── .env                       # Environment variables
└── README.md                  # This file
```

---

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for LLM inference | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode (True/False) | No |

---

## 📊 Database Models

### **Core Models**
- `AIModel` - AI model configurations
- `Document` - Uploaded documents
- `Chat` - Chat sessions
- `Message` - Chat messages
- `Quiz` - Quiz instances
- `QuizQuestion` - Quiz questions
- `QuestionPaper` - Generated question papers
- `LearningItem` - Learning track items
- `ModelFeedback` - User reviews

---

## 🎨 UI/UX Features

- **Responsive Design** - Works on desktop, tablet, mobile
- **Dark Mode Ready** - Modern color schemes
- **Glassmorphism** - Frosted glass effects
- **Smooth Animations** - CSS transitions
- **Drag & Drop** - Intuitive file uploads
- **Voice Interface** - Hands-free interaction
- **Real-time Feedback** - Instant responses

---

## 🔒 Security Features

- CSRF protection on all forms
- Environment variables for secrets
- File type validation
- SQL injection prevention (Django ORM)
- XSS protection in templates
- Secure password hashing
- Session management

---

## 🐛 Troubleshooting

### Common Issues

**1. ModuleNotFoundError**
```bash
pip install -r requirements.txt
```

**2. API Key Errors**
- Check `.env` file exists
- Verify API keys are valid
- Ensure no extra spaces

**3. Database Errors**
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
```

**4. Static Files Not Loading**
```bash
python manage.py collectstatic
```

**5. FAISS Installation Issues**
```bash
# Use CPU version
pip install faiss-cpu
```

---

## 📈 Performance Tips

- First document upload takes longer (embedding generation)
- Use local models (DistilGPT2) for faster responses
- Keep documents under 10MB for optimal performance
- Clear old chat sessions periodically
- Use FAISS indexing for large document collections

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📝 License

This project is licensed under the MIT License.

---

## 👥 Authors

- **Your Name** - Initial work

---

## 🙏 Acknowledgments

- Groq for fast LLM inference
- Google for Gemini API
- Hugging Face for transformers
- Facebook for FAISS
- Django community
- Chart.js team

---

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Contact: your.email@example.com

---

## 🔄 Version History

- **v1.0.0** - Initial release
  - AI Chatbot with RAG
  - Quiz generation
  - Question paper generation/prediction
  - Analytics dashboard
  - Multi-model support

---

**Made with ❤️ for students by students**
