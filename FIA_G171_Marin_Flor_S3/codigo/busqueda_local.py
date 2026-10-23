#!/usr/bin/env python3
"""
Algoritmos de búsqueda local: Hill Climbing y Simulated Annealing
aplicados al TSP (problema del viajante de comercio).
"""
from __future__ import annotations

import math
import random
from typing import Callable, List, Tuple

from problema_tsp import N, longitud_ruta


def generar_vecino_intercambio(ruta: List[int], rng: random.Random) -> List[int]:
    """Operador de vecindad: intercambio (swap) de dos paradas."""
    cand = list(ruta)
    i, j = sorted(rng.sample(range(1, N), 2))
    cand[i], cand[j] = cand[j], cand[i]
    return cand


def generar_vecino_inversion(ruta: List[int], rng: random.Random) -> List[int]:
    """Operador de vecindad: inversión (2-opt) de un segmento."""
    cand = list(ruta)
    i, j = sorted(rng.sample(range(1, N), 2))
    if i == j:
        return cand
    cand[i:j + 1] = cand[i:j + 1][::-1]
    return cand


def hill_climbing(
    ruta_inicial: List[int],
    rng: random.Random,
    max_iter: int = 10000,
    estrategia: str = "mejor_vecino",
) -> Tuple[List[int], float, List[float], int]:
    """
    Hill Climbing con estrategia 'mejor vecino' (steepest ascent).
    Explora intercambios y 2-opt, acepta únicamente mejoras.
    """
    ruta = list(ruta_inicial)
    actual = longitud_ruta(ruta)
    hist = [actual]
    evals = 0
    sin_mejora = 0
    max_sin_mejora = 150

    for _ in range(max_iter):
        mejor_ruta, mejor_c = None, actual
        # Explorar operadores de vecindad
        for i in range(1, N - 1):
            for j in range(i + 1, N):
                cand = ruta[:i] + ruta[i:j + 1][::-1] + ruta[j + 1:]
                c = longitud_ruta(cand)
                evals += 1
                if c < mejor_c - 1e-12:
                    mejor_c, mejor_ruta = c, cand

        for i in range(1, N - 1):
            for j in range(i + 1, N):
                cand = list(ruta)
                cand[i], cand[j] = cand[j], cand[i]
                c = longitud_ruta(cand)
                evals += 1
                if c < mejor_c - 1e-12:
                    mejor_c, mejor_ruta = c, cand

        if mejor_ruta is None or mejor_c >= actual - 1e-12:
            sin_mejora += 1
            if sin_mejora >= max_sin_mejora:
                break
            continue

        sin_mejora = 0
        ruta, actual = mejor_ruta, mejor_c
        hist.append(actual)

    return ruta, actual, hist, evals


def simulated_annealing(
    ruta_inicial: List[int],
    rng: random.Random,
    T0: float = 12.0,
    Tf: float = 0.001,
    alpha: float = 0.995,
    iter_por_T: int = 80,
) -> Tuple[List[int], float, List[float], int]:
    """
    Simulated Annealing.
    Acepta mejoras siempre y empeoramientos con probabilidad exp(-ΔE/T).
    """
    ruta = list(ruta_inicial)
    actual = longitud_ruta(ruta)
    mejor, mejor_c = list(ruta), actual
    hist = [mejor_c]
    evals = 0
    T = T0

    while T > Tf:
        for _ in range(iter_por_T):
            if rng.random() < 0.5:
                cand = generar_vecino_intercambio(ruta, rng)
            else:
                cand = generar_vecino_inversion(ruta, rng)
            c = longitud_ruta(cand)
            evals += 1
            delta = c - actual
            if delta < 0.0 or rng.random() < math.exp(-delta / T):
                ruta, actual = cand, c
                if c < mejor_c - 1e-12:
                    mejor, mejor_c = list(cand), c
            hist.append(mejor_c)
        T *= alpha

    return mejor, mejor_c, hist, evals
