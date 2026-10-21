from source.security import hash_password, verify_password


def test_hash_password_uses_random_salt():
    first = hash_password("secret123")
    second = hash_password("secret123")

    assert first != second
    assert first.startswith("scrypt$")
    assert second.startswith("scrypt$")


def test_verify_password_accepts_correct_password():
    password_hash = hash_password("secret123")

    assert verify_password("secret123", password_hash) is True


def test_verify_password_rejects_wrong_password():
    password_hash = hash_password("secret123")

    assert verify_password("wrong-password", password_hash) is False


def test_verify_password_rejects_malformed_hash():
    assert verify_password("secret123", "not-a-valid-hash") is False
