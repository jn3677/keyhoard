import json
import os

import pytest

from keyhoard.storage import ClipboardStorage, HISTORY_FILE, MAX_ENTRIES
from keyhoard.encryption import derive_key, encrypt,decrypt

def test_add_and_cycle_entries(tmp_path, test_key,test_salt):
    history_file = tmp_path  / "history.json"
    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = history_file

    storage = ClipboardStorage(test_key, test_salt)

    storage.add_entry("entry1")
    storage.add_entry("entry2")
    storage.add_entry("entry3")

    assert storage.get_next_entry() == "entry3"
    assert storage.get_next_entry() == "entry2"
    assert storage.get_next_entry() == "entry1"
    assert storage.get_next_entry() == "entry3"

    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = HISTORY_FILE

def test_get_previous_entry_cycle(tmp_path, test_key, test_salt):
    history_file = tmp_path  / "history.json"
    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = history_file
    storage = ClipboardStorage(test_key, salt=test_salt)

    storage.add_entry("entry1")
    storage.add_entry("entry2")
    storage.add_entry("entry3")

    assert storage.get_next_entry() == "entry3"
    assert storage.get_previous_entry() == "entry1"
    assert storage.get_previous_entry() == "entry2"

    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = HISTORY_FILE


def test_prevents_duplicates(tmp_path, test_key, test_salt):
    history_file = tmp_path / "history.json"
    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = history_file

    storage = ClipboardStorage(test_key, test_salt)

    storage.add_entry("entry")
    storage.add_entry("entry")

    assert storage.history.count("entry") == 1
    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = HISTORY_FILE


def test_max_entries_limit(tmp_path, test_key, test_salt):
    history_file = tmp_path / "history.json"
    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = history_file

    storage = ClipboardStorage(test_key, test_salt)
    for i in range(MAX_ENTRIES + 10):
        storage.add_entry(f"entry{i}")

    assert len(storage.history) == MAX_ENTRIES
    assert storage.history[0] == f"entry{MAX_ENTRIES + 9}"

    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = HISTORY_FILE

def test_history_persistence(tmp_path, test_key, test_salt):
    history_file = tmp_path / "history.json"
    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = history_file

    storage = ClipboardStorage(test_key, salt=test_salt)
    storage.add_entry("persist")

    new_storage = ClipboardStorage(test_key, salt=test_salt)
    assert "persist" in new_storage.history

    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = HISTORY_FILE



def test_get_previous_entry_empty(tmp_path, test_key, test_salt):
    history_file = tmp_path / "history.json"
    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = history_file

    storage = ClipboardStorage(test_key, salt=test_salt)
    assert  storage.get_previous_entry() is None
    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = HISTORY_FILE

def test_load_history_decryption_error(tmp_path, test_key, test_salt):
    history_file = tmp_path / "history.json"
    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = history_file

    history_file.write_text(json.dumps(["!!!Invalid base64"]))


    with pytest.raises(ValueError,  match="Failed to decrypt clipboard history"):
        storage = ClipboardStorage(test_key, salt=test_salt)

    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = HISTORY_FILE


def test_locked_clipboard_blocks_add_get__save(tmp_path, test_key, capsys, test_salt):
    history_file = tmp_path / "history.json"
    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = history_file

    storage = ClipboardStorage(test_key, salt=test_salt)
    storage.add_entry("test")
    storage.lock()

    assert storage.is_locked() == True
    assert storage.get_next_entry() == None
    assert storage.get_previous_entry() == None

    storage.add_entry("blocked")
    out = capsys.readouterr().out
    assert "Can not add entry while clipboard is locked." in out

    storage.save_history()
    out = capsys.readouterr().out
    assert "Can not save" in out

    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = HISTORY_FILE


def test_unlock_success(tmp_path):
    password = "password"
    salt = b"1234567890abcdef"
    key = derive_key(password, salt)
    history_file = tmp_path / "history.json"
    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = history_file

    storage = ClipboardStorage(key, salt)
    storage.add_entry("secret-entry")
    storage.lock()

    success = storage.unlock(password)
    assert success is True
    assert storage.is_locked() is False
    assert "secret-entry" in storage.history

    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = HISTORY_FILE


def test_unlock_failure_wrong_password(tmp_path):
    correct_password = "right"
    wrong_password = "wrong"
    salt = b"abcdef1234567890"
    key = derive_key(correct_password, salt)

    history_file = tmp_path / "history.json"
    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = history_file

    storage = ClipboardStorage(key, salt)
    storage.add_entry("sensitive")
    storage.lock()

    success = storage.unlock(wrong_password)
    assert success is False
    assert storage.is_locked() is True

    ClipboardStorage.__init__.__globals__['HISTORY_FILE'] = HISTORY_FILE