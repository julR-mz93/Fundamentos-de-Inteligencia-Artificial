#!/usr/bin/env python3
"""
Laberinto de la Actividad 2.4.

Representación:
  '#' = muro
  '.' = pasillo transitable
  'S' = inicio
  'E' = salida

El laberinto se modela como un grafo no dirigido y no ponderado:
  - cada celda transitable es un nodo,
  - cada par de celdas adyacentes (arriba, abajo, izquierda, derecha)
    sin muro entre ellas es una arista.

Este módulo NO usa librerías externas: solo la biblioteca estándar.
"""
from __future__ import annotations

from typing import Iterator, List, Tuple

# Laberinto de 31 columnas x 19 filas (con bucles: hay varios caminos posibles)
LABERINTO: Tuple[str, ...] = (
    "###############################",
    "#S#...............#.#.........#",
    "#.#######.######..#.#.##..#.#.#",
    "#.........#.....#.#.......#.#.#",
    "######.########.#.#.#####.#.#.#",
    "#...............#.#.......#.#.#",
    "#.#.#######.###.#.#######.#.#.#",
    "#.#.#.......#.....#...#...#.#.#",
    "#.#....##.###.##.##.#.#.###...#",
    "#.#...#.#...#.#.....#.#...#.#.#",
    "#.#..##.###.#.#..####.###.#.#.#",
    "#.#.....#.....#.#.#...#...#.#.#",
    "#.#####...#####.#.#.###.###.###",
    "#.....#.....#.....#.#.....#...#",
    "#.###.#####.#.###.#.#########.#",
    "#...#.#...#.#.#...#.........#.#",
    "#.#.###.#...#.#.#.######.##.#.#",
    "#.#.....#....................E#",
    "###############################",
)

FILAS = len(LABERINTO)
COLUMNAS = len(LABERINTO[0])

Posicion = Tuple[int, int]


def buscar_simbolo(simbolo: str) -> Posicion:
    """Devuelve la posición (fila, columna) del símbolo indicado."""
    for f, fila in enumerate(LABERINTO):
        c = fila.find(simbolo)
        if c != -1:
            return (f, c)
    raise ValueError(f"No se encontró el símbolo {simbolo!r} en el laberinto")


INICIO: Posicion = buscar_simbolo("S")
META: Posicion = buscar_simbolo("E")


def es_transitable(pos: Posicion) -> bool:
    """Indica si una celda está dentro del laberinto y no es un muro."""
    f, c = pos
    return 0 <= f < FILAS and 0 <= c < COLUMNAS and LABERINTO[f][c] != "#"


def vecinos(pos: Posicion) -> Iterator[Posicion]:
    """Genera los vecinos transitables en orden: arriba, abajo, izquierda, derecha."""
    f, c = pos
    for df, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        candidato = (f + df, c + dc)
        if es_transitable(candidato):
            yield candidato


def imprimir_laberinto(camino: List[Posicion] | None = None) -> str:
    """Devuelve el laberinto como texto, marcando el camino con '*'."""
    ocupadas = set(camino or [])
    lineas = []
    for f, fila in enumerate(LABERINTO):
        chars = []
        for c, ch in enumerate(fila):
            if (f, c) == INICIO:
                chars.append("S")
            elif (f, c) == META:
                chars.append("E")
            elif (f, c) in ocupadas and ch != "#":
                chars.append("*")
            else:
                chars.append(ch)
        lineas.append("".join(chars))
    return "\n".join(lineas)
