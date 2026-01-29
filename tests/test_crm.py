"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from uuid import uuid4

from tests.helpers import assert_healthy


def _new_hydrometer_code() -> str:
    return f"TEST_CRM_{uuid4().hex[:10]}"


def _hydrometer_payload(code: str) -> dict:
    return {"code": code, "hydroNumber": f"HN-{code}"}


def _insert_hydrometers(client, default_params, payload):
    response = client.post("/crm/hydrometers", params=default_params, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    return data


def test_insert_hydrometer_single(client, default_params):
    assert_healthy(client)

    code = _new_hydrometer_code()
    payload = _hydrometer_payload(code)

    response = client.post("/crm/hydrometers", params=default_params, json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "version" in data
    assert "body" in data


def test_insert_hydrometers_bulk(client, default_params):
    assert_healthy(client)

    payload = [_hydrometer_payload(_new_hydrometer_code()) for _ in range(2)]

    response = client.post("/crm/hydrometers", params=default_params, json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "version" in data
    assert "body" in data


def test_update_hydrometer_single(client, default_params):
    assert_healthy(client)

    code = _new_hydrometer_code()
    _insert_hydrometers(client, default_params, _hydrometer_payload(code))

    update_payload = {"code": code, "hydroNumber": f"UPDATED-{code}"}
    response = client.patch(f"/crm/hydrometers/{code}", params=default_params, json=update_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "version" in data
    assert "body" in data


def test_update_hydrometers_bulk(client, default_params):
    assert_healthy(client)

    codes = [_new_hydrometer_code(), _new_hydrometer_code()]
    payload = [_hydrometer_payload(code) for code in codes]
    _insert_hydrometers(client, default_params, payload)

    update_payload = [
        {"code": codes[0], "hydroNumber": f"UPDATED-{codes[0]}"},
        {"code": codes[1], "hydroNumber": f"UPDATED-{codes[1]}"},
    ]
    response = client.patch("/crm/hydrometers", params=default_params, json=update_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "version" in data
    assert "body" in data


def test_delete_hydrometer_single(client, default_params):
    assert_healthy(client)

    code = _new_hydrometer_code()
    _insert_hydrometers(client, default_params, _hydrometer_payload(code))

    response = client.delete(f"/crm/hydrometers/{code}", params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "version" in data
    assert "body" in data


def test_delete_hydrometers_bulk(client, default_params):
    assert_healthy(client)

    codes = [_new_hydrometer_code(), _new_hydrometer_code()]
    payload = [_hydrometer_payload(code) for code in codes]
    _insert_hydrometers(client, default_params, payload)

    response = client.delete("/crm/hydrometers", params=default_params, json=codes)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "version" in data
    assert "body" in data


def test_replace_all_hydrometers(client, default_params):
    assert_healthy(client)

    payload = [_hydrometer_payload(_new_hydrometer_code()) for _ in range(2)]
    response = client.put("/crm/hydrometers", params=default_params, json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "version" in data
    assert "body" in data
