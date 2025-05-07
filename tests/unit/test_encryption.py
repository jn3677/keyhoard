import pytest
from keyhoard.encryption import encrypt,decrypt,derive_key,generate_salt

def test_encrypt_decrypt_round_test(test_key):
    plain_text = "a plain text to encrypt"
    cipher_text = encrypt(plain_text, test_key)
    decrypted = decrypt(cipher_text, test_key)

    assert decrypted == plain_text
    assert cipher_text != plain_text

def test_encrypt_with_empty(test_key):
    plaintext = ""
    cipher_text = encrypt(plaintext, test_key)
    decrypted = decrypt(cipher_text, test_key)

    assert decrypted == plaintext

def test_encrypt_diff_keys_fail(test_key):
    plaintext = "secret"
    cipher_text = encrypt(plaintext,test_key)

    wrong_key = b'wrongkeywrongkey'

    with pytest.raises(ValueError, match="Invalid padding"):
        decrypt(cipher_text, wrong_key)


@pytest.mark.parametrize("plain_text", [
    "normal text",
    "12334567890",
    "敏感数据",
    "!@#$%^&*()",
    ""
])
def test_encrypt_decypt_inputs(test_key, plain_text):
    cipher_text = encrypt(plain_text, test_key)
    assert cipher_text != plain_text
    assert decrypt(cipher_text, test_key) == plain_text


def test_generate_salt_len_type():
    salt = generate_salt()
    assert isinstance(salt, bytes)
    assert len(salt) == 16

def test_salt_is_random():
    salt1 = generate_salt()
    salt2 = generate_salt()
    assert salt1 != salt2


def test_derive_key_consistency():
    password = "password"
    salt = b"testsalt12345678"
    key1 = derive_key(password, salt)
    key2 = derive_key(password, salt)

    assert key1 == key2
    assert isinstance(key1, bytes)
    assert len(key1) == 32

def test_derive_key_diff_passwords():
    salt = b"testsalt12345678"
    key1 = derive_key("password1", salt)
    key2 = derive_key("password2", salt)
    assert key1 != key2

def test_derive_key_diff_salt():
    password = "password"
    key1 = derive_key(password, b"testsalt12345678")
    key2 = derive_key(password,b"87654321salttest")
    assert key1 != key2