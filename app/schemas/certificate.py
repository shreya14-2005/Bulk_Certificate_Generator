from pydantic import BaseModel


class CertificateStatusResponse(BaseModel):
	certificate_id: int
	recipient_name: str
	recipient_email: str
	status: str
	error_message: str | None = None
	download_url: str | None = None
