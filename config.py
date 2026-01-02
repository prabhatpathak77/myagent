import os
from dotenv import load_dotenv

load_dotenv()

# Google API settings
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar'
]

# Google Gemini settings
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Agent settings
CHECK_INTERVAL_MINUTES = 5  # How often to check for new emails
REMINDER_HOURS_BEFORE = 1    # Send reminder X hours before meeting
MAX_EMAILS_TO_PROCESS = 10   # Max emails to process per run
