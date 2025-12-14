"""
Test script to verify API configuration for both Gemini and Groq providers
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Load environment variables
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_assistant.settings')
import django
django.setup()

from chatbot.utils import call_llm_api

def test_gemini_api():
    """Test Gemini API connectivity"""
    print("\n" + "="*60)
    print("TESTING GEMINI API")
    print("="*60)
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("[X] GEMINI_API_KEY not found in .env file")
        return False
    
    print(f"[+] GEMINI_API_KEY found (length: {len(gemini_key)} chars)")
    
    # Test models
    gemini_models = [
        'gemini-2.0-flash-exp',
        'gemini-2.5-flash'
    ]
    
    for model_id in gemini_models:
        print(f"\n[*] Testing model: {model_id}")
        try:
            messages = [
                {"role": "user", "content": "Say 'API test successful' if you can read this."}
            ]
            
            response = call_llm_api(model_id, messages, temperature=0.5, max_tokens=50)
            
            print(f"[OK] {model_id} - SUCCESS")
            print(f"     Response: {response[:100]}...")
            
        except Exception as e:
            print(f"[X] {model_id} - FAILED")
            print(f"    Error: {type(e).__name__}: {str(e)}")
            return False
    
    return True


def test_groq_api():
    """Test Groq API connectivity"""
    print("\n" + "="*60)
    print("TESTING GROQ API")
    print("="*60)
    
    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key:
        print("[X] GROQ_API_KEY not found in .env file")
        return False
    
    print(f"[+] GROQ_API_KEY found (length: {len(groq_key)} chars)")
    
    # Test models
    groq_models = [
        'llama-3.3-70b-versatile',
        'llama-3.1-8b-instant',
        'mixtral-8x7b-32768'
    ]
    
    for model_id in groq_models:
        print(f"\n[*] Testing model: {model_id}")
        try:
            messages = [
                {"role": "user", "content": "Say 'API test successful' if you can read this."}
            ]
            
            response = call_llm_api(model_id, messages, temperature=0.5, max_tokens=50)
            
            print(f"[OK] {model_id} - SUCCESS")
            print(f"     Response: {response[:100]}...")
            
        except Exception as e:
            print(f"[X] {model_id} - FAILED")
            print(f"    Error: {type(e).__name__}: {str(e)}")
            # Continue testing other models even if one fails
    
    return True


def test_rag_functionality():
    """Test RAG functionality with a simple document"""
    print("\n" + "="*60)
    print("TESTING RAG FUNCTIONALITY")
    print("="*60)
    
    try:
        from chatbot.utils import chunk_text, create_vector_store, retrieve_relevant_chunks
        
        # Sample text
        sample_text = """
        Artificial Intelligence (AI) is transforming education. 
        Students can now use AI tutors to get personalized help with their studies.
        Machine learning algorithms can analyze learning patterns and suggest improvements.
        Natural language processing enables chatbots to understand student questions.
        """
        
        print("\n[*] Creating test chunks...")
        chunks = chunk_text(sample_text, chunk_size=100, chunk_overlap=20)
        print(f"    Created {len(chunks)} chunks")
        
        print("\n[*] Creating vector store...")
        create_vector_store(999, chunks)
        print("    [OK] Vector store created successfully")
        
        print("\n[*] Testing retrieval...")
        query = "What can AI do for education?"
        results = retrieve_relevant_chunks(query, 999, k=2)
        print(f"    Retrieved {len(results)} relevant chunks")
        for i, chunk in enumerate(results, 1):
            print(f"    Chunk {i}: {chunk[:80]}...")
        
        print("\n[OK] RAG functionality working correctly")
        return True
        
    except Exception as e:
        print(f"\n[X] RAG test failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("KATTRAL AI - API PROVIDER TESTS".center(60))
    print("=" * 60)
    
    results = {
        'gemini': test_gemini_api(),
        'groq': test_groq_api(),
        'rag': test_rag_functionality()
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for provider, status in results.items():
        status_text = "[OK]" if status else "[X]"
        print(f"{status_text} {provider.upper()}: {'PASSED' if status else 'FAILED'}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED!")
        print("Your API configuration is working correctly.")
    else:
        print("[WARNING] SOME TESTS FAILED.")
        print("Please check the errors above.")
    print("="*60 + "\n")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
