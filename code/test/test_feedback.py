import pytest


@pytest.mark.parametrize("feedback", [("This is feedback from customers")])
def test_success_create_feedback(client, farmer, feedback):

    payload = {"feedback": feedback}

    response = client.post(
        f"/feedback?api_key={farmer.apikey}",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json().items() >= payload.items()


@pytest.mark.parametrize("feedback", [("")])
def test_validation_create_feedback(client, farmer, feedback):

    payload = {"feedback": feedback}

    response = client.post(
        f"/feedback?api_key={farmer.apikey}",
        json=payload,
    )

    assert response.status_code == 403


def test_success_index_feedback(client, superadmin):

    response = client.get(f"/feedback?api_key={superadmin.apikey}")

    assert response.status_code == 200


def test_invalid_permission_index_feedback(client, farmer):
    response = client.get(f"/feedback?api_key={farmer.apikey}")

    assert response.status_code == 404
