"""Security middleware tests."""

import pytest
from httpx import AsyncClient

from app.core.middleware import login_rate_limiter


@pytest.mark.asyncio
async def test_security_headers_are_added(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"


@pytest.mark.asyncio
async def test_login_rate_limit_returns_429(client: AsyncClient) -> None:
    login_rate_limiter.clear()

    for _ in range(5):
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrong"},
        )
        assert response.status_code == 401

    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong"},
    )

    assert response.status_code == 429


@pytest.mark.asyncio
async def test_http01_challenge_is_not_rate_limited(client: AsyncClient) -> None:
    login_rate_limiter.clear()

    response = await client.get("/.well-known/acme-challenge/missing-token")

    assert response.status_code == 404
    assert response.headers["x-content-type-options"] == "nosniff"
