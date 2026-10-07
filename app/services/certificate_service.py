from pathlib import Path

from sqlalchemy.orm import Session

from app.database.models import Certificate
from app.templates.certificate_template import generate_certificate
from app.utils.file_utils import get_certificate_path


def generate_single_certificate(
    db: Session,
    certificate: Certificate,
    event_name: str,
    event_date: str,
) -> None:
    certificate_id = certificate.id
    output_path: Path | None = None

    try:
        certificate.status = "PROCESSING"
        db.commit()
        output_path = get_certificate_path(certificate.job_id, certificate_id)
        generate_certificate(
            output_path=output_path,
            recipient_name=certificate.recipient_name,
            event_name=event_name,
            event_date=event_date,
        )
        certificate.status = "SUCCESS"
        certificate.file_path = str(output_path)
        certificate.error_message = None
        db.commit()
    except Exception as exc:
        db.rollback()
        if output_path is not None:
            output_path.unlink(missing_ok=True)
        failed_certificate = db.get(Certificate, certificate_id)
        if failed_certificate is not None:
            failed_certificate.status = "FAILED"
            failed_certificate.file_path = None
            failed_certificate.error_message = str(exc)[:2000]
            db.commit()