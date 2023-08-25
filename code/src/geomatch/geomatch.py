#!/usr/bin/env python
# coding: utf-8

import json
import os
from datetime import timedelta

from pandas import DataFrame
from pymongo import MongoClient

from . import haversine as hv
from . import mongo as m


def connect():
    """Connect to MongoDB using environment variables."""
    USERNAME = os.getenv("MONGO_USERNAME")
    PASSWORD = os.getenv("MONGO_PASSWORD")
    HOST = os.getenv("MONGO_HOST")
    PORT = os.getenv("MONGO_PORT")
    PATH = os.getenv("MONGO_PATH")

    link = f"mongodb://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{PATH}"
    return MongoClient(link)


def _query_result_to_gdb(cursor, index="time"):
    """Private function to parse MongoDB query results to GeoDataFrames."""

    def _single_entry(entry):
        result = {k: entry[k] for k in ["time", "id", "_id"]}
        result["lat"] = entry["loc"]["coordinates"][1]
        result["lon"] = entry["loc"]["coordinates"][0]
        result["timestamp"] = result["time"]
        return result

    entries = [_single_entry(x) for x in cursor]
    if not entries:
        return None
    df = DataFrame(entries).set_index(index)
    df = df.sort_index()
    return df


# TODO: Unify next two calls
def get_tropomi(client, query=None, index="time"):
    """Get all of the TROPOMI data from the client."""
    cursor = client["TROPOMI"].v0.find(query)
    gdf = _query_result_to_gdb(cursor, index)
    return gdf


def get_iasi(client, query=None, index="time"):
    """Get all of the IASI data from the client."""
    cursor = client["IASI"].v0.find(query)
    gdf = _query_result_to_gdb(cursor, index)
    return gdf


def temporal_boundaries(center, delta, window_center=True):
    """Calculate the temporal boundaries (+- delta/2)."""
    window = delta / 2 if window_center else delta
    tmin = center.name - window
    tmax = center.name + window
    return (tmin, tmax)


def filter_by_distance(center, candidate_list, distance_km):
    """Return only the candidates within a certain distance."""
    lat = center.lat
    lon = center.lon
    lats = candidate_list.lat.values
    lons = candidate_list.lon.values
    mask = hv.haversine_par(lats, lons, lat, lon, distance_km)
    result = candidate_list[mask]
    return result


def filter_by_time(center, candidate_list, delta):
    """Return only the candidates within a certain time window."""
    tmin, tmax = temporal_boundaries(center, delta)

    mask = candidate_list["timestamp"].between(tmin, tmax)
    result = candidate_list[mask]
    return result


def to_json(fname, obj):
    """Output object to json file."""
    with open(fname, "w") as f:
        json.dump(obj, f)


def main(distance_km, delta, ix, tropomi_in_iasi: bool, query=None):
    """Example application of this module."""
    print("Loading data")
    client = connect()
    if tropomi_in_iasi:
        source = get_tropomi(client, query=query)  # size: 155.654
        candidates = get_iasi(client)  # size: 657.417
        searchspace = "IASI"
    else:
        candidates = get_tropomi(client, query=query)  # size: 155.654
        source = get_iasi(client)  # size: 657.417
        searchspace = "TROPOMI"

    center = source.iloc[ix]
    print("Apply time constraints")
    filtered_t = filter_by_time(center, candidates, delta)
    print("Apply spatial constraints")
    filter_fin = filter_by_distance(center, filtered_t, distance_km)
    print(f"There are {filter_fin.index.size} matches for {center._id}")

    res = m.mongo_query(client, center, distance_km, delta, searchspace)
    length = 0 if res is None else res.index.size
    print(f"Mongo: There are {length} matches for {center._id}")


if __name__ == "__main__":
    distance_km = 160.934
    delta = timedelta(hours=6)
    ix = 0
    main(distance_km, delta, ix)
