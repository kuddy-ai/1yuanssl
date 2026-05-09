"""Configuration safety tests."""

import pytest
from pydantic import ValidationError

from app.config import DEFAULT_ENCRYPTION_KEY, Settings


def test_development_defaults_are_allowed() -> None:
    settings = Settings()

    assert settings.is_development is True


def test_production_rejects_default_sensitive_settings() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(APP_ENV="production", ENCRYPTION_KEY=DEFAULT_ENCRYPTION_KEY)

    error = str(exc_info.value)
    assert "ENCRYPTION_KEY must be changed in production" in error
    assert "ADMIN_PASSWORD must be changed in production" in error
    assert "ADMIN_API_TOKEN must be changed in production" in error


def test_production_rejects_debug_mode() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            APP_ENV="production",
            DEBUG=True,
            ENCRYPTION_KEY="prod-encryption-key-with-enough-length",
            ADMIN_PASSWORD="prod-password",
            ADMIN_API_TOKEN="prod-token",
            CORS_ORIGINS=["https://ssl.example.com"],
            ALLOWED_HOSTS=["ssl.example.com"],
        )

    assert "DEBUG must be false in production" in str(exc_info.value)


def test_production_accepts_hardened_settings() -> None:
    settings = Settings(
        APP_ENV="production",
        DEBUG=False,
        ENCRYPTION_KEY="prod-encryption-key-with-enough-length",
        ADMIN_USERNAME="ops",
        ADMIN_PASSWORD="prod-password",
        ADMIN_API_TOKEN="prod-token",
        CORS_ORIGINS=["https://ssl.example.com"],
        ALLOWED_HOSTS=["ssl.example.com"],
    )

    assert settings.is_production is True
    assert settings.ENCRYPTION_KEY != DEFAULT_ENCRYPTION_KEY
