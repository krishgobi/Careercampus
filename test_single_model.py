"""Quick test for the new default model"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_assistant.settings')
import django
django.setup()

from chatbot.utils import call_llm_api

def test_model():
    print("Testing llama-3.1-8b-instant (new default)...")
    try:
        messages = [{"role": "user", "content": "Say 'API test successful' if you can read this."}]
        response = call_llm_api('llama-3.1-8b-instant', messages, temperature=0.5, max_tokens=50)
        print(f"[OK] SUCCESS - Response: {response}")
        return True
    except Exception as e:
        print(f"[X] FAILED - Error: {type(e).__name__}: {str(e)}")
        return False

if __name__ == '__main__':
    test_model()
