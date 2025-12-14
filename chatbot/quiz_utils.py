"""
Quiz generation utilities using AI (Gemini)
"""
import json
import google.generativeai as genai
from django.conf import settings
from .models import Quiz, QuizQuestion, LearningItem, Document
from .utils import retrieve_relevant_chunks

def generate_quiz_questions(topic, num_questions=10, document_id=None, source_type='prompt'):
    """Generate quiz questions using Gemini AI"""
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Build context
    if source_type == 'document' and document_id:
        # Get document content
        document = Document.objects.get(id=document_id)
        context = document.text_content[:15000]  # Limit context size
        topic = f"Quiz based on: {document.title}"
        prompt = f"""Generate {num_questions} multiple choice questions based on the following document content:

{context}

Each question should have 4 options (A, B, C, D) and one correct answer.
Return ONLY a valid JSON array with this exact structure, no additional text:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option B",
    "explanation": "Brief explanation why this answer is correct"
  }}
]
"""
    else:
        # Generate from topic/prompt
        prompt = f"""Generate {num_questions} multiple choice questions on the topic: {topic}

Each question should have 4 options and one correct answer.
Return ONLY a valid JSON array with this exact structure, no additional text:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option B",
    "explanation": "Brief explanation why this answer is correct"
  }}
]
"""
    
    try:
        response = model.generate_content(prompt)
        # Extract JSON from response
        text = response.text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        questions = json.loads(text)
        return questions
    except Exception as e:
        print(f"Error generating quiz: {e}")
        # Fallback: generate sample questions
        return [
            {
                "question": f"Sample question {i+1} about {topic}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "explanation": "This is the correct answer."
            }
            for i in range(num_questions)
        ]


def evaluate_answer(question_text, user_answer, correct_answer):
    """Evaluate if answer is correct and provide explanation"""
    is_correct = user_answer.strip() == correct_answer.strip()
    
    if is_correct:
        explanation = f"Correct! {correct_answer} is the right answer."
    else:
        explanation = f"Incorrect. The correct answer is {correct_answer}, not {user_answer}."
    
    return is_correct, explanation
