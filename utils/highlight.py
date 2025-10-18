# utils/highlight.py

import re

def highlight_keywords(text: str, keywords: list[str]) -> str:
    """
    Wraps keywords in a text with HTML <mark> tags.
    This version is robust and handles case-insensitivity and punctuation correctly.
    """
    if not text or not keywords:
        return text

    # Clean and prepare keywords, removing any empty strings
    clean_keywords = [k.strip() for k in keywords if k.strip()]
    if not clean_keywords:
        return text

    # Join keywords into a regex pattern.
    # We use a negative lookahead (?![A-Za-z0-9]) to ensure we match whole words.
    # This matches the keyword as long as it's NOT followed by a letter or number.
    # This is more robust than \b for handling punctuation like ":".
    pattern = re.compile(r'(' + '|'.join(map(re.escape, clean_keywords)) + r')(?![A-Za-z0-9])', re.IGNORECASE)

    # The replacement function preserves the original casing of the matched word
    def replacer(match):
        return f"<mark>{match.group(0)}</mark>"

    # Perform the substitution
    highlighted_text = pattern.sub(replacer, text)
    
    return highlighted_text