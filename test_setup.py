import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_assistant.settings')

try:
    django.setup()
    print("Django setup successful!")
    
    # Try importing models
    from chatbot.models import Document, Chat, Message
    print("Models imported successfully!")
    
    # Run migrations check
    from django.core.management import call_command
    print("\nChecking migrations...")
    call_command('makemigrations', '--dry-run', verbosity=2)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
