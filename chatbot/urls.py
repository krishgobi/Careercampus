from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chat_interface, name='chat_interface'),
    path('api/upload/', views.upload_documents, name='upload_documents'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/chats/', views.get_chats, name='get_chats'),
    path('api/chat/rename/', views.rename_chat, name='rename_chat'),
    path('api/chat/<int:chat_id>/messages/', views.get_chat_messages, name='get_chat_messages'),
    path('api/chat/<int:chat_id>/export/', views.export_chat_pdf, name='export_chat_pdf'),
    path('api/chat/delete/', views.delete_chat, name='delete_chat'),
    path('api/documents/', views.get_documents, name='get_documents'),
]
