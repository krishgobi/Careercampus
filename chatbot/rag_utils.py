"""
RAG (Retrieval-Augmented Generation) Utilities
Handles document chunking, embedding, and semantic search
"""
import re
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer


class RAGEngine:
    """RAG engine for document-based question answering"""
    
    def __init__(self):
        """Initialize RAG engine with embedding model"""
        print("Loading embedding model...")
        # Use lightweight sentence transformer
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunks = []
        self.embeddings = None
        
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        # Add last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def index_document(self, text: str):
        """
        Index document for retrieval
        
        Args:
            text: Document text to index
        """
        print("Chunking document...")
        self.chunks = self.chunk_text(text)
        
        if not self.chunks:
            print("Warning: No chunks created from document")
            return
        
        print(f"Created {len(self.chunks)} chunks")
        print("Generating embeddings...")
        
        # Generate embeddings for all chunks
        self.embeddings = self.embedder.encode(
            self.chunks,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        print("Document indexed successfully")
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Search for relevant chunks
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of (chunk, score) tuples
        """
        if self.embeddings is None or len(self.chunks) == 0:
            print("Warning: No document indexed")
            return []
        
        # Embed query
        query_embedding = self.embedder.encode(
            [query],
            show_progress_bar=False,
            convert_to_numpy=True
        )[0]
        
        # Calculate cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return chunks with scores
        results = [
            (self.chunks[idx], float(similarities[idx]))
            for idx in top_indices
        ]
        
        return results
    
    def get_context(self, query: str, top_k: int = 3) -> str:
        """
        Get relevant context for query
        
        Args:
            query: User question
            top_k: Number of chunks to retrieve
            
        Returns:
            Concatenated context string
        """
        results = self.search(query, top_k)
        
        if not results:
            return ""
        
        # Build context from top results
        context_parts = []
        for i, (chunk, score) in enumerate(results, 1):
            context_parts.append(f"[Context {i}]: {chunk}")
        
        return "\n\n".join(context_parts)


# Global RAG engine instance
_rag_engine = None


def get_rag_engine() -> RAGEngine:
    """Get or create global RAG engine instance"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
