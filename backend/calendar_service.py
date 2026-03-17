"""
Google Calendar integration service.

Handles authentication and event creation for Google Calendar API.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .schemas import AcademicEvent
from .config import (
    GOOGLE_CALENDAR_CREDENTIALS_PATH,
    GOOGLE_CALENDAR_TOKEN_PATH,
    GOOGLE_CALENDAR_SCOPES,
    GOOGLE_CALENDAR_ID
)

def authenticate_google_calendar():
    """Authenticate with Google Calendar API."""
    creds = None
    if GOOGLE_CALENDAR_TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(GOOGLE_CALENDAR_TOKEN_PATH, GOOGLE_CALENDAR_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CALENDAR_CREDENTIALS_PATH, GOOGLE_CALENDAR_SCOPES)
            creds = flow.run_local_server(port=0)
            with open(GOOGLE_CALENDAR_TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
    
    service = build('calendar', 'v3', credentials=creds)

    return service

def convert_to_google_calendar_event(event: AcademicEvent) -> dict:
    """Convert AcademicEvent to Google Calendar event format."""
    google_event = {
        'summary': event.title,
        'description': event.description or f"{event.event_type.value} event",
        'location': event.location or '',
    }
    
    # Handle all-day and timed events
    if event.is_all_day or event.start_time is None:
        # All-day event
        google_event['start'] = {
            'date': event.start_date.isoformat(),
            'timeZone': 'America/Los_Angeles', 
        }
        google_event['end'] = {
            'date': (event.end_date or event.start_date).isoformat(),
            'timeZone': 'America/Los_Angeles',
        }
    else:
        # Timed event
        start_datetime = datetime.combine(event.start_date, event.start_time)
        
        # If no end time, default to 1 hour later
        if event.end_time:
            end_datetime = datetime.combine(
                event.end_date or event.start_date, 
                event.end_time
            )
        else:
            end_datetime = start_datetime + timedelta(hours=1)
        
        google_event['start'] = {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'America/New_York',
        }
        google_event['end'] = {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'America/New_York',
        }
    
    return google_event

def add_events_to_calendar(events: List[AcademicEvent]) -> dict:
    """Add multiple events to Google Calendar."""
    try:
        service = authenticate_google_calendar()
    except Exception as e:
        return {
            'success': False,
            'error': f'Authentication failed: {str(e)}',
            'created': [],
            'failed': []
        }
    
    # Step 2: Create each event
    created = []
    failed = []
    
    for event in events:
        try:
            # Convert to Google format
            google_event = convert_to_google_calendar_event(event)
            
            # Create in calendar
            created_event = service.events().insert(
                calendarId=GOOGLE_CALENDAR_ID,
                body=google_event
            ).execute()
            
            created.append({
                'title': event.title,
                'date': event.start_date.isoformat(),
                'calendar_id': created_event.get('id'),
                'link': created_event.get('htmlLink')
            })
            
        except HttpError as e:
            failed.append({
                'title': event.title,
                'error': str(e)
            })
    
    # Step 3: Return results
    return {
        'success': len(failed) == 0,
        'total': len(events),
        'created': created,
        'failed': failed
    }