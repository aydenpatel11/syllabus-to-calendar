"""
Business logic service layer.

Contains the core processing logic without API concerns.
"""

from pathlib import Path
from typing import List

from .extract_text import extract_text
from .extract_events import extract_events
from .normalize_events import normalize_events
from .schemas import AcademicEvent


def process_syllabus(file_path: Path) -> List[AcademicEvent]:
    """
    Process a syllabus file and return normalized events.
    
    This is the core business logic - no API concerns here.
    
    Args:
        file_path: Path to the syllabus file (PDF or text)
        
    Returns:
        List of normalized AcademicEvent objects
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If file type is unsupported or processing fails
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Syllabus file not found: {file_path}")
    
    # Step 1: Extract text from syllabus
    text = extract_text(file_path)
    
    # Step 2: Extract events from text
    raw_events = extract_events(text)
    
    # Step 3: Normalize and validate events
    normalized_events = normalize_events(raw_events)
    
    return normalized_events
