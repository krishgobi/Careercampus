"""
RAG Service for Document Analysis and Heading Extraction
"""
import re
from typing import List, Dict
from .models import Document


def extract_document_headings(document_id: int) -> List[Dict]:
    """
    Extract headings and sections from document using pattern matching
    
    Args:
        document_id: ID of the document to analyze
        
    Returns:
        List of heading dictionaries with structure:
        [
            {
                'id': 'h1',
                'text': 'Introduction to Machine Learning',
                'level': 1,
                'preview': 'First 200 chars of content...',
                'word_count': 250,
                'start_pos': 0,
                'end_pos': 500
            }
        ]
    """
    try:
        document = Document.objects.get(id=document_id)
        text = document.text_content
        
        headings = []
        lines = text.split('\n')
        
        heading_id = 0
        current_pos = 0
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            if not line_stripped:
                current_pos += len(line) + 1
                continue
            
            # Detect heading patterns
            heading_info = detect_heading(line_stripped, i, lines)
            
            if heading_info:
                # Get content preview (next 200 chars)
                preview_start = current_pos + len(line) + 1
                preview_text = text[preview_start:preview_start + 200].strip()
                
                # Calculate word count for this section
                next_heading_pos = find_next_heading(lines, i + 1)
                section_text = '\n'.join(lines[i+1:next_heading_pos])
                word_count = len(section_text.split())
                
                headings.append({
                    'id': f'h{heading_id}',
                    'text': heading_info['text'],
                    'level': heading_info['level'],
                    'preview': preview_text[:200] + '...' if len(preview_text) > 200 else preview_text,
                    'word_count': word_count,
                    'start_pos': current_pos,
                    'end_pos': current_pos + len(section_text)
                })
                
                heading_id += 1
            
            current_pos += len(line) + 1
        
        print(f"[RAG] Extracted {len(headings)} headings from document {document_id}")
        return headings
        
    except Document.DoesNotExist:
        print(f"[ERROR] Document {document_id} not found")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to extract headings: {e}")
        return []


def detect_heading(line: str, line_num: int, all_lines: List[str]) -> Dict:
    """
    Detect if a line is a heading and determine its level
    
    Patterns detected:
    - ALL CAPS (minimum 3 words)
    - Numbered sections (1., 1.1, etc.)
    - Lines ending with colon
    - Short lines (<80 chars) followed by longer paragraphs
    - Markdown-style headers (# Header)
    """
    # Pattern 1: Markdown headers
    if line.startswith('#'):
        level = len(line) - len(line.lstrip('#'))
        text = line.lstrip('#').strip()
        return {'text': text, 'level': min(level, 3)}
    
    # Pattern 2: Numbered sections
    numbered_match = re.match(r'^(\d+\.)+\s+(.+)$', line)
    if numbered_match:
        dots = numbered_match.group(1).count('.')
        text = numbered_match.group(2)
        return {'text': text, 'level': dots}
    
    # Pattern 3: ALL CAPS (minimum 3 words, max 100 chars)
    if line.isupper() and len(line.split()) >= 3 and len(line) < 100:
        return {'text': line, 'level': 1}
    
    # Pattern 4: Lines ending with colon (likely section headers)
    if line.endswith(':') and len(line) < 80 and len(line.split()) >= 2:
        return {'text': line[:-1], 'level': 2}
    
    # Pattern 5: Short line followed by longer paragraph
    if len(line) < 80 and line_num + 1 < len(all_lines):
        next_line = all_lines[line_num + 1].strip()
        if len(next_line) > 100:  # Next line is much longer
            # Check if current line looks like a title
            if not line.endswith('.') and len(line.split()) <= 10:
                return {'text': line, 'level': 2}
    
    return None


def find_next_heading(lines: List[str], start_idx: int) -> int:
    """Find the index of the next heading"""
    for i in range(start_idx, len(lines)):
        if detect_heading(lines[i].strip(), i, lines):
            return i
    return len(lines)


def get_heading_content(document_id: int, heading_ids: List[str]) -> str:
    """
    Get the content for selected headings
    
    Args:
        document_id: Document ID
        heading_ids: List of heading IDs to retrieve content for
        
    Returns:
        Combined content from all selected headings
    """
    try:
        document = Document.objects.get(id=document_id)
        headings = extract_document_headings(document_id)
        
        # Filter selected headings
        selected = [h for h in headings if h['id'] in heading_ids]
        
        # Extract content for each heading
        text = document.text_content
        content_parts = []
        
        for heading in selected:
            section_content = text[heading['start_pos']:heading['end_pos']]
            content_parts.append(f"## {heading['text']}\n{section_content}\n")
        
        combined = '\n'.join(content_parts)
        print(f"[RAG] Retrieved {len(combined)} chars from {len(selected)} headings")
        
        return combined
        
    except Exception as e:
        print(f"[ERROR] Failed to get heading content: {e}")
        return ""


def retrieve_relevant_chunks(query: str, document_id: int, k: int = 5) -> List[str]:
    """
    Retrieve relevant chunks from document using TF-IDF
    (Existing function - kept for backward compatibility)
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    try:
        document = Document.objects.get(id=document_id)
        text = document.text_content
        
        # Split into chunks
        chunks = [text[i:i+1000] for i in range(0, len(text), 800)]
        
        if not chunks:
            return []
        
        # TF-IDF vectorization
        vectorizer = TfidfVectorizer(stop_words='english')
        chunk_vectors = vectorizer.fit_transform(chunks)
        query_vector = vectorizer.transform([query])
        
        # Calculate similarity
        similarities = cosine_similarity(query_vector, chunk_vectors)[0]
        
        # Get top k chunks
        top_indices = similarities.argsort()[-k:][::-1]
        top_chunks = [chunks[i] for i in top_indices if similarities[i] > 0]
        
        return top_chunks
        
    except Exception as e:
        print(f"[ERROR] RAG retrieval failed: {e}")
        return []
