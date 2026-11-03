# Backend API

API foundation uses FastAPI, SQLAlchemy 2 and PostgreSQL. Authentication includes registration/consent, email verification, login, refresh rotation, logout, current user, resend verification and password reset. Student routes cover profile data, preferences and visibility.

Implemented auth endpoints: `POST /api/v1/auth/register`, `POST /api/v1/auth/verify-email`, `POST /api/v1/auth/resend-verification`, `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`, `GET /api/v1/auth/me`, `POST /api/v1/auth/forgot-password`, and `POST /api/v1/auth/reset-password`.

Student profile routes: `GET/PATCH /api/v1/students/me/profile`, `GET/PUT /api/v1/students/me/preferences`, and `PUT /api/v1/students/me/visibility`. Profile updates support education, skills, experience and project collections. CV routes support PDF/DOCX upload (10 MB cap), listing, default selection, deletion and local text extraction.

## Local development

1. Start PostgreSQL and local email inbox from the project root: `docker compose up -d db mailpit`.
2. From the project root, create a virtual environment and install dependencies:
   `py -m venv backend/.venv` then `backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt`.
3. Copy `backend/.env.example` to `backend/.env`.
4. From `backend/`, apply the schema with `alembic upgrade head`.
5. From `backend/`, run `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload` (or `.\.venv\Scripts\uvicorn.exe app.main:app --reload`).
6. From `backend/`, run `.\.venv\Scripts\python.exe -m app.scripts.seed_dev` to create demo users.
7. Open `http://localhost:8000` for the app, `/docs` for API docs, `/api/v1/health`, or `/api/v1/ready`. Local verification and reset emails appear at `http://localhost:8025`.

## Local demo accounts

The dev seed creates these verified accounts; passwords can be overridden with the matching `SEED_*_PASSWORD` environment variables:

| Role | Email | Default password |
|---|---|---|
| Platform admin | `admin@huong.local` | `AdminDemo2026!` |
| Student | `student@huong.local` | `StudentDemo2026!` |
| Recruiter | `recruiter@huong.local` | `RecruiterDemo2026!` |

The login screen retrieves and displays these credentials only through `GET /api/v1/system/demo-accounts` when `ENVIRONMENT=development`; that endpoint returns 404 otherwise. Run the seed only in development. It never resets the password of an account that already exists. The recruiter’s demo company stays pending verification. Do not reuse these credentials outside local testing.

Uploaded CVs are stored under `backend/storage`, outside the public static directory. The initial parser extracts PDF/DOCX text and uses basic email/phone/skill matching; it is not an AI parser and does not scan for malware yet. Do not process real CVs in production until malware scanning and private object storage are configured.

Do not use the sample database password outside local development. Production secrets must come from the deployment environment.

## Jobs and role permissions

- `GET /api/v1/jobs` returns published jobs.
- `POST/PATCH/DELETE /api/v1/jobs` requires a recruiter account and company write permission. Recruiters may change only their company's jobs; an unverified company may save drafts, and publishing requires verification via `POST /api/v1/jobs/{job_id}/publish`.
- `GET /api/v1/recruiter/jobs` lists the authenticated recruiter's company jobs.
- `POST /api/v1/jobs/{job_id}/applications`, `GET /api/v1/applications/me`, and `DELETE /api/v1/applications/me/{application_id}` require a student account. The API checks CV ownership and prevents duplicate applications.
- Recruiters with company recruiting permission may read/process applications only for their own company jobs, using `/api/v1/recruiter/jobs/{job_id}/applications` and `/api/v1/recruiter/applications/{application_id}`. CV downloads are scoped to that application.
- Migrate the new job and application tables with `alembic upgrade head` before using these endpoints.

Role enforcement is performed by FastAPI dependencies, so hiding or changing frontend controls cannot grant a different role's permissions.
