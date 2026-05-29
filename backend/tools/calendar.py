import os
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Authenticate and return Calendar service"""
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), '..', 'token_calendar.pickle')
    creds_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


def get_events(max_results: int = 5) -> str:
    """Get upcoming calendar events"""
    try:
        service = get_calendar_service()
        now = datetime.utcnow().isoformat() + 'Z'

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        if not events:
            return "No upcoming events found."

        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            title = event.get('summary', 'No Title')
            description = event.get('description', '')
            event_list.append(f"📅 {title}\n   When: {start}\n   Notes: {description}")

        return "\n\n".join(event_list)

    except Exception as e:
        return f"Calendar error: {str(e)}"


def create_event(title: str, start_time: str, end_time: str, description: str = "") -> str:
    """Create a new calendar event"""
    try:
        service = get_calendar_service()
        event = {
            'summary': title,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'},
        }

        created = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {created.get('summary')} on {start_time}"

    except Exception as e:
        return f"Calendar create error: {str(e)}"