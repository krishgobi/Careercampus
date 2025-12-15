"""
User Profile Views
Handles user profile display, editing, and activity tracking
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from datetime import datetime, timedelta
import json

from .models import (
    QuestionPaper, Document, Chat, Quiz, 
    LearningItem, GeneratedQuestion
)


@login_required
def user_profile(request):
    """Display user profile with all activity"""
    user = request.user
    print(f"DEBUG: User - {user.username}, Email - {user.email}")
    
    # SIMPLIFIED: Just query all data for now (until migrations are run)
    # This ensures we see SOMETHING on the profile page
    
    total_question_papers = QuestionPaper.objects.all().count()
    total_documents = Document.objects.all().count()
    total_chats = Chat.objects.all().count()
    total_learning_items = LearningItem.objects.all().count()
    total_quizzes = Quiz.objects.all().count()
    
    print(f"DEBUG: Counts - Papers:{total_question_papers}, Docs:{total_documents}, Chats:{total_chats}")
    
    # Recent activity - last 7 days
    week_ago = datetime.now() - timedelta(days=7)
    
    papers_this_week = QuestionPaper.objects.filter(created_at__gte=week_ago).count()
    important_papers = QuestionPaper.objects.filter(paper_type='important').count()
    predicted_papers = QuestionPaper.objects.filter(paper_type='predicted').count()
    
    # Get recent items for activity feed
    recent_papers = list(QuestionPaper.objects.all().order_by('-created_at')[:10])
    
    # Documents
    recent_documents = []
    docs = Document.objects.all().order_by('-uploaded_at')[:10]
    for doc in docs:
        try:
            doc_dict = {
                'id': doc.id,
                'title': doc.title,
                'file_type': doc.file_type,
                'uploaded_at': doc.uploaded_at,
                'file_size': doc.file.size if doc.file else 0
            }
            recent_documents.append(doc_dict)
        except Exception as e:
            print(f"DEBUG: Error processing document {doc.id}: {e}")
            pass
    
    recent_chats = list(Chat.objects.all().order_by('-updated_at')[:10])
    recent_quizzes = list(Quiz.objects.all().order_by('-created_at')[:10])
    
    # Prepare stats
    stats = {
        'total_question_papers': total_question_papers,
        'total_documents': total_documents,
        'total_chats': total_chats,
        'total_learning_items': total_learning_items,
        'total_quizzes': total_quizzes,
        'papers_this_week': papers_this_week,
        'important_papers': important_papers,
        'predicted_papers': predicted_papers,
    }
    
    # DEBUG: Print all stats
    print(f"\n{'='*50}")
    print(f"PROFILE PAGE STATS:")
    print(f"{'='*50}")
    for key, value in stats.items():
        print(f"{key}: {value}")
    print(f"Recent Papers: {len(list(recent_papers))}")
    print(f"Recent Documents: {len(recent_documents)}")
    print(f"Recent Chats: {len(list(recent_chats))}")
    print(f"Recent Quizzes: {len(list(recent_quizzes))}")
    print(f"{'='*50}\n")
    
    context = {
        'stats': stats,
        'recent_papers': recent_papers,
        'recent_documents': recent_documents,
        'recent_chats': recent_chats,
        'recent_quizzes': recent_quizzes,
    }
    
    return render(request, 'user_profile.html', context)


@csrf_exempt
@login_required
def update_profile(request):
    """Update user profile information"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)
    
    try:
        data = json.loads(request.body)
        user = request.user
        
        # Update name
        if 'first_name' in data:
            user.first_name = data['first_name']
        
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        # Update email
        if 'email' in data:
            user.email = data['email']
        
        user.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Profile updated successfully',
            'user': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
def get_all_activity(request):
    """Get all user activity as JSON for the activity timeline"""
    user = request.user
    activities = []
    
    # Get all papers
    try:
        papers = QuestionPaper.objects.filter(user_email=user.email).order_by('-created_at')
        for paper in papers:
            activities.append({
                'type': 'question_paper',
                'title': paper.title,
                'subject': paper.subject,
                'paper_type': paper.get_paper_type_display(),
                'created_at': paper.created_at.isoformat(),
                'id': paper.id,
            })
    except:
        pass
    
    # Get all documents
    try:
        documents = Document.objects.filter(uploaded_by=user).order_by('-uploaded_at')
        for doc in documents:
            activities.append({
                'type': 'document',
                'title': doc.title,
                'file_type': doc.file_type,
                'created_at': doc.uploaded_at.isoformat(),
                'id': doc.id,
            })
    except:
        pass
    
    # Get all chats
    try:
        chats = Chat.objects.filter(user=user).order_by('-created_at')
        for chat in chats:
            activities.append({
                'type': 'chat',
                'title': chat.name,
                'created_at': chat.created_at.isoformat(),
                'id': chat.id,
            })
    except:
        pass
    
    # Get all quizzes
    try:
        quizzes = Quiz.objects.filter(user=user).order_by('-created_at')
        for quiz in quizzes:
            activities.append({
                'type': 'quiz',
                'title': quiz.topic,
                'score': quiz.score,
                'total': quiz.total_questions,
                'created_at': quiz.created_at.isoformat(),
                'id': quiz.id,
            })
    except:
        pass
    
    # Sort all activities by date
    activities.sort(key=lambda x: x['created_at'], reverse=True)
    
    return JsonResponse({
        'status': 'success',
        'activities': activities,
        'total': len(activities)
    })
