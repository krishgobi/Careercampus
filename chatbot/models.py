from django.db import models
from django.contrib.auth.models import User


class AIModel(models.Model):
    """Model for available AI models"""
    PROVIDER_CHOICES = [
        ('gemini', 'Gemini'),
        ('groq', 'Groq'),
        ('gpt', 'OpenAI GPT'),
        ('local', 'Local Model'),
        ('wikipedia', 'Wikipedia'),
    ]
    
    name = models.CharField(max_length=100)  # Display name
    model_id = models.CharField(max_length=100, unique=True)  # API model identifier
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    description = models.TextField()
    use_cases = models.TextField(help_text="Comma-separated use cases")
    strength = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['provider', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.provider})"


class Document(models.Model):
    """Model for uploaded documents"""
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    file_type = models.CharField(max_length=10)  # pdf, docx, pptx
    uploaded_at = models.DateTimeField(auto_now_add=True)
    text_content = models.TextField(blank=True)  # Extracted text
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_documents')
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title


class Chat(models.Model):
    """Model for chat sessions"""
    name = models.CharField(max_length=255, default="New Chat")
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True)
    selected_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Message(models.Model):
    """Model for individual chat messages"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    model_used = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class ModelUsage(models.Model):
    """Track prompt counts per model per session"""
    session_key = models.CharField(max_length=100)
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    prompt_count = models.IntegerField(default=0)
    last_feedback_at = models.IntegerField(default=0, help_text="Prompt count when last feedback was requested")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['session_key', 'model']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.model.name} - {self.prompt_count} prompts"


class ModelFeedback(models.Model):
    """Store user feedback for AI models"""
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True)
    session_key = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.model.name} - {self.rating} stars"


class Quiz(models.Model):
    """Quiz session with questions and answers"""
    SOURCE_CHOICES = [
        ('document', 'Document'),
        ('prompt', 'Prompt'),
    ]
    
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, blank=True, related_name='quizzes')
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True)
    topic = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    total_questions = models.IntegerField(default=10)
    score = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes')
    session_key = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Quiz: {self.topic} ({self.score}/{self.total_questions})"


class QuizQuestion(models.Model):
    """Individual quiz question"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    options = models.JSONField(default=list)  # List of 4 options
    correct_answer = models.CharField(max_length=500)
    user_answer = models.CharField(max_length=500, blank=True)
    is_correct = models.BooleanField(null=True)
    explanation = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question[:50]}..."


class LearningItem(models.Model):
    """Learning track items from quiz mistakes or manual additions"""
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, blank=True, related_name='learning_items')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='learning_items')
    session_key = models.CharField(max_length=100, blank=True)
    topic = models.CharField(max_length=255)
    question = models.TextField()
    correct_answer = models.TextField()
    explanation = models.TextField()
    user_wrong_answer = models.CharField(max_length=500, blank=True)
    is_learned = models.BooleanField(default=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Learn: {self.topic} - {self.question[:30]}..."


class QuestionPaper(models.Model):
    """Generated question paper"""
    PAPER_TYPE_CHOICES = [
        ('important', 'Important Questions'),
        ('predicted', 'Predicted Paper'),
    ]
    
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=100)
    paper_type = models.CharField(max_length=20, choices=PAPER_TYPE_CHOICES)
    source_document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True)
    source_topic = models.TextField(blank=True)
    session_key = models.CharField(max_length=100, blank=True)
    rating = models.IntegerField(null=True, blank=True)  # 1-5 stars
    user_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.subject}"


class GeneratedQuestion(models.Model):
    """Individual question in a question paper"""
    paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    marks = models.IntegerField()
    question_type = models.CharField(max_length=50, blank=True)  # descriptive, short answer, etc.
    answer_hint = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['marks', 'order']
    
    def __str__(self):
        return f"{self.marks} marks: {self.question_text[:50]}..."


class PreviousPaper(models.Model):
    """Uploaded previous year question papers for prediction"""
    subject = models.CharField(max_length=100)
    file = models.FileField(upload_to='previous_papers/')
    year = models.IntegerField(null=True, blank=True)
    text_content = models.TextField(blank=True)  # Extracted text
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-year', '-uploaded_at']
    
    def __str__(self):
        return f"{self.subject} - {self.year or 'Unknown Year'}"

