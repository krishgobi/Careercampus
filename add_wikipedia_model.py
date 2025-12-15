"""
Add Wikipedia model to database
Run this with: python add_wikipedia_model.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_assistant.settings')
django.setup()

from chatbot.models import AIModel

# Check if Wikipedia already exists
if AIModel.objects.filter(model_id='wikipedia').exists():
    print("✅ Wikipedia model already exists!")
else:
    # Create Wikipedia model
    wikipedia = AIModel.objects.create(
        name="Wikipedia",
        model_id="wikipedia",
        provider="wikipedia",
        description="Free encyclopedia with millions of articles",
        use_cases="Factual information,General knowledge,Research",
        strength="Reliable factual content",
        is_active=True
    )
    print("✅ Wikipedia model added successfully!")
    print(f"   ID: {wikipedia.id}")
    print(f"   Name: {wikipedia.name}")
    print(f"   Provider: {wikipedia.provider}")

# List all models
print("\n📋 All AI Models:")
for model in AIModel.objects.all():
    print(f"   - {model.name} ({model.provider})")
