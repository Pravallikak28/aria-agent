import os
import base64
import json
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import save_token, load_token

load_dotenv(override=True)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

def get_gmail_service():
    """Authenticate and return Gmail service using database token storage"""
    creds = None
    creds_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')

    # Try loading token from database
    token_data = load_token('gmail')
    if token_data:
        creds = Credentials.from_authorized_user_info(json.loads(token_data), SCOPES)

    # If no valid credentials, refresh or re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed token back to database
            save_token('gmail', creds.to_json())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            # Save new token to database
            save_token('gmail', creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def get_unread_emails(max_results: int = 5) -> str:
    """Fetch unread emails from Gmail"""
    try:
        service = get_gmail_service()
        results = service.users().messages().list(
            userId='me',
            labelIds=['UNREAD'],
            maxResults=max_results
        ).execute()

        messages = results.get('messages', [])
        if not messages:
            return "No unread emails found."

        email_summaries = []
        for msg in messages:
            msg_data = service.users().messages().get(
                userId='me', id=msg['id'], format='full'
            ).execute()

            headers = msg_data['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            snippet = msg_data.get('snippet', '')

            email_summaries.append(f"From: {sender}\nSubject: {subject}\nPreview: {snippet}\n")

        return "\n---\n".join(email_summaries)

    except Exception as e:
        return f"Gmail error: {str(e)}"


def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail"""
    try:
        service = get_gmail_service()
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(
            userId='me', body={'raw': raw}
        ).execute()

        return f"Email sent successfully to {to}"
    except Exception as e:
        return f"Email send error: {str(e)}"