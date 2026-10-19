#!/usr/bin/env python3
"""
Script principal — Actividades 2.1 y 2.2 (Fundamentos de IA).

Ejecuta el flujo completo:

  1. Modela los 2 problemas reales como problemas de búsqueda
     (estados, acciones, coste y meta) en generador_estados.py.
  2. Genera el espacio de estados con el generador (exploración en amplitud).
  3. Construye cada espacio como GRAFO DIRIGIDO y PONDERADO con NetworkX
     y guarda las figuras en ../figuras.
  4. Ejecuta BFS, Dijkstra y A*, compara resultados y verifica la optimalidad
     del problema 2 por fuerza bruta.
  5. Escribe el informe de ejecución en ../resultados_ejecucion.txt.

Uso:  python3 main.py
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from busqueda import (
    a_estrella,
    busqueda_amplitud,
    dijkstra,
    fuerza_bruta_tsp,
    heuristica_euclidiana,
)
from construir_grafos import (
    FIGURAS_DIR,
    figura_arbol_estados,
    figura_espacio_dron,
    figura_red_calles,
    figura_red_dron,
    figura_solucion_dron,
    figura_solucion_problema1,
    grafo_espacio_estados,
    grafo_red_calles,
    grafo_red_dron,
)
from generador_estados import (
    BASE,
    NOMBRES_RED,
    PUNTOS_ENTREGA,
    RED_CALLES,
    TIEMPOS_VUELO,
    GeneradorRutaDron,
    GeneradorRuteoAmbulancia,
    explorar_espacio,
)

INFORME = Path(__file__).resolve().parent.parent / "resultados_ejecucion.txt"

_lineas: List[str] = []


def log(texto: str = "") -> None:
    """Imprime por pantalla y acumula para el informe de ejecución."""
    print(texto)
    _lineas.append(texto)


def titulo(texto: str) -> None:
    log("=" * 78)
    log(texto)
    log("=" * 78)


def seccion(texto: str) -> None:
    log()
    log(f"--- {texto} " + "-" * max(0, 72 - len(texto)))


def modelo_problema1() -> None:
    seccion("Modelo del problema 1")
    filas = [
        ("Estados (S)", "las 12 intersecciones de la red urbana (A…L)"),
        ("Estado inicial (s0)", "'A' = Cuartel"),
        ("Acciones (A)", "circular por una calle adyacente respetando el "
                         "sentido único (una acción por arista saliente)"),
        ("Función de transición", "aplicar una acción mueve la ambulancia a la "
                                  "intersección destino"),
        ("Coste", "minutos de traslado por la calle en hora pico (peso de la arista)"),
        ("Meta", "'L' = Hospital General"),
        ("Espacio de estados", "grafo DIRIGIDO (sentidos únicos) y PONDERADO (minutos); "
                               "el grafo físico y el de estados coinciden"),
        ("Propiedad", "costes no negativos → aplicable Dijkstra y A*"),
    ]
    for k, v in filas:
        log(f"  {k:<24}: {v}")


def modelo_problema2() -> None:
    seccion("Modelo del problema 2")
    filas = [
        ("Estados (S)", "(nodo_actual, conjunto_de_entregas_realizadas), p. ej. "
                        "(P1, {P1, P2})"),
        ("Estado inicial (s0)", "(BASE, ∅) = el dron en la base sin entregar"),
        ("Acciones (A)", "volar a un punto de entrega aún no visitado; cuando ya "
                         "se entregó todo, regresar a la BASE"),
        ("Función de transición", "la acción añade el punto al conjunto y mueve el dron"),
        ("Coste", "minutos de vuelo del tramo (peso de la arista)"),
        ("Meta", "(BASE, {P1, P2, P3, P4}) = de vuelta con todas las entregas"),
        ("Espacio de estados", "grafo DIRIGIDO y PONDERADO generado por el "
                               "generador de estados (los tiempos no son simétricos)"),
        ("Restricción", "no se vuelve a la base hasta completar las entregas "
                        "(autonomía del dron)"),
    ]
    for k, v in filas:
        log(f"  {k:<24}: {v}")


def problema1() -> None:
    titulo("PROBLEMA 1 — RUTEO DE UNA AMBULANCIA EN RED URBANA DE SENTIDOS ÚNICOS")
    modelo_problema1()

    g = grafo_red_calles()
    generador = GeneradorRuteoAmbulancia()
    espacio = explorar_espacio(generador)

    seccion("Generación de estados")
    log(f"  Estados generados (BFS desde el estado inicial): {espacio.num_estados}")
    log(f"  Transiciones (acciones con coste)             : {espacio.num_transiciones}")
    log(f"  Niveles del árbol de generación               : {espacio.num_niveles}")
    log("  Sucesores del estado inicial:")
    for t in generador.sucesores(generador.estado_inicial):
        log(f"     {t}")

    seccion("Grafo del espacio de estados (NetworkX)")
    log(f"  Tipo: {type(g).__name__} (grafo dirigido ponderado)")
    log(f"  Nodos (estados) : {g.number_of_nodes()}")
    log(f"  Aristas (transiciones): {g.number_of_edges()}")
    log(f"  ¿Dirigido? {g.is_directed()} | ¿Ponderado? "
        f"{'weight' in next(iter(g.edges(data=True)))[2]}")
    log("  Ejemplos de aristas (origen → destino): minutos — calle")
    for (o, d), (m, calle) in list(RED_CALLES.items())[:6]:
        log(f"     {o} → {d}: {m:>2g} min — {calle}")

    seccion("Resultados de búsqueda (cuartel A → hospital L)")
    r_bfs = busqueda_amplitud(g, generador.estado_inicial, generador.meta)
    r_dij = dijkstra(g, generador.estado_inicial, generador.meta)
    h = heuristica_euclidiana(g, generador.meta)
    r_ast = a_estrella(g, generador.estado_inicial, generador.meta, h)
    for r in (r_bfs, r_dij, r_ast):
        log("  " + r.resumen().replace("\n", "\n  "))

    mejor = min(r.coste for r in (r_bfs, r_dij, r_ast))
    log()
    log("  Análisis:")
    log(f"    • BFS encuentra {r_bfs.coste:g} min con {r_bfs.aristas} calles "
        f"(mínimo número de aristas, IGNORA el coste).")
    log(f"    • Dijkstra y A* encuentran {mejor:g} min (óptimo): "
        "minimizan el tiempo real de traslado.")
    log(f"    • A* expandió {r_ast.expandidos} estados frente a {r_dij.expandidos} "
        "de Dijkstra, con la misma solución (la heurística admisible guía la búsqueda).")
    log("    • Conclusión: en grafos ponderados, minimizar aristas no garantiza "
        "minimizar el coste.")

    seccion("Figuras generadas")
    figura_red_calles(g, FIGURAS_DIR / "problema1_red_calles.png")
    figura_arbol_estados(generador, espacio, FIGURAS_DIR / "problema1_arbol_estados.png")
    figura_solucion_problema1(
        g,
        [
            (r_bfs.camino, "#C0392B", "BFS (mín. nº de calles)", "solid"),
            (r_dij.camino, "#1E8449", "Dijkstra (mín. coste)", "solid"),
            (r_ast.camino, "#7D3C98", "A* (óptimo informado)", (0, (4, 2))),
        ],
        FIGURAS_DIR / "problema1_solucion_comparada.png",
    )
    return r_bfs, r_dij, r_ast


def problema2() -> None:
    titulo("PROBLEMA 2 — RUTA DE UN DRON DE REPARTO CON VÁRIAS ENTREGAS (TSP)")
    modelo_problema2()

    g_red = grafo_red_dron()
    generador = GeneradorRutaDron()
    espacio = explorar_espacio(generador)
    g_estados = grafo_espacio_estados(espacio)

    seccion("Generación de estados")
    log(f"  Estados generados (BFS desde (BASE, ∅)) : {espacio.num_estados}")
    log(f"  Transiciones (acciones con coste)       : {espacio.num_transiciones}")
    log(f"  Niveles del árbol de generación         : {espacio.num_niveles}")
    log("  Sucesores del estado inicial:")
    for t in generador.sucesores(generador.estado_inicial):
        log(f"     {t}")

    seccion("Grafos del problema 2 (NetworkX)")
    log(f"  Red física : {type(g_red).__name__} | {g_red.number_of_nodes()} nodos | "
        f"{g_red.number_of_edges()} aristas dirigidas (tiempos asimétricos)")
    log(f"  Ejemplo de asimetría: P2→P3 = {TIEMPOS_VUELO[('P2','P3')]:g} min, "
        f"P3→P2 = {TIEMPOS_VUELO[('P3','P2')]:g} min")
    log(f"  Espacio de estados: {type(g_estados).__name__} | "
        f"{g_estados.number_of_nodes()} estados | "
        f"{g_estados.number_of_edges()} transiciones")
    log(f"  ¿Dirigido? {g_estados.is_directed()} | ¿Ponderado? "
        f"{'weight' in next(iter(g_estados.edges(data=True)))[2]}")

    seccion("Resultados de búsqueda ((BASE, ∅) → (BASE, todas las entregas))")
    r_bfs = busqueda_amplitud(g_estados, generador.estado_inicial, generador.estado_meta)
    r_dij = dijkstra(g_estados, generador.estado_inicial, generador.estado_meta)
    for r in (r_bfs, r_dij):
        log("  " + r.resumen().replace("\n", "\n  "))
        log("     orden de entrega: "
            + " → ".join(e[0] for e in r.camino))

    orden, coste_fb = fuerza_bruta_tsp(TIEMPOS_VUELO, BASE, list(PUNTOS_ENTREGA))
    r_dij.optimum_verificado = abs(r_dij.coste - coste_fb) < 1e-9
    seccion("Verificación de optimalidad (fuerza bruta, 4! = 24 ordenes)")
    log(f"  Mejor orden por enumeración exhaustiva: "
        + " → ".join(orden) + f" | {coste_fb:g} min")
    log(f"  Coste de Dijkstra                     : {r_dij.coste:g} min")
    log(f"  ¿Coinciden? {'SÍ — solución óptima verificada' if r_dij.optimum_verificado else 'NO (revisar)'}")

    log()
    log("  Análisis:")
    log(f"    • BFS entrega una ruta de {r_bfs.coste:g} min: elige el camino con menos "
        "acciones, sin mirar los minutos de vuelo.")
    log(f"    • Dijkstra entrega la ruta óptima de {r_dij.coste:g} min "
        f"({r_bfs.coste - r_dij.coste:g} min menos que BFS).")
    log("    • El espacio de estados es EXPLÍCITO (34 estados generados): a diferencia "
        "del problema 1, el grafo físico y el de estados NO coinciden.")

    seccion("Figuras generadas")
    figura_red_dron(g_red, FIGURAS_DIR / "problema2_red_fisica.png")
    figura_espacio_dron(g_estados, espacio, FIGURAS_DIR / "problema2_espacio_estados.png")
    figura_solucion_dron(g_estados, espacio, r_dij.camino, r_dij.coste,
                         FIGURAS_DIR / "problema2_solucion_optima.png")
    return r_bfs, r_dij


def main() -> None:
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    titulo("ACTIVIDADES 2.1 y 2.2 — PROBLEMAS Y ESPACIOS DE BÚSQUEDA")
    log("Modelado + generación de estados + grafos con NetworkX + búsqueda.")
    log("Generador de estados: generador_estados.py | Grafos: construir_grafos.py | "
        "Algoritmos: busqueda.py")

    problema1()
    problema2()

    seccion("Resumen comparativo")
    log(f"  {'Problema':<26} {'estados':>9} {'transiciones':>14} {'dirigido':>10} "
        f"{'ponderado':>11}")
    log(f"  {'1. Ruteo de ambulancia':<26} {12:>9} {18:>14} {'sí':>10} {'sí':>11}")
    log(f"  {'2. Reparto del dron':<26} {34:>9} {56:>14} {'sí':>10} {'sí':>11}")

    seccion("Archivos generados")
    for f in sorted(FIGURAS_DIR.glob("*.png")):
        log(f"  ../figuras/{f.name}")
    log(f"  ../{INFORME.name}")

    INFORME.write_text("\n".join(_lineas) + "\n", encoding="utf-8")
    print(f"\nInforme de ejecución guardado en: {INFORME}")


if __name__ == "__main__":
    main()
