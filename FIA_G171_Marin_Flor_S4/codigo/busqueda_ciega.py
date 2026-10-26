#!/usr/bin/env python3
"""
Búsqueda ciega (no informada): BFS y DFS.

Ambos algoritmos reciben el laberinto como grafo implícito y devuelven:
  - el camino solución,
  - el número de nodos expandidos,
  - el número de aristas evaluadas,
  - el tamaño máximo de la frontera,
  - el tiempo de ejecución,
  - el orden de expansión (útil para las figuras).

Este módulo NO usa librerías externas: solo la biblioteca estándar.
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from laberinto import INICIO, LABERINTO, META, Posicion, vecinos


@dataclass
class Resultado:
    """Resultado de una ejecución de búsqueda."""

    algoritmo: str
    encontrado: bool
    camino: List[Posicion] = field(default_factory=list)
    expandidos: int = 0
    aristas_evaluadas: int = 0
    frontera_max: int = 0
    tiempo_seg: float = 0.0
    orden_expansion: List[Posicion] = field(default_factory=list)
    historial_frontera: List[int] = field(default_factory=list)

    @property
    def longitud_camino(self) -> int:
        """Número de celdas del camino (incluye inicio y meta)."""
        return len(self.camino)

    @property
    def coste(self) -> int:
        """Número de movimientos del camino (aristas recorridas)."""
        return max(0, len(self.camino) - 1)


def _reconstruir_camino(
    padre: Dict[Posicion, Optional[Posicion]], meta: Posicion
) -> List[Posicion]:
    """Reconstruye el camino desde el inicio hasta la meta usando el árbol de padres."""
    if meta not in padre:
        return []
    camino: List[Posicion] = []
    actual: Optional[Posicion] = meta
    while actual is not None:
        camino.append(actual)
        actual = padre[actual]
    camino.reverse()
    return camino


def bfs(
    inicio: Posicion = INICIO,
    meta: Posicion = META,
) -> Resultado:
    """
    Búsqueda en amplitud (Breadth-First Search).

    Explora por niveles con una cola FIFO. En un grafo no ponderado
    garantiza el camino de menor número de aristas (óptimo).
    Complejidad temporal: O(V + E).  Espacial: O(V).
    """
    t0 = time.perf_counter()
    padre: Dict[Posicion, Optional[Posicion]] = {inicio: None}
    frontera: deque[Posicion] = deque([inicio])
    orden: List[Posicion] = []
    expandidos = 0
    aristas_evaluadas = 0
    frontera_max = 1
    historial_frontera: List[int] = []

    while frontera:
        frontera_actual = len(frontera)
        historial_frontera.append(frontera_actual)
        frontera_max = max(frontera_max, frontera_actual)
        actual = frontera.popleft()
        expandidos += 1
        orden.append(actual)

        if actual == meta:
            break

        for vecino in vecinos(actual):
            aristas_evaluadas += 1
            if vecino not in padre:
                padre[vecino] = actual
                frontera.append(vecino)

    tiempo = time.perf_counter() - t0
    camino = _reconstruir_camino(padre, meta)
    return Resultado(
        algoritmo="BFS",
        encontrado=bool(camino),
        camino=camino,
        expandidos=expandidos,
        aristas_evaluadas=aristas_evaluadas,
        frontera_max=frontera_max,
        tiempo_seg=tiempo,
        orden_expansion=orden,
        historial_frontera=historial_frontera,
    )


def dfs(
    inicio: Posicion = INICIO,
    meta: Posicion = META,
) -> Resultado:
    """
    Búsqueda en profundidad (Depth-First Search).

    Explora por ramas con una pila LIFO. Encuentra *un* camino, pero no
    garantiza que sea el más corto.
    Complejidad temporal: O(V + E).  Espacial: O(V).
    """
    t0 = time.perf_counter()
    padre: Dict[Posicion, Optional[Posicion]] = {inicio: None}
    frontera: List[Posicion] = [inicio]
    orden: List[Posicion] = []
    expandidos = 0
    aristas_evaluadas = 0
    frontera_max = 1
    historial_frontera: List[int] = []

    while frontera:
        frontera_actual = len(frontera)
        historial_frontera.append(frontera_actual)
        frontera_max = max(frontera_max, frontera_actual)
        actual = frontera.pop()
        expandidos += 1
        orden.append(actual)

        if actual == meta:
            break

        # Se invierte el orden para que el recorrido visual vaya
        # arriba, abajo, izquierda, derecha.
        candidatos = list(vecinos(actual))
        aristas_evaluadas += len(candidatos)
        for vecino in reversed(candidatos):
            if vecino not in padre:
                padre[vecino] = actual
                frontera.append(vecino)

    tiempo = time.perf_counter() - t0
    camino = _reconstruir_camino(padre, meta)
    return Resultado(
        algoritmo="DFS",
        encontrado=bool(camino),
        camino=camino,
        expandidos=expandidos,
        aristas_evaluadas=aristas_evaluadas,
        frontera_max=frontera_max,
        tiempo_seg=tiempo,
        orden_expansion=orden,
        historial_frontera=historial_frontera,
    )


def medir_tiempo_promedio(
    funcion: Callable[[], Resultado], repeticiones: int = 200, lotes: int = 5
) -> float:
    """
    Ejecuta la búsqueda varias veces y devuelve el mejor tiempo medio por
    ejecución (en segundos).

    Se descarta una primera ejecución de calentamiento y se toman varios
    lotes, quedándose con el más rápido. Así se reduce el ruido del sistema
    operativo y la comparación entre algoritmos es más justa.
    """
    funcion()  # calentamiento (cachés de CPU, importaciones, etc.)
    mejor = float("inf")
    for _ in range(lotes):
        t0 = time.perf_counter()
        for _ in range(repeticiones):
            funcion()
        mejor = min(mejor, (time.perf_counter() - t0) / repeticiones)
    return mejor
