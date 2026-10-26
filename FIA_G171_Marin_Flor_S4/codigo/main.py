#!/usr/bin/env python3
"""
Actividad 2.4 — Algoritmos de búsqueda ciega (BFS y DFS).

Resuelve un laberinto de 31 x 19 celdas con búsqueda en amplitud (BFS) y
búsqueda en profundidad (DFS), y compara:
  - longitud del camino solución,
  - nodos expandidos,
  - aristas evaluadas,
  - tamaño máximo de la frontera,
  - tiempo de ejecución.

No requiere instalar ninguna librería: usa solo la biblioteca estándar.
"""
from __future__ import annotations

from pathlib import Path

from busqueda_ciega import bfs, dfs, medir_tiempo_promedio
from laberinto import COLUMNAS, FILAS, INICIO, LABERINTO, META, imprimir_laberinto

BASE_DIR = Path(__file__).resolve().parent
SALIDA = BASE_DIR.parent / "resultados_ejecucion_2.4.txt"
REPETICIONES = 200


def linea(caracter: str = "=", ancho: int = 68) -> str:
    return caracter * ancho


def main() -> None:
    print(linea())
    print("ACTIVIDAD 2.4 — BÚSQUEDA CIEGA: BFS Y DFS")
    print(linea())
    print(f"\nLaberinto: {FILAS} filas x {COLUMNAS} columnas "
          f"({FILAS * COLUMNAS} celdas, {sum(f.count('#') for f in LABERINTO)} muros)")
    print(f"Inicio: {INICIO}   Meta: {META}")
    print("\nRepresentación: grafo no dirigido y no ponderado")
    print("  - nodo  = celda transitable")
    print("  - arista = celdas adyacentes sin muro (arriba/abajo/izquierda/derecha)\n")

    print(linea("-"))
    print("LABERINTO")
    print(linea("-"))
    print(imprimir_laberinto())

    # Ejecuciones
    r_bfs = bfs()
    r_dfs = dfs()

    # Tiempo medio (más representativo que una sola ejecución)
    t_bfs = medir_tiempo_promedio(lambda: bfs(), REPETICIONES)
    t_dfs = medir_tiempo_promedio(lambda: dfs(), REPETICIONES)

    print("\n" + linea("-"))
    print("SOLUCIÓN CON BFS (camino más corto)")
    print(linea("-"))
    print(imprimir_laberinto(r_bfs.camino))

    print("\n" + linea("-"))
    print("SOLUCIÓN CON DFS (primer camino encontrado)")
    print(linea("-"))
    print(imprimir_laberinto(r_dfs.camino))

    print("\n" + linea("-"))
    print("COMPARACIÓN DE RESULTADOS")
    print(linea("-"))
    print(f"{'Métrica':<34}{'BFS':>14}{'DFS':>14}")
    print(f"{'-' * 62}")
    print(f"{'¿Encuentra solución?':<34}{'Sí' if r_bfs.encontrado else 'No':>14}"
          f"{'Sí' if r_dfs.encontrado else 'No':>14}")
    print(f"{'Celdas del camino':<34}{r_bfs.longitud_camino:>14}{r_dfs.longitud_camino:>14}")
    print(f"{'Movimientos (aristas)':<34}{r_bfs.coste:>14}{r_dfs.coste:>14}")
    print(f"{'Nodos expandidos':<34}{r_bfs.expandidos:>14}{r_dfs.expandidos:>14}")
    print(f"{'Aristas evaluadas':<34}{r_bfs.aristas_evaluadas:>14}{r_dfs.aristas_evaluadas:>14}")
    print(f"{'Frontera máxima':<34}{r_bfs.frontera_max:>14}{r_dfs.frontera_max:>14}")
    print(f"{'Tiempo medio (ms)':<34}{t_bfs * 1000:>14.4f}{t_dfs * 1000:>14.4f}")
    print(f"{'¿Camino óptimo?':<34}{'Sí':>14}{'No':>14}")
    print(f"\nTiempo medio calculado con {REPETICIONES} ejecuciones (mejor de 5 lotes).")

    print("\n" + linea("-"))
    print("COMPLEJIDAD")
    print(linea("-"))
    print("  BFS:  tiempo O(V + E)   ·   espacio O(V)")
    print("  DFS:  tiempo O(V + E)   ·   espacio O(V)")
    print("  V = celdas transitables, E = aristas del grafo del laberinto")

    print("\n" + linea("-"))
    print("CONCLUSIÓN")
    print(linea("-"))
    print(f"  BFS garantiza el camino más corto ({r_bfs.longitud_camino} celdas frente a")
    print(f"  {r_dfs.longitud_camino}), pero expande más nodos ({r_bfs.expandidos} frente a")
    print(f"  {r_dfs.expandidos}). En esta instancia DFS alcanzó una frontera algo mayor")
    print(f"  ({r_dfs.frontera_max} frente a {r_bfs.frontera_max}), porque apila todos los")
    print("  vecinos de cada nodo. Ambos son O(V + E) en tiempo y O(V) en espacio.")
    print("  Para laberintos con bucles conviene BFS si se busca la ruta mínima;")
    print("  DFS solo si basta con *alguna* ruta y se acepta que no sea óptima.")

    # Guardar informe
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(linea() + "\n")
        f.write("ACTIVIDAD 2.4 — BÚSQUEDA CIEGA: BFS Y DFS\n")
        f.write(linea() + "\n\n")
        f.write(f"Laberinto: {FILAS} x {COLUMNAS} celdas\n")
        f.write(f"Inicio: {INICIO}   Meta: {META}\n")
        f.write("Representación: grafo no dirigido y no ponderado\n\n")
        f.write("Métrica;BFS;DFS\n")
        f.write(f"Encuentra solución;{'Sí' if r_bfs.encontrado else 'No'};"
                f"{'Sí' if r_dfs.encontrado else 'No'}\n")
        f.write(f"Celdas del camino;{r_bfs.longitud_camino};{r_dfs.longitud_camino}\n")
        f.write(f"Movimientos;{r_bfs.coste};{r_dfs.coste}\n")
        f.write(f"Nodos expandidos;{r_bfs.expandidos};{r_dfs.expandidos}\n")
        f.write(f"Aristas evaluadas;{r_bfs.aristas_evaluadas};{r_dfs.aristas_evaluadas}\n")
        f.write(f"Frontera máxima;{r_bfs.frontera_max};{r_dfs.frontera_max}\n")
        f.write(f"Tiempo medio (ms);{t_bfs * 1000:.4f};{t_dfs * 1000:.4f}\n")
        f.write(f"Camino óptimo;Sí;No\n\n")
        f.write("Camino BFS:\n")
        f.write(" -> ".join(str(p) for p in r_bfs.camino) + "\n\n")
        f.write("Camino DFS:\n")
        f.write(" -> ".join(str(p) for p in r_dfs.camino) + "\n\n")
        f.write("Laberinto con solución BFS:\n")
        f.write(imprimir_laberinto(r_bfs.camino) + "\n\n")
        f.write("Laberinto con solución DFS:\n")
        f.write(imprimir_laberinto(r_dfs.camino) + "\n")

    print(f"\nResultados guardados en: {SALIDA}")
    print("\n¡Terminado!")


if __name__ == "__main__":
    main()
