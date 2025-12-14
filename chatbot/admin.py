from django.contrib import admin
from .models import Document, Chat, Message


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'file_type', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['title']


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['name', 'document', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['chat', 'role', 'content_preview', 'created_at']
    list_filter = ['role', 'created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
