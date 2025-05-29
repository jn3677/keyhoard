import pytest
from keyhoard.hotkeys import HotkeyManager

def test_confirm_selection_sets_clipboard(clipboard_storage, clipboard_monitor):
    manager = HotkeyManager(clipboard_storage,clipboard_monitor)
    manager.current_preview = "copied text"
    manager.confirm_selection()
    clipboard_monitor.write_to_clipboard.assert_called_once_with("copied text")


def test_cycle_forward_success(clipboard_storage, clipboard_monitor):
    manager = HotkeyManager(clipboard_storage, clipboard_monitor)
    result = manager.cycle_forward()
    assert result is True
    assert manager.current_preview == "next1"
    clipboard_monitor.suppress.assert_called()

def test_cycle_forward_failure(clipboard_storage, clipboard_monitor):
    clipboard_storage.get_next_entry.side_effect = Exception("Failure")
    manager = HotkeyManager(clipboard_storage, clipboard_monitor)
    result = manager.cycle_forward()
    assert result is False

def test_cycle_backward_success(clipboard_storage, clipboard_monitor):
    manager = HotkeyManager(clipboard_storage, clipboard_monitor)
    result = manager.cycle_backward()
    assert result is True
    assert manager.current_preview == "prev1"
    clipboard_monitor.suppress.assert_called()

def test_lock_clipboard(clipboard_storage, clipboard_monitor):
    manager = HotkeyManager(clipboard_storage, clipboard_monitor)
    manager.lock_clipboard()
    clipboard_storage.lock.assert_called_once()


def test_unlock_clipboard(monkeypatch, clipboard_storage,clipboard_monitor):
    monkeypatch.setattr("builtins.input", lambda _: "password")
    manager = HotkeyManager(clipboard_storage, clipboard_monitor)
    manager.unlock_clipboard()
    clipboard_storage.unlock.assert_called_once_with("password")

def test_show_history_prints(capsys, clipboard_storage, clipboard_monitor):
    manager = HotkeyManager(clipboard_storage, clipboard_monitor)
    manager.show_history()
    out = capsys.readouterr().out
    assert "1:" in out and "2:" in out


def test_clear_history_when_unlocked(clipboard_storage, clipboard_monitor):
    manager = HotkeyManager(clipboard_storage, clipboard_monitor)
    manager.clear_history()
    clipboard_storage.save_history.assert_called_once()
    assert clipboard_storage.history == []


def test_update_hotkey(mock_keyboard, clipboard_storage, clipboard_monitor):
    manager = HotkeyManager(clipboard_storage, clipboard_monitor)
    manager.update_hotkey("ctrl+alt+f", direction="forward")
    mock_keyboard["remove"].assert_called()
    mock_keyboard["add"].assert_called()