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
    return ClipboardMonitor()

@pytest.fixture
def test_salt():
    return b"test_salt_12345678"


@pytest.fixture(autouse=True)
def mock_pyperclip():
    with patch("pyperclip.copy") as mock_copy, patch("pyperclip.paste", return_value="mocked text") as mock_paste:
        yield mock_copy, mock_paste