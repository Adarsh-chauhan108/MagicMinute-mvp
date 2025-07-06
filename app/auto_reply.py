import base64
import re
import time
import threading
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
from datetime import datetime

# Load credentials
creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/gmail.modify"])
service = build("gmail", "v1", credentials=creds)

# Global control flag
auto_reply_running = False
replied_threads = set()
reply_count = 0
last_replied_to = ""

# Smart filters
blocked_keywords = [
    "noreply", "no-reply", "do-not-reply", "mailer-daemon", "updates", "notifications",
    "promotions", "info@", "support@", "admin@", "newsletter", "system", "automated",
    "googlemail", "notify", "donotreply", "alerts", "news", "help@", "github.com",
    "mailers", "unsubscribe", "digest", "bank", "mailer", "bot@", "api@", "security", "not-reply", "team@"
]

blocked_domains = [
    "internshala.com", "hdfcbank.net", "icicibank.com", "nsdl.com", "nse.co.in", "myntra.com",
    "zen-makemytrip.com", "coursera.org", "myprotein.com", "bigbasket.com", "unstop.com", 
    "dare2compete.news", "mailers.zomato.com", "simplilearnmailer.com", "tmes-in.trendmicro.com",
    "otter.ai"
]

my_email = "chauhan.ayush2013@gmail.com"

def is_human_email(email):
    lower_email = email.lower()
    if my_email in lower_email:
        return False
    for keyword in blocked_keywords:
        if keyword in lower_email:
            return False
    for domain in blocked_domains:
        if domain in lower_email:
            return False
    return True

def create_message(to, subject, message_text):
    message = MIMEText(message_text)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw}

def auto_reply():
    global auto_reply_running, reply_count, last_replied_to

    while auto_reply_running:
        try:
            results = service.users().messages().list(userId="me", labelIds=["INBOX"], q="is:unread").execute()
            messages = results.get("messages", [])

            for msg in messages:
                msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
                headers = msg_data["payload"]["headers"]

                sender = next((h["value"] for h in headers if h["name"] == "From"), None)
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                thread_id = msg_data.get("threadId")

                if not sender or not is_human_email(sender) or thread_id in replied_threads:
                    print(f"⛔ Skipped auto-reply to: {sender}")
                    continue

                message = create_message(
                    to=sender,
                    subject=f"Re: {subject}",
                    message_text="Hi there! 👋 This is an automated reply. I’ll get back to you soon. 🔁"
                )
                service.users().messages().send(userId="me", body=message).execute()
                replied_threads.add(thread_id)
                reply_count += 1
                last_replied_to = sender
                print(f"✅ Auto-replied to: {sender}")

                # Mark the message as read
                service.users().messages().modify(
                    userId="me",
                    id=msg["id"],
                    body={"removeLabelIds": ["UNREAD"]}
                ).execute()

            time.sleep(10)

        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

def start_auto_reply():
    global auto_reply_running
    if not auto_reply_running:
        auto_reply_running = True
        threading.Thread(target=auto_reply, daemon=True).start()

def stop_auto_reply():
    global auto_reply_running
    auto_reply_running = False

def get_status():
    return auto_reply_running, reply_count, last_replied_to