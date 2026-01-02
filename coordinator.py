import google.generativeai as genai
from config import GOOGLE_API_KEY, REMINDER_HOURS_BEFORE
from google_auth import GoogleAuthManager
from subagents.email_agent import EmailAgent
from subagents.calendar_agent import CalendarAgent
from subagents.reminder_agent import ReminderAgent
from subagents.auto_reply_agent import AutoReplyAgent


class CoordinatorAgent:
    """Main coordinator agent that manages all subagents"""
    
    def __init__(self):
        print("=" * 60)
        print("Initializing Coordinator Agent...")
        print("=" * 60)
        
        # Configure Gemini
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        # Authenticate with Google services
        auth_manager = GoogleAuthManager()
        gmail_service, calendar_service = auth_manager.authenticate()
        
        # Initialize subagents
        self.email_agent = EmailAgent(gmail_service)
        self.calendar_agent = CalendarAgent(calendar_service)
        self.reminder_agent = ReminderAgent()
        self.auto_reply_agent = AutoReplyAgent(gmail_service)
        
        print(f"✓ {self.email_agent.name} initialized")
        print(f"✓ {self.calendar_agent.name} initialized")
        print(f"✓ {self.reminder_agent.name} initialized")
        print(f"✓ {self.auto_reply_agent.name} initialized")
        print("=" * 60)
        print("Coordinator Agent ready!\n")
    
    def execute_workflow(self):
        """Execute the main workflow by coordinating subagents"""
        print("\n" + "=" * 60)
        print(f"COORDINATOR: Starting workflow cycle")
        print("=" * 60 + "\n")
        
        # Step 1: Delegate email processing to EmailAgent
        print("COORDINATOR: Delegating email processing to EmailAgent...")
        email_summary = self.email_agent.process({
            'type': 'summarize',
            'max_emails': 10
        })
        
        if email_summary['result']['count'] > 0:
            print(f"\n📧 Email Summary ({email_summary['result']['count']} emails):")
            print("-" * 60)
            print(email_summary['result']['summary'])
            print("-" * 60 + "\n")
            
            # Step 1.5: Auto-reply to resume/profile-related emails (AUTONOMOUS)
            print("COORDINATOR: Delegating auto-reply detection to AutoReplyAgent...")
            auto_reply_result = self.auto_reply_agent.process({
                'type': 'auto_reply',
                'emails': email_summary['result']['emails']
            })
            
            if auto_reply_result['result']['replied'] > 0:
                print(f"✓ AutoReplyAgent: Automatically replied to {auto_reply_result['result']['replied']} email(s)")
                print(f"  (Skipped {auto_reply_result['result']['skipped']} non-relevant emails)\n")
            else:
                print("COORDINATOR: No auto-reply emails detected\n")
            
            # Step 2: Extract meeting requests
            print("COORDINATOR: Asking EmailAgent to extract meeting requests...")
            meeting_extraction = self.email_agent.process({
                'type': 'extract_meetings',
                'emails': email_summary['result']['emails']
            })
            
            # Step 3: Delegate scheduling to CalendarAgent
            if meeting_extraction['result']['count'] > 0:
                print(f"COORDINATOR: Found {meeting_extraction['result']['count']} meeting requests")
                print("COORDINATOR: Delegating scheduling to CalendarAgent...\n")
                
                for meeting in meeting_extraction['result']['meeting_requests']:
                    schedule_result = self.calendar_agent.process({
                        'type': 'schedule',
                        'meeting_info': meeting
                    })
                    
                    if schedule_result['result']['scheduled']:
                        print(f"✓ Scheduled: {meeting['title']}")
                    else:
                        print(f"✗ Failed: {meeting['title']} - {schedule_result['result'].get('reason', 'Unknown error')}")
                
                # Mark emails as processed
                email_ids = [m['email_id'] for m in meeting_extraction['result']['meeting_requests']]
                self.email_agent.mark_emails_processed(email_ids)
            else:
                print("COORDINATOR: No meeting requests found in emails\n")
        else:
            print("COORDINATOR: No unread emails to process\n")
        
        # Step 4: Check for upcoming events and reminders
        print("COORDINATOR: Asking CalendarAgent for upcoming events...")
        upcoming_events = self.calendar_agent.process({
            'type': 'check_upcoming',
            'hours': REMINDER_HOURS_BEFORE + 1
        })
        
        if upcoming_events['result']['count'] > 0:
            print(f"COORDINATOR: Found {upcoming_events['result']['count']} upcoming events")
            print("COORDINATOR: Delegating reminder check to ReminderAgent...\n")
            
            # Step 5: Delegate reminder generation to ReminderAgent
            reminder_check = self.reminder_agent.process({
                'type': 'check_reminders',
                'events': upcoming_events['result']['events'],
                'hours_before': REMINDER_HOURS_BEFORE
            })
            
            if reminder_check['result']['count'] > 0:
                print(f"🔔 {reminder_check['result']['count']} Reminder(s):")
                print("-" * 60)
                for reminder_data in reminder_check['result']['reminders']:
                    print(reminder_data['reminder'])
                    print("-" * 60)
            else:
                print("COORDINATOR: No reminders needed at this time\n")
        else:
            print("COORDINATOR: No upcoming events\n")
        
        # Step 6: Generate final report
        self._generate_report(email_summary, upcoming_events)
        
        print("\n" + "=" * 60)
        print("COORDINATOR: Workflow cycle completed")
        print("=" * 60 + "\n")
    
    def _generate_report(self, email_summary, upcoming_events):
        """Generate a summary report using Gemini"""
        print("COORDINATOR: Generating final report...\n")
        
        prompt = f"""As a personal assistant coordinator, create a brief status report:

Email Status:
- Unread emails: {email_summary['result']['count']}

Calendar Status:
- Upcoming events (next 24h): {upcoming_events['result']['count']}

Provide a concise 2-3 sentence summary of the current status."""
        
        try:
            response = self.model.generate_content(prompt)
            print("📊 Status Report:")
            print("-" * 60)
            print(response.text)
            print("-" * 60)
        except Exception as e:
            print(f"Error generating report: {e}")
    
    def process_user_command(self, command):
        """Process natural language commands from user"""
        print(f"\nCOORDINATOR: Processing command: '{command}'")
        
        # First, determine if this is a task or just conversation
        analysis_prompt = f"""You are Carlo, a friendly AI assistant. Analyze this user message:

"{command}"

Determine if this requires:
1. A TASK (email, calendar, scheduling action)
2. Just CONVERSATION (greeting, question, chat)

Respond with ONLY valid JSON:
{{
    "type": "task|conversation",
    "agent": "EmailAgent|CalendarAgent|ReminderAgent|none",
    "action": "summarize|send|schedule|check_upcoming|none",
    "conversational_response": "A friendly response to the user",
    "parameters": {{}}
}}

For tasks, extract parameters:
- For scheduling: title, date (YYYY-MM-DD), time (HH:MM 24-hour), duration_minutes, attendees, location
- For emails: to, subject, body
- For calendar checks: hours

Be conversational and friendly in your response!"""
        
        try:
            response = self.model.generate_content(analysis_prompt)
            result_text = response.text.strip()
            
            # Extract JSON
            import re
            import json
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if not json_match:
                return {
                    'message': "I'm here to help! You can ask me to manage emails, schedule meetings, or just chat.",
                    'error': False
                }
            
            intent = json.loads(json_match.group())
            message_type = intent.get('type')
            conversational_response = intent.get('conversational_response', '')
            
            # If it's just conversation, respond directly
            if message_type == 'conversation':
                return {
                    'message': conversational_response,
                    'tasks': []
                }
            
            # If it's a task, execute it
            agent_name = intent.get('agent')
            action = intent.get('action')
            params = intent.get('parameters', {})
            
            if agent_name == 'none' or action == 'none':
                return {
                    'message': conversational_response,
                    'tasks': []
                }
            
            print(f"COORDINATOR: Delegating to {agent_name} for action: {action}")
            
            # Delegate to appropriate agent
            tasks = []
            
            if agent_name == 'EmailAgent':
                result = self._handle_email_task(action, params)
                tasks.append(result)
            elif agent_name == 'CalendarAgent':
                result = self._handle_calendar_task(action, params)
                tasks.append(result)
            elif agent_name == 'ReminderAgent':
                result = self._handle_reminder_task(action, params)
                tasks.append(result)
            
            # Combine conversational response with task results
            task_summary = self._generate_task_summary(tasks)
            final_message = f"{conversational_response}\n\n{task_summary}" if conversational_response else task_summary
            
            return {
                'message': final_message,
                'delegated_to': agent_name,
                'tasks': tasks
            }
            
        except Exception as e:
            print(f"Error processing command: {e}")
            return {
                'message': "I'm having trouble processing that right now. Could you try rephrasing your request?",
                'error': True
            }
    
    def _handle_email_task(self, action, params):
        """Handle email-related tasks"""
        if action == 'summarize':
            result = self.email_agent.process({'type': 'summarize', 'max_emails': 10})
            count = result['result']['count']
            if count == 0:
                return {
                    'agent': 'EmailAgent',
                    'success': True,
                    'message': "Good news! Your inbox is clear - no unread emails."
                }
            summary = result['result']['summary']
            return {
                'agent': 'EmailAgent',
                'success': True,
                'message': f"You have {count} unread email{'s' if count != 1 else ''}:\n\n{summary}"
            }
        elif action == 'send':
            result = self.email_agent.process({
                'type': 'send',
                'to': params.get('to'),
                'subject': params.get('subject', 'No Subject'),
                'body': params.get('body', '')
            })
            success = result['result'].get('sent', False)
            if success:
                return {
                    'agent': 'EmailAgent',
                    'success': True,
                    'message': f"Done! I've sent the email to {params.get('to')}."
                }
            else:
                return {
                    'agent': 'EmailAgent',
                    'success': False,
                    'message': f"I couldn't send the email. Please check the recipient address."
                }
        return {'agent': 'EmailAgent', 'success': False, 'message': 'I need more information to help with that.'}
    
    def _handle_calendar_task(self, action, params):
        """Handle calendar-related tasks"""
        if action == 'schedule':
            # Validate required parameters
            if not params.get('title'):
                return {
                    'agent': 'CalendarAgent',
                    'success': False,
                    'message': "I'd love to schedule that for you! What should I call this meeting?"
                }
            
            if not params.get('date') or not params.get('time'):
                return {
                    'agent': 'CalendarAgent',
                    'success': False,
                    'message': "When would you like to schedule this meeting? Please provide a date and time."
                }
            
            print(f"[CalendarAgent] Scheduling: {params.get('title')} on {params.get('date')} at {params.get('time')}")
            
            result = self.calendar_agent.process({
                'type': 'schedule',
                'meeting_info': params
            })
            
            success = result['result'].get('scheduled', False)
            error_msg = result['result'].get('error', result['result'].get('reason', ''))
            
            if success:
                attendees_str = f" with {', '.join(params.get('attendees', []))}" if params.get('attendees') else ""
                return {
                    'agent': 'CalendarAgent',
                    'success': True,
                    'message': f"Perfect! I've scheduled '{params.get('title')}' for {params.get('date')} at {params.get('time')}{attendees_str}. You're all set!"
                }
            else:
                return {
                    'agent': 'CalendarAgent',
                    'success': False,
                    'message': f"I had trouble scheduling that meeting: {error_msg}"
                }
        
        elif action == 'check_upcoming':
            result = self.calendar_agent.process({
                'type': 'check_upcoming',
                'hours': params.get('hours', 24)
            })
            count = result['result']['count']
            hours = params.get('hours', 24)
            if count == 0:
                return {
                    'agent': 'CalendarAgent',
                    'success': True,
                    'message': f"Your calendar is clear for the next {hours} hours. Enjoy your free time!"
                }
            return {
                'agent': 'CalendarAgent',
                'success': True,
                'message': f"You have {count} event{'s' if count != 1 else ''} coming up in the next {hours} hours."
            }
        
        return {'agent': 'CalendarAgent', 'success': False, 'message': 'I need more details to help with that.'}
    
    def _handle_reminder_task(self, action, params):
        """Handle reminder-related tasks"""
        upcoming = self.calendar_agent.process({'type': 'check_upcoming', 'hours': 24})
        result = self.reminder_agent.process({
            'type': 'check_reminders',
            'events': upcoming['result']['events'],
            'hours_before': 1
        })
        count = result['result']['count']
        return {
            'agent': 'ReminderAgent',
            'success': True,
            'message': f"{count} reminder(s) pending"
        }
    
    def _generate_task_summary(self, tasks):
        """Generate a summary of completed tasks"""
        if not tasks:
            return ""
        
        successful = sum(1 for t in tasks if t.get('success'))
        total = len(tasks)
        
        if successful == total:
            # Return the detailed message from the task
            return tasks[0].get('message', 'Task completed!')
        else:
            return f"I completed {successful} out of {total} tasks."
