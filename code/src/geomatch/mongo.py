#!/usr/bin/env python
# coding: utf-8

import concurrent.futures
import time
from datetime import timedelta

from geomatch import geomatch as gm


def create_query(center, distance_km, delta):
    """Create a query for MongoDB using a temporal and spatial threshold."""
    tmin, tmax = gm.temporal_boundaries(center=center, delta=delta)
    result = {
        "$and": [
            {
                "loc": {
                    "$geoWithin": {
                        "$centerSphere": [
                            [center.lon, center.lat],
                            distance_km / 6378.1,
                        ]
                    }
                }
            },
            {"time": {"$gte": tmin, "$lte": tmax}},
        ]
    }
    return result


def parallel_mongo(client, tropomi, distance_km, delta, rparams=None, output=None):
    """Return all data within distance and temporal thresholds from MongoDB."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {}
        result = dict(
            distance=f"{distance_km} km",
            delta=f"{delta.total_seconds()/60} min",
            matches=[],
        )
        for k, center in tropomi.iterrows():
            key = executor.submit(
                mongo_query, client, center, distance_km, delta, rparams
            )
            futures[key] = center["_id"]
        for future in concurrent.futures.as_completed(futures):
            tropomi_id = futures[future]
            try:
                data = future.result()
            except Exception as exc:
                print("%r generated an exception: %s" % (tropomi_id, exc))
            else:
                found = [str(x) for x in data._id] if data is not None else []
                print(f"There are {len(found)} matches for {tropomi_id}")
                result["matches"].append({str(tropomi_id): found})
        if output is not None:
            gm.to_json(output, result)


def mongo_query(client, center, distance_km, delta, rparams=None):
    """Return all data within distance and temporal window using MongoDB."""
    multiparam = create_query(center, distance_km, delta)
    result = client["IASI"].v0.find(multiparam, rparams)
    return gm._query_result_to_gdb(result)


def main(distance_km, delta, percentage, output):
    """Example application of the methods in this module."""
    print("Loading data")
    client = gm.connect()
    tropomi = gm.get_tropomi(client)
    n = int(tropomi.index.size * percentage)

    print(f"Running {n} queries")
    tic = time.perf_counter()
    parallel_mongo(client, tropomi[:n], distance_km, delta, output=output)
    toc = time.perf_counter()

    print(f"Calculation was done in {toc - tic:0.4f} seconds")


if __name__ == "__main__":
    distance_km = 160.934
    delta = timedelta(hours=6)
    percentage = 0.01
    output = None
    main(distance_km, delta, percentage, output)
