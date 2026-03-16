"""
Configuration settings for the application.
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Sample syllabi directory
SAMPLE_SYLLABI_DIR = PROJECT_ROOT / "sample_syllabi"

# Google Calendar API settings 
GOOGLE_CALENDAR_CREDENTIALS_PATH = os.getenv(
    "GOOGLE_CALENDAR_CREDENTIALS_PATH",
    PROJECT_ROOT / "credentials.json"
)
GOOGLE_CALENDAR_TOKEN_PATH = os.getenv(
    "GOOGLE_CALENDAR_TOKEN_PATH",
    PROJECT_ROOT / "token.json"
)

GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.events']
GOOGLE_CALENDAR_ID = 'primary'
