"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import json
import warnings

import pytest

from tests.helpers import assert_healthy


@pytest.mark.ws
def test_get_object_optimal_path_order(client, default_params):
    assert_healthy(client)

    response = client.get(
        "/routing/getobjectoptimalpathorder",
        params={
            **default_params,
            "objectType": "HYDRANT",
            "mapzoneType": "EXPLOITATION",
            "mapzoneId": 1,
            "initialPoint": json.dumps({"x": 419436.50, "y": 4576993.97, "epsg": 25831}),
            "transportMode": "auto",
            "units": "kilometers",
            "language": "en-US",
        },
    )

    if response.status_code == 500 and "Valhalla" in response.text:
        warnings.warn("Valhalla API not available, skipping assertion", stacklevel=2)
        return

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


@pytest.mark.ws
def test_get_object_parameter_order(client, default_params):
    assert_healthy(client)

    response = client.get(
        "/routing/getobjectparameterorder",
        params={
            **default_params,
            "objectType": "HYDRANT",
            "mapzoneType": "EXPLOITATION",
            "mapzoneId": 1,
            "parameter": "node_id",
            "order": "asc",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data
