
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import json

from .models import Quiz, QuizQuestion, LearningItem, Document
from .quiz_utils import generate_quiz_questions, evaluate_answer
from .utils import generate_answer

# ===== Quiz API Endpoints =====


@csrf_exempt
@require_http_methods(["POST"])
def generate_quiz(request):
    """Generate quiz from document or custom prompt"""
    try:
        data = json.loads(request.body)
        source_type = data.get('source_type', 'prompt')
        topic = data.get('topic', '')
        num_questions = int(data.get('num_questions', 10))
        document_id = data.get('document_id')
        
        # Generate questions using AI
        questions_data = generate_quiz_questions(
            topic=topic,
            num_questions=num_questions,
            document_id=document_id,
            source_type=source_type
        )
        
        # Create quiz in database
        session_key = request.session.session_key or 'default'
        doc = None
        if document_id:
            doc = Document.objects.get(id=document_id)
            
        quiz = Quiz.objects.create(
            topic=topic,
            source_type=source_type,
            total_questions=num_questions,
            document=doc,
            session_key=session_key
        )
        
        # Create quiz questions
        for idx, q_data in enumerate(questions_data):
            QuizQuestion.objects.create(
                quiz=quiz,
                question=q_data['question'],
                options=q_data['options'],
                correct_answer=q_data['correct_answer'],
                explanation=q_data.get('explanation', ''),
                order=idx
            )
        
        # Return quiz data
        questions = quiz.questions.all()
        return JsonResponse({
            'status': 'success',
            'quiz': {
                'id': quiz.id,
                'topic': quiz.topic,
                'total_questions': quiz.total_questions
            },
            'questions': [
                {
                    'id': q.id,
                    'question': q.question,
                    'options': q.options,
                    'correct_answer': q.correct_answer,
                    'order': q.order
                }
                for q in questions
            ]
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def submit_quiz_answer(request, quiz_id):
    """Submit answer for a quiz question"""
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        user_answer = data.get('answer', '')
        
        question = get_object_or_404(QuizQuestion, id=question_id, quiz_id=quiz_id)
        
        # Evaluate answer
        is_correct, explanation = evaluate_answer(
            question.question,
            user_answer,
            question.correct_answer
        )
        
        # Update question
        question.user_answer = user_answer
        question.is_correct = is_correct
        if not question.explanation:
            question.explanation = explanation
        question.save()
        
        return JsonResponse({
            'status': 'success',
            'is_correct': is_correct,
            'explanation': question.explanation
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def complete_quiz(request, quiz_id):
    """Mark quiz as complete and calculate score"""
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = quiz.questions.all()
        
        # Calculate score
        correct_count = sum(1 for q in questions if q.is_correct)
        quiz.score = correct_count
        quiz.is_completed = True
        quiz.save()
        
        return JsonResponse({
            'status': 'success',
            'score': correct_count,
            'total_questions': quiz.total_questions,
            'wrong_answers': [
                {
                    'question': q.question,
                    'user_answer': q.user_answer,
                    'correct_answer': q.correct_answer,
                    'explanation': q.explanation
                }
                for q in questions if not q.is_correct
            ]
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# ===== Learning Track API Endpoints =====

@require_http_methods(["GET"])
def get_learning_items(request):
    """Get all learning items for current session"""
    try:
        session_key = request.session.session_key or 'default'
        items = LearningItem.objects.filter(session_key=session_key, is_learned=False)
        
        return JsonResponse({
            'status': 'success',
            'items': [
                {
                    'id': item.id,
                    'topic': item.topic,
                    'question': item.question,
                    'correct_answer': item.correct_answer,
                    'explanation': item.explanation,
                    'user_wrong_answer': item.user_wrong_answer
                }
                for item in items
            ]
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_to_learning(request):
    """Add item to learning track"""
    try:
        data = json.loads(request.body)
        session_key = request.session.session_key or 'default'
        
        quiz_id = data.get('quiz_id')
        quiz = Quiz.objects.get(id=quiz_id) if quiz_id else None
        
        learning_item = LearningItem.objects.create(
            session_key=session_key,
            topic=data.get('topic', ''),
            question=data.get('question', ''),
            correct_answer=data.get('correct_answer', ''),
            explanation=data.get('explanation', ''),
            user_wrong_answer=data.get('user_wrong_answer', ''),
            quiz=quiz
        )
        
        return JsonResponse({
            'status': 'success',
            'item_id': learning_item.id
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def mark_learned(request, item_id):
    """Mark learning item as learned"""
    try:
        item = get_object_or_404(LearningItem, id=item_id)
        item.is_learned = True
        item.save()
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def export_learning_pdf(request):
    """Export learning items as PDF"""
    try:
        session_key = request.session.session_key or 'default'
        items = LearningItem.objects.filter(session_key=session_key)
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        story = []
        story.append(Paragraph("Learning Track - Kattral AI", styles['Title']))
        story.append(Spacer(1, 0.5 * inch))
        
        for item in items:
            story.append(Paragraph(f"<b>Topic:</b> {item.topic}", styles['Heading3']))
            story.append(Paragraph(f"<b>Question:</b> {item.question}", styles['Normal']))
            story.append(Paragraph(f"<b>Correct Answer:</b> {item.correct_answer}", styles['Normal']))
            if item.explanation:
                story.append(Paragraph(f"<b>Explanation:</b> {item.explanation}", styles['Normal']))
            story.append(Spacer(1, 0.3 * inch))
        
        doc.build(story)
        buffer.seek(0)
        
        return FileResponse(buffer, as_attachment=True, filename='learning_track.pdf')
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_learning_email(request):
    """Send learning items via email"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '')
        
        if not email:
            return JsonResponse({
                'status': 'error',
                'message': 'Email address required'
            }, status=400)
        
        session_key = request.session.session_key or 'default'
        items = LearningItem.objects.filter(session_key=session_key)
        
        # Build email content
        content = "Your Learning Track from Kattral AI\n\n"
        content += "=" * 50 + "\n\n"
        
        for item in items:
            content += f"Topic: {item.topic}\n"
            content += f"Question: {item.question}\n"
            content += f"Correct Answer: {item.correct_answer}\n"
            if item.explanation:
                content += f"Explanation: {item.explanation}\n"
            content += "\n" + "-" * 50 + "\n\n"
        
        # Send email
        send_mail(
            subject='Your Learning Track - Kattral AI',
            message=content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# ===== Teaching Mode API =====

@csrf_exempt
@require_http_methods(["POST"])
def teach_topic(request):
    """Teach user about a topic before quiz"""
    try:
        data = json.loads(request.body)
        topic = data.get('topic', '')
        
        if not topic:
            return JsonResponse({
                'status': 'error',
                'message': 'Topic required'
            }, status=400)
        
        # Use Gemini 2.5 Flash to generate teaching content
        teaching_content = generate_answer(
            query=f"Teach me about: {topic}. Provide a comprehensive explanation suitable for learning.",
            context="",
            model_id='gemini-2.5-flash'
        )
        
        # Save to learning track
        session_key = request.session.session_key or 'default'
        learning_item = LearningItem.objects.create(
            session_key=session_key,
            topic=topic,
            question=f"Learning session: {topic}",
            correct_answer=teaching_content[:500],  # Store summary
            explanation=teaching_content
        )
        
        return JsonResponse({
            'status': 'success',
            'teaching_content': teaching_content,
            'learning_item_id': learning_item.id
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
