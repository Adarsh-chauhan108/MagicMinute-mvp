import os
import openai
import json
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are an advanced email assistant that understands all types of email topics including:
- Current events (wars, politics, etc.)
- Personal messages
- Business communication
- Technical topics

For any valid email request, return structured JSON with complete email content.
For unclear requests, ask follow-up questions.

Response format:
{
  "task_type": "email",
  "recipient": "email@example.com",
  "subject": "Subject",
  "body": "Complete email content with proper formatting",
  "show_draft": true,
  "follow_up": {
    "question": "What specific aspects should I focus on?",
    "options": ["Military updates", "Humanitarian impact", "Political analysis"]
  }
}
"""

def generate_contextual_reply(sender: str, subject: str, email_content: str, rule_message: str = None) -> str:
    """
    Generate a personalized reply based on the email content and context.
    """
    prompt = f"""
Generate a thoughtful, personalized reply to this email. Be helpful, polite, and conversational.

From: {sender}
Subject: {subject}
Content: {email_content[:2000]}  # Truncate very long emails

Guidelines:
1. If the email asks specific questions, answer them naturally
2. If it's a general message, respond appropriately to the tone
3. Keep it professional but friendly
4. Use the following base message only as inspiration: {rule_message or "I'll respond soon"}
5. Never include placeholders like [Your Name] - use first person
6. Keep it concise (2-4 sentences max)
"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful email assistant that writes perfect replies."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating contextual reply: {e}")
        return rule_message or "Thank you for your email. I'll respond soon."

def interpret_auto_reply_command(prompt, current_rules=None):
    SYSTEM_PROMPT = """You are an auto-reply configuration assistant. Analyze the prompt and return structured JSON:
{
  "action": "enable|disable|add_rule|remove_rule|list_rules|toggle_smart",
  "senders": ["email1@x.com", "name2"],  // For specific senders
  "message": "Custom reply text",  // Optional
  "start_time": "HH:MM",  // Optional
  "end_time": "HH:MM",   // Optional
  "use_llm": true/false,  // Whether to use AI for replies
  "default": true/false,  // If this is default rule
  "identifier": "id"      // For removing rules
  "status": "on|off"      // For enable/disable commands
}

Example commands to handle:
- "Turn on auto-reply for all emails"
- "Set up auto-reply from 9am to 5pm with message 'I'm on vacation'"
- "Add auto-reply for emails from john@example.com saying 'I'll be back Monday'"
- "Remove the second auto-reply rule"
- "Show current auto-reply rules"
- "Disable auto-replies after 6pm"
- "Turn on smart replies"
- "Disable AI responses"
"""
    
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": json.dumps({"current_rules": current_rules or []})}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

def interpret_task_with_llm(user_input: str, previous_draft: dict = None) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]
    
    if previous_draft:
        messages.insert(1, {
            "role": "assistant",
            "content": json.dumps({"current_draft": previous_draft})
        })

    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        
        # Ensure minimum viable email content
        if result["task_type"] == "email":
            if not result.get("body"):
                result["body"] = f"Hi,\n\n{user_input}\n\nBest regards,\n[Your Name]"
            if not result.get("subject"):
                result["subject"] = user_input[:50]
                
        return result
    except Exception as e:
        return {
            "task_type": "unknown",
            "error": str(e),
            "follow_up": {
                "question": "I didn't understand. Could you clarify?",
                "options": ["Try rephrasing", "Provide more details"]
            }
        }
