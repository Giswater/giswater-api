import json
import requests
from urllib.parse import quote
from typing import List, Tuple
from ..models.routing.routing_models import Location
from ..utils.utils import create_body_dict, execute_procedure


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


def get_geojson_from_optimized_route(trip_data, mode):
    """
    Get the geojson from an optimized route with multiple legs
    Each leg gets its own feature with different properties and colors
    """
    features = []

    # Define a color palette for different legs
    colors = [
        "#FF0000",  # Red
        "#00FF00",  # Green
        "#0000FF",  # Blue
        "#FFFF00",  # Yellow
        "#FF00FF",  # Magenta
        "#00FFFF",  # Cyan
        "#FFA500",  # Orange
        "#800080",  # Purple
        "#008000",  # Dark Green
        "#000080",  # Navy
        "#800000",  # Maroon
        "#808000",  # Olive
        "#FFC0CB",  # Pink
        "#A52A2A",  # Brown
        "#DDA0DD",  # Plum
    ]

    if not trip_data or "legs" not in trip_data:
        return {
            "type": "FeatureCollection",
            "features": []
        }

    for i, leg in enumerate(trip_data["legs"]):
        try:
            # Decode the shape for this leg
            shape = decode(leg.get("shape", ""))
            if not shape:
                continue

            # Get leg properties
            leg_properties = {
                "mode": mode,
                "leg_index": i,
                "leg_id": f"leg_{i}",
                "distance": leg.get("summary", {}).get("length"),
                "duration": leg.get("summary", {}).get("time"),
                "from_index": leg.get("from_index"),
                "to_index": leg.get("to_index")
            }

            # Add SimpleStyle properties
            color_index = i % len(colors)
            leg_properties.update({
                "stroke": colors[color_index],
                "stroke-width": 3,
                "stroke-opacity": 0.8,
                "fill": colors[color_index],
                "fill-opacity": 0.1,
                "title": f"Leg {i}",
                "description": f"Distance: {leg.get('summary', {}).get('length', 'N/A')} km, Duration: {leg.get('summary', {}).get('time', 'N/A')} s"  # noqa: E501
            })

            # Add any additional leg-specific properties
            if "maneuvers" in leg:
                leg_properties["maneuver_count"] = len(leg["maneuvers"])

            geojson_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": shape
                },
                "properties": leg_properties
            }

            features.append(geojson_feature)

        except Exception as e:
            print(f"Error processing leg {i}: {e}")
            continue

    return {
        "type": "FeatureCollection",
        "features": features
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


def get_valhalla_optimized_route(input_parameters):
    """
    Get the optimized route from Valhalla API
    """
    base_url = "https://valhalla1.openstreetmap.de/optimized_route"
    json_string = json.dumps(input_parameters).replace(' ', '')
    encoded_json = quote(json_string, safe='[],:')
    url = f"{base_url}?json={encoded_json}"
    response = requests.get(url)
    if response.status_code != 200:
        return response, {}
    response_json = response.json()

    # Return the full response and all legs
    try:
        trip_data = response_json.get("trip", {})
        legs = trip_data.get("legs", [])
        return response_json, legs
    except Exception:
        return response_json, {}


def get_maneuvers(valhalla_response):
    """
    Get the maneuvers from the Valhalla response
    """
    maneuvers = []
    for leg in valhalla_response["trip"]["legs"]:
        maneuvers.extend(leg["maneuvers"])

    return maneuvers


def get_network_points(object_type, mapzone_type, mapzone_id, log, schema) -> Tuple[dict, List[Location]]:
    points = []

    # Get the network points from the database
    body = create_body_dict(
        extras={"sysType": object_type, "mapzoneType": mapzone_type, "mapzoneId": mapzone_id}
    )

    result = execute_procedure(log, "gw_fct_getfeatures", body, schema=schema)
    if not result:
        return {}, []

    points_data = result["body"]["data"]["features"]
    for point in points_data:
        point_coordinates = point["coordinates"]
        points.append(Location(x=point_coordinates['x'], y=point_coordinates['y'], epsg=point_coordinates['epsg'], street=None))

    return result, points
