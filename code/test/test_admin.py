import pytest


@pytest.mark.parametrize(
    "name, site, country, email, password",
    [
        ("Map My Crop", "mapmycrop.com", "India", "info@mapmycrop.com", "password"),
        ("EOS", "eos.com", "US", "info@eos.com", "password"),
    ],
)
def test_success_create_company(
    client, superadmin, name, site, country, email, password
):
    payload = {
        "name": name,
        "site": site,
        "country": country,
        "email": email,
        "password": password,
    }

    response = client.post(
        f"/admin/company?api_key={superadmin.apikey}",
        json=payload,
    )

    del payload["password"]

    assert response.status_code == 200
    assert response.json().items() >= payload.items()


@pytest.mark.parametrize(
    "name, site, country, email, password, error",
    [
        (
            "Map My Crop",
            "mapmycrop.com",
            "India",
            "company@test.com",
            "password",
            "Company with this email already exists",
        ),
        (
            "company",
            "eos.com",
            "US",
            "info@eos.com",
            "password",
            "Company with this name already exists",
        ),
    ],
)
def test_validation_error_create_company(
    client, superadmin, name, site, country, email, password, error
):
    payload = {
        "name": name,
        "site": site,
        "country": country,
        "email": email,
        "password": password,
    }

    response = client.post(
        f"/admin/company?api_key={superadmin.apikey}",
        json=payload,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == error
