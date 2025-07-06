# memory_manager.py
import json
import os
import threading
from typing import Dict, List, Optional, Any

class MemoryManager:
    """
    Manages persistent storage of user data including contacts, preferences, and settings.
    Thread-safe implementation with JSON file storage.
    """
    
    def __init__(self, storage_file: str = "memory_data.json"):
        self.storage_file = storage_file
        self.lock = threading.Lock()
        self._ensure_storage()

    def _ensure_storage(self):
        """Initialize storage file if it doesn't exist"""
        if not os.path.exists(self.storage_file):
            with self.lock:
                try:
                    with open(self.storage_file, "w") as f:
                        json.dump({
                            "contacts": {},
                            "preferences": {},
                            "auto_reply_rules": [],
                            "email_history": []
                        }, f, indent=2)
                except Exception as e:
                    print(f"Error creating storage file: {e}")

    def _load_data(self) -> Dict[str, Any]:
        """Load data from storage file"""
        try:
            with open(self.storage_file, "r") as f:
                data = json.load(f)
                # Ensure all required keys exist
                if "contacts" not in data:
                    data["contacts"] = {}
                if "preferences" not in data:
                    data["preferences"] = {}
                if "auto_reply_rules" not in data:
                    data["auto_reply_rules"] = []
                if "email_history" not in data:
                    data["email_history"] = []
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading data: {e}")
            return {
                "contacts": {},
                "preferences": {},
                "auto_reply_rules": [],
                "email_history": []
            }

    def _save_data(self, data: Dict[str, Any]) -> bool:
        """Save data to storage file"""
        try:
            with open(self.storage_file, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

    # Contact Management
    def save_contact(self, name: str, email: str) -> bool:
        """Save a contact with name and email"""
        if not name or not email or "@" not in email:
            return False
        
        try:
            with self.lock:
                data = self._load_data()
                data["contacts"][name.lower().strip()] = email.strip()
                return self._save_data(data)
        except Exception as e:
            print(f"Error saving contact: {e}")
            return False

    def get_contact(self, name: str) -> Optional[str]:
        """Get email address for a contact name"""
        if not name:
            return None
        
        try:
            with self.lock:
                data = self._load_data()
                return data["contacts"].get(name.lower().strip())
        except Exception as e:
            print(f"Error getting contact: {e}")
            return None

    def get_all_contacts(self) -> Dict[str, str]:
        """Get all saved contacts"""
        try:
            with self.lock:
                data = self._load_data()
                return data.get("contacts", {})
        except Exception:
            return {}

    def remove_contact(self, name: str) -> bool:
        """Remove a contact by name"""
        if not name:
            return False
        
        try:
            with self.lock:
                data = self._load_data()
                if name.lower().strip() in data["contacts"]:
                    del data["contacts"][name.lower().strip()]
                    return self._save_data(data)
                return False
        except Exception as e:
            print(f"Error removing contact: {e}")
            return False

    # Preference Management
    def save_preference(self, key: str, value: str) -> bool:
        """Save a user preference"""
        if not key or value is None:
            return False
        
        try:
            with self.lock:
                data = self._load_data()
                data["preferences"][key.strip()] = str(value).strip()
                return self._save_data(data)
        except Exception as e:
            print(f"Error saving preference: {e}")
            return False

    def get_preference(self, key: str) -> Optional[str]:
        """Get a user preference value"""
        if not key:
            return None
        
        try:
            with self.lock:
                data = self._load_data()
                return data["preferences"].get(key.strip())
        except Exception as e:
            print(f"Error getting preference: {e}")
            return None

    def get_all_preferences(self) -> Dict[str, str]:
        """Get all user preferences"""
        try:
            with self.lock:
                data = self._load_data()
                return data.get("preferences", {})
        except Exception:
            return {}

    def remove_preference(self, key: str) -> bool:
        """Remove a preference by key"""
        if not key:
            return False
        
        try:
            with self.lock:
                data = self._load_data()
                if key.strip() in data["preferences"]:
                    del data["preferences"][key.strip()]
                    return self._save_data(data)
                return False
        except Exception as e:
            print(f"Error removing preference: {e}")
            return False

    # Auto-reply Rules Management
    def save_auto_reply_rule(self, rule: Dict[str, Any]) -> bool:
        """Save an auto-reply rule"""
        if not rule or not isinstance(rule, dict):
            return False
        
        try:
            with self.lock:
                data = self._load_data()
                # Add unique ID if not present
                if "id" not in rule:
                    rule["id"] = f"rule_{len(data['auto_reply_rules']) + 1}"
                data["auto_reply_rules"].append(rule)
                return self._save_data(data)
        except Exception as e:
            print(f"Error saving auto-reply rule: {e}")
            return False

    def get_auto_reply_rules(self) -> List[Dict[str, Any]]:
        """Get all auto-reply rules"""
        try:
            with self.lock:
                data = self._load_data()
                return data.get("auto_reply_rules", [])
        except Exception:
            return []

    def remove_auto_reply_rule(self, rule_id: str) -> bool:
        """Remove an auto-reply rule by ID"""
        if not rule_id:
            return False
        
        try:
            with self.lock:
                data = self._load_data()
                data["auto_reply_rules"] = [
                    rule for rule in data["auto_reply_rules"] 
                    if rule.get("id") != rule_id
                ]
                return self._save_data(data)
        except Exception as e:
            print(f"Error removing auto-reply rule: {e}")
            return False

    def clear_auto_reply_rules(self) -> bool:
        """Clear all auto-reply rules"""
        try:
            with self.lock:
                data = self._load_data()
                data["auto_reply_rules"] = []
                return self._save_data(data)
        except Exception as e:
            print(f"Error clearing auto-reply rules: {e}")
            return False

    # Email History Management
    def save_email_to_history(self, email_data: Dict[str, Any]) -> bool:
        """Save an email to history"""
        if not email_data or not isinstance(email_data, dict):
            return False
        
        try:
            with self.lock:
                data = self._load_data()
                # Add timestamp if not present
                if "timestamp" not in email_data:
                    from datetime import datetime
                    email_data["timestamp"] = datetime.now().isoformat()
                
                data["email_history"].append(email_data)
                
                # Keep only last 100 emails to prevent file from growing too large
                if len(data["email_history"]) > 100:
                    data["email_history"] = data["email_history"][-100:]
                
                return self._save_data(data)
        except Exception as e:
            print(f"Error saving email to history: {e}")
            return False

    def get_email_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get email history with optional limit"""
        try:
            with self.lock:
                data = self._load_data()
                history = data.get("email_history", [])
                return history[-limit:] if limit > 0 else history
        except Exception:
            return []

    def clear_email_history(self) -> bool:
        """Clear all email history"""
        try:
            with self.lock:
                data = self._load_data()
                data["email_history"] = []
                return self._save_data(data)
        except Exception as e:
            print(f"Error clearing email history: {e}")
            return False

    # Utility Methods
    def get_storage_stats(self) -> Dict[str, int]:
        """Get statistics about stored data"""
        try:
            with self.lock:
                data = self._load_data()
                return {
                    "contacts_count": len(data.get("contacts", {})),
                    "preferences_count": len(data.get("preferences", {})),
                    "auto_reply_rules_count": len(data.get("auto_reply_rules", [])),
                    "email_history_count": len(data.get("email_history", []))
                }
        except Exception:
            return {
                "contacts_count": 0,
                "preferences_count": 0,
                "auto_reply_rules_count": 0,
                "email_history_count": 0
            }

    def export_data(self) -> Dict[str, Any]:
        """Export all data for backup purposes"""
        try:
            with self.lock:
                return self._load_data()
        except Exception:
            return {}

    def import_data(self, imported_data: Dict[str, Any]) -> bool:
        """Import data from backup"""
        if not imported_data or not isinstance(imported_data, dict):
            return False
        
        try:
            with self.lock:
                # Validate structure
                required_keys = ["contacts", "preferences", "auto_reply_rules", "email_history"]
                for key in required_keys:
                    if key not in imported_data:
                        imported_data[key] = {} if key in ["contacts", "preferences"] else []
                
                return self._save_data(imported_data)
        except Exception as e:
            print(f"Error importing data: {e}")
            return False

    def reset_all_data(self) -> bool:
        """Reset all data to default state"""
        try:
            with self.lock:
                default_data = {
                    "contacts": {},
                    "preferences": {},
                    "auto_reply_rules": [],
                    "email_history": []
                }
                return self._save_data(default_data)
        except Exception as e:
            print(f"Error resetting data: {e}")
            return False