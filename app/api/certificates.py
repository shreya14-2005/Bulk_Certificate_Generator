from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Certificate, Job
from app.schemas.certificate import CertificateStatusResponse


router = APIRouter(tags=["Certificates"])


@router.get(
    "/jobs/{job_id}/certificates",
    response_model=list[CertificateStatusResponse],
)
def list_job_certificates(
    job_id: int,
    db: Session = Depends(get_db),
) -> list[CertificateStatusResponse]:
    if db.get(Job, job_id) is None:
        raise HTTPException(status_code=404, detail="Job not found")
    certificates = (
        db.query(Certificate)
        .filter(Certificate.job_id == job_id)
        .order_by(Certificate.id)
        .all()
    )
    return [
        CertificateStatusResponse(
            certificate_id=certificate.id,
            recipient_name=certificate.recipient_name,
            recipient_email=certificate.recipient_email,
            status=certificate.status,
            error_message=certificate.error_message,
            download_url=(
                f"/certificates/{certificate.id}/download"
                if certificate.status == "SUCCESS"
                else None
            ),
        )
        for certificate in certificates
    ]


@router.get("/certificates/{certificate_id}/download")
def download_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
) -> FileResponse:
    certificate = db.get(Certificate, certificate_id)
    if certificate is None:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if certificate.status != "SUCCESS" or not certificate.file_path:
        raise HTTPException(status_code=409, detail="Certificate is not ready")
    path = Path(certificate.file_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Certificate file not found")
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=path.name,
    )