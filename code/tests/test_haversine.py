import json
import math

import pytest

from geomatch.haversine import jit_haversine

# Load city coordinates from cities.json
with open("tests/cities.json", "r") as cities_file:
    cities = json.load(cities_file)

# Load actual distances from distances.json
with open("tests/distances.json", "r") as distances_file:
    actual_distances = json.load(distances_file)

# Tolerance for differences between calculated and actual distances in %
distance_tolerance = 0.1


# Test case: Check calculated distances against actual values
@pytest.mark.parametrize(
    "cities, actual_distances", [(cities, x) for x in actual_distances]
)
def test_haversine_jit(cities, actual_distances):
    from_city = cities[actual_distances["from"]]
    lat1, lon1 = from_city["lat"], from_city["lon"]
    to_city = cities[actual_distances["to"]]
    lat2, lon2 = to_city["lat"], to_city["lon"]
    result = jit_haversine(lat1, lon1, lat2, lon2)
    assert math.isclose(
        result, actual_distances["distance_km"], rel_tol=distance_tolerance
    )

# Test case: Check calculated distances against actual values
@pytest.mark.parametrize("city", cities)
def test_haversine_jit_self(city):
    lat1, lon1 = cities[city]["lat"], cities[city]["lon"]
    lat2, lon2 = cities[city]["lat"], cities[city]["lon"]
    result = jit_haversine(lat1, lon1, lat2, lon2)
    assert math.isclose(result, 0, rel_tol=distance_tolerance)
