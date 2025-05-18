import json
from pathlib import Path
from keyhoard.encryption import encrypt, decrypt, derive_key

HISTORY_FILE = Path("history.json")
MAX_ENTRIES = 50

class ClipboardStorage:
    def __init__(self, key: bytes, salt: bytes):
        self.key = key
        self.salt = salt
        self.history = self.load_history()
        self.current_index = -1
        self.locked = False

    def get_next_entry(self):
        if self.locked or not self.history:
            return None
        self.current_index = (self.current_index + 1) % len(self.history)
        return self.history[self.current_index]

    def get_previous_entry(self):
        if self.locked or not self.history:
            return None
        self.current_index = (self.current_index - 1) % len(self.history)
        return self.history[self.current_index]


    def load_history(self):
        if HISTORY_FILE.exists():
            try:
                raw = json.loads(HISTORY_FILE.read_text())
                return [decrypt( e,self.key) for e in raw]
            except Exception as e:
                print(f"Decryption error: {e}")
                raise ValueError("Failed to decrypt clipboard history")
        return []

    def save_history(self):
        if self.locked:
            print("Can not save while clipboard is locked")
            return None
        encrypted = [encrypt(entry, self.key) for entry in self.history]
        HISTORY_FILE.write_text(json.dumps(encrypted, indent=2))

    def add_entry(self, text):
        if self.locked:
            print("Can not add entry while clipboard is locked.")
            return None
        self.add_to_history(text)

    def add_to_history(self, text):
        if text in self.history:
            self.history.remove(text) # Remove duplicates
        self.history.insert(0, text)
        if len(self.history) > MAX_ENTRIES:
            self.history = self.history[:MAX_ENTRIES]
        self.save_history()


    def lock(self):
        self.locked = True
        print("Clipboard locked")

    def unlock(self, password):
        try:
            key_attempt = derive_key(password, self.salt)
            if key_attempt == self.key:
                self.locked = False
                print("Clipboard unlocked.")
                return True
            return False
        except Exception as e:
            print(f"Unlock failed {e}")
            return False

    def is_locked(self):
        return self.locked