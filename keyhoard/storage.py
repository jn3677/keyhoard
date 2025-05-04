import json
from pathlib import Path
from encryption import encrypt, decrypt

HISTORY_FILE = Path("history.json")
MAX_ENTRIES = 50

class ClipboardStorage:
    def __init__(self, key: bytes):
        self.key = key
        self.history = self.load_history()
        self.current_index = -1

    def get_next_entry(self):
        if not self.history:
            return None
        self.current_index = (self.current_index + 1) % len(self.history)
        return self.history[self.current_index]


    def load_history(self):
        if HISTORY_FILE.exists():
            try:
                raw = json.loads(HISTORY_FILE.read_text())
                for e in raw:
                    d = decrypt(e, self.key)
                    print(f"Decrypted entry: {d[:30]!r}...")
                return [decrypt( e,self.key) for e in raw]
            except Exception as e:
                print(f"Decryption error: {e}")
                return []
        return []

    def save_history(self):
        encrypted = [encrypt(entry, self.key) for entry in self.history]
        HISTORY_FILE.write_text(json.dumps(encrypted, indent=2))

    def add_entry(self, text):
        if text in self.history:
            self.history.remove(text) # Remove duplicates
        self.history.insert(0, text)
        if len(self.history) > MAX_ENTRIES:
            self.history = self.history[:MAX_ENTRIES]
        self.save_history()