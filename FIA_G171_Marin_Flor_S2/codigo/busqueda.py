#!/usr/bin/env python3
"""
Algoritmos de búsqueda no informada e informada — Actividades 2.1 y 2.2.

Se implementan tres algoritmos CLÁSICOS sobre los grafos dirigidos y
ponderados construidos con NetworkX:

  • Búsqueda en amplitud (BFS): no usa costes; devuelve un camino con el
    MÍNIMO NÚMERO DE ARISTAS (calles / acciones).
  • Dijkstra: usa los costes; devuelve el camino de MENOR COSTE (óptimo).
  • A*: Dijkstra + heurística admisible; también óptimo, pero expandiendo
    menos estados cuando la heurística es buena.

Cada algoritmo devuelve un Resultado con el camino, su coste y el número de
estados expandidos, de modo que los tres puedan compararse.

Se añade `fuerza_bruta_tsp`, una enumeración exhaustiva de todos los órdenes
de entrega, utilizada como COMPROBACIÓN independiente de la optimalidad de la
solución del problema 2 (4! = 24 ordenes posibles).
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from itertools import permutations
from typing import Callable, Dict, Hashable, List, Optional, Sequence, Tuple

import networkx as nx

Estado = Hashable


@dataclass
class Resultado:
    """Salida común de los algoritmos de búsqueda."""
    algoritmo: str
    camino: List[Estado]
    coste: float
    expandidos: int          # estados extraídos de la frontera
    descubiertos: int        # estados insertados en la frontera
    optimum_verificado: Optional[bool] = None  # si se comparó con fuerza bruta

    @property
    def aristas(self) -> int:
        return max(0, len(self.camino) - 1)

    def resumen(self) -> str:
        ruta = " → ".join(str(e) for e in self.camino)
        linea = (
            f"{self.algoritmo:<26} coste = {self.coste:>5g} min | "
            f"aristas = {self.aristas:>2d} | expandidos = {self.expandidos:>2d} | "
            f"descubiertos = {self.descubiertos:>3d}"
        )
        return linea + "\n" + f"{'':<26} ruta: {ruta}"


# =========================================================================
# 1. Búsqueda en amplitud (BFS) — sin costes
# =========================================================================

def busqueda_amplitud(g: nx.DiGraph, inicio: Estado, meta: Estado) -> Resultado:
    """BFS: mínimo número de aristas entre `inicio` y `meta` (ignora pesos)."""
    padre: Dict[Estado, Optional[Estado]] = {inicio: None}
    cola = [inicio]
    cabeza = 0
    expandidos = 0
    while cabeza < len(cola):
        estado = cola[cabeza]
        cabeza += 1
        expandidos += 1
        if estado == meta:
            break
        for vecino in g.successors(estado):
            if vecino not in padre:
                padre[vecino] = estado
                cola.append(vecino)
    if meta not in padre:
        return Resultado("BFS (amplitud)", [], float("inf"), expandidos, len(padre))
    camino, actual = [], meta
    while actual is not None:
        camino.append(actual)
        actual = padre[actual]
    camino.reverse()
    coste = sum(g[o][d]["weight"] for o, d in zip(camino, camino[1:]))
    return Resultado("BFS (amplitud)", camino, coste, expandidos, len(padre))


# =========================================================================
# 2. Dijkstra — mínimo coste
# =========================================================================

def dijkstra(g: nx.DiGraph, inicio: Estado, meta: Estado) -> Resultado:
    """Dijkstra: camino de coste total mínimo (óptimo) en grafos con pesos ≥ 0."""
    mejor: Dict[Estado, float] = {inicio: 0.0}
    padre: Dict[Estado, Optional[Estado]] = {inicio: None}
    cola: List[Tuple[float, int, Estado]] = [(0.0, 0, inicio)]
    contador = 0
    expandidos = 0
    vistos = set()

    while cola:
        dist, _, estado = heapq.heappop(cola)
        if estado in vistos:
            continue
        vistos.add(estado)
        expandidos += 1
        if estado == meta:
            break
        for vecino, data in g[estado].items():
            nuevo = dist + data["weight"]
            if vecino not in mejor or nuevo < mejor[vecino]:
                mejor[vecino] = nuevo
                padre[vecino] = estado
                contador += 1
                heapq.heappush(cola, (nuevo, contador, vecino))

    if meta not in mejor:
        return Resultado("Dijkstra", [], float("inf"), expandidos, len(padre))
    camino, actual = [], meta
    while actual is not None:
        camino.append(actual)
        actual = padre[actual]
    camino.reverse()
    return Resultado("Dijkstra", camino, mejor[meta], expandidos, len(padre))


# =========================================================================
# 3. A* — Dijkstra + heurística admisible
# =========================================================================

def a_estrella(g: nx.DiGraph, inicio: Estado, meta: Estado,
               h: Callable[[Estado], float]) -> Resultado:
    """A* con heurística admisible h: óptimo y, en general, expande menos."""
    g_score: Dict[Estado, float] = {inicio: 0.0}
    padre: Dict[Estado, Optional[Estado]] = {inicio: None}
    cola: List[Tuple[float, int, Estado]] = [(h(inicio), 0, inicio)]
    contador = 0
    expandidos = 0
    vistos = set()

    while cola:
        f, _, estado = heapq.heappop(cola)
        if estado in vistos:
            continue
        vistos.add(estado)
        expandidos += 1
        if estado == meta:
            break
        for vecino, data in g[estado].items():
            nuevo = g_score[estado] + data["weight"]
            if vecino not in g_score or nuevo < g_score[vecino]:
                g_score[vecino] = nuevo
                padre[vecino] = estado
                contador += 1
                heapq.heappush(cola, (nuevo + h(vecino), contador, vecino))

    if meta not in g_score:
        return Resultado("A*", [], float("inf"), expandidos, len(padre))
    camino, actual = [], meta
    while actual is not None:
        camino.append(actual)
        actual = padre[actual]
    camino.reverse()
    return Resultado("A*", camino, g_score[meta], expandidos, len(padre))


def heuristica_euclidiana(g: nx.DiGraph, meta: Estado, atributo_pos: str = "pos"
                          ) -> Callable[[Estado], float]:
    """
    Construye h(n) = (menor coste por unidad de distancia) × distancia(n, meta).

    Como el factor es el MÍNIMO coste/longitud de todas las aristas del grafo,
    la heurística nunca sobreestima el coste real -> es ADMISIBLE (y consistente).
    """
    px = {n: g.nodes[n][atributo_pos] for n in g.nodes()}
    minimo = float("inf")
    for o, d, data in g.edges(data=True):
        largo = ((px[o][0] - px[d][0]) ** 2 + (px[o][1] - px[d][1]) ** 2) ** 0.5
        if largo > 0:
            minimo = min(minimo, data["weight"] / largo)

    def h(estado: Estado) -> float:
        if estado == meta:
            return 0.0
        dx = px[estado][0] - px[meta][0]
        dy = px[estado][1] - px[meta][1]
        return minimo * (dx * dx + dy * dy) ** 0.5

    return h


# =========================================================================
# 4. Comprobación por fuerza bruta (problema 2)
# =========================================================================

def fuerza_bruta_tsp(tiempos: Dict[Tuple[str, str], float], base: str,
                     puntos: Sequence[str]) -> Tuple[List[str], float]:
    """
    Enumera todos los órdenes de entrega posibles y devuelve el mejor
    (problema del agente viajero con regreso a la base). Sirve como
    referencia independiente para validar la solución de Dijkstra.
    """
    mejor_camino: List[str] = []
    mejor_coste = float("inf")
    for orden in permutations(puntos):
        coste = tiempos[(base, orden[0])]
        for a, b in zip(orden, orden[1:]):
            coste += tiempos[(a, b)]
        coste += tiempos[(orden[-1], base)]
        if coste < mejor_coste:
            mejor_coste = coste
            mejor_camino = [base, *orden, base]
    return mejor_camino, mejor_coste


# =========================================================================
# 5. Prueba rápida
# =========================================================================

if __name__ == "__main__":
    from generador_estados import (
        BASE, PUNTOS_ENTREGA, TIEMPOS_VUELO, GeneradorRutaDron,
        explorar_espacio,
    )
    from construir_grafos import grafo_espacio_estados, grafo_red_calles

    g1 = grafo_red_calles()
    for r in (busqueda_amplitud(g1, "A", "L"),
              dijkstra(g1, "A", "L"),
              a_estrella(g1, "A", "L", heuristica_euclidiana(g1, "L"))):
        print(r.resumen())
        print()

    gen2 = GeneradorRutaDron()
    esp2 = explorar_espacio(gen2)
    g2 = grafo_espacio_estados(esp2)
    r_bfs = busqueda_amplitud(g2, gen2.estado_inicial, gen2.estado_meta)
    r_dij = dijkstra(g2, gen2.estado_inicial, gen2.estado_meta)
    print(r_bfs.resumen())
    print(r_dij.resumen())
    orden, coste = fuerza_bruta_tsp(TIEMPOS_VUELO, BASE, list(PUNTOS_ENTREGA))
    print(f"Fuerza bruta (24 órdenes)   : {' → '.join(orden)} | {coste:g} min")
