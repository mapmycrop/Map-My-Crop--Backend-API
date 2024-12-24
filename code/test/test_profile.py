import pytest


# @pytest.mark.parametrize(
#     "email, ph", [("update@mmc.com", "1234567890"), (None, "1234567890")]
# )
# def test_success_update_user(client, farmer, email, ph):
#     payload = {"email": email, "ph": ph}

#     response = client.put(f"/profile?api_key={farmer.apikey}", json=payload)

#     assert response.status_code == 200


# @pytest.mark.parametrize("email, ph", [("update@mmc.com", None)])
# def test_success_update_company(client, company, email, ph):
#     payload = {"email": email, "ph": ph}

#     response = client.put(f"/profile?api_key={company.apikey}", json=payload)

#     assert response.status_code == 200


# @pytest.mark.parametrize("invalid_api_key", [("invaid")])
# def test_validation_api_key_update(client, invalid_api_key):
#     response = client.put(f"/profile?api_key={invalid_api_key}", json={})

#     assert response.status_code == 403


# @pytest.mark.parametrize(
#     "email, ph",
#     [
#         ("update@mmc.com", ""),
#         ("update@mmc.com", "123456"),
#     ],
# )
# def test_validation_update_user(client, farmer, email, ph):
#     payload = {"email": email, "ph": ph}

#     response = client.put(f"/profile?api_key={farmer.apikey}", json=payload)

#     assert response.status_code == 422


# @pytest.mark.parametrize(
#     "email, ph",
#     [
#         ("", None),
#         ("invalid", None),
#     ],
# )
# def test_validation_update_company(client, company, email, ph):
#     payload = {"email": email, "ph": ph}

#     response = client.put(f"/profile?api_key={company.apikey}", json=payload)

#     assert response.status_code == 422


@pytest.mark.parametrize(
    "old_password, new_password, confirm_new_password",
    [("farmerpassword", "newpassword", "newpassword")],
)
def test_success_change_password(
    client, farmer, old_password, new_password, confirm_new_password
):
    payload = {
        "old_password": old_password,
        "new_password": new_password,
        "confirm_new_password": confirm_new_password,
    }

    response = client.put(
        f"/profile/change-password?api_key={farmer.apikey}", json=payload
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "old_password, new_password, confirm_new_password",
    [("", "", ""), ("farmerpassword", "new password", "confirm_password")],
)
def test_validation_change_password(
    client, farmer, old_password, new_password, confirm_new_password
):
    payload = {
        "old_password": old_password,
        "new_password": new_password,
        "confirm_new_password": confirm_new_password,
    }

    response = client.put(
        f"/profile/change-password?api_key={farmer.apikey}", json=payload
    )

    assert response.status_code == 403
