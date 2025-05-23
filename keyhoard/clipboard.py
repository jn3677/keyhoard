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
        except Exception as e:
            print(f"[Clipboard Error]: {e}")
            return None

    def has_new_text(self):
        text = self.get_clipboard()
        if text and text != self.last_text:
            self.last_text = text
            return text
        return None

    def write_to_clipboard(self, text):
        pyperclip.copy(text)

    @contextlib.contextmanager
    def suppress(self):
        self.suppressed = True
        try:
            yield
        finally:
            self.suppressed = False