# AGENTS.md

This file gives coding agents the practical context needed to work in this repository.

## Project Overview

`1yuanssl` is an MVP SSL certificate application and deployment assistant. It is intended to automate Let's Encrypt certificate ordering through ACME, but the current implementation uses a Mock ACME client and does not call the real Let's Encrypt API.

Core principle: avoid collecting customer secrets whenever possible. Do not introduce features that require storing SSH passwords, root keys, cloud account master keys, or DNS provider master keys.

## Repository Layout

- `backend/`: FastAPI backend.
- `frontend/`: React + TypeScript + Vite frontend.
- `docker-compose.yml`: local Docker development stack, exposing backend on `7000` and frontend on `7001`.
- `Makefile`: common install, dev, Docker, database, test, lint, and format commands.
- `CLAUDE.md`: existing Claude Code guidance. Keep it consistent if changing project conventions.

## Backend

Tech stack:

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x async ORM
- Pydantic v2 / pydantic-settings
- SQLite for development, PostgreSQL support reserved
- AES-256-GCM style encryption utilities for stored certificate material
- uv for dependency and command execution

Important paths:

- `backend/app/main.py`: FastAPI app entrypoint, CORS setup, router registration, startup DB initialization.
- `backend/app/config.py`: environment-based settings. Reads `.env` from the backend working directory.
- `backend/app/db/session.py`: async engine/session factory and `init_db()`.
- `backend/app/api/v1/`: REST API routers.
- `backend/app/api/v1/challenges.py`: special HTTP-01 route at `/.well-known/acme-challenge/{token}` without the `/api/v1` prefix.
- `backend/app/services/`: business logic.
- `backend/app/acme/`: ACME abstractions and mock implementation.
- `backend/app/models/`: SQLAlchemy models.
- `backend/app/schemas/`: Pydantic request/response schemas.
- `backend/app/core/security.py`: encryption/decryption helpers. Treat outputs and inputs as sensitive.
- `backend/alembic/`: migration scaffolding exists, but startup currently creates tables via `Base.metadata.create_all`.

Current API shape:

- API prefix: `/api/v1`
- Health: `/api/v1/health`
- Certificate stats: `/api/v1/certificates/stats`
- Certificate orders: `/api/v1/certificates/orders`
- Order challenges: `/api/v1/certificates/orders/{order_id}/challenges`
- Validate order: `/api/v1/certificates/orders/{order_id}/validate`
- Issue certificate: `/api/v1/certificates/orders/{order_id}/issue`
- Download files: `/api/v1/certificates/orders/{order_id}/download/{file_type}`
- HTTP-01 challenge: `/.well-known/acme-challenge/{token}`

Backend style:

- Prefer async FastAPI handlers and async SQLAlchemy sessions.
- Keep business logic in `services/`; API routers should stay thin.
- Add or update Pydantic schemas when API contracts change.
- Keep database model changes aligned with schemas and services.
- Do not log private keys, certificate PEM bodies, tokens, authorization strings, API credentials, or decrypted secret values.
- Use `SecureLogger` patterns from `backend/app/core/logging.py` for logs that may include sensitive context.

## Frontend

Tech stack:

- React 18
- TypeScript
- Vite
- Ant Design
- React Router
- Axios
- pnpm

Important paths:

- `frontend/src/main.tsx`: React entrypoint.
- `frontend/src/App.tsx`: route definitions.
- `frontend/src/components/Layout.tsx`: shared page layout.
- `frontend/src/pages/`: page components.
- `frontend/src/api/client.ts`: Axios client. Default backend base URL is `http://localhost:7000/api/v1`.
- `frontend/src/api/certificates.ts`: certificate API wrapper functions.
- `frontend/src/types/certificate.ts`: shared TypeScript API/domain types.
- `frontend/src/styles/index.css`: global styling.

Frontend notes:

- Current implemented pages are dashboard and certificate list.
- Some navigation targets are referenced but not implemented yet, such as `/certificates/:id` and `/certificates/create`.
- Keep UI consistent with Ant Design and existing Chinese product copy.
- Update `frontend/src/types/certificate.ts` together with backend schema changes.
- Keep API calls centralized in `frontend/src/api/`.

## Common Commands

Install dependencies:

```bash
make install
make install-backend
make install-frontend
```

Run locally:

```bash
make dev-backend
make dev-frontend
```

Docker development:

```bash
make docker-dev
make docker-logs
make docker-down
```

Database:

```bash
make db-init
make db-migrate
make db-reset
```

Checks:

```bash
make lint-backend
make format-backend
make test-backend
make lint-frontend
make format-frontend
make test-frontend
```

Important caveat: `make test-backend` expects `backend/tests/`, and `make test-frontend` expects a frontend `test` script. At the time this file was written, neither exists, so these commands may fail until tests are added.

## Environment

Use the example env files as references:

- `.env.example`
- `backend/.env.example`
- `frontend/.env.example`

Key variables:

- `ENCRYPTION_KEY`: required to protect stored certificate/private-key material. The default value is for local MVP only and must not be used in production.
- `ACME_MODE`: currently expected to be `mock` for MVP.
- `DATABASE_URL`: defaults to SQLite development database.
- `CORS_ORIGINS`: frontend origins allowed by the backend.
- `VITE_API_BASE_URL`: frontend API base URL.

## Security Rules

- Do not commit real `.env` files, private keys, certificates, database dumps, API tokens, SSH keys, DNS provider credentials, or customer data.
- Do not add static file serving for private keys or certificate downloads. Keep certificate downloads behind API logic.
- Prefer customer-side private key generation / CSR flows for future real ACME features when practical.
- For DNS automation, require least-privilege zone-scoped tokens. Never encourage use of account master keys.
- Preserve the MVP mock ACME behavior unless the task explicitly asks to implement real ACME integration.

## Development Guidance

- Development workflow: create or confirm a GitHub issue first, switch to a dedicated development branch for that issue, commit the finished changes, open a pull request, and merge the pull request after checks/review. Do not develop directly on `main` for feature or fix work.
- Read existing code before changing patterns. This repo is small and favors direct service classes over broad abstractions.
- Keep changes scoped. Avoid unrelated rewrites or formatting churn.
- If adding backend behavior, update route, schema, service, and model layers as needed.
- If adding frontend behavior, update page/component, API wrapper, and shared types together.
- Prefer Makefile commands when available.
- After backend changes, run at least `make lint-backend` if dependencies are installed.
- After frontend changes, run at least `make lint-frontend` or `pnpm build` if dependencies are installed.
- When tests are missing, mention that verification was limited and add focused tests if the change is risky enough.

## Known MVP Gaps

- Real Let's Encrypt integration is not implemented.
- APScheduler renewal flow is scaffolded but not enabled.
- Authentication and authorization are not implemented.
- Frontend create/detail certificate pages are referenced by navigation but not present.
- Alembic exists, but the app currently relies on automatic table creation at startup.
- Test directories/scripts are incomplete.
