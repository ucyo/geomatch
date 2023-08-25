#!/usr/bin/env python
# coding: utf-8

import concurrent.futures
import time
from datetime import timedelta

from geomatch import geomatch as gm


def parallel_process(tropomi, iasi, distance_km, delta, output=None):
    """Return all data within temporal and spatial distance with a ProcessPool."""
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {}
        result = dict(
            distance=f"{distance_km} km",
            delta=f"{delta.total_seconds()/60} min",
            matches=[],
        )
        for k, center in tropomi.iterrows():
            filtered = gm.filter_by_distance(center, iasi, distance_km)
            key = executor.submit(gm.filter_by_time, center, filtered, delta)
            futures[key] = center["_id"]

        for future in concurrent.futures.as_completed(futures):
            tropomi_id = futures[future]
            try:
                data = future.result()
            except Exception as exc:
                print("%r generated an exception: %s" % (tropomi_id, exc))
            else:
                print(f"There are {data.index.size} matches for {tropomi_id}")
                result["matches"].append({str(tropomi_id): [str(x) for x in data._id]})
        if output is not None:
            gm.to_json(output, result)


def parallel_thread(tropomi, iasi, distance_km, delta, output=None):
    """Return all data within temporal and spatial distance with a ThreadPool."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {}
        result = dict(
            distance=f"{distance_km} km",
            delta=f"{delta.total_seconds()/60} min",
            matches=[],
        )
        for k, center in tropomi.iterrows():
            filtered = gm.filter_by_distance(center, iasi, distance_km)
            key = executor.submit(gm.filter_by_time, center, filtered, delta)
            futures[key] = center["_id"]

        for future in concurrent.futures.as_completed(futures):
            tropomi_id = futures[future]
            try:
                data = future.result()
            except Exception as exc:
                print("%r generated an exception: %s" % (tropomi_id, exc))
            else:
                print(f"There are {data.index.size} matches for {tropomi_id}")
                result["matches"].append({str(tropomi_id): [str(x) for x in data._id]})
        if output is not None:
            gm.to_json(output, result)


def main(distance_km, delta, percentage, output, tropomi_in_iasi: bool):
    """Example application of the methods in this module."""
    print("Loading data")
    client = gm.connect()
    if tropomi_in_iasi:
        source = gm.get_tropomi(client)
        candidates = gm.get_iasi(client)
    else:
        candidates = gm.get_tropomi(client)
        source = gm.get_iasi(client)

    n = int(source.index.size * percentage)
    print(f"Processing {n} data")

    tic = time.perf_counter()
    parallel_thread(source[:n], candidates, distance_km, delta, output)
    toc = time.perf_counter()

    print(f"Calculation was done in {toc - tic:0.4f} seconds")


if __name__ == "__main__":
    distance_km = 160.934
    delta = timedelta(hours=6)
    percentage = 0.01
    output = None
    tropomi_in_iasi = True
    main(distance_km, delta, percentage, output, tropomi_in_iasi)
