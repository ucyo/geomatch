#!/usr/bin/env python
# coding: utf-8

import concurrent.futures
import time
from datetime import timedelta

import geomatch as gm


def parallel_process(num, distance_radius, delta):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {}
        for k, center in tropomi[:num].iterrows():
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


def parallel_thread(num, distance_radius, delta):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {}
        for k, center in tropomi[:num].iterrows():
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


if __name__ == "__main__":
    print("Loading data")
    client = gm.connect()
    tropomi = gm.get_tropomi(client)
    iasi = gm.get_iasi(client)

    distance_threshold_km = 160.934
    # distance_threshold_m = 10000
    delta = timedelta(hours=6)
    # delta = timedelta(minutes=6)
    # n = 10
    n = int(tropomi.index.size * 0.01)

    print(f"Processing {n} data")

    tic = time.perf_counter()
    parallel_thread(n, distance_threshold_km, delta)
    toc = time.perf_counter()

    print(f"Calculation was done in {toc - tic:0.4f} seconds")
    # parallel_process(n, distance_threshold_m, delta)
