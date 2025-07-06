import os
import time
import json
import base64
import threading
from datetime import datetime
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Load Gmail service
creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/gmail.modify"])
service = build("gmail", "v1", credentials=creds)

# Track replied threads to avoid duplicate replies
replied_threads = set()

# Rule storage file
RULE_FILE = "auto_reply_rules.json"
agent_running = False

def load_rules():
    if not os.path.exists(RULE_FILE):
        return []
    with open(RULE_FILE, "r") as f:
        return json.load(f)

def save_rule(start_time, end_time, message):
    rules = load_rules()
    rules.append({
        "start_time": start_time,
        "end_time": end_time,
        "message": message
    })
    with open(RULE_FILE, "w") as f:
        json.dump(rules, f, indent=2)

def is_within_time_window(start_str, end_str):
    now = datetime.now().time()
    fmt = "%H:%M"
    start = datetime.strptime(start_str, fmt).time()
    end = datetime.strptime(end_str, fmt).time()
    return start <= now <= end

def is_valid_email(sender):
    sender = sender.lower()
    blocked = ["noreply", "no-reply", "promotions", "newsletter", "updates", "mailer"]
    return not any(b in sender for b in blocked)

def create_message(to, subject, body):
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw}

def auto_reply_loop():
    global agent_running
    print("✅ Auto-reply agent started.")
    while agent_running:
        try:
            rules = load_rules()
            for rule in rules:
                if not is_within_time_window(rule["start_time"], rule["end_time"]):
                    continue

                # Get unread emails
                results = service.users().messages().list(userId="me", labelIds=["INBOX"], q="is:unread").execute()
                messages = results.get("messages", [])

                for msg in messages:
                    msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
                    headers = msg_data["payload"]["headers"]
                    sender = next((h["value"] for h in headers if h["name"] == "From"), None)
                    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                    thread_id = msg_data.get("threadId")

                    if not sender or not is_valid_email(sender) or thread_id in replied_threads:
                        continue

                    reply = create_message(to=sender, subject=f"Re: {subject}", body=rule["message"])
                    service.users().messages().send(userId="me", body=reply).execute()
                    replied_threads.add(thread_id)

                    # Mark as read
                    service.users().messages().modify(userId="me", id=msg["id"], body={"removeLabelIds": ["UNREAD"]}).execute()

                    print(f"✅ Auto-replied to {sender} with: {rule['message']}")

        except Exception as e:
            print(f"❌ Auto-reply error: {e}")

        time.sleep(10)

def start_agent():
    global agent_running
    if not agent_running:
        agent_running = True
        threading.Thread(target=auto_reply_loop, daemon=True).start()

def stop_agent():
    global agent_running
    agent_running = False
