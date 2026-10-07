def test_create_job_and_track_progress(client):
	response = client.post(
		"/jobs",
		json={
			"event_name": "First Aid Training",
			"event_date": "2026-10-07",
			"recipients": [
				{"name": "Alex Rivera", "email": "alex@example.com"},
				{"name": "Sam Chen", "email": "sam@example.com"},
			],
		},
	)

	assert response.status_code == 202
	created = response.json()
	assert created["total_count"] == 2
	assert created["status"] == "PENDING"

	status_response = client.get(f"/jobs/{created['job_id']}")
	assert status_response.status_code == 200
	job = status_response.json()
	assert job["status"] == "COMPLETED"
	assert job["processed_count"] == 2
	assert job["success_count"] == 2
	assert job["failure_count"] == 0
