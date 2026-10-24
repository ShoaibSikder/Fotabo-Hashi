# Fotabo Hashi

![License](https://img.shields.io/badge/License-MIT-blue)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB)
![Backend](https://img.shields.io/badge/Backend-Django-0C4B33)
![API](https://img.shields.io/badge/API-Django%20REST%20Framework-red)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791)
![Deployment](https://img.shields.io/badge/Deploy-Vercel%20%2B%20Render-black)

Fotabo Hashi is a bilingual blood donation and community support platform. It helps people find nearby blood donors, publish and manage blood requests, and recognize verified donations. The system has separate user and administrator workspaces.

The frontend is a React single-page application. The backend is a Django REST API using PostgreSQL, JWT authentication in secure cookies, Redis for caching and request throttling, Supabase Storage for member photos, and Resend for account email delivery.

## Contents

- [Screenshots](#screenshots)
- [Features](#features)
- [Roles and access](#roles-and-access)
- [Technology](#technology)
- [Architecture](#architecture)
- [Project layout](#project-layout)
- [API overview](#api-overview)
- [Environment configuration](#environment-configuration)
- [Local development](#local-development)
- [Checks](#checks)
- [Deployment](#deployment)
- [License](#license)

## Screenshots

Screenshots are in [`frontend/public/system images`](frontend/public/system%20images).

| Public site | User dashboard |
| --- | --- |
| ![Public site](frontend/public/system%20images/public%20page.png) | ![User dashboard](frontend/public/system%20images/user%20dashboard.png) |

| Donor search | Blood requests |
| --- | --- |
| ![Donor search](frontend/public/system%20images/find%20donor.png) | ![Blood requests](frontend/public/system%20images/blood%20requests.png) |

| Administrator dashboard | Registration |
| --- | --- |
| ![Administrator dashboard](frontend/public/system%20images/admin%20dashboard.png) | ![Registration](frontend/public/system%20images/registration.png) |

## Features

### Public site

- Organization information, notices, and active members.
- Responsive public pages in English and Bangla.
- Donor, blood-request, registration, and login entry points.
- Locally hosted hero video in `frontend/public/videos`.

### User workspace

- Email and password registration and login.
- Secure access and refresh cookie authentication, logout, and password reset.
- User dashboard, profile and donation availability settings.
- Donor search by blood group and location.
- Create, view, fulfill, and cancel blood requests according to request ownership and status rules.
- Leaderboard based on administrator-verified donation records.
- In-app notifications and account settings.

### Administrator workspace

- Separate administrator dashboard and protected routes.
- Search and filter people by name, email, phone, and blood group; review and update accounts.
- Delete accounts with protections against self-deletion and deleting the last active administrator.
- Record verified donations and review user-submitted donation-count changes.
- Manage blood requests, public notices, and active members.
- Review audit activity and account notifications.

### Reliability and security

- Django REST Framework API versioned under `/api/v1/`.
- Role checks enforced by the backend as well as the frontend routes.
- API pagination, throttling, structured errors, readiness checks, and request IDs.
- Redis-backed caching and rate limits in production; local development can use Django's in-memory cache.
- Supabase Storage integration for active-member photos. User profile photo uploads are not part of the registration/profile flow.
- CI checks Python formatting and linting, runs backend tests, validates the API schema, audits dependencies, and builds the frontend.

## Roles and access

The application roles are `USER` and `ADMIN`.

| Role | Workspace |
| --- | --- |
| Public visitor | Public pages, notices, member listing, login, and registration |
| `USER` | `/dashboard`, `/donors`, `/requests`, `/leaderboard`, `/profile`, and `/settings` |
| `ADMIN` | `/admin/dashboard`, `/admin/users`, `/admin/donation-reviews`, `/admin/requests`, `/admin/public-content`, and `/admin/audit` |

The API independently checks permissions. Hiding a route in the frontend is not the backend security boundary.

## Technology

| Area | Stack |
| --- | --- |
| Frontend | React 18, Vite 6, React Router 7, Tailwind CSS 3, Lucide |
| Backend | Python 3.13, Django 5.2, Django REST Framework |
| Authentication | Simple JWT, secure HttpOnly cookies, CSRF protection |
| Database | PostgreSQL (Supabase PostgreSQL in the hosted setup) |
| Cache and throttling | Redis, django-redis |
| Media | Supabase Storage |
| Email | Resend |
| Hosting | Vercel frontend, Render API |
| Quality checks | pytest, Ruff, Black, pip-audit, ESLint, npm audit |

## Architecture

```text
Browser
  └── React + Vite on Vercel
        └── HTTPS /api/v1/ requests with secure cookies
              └── Django REST API on Render
                    ├── PostgreSQL
                    ├── Redis
                    ├── Supabase Storage
                    └── Resend email API
```

The frontend reads its API root from `VITE_API_BASE_URL`. Django settings are split into `base.py`, `development.py`, `testing.py`, and `production.py`. Render runs database migrations before starting a deployment.

## Project layout

```text
Fotabo-Hashi/
├── .github/
│   ├── dependabot.yml
│   └── workflows/ci.yml
├── backend/
│   ├── api/v1/                 # API version routing and health endpoints
│   ├── apps/
│   │   ├── accounts/           # Custom User model and authentication
│   │   ├── administration/     # Admin API and review actions
│   │   ├── audit/              # Administrative audit records
│   │   ├── blood_requests/
│   │   ├── common/              # Shared API infrastructure
│   │   ├── content/             # Organization details, notices, members
│   │   ├── donors/
│   │   ├── leaderboard/
│   │   ├── notifications/
│   │   └── profiles/
│   ├── config/settings/        # Environment-specific Django settings
│   ├── infrastructure/         # Cache, database, storage, monitoring, logging
│   ├── tests/                   # Backend unit, API, and security tests
│   ├── manage.py
│   ├── requirements.txt         # Runtime packages
│   └── requirements-dev.txt    # Runtime and development/test packages
├── frontend/
│   ├── public/                  # Static assets and hero video
│   └── src/
│       ├── app/                 # App providers and route map
│       ├── components/          # Shared UI and layouts
│       ├── contexts/            # Authentication and language state
│       ├── features/            # User, admin, auth, and public pages
│       ├── i18n/                # English and Bangla translations
│       └── services/            # API client and endpoint configuration
├── render.yaml
└── README.md
```

### Backend apps

| App | Responsibility |
| --- | --- |
| `accounts` | Custom email-based user model, registration, login, logout, and password reset |
| `profiles` | User names, phone, blood group, location, and donation availability |
| `donors` | Publicly safe donor search and filtering |
| `blood_requests` | Request creation, ownership, status transitions, and summaries |
| `leaderboard` | Verified donation records and user-submitted count review |
| `content` | Organization information, active members, and notices |
| `notifications` | User and administrator notifications and read state |
| `administration` | Admin overview, account control, donation review, public content, and audit views |
| `audit` | Records administrative and security-sensitive actions |
| `common` | Shared pagination, responses, error handling, and throttling |

### Frontend architecture

- `src/app` composes providers and lazy-loaded routes.
- `src/features` keeps public, authentication, user, and admin pages grouped by feature.
- `src/components/layout` contains the public, user, and admin application shells.
- `src/services` centralizes the API root, endpoint paths, and cookie/CSRF-aware API client.
- `src/contexts` provides authentication and language state.
- `src/i18n/locales` contains English and Bangla messages.

## API overview

Base path: `/api/v1/`

| Endpoint | Purpose |
| --- | --- |
| `/health/`, `/health/live/`, `/health/ready/` | API, liveness, and dependency health |
| `/auth/register/`, `/auth/login/`, `/auth/refresh/`, `/auth/logout/` | Authentication |
| `/auth/password-reset/`, `/auth/password-reset/confirm/` | Password reset |
| `/profile/me/` | Current user profile |
| `/donors/` | Donor search |
| `/blood-requests/` | Blood request listing and creation |
| `/blood-requests/mine/summary/` | Current user's request summary |
| `/leaderboard/` | Verified donation leaderboard |
| `/content/organization/`, `/content/notices/`, `/content/active-members/` | Public content |
| `/notifications/` | Current user's notifications and read actions |
| `/admin/` | Protected overview, user, donation, request, content, and audit APIs |
| `/schema/`, `/docs/`, `/redoc/` | OpenAPI schema and API documentation |

## Environment configuration

Copy the examples for local development and fill in local service values:

- Backend: [`backend/.env.example`](backend/.env.example)
- Frontend: [`frontend/.env.example`](frontend/.env.example)

The backend needs a PostgreSQL `DATABASE_URL`. Set `DJANGO_SETTINGS_MODULE=config.settings.development` for local work. Local development defaults to Django's in-memory cache; set `DJANGO_USE_REDIS_CACHE=True` only when a local Redis service is running.

For deployment, set environment variables in Render and Vercel, not in a committed file. Render requires the database URL, allowed host(s), frontend CORS and CSRF origins, HTTPS frontend base URL, Supabase URL and service-role key, and Resend key and verified sender. `REDIS_URL` is wired to the private Render Key Value service by `render.yaml`. Vercel requires `VITE_API_BASE_URL` pointing to the deployed API's `/api/v1` path.

Never expose `DJANGO_SECRET_KEY`, database credentials, `SUPABASE_SERVICE_ROLE_KEY`, or `RESEND_API_KEY` through `VITE_*` variables. Vite variables are public in the browser bundle.

## Local development

### Backend (Windows PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and set `DATABASE_URL` to your PostgreSQL connection string. Local development does not require Redis unless `DJANGO_USE_REDIS_CACHE=True`. Then run:

```powershell
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

### Frontend

In another terminal:

```powershell
cd frontend
npm ci
Copy-Item .env.example .env
npm run dev
```

The Vite development server runs at `http://127.0.0.1:5173/`. The example API URL targets the local Django server. Ensure the backend CORS and CSRF origin lists include the actual Vite origin if its port differs.

## Checks

Backend checks and tests:

```powershell
cd backend
ruff check .
black --check .
python manage.py check
pytest
python manage.py spectacular --validate
pip-audit -r requirements.txt
```

Frontend checks:

```powershell
cd frontend
npm ci
npm run lint
npm audit --audit-level=moderate
npm run build
```

CI runs these checks with PostgreSQL and Redis services. Run them before deploying changes.

## Deployment

### Render API

1. Push the repository to GitHub and create a Render Blueprint from [`render.yaml`](render.yaml).
2. Provide the requested Supabase, Resend, domain, and database values in Render's environment settings. Do not put production secrets in Git.
3. Use HTTPS origins in `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`. Include the frontend origin in both; put the backend host in `DJANGO_ALLOWED_HOSTS`.
4. Set `FRONTEND_BASE_URL` to the deployed frontend origin. The verified Resend sender must be authorized for your Resend account.
5. Render builds static assets, applies database migrations in the pre-deploy step, and starts Gunicorn. The blueprint requires a paid web service for pre-deploy migrations and provisions a private Redis service.

### Vercel frontend

1. Import the same repository into Vercel and set the project root directory to `frontend`.
2. Set `VITE_API_BASE_URL` to `https://<your-api-domain>/api/v1` for the production environment.
3. Deploy after the Render API is available, then check the public page, authentication, password reset, donor search, requests, and admin access.

Use frontend and API custom domains under the same parent domain where possible (for example, `app.example.com` and `api.example.com`). This helps browsers treat the secure cross-origin authentication cookies as same-site. Match the Render region with the Supabase database region to limit database round-trip latency.

After deployment, check `https://<your-api-domain>/api/v1/health/ready/`. Create the initial administrator using Render's Shell:

```bash
python manage.py createsuperuser
```

Back up the production database and verify that a restore works before relying on it for live data. Enable HSTS subdomain and preload options only after confirming every affected subdomain is HTTPS-only.

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE).
