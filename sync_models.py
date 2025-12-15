"""
Ensure only the 7 models from chat are shown on models page
Run with: python sync_models.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_assistant.settings')
django.setup()

from chatbot.models import AIModel

# Models that should be active (from the uploaded image)
active_models = [
    'gemini-2.5-flash',
    'gemma-7b-it',
    'llama-3.1-8b-instant',
    'llama-3.2-3b-preview',
    'llama-3.3-70b-versatile',
    'mixtral-8x7b-32768',
    'distilgpt2'
]

print("Syncing models...")
print("=" * 50)

# Set all models to inactive first
AIModel.objects.all().update(is_active=False)
print("✓ Set all models to inactive")

# Activate only the 7 models
for model_id in active_models:
    updated = AIModel.objects.filter(model_id=model_id).update(is_active=True)
    if updated:
        print(f"✓ Activated: {model_id}")
    else:
        print(f"✗ Not found: {model_id}")

print("=" * 50)
print("\nActive models:")
for model in AIModel.objects.filter(is_active=True):
    print(f"  - {model.name} ({model.model_id})")

print(f"\nTotal active models: {AIModel.objects.filter(is_active=True).count()}")
