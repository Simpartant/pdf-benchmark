"""Text utilities."""

import re
from typing import Dict, Any


def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Text to count words in
        
    Returns:
        Word count
    """
    if not text:
        return 0
    
    # Split on whitespace and count non-empty tokens
    words = text.split()
    return len([w for w in words if w.strip()])


def count_characters(text: str) -> int:
    """
    Count characters in text (excluding whitespace).
    
    Args:
        text: Text to count characters in
        
    Returns:
        Character count
    """
    if not text:
        return 0
    
    return len(text.replace(" ", "").replace("\n", "").replace("\t", ""))


def extract_text_stats(text: str) -> Dict[str, Any]:
    """
    Extract statistics from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with text statistics
    """
    return {
        "total_chars": len(text),
        "chars_no_space": count_characters(text),
        "word_count": count_words(text),
        "line_count": text.count("\n") + 1 if text else 0,
        "paragraph_count": len([p for p in text.split("\n\n") if p.strip()]),
    }


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing excessive whitespace.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple newlines with double newline
    text = re.sub(r'\n\n+', '\n\n', text)
    
    # Remove trailing/leading whitespace
    text = text.strip()
    
    return text
