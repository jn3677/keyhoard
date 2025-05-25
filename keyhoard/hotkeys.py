import getpass
import sys
from typing import Callable

import keyboard

from keyhoard.clipboard import ClipboardMonitor
from keyhoard.storage import ClipboardStorage


class HotkeyManager:

    def __init__(self, storage: ClipboardStorage , clipboard: ClipboardMonitor):
        self.storage = storage
        self.clipboard = clipboard
        self.current_preview: str| None = None
        self.forward_hotkey = 'right'
        self.backward_hotkey = 'left'
        self.lock_hotkey = 'ctrl+shift+l'
        self.unlock_hotkey = 'ctrl+shift+u'
        self.show_history_hotkey =  'ctrl+shift+h'
        self.clear_history_hotkey = 'ctrl+shift+c'
        self.quit_hotkey = 'ctrl+shift+q'
        self.select_hotkey = 'enter'
        self.hotkey_handlers = {}
        self.register_defaults()

    def register_defaults(self):
        self.register_hotkey(self.forward_hotkey, self.cycle_forward)
        self.register_hotkey(self.backward_hotkey, self.cycle_backward)
        self.register_hotkey(self.lock_hotkey, self.lock_clipboard)
        self.register_hotkey(self.unlock_hotkey, self.unlock_clipboard)
        self.register_hotkey(self.show_history_hotkey, self.show_history)
        self.register_hotkey(self.clear_history_hotkey, self.clear_history)
        self.register_hotkey(self.quit_hotkey, self.quit_program)
        self.register_hotkey(self.select_hotkey, self.confirm_selection)
        print(f'Hotkeys registered')

    def confirm_selection(self):
        if self.current_preview:
            self.clipboard.write_to_clipboard(self.current_preview)
            print(f"Copied {self.current_preview}")

    def cycle_forward(self)->bool:
        try:
            if next_item:= self.storage.get_next_entry():
                with self.suppress_monitoring():
                    print(f"Cycle forward next {next_item}")
                    self.current_preview = next_item
                return True
        except Exception as e:
            print(f"Cycle error: {str(e)}")
        return False

    def cycle_backward(self) -> bool:
        if next_item:= self.storage.get_previous_entry():
            with self.suppress_monitoring():
                print(f"Cycle backward next {next_item}")
                self.current_preview = next_item
            return True
        return False

    def lock_clipboard(self):
        self.storage.lock()
        print("Locked")

    def unlock_clipboard(self):
        password = input("Enter to unlock password:")
        unlocked = self.storage.unlock(password)
        if not unlocked:
            print("Unlock failed.")
        else:
            print("Unlocked")

    def show_history(self):
        if self.storage.is_locked():
            print("Clipboard locked, unable to view history")
            return
        if not self.storage.history:
            print("   (empty)")
        print('/n')
        for i, item in enumerate(self.storage.history, 1):
            preview = item.replace('\n', ' ')[:60]
            if len(item) > 60:
                preview += "..."
            print(f"  {i}: {preview}")

    def clear_history(self):
        if self.storage.is_locked():
            print("Clipboard locked, unable to clear history")
            return
        self.storage.history.clear()
        self.storage.current_index = -1
        self.storage.save_history()
        print("Clipboard history cleared.")


    def quit_program(self):
        print("Exiting")
        self.cleanup()
        sys.exit(0)

    def is_valid_hotkey(self, hotkey:str) ->bool:
        try:
            keyboard.parse_hotkey(hotkey)
            return True
        except ValueError:
            return False


    def suppress_monitoring(self):
        return self.clipboard.suppress()

    def register_hotkey(self, hotkey:str, callback: Callable):
        if hotkey in self.hotkey_handlers:
            try:
                keyboard.remove_hotkey(hotkey)
            except KeyError:
                pass
        handler = keyboard.add_hotkey(hotkey, callback)
        self.hotkey_handlers[hotkey] = handler


    def update_hotkey(self, new_hotkey:str, direction: str = 'forward'):
        if direction == 'forward':
            old_hotkey = self.forward_hotkey
            callback = self.cycle_forward
            self.forward_hotkey = new_hotkey
        elif direction == 'backward':
            old_hotkey = self.backward_hotkey
            callback = self.cycle_backward
            self.backward_hotkey = new_hotkey
        else:
            raise ValueError(f"Unknown direction: {direction}")
        keyboard.remove_hotkey(old_hotkey)
        self.register_hotkey(new_hotkey, callback)
        print(f'Updated {direction} hotkey from {old_hotkey} to {new_hotkey}')



    def cleanup(self):
        keyboard.unhook_all()