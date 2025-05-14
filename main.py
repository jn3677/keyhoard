import time
import getpass

from keyhoard.clipboard import ClipboardMonitor
from keyhoard.hotkeys import HotkeyManager
from keyhoard.storage import ClipboardStorage
from keyhoard.config import load_config
from keyhoard.encryption import derive_key
import base64

def main():
    print("Loading configuration...")
    password = input("Enter master password: ")
    print("Password accepted...")
    config = load_config()

    salt = base64.b64decode(config["salt"])
    key = derive_key(password, salt)

    clipboard = ClipboardMonitor()
    storage = ClipboardStorage(key, salt)
    print("Clipboard monitoring started...")
    hotkey_mgr = HotkeyManager(storage,clipboard)
    print(f"Clipboard monitoring started. Press {8} to exit.")
    try:
        while True:
            if not storage.is_locked():
                if new_text := clipboard.has_new_text():
                    print(f"New clipboard text detected: {new_text[:30]!r}...")
                    storage.add_entry(new_text)
                time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        hotkey_mgr.cleanup()
        storage.lock()
        print("Exiting clipboard monitor...")

if __name__ == "__main__":
    main()