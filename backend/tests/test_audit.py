"""Audit logging tests."""

from app.core import audit


def test_audit_event_sanitizes_sensitive_metadata(monkeypatch) -> None:
    calls: list[tuple[str, str]] = []

    def capture(message: str, payload: str) -> None:
        calls.append((message, payload))

    monkeypatch.setattr(audit.audit_logger.logger, "info", capture)

    audit.audit_event(
        "certificate_file_downloaded",
        order_id=1,
        private_key="-----BEGIN PRIVATE KEY-----secret",
        token="very-sensitive-token-value",
        key_authorization="token.mock-thumbprint.more",
    )

    assert calls
    message, payload = calls[0]
    assert message == "audit_event %s"
    assert "certificate_file_downloaded" in payload
    assert "-----BEGIN PRIVATE KEY-----" not in payload
    assert "very-sensitive-token-value" not in payload
    assert "token.mock-thumbprint.more" not in payload
    assert "[SENSITIVE]" in payload
