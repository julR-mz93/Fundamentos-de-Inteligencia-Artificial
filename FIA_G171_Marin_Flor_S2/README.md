# Actividad 2.1 — Problemas de búsqueda · Actividad 2.2 — Espacios de búsqueda

**Entregable:** modelado + código (Python + NetworkX) + memoria en Word/PDF.

Dos problemas reales se modelan como problemas de búsqueda
`P = <S, s0, A, coste, meta>`, se representan cada uno como **grafo dirigido
y ponderado**, se genera su espacio de estados con un **generador de estados**
en Python y se resuelven con algoritmos clásicos (BFS, Dijkstra y A*).

## Problemas modelados

| | Problema 1 | Problema 2 |
|---|---|---|
| **Descripción** | Ruteo de una ambulancia del cuartel al hospital en una red de calles con sentidos únicos | Ruta de un dron que entrega en 4 puntos y regresa a la base |
| **Estados** | 12 intersecciones (A…L) | `(nodo actual, entregas realizadas)` |
| **Acciones** | Circula por una calle adyacente respetando el sentido único | Volar a un punto sin entregar; al terminar, regresar a la base |
| **Coste** | Minutos de traslado en hora pico (peso de la arista) | Minutos de vuelo por tramo (asimétricos) |
| **Meta** | `L` (Hospital General) | `(BASE, {P1,P2,P3,P4})` |
| **Grafo** | Dirigido + ponderado · 12 nodos / 18 aristas | Dirigido + ponderado · 34 estados / 56 transiciones |

## Resultados principales

| Algoritmo | Problema 1 (A → L) | Problema 2 (base → base) |
|-----------|--------------------|--------------------------|
| BFS (amplitud) | 21 min · 5 calles · 12 expandidos | 26 min (BASE→P1→P2→P3→P4→BASE) |
| Dijkstra | **16 min** · 10 expandidos | **22 min** (BASE→P3→P4→P1→P2→BASE) |
| A* (heurística admisible) | **16 min** · 9 expandidos | — |
| Fuerza bruta (24 órdenes) | — | **22 min** → confirma la optimalidad |

Conclusión clave: **minimizar el número de aristas (BFS) no minimiza el coste**
en grafos ponderados; Dijkstra y A* sí encuentran la solución óptima.

## Estructura

```
actividad_2.1_2.2_problemas_busqueda/
├── memoria_actividad_2.1_2.2.docx   ← memoria completa (modelado, grafos, resultados)
├── memoria_actividad_2.1_2.2.pdf
├── resultados_ejecucion.txt         ← salida íntegra de main.py
├── README.md
├── codigo/
│   ├── generador_estados.py         ← datos + modelos + GENERADOR DE ESTADOS (BFS)
│   ├── construir_grafos.py          ← grafos NetworkX + figuras (dirigidos/ponderados)
│   ├── busqueda.py                  ← BFS, Dijkstra, A* y verificación por fuerza bruta
│   ├── main.py                      ← script principal (ejecuta todo)
│   └── requirements.txt
└── figuras/
    ├── problema1_red_calles.png          grafo del espacio de estados (P1)
    ├── problema1_arbol_estados.png       generación de estados en amplitud
    ├── problema1_solucion_comparada.png  BFS vs Dijkstra vs A*
    ├── problema2_red_fisica.png          red del dron (tiempos asimétricos)
    ├── problema2_espacio_estados.png     34 estados generados
    └── problema2_solucion_optima.png     solución óptima resaltada
```

## Cómo ejecutar

```bash
cd actividad_2.1_2.2_problemas_busqueda/codigo
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py            # genera figuras, resultados y ../resultados_ejecucion.txt
```

> Si ya existe un entorno virtual en la raíz del repositorio, basta con:
> `../../.venv/bin/python main.py`

Módulos independientes (se pueden ejecutar por separado):

```bash
python generador_estados.py   # muestra el generador de estados de ambos problemas
python construir_grafos.py    # sólo construye los grafos y las figuras
python busqueda.py            # sólo ejecuta los algoritmos de búsqueda
```
