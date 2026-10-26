# Actividad 2.4 — Búsqueda ciega (BFS y DFS)

Implementación de **Búsqueda en Amplitud (BFS)** y **Búsqueda en Profundidad (DFS)**
para resolver un **laberinto de 31 × 19 celdas**. Se compara el camino solución,
los nodos expandidos, el tamaño de la frontera y el tiempo de ejecución.

> ✅ **No requiere instalar ninguna librería.** Solo usa la biblioteca estándar
> de Python (3.10 o superior): `collections`, `time`, `dataclasses`, `pathlib` y `typing`.

## 1. Requisitos

- **Python 3.10 o superior** (nada más).
- **No** hace falta `pip install` ni `requirements.txt` (aunque se incluye por
  comodidad y está vacío de dependencias).

## 2. Cómo ejecutar

Abre una terminal dentro de esta carpeta (`codigo/`) y ejecuta:

```bash
python main.py
```

En **Windows** puede ser `py main.py` o `python3 main.py` en Linux/macOS.

### Desde Visual Studio Code

1. Abre la carpeta **`codigo/`** en VS Code (`Archivo → Abrir carpeta`).
2. Abre `main.py`.
3. Pulsa el botón **Run Python File** (▶) o `Ctrl + F5`.
4. También puedes usar la terminal integrada (`Ctrl + Ñ`) y escribir `python main.py`.

## 3. Qué produce

- Resultados en pantalla: laberinto, solución de BFS, solución de DFS y tabla comparativa.
- El archivo **`../resultados_ejecucion_2.4.txt`** con los mismos resultados y los caminos completos.

## 4. Archivos del proyecto

| Archivo | Descripción |
|---|---|
| `laberinto.py` | Define el laberinto (31 × 19), el inicio, la meta, los vecinos y la representación del grafo implícito. |
| `busqueda_ciega.py` | Implementa **BFS** (cola FIFO) y **DFS** (pila LIFO), midiendo nodos expandidos, aristas evaluadas, frontera máxima y tiempo. |
| `main.py` | Ejecuta ambos algoritmos, muestra las soluciones, compara resultados y guarda el informe. |
| `requirements.txt` | Sin dependencias externas (solo informativo). |

## 5. Representación del grafo

- **Nodo:** cada celda transitable (`.`), más el inicio (`S`) y la meta (`E`).
- **Arista:** conexión entre dos celdas adyacentes sin muro (arriba, abajo, izquierda, derecha).
- **Grafo:** no dirigido y **no ponderado** (todas las aristas cuestan 1).

## 6. Complejidad

| Algoritmo | Tiempo | Espacio | ¿Camino óptimo? |
|---|---|---|---|
| **BFS** | O(V + E) | O(V) | Sí |
| **DFS** | O(V + E) | O(V) | No |

donde **V** es el número de celdas transitables y **E** el número de aristas.

## 7. Resultado esperado

Con la instancia incluida:

| Métrica | BFS | DFS |
|---|---|---|
| Celdas del camino | **47** | 85 |
| Nodos expandidos | 214 | **175** |
| Aristas evaluadas | 467 | 382 |
| Frontera máxima | **13** | 19 |
| ¿Camino óptimo? | **Sí** | No |

**Conclusión:** BFS es la mejor opción cuando se necesita la ruta más corta
(laberintos, mapas sin pesos), aunque expanda más nodos. DFS encuentra *alguna*
solución con menos expansiones, pero el camino puede ser mucho más largo
(85 frente a 47 celdas) y no garantiza optimalidad. En esta instancia la
frontera de DFS resultó incluso algo mayor (19 frente a 13), porque apila
todos los vecinos de cada nodo; el ahorro de memoria de DFS solo es claro en
implementaciones recursivas con retroceso sobre árboles, no en búsqueda de
grafos con conjunto de visitados.
