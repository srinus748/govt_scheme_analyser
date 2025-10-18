# services/scheme_detector.py

import re
from typing import List, Dict, Tuple
from utils.logger import logger

class SchemeDetector:
    def __init__(self):
        # Common scheme indicators
        self.scheme_indicators = [
            r'(?:Scheme|Yojana|Programme|Project|Plan)\s*[:\-]?\s*([^\n]+)',
            r'(?:Pradhan Mantri|PM)\s+([A-Za-z\s]+(?:Scheme|Yojana))',
            r'([A-Z][a-zA-Z\s]*(?:Scheme|Yojana|Programme|Plan))',
            r'Jeevan\s+([A-Za-z\s]+)',  # For LIC schemes
            r'Atal\s+([A-Za-z\s]+)',  # For Atal schemes
            r'Sukanya\s+([A-Za-z\s]+)',  # For Sukanya schemes
        ]
        
        # Section separators
        self.section_separators = [
            r'\n\s*\n',
            r'---+',
            r'===+',
            r'\*\*\*+',
        ]
    
    def detect_schemes(self, text: str) -> List[Dict]:
        """
        Detect and separate multiple schemes from a single text.
        
        Returns:
            List of dictionaries, each containing a scheme's information
        """
        logger.info("Detecting multiple schemes in the text...")
        
        # First, try to find scheme boundaries
        scheme_sections = self._find_scheme_sections(text)
        
        if len(scheme_sections) > 1:
            logger.info(f"Found {len(scheme_sections)} potential schemes")
            return self._process_scheme_sections(scheme_sections)
        else:
            # If clear separation not found, try keyword-based detection
            return self._extract_schemes_by_keywords(text)
    
    def _find_scheme_sections(self, text: str) -> List[str]:
        """Find potential scheme sections in the text."""
        sections = []
        
        # Look for scheme headers
        scheme_positions = []
        for pattern in self.scheme_indicators:
            matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
            for match in matches:
                scheme_positions.append((match.start(), match.group(1)))
        
        # Sort by position
        scheme_positions.sort(key=lambda x: x[0])
        
        # Extract sections between scheme headers
        for i, (start, name) in enumerate(scheme_positions):
            end_pos = scheme_positions[i + 1][0] if i + 1 < len(scheme_positions) else len(text)
            section_text = text[start:end_pos].strip()
            sections.append(section_text)
        
        return sections
    
    def _process_scheme_sections(self, sections: List[str]) -> List[Dict]:
        """Process detected scheme sections."""
        schemes = []
        
        for section in sections:
            # Extract scheme name
            scheme_name = self._extract_scheme_name(section)
            
            # Extract content for this scheme
            scheme_content = self._clean_scheme_content(section)
            
            if len(scheme_content) > 100:  # Only include substantial content
                schemes.append({
                    'name': scheme_name,
                    'content': scheme_content,
                    'word_count': len(scheme_content.split())
                })
        
        return schemes
    
    def _extract_schemes_by_keywords(self, text: str) -> List[Dict]:
        """Extract schemes using keyword-based approach."""
        # Split text by major headings
        potential_schemes = re.split(r'\n[A-Z][A-Z\s]{10,}\n', text)
        
        schemes = []
        for i, section in enumerate(potential_schemes):
            if len(section.strip()) > 200:  # Substantial content
                # Try to find a scheme name in this section
                scheme_name = self._extract_scheme_name(section)
                
                if not scheme_name:
                    scheme_name = f"Scheme {i + 1}"
                
                schemes.append({
                    'name': scheme_name,
                    'content': section.strip(),
                    'word_count': len(section.split())
                })
        
        return schemes
    
    def _extract_scheme_name(self, text: str) -> str:
        """Extract scheme name from text."""
        for pattern in self.scheme_indicators:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up the name
                name = re.sub(r'[:\-]\s*$', '', name)  # Remove trailing colon or dash
                name = re.sub(r'\s+', ' ', name)  # Normalize spaces
                return name
        
        # If no pattern matches, try to get the first line
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 5 and len(line) < 100:
                # Check if it looks like a title
                if any(word in line.upper() for word in ['SCHEME', 'YOJANA', 'PLAN', 'PROGRAMME']):
                    return line
        
        return "Unknown Scheme"
    
    def _clean_scheme_content(self, text: str) -> str:
        """Clean and format scheme content."""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # Remove common navigation elements
        text = re.sub(r'(?:Home|About Us|Contact|Login|Register)[\s\n]*', '', text, flags=re.IGNORECASE)
        
        # Remove URLs and emails
        text = re.sub(r'https?://[^\s<>"{}|\\^`[\]]+', '', text)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Clean up extra spaces
        text = re.sub(r' +', ' ', text)
        
        return text.strip()