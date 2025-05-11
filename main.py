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
    storage = ClipboardStorage(key)
    print("Clipboard monitoring started...")
    hotkey_mgr = HotkeyManager(storage,clipboard)

    try:
        while True:
            new_text = clipboard.has_new_text()
            if new_text:
                print(f"New clipboard text detected: {new_text[:30]!r}...")
                storage.add_entry(new_text)
            time.sleep(0.5)
    except KeyboardInterrupt:
        hotkey_mgr.cleanup()
        print("Exiting clipboard monitor...")

if __name__ == "__main__":
    main()