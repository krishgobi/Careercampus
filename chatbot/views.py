from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
import json
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

from .models import Document, Chat, Message
from .utils import (
    extract_text_from_file,
    chunk_text,
    create_vector_store,
    process_query
)


def home(request):
    """Render home page with document upload"""
    documents = Document.objects.all()
    return render(request, 'home.html', {'documents': documents})


@csrf_exempt
@require_http_methods(["POST"])
def upload_documents(request):
    """Handle multiple document uploads"""
    try:
        files = request.FILES.getlist('files')
        uploaded_docs = []
        
        for file in files:
            # Determine file type
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in ['pdf', 'docx', 'pptx']:
                continue
            
            # Save document
            document = Document.objects.create(
                title=file.name,
                file=file,
                file_type=file_extension
            )
            
            # Extract text
            file_path = document.file.path
            text_content = extract_text_from_file(file_path, file_extension)
            document.text_content = text_content
            document.save()
            
            # Create vector store
            chunks = chunk_text(text_content)
            create_vector_store(document.id, chunks)
            
            uploaded_docs.append({
                'id': document.id,
                'title': document.title,
                'file_type': document.file_type,
                'uploaded_at': document.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'status': 'success',
            'documents': uploaded_docs
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def chat_interface(request):
    """Render chatbot interface"""
    documents = Document.objects.all()
    chats = Chat.objects.all()
    return render(request, 'chatbot.html', {
        'documents': documents,
        'chats': chats
    })


@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """Handle chat messages with RAG"""
    try:
        data = json.loads(request.body)
        query = data.get('message')
        document_id = data.get('document_id')
        chat_id = data.get('chat_id')
        
        if not query or not document_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing message or document_id'
            }, status=400)
        
        # Get or create chat
        if chat_id:
            chat = get_object_or_404(Chat, id=chat_id)
        else:
            document = get_object_or_404(Document, id=document_id)
            chat = Chat.objects.create(
                name=f"Chat about {document.title}",
                document=document
            )
        
        # Save user message
        Message.objects.create(
            chat=chat,
            role='user',
            content=query
        )
        
        # Get chat history
        messages = chat.messages.all()
        chat_history = [
            {'role': msg.role, 'content': msg.content}
            for msg in messages
        ]
        
        # Process query with RAG
        answer = process_query(query, document_id, chat_history[:-1])  # Exclude current query
        
        # Save assistant message
        Message.objects.create(
            chat=chat,
            role='assistant',
            content=answer
        )
        
        return JsonResponse({
            'status': 'success',
            'chat_id': chat.id,
            'answer': answer
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_chats(request):
    """Get all chats"""
    chats = Chat.objects.all()
    chat_list = [
        {
            'id': chat.id,
            'name': chat.name,
            'document_id': chat.document.id if chat.document else None,
            'document_title': chat.document.title if chat.document else None,
            'updated_at': chat.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for chat in chats
    ]
    return JsonResponse({'chats': chat_list})


@csrf_exempt
@require_http_methods(["POST"])
def rename_chat(request):
    """Rename a chat"""
    try:
        data = json.loads(request.body)
        chat_id = data.get('chat_id')
        new_name = data.get('name')
        
        chat = get_object_or_404(Chat, id=chat_id)
        chat.name = new_name
        chat.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Chat renamed successfully'
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_chat_messages(request, chat_id):
    """Get all messages for a chat"""
    chat = get_object_or_404(Chat, id=chat_id)
    messages = chat.messages.all()
    
    message_list = [
        {
            'role': msg.role,
            'content': msg.content,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for msg in messages
    ]
    
    return JsonResponse({
        'chat_id': chat.id,
        'chat_name': chat.name,
        'messages': message_list
    })


@require_http_methods(["GET"])
def export_chat_pdf(request, chat_id):
    """Export chat history as PDF"""
    chat = get_object_or_404(Chat, id=chat_id)
    messages = chat.messages.all()
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    
    # Build PDF content
    story = []
    story.append(Paragraph(f"Chat: {chat.name}", title_style))
    story.append(Spacer(1, 0.2 * inch))
    
    for msg in messages:
        role_text = "You" if msg.role == "user" else "AI Assistant"
        story.append(Paragraph(f"<b>{role_text}:</b>", styles['Heading3']))
        story.append(Paragraph(msg.content, styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
    
    # Generate PDF
    doc.build(story)
    buffer.seek(0)
    
    # Return as download
    response = FileResponse(buffer, as_attachment=True, filename=f'{chat.name}.pdf')
    response['Content-Type'] = 'application/pdf'
    return response


@csrf_exempt
@require_http_methods(["POST"])
def delete_chat(request):
    """Delete a chat"""
    try:
        data = json.loads(request.body)
        chat_id = data.get('chat_id')
        
        chat = get_object_or_404(Chat, id=chat_id)
        chat.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Chat deleted successfully'
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_documents(request):
    """Get all documents"""
    documents = Document.objects.all()
    doc_list = [
        {
            'id': doc.id,
            'title': doc.title,
            'file_type': doc.file_type,
            'uploaded_at': doc.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for doc in documents
    ]
    return JsonResponse({'documents': doc_list})
