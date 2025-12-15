"""
Delete all documents from database
Run with: python delete_all_documents.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_assistant.settings')
django.setup()

from chatbot.models import Document

# Get count before deletion
count = Document.objects.count()
print(f"Found {count} documents")

# Delete all
Document.objects.all().delete()

print(f"✅ Deleted all {count} documents")
print("Database is now clean for testing!")
