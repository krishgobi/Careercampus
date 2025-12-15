"""
DistilGPT2 Handler with RAG Support
Handles local model inference with document context
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from .rag_utils import get_rag_engine


class DistilGPT2Handler:
    """Handler for DistilGPT2 model with RAG"""
    
    def __init__(self):
        """Initialize model and tokenizer"""
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self):
        """Load DistilGPT2 model and tokenizer"""
        if self.model is not None:
            return  # Already loaded
        
        print(f"Loading DistilGPT2 model on {self.device}...")
        
        self.tokenizer = AutoTokenizer.from_pretrained("distilbert/distilgpt2")
        self.model = AutoModelForCausalLM.from_pretrained("distilbert/distilgpt2")
        
        # Set padding token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Move to device
        self.model.to(self.device)
        self.model.eval()
        
        print("Model loaded successfully")
    
    def generate_response(
        self,
        question: str,
        context: str = "",
        max_length: int = 200,
        temperature: float = 0.7
    ) -> str:
        """
        Generate response using DistilGPT2 with optional context
        
        Args:
            question: User question
            context: Retrieved context from documents
            max_length: Maximum response length
            temperature: Sampling temperature
            
        Returns:
            Generated response
        """
        # Load model if not loaded
        if self.model is None:
            self.load_model()
        
        # Build prompt
        if context:
            prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {question}

Answer:"""
        else:
            prompt = f"Question: {question}\n\nAnswer:"
        
        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=inputs['input_ids'].shape[1] + max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
                num_return_sequences=1
            )
        
        # Decode
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract answer (remove prompt)
        if "Answer:" in response:
            answer = response.split("Answer:")[-1].strip()
        else:
            answer = response[len(prompt):].strip()
        
        return answer
    
    def chat_with_rag(self, question: str, document_text: str = None) -> str:
        """
        Chat with RAG support
        
        Args:
            question: User question
            document_text: Optional document text for RAG
            
        Returns:
            Generated answer
        """
        context = ""
        
        # Use RAG if document provided
        if document_text:
            print("Using RAG for context retrieval...")
            rag_engine = get_rag_engine()
            
            # Index document if not already indexed
            if not rag_engine.chunks:
                rag_engine.index_document(document_text)
            
            # Get relevant context
            context = rag_engine.get_context(question, top_k=3)
            print(f"Retrieved {len(context)} characters of context")
        
        # Generate response
        response = self.generate_response(question, context)
        
        return response


# Global handler instance
_handler = None


def get_distilgpt_handler() -> DistilGPT2Handler:
    """Get or create global DistilGPT2 handler"""
    global _handler
    if _handler is None:
        _handler = DistilGPT2Handler()
    return _handler
