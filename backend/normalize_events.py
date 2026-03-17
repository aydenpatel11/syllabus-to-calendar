"""
Event normalization and quality control module.

Handles cleaning, validation, and confidence scoring of extracted events.
"""

from typing import List, Tuple
from datetime import date, datetime
from .schemas import AcademicEvent, EventType
import re


def normalize_title(title: str, event_type: EventType) -> str:
    """
    Clean and normalize event titles.
    
    Args:
        title: Raw title from extraction
        event_type: Type of event (for context-aware cleaning)
        
    Returns:
        Normalized title string
    """
    if not title or title.strip() == "":
        return title
    
    # Remove all colons
    title = title.replace(':', '').strip()
    
    # Remove the word "Due" (always redundant, case-insensitive)
    title = re.sub(r'\b[Dd]ue\b', '', title).strip()
    
    # Context-aware word removal based on event_type
    if event_type in [EventType.ASSIGNMENT, EventType.DEADLINE]:
        # Only remove "Assignment" or "Homework" if followed by substantial text (not just numbers)
        if re.match(r'^(?:Assignment|Homework)\s*[:]\s*.+', title, re.IGNORECASE):
            title = re.sub(r'^(?:Assignment|Homework)\s*[:]\s*', '', title, flags=re.IGNORECASE).strip()
    elif event_type == EventType.EXAM:
        # Remove "Exam" only if it's at the end and there's descriptive content
        if re.search(r'\b(?:Midterm|Final|Mid-term)\s+Exam\b', title, re.IGNORECASE):
            title = re.sub(r'\s+Exam\b', '', title, flags=re.IGNORECASE).strip()
    elif event_type == EventType.QUIZ:
        # Remove "Quiz" if it's clearly redundant (e.g., "Quiz Quiz" -> "Quiz")
        title = re.sub(r'\bQuiz\s+Quiz\b', 'Quiz', title, flags=re.IGNORECASE).strip()
    
    # Clean up any extra whitespace
    title = re.sub(r'\s+', ' ', title).strip()
    
    # Title case 
    title = title.title()
    
    # Remove only trailing punctuation 
    title = re.sub(r'[^\w\s]+$', '', title).strip()
    
    # Final whitespace cleanup
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title


def validate_event(event: AcademicEvent) -> Tuple[bool, List[str]]:
    """
    Validate an event and return warnings.
    
    Args:
        event: Event to validate
        
    Returns:
        Tuple of (is_valid, list_of_warnings)
        - is_valid: True if event passes basic checks
        - list_of_warnings: List of warning messages
    """
    warnings = []
    is_valid = True
    
    # Check required fields
    if not event.title or event.title.strip() == "" or event.title.lower() == "event":
        warnings.append("Title is missing or default")
        is_valid = False
    
    if not event.start_date:
        warnings.append("Start date is missing")
        is_valid = False
        return (is_valid, warnings)  # Can't validate further without date
    
    if not event.event_type:
        warnings.append("Event type is missing")
        is_valid = False
    
    # Check date validity
    today = date.today()
    days_diff = (event.start_date - today).days
    
    if days_diff < 0:
        if days_diff < -90:  # More than 3 months ago
            warnings.append(f"Date is {abs(days_diff)} days in the past")
        else:
            warnings.append("Date is in the past (might be from previous semester)")
    
    if days_diff > 730:  # More than 2 years
        warnings.append("Date is more than 2 years in the future")
    
    # Check end_date if provided
    if event.end_date:
        if event.end_date < event.start_date:
            warnings.append("End date is before start date")
            is_valid = False
    
    # Check time validity
    if event.start_time and event.end_time:
        if event.end_time < event.start_time and event.start_date == event.end_date:
            warnings.append("End time is before start time on same day")
    
    # Check title length
    if event.title:
        if len(event.title) < 3:
            warnings.append("Title is very short")
        elif len(event.title) > 100:
            warnings.append("Title is very long (might contain extra text)")
    
    return (is_valid, warnings)


def remove_duplicate_events(events: List[AcademicEvent]) -> List[AcademicEvent]:
    """
    Remove duplicate events from a list.
    
    Args:
        events: List of events
        
    Returns:
        List with duplicates removed
    """
    if not events:
        return events
    
    seen = set()
    unique_events = []
    
    for event in events:
        # Create a key based on title and date (exact match)
        key = (event.title.lower().strip(), event.start_date)
        
        if key not in seen:
            seen.add(key)
            unique_events.append(event)
        else:
            # Duplicate found - skip the duplicate
            continue
    
    return unique_events


def normalize_events(events: List[AcademicEvent]) -> List[AcademicEvent]:
    """
    Main function: normalize and validate a list of events.
    
    This is the entry point that orchestrates all normalization steps.
    
    Args:
        events: Raw list of extracted events
        
    Returns:
        Normalized and validated list of events
    """
    if not events:
        return events
    
    normalized = []
    
    for event in events:
        # Step 1: Normalize title
        event.title = normalize_title(event.title, event.event_type)
        
        # Step 2: Validate event
        is_valid, warnings = validate_event(event)
        
        # Add warnings to description if any
        if warnings:
            warning_text = f"Warnings: {', '.join(warnings)}"
            if event.description:
                event.description = f"{event.description}\n{warning_text}"
            else:
                event.description = warning_text
        
        # Only add if valid
        if is_valid:
            normalized.append(event)
    
    # Step 4: Remove duplicates
    normalized = remove_duplicate_events(normalized)
    
    # Step 5: Sort by date for consistency
    normalized.sort(key=lambda e: e.start_date)
    
    return normalized
