import hashlib
import json
from datetime import datetime
from typing import Dict, Any
from memory_manager import MemoryManager

def generate_slot_id(user_email: str) -> str:
    """Generate a unique slot ID based on user email and current state"""
    try:
        if not user_email:
            user_email = "unknown"
        
        timestamp = datetime.now().strftime("%Y%m%d%H")
        hash_input = f"{user_email.lower().strip()}-{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:32]
    except Exception:
        return "00000000000000000000000000000000"

def calculate_version() -> str:
    """Calculate version based on current date"""
    try:
        now = datetime.now()
        return f"1.{now.year % 100}.{now.month}.{now.day}"
    except Exception:
        return "1.0.0"

def generate_avatar_url(user_email: str) -> str:
    """Generate deterministic avatar URL based on email"""
    try:
        if not user_email:
            user_email = "magicminute@example.com"
        
        hash_str = hashlib.md5(user_email.lower().strip().encode()).hexdigest()
        return f"https://www.gravatar.com/avatar/{hash_str}?d=identicon&s=256"
    except Exception:
        return "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=identicon&s=256"

def calculate_success_score(memory: MemoryManager) -> float:
    """Calculate a success score based on interaction history"""
    try:
        email_history = memory.get_email_history()
        if not email_history:
            return 0.8  # Default score for new users
        
        # Simple scoring based on email count and diversity
        unique_recipients = len({e.get("recipient", "") for e in email_history if e.get("recipient")})
        total_emails = len(email_history)
        return min(0.99, 0.5 + (unique_recipients * 0.1) + (total_emails * 0.01))
    except Exception:
        return 0.8

def get_milestones(memory: MemoryManager) -> Dict[str, str]:
    """Generate milestones based on user activity"""
    milestones = {}
    try:
        stats = memory.get_storage_stats()
        
        # Contact milestones
        contacts_count = stats.get("contacts_count", 0)
        if contacts_count >= 10:
            milestones["contacts_10"] = "Reached 10 contacts"
        if contacts_count >= 25:
            milestones["contacts_25"] = "Reached 25 contacts"
        
        # Email milestones
        email_count = stats.get("email_history_count", 0)
        if email_count >= 50:
            milestones["emails_50"] = "Handled 50 emails"
        if email_count >= 100:
            milestones["emails_100"] = "Handled 100 emails"
        
        # Add first contact date if available
        email_history = memory.get_email_history(1)
        if email_history:
            first_email = email_history[0].get("timestamp")
            if first_email:
                milestones["first_email"] = f"First email on {first_email[:10]}"
        
        # Add preference milestone if any preferences exist
        if memory.get_all_preferences():
            milestones["has_preferences"] = "Custom preferences set"
            
    except Exception:
        pass
    
    return milestones or {"welcome": "New MagicMinute user"}

def get_communication_style(memory: MemoryManager) -> str:
    """Determine communication style based on preferences"""
    try:
        prefs = memory.get_all_preferences()
        if prefs.get("formal_tone", "").lower() == "true":
            return "formal"
        if prefs.get("casual_tone", "").lower() == "true":
            return "casual"
        return "balanced"
    except Exception:
        return "balanced"

def export_erc3525_metadata(user_email: str) -> dict:
    """Export ERC-3525 compliant metadata for the assistant"""
    try:
        memory = MemoryManager()
        stats = memory.get_storage_stats()
        preferences = memory.get_all_preferences()
        
        metadata = {
            "$schema": "ERC-3525",
            "slot": generate_slot_id(user_email),
            "name": "MagicMinute Assistant",
            "description": "AI email assistant with evolving capabilities",
            "image": generate_avatar_url(user_email),
            "version": calculate_version(),
            "schema_version": "1.0.0",
            
            "identity": {
                "user_name": preferences.get("user_name", "User"),
                "user_email": user_email,
                "assistant_name": preferences.get("assistant_name", "MagicMinute"),
                "specialization": "Email productivity and communication",
                "created": datetime.now().isoformat()
            },
            
            "memory": {
                "contacts_count": stats.get("contacts_count", 0),
                "preferences_count": stats.get("preferences_count", 0),
                "auto_reply_rules_count": stats.get("auto_reply_rules_count", 0),
                "email_history_count": stats.get("email_history_count", 0),
                "last_interaction": memory.get_email_history(1)[0].get("timestamp", "") if stats.get("email_history_count", 0) > 0 else ""
            },
            
            "evolution": {
                "total_interactions": stats.get("email_history_count", 0) + stats.get("preferences_count", 0),
                "emails_handled": stats.get("email_history_count", 0),
                "milestones": get_milestones(memory),
                "success_score": calculate_success_score(memory),
                "last_updated": datetime.now().isoformat()
            },
            
            "attributes": {
                "communication_style": get_communication_style(memory),
                "expertise_level": min(5, 1 + (stats.get("email_history_count", 0) // 20)),
                "response_speed": "instant",
                "languages": ["en"],
                "timezone": preferences.get("timezone", "UTC"),
                "signature_style": preferences.get("signature_style", "standard")
            }
        }
        
        return metadata
        
    except Exception as e:
        # Fallback metadata in case of any errors
        return {
            "$schema": "ERC-3525",
            "slot": "00000000000000000000000000000000",
            "name": "MagicMinute Assistant",
            "description": "AI email assistant with evolving capabilities",
            "image": "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=identicon&s=256",
            "version": "1.0.0",
            "schema_version": "1.0.0",
            "identity": {
                "user_name": "User",
                "user_email": user_email or "unknown@example.com",
                "assistant_name": "MagicMinute",
                "specialization": "Email productivity and communication",
                "created": datetime.now().isoformat()
            },
            "error": str(e)[:200] if str(e) else "Unknown error"
        }

if __name__ == "__main__":
    metadata = export_erc3525_metadata("user@example.com")
    print(json.dumps(metadata, indent=2))