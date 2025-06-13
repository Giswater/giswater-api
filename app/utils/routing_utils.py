import json
import requests
from urllib.parse import quote


def decode(encoded):
    """
    Decode Valhalla encoded polyline shape
    https://valhalla.github.io/valhalla/decoding/#python
    """
    inv = 1.0 / 1e6
    decoded = []
    previous = [0, 0]
    i = 0
    while i < len(encoded):
        ll = [0, 0]
        for j in [0, 1]:
            shift = 0
            byte = 0x20
            while byte >= 0x20:
                byte = ord(encoded[i]) - 63
                i += 1
                ll[j] |= (byte & 0x1f) << shift
                shift += 5
            ll[j] = previous[j] + (~(ll[j] >> 1) if ll[j] & 1 else (ll[j] >> 1))
            previous[j] = ll[j]
        decoded.append([float('%.6f' % (ll[1] * inv)), float('%.6f' % (ll[0] * inv))])
    return decoded


def get_geojson_from_route(route, mode):
    """
    Get the geojson from the route
    """

    geojson_feature = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": route
        },
        "properties": {
            "mode": mode
        }
    }

    return {
        "type": "FeatureCollection",
        "features": [geojson_feature]
    }

def get_valhalla_route(input_parameters):
    """
    Get the route from Valhalla API
    """
    base_url = "https://valhalla1.openstreetmap.de/route"
    json_string = json.dumps(input_parameters).replace(' ', '')
    encoded_json = quote(json_string, safe='[],:')
    url = f"{base_url}?json={encoded_json}"
    response = requests.get(url)
    if response.status_code != 200:
        return response, {}
    response_json = response.json()

    # Decode the path
    try:
        path = decode(response_json.get("trip").get("legs")[0].get("shape"))
        return response_json, path
    except Exception:
        return response_json, {}
