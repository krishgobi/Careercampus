"""
Quiz generation utilities using AI (Groq primary, Gemini fallback)
"""
import json
import google.generativeai as genai
from groq import Groq
from django.conf import settings
from .models import Quiz, QuizQuestion, LearningItem, Document
from .utils import retrieve_relevant_chunks

def generate_quiz_questions(topic, num_questions=10, document_id=None, source_type='prompt'):
    """Generate quiz questions using Groq (primary) with Gemini fallback"""
    
    print(f"\n{'='*60}")
    print(f"[QUIZ GEN] Starting quiz generation")
    print(f"[QUIZ GEN] Topic: {topic}")
    print(f"[QUIZ GEN] Source type: {source_type}")
    print(f"[QUIZ GEN] Document ID: {document_id}")
    print(f"[QUIZ GEN] Num questions: {num_questions}")
    print(f"{'='*60}\n")
    
    # Build prompt based on source type
    if source_type == 'document' and document_id:
        try:
            print(f"[QUIZ GEN] Fetching document with ID: {document_id}")
            document = Document.objects.get(id=document_id)
            print(f"[QUIZ GEN] Document found: {document.title}")
            print(f"[QUIZ GEN] Document content length: {len(document.text_content)} characters")
            
            if not document.text_content or len(document.text_content.strip()) < 50:
                print(f"[ERROR] Document has no content or too short!")
                return generate_fallback_questions(topic, num_questions)
            
            # Use direct document content (first 10k chars for better context)
            context = document.text_content[:10000]
            print(f"[QUIZ GEN] Using document content: {len(context)} chars")
            
            topic_name = document.title
            
        except Exception as e:
            print(f"[ERROR] Error retrieving document: {e}")
            return generate_fallback_questions(topic, num_questions)
    else:
        context = ""
        topic_name = topic
    
    # Build the prompt
    if context:
        prompt = f"""Create {num_questions} multiple choice quiz questions about this document.

Document: {topic_name}
Content:
{context}

Create educational questions that test understanding of the key concepts in this document.

Return ONLY a JSON array (no markdown, no code blocks):
[
  {{
    "question": "What is...",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "correct_answer": "A) ...",
    "explanation": "This is correct because..."
  }}
]"""
    else:
        prompt = f"""Create {num_questions} multiple choice quiz questions about: {topic_name}

Make the questions educational and test real understanding.

Return ONLY a JSON array (no markdown, no code blocks):
[
  {{
    "question": "What is...",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "correct_answer": "A) ...",
    "explanation": "This is correct because..."
  }}
]"""
    
    print(f"[QUIZ GEN] Prompt created ({len(prompt)} chars)")
    
    # Try Groq FIRST (more reliable)
    try:
        print(f"[QUIZ GEN] Attempting Groq API...")
        print(f"[DEBUG] Groq API Key present: {bool(settings.GROQ_API_KEY)}")
        questions = generate_with_groq_direct(prompt, num_questions, topic_name)
        if questions and len(questions) > 0:
            print(f"[SUCCESS] Groq generated {len(questions)} questions!")
            return questions
    except Exception as e:
        import traceback
        print(f"[ERROR] Groq failed with error: {type(e).__name__}: {str(e)}")
        print(f"[ERROR] Groq traceback:")
        traceback.print_exc()

    
    # Try Gemini as fallback
    try:
        print(f"[QUIZ GEN] Attempting Gemini API...")
        questions = generate_with_gemini_direct(prompt, num_questions, topic_name)
        if questions and len(questions) > 0:
            print(f"[SUCCESS] Gemini generated {len(questions)} questions!")
            return questions
    except Exception as e:
        print(f"[WARNING] Gemini failed: {e}")
    
    # Both failed - return fallback
    print(f"[ERROR] Both APIs failed - using fallback questions")
    return generate_fallback_questions(topic_name, num_questions)


def generate_with_groq_direct(prompt, num_questions, topic):
    """Generate quiz using Groq API"""
    print(f"[GROQ] Starting Groq generation...")
    print(f"[GROQ] API Key present: {bool(settings.GROQ_API_KEY)}")
    try:
        print(f"[GROQ] Initializing client...")
        # Initialize Groq client (no proxies parameter)
        client = Groq(api_key=settings.GROQ_API_KEY)
        print(f"[GROQ] Client initialized!")
        
        print(f"[GROQ] Calling API...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a quiz generator. Return ONLY a valid JSON array. No markdown, no explanations, just the JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=3000
        )
        print(f"[GROQ] API call successful!")
        
        text = response.choices[0].message.content.strip()
        print(f"[GROQ] Response length: {len(text)} chars")
        print(f"[GROQ] Response preview: {text[:200]}...")
        
        # Clean and parse
        print(f"[GROQ] Cleaning JSON...")
        text = clean_json_response(text)
        print(f"[GROQ] Parsing JSON...")
        questions = json.loads(text)
        print(f"[GROQ] Parsed {len(questions) if isinstance(questions, list) else 0} items")
        
        # Validate
        if not isinstance(questions, list):
            raise ValueError("Response is not a list")
        
        valid_questions = []
        for q in questions:
            if all(k in q for k in ['question', 'options', 'correct_answer', 'explanation']):
                valid_questions.append(q)
        
        return valid_questions
    except Exception as e:
        print(f"[ERROR] Groq error details: {type(e).__name__}: {str(e)}")
        raise


def generate_with_gemini_direct(prompt, num_questions, topic):
    """Generate quiz using Gemini API"""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Use gemini-2.0-flash-exp (available model)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=3000,
            )
        )
        
        text = response.text.strip()
        print(f"[DEBUG] Gemini response length: {len(text)} chars")
        
        # Clean and parse
        text = clean_json_response(text)
        questions = json.loads(text)
        
        # Validate
        if not isinstance(questions, list):
            raise ValueError("Response is not a list")
        
        valid_questions = []
        for q in questions:
            if all(k in q for k in ['question', 'options', 'correct_answer', 'explanation']):
                valid_questions.append(q)
        
        return valid_questions
    except Exception as e:
        print(f"[ERROR] Gemini error details: {type(e).__name__}: {str(e)}")
        raise


def clean_json_response(text):
    """Clean JSON response from AI models"""
    # Remove markdown code blocks
    if '```json' in text:
        text = text.split('```json')[1]
    if '```' in text:
        text = text.split('```')[0]
    
    # Find JSON array
    start = text.find('[')
    end = text.rfind(']') + 1
    
    if start != -1 and end > start:
        text = text[start:end]
    
    return text.strip()


def generate_fallback_questions(topic, num_questions):
    """Generate fallback sample questions when APIs fail"""
    print(f"[WARNING] Using fallback questions for: {topic}")
    return [
        {
            "question": f"Sample Question {i+1} about {topic}",
            "options": [
                f"A) First option about {topic}",
                f"B) Second option about {topic}",
                f"C) Third option about {topic}",
                f"D) Fourth option about {topic}"
            ],
            "correct_answer": f"A) First option about {topic}",
            "explanation": "This is a sample question. The quiz generation API is not working. Please check your API keys."
        }
        for i in range(min(num_questions, 5))
    ]


def evaluate_answer(question_text, user_answer, correct_answer):
    """Evaluate if answer is correct and provide explanation"""
    is_correct = user_answer.strip() == correct_answer.strip()
    
    if is_correct:
        explanation = f"Correct! {correct_answer} is the right answer."
    else:
        explanation = f"Incorrect. The correct answer is {correct_answer}, not {user_answer}."
    
    return is_correct, explanation


def generate_quiz_from_headings(document_id, selected_headings, num_questions=10):
    """
    Generate unique quiz questions from selected document headings using Groq
    
    Args:
        document_id: Document ID
        selected_headings: List of heading IDs to generate questions from
        num_questions: Number of unique questions to generate
        
    Returns:
        List of unique question dictionaries
    """
    from .rag_service import get_heading_content
    
    print(f"\n{'='*60}")
    print(f"[QUIZ FROM HEADINGS] Starting generation")
    print(f"[QUIZ FROM HEADINGS] Document ID: {document_id}")
    print(f"[QUIZ FROM HEADINGS] Selected headings: {len(selected_headings)}")
    print(f"[QUIZ FROM HEADINGS] Num questions: {num_questions}")
    print(f"{'='*60}\n")
    
    try:
        # Get content from selected headings
        heading_content = get_heading_content(document_id, selected_headings)
        
        if not heading_content or len(heading_content.strip()) < 50:
            print("[ERROR] Insufficient content from selected headings")
            return generate_fallback_questions("Selected sections", num_questions)
        
        print(f"[QUIZ FROM HEADINGS] Content length: {len(heading_content)} chars")
        
        # Build enhanced prompt for Groq
        prompt = f"""Generate {num_questions} COMPLETELY UNIQUE multiple choice questions from these document sections.

Document Content:
{heading_content[:8000]}

CRITICAL REQUIREMENTS:
1. Each question must be COMPLETELY DIFFERENT - no similar variations
2. Questions must test UNDERSTANDING, not just memory recall
3. Cover DIFFERENT aspects of the content
4. Each question has exactly 4 options (A, B, C, D)
5. Only ONE correct answer per question
6. Provide a brief 1-sentence explanation for the correct answer

Return ONLY a valid JSON array (no markdown, no code blocks):
[
  {{
    "question": "What is the main concept of...",
    "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
    "correct_answer": "A) First option",
    "explanation": "This is correct because..."
  }}
]
"""
        
        # Try Groq first (primary)
        try:
            print("[QUIZ FROM HEADINGS] Attempting Groq API...")
            questions = generate_with_groq_direct(prompt, num_questions, "document headings")
            
            if questions and len(questions) > 0:
                # Validate uniqueness
                unique_questions = ensure_unique_questions(questions)
                print(f"[SUCCESS] Generated {len(unique_questions)} unique questions from headings!")
                return unique_questions
                
        except Exception as e:
            print(f"[WARNING] Groq failed: {e}")
        
        # Try Gemini as fallback
        try:
            print("[QUIZ FROM HEADINGS] Attempting Gemini API...")
            questions = generate_with_gemini_direct(prompt, num_questions, "document headings")
            
            if questions and len(questions) > 0:
                unique_questions = ensure_unique_questions(questions)
                print(f"[SUCCESS] Generated {len(unique_questions)} unique questions from headings!")
                return unique_questions
                
        except Exception as e:
            print(f"[WARNING] Gemini failed: {e}")
        
        # Both failed
        print("[ERROR] Both APIs failed for heading-based quiz")
        return generate_fallback_questions("Selected sections", num_questions)
        
    except Exception as e:
        print(f"[ERROR] Failed to generate quiz from headings: {e}")
        import traceback
        traceback.print_exc()
        return generate_fallback_questions("Selected sections", num_questions)


def ensure_unique_questions(questions):
    """
    Ensure all questions are unique by removing duplicates and very similar questions
    
    Args:
        questions: List of question dictionaries
        
    Returns:
        List of unique questions
    """
    if not questions:
        return []
    
    unique = []
    seen_keywords = set()
    
    for q in questions:
        # Extract key terms from question (simple keyword extraction)
        question_text = q.get('question', '').lower()
        words = question_text.split()
        
        # Get significant words (>4 chars, not common words)
        keywords = {w for w in words if len(w) > 4 and w not in ['what', 'which', 'where', 'when', 'following', 'describe', 'explain']}
        
        # Check if this question is too similar to existing ones
        overlap = keywords.intersection(seen_keywords)
        similarity_ratio = len(overlap) / len(keywords) if keywords else 0
        
        # Only add if less than 50% keyword overlap
        if similarity_ratio < 0.5:
            unique.append(q)
            seen_keywords.update(keywords)
    
    print(f"[UNIQUENESS] Filtered {len(questions)} → {len(unique)} unique questions")
    return unique
