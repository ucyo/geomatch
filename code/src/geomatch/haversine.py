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
def jit_haversine_arr_par(a1, a2, lat, lon, distance):
    result = np.full(a1.size, False)
    for i in prange(0, a1.size):
        result[i] = jit_haversine(a1[i], a2[i], lat, lon) <= distance
    return result
