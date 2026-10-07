from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Job(Base):
	__tablename__ = "jobs"

	id = Column(Integer, primary_key=True, index=True)
	event_name = Column(String(255), nullable=False)
	event_date = Column(String(10), nullable=False)
	status = Column(String(32), nullable=False, default="PENDING", index=True)
	total_count = Column(Integer, nullable=False, default=0)
	processed_count = Column(Integer, nullable=False, default=0)
	success_count = Column(Integer, nullable=False, default=0)
	failure_count = Column(Integer, nullable=False, default=0)
	created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
	completed_at = Column(DateTime(timezone=True), nullable=True)

	certificates = relationship(
		"Certificate",
		back_populates="job",
		cascade="all, delete-orphan",
	)


class Certificate(Base):
	__tablename__ = "certificates"

	id = Column(Integer, primary_key=True, index=True)
	job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
	recipient_name = Column(String(255), nullable=False)
	recipient_email = Column(String(320), nullable=False)
	status = Column(String(32), nullable=False, default="PENDING", index=True)
	file_path = Column(String(1024), nullable=True)
	error_message = Column(Text, nullable=True)

	job = relationship("Job", back_populates="certificates")
