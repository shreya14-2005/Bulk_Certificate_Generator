# Bulk Certificate Generator

A FastAPI service that accepts one bulk request, validates its recipients, generates a PDF certificate for each recipient, and records progress and per-recipient outcomes in SQLite.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux, activate the environment with `source .venv/bin/activate`.

## Run

```powershell
python run.py
```

The API is available at `http://127.0.0.1:8000`; interactive API documentation is at `/docs`. SQLite data is stored in `certificate_generator.db`, and generated PDFs are stored in `generated/`. Set `DATABASE_URL` or `GENERATED_DIR` to change those locations.

## Create A Generation Job

Submit one request containing the event and recipient list:

```http
POST /jobs
Content-Type: application/json
```

```json
{
	"event_name": "First Aid Training",
	"event_date": "2026-10-07",
	"recipients": [
		{"name": "Alex Rivera", "email": "alex@example.com"},
		{"name": "Sam Chen", "email": "sam@example.com"}
	]
}
```

The endpoint returns HTTP `202 Accepted` with a `job_id`. Each request must contain 1-500 recipients. Names must be non-blank, email addresses must be valid, and `event_date` must be an ISO date (`YYYY-MM-DD`). Invalid request data returns HTTP `422` before a job is created.

## Track And Retrieve Results

- `GET /jobs/{job_id}` returns job status and counts (`total_count`, `processed_count`, `success_count`, and `failure_count`).
- `GET /jobs/{job_id}/certificates` returns each recipient's status and, when successful, a download URL. Failed entries include an error message.
- `GET /certificates/{certificate_id}/download` returns the generated PDF.

Job states are `PENDING`, `PROCESSING`, `COMPLETED`, `COMPLETED_WITH_ERRORS`, and `FAILED`. A certificate generation failure is recorded for that recipient and processing continues for the rest of the job.

## Run Tests

```powershell
python -m pytest
```

## Design Decisions

- FastAPI provides request validation, typed responses, and generated OpenAPI documentation. SQLAlchemy stores jobs and individual certificate outcomes in SQLite; the database URL is configurable.
- One predefined ReportLab template creates one PDF per recipient. Files are stored outside the database, while their paths and status are stored in the certificate row.
- FastAPI `BackgroundTasks` starts processing after the API response, so clients submit one bulk request and poll for progress instead of waiting for every PDF. This is an in-process worker suitable for a single application instance; use a durable queue such as Celery for multi-instance deployments or jobs that must survive process restarts.
- The job row is committed before background work begins. Recipient outcomes and aggregate counters are committed as each certificate is handled, and an individual failure does not abort the remaining certificates.
