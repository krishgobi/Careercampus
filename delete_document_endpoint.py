"""
Delete Document API Endpoint
Add this to chatbot/views.py
"""
from django.shortcuts import get_object_or_404

@csrf_exempt
@require_http_methods(["POST"])
def delete_document(request, document_id):
    """Delete a document and its file"""
    try:
        document = get_object_or_404(Document, id=document_id)
        
        # Delete the file from storage
        if document.file:
            try:
                document.file.delete(save=False)
            except:
                pass  # File might already be deleted
        
        # Delete from database
        document.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Document deleted successfully'
        })
    except Exception as e:
        print(f"Error deleting document: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
