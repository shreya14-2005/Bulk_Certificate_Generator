from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Certificate, Job
from app.schemas.job import JobCreate, JobCreateResponse, JobStatusResponse
from app.services.job_service import process_job


router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("", response_model=JobCreateResponse, status_code=status.HTTP_202_ACCEPTED)
def create_job(
	payload: JobCreate,
	background_tasks: BackgroundTasks,
	request: Request,
	db: Session = Depends(get_db),
) -> JobCreateResponse:
	job = Job(
		event_name=payload.event_name,
		event_date=payload.event_date.isoformat(),
		status="PENDING",
		total_count=len(payload.recipients),
	)
	db.add(job)
	db.flush()
	db.add_all(
		[
			Certificate(
				job_id=job.id,
				recipient_name=recipient.name,
				recipient_email=str(recipient.email),
				status="PENDING",
			)
			for recipient in payload.recipients
		]
	)
	db.commit()
	db.refresh(job)
	background_tasks.add_task(
		process_job,
		job.id,
		request.app.state.session_factory,
	)
	return JobCreateResponse(
		job_id=job.id,
		status=job.status,
		total_count=job.total_count,
	)


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: int, db: Session = Depends(get_db)) -> JobStatusResponse:
	job = db.get(Job, job_id)
	if job is None:
		raise HTTPException(status_code=404, detail="Job not found")
	return JobStatusResponse(
		job_id=job.id,
		event_name=job.event_name,
		event_date=date.fromisoformat(job.event_date),
		status=job.status,
		total_count=job.total_count,
		processed_count=job.processed_count,
		success_count=job.success_count,
		failure_count=job.failure_count,
		created_at=job.created_at,
		completed_at=job.completed_at,
	)
