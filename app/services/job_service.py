from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database.models import Certificate, Job
from app.services.certificate_service import generate_single_certificate


def process_job(job_id: int, database_session_factory) -> None:
    db: Session = database_session_factory()
    try:
        job = db.get(Job, job_id)
        if job is None:
            return

        job.status = "PROCESSING"
        db.commit()
        certificates = (
            db.query(Certificate)
            .filter(Certificate.job_id == job_id)
            .order_by(Certificate.id)
            .all()
        )

        for certificate in certificates:
            generate_single_certificate(
                db=db,
                certificate=certificate,
                event_name=job.event_name,
                event_date=job.event_date,
            )
            db.refresh(certificate)
            job.processed_count += 1
            if certificate.status == "SUCCESS":
                job.success_count += 1
            else:
                job.failure_count += 1
            db.commit()

        if job.failure_count == 0:
            job.status = "COMPLETED"
        elif job.success_count == 0:
            job.status = "FAILED"
        else:
            job.status = "COMPLETED_WITH_ERRORS"
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
    except Exception:
        db.rollback()
        job = db.get(Job, job_id)
        if job is not None:
            job.status = "FAILED"
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()