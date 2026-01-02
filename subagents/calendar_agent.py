from subagents.base_agent import BaseAgent
from calendar_handler import CalendarHandler
from datetime import datetime, timedelta


class CalendarAgent(BaseAgent):
    """Subagent responsible for calendar operations"""
    
    def __init__(self, calendar_service):
        super().__init__("CalendarAgent", "Calendar Management Specialist")
        self.calendar = CalendarHandler(calendar_service)
    
    def process(self, task):
        """Process calendar-related tasks"""
        task_type = task.get('type')
        
        if task_type == 'schedule':
            return self._schedule_meeting(task.get('meeting_info'))
        elif task_type == 'check_upcoming':
            return self._check_upcoming_events(task.get('hours', 24))
        elif task_type == 'check_availability':
            return self._check_availability(task.get('start_time'), task.get('end_time'))
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    def _schedule_meeting(self, meeting_info):
        """Schedule a meeting"""
        print(f"[{self.name}] Scheduling meeting: {meeting_info.get('title')}...")
        
        try:
            date_str = meeting_info.get('date')
            time_str = meeting_info.get('time')
            duration = meeting_info.get('duration_minutes', 60)
            
            if not date_str or not time_str:
                return self.report_to_coordinator({
                    'scheduled': False,
                    'error': 'Missing date or time information'
                })
            
            # Parse datetime
            try:
                start_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            except ValueError as e:
                return self.report_to_coordinator({
                    'scheduled': False,
                    'error': f'Invalid date/time format: {e}'
                })
            
            end_time = start_time + timedelta(minutes=duration)
            
            print(f"[{self.name}] Start: {start_time}, End: {end_time}")
            
            # Check availability first
            if not self.calendar.check_availability(start_time, end_time):
                return self.report_to_coordinator({
                    'scheduled': False,
                    'reason': 'Time slot not available - you have a conflicting event',
                    'meeting': meeting_info.get('title')
                })
            
            # Create event
            attendees = meeting_info.get('attendees', [])
            location = meeting_info.get('location', 'TBD')
            
            event = self.calendar.create_event(
                summary=meeting_info.get('title'),
                start_time=start_time,
                end_time=end_time,
                attendees=attendees,
                description=f"Location: {location}"
            )
            
            if event:
                print(f"[{self.name}] ✓ Meeting scheduled successfully!")
                return self.report_to_coordinator({
                    'scheduled': True,
                    'event_id': event.get('id'),
                    'meeting': meeting_info.get('title'),
                    'start_time': start_time.isoformat(),
                    'attendees': attendees
                })
            else:
                return self.report_to_coordinator({
                    'scheduled': False,
                    'error': 'Failed to create calendar event'
                })
                
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return self.report_to_coordinator({
                'scheduled': False,
                'error': str(e)
            })
    
    def _check_upcoming_events(self, hours):
        """Get upcoming events"""
        print(f"[{self.name}] Checking upcoming events for next {hours} hours...")
        events = self.calendar.get_upcoming_events(hours=hours)
        
        return self.report_to_coordinator({
            'events': events,
            'count': len(events)
        })
    
    def _check_availability(self, start_time, end_time):
        """Check if time slot is available"""
        available = self.calendar.check_availability(start_time, end_time)
        return self.report_to_coordinator({
            'available': available,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        })
