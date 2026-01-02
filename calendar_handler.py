from datetime import datetime, timedelta
import pytz


class CalendarHandler:
    def __init__(self, service):
        self.service = service
    
    def create_event(self, summary, start_time, end_time, attendees=None, description=''):
        """Create a calendar event"""
        try:
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'
            ).execute()
            
            print(f"Event created: {created_event.get('htmlLink')}")
            return created_event
        except Exception as e:
            print(f"Error creating event: {e}")
            return None
    
    def get_upcoming_events(self, hours=24):
        """Get upcoming events within specified hours"""
        try:
            now = datetime.utcnow()
            time_max = now + timedelta(hours=hours)
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    def check_availability(self, start_time, end_time):
        """Check if time slot is available"""
        try:
            events = self.service.events().list(
                calendarId='primary',
                timeMin=start_time.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                singleEvents=True
            ).execute()
            
            return len(events.get('items', [])) == 0
        except Exception as e:
            print(f"Error checking availability: {e}")
            return False
