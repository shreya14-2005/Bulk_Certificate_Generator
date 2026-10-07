def test_job_generates_a_pdf_certificate(client):
	response = client.post(
		"/jobs",
		json={
			"event_name": "Python Basics",
			"event_date": "2026-10-07",
			"recipients": [{"name": "Jordan Lee", "email": "jordan@example.com"}],
		},
	)

	assert response.status_code == 202
	job_id = response.json()["job_id"]
	certificates = client.get(f"/jobs/{job_id}/certificates").json()
	assert len(certificates) == 1
	assert certificates[0]["status"] == "SUCCESS"
	assert certificates[0]["download_url"] is not None
