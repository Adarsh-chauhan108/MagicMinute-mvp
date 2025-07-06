import re

def interpret_nlp_command(task: str) -> dict:
    """
    Parses natural language task like:
    "Send email to abc@gmail.com saying Hello at 14:30"
    and returns a dictionary with recipient, body, and time.
    """
    recipient_match = re.search(r"to\s+(\S+@\S+)", task, re.IGNORECASE)
    body_match = re.search(r"saying\s+['\"]?(.+?)['\"]?(?:\s+at|\s+in|$)", task, re.IGNORECASE)
    time_match = re.search(r"at\s+(\d{1,2}:\d{2})", task)
    delay_match = re.search(r"in\s+(\d{1,3})\s+(minute|minutes)", task)

    result = {
        "recipient": recipient_match.group(1) if recipient_match else None,
        "body": body_match.group(1).strip() if body_match else None,
        "time": None
    }

    if delay_match:
        from datetime import datetime, timedelta
        delay = int(delay_match.group(1))
        result["time"] = (datetime.now() + timedelta(minutes=delay)).strftime("%H:%M")
    elif time_match:
        result["time"] = time_match.group(1)

    return result if result["recipient"] and result["body"] else None