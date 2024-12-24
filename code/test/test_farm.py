import pytest


@pytest.mark.parametrize("name", [("another name")])
def test_success_update_farm(client, farm, farmer, name):

    payload = {"name": name}

    response = client.put(
        f"/farm/{farm.id}?api_key={farmer.apikey}",
        json=payload,
    )

    assert response.status_code == 200
