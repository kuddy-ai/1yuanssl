"""Certificate API smoke tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["database"] == "healthy"


@pytest.mark.asyncio
async def test_protected_certificate_api_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/certificates/orders")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_login_returns_token(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"] == "dev-admin-token"
    assert body["data"]["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_admin_login_rejects_invalid_credentials(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_certificate_order_lifecycle(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/certificates/orders",
        headers=auth_headers,
        json={
            "domains": ["example.com", "www.example.com"],
            "email": "admin@example.com",
            "cert_type": "multi",
            "challenge_type": "http-01",
            "auto_renew": True,
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["success"] is True
    order = created["data"]
    assert order["status"] == "pending"
    assert order["domains"] == ["example.com", "www.example.com"]
    order_id = order["id"]

    challenges_response = await client.get(
        f"/api/v1/certificates/orders/{order_id}/challenges",
        headers=auth_headers,
    )

    assert challenges_response.status_code == 200
    challenges = challenges_response.json()["data"]
    assert len(challenges) == 2
    assert {challenge["domain"] for challenge in challenges} == {"example.com", "www.example.com"}
    assert all(challenge["challenge_type"] == "http-01" for challenge in challenges)
    assert all(challenge["token"] for challenge in challenges)

    token = challenges[0]["token"]
    http01_response = await client.get(f"/.well-known/acme-challenge/{token}")
    assert http01_response.status_code == 200
    assert http01_response.text == challenges[0]["key_authorization"]

    validate_response = await client.post(
        f"/api/v1/certificates/orders/{order_id}/validate",
        headers=auth_headers,
    )

    assert validate_response.status_code == 200
    validated = validate_response.json()["data"]
    assert validated["status"] == "validating"

    issue_response = await client.post(
        f"/api/v1/certificates/orders/{order_id}/issue",
        headers=auth_headers,
    )

    assert issue_response.status_code == 200
    issued = issue_response.json()["data"]
    assert issued["status"] == "issued"
    assert issued["not_after"] is not None

    download_response = await client.get(
        f"/api/v1/certificates/orders/{order_id}/download/fullchain",
        headers=auth_headers,
    )

    assert download_response.status_code == 200
    assert "BEGIN CERTIFICATE" in download_response.text
    assert "attachment; filename=cert-" in download_response.headers["content-disposition"]


@pytest.mark.asyncio
async def test_dns01_order_returns_txt_record(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/certificates/orders",
        headers=auth_headers,
        json={
            "domains": ["*.example.com"],
            "email": "admin@example.com",
            "cert_type": "wildcard",
            "challenge_type": "dns-01",
            "auto_renew": False,
        },
    )

    assert create_response.status_code == 201
    order_id = create_response.json()["data"]["id"]

    challenges_response = await client.get(
        f"/api/v1/certificates/orders/{order_id}/challenges",
        headers=auth_headers,
    )

    assert challenges_response.status_code == 200
    challenges = challenges_response.json()["data"]
    assert len(challenges) == 1
    assert challenges[0]["challenge_type"] == "dns-01"
    assert challenges[0]["dns_txt_name"]
    assert challenges[0]["dns_txt_value"]
