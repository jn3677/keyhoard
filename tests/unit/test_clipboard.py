import pytest
from unittest.mock import patch, MagicMock
from keyhoard.clipboard import ClipboardMonitor

@pytest.fixture
def monitor():
    return ClipboardMonitor()

def test_get_clipboard_success(monitor, mock_pyperclip):
    mock_copy, mock_paste = mock_pyperclip
    mock_paste.return_value = "test text"
    assert monitor.get_clipboard() == "test text"


def test_get_clipboard_failure(monitor, capsys, mock_pyperclip):
    mock_copy, mock_paste = mock_pyperclip
    mock_paste.side_effect = Exception("Clipboard error")
    result = monitor.get_clipboard()
    assert result == None
    captured = capsys.readouterr()
    assert "[Clipboard Error]" in captured.out


def test_has_new_text_returns_text(monitor, mock_pyperclip):
    mock_copy, mock_paste = mock_pyperclip
    mock_paste.return_value = "new_text"
    assert monitor.has_new_text() == "new_text"
    assert monitor.last_text == "new_text"


def test_has_next_text_retuns_none_if_same(monitor,mock_pyperclip):
    monitor.last_text = "unchanged"
    mock_copy, mock_paste = mock_pyperclip
    mock_paste.return_value = "unchanged"
    assert monitor.has_new_text() == None


def test_has_next_returns_non_if_empty(monitor, mock_pyperclip):
    mock_copy, mock_paste = mock_pyperclip
    mock_paste.return_value=""
    assert monitor.has_new_text() == None


def test_write_to_clipboard(monitor, mock_pyperclip):
    mock_copy, mock_paste = mock_pyperclip
    monitor.write_to_clipboard("copied text")
    mock_copy.assert_called_once_with("copied text")


def test_suppress_context_manager(monitor):
    assert not monitor.suppressed
    with monitor.suppress():
        assert monitor.suppressed
    assert not monitor.suppressed