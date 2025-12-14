from django.db import models
from django.contrib.auth.models import User


class Document(models.Model):
    """Model for uploaded documents"""
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    file_type = models.CharField(max_length=10)  # pdf, docx, pptx
    uploaded_at = models.DateTimeField(auto_now_add=True)
    text_content = models.TextField(blank=True)  # Extracted text
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title


class Chat(models.Model):
    """Model for chat sessions"""
    name = models.CharField(max_length=255, default="New Chat")
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True)
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
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
