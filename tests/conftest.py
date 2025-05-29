import keyboard
import pytest
from keyhoard.encryption import derive_key
from keyhoard.storage import ClipboardStorage
from keyhoard.clipboard import ClipboardMonitor
from unittest.mock import patch, MagicMock

@pytest.fixture
def test_key():
    return derive_key("test_password",b"test_salt_123456")

@pytest.fixture
def empty_storage(tmp_path, test_key):
    return ClipboardStorage(key=test_key)


@pytest.fixture
def populated_storage(empty_storage):
    test_entries = ["test1", "test2", "敏感数据"]
    for entry in test_entries:
        empty_storage.add_entry(entry)
    return empty_storage

@pytest.fixture
def clipboard_monitor():
    cm = ClipboardMonitor()
    cm.write_to_clipboard = MagicMock()

    mock_context_manager = MagicMock()
    mock_context_manager.__enter__.return_value = None
    mock_context_manager.__exit__.return_value = None
    cm.suppress = MagicMock(return_value=mock_context_manager)
    return cm

@pytest.fixture
def test_salt():
    return b"test_salt_12345678"


@pytest.fixture(autouse=True)
def mock_pyperclip():
    with patch("pyperclip.copy") as mock_copy, patch("pyperclip.paste", return_value="mocked text") as mock_paste:
        yield mock_copy, mock_paste

@pytest.fixture
def clipboard_storage():
    storage = MagicMock(spec=ClipboardStorage)
    storage.history = ["a" * 70, "short"]
    storage.get_next_entry.side_effect = ["next1", None]
    storage.get_previous_entry.side_effect = ["prev1", None]
    storage.is_locked.return_value = False
    storage.unlock.return_value = True
    return storage

@pytest.fixture(autouse=True)
def mock_keyboard():
    with patch("keyboard.add_hotkey", return_value="mocked_handler") as mock_add, \
            patch("keyboard.remove_hotkey") as mock_remove, \
            patch("keyboard.unhook_all") as mock_unhook, \
            patch("keyboard.parse_hotkey", side_effect=lambda h:h):
        yield {
            "add": mock_add,
            "remove": mock_remove,
            "unhook": mock_unhook,
            "parse" : keyboard.parse_hotkey
        }
