import re

def parse_task_smart(task: str):
    task = task.lower()

    # Auto-reply setup
    auto_reply_match = re.search(
        r"from (\d{1,2}:\d{2}(?:am|pm)?) to (\d{1,2}:\d{2}(?:am|pm)?) .*auto ?reply ['\"](.+?)['\"]", task
    )
    if auto_reply_match:
        start_time = auto_reply_match.group(1)
        end_time = auto_reply_match.group(2)
        message = auto_reply_match.group(3)
        return {
            "task_type": "auto_reply_setup",
            "start_time": start_time,
            "end_time": end_time,
            "message": message
        }

    # Email + Schedule
    email_match = re.search(r"to (\S+@\S+)", task)
    body_match = re.search(r"saying ['\"](.+?)['\"]", task)
    time_match = re.search(r"at (\d{1,2}:\d{2})", task)

    if email_match and body_match:
        return {
            "task_type": "email",
            "recipient": email_match.group(1),
            "body": body_match.group(1),
            "schedule": time_match.group(1) if time_match else None
        }

    return {
        "task_type": "unknown"
    }