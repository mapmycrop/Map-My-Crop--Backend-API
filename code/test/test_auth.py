import pytest


@pytest.mark.parametrize(
    "type, email, phone",
    [
        ("email", "user@test.com", "1234567890"),
        ("phone", "user@test.com", "1234567899"),
    ],
)
def test_validation_422_error_send_otp(client, type, email, phone):
    payload = {}

    if type == "email":
        payload = {"type": type, "phone": phone}

    if type == "phone":
        payload = {"type": type, "email": email}

    response = client.post("/auth/send_otp", json=payload)

    assert response.status_code == 400


@pytest.mark.parametrize(
    "type, email, phone",
    [
        ("email", "user@test.com", "1234567890"),
        ("phone", "user@test.com", "1234567899"),
    ],
)
def test_validation_403_error_send_otp(client, type, email, phone):
    payload = {"type": type, "email": email, "phone": phone}

    response = client.post("/auth/send_otp", json=payload)

    assert response.status_code == 403
