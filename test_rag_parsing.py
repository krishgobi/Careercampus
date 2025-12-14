"""
Test script to verify RAG and document parsing
"""
import os
import sys
import django

# Setup Django
sys.path.append('p:/antigravity')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_assistant.settings')
django.setup()

from chatbot.models import Document
from chatbot.rag_service import extract_document_headings

print("="*60)
print("Testing Document Parsing and RAG")
print("="*60)

# Test 1: Check if documents exist
print("\n[TEST 1] Checking documents in database...")
documents = Document.objects.all()
print(f"Total documents: {documents.count()}")

if documents.count() == 0:
    print("[WARNING] No documents found! Please upload a document first.")
    sys.exit(0)

# Test 2: Check document content
print("\n[TEST 2] Checking document content...")
for doc in documents[:3]:
    print(f"\nDocument ID: {doc.id}")
    print(f"Title: {doc.title}")
    print(f"Content length: {len(doc.text_content)} characters")
    print(f"First 200 chars: {doc.text_content[:200]}...")
    
    if len(doc.text_content) < 100:
        print("[WARNING] Document content is too short!")

# Test 3: Test RAG heading extraction
print("\n[TEST 3] Testing RAG heading extraction...")
if documents.count() > 0:
    test_doc = documents.first()
    print(f"Testing with document: {test_doc.title}")
    
    try:
        headings = extract_document_headings(test_doc.id)
        print(f"\n[SUCCESS] Extracted {len(headings)} headings:")
        
        for i, heading in enumerate(headings[:10], 1):
            print(f"\n{i}. {heading['text']}")
            print(f"   Level: {heading['level']}")
            print(f"   Preview: {heading['preview'][:100]}...")
            print(f"   Word count: {heading['word_count']}")
        
        if len(headings) == 0:
            print("[WARNING] No headings found! Document might not have clear structure.")
            print("Trying to show document structure:")
            lines = test_doc.text_content.split('\n')[:20]
            for i, line in enumerate(lines, 1):
                if line.strip():
                    print(f"{i}: {line[:80]}")
        
    except Exception as e:
        print(f"[ERROR] RAG extraction failed: {e}")
        import traceback
        traceback.print_exc()

# Test 4: Test quiz generation endpoint
print("\n[TEST 4] Testing quiz generation...")
print("To test quiz generation, use:")
print(f"POST /api/quiz/extract-headings/")
print(f"Body: {{'document_id': {documents.first().id if documents.count() > 0 else 'N/A'}}}")

print("\n" + "="*60)
print("Test Complete!")
print("="*60)
