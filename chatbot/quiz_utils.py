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
            
            # Use direct document content (RAG can fail)
            context = document.text_content[:10000]  # First 10k chars
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
        questions = generate_with_groq_direct(prompt, num_questions, topic_name)
        if questions and len(questions) > 0:
            print(f"[SUCCESS] Groq generated {len(questions)} questions!")
            return questions
    except Exception as e:
        print(f"[WARNING] Groq failed: {e}")
    
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
    try:
        # Initialize Groq client without proxies parameter
        client = Groq(api_key=settings.GROQ_API_KEY)
        
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
        
        text = response.choices[0].message.content.strip()
        print(f"[DEBUG] Groq response length: {len(text)} chars")
        
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
        print(f"[ERROR] Groq error details: {type(e).__name__}: {str(e)}")
        raise


def generate_with_gemini_direct(prompt, num_questions, topic):
    """Generate quiz using Gemini API"""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Use gemini-1.5-pro (stable v1 API model)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
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

import json
import google.generativeai as genai
from groq import Groq
from django.conf import settings
from .models import Quiz, QuizQuestion, LearningItem, Document
from .utils import retrieve_relevant_chunks

def generate_quiz_questions(topic, num_questions=10, document_id=None, source_type='prompt'):
    """Generate quiz questions using Gemini 1.5 Flash with Groq fallback"""
    
    print(f"\n{'='*60}")
    print(f"[QUIZ GEN] Starting quiz generation")
    print(f"[QUIZ GEN] Topic: {topic}")
    print(f"[QUIZ GEN] Source type: {source_type}")
    print(f"[QUIZ GEN] Document ID: {document_id}")
    print(f"[QUIZ GEN] Num questions: {num_questions}")
    print(f"{'='*60}\n")
    
    # Build context based on source type
    if source_type == 'document' and document_id:
        try:
            print(f"[QUIZ GEN] Fetching document with ID: {document_id}")
            
            # Use RAG to get relevant chunks from document
            document = Document.objects.get(id=document_id)
            print(f"[QUIZ GEN] Document found: {document.title}")
            print(f"[QUIZ GEN] Document content length: {len(document.text_content)} characters")
            
            if not document.text_content or len(document.text_content.strip()) < 50:
                print(f"[ERROR] Document has no content or too short!")
                return generate_fallback_questions(topic, num_questions)
            
            # Get relevant chunks using retrieval
            query = f"Generate comprehensive quiz questions covering main topics in this document"
            print(f"[QUIZ GEN] Attempting RAG retrieval...")
            
            try:
                relevant_chunks = retrieve_relevant_chunks(query, document.id, k=5)
                print(f"[QUIZ GEN] RAG retrieved {len(relevant_chunks)} chunks")
            except Exception as rag_error:
                print(f"[WARNING] RAG failed: {rag_error}")
                print(f"[QUIZ GEN] Falling back to direct document content")
                relevant_chunks = []
            
            if relevant_chunks and len(relevant_chunks) > 0:
                context = "\n\n".join(relevant_chunks)
                print(f"[QUIZ GEN] Using RAG chunks, total length: {len(context)} chars")
            else:
                # Fallback to full document text
                context = document.text_content[:15000]
                print(f"[QUIZ GEN] Using direct document content: {len(context)} chars")
            
            topic = f"Quiz based on: {document.title}"
            
            prompt = f"""You are an expert quiz generator. Create {num_questions} high-quality multiple choice questions based on this document content.

Document Content:
{context}

Requirements:
- Each question must have exactly 4 options (labeled A, B, C, D)
- Only ONE option should be correct
- Questions should test understanding, not just memory
- Include a brief explanation for the correct answer
- Questions should cover different aspects of the content

Return ONLY valid JSON array in this EXACT format (no markdown, no additional text):
[
  {{
    "question": "What is the main concept discussed?",
    "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
    "correct_answer": "Option A text",
    "explanation": "This is correct because..."
  }}
]
"""
            print(f"[QUIZ GEN] Prompt created, length: {len(prompt)} chars")
            
        except Document.DoesNotExist:
            print(f"[ERROR] Document with ID {document_id} not found!")
            return generate_fallback_questions(topic, num_questions)
        except Exception as e:
            print(f"[ERROR] Error retrieving document: {e}")
            import traceback
            traceback.print_exc()
            return generate_fallback_questions(topic, num_questions)
    else:
        # Generate from topic/prompt
        prompt = f"""You are an expert quiz generator. Create {num_questions} high-quality multiple choice questions on the topic: {topic}

Requirements:
- Each question must have exactly 4 options
- Only ONE option should be correct
- Questions should test understanding at different difficulty levels
- Include a brief explanation for the correct answer
- Make questions educational and engaging

Return ONLY valid JSON array in this EXACT format (no markdown, no additional text):
[
  {{
    "question": "Question text here?",
    "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
    "correct_answer": "Option A text",
    "explanation": "This is correct because..."
  }}
]
"""
    
    # Try Gemini 1.5 Flash (latest stable model)
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print(f"[INFO] Generating quiz with Gemini 1.5 Flash on topic: {topic}")
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,  # Higher for more diverse questions
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            )
        )
        
        # Extract JSON from response
        text = response.text.strip()
        print(f"[DEBUG] Raw response: {text[:200]}...")
        
        text = clean_json_response(text)
        print(f"[DEBUG] Cleaned response: {text[:200]}...")
        
        questions = json.loads(text)
        
        # Validate questions
        if not isinstance(questions, list) or len(questions) == 0:
            raise ValueError("No questions generated")
        
        # Ensure each question has required fields
        validated_questions = []
        for q in questions:
            if all(key in q for key in ['question', 'options', 'correct_answer', 'explanation']):
                validated_questions.append(q)
        
        if len(validated_questions) == 0:
            raise ValueError("No valid questions found in response")
        
        print(f"[SUCCESS] Generated {len(validated_questions)} unique questions using Gemini 1.5 Flash")
        return validated_questions
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parsing failed: {e}")
        print(f"[ERROR] Response text: {text}")
        # Try Groq fallback
        print("[INFO] Switching to Groq due to JSON error...")
        return generate_with_groq(prompt, num_questions, topic)
        
    except Exception as e:
        error_str = str(e).lower()
        print(f"[ERROR] Gemini 1.5 Flash error: {e}")
        
        # If quota exhausted or rate limited, try Groq
        if 'resource' in error_str or 'quota' in error_str or 'exhausted' in error_str or 'rate' in error_str:
            print("[INFO] Switching to Groq API due to Gemini quota...")
            return generate_with_groq(prompt, num_questions, topic)
        else:
            # For other errors, try Groq first before fallback
            print("[INFO] Attempting Groq as backup...")
            try:
                return generate_with_groq(prompt, num_questions, topic)
            except:
                print("[WARNING] Both APIs failed, using fallback questions")
                return generate_fallback_questions(topic, num_questions)


def generate_with_groq(prompt, num_questions, topic):
    """Generate quiz using Groq API as fallback"""
    try:
        print(f"[INFO] Generating quiz with Groq on topic: {topic}")
        
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a quiz generator. Return ONLY a valid JSON array of questions. No markdown, no code blocks, no additional text. Just the JSON array."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,  # Higher for diversity
            max_tokens=2048
        )
        
        text = response.choices[0].message.content.strip()
        print(f"[DEBUG] Groq raw response: {text[:200]}...")
        
        text = clean_json_response(text)
        print(f"[DEBUG] Groq cleaned response: {text[:200]}...")
        
        questions = json.loads(text)
        
        # Validate
        if not isinstance(questions, list) or len(questions) == 0:
            raise ValueError("No questions generated by Groq")
        
        print(f"[SUCCESS] Generated {len(questions)} unique questions using Groq")
        return questions
        
    except Exception as e:
        print(f"[ERROR] Groq API error: {e}")
        return generate_fallback_questions(topic, num_questions)


def clean_json_response(text):
    """Clean JSON response from AI models"""
    # Remove markdown code blocks if present
    if text.startswith('```json'):
        text = text[7:]
    if text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    return text.strip()


def generate_fallback_questions(topic, num_questions):
    """Generate fallback sample questions when APIs fail"""
    print(f"[WARNING] Using fallback questions for: {topic}")
    return [
        {
            "question": f"Which of the following best describes {topic}?",
            "options": [
                f"A fundamental concept in {topic}",
                f"An unrelated topic",
                f"A minor detail",
                f"None of the above"
            ],
            "correct_answer": f"A fundamental concept in {topic}",
            "explanation": "This is a sample question. Please check your API configuration for better quiz quality."
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
