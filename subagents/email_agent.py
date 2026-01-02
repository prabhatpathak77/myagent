from subagents.base_agent import BaseAgent
from gmail_handler import GmailHandler
import json


class EmailAgent(BaseAgent):
    """Subagent responsible for email operations"""
    
    def __init__(self, gmail_service):
        super().__init__("EmailAgent", "Email Management Specialist")
        self.gmail = GmailHandler(gmail_service)
    
    def process(self, task):
        """Process email-related tasks"""
        task_type = task.get('type')
        
        if task_type == 'summarize':
            return self._summarize_emails(task.get('max_emails', 10))
        elif task_type == 'extract_meetings':
            return self._extract_meeting_requests(task.get('emails', []))
        elif task_type == 'send':
            return self._send_email(task.get('to'), task.get('subject'), task.get('body'))
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    def _summarize_emails(self, max_emails):
        """Fetch and summarize unread emails"""
        print(f"[{self.name}] Fetching unread emails...")
        emails = self.gmail.get_unread_emails(max_results=max_emails)
        
        if not emails:
            return self.report_to_coordinator({
                'summary': 'No unread emails',
                'count': 0,
                'emails': []
            })
        
        # Use Gemini to summarize
        email_texts = []
        for email in emails:
            email_texts.append(
                f"From: {email['sender']}\n"
                f"Subject: {email['subject']}\n"
                f"Body: {email['body'][:300]}..."
            )
        
        prompt = f"""You are an email assistant. Summarize these {len(emails)} emails concisely.
Highlight important emails and action items.

Emails:
{chr(10).join(email_texts)}

Provide a brief, actionable summary."""
        
        try:
            summary = self.generate_with_retry(prompt)
        except Exception as e:
            summary = f"Error generating summary: {e}"
        
        return self.report_to_coordinator({
            'summary': summary,
            'count': len(emails),
            'emails': emails
        })
    
    def _extract_meeting_requests(self, emails):
        """Extract meeting information from emails"""
        print(f"[{self.name}] Analyzing emails for meeting requests...")
        meeting_requests = []
        
        for email in emails:
            prompt = f"""Analyze this email for meeting requests.

Subject: {email['subject']}
Body: {email['body']}

If this contains a meeting request, respond with JSON:
{{
    "is_meeting": true,
    "title": "meeting title",
    "date": "YYYY-MM-DD",
    "time": "HH:MM",
    "duration_minutes": 60,
    "attendees": ["email@example.com"],
    "location": "location or online"
}}

If no meeting request, respond: {{"is_meeting": false}}"""
            
            try:
                result_text = self.generate_with_retry(prompt)
                
                # Extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    meeting_info = json.loads(json_match.group())
                    if meeting_info.get('is_meeting'):
                        meeting_info['email_id'] = email['id']
                        meeting_info['email_subject'] = email['subject']
                        meeting_requests.append(meeting_info)
            except Exception as e:
                print(f"Error parsing email {email['id']}: {e}")
        
        return self.report_to_coordinator({
            'meeting_requests': meeting_requests,
            'count': len(meeting_requests)
        })
    
    def _send_email(self, to, subject, body):
        """Send an email"""
        print(f"[{self.name}] Sending email to {to}...")
        self.gmail.send_email(to, subject, body)
        return self.report_to_coordinator({'sent': True, 'to': to})
    
    def mark_emails_processed(self, email_ids):
        """Mark emails as read"""
        for email_id in email_ids:
            self.gmail.mark_as_read(email_id)
