import pytest


def test_success_statistic(client, superadmin, farmer, farm):
    response = client.get(f"/mis/statistic?api_key={superadmin.apikey}")

    assert response.status_code == 200

    data = response.json()

    assert len(data["farmers"]) == 1
    assert len(data["farms"]) == 1


def test_success_global_farm(client, farm, superadmin):
    response = client.get(f"/mis/global-farm?api_key={superadmin.apikey}")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1


@pytest.mark.parametrize("country, state", [("91", ""), ("", "VA"), ("91", "VA")])
def test_success_filter_farm(client, superadmin, farm, country, state):
    response = client.get(
        f"/mis/filter-farm?api_key={superadmin.apikey}&country={country}&state={state}"
    )

    assert response.status_code == 200
    assert response.json() == 1
