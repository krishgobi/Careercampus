"""
Views for Question Paper Generation
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import QuestionPaper, GeneratedQuestion, PreviousPaper, Document
from .question_generator import generate_important_questions_ai, predict_questions_from_papers
from .pdf_export import export_question_paper_pdf
from .utils import extract_text_from_file
import json


def question_paper_home(request):
    """Main question paper page"""
    recent_papers = QuestionPaper.objects.all()[:10]
    return render(request, 'question_paper.html', {
        'recent_papers': recent_papers
    })


@csrf_exempt
@require_http_methods(["POST"])
def generate_important_questions(request):
    """Generate important questions from topic or document"""
    try:
        print("[VIEW] Generating important questions...")
        
        # Get form data
        source_type = request.POST.get('source_type')  # 'topic' or 'document'
        subject = request.POST.get('subject', 'General')
        requirements_text = request.POST.get('requirements', '')
        
        print(f"[DEBUG] source_type: {source_type}")
        print(f"[DEBUG] subject: {subject}")
        print(f"[DEBUG] requirements_text: '{requirements_text}'")
        print(f"[DEBUG] POST data: {dict(request.POST)}")
        
        # Parse natural language requirements
        from .nl_parser import parse_question_requirements, validate_requirements
        requirements = parse_question_requirements(requirements_text)
        
        print(f"[DEBUG] Parsed requirements: {requirements}")
        
        # Validate
        is_valid, error_msg = validate_requirements(requirements)
        print(f"[DEBUG] Validation: is_valid={is_valid}, error_msg='{error_msg}'")
        
        if not is_valid:
            return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
        
        marks_list = list(requirements.keys())
        
        # Get content
        if source_type == 'topic':
            topic = request.POST.get('topic', '')
            content = topic
            title = f"Important Questions - {topic[:50]}"
        else:  # document
            file = request.FILES.get('document')
            if not file:
                return JsonResponse({'status': 'error', 'message': 'No document uploaded'}, status=400)
            
            # Save document
            doc = Document.objects.create(
                title=file.name,
                file=file,
                file_type=file.name.split('.')[-1].lower()
            )
            
            # Extract text
            content = extract_text_from_file(doc.file.path, doc.file_type)
            doc.text_content = content
            doc.save()
            
            title = f"Important Questions - {file.name}"
        
        # Generate questions using AI with specific counts
        questions_by_marks = generate_important_questions_ai(content, requirements, subject)
        
        # Save to database
        paper = QuestionPaper.objects.create(
            title=title,
            subject=subject,
            paper_type='important',
            source_topic=content[:500] if source_type == 'topic' else '',
            source_document=doc if source_type == 'document' else None
        )
        
        # Save questions
        for marks, questions in questions_by_marks.items():
            for idx, q in enumerate(questions):
                GeneratedQuestion.objects.create(
                    paper=paper,
                    question_text=q['question'],
                    marks=int(marks),
                    answer_hint=q.get('hint', ''),
                    order=idx
                )
        
        print(f"[SUCCESS] Generated paper ID: {paper.id}")
        
        return JsonResponse({
            'status': 'success',
            'paper_id': paper.id,
            'questions': questions_by_marks
        })
        
    except Exception as e:
        import traceback
        print(f"[ERROR] {e}")
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def predict_questions(request):
    """Predict questions from previous papers"""
    try:
        print("[VIEW] Predicting questions from previous papers...")
        
        subject = request.POST.get('subject', 'General')
        requirements_text = request.POST.get('requirements', '')
        
        # Parse requirements (now comes as JSON)
        import json
        try:
            requirements = json.loads(requirements_text)
            requirements = {int(k): v for k, v in requirements.items()}
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'status': 'error', 'message': 'Invalid requirements format'}, status=400)
        
        from .nl_parser import validate_requirements
        is_valid, error_msg = validate_requirements(requirements)
        if not is_valid:
            return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
        
        marks_list = list(requirements.keys())
        
        # Get uploaded files
        files = request.FILES.getlist('previous_papers')
        if not files:
            return JsonResponse({'status': 'error', 'message': 'No files uploaded'}, status=400)
        
        print(f"[VIEW] Processing {len(files)} previous papers...")
        
        # Save and extract text from papers
        papers_content = []
        for file in files:
            prev_paper = PreviousPaper.objects.create(
                subject=subject,
                file=file
            )
            
            # Extract text
            file_type = file.name.split('.')[-1].lower()
            text = extract_text_from_file(prev_paper.file.path, file_type)
            prev_paper.text_content = text
            prev_paper.save()
            
            papers_content.append(text)
        
        # Predict questions using AI with exact requirements
        questions_by_marks = predict_questions_from_papers(papers_content, subject, requirements)
        
        # Save to database
        paper = QuestionPaper.objects.create(
            title=f"Predicted Paper - {subject}",
            subject=subject,
            paper_type='predicted'
        )
        
        # Save questions
        for marks, questions in questions_by_marks.items():
            for idx, q in enumerate(questions):
                GeneratedQuestion.objects.create(
                    paper=paper,
                    question_text=q['question'],
                    marks=int(marks),
                    answer_hint=q.get('reasoning', ''),
                    order=idx
                )
        
        print(f"[SUCCESS] Predicted paper ID: {paper.id}")
        
        return JsonResponse({
            'status': 'success',
            'paper_id': paper.id,
            'questions': questions_by_marks
        })
        
    except Exception as e:
        import traceback
        print(f"[ERROR] {e}")
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def export_pdf(request, paper_id):
    """Export question paper as PDF"""
    try:
        paper = QuestionPaper.objects.get(id=paper_id)
        questions = GeneratedQuestion.objects.filter(paper=paper)
        
        # Organize questions by marks
        questions_by_marks = {}
        for q in questions:
            marks_key = str(q.marks)
            if marks_key not in questions_by_marks:
                questions_by_marks[marks_key] = []
            questions_by_marks[marks_key].append({
                'question': q.question_text,
                'hint': q.answer_hint
            })
        
        return export_question_paper_pdf(paper, questions_by_marks)
        
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)


def view_paper(request, paper_id):
    """View generated question paper"""
    paper = QuestionPaper.objects.get(id=paper_id)
    questions = GeneratedQuestion.objects.filter(paper=paper)
    
    # Organize by marks
    questions_by_marks = {}
    for q in questions:
        marks = q.marks
        if marks not in questions_by_marks:
            questions_by_marks[marks] = []
        questions_by_marks[marks].append(q)
    
    return render(request, 'view_paper.html', {
        'paper': paper,
        'questions_by_marks': dict(sorted(questions_by_marks.items()))
    })


def learn_mode(request, paper_id):
    """Learn mode with AI chat for questions"""
    from .models import AIModel
    
    paper = QuestionPaper.objects.get(id=paper_id)
    questions = GeneratedQuestion.objects.filter(paper=paper)
    
    # Organize by marks
    questions_by_marks = {}
    total_questions = 0
    for q in questions:
        marks = q.marks
        if marks not in questions_by_marks:
            questions_by_marks[marks] = []
        questions_by_marks[marks].append(q)
        total_questions += 1
    
    # Get AI models suitable for learning
    ai_models = AIModel.objects.filter(is_active=True)
    
    return render(request, 'learn_mode.html', {
        'paper': paper,
        'questions_by_marks': dict(sorted(questions_by_marks.items())),
        'total_questions': total_questions,
        'ai_models': ai_models
    })
