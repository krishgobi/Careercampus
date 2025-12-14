from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg
import json
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

from .models import Document, Chat, Message, AIModel, ModelUsage, ModelFeedback, Quiz, QuizQuestion, LearningItem
from .utils import (
    extract_text_from_file,
    chunk_text,
    create_vector_store,
    process_query,
    generate_answer
)
from .quiz_utils import generate_quiz_questions, evaluate_answer


def home(request):
    """Render home page with document upload"""
    documents = Document.objects.all()
    return render(request, 'home.html', {'documents': documents})


@csrf_exempt
@require_http_methods(["POST"])
def upload_documents(request):
    """Handle multiple document uploads"""
    import traceback
    try:
        print("[DEBUG] Upload request received")
        files = request.FILES.getlist('files')
        print(f"[DEBUG] Number of files: {len(files)}")
        uploaded_docs = []
        
        for idx, file in enumerate(files):
            print(f"[DEBUG] Processing file {idx + 1}/{len(files)}: {file.name}")
            
            # Determine file type
            file_extension = file.name.split('.')[-1].lower()
            print(f"[DEBUG] File extension: {file_extension}")
            
            if file_extension not in ['pdf', 'docx', 'pptx']:
                print(f"[WARNING] Skipping unsupported file type: {file_extension}")
                continue
            
            # Save document
            print(f"[DEBUG] Creating document record in database...")
            document = Document.objects.create(
                title=file.name,
                file=file,
                file_type=file_extension
            )
            print(f"[DEBUG] Document created with ID: {document.id}")
            
            # Extract text
            file_path = document.file.path
            print(f"[DEBUG] File saved to: {file_path}")
            print(f"[DEBUG] Extracting text from {file_extension} file...")
            
            text_content = extract_text_from_file(file_path, file_extension)
            print(f"[DEBUG] Extracted {len(text_content)} characters of text")
            
            document.text_content = text_content
            document.save()
            print(f"[DEBUG] Document text content saved")
            
            # Create vector store
            print(f"[DEBUG] Chunking text...")
            chunks = chunk_text(text_content)
            print(f"[DEBUG] Created {len(chunks)} chunks")
            
            print(f"[DEBUG] Creating vector store...")
            create_vector_store(document.id, chunks)
            print(f"[DEBUG] Vector store created successfully")
            
            uploaded_docs.append({
                'id': document.id,
                'title': document.title,
                'file_type': document.file_type,
                'uploaded_at': document.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
            })
            print(f"[DEBUG] File {idx + 1} processed successfully")
        
        print(f"[DEBUG] All files processed. Total uploaded: {len(uploaded_docs)}")
        return JsonResponse({
            'status': 'success',
            'documents': uploaded_docs
        })
    
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"[ERROR] Upload failed with exception:")
        print(error_trace)
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'traceback': error_trace
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
    """Handle chat messages with RAG and model selection"""
    try:
        data = json.loads(request.body)
        query = data.get('message')
        document_id = data.get('document_id')
        chat_id = data.get('chat_id')
        model_id = data.get('model_id', 'llama-3.1-8b-instant')  # Default model
        
        if not query or not document_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing message or document_id'
            }, status=400)
        
        # Get model instance
        try:
            ai_model = AIModel.objects.get(model_id=model_id, is_active=True)
        except AIModel.DoesNotExist:
            ai_model = AIModel.objects.get(model_id='llama-3.1-8b-instant')  # Fallback
        
        # Get or create chat
        if chat_id:
            chat = get_object_or_404(Chat, id=chat_id)
            # Update selected model if different
            if chat.selected_model != ai_model:
                chat.selected_model = ai_model
                chat.save()
        else:
            document = get_object_or_404(Document, id=document_id)
            chat = Chat.objects.create(
                name=f"Chat about {document.title}",
                document=document,
                selected_model=ai_model
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
        
        # Track model usage
        session_key = request.session.session_key or 'default'
        usage, created = ModelUsage.objects.get_or_create(
            session_key=session_key,
            model=ai_model
        )
        usage.prompt_count += 1
        usage.save()
        
        # Check if feedback is needed (every 10 prompts after last feedback)
        need_feedback = (usage.prompt_count - usage.last_feedback_at) >= 10
        
        # Process query with RAG (pass model_id)
        from .utils import generate_answer, retrieve_relevant_chunks
        chunks = retrieve_relevant_chunks(query, document_id)
        context = "\n\n".join(chunks)
        answer = generate_answer(query, context, model_id=model_id, chat_history=chat_history[:-1])
        
        # Save assistant message
        Message.objects.create(
            chat=chat,
            role='assistant',
            content=answer,
            model_used=ai_model
        )
        
        return JsonResponse({
            'status': 'success',
            'chat_id': chat.id,
            'answer': answer,
            'prompt_count': usage.prompt_count,
            'need_feedback': need_feedback
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
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


@require_http_methods(["GET"])
def list_models(request):
    """Get all available AI models"""
    models = AIModel.objects.filter(is_active=True)
    model_list = [
        {
            'id': model.id,
            'name': model.name,
            'model_id': model.model_id,
            'provider': model.provider,
            'description': model.description,
            'use_cases': model.use_cases.split(',') if model.use_cases else [],
            'strength': model.strength
        }
        for model in models
    ]
    return JsonResponse({'models': model_list})


@csrf_exempt
@require_http_methods(["POST"])
def submit_feedback(request):
    """Submit feedback for a model"""
    try:
        data = json.loads(request.body)
        model_id = data.get('model_id')
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if not model_id or not rating:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing model_id or rating'
            }, status=400)
        
        # Get model
        ai_model = get_object_or_404(AIModel, model_id=model_id)
        
        # Create feedback
        session_key = request.session.session_key or 'default'
        feedback = ModelFeedback.objects.create(
            model=ai_model,
            rating=rating,
            comment=comment,
            session_key=session_key
        )
        
        # Update last_feedback_at in ModelUsage
        try:
            usage = ModelUsage.objects.get(session_key=session_key, model=ai_model)
            usage.last_feedback_at = usage.prompt_count
            usage.save()
        except ModelUsage.DoesNotExist:
            pass
        
        return JsonResponse({
            'status': 'success',
            'message': 'Feedback submitted successfully'
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_model_feedback(request):
    """Get feedback for all models (for models page)"""
    models = AIModel.objects.filter(is_active=True)
    models_data = []
    
    for model in models:
        feedback_list = model.feedback.all()[:10]  # Latest 10 feedback
        avg_rating = model.feedback.aggregate(Avg('rating'))['rating__avg'] or 0
        
        models_data.append({
            'id': model.id,
            'name': model.name,
            'model_id': model.model_id,
            'provider': model.provider,
            'description': model.description,
            'use_cases': model.use_cases.split(',') if model.use_cases else [],
            'strength': model.strength,
            'avg_rating': round(avg_rating, 1),
            'feedback_count': model.feedback.count(),
            'recent_feedback': [
                {
                    'rating': fb.rating,
                    'comment': fb.comment,
                    'created_at': fb.created_at.strftime('%Y-%m-%d %H:%M')
                }
                for fb in feedback_list
            ]
        })
    
    return JsonResponse({'models': models_data})


def models_page(request):
    """Render models page with feedback"""
    return render(request, 'models.html')
