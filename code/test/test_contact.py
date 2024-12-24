import pytest


@pytest.mark.parametrize(
    "title, message, source",
    [
        ("Help me", "For agriculture", "Web"),
        ("Help me", "For agriculture", "Mobile"),
    ],
)
def test_success_contact(client, farmer, title, message, source):
    payload = {"title": title, "message": message, "source": source}

    response = client.post(
        f"/contact?api_key={farmer.apikey}",
        json=payload,
    )

    assert response.status_code == 201


@pytest.mark.parametrize(
    "title, message, source",
    [
        ("Help me", "For agriculture", "Desktop"),
        ("", "For agriculture", "Web"),
        ("Help me", "", "Web"),
    ],
)
def test_validation_error_contact(client, superadmin, title, message, source):
    payload = {"title": title, "message": message, "source": source}

    response = client.post(
        f"/contact?api_key={superadmin.apikey}",
        json=payload,
    )

    assert response.status_code == 422
