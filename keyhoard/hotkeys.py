from typing import Callable

import keyboard
import pyperclip

from clipboard import ClipboardMonitor
from storage import ClipboardStorage


class HotkeyManager:

    def __init__(self, storage: ClipboardStorage):
        self.storage = storage
        self.current_hotkey = 'right'
        self.hotkey_handlers = {}
        self.register_defaults()

    def register_defaults(self):
        self.register_hotkey(
            hotkey=self.current_hotkey,
            callback=lambda : self.cycle_clipboard()
        )
        print(f'Clipboard cycle hotkey registered: {self.current_hotkey}')

    def cycle_clipboard(self) -> bool:
        if next_item:= self.storage.get_next_entry():
            with self.suppress_monitoring():
                pyperclip.copy(next_item)
            return True
        return False


    def suppress_monitoring(self):
        return ClipboardMonitor.suppress()

    def register_hotkey(self, hotkey:str, callback: Callable):
        keyboard.add_hotkey(hotkey, callback)
        self.hotkey_handlers[hotkey] = callback


    def update_hotkey(self, new_hotkey:str):
        keyboard.remove_hotkey(self.current_hotkey)
        self.register_hotkey(new_hotkey, self.cycle_clipboard())
        self.current_hotkey = new_hotkey

    def cleanup(self):
        keyboard.unhook_all()