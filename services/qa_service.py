# services/qa_service.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils.text_chunker import chunk_text_simple
from services.openrouter_service import get_embedding, answer_question
from utils.logger import logger
import time
from typing import List, Tuple

class QAEngine:
    def __init__(self):
        self.text_chunks = []
        self.chunk_embeddings = []
        self.is_ready = False
        self.full_text = ""  # Store full text for fallback

    def process_document(self, full_text: str):
        """Enhanced document processing with better chunking and multiple embedding strategies."""
        logger.info("Processing document for Q&A...")
        try:
            self.full_text = full_text
            
            # Use larger chunks for better context
            self.text_chunks = chunk_text_simple(
                full_text, 
                max_chunk_size=2000,  # Increased from 1000
                overlap=300  # Increased from 200
            )
            
            if not self.text_chunks:
                logger.error("No text chunks created from document")
                return False
            
            # Generate embeddings for each chunk
            self.chunk_embeddings = []
            logger.info(f"Generating embeddings for {len(self.text_chunks)} chunks...")
            
            for i, chunk in enumerate(self.text_chunks):
                logger.info(f"Generating embedding for chunk {i+1}/{len(self.text_chunks)}")
                embedding = get_embedding(chunk)
                if embedding:
                    self.chunk_embeddings.append(embedding)
                else:
                    logger.warning(f"Failed to generate embedding for chunk {i+1}")
                    # Add a zero embedding as fallback
                    self.chunk_embeddings.append([0.0] * 1536)
            
            if len(self.chunk_embeddings) > 0:
                self.is_ready = True
                logger.info(f"Q&A engine is ready with {len(self.chunk_embeddings)} chunks.")
                return True
            else:
                logger.error("No embeddings were generated")
                return False
                
        except Exception as e:
            logger.error(f"Error processing document for Q&A: {e}")
            return False

    def ask(self, question: str) -> Tuple[str, str]:
        """Enhanced question answering with multiple context selection."""
        if not self.is_ready or not self.text_chunks:
            return "Error", "The Q&A engine is not ready. Please summarize a document first."
        
        if not question or not question.strip():
            return "Error", "Please enter a valid question."

        try:
            # Generate embedding for the user's question
            logger.info(f"Processing question: {question}")
            question_embedding = get_embedding(question)
            
            if not question_embedding:
                return self._fallback_answer(question)
            
            # Calculate similarities
            similarities = cosine_similarity([question_embedding], self.chunk_embeddings)[0]
            
            # Get top 3 most relevant chunks (instead of just 1)
            top_indices = np.argsort(similarities)[-3:][::-1]  # Get top 3 in descending order
            top_similarities = similarities[top_indices]
            
            logger.info(f"Top 3 similarities: {top_similarities}")
            
            # Check if best similarity is too low
            if top_similarities[0] < 0.5:  # Increased threshold from 0.3
                return self._fallback_answer(question)
            
            # Combine multiple relevant chunks for better context
            relevant_contexts = []
            for i, idx in enumerate(top_indices):
                if top_similarities[i] > 0.3:  # Still include chunks with decent similarity
                    relevant_contexts.append(self.text_chunks[idx])
            
            # Combine contexts with separators
            combined_context = "\n\n---\n\n".join(relevant_contexts)
            
            # Limit context length to avoid token limits
            if len(combined_context) > 6000:
                combined_context = combined_context[:6000] + "..."
            
            # Use enhanced QA prompt
            answer = self._enhanced_qa(question, combined_context)
            
            if answer.startswith("Error:"):
                return self._fallback_answer(question)
            
            return "Answer", answer
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return "Error", f"An error occurred while processing your question: {str(e)}"

    def _enhanced_qa(self, question: str, context: str) -> str:
        """Enhanced QA with better prompt engineering."""
        from services.openrouter_service import get_openai_client
        import os
        
        client = get_openai_client()
        model = os.getenv("QA_MODEL", "mistralai/mistral-small-3.2-24b-instruct")
        
        # Enhanced prompt with specific instructions
        prompt = f"""
        You are an expert assistant helping citizens understand Indian government schemes.
        
        Based on the provided context, answer the user's question accurately and completely.
        
        IMPORTANT GUIDELINES:
        1. Answer ONLY based on the information in the context
        2. If the context doesn't contain the answer, say "I couldn't find specific information about this in the document"
        3. Provide detailed, specific answers when possible
        4. Include relevant numbers, dates, amounts, or criteria mentioned in the context
        5. Structure your answer clearly with bullet points if listing multiple items
        6. Keep the language simple and easy to understand
        
        Context from government scheme document:
        ---
        {context}
        ---
        
        User's Question: {question}
        
        Answer:
        """
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that accurately answers questions about government schemes based only on the provided context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Lower temperature for more consistent answers
                max_tokens=1000   # Limit response length
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error in enhanced QA: {e}")
            return "Error: Could not generate an answer due to an API issue."

    def _fallback_answer(self, question: str) -> Tuple[str, str]:
        """Improved fallback with better keyword matching."""
        question_lower = question.lower()
        
        # Define keyword patterns for common question types
        patterns = {
            'eligibility': ['eligible', 'eligibility', 'who can apply', 'criteria', 'qualification'],
            'benefits': ['benefit', 'benefits', 'advantage', 'what will i get', 'amount'],
            'apply': ['apply', 'application', 'how to', 'process', 'register'],
            'documents': ['documents', 'papers', 'required', 'need'],
            'deadline': ['last date', 'deadline', 'when', 'time']
        }
        
        # Find the most relevant pattern
        best_category = None
        best_score = 0
        
        for category, keywords in patterns.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > best_score:
                best_score = score
                best_category = category
        
        # Search for relevant chunks based on category
        if best_category:
            relevant_chunks = []
            for chunk in self.text_chunks:
                chunk_lower = chunk.lower()
                if any(keyword in chunk_lower for keyword in patterns[best_category]):
                    relevant_chunks.append(chunk)
            
            if relevant_chunks:
                # Return the most relevant chunk
                best_chunk = max(relevant_chunks, key=lambda x: len(x))
                return "Answer", f"Based on the document, here's what I found about {best_category}:\n\n{best_chunk[:500]}..."
        
        # Final fallback - search for any keyword match
        keywords = question_lower.split()
        best_chunk = ""
        best_score = 0
        
        for chunk in self.text_chunks:
            chunk_lower = chunk.lower()
            score = sum(1 for keyword in keywords if keyword in chunk_lower)
            if score > best_score:
                best_score = score
                best_chunk = chunk
        
        if best_score > 0:
            return "Answer", f"Based on the document, here's relevant information:\n\n{best_chunk[:400]}..."
        else:
            return "Answer", "I couldn't find specific information about your question in the document. Please try asking about eligibility criteria, benefits, or the application process."

    def get_relevant_snippets(self, question: str, max_snippets: int = 3) -> List[str]:
        """Get relevant text snippets for a question (useful for debugging)."""
        if not self.is_ready:
            return []
        
        question_embedding = get_embedding(question)
        if not question_embedding:
            return []
        
        similarities = cosine_similarity([question_embedding], self.chunk_embeddings)[0]
        top_indices = np.argsort(similarities)[-max_snippets:][::-1]
        
        snippets = []
        for idx in top_indices:
            if similarities[idx] > 0.3:
                snippets.append(self.text_chunks[idx])
        
        return snippets