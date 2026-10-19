#!/usr/bin/env python3
"""
=============================================================================
 Generador de estados — Actividades 2.1 y 2.2 (Fundamentos de IA)
=============================================================================

Un *problema de búsqueda* se define como la terna:

        P = <S, s0, A, coste, meta>

  • S      : conjunto de estados del sistema.
  • s0     : estado inicial.
  • A(s)   : conjunto de acciones aplicables en el estado s.
  • coste  : función coste(s, a, s') >= 0 para cada transición.
  • meta   : conjunto (o predicado) de estados meta.

Este módulo modela DOS problemas reales y, para cada uno, implementa un
*generador de estados*: una función que, dado un estado, produce todos los
estados alcanzables mediante una acción junto con el coste de la transición.
Una exploración en amplitud (BFS) sobre ese generador construye el espacio de
estados completo, que después se vierte a un grafo de NetworkX
(ver construir_grafos.py).

-----------------------------------------------------------------------------
 PROBLEMA 1 — Ruteo de una ambulancia en red urbana
-----------------------------------------------------------------------------
  • Problema real : minimizar el tiempo de traslado del cuartel al hospital
                    en una red de calles con sentidos únicos (horas pico).
  • Estados       : las intersecciones de la red (un nodo por intersección).
  • Estado inicial: "A" (Cuartel).
  • Acciones      : circular por una calle adyacente respetando el sentido
                    de circulación (una por cada arista saliente).
  • Coste         : minutos de traslado de la calle (arista ponderada).
  • Meta          : "L" (Hospital General).
  • Grafo         : DIRIGIDO (sentidos únicos) y PONDERADO (minutos).

-----------------------------------------------------------------------------
 PROBLEMA 2 — Ruta de un dron de reparto con varias entregas
-----------------------------------------------------------------------------
  • Problema real : un dron debe entregar en 4 puntos y regresar a la base
                    minimizando el tiempo total de vuelo (corredores aéreos
                    con tiempos asimétricos por sentido).
  • Estados       : (nodo_actual, conjunto_de_entregas_realizadas).
  • Estado inicial: (BASE, {}).
  • Acciones      : volar a un punto de entrega aún no visitado; o, cuando ya
                    se entregó todo, regresar a la BASE.
  • Coste         : minutos de vuelo de cada tramo.
  • Meta          : (BASE, {todas las entregas}).
  • Grafo         : DIRIGIDO (los tiempos no son simétricos) y PONDERADO.

Para el problema 2 el espacio de estados es EXPLÍCITO y se genera con este
módulo (66 estados); para el problema 1 el grafo físico y el de estados
coinciden.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Hashable, List, Sequence, Tuple

Estado = Hashable

# =========================================================================
# PROBLEMA 1 — Red de calles para el ruteo de la ambulancia
# =========================================================================

# Nodos de la red (intersecciones). El id se usa en el código y el nombre
# humano se muestra en las figuras.
NOMBRES_RED: Dict[str, str] = {
    "A": "Cuartel",
    "B": "Banco",
    "C": "Mercado",
    "D": "Av. Norte",
    "E": "Plaza",
    "F": "Terminal",
    "G": "Parque",
    "H": "Bodega",
    "I": "Iglesia",
    "J": "Colegio",
    "K": "Depósito",
    "L": "Hospital",
}

# Coordenadas (x, y) usadas solo para dibujar la red tipo cuadrícula.
POSICIONES_RED: Dict[str, Tuple[float, float]] = {
    "A": (0, 2), "B": (1, 2), "C": (2, 2), "D": (3, 2),
    "E": (0, 1), "F": (1, 1), "G": (2, 1), "H": (3, 1),
    "I": (0, 0), "J": (1, 0), "K": (2, 0), "L": (3, 0),
}

# Calles DIRIGIDAS (sentido único): (origen, destino) -> (minutos, nombre).
# Los minutos corresponden al tiempo de traslado en hora pico.
RED_CALLES: Dict[Tuple[str, str], Tuple[float, str]] = {
    # fila norte, sentido este
    ("A", "B"): (3, "Av. Central"),
    ("B", "C"): (5, "Av. Central"),
    ("C", "D"): (4, "Av. Central"),
    # fila central, sentido oeste
    ("H", "G"): (3, "Calle Morelos"),
    ("G", "F"): (4, "Calle Morelos"),
    ("F", "E"): (2, "Calle Morelos"),
    # fila sur, sentido este
    ("I", "J"): (3, "Calle 5 de Mayo"),
    ("J", "K"): (3, "Calle 5 de Mayo"),
    ("K", "L"): (4, "Calle 5 de Mayo"),
    # columna izquierda, sentido norte (y su contraflujo en hora pico)
    ("I", "E"): (4, "Calle Allende"),
    ("E", "A"): (3, "Calle Allende"),
    ("E", "I"): (5, "Calle Allende"),
    # columna central, sentido sur
    ("B", "F"): (3, "Av. Hidalgo"),
    ("F", "J"): (3, "Av. Hidalgo"),
    # columna derecha-izquierda, sentido norte
    ("K", "G"): (5, "Calle Zaragoza"),
    ("G", "C"): (4, "Calle Zaragoza"),
    # columna derecha, sentido sur
    ("D", "H"): (5, "Av. Madero"),
    ("H", "L"): (4, "Av. Madero"),
}

INICIO_RED = "A"   # Cuartel
META_RED = "L"     # Hospital General

# =========================================================================
# PROBLEMA 2 — Dron de reparto con varias entregas
# =========================================================================

BASE = "BASE"
PUNTOS_ENTREGA: Dict[str, str] = {
    "P1": "Farmacia",
    "P2": "Clínica",
    "P3": "Mercado",
    "P4": "Escuela",
}

# Tiempos de vuelo en minutos: (origen, destino) -> minutos.
# Son ASIMÉTRICOS a propósito: corredores aéreos unidireccionales,
# viento y zonas de exclusión hacen que un trayecto no cueste lo mismo
# que su inverso -> por eso el grafo es DIRIGIDO.
TIEMPOS_VUELO: Dict[Tuple[str, str], float] = {
    ("BASE", "P1"): 4,  ("P1", "BASE"): 6,
    ("BASE", "P2"): 6,  ("P2", "BASE"): 5,
    ("BASE", "P3"): 7,  ("P3", "BASE"): 8,
    ("BASE", "P4"): 5,  ("P4", "BASE"): 7,
    ("P1", "P2"): 3,    ("P2", "P1"): 4,
    ("P1", "P3"): 5,    ("P3", "P1"): 5,
    ("P1", "P4"): 6,    ("P4", "P1"): 3,
    ("P2", "P3"): 8,    ("P3", "P2"): 6,   # corredor con desvío por zona de exclusión
    ("P2", "P4"): 3,    ("P4", "P2"): 5,
    ("P3", "P4"): 4,    ("P4", "P3"): 6,
}

# Posiciones (para dibujar la red física del dron, no afectan al coste).
POSICIONES_DRON: Dict[str, Tuple[float, float]] = {
    "BASE": (0, 0),
    "P1": (-1.6, 1.4),
    "P2": (1.7, 1.5),
    "P3": (-1.4, -1.6),
    "P4": (1.8, -1.3),
}

CONJUNTO_TOTAL: FrozenSet[str] = frozenset(PUNTOS_ENTREGA)
EstadoDron = Tuple[str, FrozenSet[str]]
INICIO_DRON: EstadoDron = (BASE, frozenset())
META_DRON: EstadoDron = (BASE, CONJUNTO_TOTAL)


# =========================================================================
# Transición y generadores de estados
# =========================================================================

@dataclass(frozen=True)
class Transicion:
    """Una acción aplicada a un estado: s --(accion, coste)--> s'."""
    accion: str
    origen: Estado
    destino: Estado
    coste: float

    def __str__(self) -> str:
        return f"{self.origen} --[{self.accion}; {self.coste:g} min]--> {self.destino}"


class GeneradorRuteoAmbulancia:
    """Generador de estados del problema 1 (red de calles dirigida y ponderada)."""

    descripcion = "Ruteo de ambulancia: cuartel -> hospital por red de sentidos únicos"

    def __init__(
        self,
        red: Dict[Tuple[str, str], Tuple[float, str]] = RED_CALLES,
        inicio: str = INICIO_RED,
        meta: str = META_RED,
    ) -> None:
        self.red = red
        self.inicio = inicio
        self.meta = meta

    # -- interfaz del generador ------------------------------------------
    @property
    def estado_inicial(self) -> Estado:
        return self.inicio

    def es_meta(self, estado: Estado) -> bool:
        return estado == self.meta

    def acciones(self, estado: Estado) -> List[str]:
        return [
            f"Tomar {nombre} hacia {destino}"
            for (origen, destino), (_, nombre) in self.red.items()
            if origen == estado
        ]

    def sucesores(self, estado: Estado) -> List[Transicion]:
        """Todos los estados alcanzables desde `estado` con su coste."""
        return [
            Transicion(
                accion=f"Tomar {nombre} hacia {destino}",
                origen=estado,
                destino=destino,
                coste=minutos,
            )
            for (origen, destino), (minutos, nombre) in self.red.items()
            if origen == estado
        ]


class GeneradorRutaDron:
    """Generador de estados del problema 2 (rutas de reparto del dron)."""

    descripcion = "Ruta de dron con 4 entregas y regreso a la base (tiempos asimétricos)"

    def __init__(
        self,
        tiempos: Dict[Tuple[str, str], float] = TIEMPOS_VUELO,
        puntos: Dict[str, str] = PUNTOS_ENTREGA,
        base: str = BASE,
    ) -> None:
        self.tiempos = tiempos
        self.puntos = puntos
        self.base = base
        self.total = frozenset(puntos)

    # -- interfaz del generador ------------------------------------------
    @property
    def estado_inicial(self) -> Estado:
        return (self.base, frozenset())

    @property
    def estado_meta(self) -> Estado:
        return (self.base, self.total)

    def es_meta(self, estado: Estado) -> bool:
        return estado == self.estado_meta

    def acciones(self, estado: Estado) -> List[str]:
        nodo, hechas = estado  # type: ignore[misc]
        if hechas == self.total:
            return [f"Regresar a {self.base}"] if nodo != self.base else []
        return [
            f"Volar a {self.puntos[p]} ({p})"
            for p in sorted(self.puntos)
            if p not in hechas
        ]

    def sucesores(self, estado: Estado) -> List[Transicion]:
        nodo, hechas = estado  # type: ignore[misc]
        # Regreso a la base sólo cuando ya se completaron las entregas.
        if hechas == self.total:
            if nodo == self.base:
                return []
            return [Transicion(
                accion=f"Regresar a {self.base}",
                origen=estado,
                destino=(self.base, self.total),
                coste=self.tiempos[(nodo, self.base)],
            )]
        # Elegir el siguiente punto de entrega aún no visitado.
        return [
            Transicion(
                accion=f"Volar a {self.puntos[p]} ({p})",
                origen=estado,
                destino=(p, hechas | {p}),
                coste=self.tiempos[(nodo, p)],
            )
            for p in sorted(self.puntos)
            if p not in hechas
        ]


# =========================================================================
# Exploración del espacio de estados (BFS sobre el generador)
# =========================================================================

@dataclass
class EspacioEstados:
    """Resultado de explorar el generador desde el estado inicial."""
    estados: List[Estado] = field(default_factory=list)          # orden de descubrimiento
    nivel: Dict[Estado, int] = field(default_factory=dict)        # profundidad en el árbol BFS
    transiciones: Dict[Estado, List[Transicion]] = field(default_factory=dict)
    alcanzables: int = 0

    @property
    def num_estados(self) -> int:
        return len(self.estados)

    @property
    def num_transiciones(self) -> int:
        return sum(len(t) for t in self.transiciones.values())

    @property
    def num_niveles(self) -> int:
        return max(self.nivel.values(), default=0) + 1


def explorar_espacio(generador, limite: int = 100_000) -> EspacioEstados:
    """
    Genera el espacio de estados mediante exploración en amplitud (BFS)
    desde el estado inicial, hasta agotar los estados alcanzables (o
    alcanzar el límite de seguridad `limite`).

    Devuelve los estados descubiertos, su profundidad y las transiciones
    (accion, coste) entre ellos: es la materia prima para dibujar el grafo
    del espacio de estados con NetworkX.
    """
    espacio = EspacioEstados()
    inicial = generador.estado_inicial
    cola = deque([inicial])
    vistos = {inicial}
    espacio.nivel[inicial] = 0
    espacio.transiciones[inicial] = []

    while cola:
        estado = cola.popleft()
        espacio.estados.append(estado)
        sucesores = generador.sucesores(estado)
        espacio.transiciones[estado] = sucesores
        for tr in sucesores:
            if tr.destino not in vistos:
                vistos.add(tr.destino)
                espacio.nivel[tr.destino] = espacio.nivel[estado] + 1
                espacio.transiciones[tr.destino] = []
                if len(vistos) > limite:
                    raise RuntimeError(
                        f"El espacio supera el límite de {limite} estados; "
                        "ajusta el problema o aumenta el límite."
                    )
                cola.append(tr.destino)

    espacio.alcanzables = len(vistos)
    return espacio


# =========================================================================
# Prueba rápida del módulo
# =========================================================================

if __name__ == "__main__":
    print("=" * 74)
    print("PROBLEMA 1 —", GeneradorRuteoAmbulancia.descripcion)
    print("=" * 74)
    g1 = GeneradorRuteoAmbulancia()
    e1 = explorar_espacio(g1)
    print(f"Estados generados : {e1.num_estados}")
    print(f"Transiciones      : {e1.num_transiciones}")
    print(f"Niveles (BFS)     : {e1.num_niveles}")
    print("Sucesores del estado inicial:")
    for t in g1.sucesores(g1.estado_inicial):
        print("   ", t)

    print()
    print("=" * 74)
    print("PROBLEMA 2 —", GeneradorRutaDron.descripcion)
    print("=" * 74)
    g2 = GeneradorRutaDron()
    e2 = explorar_espacio(g2)
    print(f"Estados generados : {e2.num_estados}")
    print(f"Transiciones      : {e2.num_transiciones}")
    print(f"Niveles (BFS)     : {e2.num_niveles}")
    print("Sucesores del estado inicial:")
    for t in g2.sucesores(g2.estado_inicial):
        print("   ", t)
    print("Sucesores de (P1, {P1}):")
    for t in g2.sucesores(("P1", frozenset({"P1"}))):
        print("   ", t)
