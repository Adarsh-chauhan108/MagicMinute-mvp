import json
import os
import time
from typing import Dict, Optional, List
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memory_manager.log"),
        logging.StreamHandler()
    ]
)

class MemoryManager:
    def __init__(self, storage_file: str = "memory_data.json"):
        self.storage_file = storage_file
        self._ensure_storage()
        self.backup_file = f"{storage_file}.bak"
        self.lock = threading.Lock()

    def _ensure_storage(self):
        """Create storage file with all required structures if it doesn't exist"""
        if not os.path.exists(self.storage_file):
            default_data = {
                "contacts": {},
                "preferences": {},
                "conversation_history": [],
                "context_snapshots": []
            }
            self._save_data(default_data)

    def _load_data(self) -> Dict:
        """Load all memory data with error handling"""
        try:
            with self.lock:
                with open(self.storage_file, "r") as f:
                    return json.load(f)
        except json.JSONDecodeError:
            logging.warning("Corrupted data file, attempting backup restore")
            return self._restore_from_backup()
        except Exception as e:
            logging.error(f"Failed to load data: {e}")
            return self._get_fallback_data()

    def _save_data(self, data: Dict):
        """Save all memory data with atomic write and backup"""
        try:
            # First save to backup
            with self.lock:
                with open(self.backup_file, "w") as f:
                    json.dump(data, f, indent=2)
                
                # Then rename to main file (atomic operation)
                os.replace(self.backup_file, self.storage_file)
        except Exception as e:
            logging.error(f"Failed to save data: {e}")

    def _restore_from_backup(self) -> Dict:
        """Attempt to restore data from backup"""
        try:
            if os.path.exists(self.backup_file):
                with open(self.backup_file, "r") as f:
                    return json.load(f)
            return self._get_fallback_data()
        except Exception:
            return self._get_fallback_data()

    def _get_fallback_data(self) -> Dict:
        """Return empty data structure when all else fails"""
        return {
            "contacts": {},
            "preferences": {},
            "conversation_history": [],
            "context_snapshots": []
        }

    # Enhanced contact methods
    def save_contact(self, name: str, email: str) -> bool:
        """Save a new contact alias with validation"""
        if not name or not email or "@" not in email:
            return False
            
        try:
            data = self._load_data()
            data["contacts"][name.lower()] = email
            self._save_data(data)
            logging.info(f"Saved contact: {name} -> {email}")
            return True
        except Exception as e:
            logging.error(f"Failed to save contact: {e}")
            return False

    def get_contact(self, name: str) -> Optional[str]:
        """Retrieve email by alias with fuzzy matching"""
        data = self._load_data()
        name_lower = name.lower()
        
        # Exact match
        if name_lower in data["contacts"]:
            return data["contacts"][name_lower]
            
        # Fuzzy match
        for contact_name, email in data["contacts"].items():
            if name_lower in contact_name or contact_name in name_lower:
                return email
                
        return None

    # Conversation history methods
    def save_conversation(self, role: str, content: str, metadata: Dict = None):
        """Save a conversation entry"""
        try:
            data = self._load_data()
            entry = {
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "content": content,
                "metadata": metadata or {}
            }
            data["conversation_history"].append(entry)
            
            # Keep only last 100 messages
            data["conversation_history"] = data["conversation_history"][-100:]
            
            self._save_data(data)
            return True
        except Exception as e:
            logging.error(f"Failed to save conversation: {e}")
            return False

    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        data = self._load_data()
        return data["conversation_history"][-limit:]

    # Context snapshot methods
    def save_context_snapshot(self, context: Dict):
        """Save a context snapshot"""
        try:
            data = self._load_data()
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "context": context
            }
            data["context_snapshots"].append(snapshot)
            
            # Keep only last 20 snapshots
            data["context_snapshots"] = data["context_snapshots"][-20:]
            
            self._save_data(data)
            return True
        except Exception as e:
            logging.error(f"Failed to save context snapshot: {e}")
            return False

    def get_latest_context(self) -> Optional[Dict]:
        """Get the most recent context snapshot"""
        data = self._load_data()
        if data["context_snapshots"]:
            return data["context_snapshots"][-1]["context"]
        return None

    # Existing preference methods remain the same but with error handling
    def save_preference(self, key: str, value: str) -> bool:
        try:
            data = self._load_data()
            data["preferences"][key] = value
            self._save_data(data)
            return True
        except Exception as e:
            logging.error(f"Failed to save preference: {e}")
            return False

    def get_preference(self, key: str) -> Optional[str]:
        data = self._load_data()
        return data["preferences"].get(key)