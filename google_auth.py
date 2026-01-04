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
        # 1. Try environment variables (for Vercel)
        token_json_env = os.environ.get('GOOGLE_TOKEN_JSON')
        creds_json_env = os.environ.get('GOOGLE_CREDENTIALS_JSON')

        if token_json_env:
            # Load from env var
            import json
            info = json.loads(token_json_env)
            self.creds = Credentials.from_authorized_user_info(info, SCOPES)
        
        # 2. Try local file if env var didn't work or expired
        if not self.creds and os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # 3. Validation and Refresh
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # If we have credentials env var but no token yet
                if creds_json_env:
                     import json
                     info = json.loads(creds_json_env)
                     flow = InstalledAppFlow.from_client_config(info, SCOPES)
                     # Note: This requires a browser, which won't work on Vercel backend
                     # But useful for local dev with env vars
                     self.creds = flow.run_local_server(port=8080)
                else:
                    # Fallback to local file
                    if os.path.exists('credentials.json'):
                        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                        self.creds = flow.run_local_server(port=8080)
            
            # Only save to file if we are NOT on Vercel (simple check: if we started with local files)
            # Or just wrap in try-except
            try:
                with open('token.json', 'w') as token:
                    token.write(self.creds.to_json())
            except Exception:
                # Likely read-only filesystem on Vercel
                pass
        
        self.gmail_service = build('gmail', 'v1', credentials=self.creds)
        self.calendar_service = build('calendar', 'v3', credentials=self.creds)
        
        return self.gmail_service, self.calendar_service
