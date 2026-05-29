import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def send_whatsapp_message(message: str) -> str:
    """Send a WhatsApp message via Twilio"""
    try:
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )

        msg = client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
            to=os.getenv("TWILIO_TO_WHATSAPP"),
            body=message
        )

        return f"WhatsApp message sent! SID: {msg.sid}"

    except Exception as e:
        return f"WhatsApp error: {str(e)}"