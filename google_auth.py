import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import SCOPES


class GoogleAuthManager:
    def __init__(self):
        self.creds = None
        self.gmail_service = None
        self.calendar_service = None
    
    def authenticate(self):
        """Authenticate with Google APIs"""
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=8080)
            
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        
        self.gmail_service = build('gmail', 'v1', credentials=self.creds)
        self.calendar_service = build('calendar', 'v3', credentials=self.creds)
        
        return self.gmail_service, self.calendar_service
