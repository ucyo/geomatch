#!/usr/bin/env python
# coding: utf-8

import numpy as np
from numba import jit, prange


@jit(nopython=True)
def jit_haversine(lat1, lon1, lat2, lon2):
    R = 6371  # earth radius in km
    φ1 = lat1 * np.pi / 180
    φ2 = lat2 * np.pi / 180
    Δφ = (lat2 - lat1) * np.pi / 180
    Δλ = (lon2 - lon1) * np.pi / 180

    a = np.math.sin(Δφ / 2) * np.math.sin(Δφ / 2) + np.math.cos(φ1) * np.math.cos(
        φ2
    ) * np.math.sin(Δλ / 2) * np.math.sin(Δλ / 2)

    c = 2 * np.math.atan2(np.math.sqrt(a), np.math.sqrt(1 - a))

    return R * c


@jit(nopython=True, parallel=True)
def jit_haversine_arr_par(arr_lats, arr_lons, lat, lon, distance):
    result = np.full(arr_lats.size, False)
    for i in prange(0, arr_lats.size):
        result[i] = jit_haversine(arr_lats[i], arr_lons[i], lat, lon) <= distance
    return result
