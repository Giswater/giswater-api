"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import pytest
from tests.helpers import assert_healthy


@pytest.mark.ws
@pytest.mark.parametrize(
    ("xcoord", "ycoord", "zoom_ratio"),
    [
        (419487.25, 4576484.26, 1000),
        (418954.621, 4576573.944, 1000),
        (418294.927, 4577779.925, 1000),
    ],
)
def test_get_info_from_coordinates_ws(client, default_params, xcoord: float, ycoord: float, zoom_ratio: int):
    assert_healthy(client)

    response = client.get(
        "/basic/getinfofromcoordinates",
        params={
            **default_params,
            "xcoord": xcoord,
            "ycoord": ycoord,
            "epsg": 25831,
            "zoomRatio": zoom_ratio,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "version" in data
    assert "body" in data


@pytest.mark.ud
@pytest.mark.parametrize(
    ("xcoord", "ycoord", "zoom_ratio"),
    [
        (419433.85, 4576570.45, 1000),
        (419236.08, 4576621.77, 1000),
        (418308.548, 4577923.667, 1000),
    ],
)
def test_get_info_from_coordinates_ud(client, default_params, xcoord: float, ycoord: float, zoom_ratio: int):
    assert_healthy(client)

    response = client.get(
        "/basic/getinfofromcoordinates",
        params={
            **default_params,
            "xcoord": xcoord,
            "ycoord": ycoord,
            "epsg": 25831,
            "zoomRatio": zoom_ratio,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "version" in data
    assert "body" in data


@pytest.mark.ws
@pytest.mark.ud
@pytest.mark.parametrize(
    ("feature_type", "action", "last_feeding"),
    [
        ("FEATURE", "INSERT", "2020-01-01"),
        ("ARC", "INSERT", "2021-01-01"),
        ("NODE", "INSERT", "2022-01-01"),
        ("CONNEC", "INSERT", "2023-01-01"),
        ("GULLY", "INSERT", "2024-01-01"),
        ("ELEMENT", "INSERT", "2025-01-01"),
    ],
)
def test_get_feature_changes(client, default_params, feature_type, action, last_feeding):
    assert_healthy(client)

    response = client.get(
        "/basic/getfeaturechanges",
        params={
            **default_params,
            "featureType": feature_type,
            "action": action,
            "lastFeeding": last_feeding,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "version" in data
    assert "body" in data
    assert "data" in data["body"]
    assert "features" in data["body"]["data"]
