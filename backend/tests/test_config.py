import pytest

import config

ENV_KEYS = ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT"]


def write_env(tmp_path, text):
    env_file = tmp_path / ".env"
    env_file.write_text(text, encoding="utf-8")
    return env_file


def clear_env(monkeypatch):
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_load_settings_reads_values_from_env_file(tmp_path, monkeypatch):
    clear_env(monkeypatch)
    env_file = write_env(
        tmp_path,
        "DB_NAME=etir_test\n"
        "DB_USER=etir_user\n"
        "DB_PASSWORD=p@ss!word\n"
        "DB_HOST=db.example\n"
        "DB_PORT=6543\n",
    )

    settings = config.load_settings(env_file)

    assert settings.db_name == "etir_test"
    assert settings.db_user == "etir_user"
    assert settings.db_password == "p@ss!word"
    assert settings.db_host == "db.example"
    assert settings.db_port == 6543


def test_settings_builds_single_encoded_dsn(tmp_path, monkeypatch):
    clear_env(monkeypatch)
    env_file = write_env(
        tmp_path,
        "DB_NAME=etir_test\n"
        "DB_USER=etir_user\n"
        "DB_PASSWORD=p@ss!word\n"
        "DB_HOST=db.example\n"
        "DB_PORT=6543\n",
    )

    settings = config.load_settings(env_file)

    assert settings.database_url == (
        "postgresql://etir_user:p%40ss%21word@db.example:6543/etir_test"
    )


def test_load_settings_fails_when_required_value_is_missing(tmp_path, monkeypatch):
    clear_env(monkeypatch)
    env_file = write_env(tmp_path, "DB_NAME=etir_test\nDB_USER=etir_user\n")

    with pytest.raises(RuntimeError, match="DB_PASSWORD"):
        config.load_settings(env_file)


def test_load_settings_rejects_invalid_port(tmp_path, monkeypatch):
    clear_env(monkeypatch)
    env_file = write_env(
        tmp_path,
        "DB_NAME=etir_test\n"
        "DB_USER=etir_user\n"
        "DB_PASSWORD=secret\n"
        "DB_HOST=localhost\n"
        "DB_PORT=not-a-port\n",
    )

    with pytest.raises(RuntimeError, match="DB_PORT"):
        config.load_settings(env_file)
