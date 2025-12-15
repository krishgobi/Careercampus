import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_assistant.settings')
django.setup()

from chatbot.models import QuestionPaper, Document, Chat, Quiz, LearningItem

print("\n" + "="*60)
print("DATABASE CONTENT CHECK")
print("="*60)

# Check each model
models_data = {
    'Question Papers': QuestionPaper.objects.all(),
    'Documents': Document.objects.all(),
    'Chats': Chat.objects.all(),
    'Quizzes': Quiz.objects.all(),
    'Learning Items': LearningItem.objects.all(),
}

for name, queryset in models_data.items():
    count = queryset.count()
    print(f"\n{name}: {count}")
    if count > 0:
        print(f"  First 3 items:")
        for item in queryset[:3]:
            print(f"  - {item}")

print("\n" + "="*60)
print("CONCLUSION:")
if all(qs.count() == 0 for qs in models_data.values()):
    print("❌ DATABASE IS EMPTY - You need to create some data first!")
    print("\nSuggestions:")
    print("1. Generate a question paper")
    print("2. Upload documents")
    print("3. Have chat conversations")
else:
    print("✅ Database has data - Backend should be working")
print("="*60 + "\n")
