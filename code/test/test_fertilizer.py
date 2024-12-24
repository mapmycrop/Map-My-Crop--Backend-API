import pytest


def test_success_fertilizer(client, farmer, farm, fertilizer, farm_crop):

    response = client.get(
        f"/fertilizer?api_key={farmer.apikey}&farm_id={farm.id}",
    )

    area = farm.area

    assert response.status_code == 200
    assert (
        response.json().items()
        > (
            {
                "urea": round(fertilizer.urea * area, 2),
                "ssp": round(fertilizer.ssp * area, 2),
                "mop": round(fertilizer.mop * area, 2),
                "dap": round(fertilizer.dap * area, 2),
            }
        ).items()
    )
