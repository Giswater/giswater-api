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


@pytest.mark.parametrize(
    ("feature_type", "action", "last_feeding"),
    [
        ("FEATURE", "INSERT", "2020-01-01"),
        ("ARC", "INSERT", "2021-01-01"),
        ("NODE", "INSERT", "2022-01-01"),
        ("CONNEC", "INSERT", "2023-01-01"),
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


def test_get_features_from_polygon(client, default_params):
    assert_healthy(client)

    polygon = (
        "MULTIPOLYGON (((419023.56746357883 4576663.176018708, "
        "419062.1908605342 4576737.759130071, "
        "419101.1472178081 4576736.760249115, "
        "419143.10021794925 4576649.857605965, "
        "419128.1170036131 4576618.2263757, "
        "419025.23226517177 4576637.205113859, "
        "419023.56746357883 4576663.176018708)))"
    )

    response = client.get(
        "/basic/getfeaturesfrompolygon",
        params={
            **default_params,
            "featureType": "NODE",
            "polygonGeom": polygon,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


@pytest.mark.skip(reason="getselectors DB function needs refactoring")
def test_get_selectors(client, default_params):
    assert_healthy(client)

    response = client.get(
        "/basic/getselectors",
        params={
            **default_params,
            "selectorType": "selector_basic",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


def test_get_search(client, default_params):
    assert_healthy(client)

    response = client.get(
        "/basic/getsearch",
        params={
            **default_params,
            "searchText": "test",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


def test_get_arc_audit_values(client, default_params):
    assert_healthy(client)

    response = client.get(
        "/basic/getarcauditvalues",
        params={
            **default_params,
            "startDate": "2020-01-01",
            "endDate": "2026-01-31",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


@pytest.mark.skip(reason="getlist DB function needs refactoring")
def test_get_list(client, default_params):
    assert_healthy(client)

    response = client.get(
        "/basic/getlist",
        params={
            **default_params,
            "tableName": "ve_arc_pipe",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data
