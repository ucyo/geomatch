#!/usr/bin/env python
# coding: utf-8

import concurrent.futures
import time
from datetime import timedelta

from geomatch import geomatch as gm


def parallel_process(tropomi, iasi, distance_radius, delta):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {}
        for k, center in tropomi.iterrows():
            filtered_t = gm.filter_by_distance(center, iasi, distance_radius)
            key = executor.submit(
                gm.filter_candidates_by_time, center, filtered_t, delta
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


def parallel_thread(tropomi, iasi, distance_radius, delta):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {}
        for k, center in tropomi.iterrows():
            filtered_t = gm.filter_by_distance(center, iasi, distance_radius)
            key = executor.submit(
                gm.filter_candidates_by_time, center, filtered_t, delta
            )
            # filtered_t = gm.filter_candidates_by_time(center, iasi, delta)
            # key = executor.submit(gm.filter_by_distance,
            #                       center, filtered_t, distance_threshold_m)
            futures[key] = center["_id"]

        for future in concurrent.futures.as_completed(futures):
            tropomi_id = futures[future]
            try:
                data = future.result()
            except Exception as exc:
                print("%r generated an exception: %s" % (tropomi_id, exc))
            else:
                print(f"There are {data.index.size} matches for {tropomi_id}")


def main(distance_threshold_km, delta, percentage):
    print("Loading data")
    client = gm.connect()
    tropomi = gm.get_tropomi(client)
    iasi = gm.get_iasi(client)

    n = int(tropomi.index.size * percentage)
    print(f"Processing {n} data")

    tic = time.perf_counter()
    parallel_thread(tropomi[:n], iasi, distance_threshold_km, delta)
    toc = time.perf_counter()

    print(f"Calculation was done in {toc - tic:0.4f} seconds")
    # parallel_process(n, distance_threshold_m, delta)


if __name__ == "__main__":
    distance_threshold_km = 160.934
    delta = timedelta(hours=6)
    percentage = 0.01
    main(distance_threshold_km, delta, percentage)
