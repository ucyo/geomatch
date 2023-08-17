#!/usr/bin/env python
# coding: utf-8

import concurrent.futures
import time
from datetime import timedelta

from geomatch import geomatch as gm


def create_query(center, distance_km, delta):
    lo = center.name - delta
    up = center.name + delta
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
            {"time": {"$gte": lo, "$lte": up}},
        ]
    }
    return result


def parallel_mongo(client, tropomi, distance_km, delta, rparams=None):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {}
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
                print(f"There are {data.index.size} matches for {tropomi_id}")


def mongo_query(client, center, distance_km, delta, rparams=None):
    multiparam = create_query(center, distance_km, delta)
    result = client["IASI"].v0.find(multiparam, rparams)
    return gm._query_result_to_gdb(result)


def main(distance_km, delta, percentage):
    print("Loading data")
    client = gm.connect()
    tropomi = gm.get_tropomi(client)

    delta = timedelta(hours=4)
    distance_km = 160.934
    n = int(tropomi.index.size * percentage)

    print(f"Running {n} queries")
    tic = time.perf_counter()
    parallel_mongo(client, tropomi[:n], distance_km, delta)
    toc = time.perf_counter()

    print(f"Calculation was done in {toc - tic:0.4f} seconds")


if __name__ == "__main__":
    distance_km = 160.934
    delta = timedelta(hours=6)
    percentage = 0.01
    main(distance_km, delta, percentage)
