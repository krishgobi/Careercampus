import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_assistant.settings')
django.setup()

from chatbot.models import AIModel

# Check if DistilGPT2 already exists
existing = AIModel.objects.filter(model_id='distilgpt2').first()

if existing:
    print(f"✅ DistilGPT2 already exists: {existing.name}")
else:
    # Create DistilGPT2 model
    distilgpt = AIModel.objects.create(
        name="DistilGPT2 (Local)",
        model_id="distilgpt2",
        provider="local",
        description="Local lightweight GPT-2 model with RAG support",
        use_cases="Document Q&A,Offline usage,Privacy-focused chat",
        strength="Runs locally with document context",
        is_active=True
    )
    print(f"✅ Created DistilGPT2 model: {distilgpt.name}")

# List all models
print("\nAll models in database:")
for model in AIModel.objects.all():
    print(f"  - {model.name} ({model.provider}) - {model.model_id}")
