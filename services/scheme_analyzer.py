# services/scheme_analyzer.py

import re
from typing import Dict, List, Tuple
from utils.logger import logger
from services.openrouter_service import summarize_chunk, consolidate_summaries
from utils.text_chunker import chunk_text_simple

class SchemeAnalyzer:
    def __init__(self):
        self.confidence_score = 0.0
        self.scheme_name = ""
        self.missing_sections = []
        
    def analyze_scheme(self, text: str, url: str = "") -> Dict:
        """
        Analyze scheme content and generate a comprehensive summary.
        
        Args:
            text: Extracted text from the webpage
            url: URL of the webpage (for extracting scheme name)
            
        Returns:
            Dictionary containing summary, confidence score, and metadata
        """
        logger.info("Starting scheme analysis...")
        
        # Extract scheme name from URL or text
        self.scheme_name = self._extract_scheme_name(text, url)
        
        # Split text into chunks
        chunks = chunk_text_simple(text, max_chunk_size=3000, overlap=300)
        logger.info(f"Processing {len(chunks)} chunks for analysis")
        
        # Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Analyzing chunk {i+1}/{len(chunks)}")
            summary = summarize_chunk(chunk)
            if not summary.startswith("Error:"):
                chunk_summaries.append(summary)
        
        if not chunk_summaries:
            return {
                "summary": "Error: Could not analyze the scheme content.",
                "confidence_score": 0.0,
                "scheme_name": self.scheme_name,
                "missing_sections": ["All sections"],
                "word_count": len(text.split())
            }
        
        # Consolidate summaries
        final_summary = consolidate_summaries(chunk_summaries)
        
        # Calculate confidence score
        self.confidence_score = self._calculate_confidence_score(final_summary, text)
        
        # Identify missing sections
        self.missing_sections = self._identify_missing_sections(final_summary)
        
        # Extract structured data
        structured_data = self._extract_structured_data(final_summary)
        
        return {
            "summary": final_summary,
            "confidence_score": self.confidence_score,
            "scheme_name": self.scheme_name,
            "missing_sections": self.missing_sections,
            "structured_data": structured_data,
            "word_count": len(text.split()),
            "url": url
        }
    
    def _extract_scheme_name(self, text: str, url: str) -> str:
        """Extract scheme name from text or URL."""
        # Try to extract from common patterns in text
        patterns = [
            r'(?:Scheme|Yojana|Programme|Project):\s*([^\n]+)',
            r'([A-Z][a-zA-Z\s]*(?:Scheme|Yojana|Programme|Project))',
            r'Pradhan Mantri\s+([A-Za-z\s]+(?:Scheme|Yojana))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Try to extract from URL
        if url:
            url_parts = url.split('/')
            for part in url_parts:
                if any(keyword in part.lower() for keyword in ['scheme', 'yojana', 'pm']):
                    return part.replace('-', ' ').title()
        
        return "Unknown Scheme"
    
    def _calculate_confidence_score(self, summary: str, original_text: str) -> float:
        """Calculate confidence score based on summary quality."""
        score = 0.0
        
        # Check for required sections
        required_sections = [
            "Eligibility", "Benefits", "How to Apply", "Additional Information"
        ]
        
        for section in required_sections:
            if section.lower() in summary.lower():
                score += 0.2
        
        # Check for specific keywords
        keywords = [
            "apply", "eligible", "benefits", "documents", "amount", "process",
            "ministry", "department", "helpline", "grievance"
        ]
        
        keyword_count = sum(1 for keyword in keywords if keyword.lower() in summary.lower())
        score += (keyword_count / len(keywords)) * 0.2
        
        # Check summary length (should be substantial but not too long)
        summary_words = len(summary.split())
        if 100 <= summary_words <= 800:
            score += 0.2
        
        # Check for specific information (amounts, dates, etc.)
        if re.search(r'Rs\.\s*\d+|₹\s*\d+|\d{4}', summary):
            score += 0.1
        
        # Check for official language
        official_terms = [
            "government", "official", "portal", "authority", "approved",
            "verified", "guidelines", "procedure"
        ]
        official_count = sum(1 for term in official_terms if term.lower() in summary.lower())
        if official_count >= 2:
            score += 0.1
        
        return min(score, 1.0)
    
    def _identify_missing_sections(self, summary: str) -> List[str]:
        """Identify which sections are missing or incomplete."""
        missing = []
        
        sections = {
            "Eligibility": ["eligible", "who can apply", "criteria", "qualification"],
            "Benefits": ["benefit", "amount", "financial", "assistance", "support"],
            "How to Apply": ["apply", "application", "process", "steps", "procedure"],
            "Additional Information": ["objective", "ministry", "department", "helpline", "contact"]
        }
        
        for section, keywords in sections.items():
            if section.lower() not in summary.lower():
                # Check if any keywords are present
                if not any(keyword in summary.lower() for keyword in keywords):
                    missing.append(section)
        
        return missing
    
    def _extract_structured_data(self, summary: str) -> Dict:
        """Extract structured data from the summary."""
        structured = {
            "scheme_name": self.scheme_name,
            "eligibility": self._extract_section(summary, "Eligibility"),
            "benefits": self._extract_section(summary, "Benefits"),
            "application_process": self._extract_section(summary, "How to Apply"),
            "additional_info": self._extract_section(summary, "Additional Information")
        }
        
        # Extract specific details
        structured["financial_amounts"] = re.findall(r'(?:Rs\.|₹)\s*[\d,]+', summary)
        structured["contact_info"] = re.findall(r'(?:\+?\d{2,3}[-.\s]?)?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', summary)
        structured["websites"] = re.findall(r'https?://[^\s<>"{}|\\^`[\]]+', summary)
        
        return structured
    
    def _extract_section(self, summary: str, section_name: str) -> str:
        """Extract a specific section from the summary."""
        pattern = rf"{section_name}[.:]?\s*\n?(.*?)(?=\n\d+\.|\n[A-Z]|\Z)"
        match = re.search(pattern, summary, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return "Not specified"