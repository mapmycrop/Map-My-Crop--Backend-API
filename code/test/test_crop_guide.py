import pytest


@pytest.mark.parametrize(
    "name, link, image_url",
    [
        (
            "Aswagantha",
            "https://www.mapmycrop.com/mint-crop-guideindia-2/",
            "https://crop-guides-app.s3.ap-south-1.amazonaws.com/Withania-Somnifera.jpg",
        )
    ],
)
def test_success_create_crop_guide(client, superadmin, name, link, image_url):

    payload = {"name": name, "link": link, "image_url": image_url}

    response = client.post(
        f"/crop_guide?api_key={superadmin.apikey}",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json().items() >= payload.items()


@pytest.mark.parametrize(
    "name, link, image_url",
    [
        (
            "Aswagantha",
            "https://www.mapmycrop.com/mint-crop-guideindia-2/",
            "https://crop-guides-app.s3.ap-south-1.amazonaws.com/Withania-Somnifera.jpg",
        )
    ],
)
def test_invalid_permission_create_crop_guide(client, farmer, name, link, image_url):

    payload = {"name": name, "link": link, "image_url": image_url}

    response = client.post(
        f"/crop_guide?api_key={farmer.apikey}",
        json=payload,
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "name, link, image_url",
    [
        (
            "",
            "https://www.mapmycrop.com/mint-crop-guideindia-2/",
            "https://crop-guides-app.s3.ap-south-1.amazonaws.com/Withania-Somnifera.jpg",
        ),
        (
            "Aswagantha",
            "",
            "https://crop-guides-app.s3.ap-south-1.amazonaws.com/Withania-Somnifera.jpg",
        ),
        ("Aswagantha", "https://www.mapmycrop.com/mint-crop-guideindia-2/", ""),
    ],
)
def test_validation_create_crop_guide(client, superadmin, name, link, image_url):

    payload = {"name": name, "link": link, "image_url": image_url}

    response = client.post(
        f"/crop_guide?api_key={superadmin.apikey}",
        json=payload,
    )

    assert response.status_code == 422


def test_success_index_crop_guide(client, farmer):

    response = client.get(f"/crop_guide?api_key={farmer.apikey}")

    assert response.status_code == 200
