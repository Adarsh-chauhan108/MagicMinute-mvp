# auth_test.py
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
from gmail_utils import get_gmail_service
get_gmail_service()
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_PATH = 'app/credentials.json'
TOKEN_PATH = 'token.json'

def authenticate_gmail():
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    print("✅ Auth successful. token.json generated.")
    return build('gmail', 'v1', credentials=creds)

if __name__ == "__main__":
    authenticate_gmail()