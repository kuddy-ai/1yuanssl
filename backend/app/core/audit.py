"""Security audit logging helpers."""

import json
from typing import Any

from app.core.logging import SecureLogger, sanitize_for_log

audit_logger = SecureLogger("app.audit")


def audit_event(event: str, **metadata: Any) -> None:
    """Write a structured, sanitized audit event."""
    payload = {
        "event": event,
        **metadata,
    }
    sanitized = sanitize_for_log(payload)
    audit_logger.logger.info(
        "audit_event %s",
        json.dumps(sanitized, ensure_ascii=False, sort_keys=True),
    )
