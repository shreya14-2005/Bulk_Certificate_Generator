from pathlib import Path

from app.core.config import GENERATED_DIR


def ensure_generated_directory() -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)


def get_certificate_path(job_id: int, certificate_id: int) -> Path:
    ensure_generated_directory()
    return GENERATED_DIR / f"job_{job_id}_certificate_{certificate_id}.pdf"