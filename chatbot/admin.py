from django.contrib import admin
from .models import Document, Chat, Message, AIModel, ModelUsage, ModelFeedback


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_id', 'provider', 'is_active')
    list_filter = ('provider', 'is_active')
    search_fields = ('name', 'model_id', 'description')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('title',)


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'document', 'selected_model', 'created_at', 'updated_at')
    list_filter = ('created_at', 'selected_model')
    search_fields = ('name',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'role', 'model_used', 'created_at')
    list_filter = ('role', 'model_used', 'created_at')
    search_fields = ('content',)


@admin.register(ModelUsage)
class ModelUsageAdmin(admin.ModelAdmin):
    list_display = ('model', 'session_key', 'prompt_count', 'updated_at')
    list_filter = ('model', 'updated_at')
    search_fields = ('session_key',)


@admin.register(ModelFeedback)
class ModelFeedbackAdmin(admin.ModelAdmin):
    list_display = ('model', 'rating', 'created_at')
    list_filter = ('model', 'rating', 'created_at')
    search_fields = ('comment',)
