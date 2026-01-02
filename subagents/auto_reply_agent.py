"""
AutoReplyAgent - Fully Autonomous Email Response System

This agent automatically detects and responds to RESUME/CV requests ONLY.
No other keywords will trigger an auto-reply.

Features:
- Automatic keyword detection (ONLY: resume, cv, curriculum vitae)
- AI-generated personalized responses using user profile
- Thread-aware replies (responds in same email thread)
- Configurable keywords, tone, and exclusions
- Automatic email marking as read

Configuration:
- user_profile.json: Your professional information
- auto_reply_config.json: Auto-reply settings and exclusions

Usage:
The agent runs automatically as part of the coordinator workflow.
No manual action required - completely autonomous!

IMPORTANT: Only replies to emails containing "resume", "cv", or "curriculum vitae"
"""
from subagents.rag_agent import RAGAgent
from subagents.base_agent import BaseAgent
from gmail_handler import GmailHandler
import json
import os


class AutoReplyAgent(BaseAgent):
    """Autonomous agent that automatically replies to resume/profile-related emails"""
    
    def __init__(self, gmail_service):
        super().__init__("AutoReplyAgent", "Autonomous Email Auto-Reply Specialist")
        self.gmail = GmailHandler(gmail_service)
        self.user_profile = self._load_user_profile()
        self.config = self._load_config()
        self.rag_agent = RAGAgent()  # NEW
    
    def _load_user_profile(self):
        """Load user profile data"""
        try:
            with open('user_profile.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[{self.name}] Error loading user profile: {e}")
            return {}
    
    def _load_config(self):
        """Load auto-reply configuration"""
        try:
            with open('auto_reply_config.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[{self.name}] Error loading config, using defaults: {e}")
            return {
                'enabled': True,
                'auto_mark_as_read': True,
                'keywords': {},
                'response_settings': {},
                'exclusions': {}
            }
    
    def process(self, task):
        """Process auto-reply tasks"""
        task_type = task.get('type')
        
        if task_type == 'auto_reply':
            return self._auto_reply_to_emails(task.get('emails', []))
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    def _auto_reply_to_emails(self, emails):
        """Automatically detect and reply to resume/profile-related emails"""
        # Check if auto-reply is enabled
        if not self.config.get('enabled', True):
            print(f"[{self.name}] Auto-reply is disabled in config")
            return self.report_to_coordinator({
                'replied': 0,
                'skipped': len(emails),
                'total': len(emails)
            })
        
        print(f"[{self.name}] Analyzing {len(emails)} emails for auto-reply...")
        
        replied_count = 0
        skipped_count = 0
        
        for email in emails:
            # Check exclusions first
            if self._is_excluded(email):
                skipped_count += 1
                continue
            
            # Check if this email needs an auto-reply
            should_reply, reply_type = self._should_auto_reply(email)
            
            if should_reply:
                print(f"[{self.name}] 🎯 Detected RESUME/CV request from {email['sender']}")
                reply_sent = self._generate_and_send_reply(email, reply_type)
                
                if reply_sent:
                    replied_count += 1
                    # Mark as read after replying if configured
                    if self.config.get('auto_mark_as_read', True):
                        self.gmail.mark_as_read(email['id'])
                    print(f"[{self.name}] ✓ Auto-replied to: {email['subject']}")
                else:
                    skipped_count += 1
            else:
                skipped_count += 1
        
        return self.report_to_coordinator({
            'replied': replied_count,
            'skipped': skipped_count,
            'total': len(emails)
        })
    
    def _is_excluded(self, email):
        """Check if email should be excluded from auto-reply"""
        exclusions = self.config.get('exclusions', {})
        
        # Check sender email
        sender = email['sender'].lower()
        excluded_emails = exclusions.get('sender_emails', [])
        if any(excluded in sender for excluded in excluded_emails):
            print(f"[{self.name}] ✗ Excluded: sender email matches exclusion list")
            return True
        
        # Check sender domain
        excluded_domains = exclusions.get('sender_domains', [])
        if any(domain in sender for domain in excluded_domains):
            print(f"[{self.name}] ✗ Excluded: sender domain matches exclusion list")
            return True
        
        # Check subject keywords
        subject = email['subject'].lower()
        body = email['body'].lower()
        excluded_keywords = exclusions.get('subject_keywords', [])
        
        # Check both subject and body for exclusion keywords
        for keyword in excluded_keywords:
            if keyword in subject or keyword in body:
                print(f"[{self.name}] ✗ Excluded: contains keyword '{keyword}'")
                return True
        
        # Additional automated email detection
        automated_indicators = [
            'do not reply',
            'do-not-reply',
            'automated message',
            'automatic notification',
            'this is an automated',
            'unsubscribe',
            'opt out',
            'manage preferences',
            'view in browser',
            'click here to view'
        ]
        
        combined = f"{subject} {body}"
        for indicator in automated_indicators:
            if indicator in combined:
                print(f"[{self.name}] ✗ Excluded: automated email detected ('{indicator}')")
                return True
        
        return False
    
    def _should_auto_reply(self, email):
        """Determine if email requires auto-reply - ONLY for SPECIFIC resume/CV requests"""
        subject = email['subject'].lower()
        body = email['body'].lower()
        combined_text = f"{subject} {body}"
        
        # STRICT: Must contain specific request phrases, not just the word "resume"
        # This avoids newsletters, notifications, and generic mentions
        request_phrases = [
            'send your resume',
            'share your resume',
            'send your cv',
            'share your cv',
            'send me your resume',
            'share me your resume',
            'send me your cv',
            'share me your cv',
            'send resume',
            'share resume',
            'send cv',
            'share cv',
            'your resume',
            'your cv',
            'attach your resume',
            'attach your cv',
            'submit your resume',
            'submit your cv',
            'provide your resume',
            'provide your cv',
            'forward your resume',
            'forward your cv',
            'send us your resume',
            'send us your cv',
            'email your resume',
            'email your cv',
            'can you send your resume',
            'can you send your cv',
            'could you send your resume',
            'could you send your cv',
            'please send your resume',
            'please send your cv',
            'please share your resume',
            'please share your cv',
            'need your resume',
            'need your cv',
            'request your resume',
            'request your cv',
            'looking for your resume',
            'looking for your cv'
        ]
        
        # Check if email contains any specific request phrase
        for phrase in request_phrases:
            if phrase in combined_text:
                print(f"[{self.name}] ✓ Matched request phrase: '{phrase}'")
                return True, 'resume'
        
        # If just contains "resume" or "cv" without a request context, ignore it
        # This filters out newsletters, job postings, etc.
        print(f"[{self.name}] ✗ No specific resume/CV request detected (avoiding newsletters/generic mentions)")
        return False, None
    
    def _generate_and_send_reply(self, email, reply_type):
        try:
            context = self._prepare_context(reply_type, email)
            
            # Get response settings from config
            response_settings = self.config.get('response_settings', {})
            tone = response_settings.get('tone', 'professional and friendly')
            max_words = response_settings.get('max_words', 300)
            signature = response_settings.get('signature', 'Best regards')
            
            # Generate reply using Gemini
            prompt = f"""You are an AI assistant helping to respond to a professional email.

Original Email:
From: {email['sender']}
Subject: {email['subject']}
Body: {email['body'][:500]}

User Profile Information:
{context}

Task: Generate a {tone} email reply that:
1. Thanks them for reaching out
2. Provides the requested information about {reply_type}
3. Includes relevant details from the user profile
4. Offers to provide more information if needed
5. Maintains a {tone} tone

IMPORTANT: 
- Keep the response concise (maximum {max_words} words)
- Format it as a complete email body (no subject line needed)
- Be specific and highlight key strengths
- End with "{signature}"

Generate the email body only:"""
            
            reply_body = self.generate_with_retry(prompt)
            
            # Generate subject line
            subject = f"Re: {email['subject']}"
            
            # Send the reply
            self.gmail.send_email(
                to=email['sender'],
                subject=subject,
                body=reply_body,
                thread_id=email.get('thread_id')
            )
            
            return True
            
        except Exception as e:
            print(f"[{self.name}] Error generating/sending reply: {e}")
            return False
    
    def _prepare_context(self, reply_type, email=None):
        """Prepare context with RAG enhancement"""
        profile = self.user_profile
        
        # Base context from profile
        base_context = f"""
Personal Information:
- Name: {profile.get('personal_info', {}).get('name', 'N/A')}
- Email: {profile.get('personal_info', {}).get('email', 'N/A')}
- LinkedIn: {profile.get('personal_info', {}).get('linkedin', 'N/A')}
- GitHub: {profile.get('personal_info', {}).get('github', 'N/A')}

Professional Summary:
{profile.get('professional_summary', 'N/A')}
"""
        
        # NEW: Query RAG for additional context
        if email:
            query = f"{email['subject']} {email['body'][:200]}"
            rag_results = self.rag_agent.query(query, n_results=3)
            
            if rag_results:
                rag_context = "\n\n".join(rag_results)
                base_context += f"\n\nAdditional Relevant Information:\n{rag_context}"
        
        return base_context