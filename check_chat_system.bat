@echo off
echo ========================================
echo AI Chat System Diagnostic
echo ========================================
echo.

echo [1/3] Checking AI Models in Database...
python manage.py shell -c "from chatbot.models import AIModel; models = AIModel.objects.filter(is_active=True); print(f'Active models: {models.count()}'); [print(f'  - {m.name} ({m.provider}): {m.model_id}') for m in models]; print(); print('If no models shown, run: python manage.py loaddata chatbot/fixtures/ai_models.json')"
echo.

echo [2/3] Checking Documents...
python manage.py shell -c "from chatbot.models import Document; docs = Document.objects.all(); print(f'Total documents: {docs.count()}'); [print(f'  - {d.title}') for d in docs[:5]]"
echo.

echo [3/3] Testing Chat API...
echo Visit: http://127.0.0.1:8000/chatbot/
echo Upload a document and try chatting
echo.

pause
