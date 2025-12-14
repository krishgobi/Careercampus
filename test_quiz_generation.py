"""
Test quiz generation to debug API issues
"""
import os
import sys
import django

# Setup Django
sys.path.append('p:/antigravity')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_assistant.settings')
django.setup()

from chatbot.quiz_utils import generate_quiz_questions

print("Testing quiz generation...")
print("="*60)

# Test 1: Simple prompt-based quiz
print("\nTest 1: Prompt-based quiz on 'Python Programming'")
questions = generate_quiz_questions(
    topic="Python Programming",
    num_questions=3,
    source_type='prompt'
)

print(f"\nGenerated {len(questions)} questions:")
for i, q in enumerate(questions, 1):
    print(f"\nQ{i}: {q['question']}")
    print(f"Options: {q['options']}")
    print(f"Correct: {q['correct_answer']}")

print("\n" + "="*60)
print("Test complete!")
