from chatbot.models import QuestionPaper, Document, Chat, Quiz, LearningItem

print("=== DATABASE CHECK ===")
print(f"Total Question Papers: {QuestionPaper.objects.count()}")
print(f"Total Documents: {Document.objects.count()}")
print(f"Total Chats: {Chat.objects.count()}")
print(f"Total Quizzes: {Quiz.objects.count()}")
print(f"Total Learning Items: {LearningItem.objects.count()}")

print("\n=== RECENT PAPERS ===")
for paper in QuestionPaper.objects.all()[:5]:
    print(f"- {paper.title} ({paper.subject}) - {paper.user_email}")

print("\n=== RECENT DOCUMENTS ===")
for doc in Document.objects.all()[:5]:
    print(f"- {doc.title} ({doc.file_type})")

print("\n=== RECENT CHATS ===")
for chat in Chat.objects.all()[:5]:
    print(f"- {chat.name}")
