# services/openrouter_service.py

import os
import time
from openai import OpenAI
from utils.logger import logger

def get_openai_client():
    """Initializes and returns the OpenAI client for OpenRouter."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("FATAL ERROR: OPENROUTER_API_KEY not found in environment variables.")
    return OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
# services/openrouter_service.py

def summarize_chunk(text_chunk: str) -> str:
    """Summarizes a chunk of text using an OpenRouter model."""
    client = get_openai_client()
    model = os.getenv("SUMMARIZATION_MODEL", "mistralai/mistral-small-3.2-24b-instruct")
    
    prompt = f"""
    You are an expert assistant summarizing Indian government schemes for official documentation.
    
    Summarize the following text from a government scheme webpage in the EXACT format below:
    
    Consolidated Summary: [Extract the scheme name from the content]
    
    1. Eligibility
    
    Who can apply (age, gender, income, occupation, etc.)
    
    Required conditions (BPL, disability, widowhood, etc.)
    
    2. Benefits
    
    Financial benefits and assistance amounts
    
    Mode of transfer (DBT, PFMS, etc.)
    
    Monitoring or review mechanisms (if any)
    
    3. How to Apply
    
    Application steps
    
    Where to apply (Gram Panchayat, online portal, etc.)
    
    Required documents
    
    Approval and disbursement process
    
    4. Additional Information (if available)
    
    Scheme objectives
    
    Implementing ministry/department
    
    Helpline or grievance redressal mechanism
    
    IMPORTANT GUIDELINES:
    - Use official government-style tone
    - Avoid redundant text or assumptions
    - If information is not available, write "Not specified on the site"
    - Extract the actual scheme name from the content
    - Be precise and factual
    
    Text to summarize:
    ---
    {text_chunk}
    ---
    
    Summary:
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes government schemes in official format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error calling OpenRouter API for summarization: {e}")
        # Add retry logic for rate limiting
        if "rate limit" in str(e).lower():
            logger.info("Rate limit reached, waiting 5 seconds...")
            time.sleep(5)
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that summarizes government schemes in official format."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                )
                return response.choices[0].message.content.strip()
            except Exception as retry_e:
                logger.error(f"Retry failed: {retry_e}")
        return "Error: Could not generate summary due to an API issue."

def consolidate_summaries(chunk_summaries: list[str]) -> str:
    """Consolidate multiple summaries into a single comprehensive summary."""
    client = get_openai_client()
    model = os.getenv("SUMMARIZATION_MODEL", "mistralai/mistral-small-3.2-24b-instruct")
    
    combined_text = "\n\n---\n\n".join(chunk_summaries)
    
    prompt = f"""
    You are an expert editor consolidating multiple summaries of an Indian government scheme.
    
    Combine the following summaries into ONE comprehensive summary in the EXACT format below:
    
    Consolidated Summary: [Scheme Name]
    
    1. Eligibility
    
    Who can apply (age, gender, income, occupation, etc.)
    
    Required conditions (BPL, disability, widowhood, etc.)
    
    2. Benefits
    
    Financial benefits and assistance amounts
    
    Mode of transfer (DBT, PFMS, etc.)
    
    Monitoring or review mechanisms (if any)
    
    3. How to Apply
    
    Application steps
    
    Where to apply (Gram Panchayat, online portal, etc.)
    
    Required documents
    
    Approval and disbursement process
    
    4. Additional Information (if available)
    
    Scheme objectives
    
    Implementing ministry/department
    
    Helpline or grievance redressal mechanism
    
    IMPORTANT GUIDELINES:
    - Use official government-style tone
    - Avoid redundant text or assumptions
    - If information is not available, write "Not specified on the site"
    - Ensure all sections are properly formatted
    - Remove any duplicate information
    - Be precise and factual
    
    Summaries to consolidate:
    ---
    {combined_text}
    ---
    
    Final Consolidated Summary:
    """
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert editor that consolidates government scheme summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error consolidating summaries: {e}")
        return "\n\n".join(chunk_summaries)  # Fallback to join summaries

def translate_text(text: str) -> str:
    """Translates English text to Telugu using an OpenRouter model."""
    client = get_openai_client()
    model = os.getenv("TRANSLATION_MODEL", "google/gemma-3-27b-instruct")

    prompt = f"""
    Translate the following English text to Telugu.
    Preserve the structure, including bullet points and headings.
    Only provide the translated Telugu text, nothing else.

    English Text:
    ---
    {text}
    ---

    Telugu Translation:
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a precise translator from English to Telugu."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error calling OpenRouter API for translation: {e}")
        # Add retry logic for rate limiting
        if "rate limit" in str(e).lower():
            logger.info("Rate limit reached, waiting 5 seconds...")
            time.sleep(5)
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a precise translator from English to Telugu."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                )
                return response.choices[0].message.content.strip()
            except Exception as retry_e:
                logger.error(f"Retry failed: {retry_e}")
        return "Error: Could not translate due to an API issue."

def get_embedding(text: str) -> list[float] | None:
    """Generates an embedding for a given text using an OpenRouter model."""
    client = get_openai_client()
    model = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")
    
    try:
        # Clean and truncate text if too long
        text = text.strip()
        if len(text) > 8000:
            text = text[:8000]
            logger.info("Text truncated for embedding generation")
        
        response = client.embeddings.create(
            model=model,
            input=text
        )
        embedding = response.data[0].embedding
        logger.info(f"Successfully generated embedding of length: {len(embedding)}")
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        # Add retry logic
        if "rate limit" in str(e).lower():
            logger.info("Rate limit reached for embeddings, waiting 10 seconds...")
            time.sleep(10)
            try:
                response = client.embeddings.create(
                    model=model,
                    input=text
                )
                embedding = response.data[0].embedding
                logger.info(f"Successfully generated embedding on retry: {len(embedding)}")
                return embedding
            except Exception as retry_e:
                logger.error(f"Embedding retry failed: {retry_e}")
        return None

def answer_question(question: str, context: str) -> str:
    """Enhanced Q&A with better prompt."""
    client = get_openai_client()
    model = os.getenv("QA_MODEL", "mistralai/mistral-7b-instruct")

    if len(context) > 4000:
        context = context[:4000] + "..."

    prompt = f"""
    You are an expert assistant for Indian government schemes.
    
    Answer the following question based ONLY on the provided context.
    Be specific, accurate, and include any relevant details from the context.
    
    If the context doesn't contain the answer, say: "I couldn't find this information in the document."
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant answering questions based on a given context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error calling OpenRouter API for Q&A: {e}")
        # Add retry logic
        if "rate limit" in str(e).lower():
            logger.info("Rate limit reached for Q&A, waiting 5 seconds...")
            time.sleep(5)
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant answering questions based on a given context."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                )
                return response.choices[0].message.content.strip()
            except Exception as retry_e:
                logger.error(f"Q&A retry failed: {retry_e}")
        return "Error: Could not generate an answer due to an API issue."