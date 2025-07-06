import os
import base64
import schedule
import time
import threading
from datetime import datetime
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# === CONFIGURATION ===
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.modify']
TOKEN_PATH = 'app/token.json'  # ✅ Token now inside /app
CREDENTIALS_PATH = 'app/credentials.json'  # ✅ Also inside /app

# === AUTHENTICATE & GET SERVICE ===
def get_gmail_service():
    creds = None

    # Try loading existing token
    if os.path.exists(TOKEN_PATH):
        print(f"🔐 Loading token from {TOKEN_PATH}")
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # Refresh or request new token if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("🔁 Token refreshed successfully.")
            except Exception as e:
                print(f"❌ Token refresh failed: {e}")
                creds = None  # fallback to full re-auth

        if not creds:
            print("🌐 Opening browser for Google auth...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for future use
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
        print(f"✅ Token saved to {TOKEN_PATH}")

    return build('gmail', 'v1', credentials=creds)

# === IMMEDIATE EMAIL ===
def send_email(recipient, subject, body):
    try:
        service = get_gmail_service()

        message = MIMEText(body)
        message['to'] = recipient
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        send_message = {'raw': raw}
        result = service.users().messages().send(userId="me", body=send_message).execute()
        print(f"✅ Email sent to {recipient}")
        return result
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return None

# === SCHEDULE EMAIL ===
scheduled_jobs = []

def schedule_email(recipient, subject, body, time_str):
    def job():
        try:
            send_email(recipient, subject, body)
            print(f"📬 Scheduled email sent to {recipient} at {datetime.now().strftime('%H:%M')}")
        except Exception as e:
            print(f"❌ Failed to send scheduled email: {e}")

    schedule.every().day.at(time_str).do(job)
    scheduled_jobs.append(job)

# === SCHEDULER BACKGROUND THREAD ===
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_scheduler():
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("✅ Background scheduler started.")