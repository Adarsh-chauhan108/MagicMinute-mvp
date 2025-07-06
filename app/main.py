import os
import base64
import pickle
import threading
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import pytz
import re
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from llm_interpreter import interpret_task_with_llm, interpret_auto_reply_command, generate_contextual_reply
from contacts import resolve_email
from persistent_scheduler import start_scheduler, schedule_email_background

# Initialize scheduler at startup
start_scheduler()

# Gmail Setup
SCOPES = ["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.modify"]

def get_gmail_service():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("gmail", "v1", credentials=creds)

def send_email(recipient, subject, body, attachments=None):
    try:
        service = get_gmail_service()
        message = MIMEMultipart() if attachments else MIMEText(body)
        message['to'] = recipient
        message['subject'] = subject
        
        if attachments:
            message.attach(MIMEText(body))
            for file in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file['bytes'])
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={file["name"]}')
                message.attach(part)
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId="me", body={'raw': raw}).execute()
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def parse_time(time_str):
    """Parse various time formats into HH:MM"""
    try:
        if re.match(r'^\d{1,2}:\d{2}$', time_str):  # 23:59 format
            return datetime.strptime(time_str, "%H:%M").strftime("%H:%M")
        if re.match(r'^\d{1,2}:\d{2}[ap]m$', time_str.lower()):  # 11:59pm format
            return datetime.strptime(time_str, "%I:%M%p").strftime("%H:%M")
        if re.match(r'^\d{1,2}[ap]m$', time_str.lower()):  # 11pm format
            return datetime.strptime(time_str, "%I%p").strftime("%H:%M")
    except ValueError:
        pass
    return None

class AutoReplyAgent:
    def __init__(self):
        self.config = {"rules": [], "active": False}
        self.replied_threads = set()
        self.blocked_keywords = ["noreply", "no-reply", "promotions", "newsletter"]
        self.blocked_domains = ["internshala.com", "hdfcbank.net"]
        self.my_email = "chauhan.ayush2013@gmail.com"
        self.running = False
        self.thread = None
        self.smart_replies_enabled = True  # Default to enabled

    def is_blocked_sender(self, sender):
        if not sender or self.my_email in sender.lower():
            return True
        sender_lower = sender.lower()
        return any(kw in sender_lower for kw in self.blocked_keywords) or \
               any(domain in sender_lower for domain in self.blocked_domains)

    def toggle_active(self, active):
        self.config["active"] = active
        if active and not self.running:
            self.start_auto_reply()
        elif not active and self.running:
            self.stop_auto_reply()
        return f"Auto-reply {'enabled' if active else 'disabled'}"

    def toggle_smart_replies(self, enabled):
        self.smart_replies_enabled = enabled
        return f"Smart AI replies {'enabled' if enabled else 'disabled'}"

    def add_rule(self, rule):
        self.config["rules"].append(rule)
        return "New rule added successfully"

    def remove_rule(self, index):
        if 0 <= index < len(self.config["rules"]):
            self.config["rules"].pop(index)
            return "Rule removed successfully"
        return "Invalid rule index"

    def start_auto_reply(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.check_emails_loop, daemon=True)
            self.thread.start()
            return "Auto-reply service started"
        return "Auto-reply is already running"

    def stop_auto_reply(self):
        self.running = False
        if self.thread:
            self.thread.join()
        return "Auto-reply service stopped"

    def extract_email_content(self, msg_data):
        """Extract the full email content from message data"""
        payload = msg_data.get('payload', {})
        parts = payload.get('parts', [])
        body = ""
        
        # Try to find the main text/plain part
        for part in parts:
            if part['mimeType'] == 'text/plain':
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
        
        # If no plain text part found, try to get from the main body
        if not body and 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body

    def check_emails_loop(self):
        service = get_gmail_service()
        while self.running:
            try:
                if not self.config["active"]:
                    time.sleep(10)
                    continue

                current_time = datetime.now().time()
                active_rules = [
                    rule for rule in self.config["rules"]
                    if self.is_time_active(rule["start_time"], rule["end_time"])
                ]

                if not active_rules:
                    time.sleep(10)
                    continue

                results = service.users().messages().list(
                    userId="me",
                    labelIds=["INBOX"],
                    q="is:unread"
                ).execute()
                messages = results.get("messages", [])

                for msg in messages:
                    msg_data = service.users().messages().get(
                        userId="me",
                        id=msg["id"],
                        format="full"
                    ).execute()
                    headers = msg_data["payload"]["headers"]
                    sender = next((h["value"] for h in headers if h["name"] == "From"), None)
                    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                    thread_id = msg_data.get("threadId")

                    if not sender or thread_id in self.replied_threads or self.is_blocked_sender(sender):
                        continue

                    for rule in active_rules:
                        if rule["senders"] and not any(s.lower() in sender.lower() for s in rule["senders"]):
                            continue

                        # Get the full email content
                        email_content = self.extract_email_content(msg_data)
                        
                        if self.smart_replies_enabled and rule.get("use_llm"):
                            reply_msg = generate_contextual_reply(
                                sender=sender,
                                subject=subject,
                                email_content=email_content,
                                rule_message=rule["message"]
                            )
                        else:
                            reply_msg = rule["message"]

                        if send_email(sender, f"Re: {subject}", reply_msg):
                            self.replied_threads.add(thread_id)
                            service.users().messages().modify(
                                userId="me",
                                id=msg["id"],
                                body={"removeLabelIds": ["UNREAD"]}
                            ).execute()

                time.sleep(10)
            except Exception as e:
                print(f"Auto-reply error: {e}")
                time.sleep(30)

    def is_time_active(self, start_str, end_str):
        now = datetime.now().time()
        start = datetime.strptime(start_str, "%H:%M").time()
        end = datetime.strptime(end_str, "%H:%M").time()
        return start <= now <= end

    def handle_natural_language_command(self, command):
        try:
            parsed = interpret_auto_reply_command(command, self.config["rules"])
            
            response = ""
            if parsed["action"] == "enable":
                response = self.toggle_active(True)
            elif parsed["action"] == "disable":
                response = self.toggle_active(False)
            elif parsed["action"] == "add_rule":
                new_rule = {
                    "senders": parsed.get("senders", []),
                    "message": parsed.get("message", "I'm currently unavailable. I'll respond soon."),
                    "start_time": parsed.get("start_time", "09:00"),
                    "end_time": parsed.get("end_time", "17:00"),
                    "use_llm": parsed.get("use_llm", False),
                    "default": not bool(parsed.get("senders", []))
                }
                response = self.add_rule(new_rule)
            elif parsed["action"] == "remove_rule":
                if parsed.get("identifier") and parsed["identifier"].isdigit():
                    response = self.remove_rule(int(parsed["identifier"]))
                else:
                    response = "Please specify a valid rule number to remove"
            elif parsed["action"] == "list_rules":
                if not self.config["rules"]:
                    response = "No auto-reply rules configured"
                else:
                    response = "Current auto-reply rules:\n"
                    for i, rule in enumerate(self.config["rules"]):
                        response += f"{i+1}. {rule['start_time']}-{rule['end_time']}: "
                        response += f"for {', '.join(rule['senders']) if rule['senders'] else 'all emails'}\n"
                        response += f"   Message: {rule['message'][:50]}...\n"
                        response += f"   Smart AI: {'✅' if rule.get('use_llm') else '❌'}\n"
            elif parsed["action"] == "toggle_smart":
                response = self.toggle_smart_replies(parsed.get("status") == "on")
            
            return response
        except Exception as e:
            return f"Error processing command: {str(e)}"