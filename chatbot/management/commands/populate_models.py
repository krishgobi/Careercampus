"""
Management command to populate AI models in the database
"""
from django.core.management.base import BaseCommand
from chatbot.models import AIModel


class Command(BaseCommand):
    help = 'Populate AI models in the database'

    def handle(self, *args, **kwargs):
        models_data = [
            {
                'name': 'Gemini 2.5 Flash',
                'model_id': 'gemini-2.5-flash',
                'provider': 'gemini',
                'description': 'Latest Gemini model with enhanced performance and reasoning capabilities',
                'strength': 'Superior speed, excellent reasoning, large context window',
                'use_cases': 'Advanced chatbots, Complex Q&A, Document analysis, Code generation, Educational content'
            },
            {
                'name': 'Gemini 2.0 Flash Lite',
                'model_id': 'gemini-2.0-flash-lite',
                'provider': 'gemini',
                'description': 'Lightweight text model optimized for speed',
                'strength': 'Very fast, low cost',
                'use_cases': 'Simple bots, Auto-reply systems, Form validation, Text processing, Educational demos'
            },
            {
                'name': 'Llama 3.1 8B Instant',
                'model_id': 'llama-3.1-8b-instant',
                'provider': 'groq',
                'description': 'General-purpose LLM with excellent speed and good reasoning',
                'strength': 'Best overall Groq free model, very fast inference',
                'use_cases': 'Production chatbots, Backend assistants, Interview bots, Text classification, Business logic'
            },
            {
                'name': 'Llama 3.3 70B Versatile',
                'model_id': 'llama-3.3-70b-versatile',
                'provider': 'groq',
                'description': 'Powerful 70B parameter model with excellent reasoning and instruction following',
                'strength': 'Superior reasoning, handles complex tasks, very fast inference',
                'use_cases': 'Advanced reasoning, Complex Q&A, Educational content, Code generation, Research assistance'
            },
        ]

        created_count = 0
        updated_count = 0

        for data in models_data:
            model, created = AIModel.objects.update_or_create(
                model_id=data['model_id'],
                defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {model.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated: {model.name}'))

        self.stdout.write(self.style.SUCCESS(f'\nSummary: {created_count} created, {updated_count} updated'))
