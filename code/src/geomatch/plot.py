#!/usr/bin/env python
# coding: utf-8

from datetime import timedelta

import folium

from . import geomatch as gm
from . import mongo as m


def generate_map(lat, lon, tiles="Stamen Terrain", zoom_start=5):
    """Create a Folium map for visualisation."""
    return folium.Map(location=[lat, lon], tiles=tiles, zoom_start=zoom_start)


def add_center_marker(m, center, color="darkred", icon="info-sign"):
    """Add center data point to Folium Map (m)."""
    folium.Marker(
        location=[center.lat, center.lon],
        popup=center.name,
        color=color,
        icon=folium.Icon(color=color, icon=icon),
    ).add_to(m)
    return m


def add_center_radius(m, center, distance_km):
    """Add distance threshold to Folium Map (m)."""
    folium.Circle(
        radius=distance_km * 1000,
        location=[center.lat, center.lon],
        popup="TROPOMI Center",
        color="crimson",
        fill=False,
    ).add_to(m)
    return m


def add_geomatch_results(m, center, results):
    """Add Geomatch results to Folium Map (m)."""
    for i, res in results.iterrows():
        time_diff = (center.name - i).total_seconds() / 60
        sign = "+" if time_diff >= 0 else "-"
        folium.Circle(
            radius=5000,
            location=[res.lat, res.lon],
            popup="{}{:.2f} Min.".format(sign, abs(time_diff)),
            color="red",
            fill=True,
        ).add_to(m)
    return m


def add_mongo_results(m, results):
    """Add MongoDB results to Folium Map (m)."""
    for i, res in results.iterrows():
        folium.Circle(
            radius=5000,
            location=[res.lat, res.lon],
            popup="Time: {} <br>Lat: {:.2f}<br>Lon: {:.2f}".format(i, res.lat, res.lon),
            color="green",
            fill=False,
        ).add_to(m)
    return m


def map_results(
    center,
    distance_km,
    result_geomatch,
    result_mongo=None,
    tiles="Stamen Terrain",
    zoom_start=5,
):
    """Create plot for a single data point from TROPOMI (m)."""

    m = generate_map(center.lat, center.lon, tiles, zoom_start)

    m = add_center_radius(m, center, distance_km)

    m = add_center_marker(m, center)

    m = add_geomatch_results(m, center, result_geomatch)

    if result_mongo is not None:
        m = add_mongo_results(m, result_mongo)

    return m


def main(distance_km, delta, ix, tropomi_in_iasi: bool, query=None, save=None):
    """Example application of the methods defined in this module."""
    print("Loading data")
    client = gm.connect()
    if tropomi_in_iasi:
        source = gm.get_tropomi(client, query=query)  # size: 155.654
        candidates = gm.get_iasi(client)  # size: 657.417
        searchspace = "IASI"
    else:
        candidates = gm.get_tropomi(client, query=query)  # size: 155.654
        source = gm.get_iasi(client)  # size: 657.417
        searchspace = "TROPOMI"

    center = source.iloc[ix]
    print("Apply time constraints")
    filtered_t = gm.filter_by_time(center, candidates, delta)
    print("Apply spatial constraints")
    result_geomatch = gm.filter_by_distance(center, filtered_t, distance_km)
    print(f"There are {result_geomatch.index.size} matches for {center._id}")

    res = m.mongo_query(client, center, distance_km, delta, searchspace)
    length = 0 if res is None else res.index.size
    print(f"Mongo: There are {length} matches for {center._id}")

    if length >= 0:
        plot = map_results(center, distance_km, result_geomatch, res)

        if save is not None:
            plot.save(save)
            print(f"Plot is saved to: {save}.")
        else:
            plot.show_in_browser()


if __name__ == "__main__":
    distance_km = 160.934
    delta = timedelta(hours=6)
    ix = 0
    tropomi_in_iasi = True
    main(distance_km, delta, ix, tropomi_in_iasi)
