import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_assistant.settings')
django.setup()

from chatbot.models import QuestionPaper, Document, Chat, Quiz, LearningItem

print("\n" + "="*70)
print("DIRECT DATABASE CHECK")
print("="*70)

# QuestionPaper
qp_count = QuestionPaper.objects.count()
print(f"\n1. QuestionPaper.objects.count() = {qp_count}")
if qp_count > 0:
    print("   First 3 papers:")
    for paper in QuestionPaper.objects.all()[:3]:
        print(f"   - {paper.id}: {paper.title} | Subject: {paper.subject} | User: {paper.user_email}")

# Document
doc_count = Document.objects.count()
print(f"\n2. Document.objects.count() = {doc_count}")
if doc_count > 0:
    print("   First 3 documents:")
    for doc in Document.objects.all()[:3]:
        print(f"   - {doc.id}: {doc.title} | Type: {doc.file_type}")
        # Check if uploaded_by field exists
        try:
            print(f"      Uploaded by: {doc.uploaded_by}")
        except AttributeError:
            print(f"      Uploaded by: FIELD DOES NOT EXIST")

# Chat
chat_count = Chat.objects.count()
print(f"\n3. Chat.objects.count() = {chat_count}")
if chat_count > 0:
    print("   First 3 chats:")
    for chat in Chat.objects.all()[:3]:
        print(f"   - {chat.id}: {chat.name}")
        # Check if user field exists
        try:
            print(f"      User: {chat.user}")
        except AttributeError:
            print(f"      User: FIELD DOES NOT EXIST")

# Quiz
quiz_count = Quiz.objects.count()
print(f"\n4. Quiz.objects.count() = {quiz_count}")

# LearningItem
learn_count = LearningItem.objects.count()
print(f"\n5. LearningItem.objects.count() = {learn_count}")

print("\n" + "="*70)
print("DIAGNOSIS:")
print("="*70)

if qp_count == 0 and doc_count == 0 and chat_count == 0:
    print("❌ DATABASE IS COMPLETELY EMPTY")
    print("\nYou need to:")
    print("1. Go to /question-paper/ and generate a paper")
    print("2. Go to /chat/ and upload a document")
else:
    print(f"✅ Database has data:")
    print(f"   - {qp_count} question papers")
    print(f"   - {doc_count} documents")
    print(f"   - {chat_count} chats")
    print(f"   - {quiz_count} quizzes")
    print(f"   - {learn_count} learning items")
    
    print("\n⚠️  But profile shows 0s - This means:")
    print("   - The user-specific queries are failing (expected)")
    print("   - The FALLBACK queries are ALSO failing (unexpected)")
    print("\n   Need to check the exception handling in profile_views.py")

print("="*70 + "\n")
