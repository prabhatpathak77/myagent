import base64
from email.mime.text import MIMEText
from datetime import datetime


class GmailHandler:
    def __init__(self, service):
        self.service = service
    
    def get_unread_emails(self, max_results=10):
        """Fetch unread emails"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email_data = self.get_email_details(msg['id'])
                emails.append(email_data)
            
            return emails
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def get_email_details(self, msg_id):
        """Get detailed email information"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            body = self._get_email_body(message['payload'])
            thread_id = message.get('threadId', msg_id)
            
            return {
                'id': msg_id,
                'thread_id': thread_id,
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body
            }
        except Exception as e:
            print(f"Error getting email details: {e}")
            return None
    
    def _get_email_body(self, payload):
        """Extract email body from payload"""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    return base64.urlsafe_b64decode(data).decode('utf-8')
        elif 'body' in payload:
            data = payload['body'].get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')
        return ''
    
    def mark_as_read(self, msg_id):
        """Mark email as read"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
        except Exception as e:
            print(f"Error marking email as read: {e}")
    
    def send_email(self, to, subject, body, thread_id=None):
        """Send an email, optionally as a reply in a thread"""
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            send_body = {'raw': raw}
            if thread_id:
                send_body['threadId'] = thread_id
            
            self.service.users().messages().send(
                userId='me',
                body=send_body
            ).execute()
            print(f"Email sent to {to}")
        except Exception as e:
            print(f"Error sending email: {e}")
