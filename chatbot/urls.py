from django.urls import path
from . import views
from . import quiz_views
from . import question_paper_views

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chat_interface, name='chat'),
    path('models/', views.models_page, name='models'),
    
    # API endpoints
    path('api/upload/', views.upload_documents, name='upload_documents'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/chats/', views.get_chats, name='get_chats'),
    path('api/chat/<int:chat_id>/messages/', views.get_chat_messages, name='get_chat_messages'),
    path('api/chat/<int:chat_id>/export/', views.export_chat_pdf, name='export_chat_pdf'),
    path('api/chat/rename/', views.rename_chat, name='rename_chat'),
    path('api/chat/delete/', views.delete_chat, name='delete_chat'),
    path('api/documents/', views.get_documents, name='get_documents'),
    
    # Multi-model endpoints
    path('api/models/', views.list_models, name='list_models'),
    path('api/feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('api/feedback/models/', views.get_model_feedback, name='get_model_feedback'),
    
    # Quiz endpoints
    path('api/quiz/generate/', quiz_views.generate_quiz, name='generate_quiz'),
    path('api/quiz/<int:quiz_id>/submit/', quiz_views.submit_quiz_answer, name='submit_quiz_answer'),
    path('api/quiz/<int:quiz_id>/complete/', quiz_views.complete_quiz, name='complete_quiz'),
    
    # Learning Track endpoints
    path('api/learning/', quiz_views.get_learning_items, name='get_learning_items'),
    path('api/learning/add/', quiz_views.add_to_learning, name='add_to_learning'),
    path('api/learning/<int:item_id>/learned/', quiz_views.mark_learned, name='mark_learned'),
    path('api/learning/export/pdf/', quiz_views.export_learning_pdf, name='export_learning_pdf'),
    path('api/learning/send-email/', quiz_views.send_learning_email, name='send_learning_email'),
    
    # Teaching Mode
    path('api/teach/', quiz_views.teach_topic, name='teach_topic'),
    
    # Enhanced Quiz endpoints (RAG-based)
    path('api/quiz/extract-headings/', quiz_views.extract_headings, name='extract_headings'),
    path('api/quiz/generate-from-headings/', quiz_views.generate_quiz_from_headings_api, name='generate_quiz_from_headings'),
    path('api/quiz/submit-instant/', quiz_views.submit_quiz_instant, name='submit_quiz_instant'),
    
    # Question Paper endpoints
    path('question-paper/', question_paper_views.question_paper_home, name='question_paper'),
    path('api/question-paper/generate/', question_paper_views.generate_important_questions, name='generate_important_questions'),
    path('api/question-paper/predict/', question_paper_views.predict_questions, name='predict_questions'),
    path('api/question-paper/<int:paper_id>/export/', question_paper_views.export_pdf, name='export_question_paper'),
    path('question-paper/<int:paper_id>/', question_paper_views.view_paper, name='view_paper'),
]

