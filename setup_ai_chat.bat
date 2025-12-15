@echo off
echo ========================================
echo Setup AI Chat System
echo ========================================
echo.

echo Step 1: Loading AI Models into Database...
python manage.py loaddata chatbot\fixtures\ai_models.json
echo.

echo Step 2: Verifying Models...
python manage.py shell -c "from chatbot.models import AIModel; print(f'Active models: {AIModel.objects.filter(is_active=True).count()}'); [print(f'  - {m.name}') for m in AIModel.objects.filter(is_active=True)]"
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo AI Chat is now ready to use!
echo Models available:
echo - Llama 3.1 8B (fast)
echo - Llama 3.3 70B (powerful)
echo - Gemini 2.0 Flash (multimodal)
echo - Mixtral 8x7B (large context)
echo.
pause
