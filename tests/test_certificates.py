def test_list_and_download_generated_certificate(client):
	response = client.post(
		"/jobs",
		json={
			"event_name": "Safety Course",
			"event_date": "2026-10-07",
			"recipients": [{"name": "Avery Kim", "email": "avery@example.com"}],
		},
	)

	job_id = response.json()["job_id"]
	certificate = client.get(f"/jobs/{job_id}/certificates").json()[0]
	download = client.get(certificate["download_url"])

	assert download.status_code == 200
	assert download.headers["content-type"] == "application/pdf"
	assert download.content.startswith(b"%PDF-")


def test_missing_certificate_returns_not_found(client):
	response = client.get("/certificates/999999/download")

	assert response.status_code == 404
