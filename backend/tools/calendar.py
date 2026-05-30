import os
import json
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import save_token, load_token

load_dotenv(override=True)

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Authenticate and return Calendar service using database token storage"""
    creds = None
    creds_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')

    # Try loading token from database
    token_data = load_token('calendar')
    if token_data:
        creds = Credentials.from_authorized_user_info(json.loads(token_data), SCOPES)

    # If no valid credentials, refresh or re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_token('calendar', creds.to_json())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            save_token('calendar', creds.to_json())

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