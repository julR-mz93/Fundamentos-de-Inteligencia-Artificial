#!/usr/bin/env python3
"""
Problema: Ruta mínima de reparto (Traveling Salesperson Problem - TSP).

Se trata de encontrar el recorrido que pasa por todas las paradas de entrega
saliendo y volviendo al almacén, minimizando la distancia total recorrida.

Cada solución es un orden de visita (permutación) que comienza y termina
en el almacén (punto 0). La función objetivo a minimizar es la longitud
total del recorrido.
"""
from __future__ import annotations

import math
from typing import List, Tuple

import numpy as np

# Almacén
DEPOT = (5.0, 5.0)

# Puntos de entrega
CLIENTES = [
    (1.0, 9.0), (2.0, 3.0), (8.5, 9.5), (9.5, 6.0), (7.0, 2.0),
    (1.5, 5.5), (3.5, 7.5), (6.5, 8.0), (8.0, 3.5), (4.0, 1.0),
    (2.5, 9.5), (9.0, 8.5), (0.5, 6.5), (5.5, 9.0), (7.5, 6.5),
    (3.0, 4.0), (6.0, 2.5), (8.5, 1.0), (1.0, 1.5), (4.5, 6.5),
]

PUNTOS: List[Tuple[float, float]] = [DEPOT] + CLIENTES
N = len(PUNTOS)

# Matriz de distancias euclídeas
MATRIZ_DIST = np.array([[math.dist(a, b) for b in PUNTOS] for a in PUNTOS])


def longitud_ruta(ruta: List[int]) -> float:
    """Longitud total del recorrido (almacén -> ... -> almacén)."""
    total = 0.0
    for a, b in zip(ruta, ruta[1:]):
        total += MATRIZ_DIST[a, b]
    if ruta:
        total += MATRIZ_DIST[ruta[-1], ruta[0]]
    return float(total)


def ruta_aleatoria(rng) -> List[int]:
    """Genera una ruta aleatoria comenzando en el almacén."""
    cuerpo = list(range(1, N))
    rng.shuffle(cuerpo)
    return [0] + cuerpo


def ruta_inicial_greedy(rng=None) -> List[int]:
    """Heurística del vecino más próximo para obtener una ruta inicial razonable."""
    visitado = {0}
    ruta = [0]
    actual = 0
    while len(visitado) < N:
        mejor, mejor_d = None, float("inf")
        for j in range(1, N):
            if j in visitado:
                continue
            d = MATRIZ_DIST[actual, j]
            if d < mejor_d:
                mejor_d, mejor = d, j
        ruta.append(mejor)
        visitado.add(mejor)
        actual = mejor
    return ruta
