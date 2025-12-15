"""
Question Paper Generation Logic
Generates important questions and predicts question papers using AI
"""
import json
from groq import Groq
import google.generativeai as genai
from django.conf import settings
from .utils import extract_text_from_file


def generate_important_questions_ai(content, requirements, subject=""):
    """
    Generate important questions from content based on specified requirements
    
    Args:
        content: Text content (from topic or document)
        requirements: Dict of {marks: count} e.g., {2: 10, 5: 5, 10: 3}
        subject: Subject name (optional)
        
    Returns:
        Dict with questions organized by marks
    """
    print(f"[QUESTION GEN] Generating questions for requirements: {requirements}")
    
    # Build detailed prompt with specific counts
    requirements_text = ", ".join([f"{count} {marks}-mark questions" for marks, count in requirements.items()])
    
    # Build JSON structure example based on actual requirements
    json_structure = {}
    for marks, count in requirements.items():
        json_structure[str(marks)] = [
            {"question": "Question text here", "hint": "Brief hint for answer"}
            for _ in range(min(count, 2))  # Show 2 examples
        ]
    
    json_example = json.dumps(json_structure, indent=2)
    
    prompt = f"""Generate exam questions from the following content.

Subject: {subject or 'General'}
Content:
{content[:8000]}

STRICT REQUIREMENT - Generate EXACTLY these questions (no more, no less):
{requirements_text}

For each mark category, create appropriate questions:
- 2 marks: Short answer questions (1-2 sentences)
- 5 marks: Medium answer questions (1 paragraph)
- 10 marks: Long answer/essay questions (detailed explanation)
- 15 marks: Very detailed essay questions (comprehensive explanation)

Return ONLY a JSON object in this exact format:
{json_example}

CRITICAL: 
1. Generate the EXACT number of questions specified for each mark category
2. If asked for "2 two-mark questions", generate ONLY 2 questions in the "2" category
3. Do NOT add extra questions
4. Do NOT generate questions for mark categories not requested
"""
    
    # Try Groq first
    try:
        print("[QUESTION GEN] Attempting Groq...")
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert question paper generator. You MUST generate EXACTLY the number of questions requested for each mark category. Return ONLY valid JSON, no markdown, no extra text. Follow the requirements PRECISELY."
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
        text = clean_json_response(text)
        questions = json.loads(text)
        
        print(f"[SUCCESS] Generated questions via Groq")
        return questions
        
    except Exception as e:
        print(f"[WARNING] Groq failed: {e}")
    
    # Try Gemini as fallback
    try:
        print("[QUESTION GEN] Attempting Gemini...")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=3000,
            )
        )
        
        text = response.text.strip()
        text = clean_json_response(text)
        questions = json.loads(text)
        
        print(f"[SUCCESS] Generated questions via Gemini")
        return questions
        
    except Exception as e:
        print(f"[ERROR] Gemini failed: {e}")
    
    # Return fallback
    return generate_fallback_questions(list(requirements.keys()))


def predict_questions_from_papers(papers_content, subject, requirements):
    """
    Analyze previous papers and predict likely questions
    
    Args:
        papers_content: List of text content from previous papers
        subject: Subject name
        requirements: Dict of {marks: count} e.g., {2: 10, 5: 5}
        
    Returns:
        Dict with predicted questions organized by marks
    """
    print(f"[PREDICTION] Analyzing {len(papers_content)} previous papers")
    print(f"[PREDICTION] Requirements: {requirements}")
    
    # Combine all papers
    combined_content = "\n\n---PAPER SEPARATOR---\n\n".join(papers_content[:5])  # Max 5 papers
    
    # Build requirements text
    requirements_text = ", ".join([f"{count} {marks}-mark questions" for marks, count in requirements.items()])
    
    # Build JSON structure example
    json_structure = {}
    for marks, count in requirements.items():
        json_structure[str(marks)] = [
            {"question": "Predicted question", "reasoning": "Why this is likely"}
            for _ in range(min(count, 2))  # Show 2 examples
        ]
    
    json_example = json.dumps(json_structure, indent=2)
    
    prompt = f"""Analyze these previous year question papers and predict likely exam questions.

Subject: {subject}

Previous Papers:
{combined_content[:10000]}

Based on patterns in these papers, predict EXACTLY these questions (no more, no less):
{requirements_text}

Consider:
1. Frequently asked topics
2. Question patterns and formats
3. Important concepts that appear multiple times
4. Logical progression of difficulty

Return ONLY a JSON object in this exact format:
{json_example}

IMPORTANT: Generate the EXACT number of questions specified for each mark category.
"""
    
    # Try Groq first
    try:
        print("[PREDICTION] Attempting Groq...")
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing exam patterns and predicting questions. Return ONLY valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.6,
            max_tokens=3500
        )
        
        text = response.choices[0].message.content.strip()
        text = clean_json_response(text)
        questions = json.loads(text)
        
        print(f"[SUCCESS] Predicted questions via Groq")
        return questions
        
    except Exception as e:
        print(f"[WARNING] Groq failed: {e}")
    
    # Try Gemini as fallback
    try:
        print("[PREDICTION] Attempting Gemini...")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.6,
                max_output_tokens=3500,
            )
        )
        
        text = response.text.strip()
        text = clean_json_response(text)
        questions = json.loads(text)
        
        print(f"[SUCCESS] Predicted questions via Gemini")
        return questions
        
    except Exception as e:
        print(f"[ERROR] Gemini failed: {e}")
    
    # Return fallback
    return generate_fallback_questions(mark_types)


def clean_json_response(text):
    """Clean JSON response from AI models"""
    # Remove markdown code blocks
    if '```json' in text:
        text = text.split('```json')[1]
    if '```' in text:
        text = text.split('```')[0]
    
    # Find JSON object
    start = text.find('{')
    end = text.rfind('}') + 1
    
    if start != -1 and end > start:
        text = text[start:end]
    
    return text.strip()


def generate_fallback_questions(marks_list):
    """Generate fallback questions when AI fails"""
    fallback = {}
    for marks in marks_list:
        fallback[str(marks)] = [
            {
                "question": f"Sample {marks}-mark question (AI generation failed)",
                "hint": "Please check your API keys and try again"
            }
            for i in range(3)
        ]
    return fallback
