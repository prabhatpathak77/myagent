from subagents.base_agent import BaseAgent
from datetime import datetime, timedelta


class ReminderAgent(BaseAgent):
    """Subagent responsible for reminders and notifications"""
    
    def __init__(self):
        super().__init__("ReminderAgent", "Reminder & Notification Specialist")
    
    def process(self, task):
        """Process reminder-related tasks"""
        task_type = task.get('type')
        
        if task_type == 'check_reminders':
            return self._check_reminders(task.get('events', []), task.get('hours_before', 1))
        elif task_type == 'generate_reminder':
            return self._generate_reminder(task.get('event'))
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    def _check_reminders(self, events, hours_before):
        """Check which events need reminders"""
        print(f"[{self.name}] Checking for events needing reminders...")
        reminders_needed = []
        
        for event in events:
            start_time_str = event.get('start', {}).get('dateTime')
            if not start_time_str:
                continue
            
            try:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                time_until = start_time - datetime.now(start_time.tzinfo)
                
                # Check if within reminder window
                if timedelta(hours=hours_before - 0.5) <= time_until <= timedelta(hours=hours_before + 0.5):
                    reminder = self._generate_reminder_text(event)
                    reminders_needed.append({
                        'event': event,
                        'reminder': reminder
                    })
            except Exception as e:
                print(f"Error processing event: {e}")
        
        return self.report_to_coordinator({
            'reminders': reminders_needed,
            'count': len(reminders_needed)
        })
    
    def _generate_reminder(self, event):
        """Generate a reminder message for an event"""
        reminder = self._generate_reminder_text(event)
        return self.report_to_coordinator({'reminder': reminder})
    
    def _generate_reminder_text(self, event):
        """Generate reminder text using Gemini"""
        summary = event.get('summary', 'Upcoming Event')
        start_time = event.get('start', {}).get('dateTime', 'Unknown time')
        location = event.get('location', 'Not specified')
        
        prompt = f"""Generate a friendly reminder message for this meeting:

Event: {summary}
Time: {start_time}
Location: {location}

Create a brief, professional reminder that encourages preparation."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"""Reminder: You have an upcoming meeting!

Event: {summary}
Time: {start_time}
Location: {location}

Don't forget to prepare!"""
