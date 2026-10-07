from app.services import certificate_service


def test_one_generation_failure_does_not_stop_job(client, monkeypatch):
	original_generator = certificate_service.generate_certificate

	def fail_for_one_recipient(**kwargs):
		if kwargs["recipient_name"] == "Morgan Failure":
			raise RuntimeError("simulated PDF error")
		return original_generator(**kwargs)

	monkeypatch.setattr(certificate_service, "generate_certificate", fail_for_one_recipient)
	response = client.post(
		"/jobs",
		json={
			"event_name": "Workshop",
			"event_date": "2026-10-07",
			"recipients": [
				{"name": "Morgan Failure", "email": "morgan@example.com"},
				{"name": "Casey Success", "email": "casey@example.com"},
			],
		},
	)

	job_id = response.json()["job_id"]
	job = client.get(f"/jobs/{job_id}").json()
	results = client.get(f"/jobs/{job_id}/certificates").json()
	assert job["status"] == "COMPLETED_WITH_ERRORS"
	assert job["processed_count"] == 2
	assert job["success_count"] == 1
	assert job["failure_count"] == 1
	assert results[0]["error_message"] == "simulated PDF error"
	assert results[1]["status"] == "SUCCESS"
