import contextlib

import pyperclip


class ClipboardMonitor:

    def __init__(self):
        # Gets the last polled text
        self.last_text = None
        self.suppressed = False

    def get_clipboard(self):
        try:
            return pyperclip.paste()
        except Exception:
            print(f"[Clipboard Error]: {e}")
            return None

    def has_new_text(self):
        text = self.get_clipboard()
        if text and text != self.last_text:
            self.last_text = text
            return text
        return None

    @contextlib.contextmanager
    def suppress(self):
        self.suppressed = True
        try:
            yield
        finally:
            self.suppressed = False