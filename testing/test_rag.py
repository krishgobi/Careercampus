"""
Test script to verify RAG components are working
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_assistant.settings')
django.setup()

from django.conf import settings
import google.generativeai as genai
from groq import Groq

print("=" * 60)
print("Testing Smart Campus Assistant RAG Components")
print("=" * 60)

# Test 1: Check API Keys
print("\n1. Checking API Keys...")
groq_key = settings.GROQ_API_KEY
gemini_key = settings.GEMINI_API_KEY

if groq_key:
    print(f"   ✓ Groq API Key found: {groq_key[:20]}...")
else:
    print("   ✗ Groq API Key missing!")

if gemini_key:
    print(f"   ✓ Gemini API Key found: {gemini_key[:20]}...")
else:
    print("   ✗ Gemini API Key missing!")

# Test 2: Test Groq Connection
print("\n2. Testing Groq API Connection...")
try:
    client = Groq(api_key=groq_key)
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello World' if you can hear me."}
        ],
        max_tokens=50
    )
    print(f"   ✓ Groq API working!")
    print(f"   Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"   ✗ Groq API Error: {e}")

# Test 3: Test Gemini Connection
print("\n3. Testing Gemini API Connection...")
try:
    genai.configure(api_key=gemini_key)
    
    # Test embedding
    result = genai.embed_content(
        model="models/embedding-001",
        content="This is a test sentence.",
        task_type="retrieval_document"
    )
    embedding = result['embedding']
    print(f"   ✓ Gemini API working!")
    print(f"   Embedding dimension: {len(embedding)}")
except Exception as e:
    print(f"   ✗ Gemini API Error: {e}")

# Test 4: Check Database
print("\n4. Checking Database...")
try:
    from chatbot.models import Document, Chat, Message
    doc_count = Document.objects.count()
    chat_count = Chat.objects.count()
    msg_count = Message.objects.count()
    
    print(f"   ✓ Database accessible!")
    print(f"   Documents: {doc_count}")
    print(f"   Chats: {chat_count}")
    print(f"   Messages: {msg_count}")
    
    if doc_count > 0:
        print("\n   Recent documents:")
        for doc in Document.objects.all()[:3]:
            print(f"   - {doc.title} ({doc.file_type})")
            text_preview = doc.text_content[:100] if doc.text_content else "No text extracted"
            print(f"     Text preview: {text_preview}...")
except Exception as e:
    print(f"   ✗ Database Error: {e}")

# Test 5: Test RAG Pipeline
print("\n5. Testing RAG Pipeline...")
try:
    from chatbot.utils import extract_text_from_file, chunk_text, get_embeddings
    
    print("   ✓ RAG utilities imported successfully!")
    
    # Test text chunking
    test_text = "This is a test. " * 100
    chunks = chunk_text(test_text, chunk_size=100, chunk_overlap=20)
    print(f"   ✓ Text chunking working! Created {len(chunks)} chunks")
    
    # Test embeddings (small test)
    print("   Testing embeddings generation...")
    test_chunks = ["Hello world", "This is a test"]
    embeddings = get_embeddings(test_chunks)
    print(f"   ✓ Embeddings working! Shape: {embeddings.shape}")
    
except Exception as e:
    print(f"   ✗ RAG Pipeline Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)
