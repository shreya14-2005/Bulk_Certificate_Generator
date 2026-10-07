import pytest


@pytest.mark.parametrize(
	"recipient",
	[
		{"name": "   ", "email": "valid@example.com"},
		{"name": "Taylor", "email": "not-an-email"},
	],
)
def test_invalid_recipient_is_rejected(client, recipient):
	response = client.post(
		"/jobs",
		json={
			"event_name": "Workshop",
			"event_date": "2026-10-07",
			"recipients": [recipient],
		},
	)

	assert response.status_code == 422


def test_empty_recipient_list_is_rejected(client):
	response = client.post(
		"/jobs",
		json={
			"event_name": "Workshop",
			"event_date": "2026-10-07",
			"recipients": [],
		},
	)

	assert response.status_code == 422
