"""Utility functions for audio processing."""

from pathlib import Path
from typing import Optional
from src.quotes import Quote

def generate_filename(voice: str, quote: Quote, index: int) -> str:
    """Generate filename following the convention.
    
    Args:
        voice: Voice name (Matthew/Stephen)
        quote: Quote to generate filename for
        index: Index of quote in its category/context
        
    Returns:
        Generated filename
    """
    # Clean text for filename (first few words)
    clean_text = "_".join(quote.text.split()[:3]).lower()
    clean_text = "".join(c for c in clean_text if c.isalnum() or c == "_")
    
    return f"{voice}_neural_{quote.category.value}_{quote.context}_{index:03d}_{clean_text}.wav" 