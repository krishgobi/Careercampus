"""
Quick test script for DistilGPT2 with RAG
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_assistant.settings')
django.setup()

from chatbot.models import AIModel

print("\n" + "="*60)
print("DISTILGPT2 MODEL CHECK")
print("="*60)

# Check if DistilGPT2 is in database
distilgpt = AIModel.objects.filter(model_id='distilgpt2').first()

if distilgpt:
    print(f"\n✅ DistilGPT2 Model Found!")
    print(f"   Name: {distilgpt.name}")
    print(f"   Provider: {distilgpt.provider}")
    print(f"   Active: {distilgpt.is_active}")
    print(f"   Description: {distilgpt.description}")
else:
    print("\n❌ DistilGPT2 not found in database")
    print("   Run: python manage.py loaddata chatbot/fixtures/ai_models.json")

print("\n" + "="*60)
print("ALL MODELS:")
print("="*60)
for model in AIModel.objects.all():
    print(f"- {model.name} ({model.provider})")

print("\n" + "="*60 + "\n")
