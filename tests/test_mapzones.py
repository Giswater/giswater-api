"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import pytest

from tests.helpers import assert_healthy


# ---------------------------------------------------------------------------
# DMAs (no marker -- run for all schemas)
# ---------------------------------------------------------------------------


def test_get_dmas(client, default_params):
    assert_healthy(client)

    response = client.get("/om/dmas", params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


@pytest.mark.ws
def test_get_macrodmas(client, default_params):
    assert_healthy(client)

    response = client.get("/om/macrodmas", params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


def test_get_dma_hydrometers(client, default_params):
    assert_healthy(client)

    response = client.get("/om/dmas/1/hydrometers", params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


def test_get_dma_parameters(client, default_params):
    assert_healthy(client)

    response = client.get("/om/dmas/1/parameters", params=default_params)

    assert response.status_code == 200


def test_get_dma_connecs(client, default_params):
    assert_healthy(client)

    response = client.get("/om/dmas/1/connecs", params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


# ---------------------------------------------------------------------------
# Sectors (no marker -- run for all schemas)
# ---------------------------------------------------------------------------


def test_get_macrosectors(client, default_params):
    assert_healthy(client)

    response = client.get("/om/macrosectors", params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


def test_get_sectors(client, default_params):
    assert_healthy(client)

    response = client.get("/om/sectors", params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


# ---------------------------------------------------------------------------
# Presszones (@pytest.mark.ws)
# ---------------------------------------------------------------------------


@pytest.mark.ws
def test_get_presszones(client, default_params):
    assert_healthy(client)

    response = client.get("/om/presszones", params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


# ---------------------------------------------------------------------------
# DQAs (@pytest.mark.ws)
# ---------------------------------------------------------------------------


@pytest.mark.ws
def test_get_macrodqas(client, default_params):
    assert_healthy(client)

    response = client.get("/om/macrodqas", params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


@pytest.mark.ws
def test_get_dqas(client, default_params):
    assert_healthy(client)

    response = client.get("/om/dqas", params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


# ---------------------------------------------------------------------------
# OM Zones (no marker -- run for all schemas)
# ---------------------------------------------------------------------------


def test_get_macroomzones(client, default_params):
    assert_healthy(client)

    response = client.get("/om/macroomzones", params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


def test_get_omzones(client, default_params):
    assert_healthy(client)

    response = client.get("/om/omzones", params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


# ---------------------------------------------------------------------------
# OM Units (@pytest.mark.ud)
# ---------------------------------------------------------------------------


@pytest.mark.ud
def test_get_omunits(client, default_params):
    assert_healthy(client)

    response = client.get("/om/omunits", params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data
