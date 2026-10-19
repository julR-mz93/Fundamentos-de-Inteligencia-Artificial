# Código — Actividades 2.1 y 2.2 (Problemas y espacios de búsqueda)

Modelado de dos problemas reales como **problemas de búsqueda**
`P = <S, s0, A, coste, meta>`, representación de cada espacio de estados como
**grafo dirigido y ponderado** (NetworkX) y resolución con los algoritmos
**BFS, Dijkstra y A\***.

Este programa **solo genera archivos nuevos** (figuras y un informe de texto);
no modifica ningún otro archivo.

---

## 1. Requisitos

- **Python 3.10 o superior**
- Librerías: **NetworkX** y **Matplotlib** (se instalan con `requirements.txt`)

## 2. Cómo ejecutar

Abre una terminal **dentro de esta carpeta** (`codigo/`) y ejecuta:

```bash
# (opcional) crear un entorno virtual
python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate

# instalar dependencias
pip install -r requirements.txt

# ejecutar el programa
python main.py
```

> **Sin entorno virtual** también sirve: `pip install networkx matplotlib` y luego `python main.py`.

### Ejecución desde VS Code
1. Abre esta carpeta (`codigo/`) con *Archivo → Abrir carpeta*.
2. Abre la terminal integrada con **Ctrl + Ñ**.
3. Ejecuta `pip install -r requirements.txt` y después `python main.py`.

## 3. Qué produce

Al terminar, el programa crea:

- `../figuras/` — **6 imágenes PNG** con los grafos, el árbol de estados y las soluciones
- `../resultados_ejecucion.txt` — informe con todos los resultados (modelado, grafos, rutas y costes)

> Las salidas se crean **un nivel arriba** de esta carpeta (junto a `codigo/`).
> Eso es normal: no borra ni sobrescribe nada de lo que ya exista con otro nombre.

## 4. Contenido de la carpeta

| Archivo | Descripción |
|---|---|
| `main.py` | Script principal: ejecuta todo el flujo y escribe los resultados |
| `generador_estados.py` | Datos y clases que modelan los problemas (`GeneradorRuteoAmbulancia`, `GeneradorRutaDron`) y la función `explorar_espacio` |
| `construir_grafos.py` | Construcción de los grafos dirigidos y ponderados con NetworkX + dibujo de las figuras |
| `busqueda.py` | Algoritmos propios: BFS, Dijkstra, A\* y verificación por fuerza bruta |
| `requirements.txt` | Dependencias (NetworkX y Matplotlib) |

## 5. Los dos problemas

| | Problema 1 | Problema 2 |
|---|---|---|
| **Descripción** | Ruta de una ambulancia del cuartel al hospital (calles de sentido único) | Ruta de un dron que entrega en 4 puntos y regresa a la base |
| **Estados** | 12 intersecciones (A…L) | `(nodo actual, entregas realizadas)` |
| **Coste** | Minutos de traslado (hora pico) | Minutos de vuelo por tramo (asimétricos) |
| **Meta** | `L` (Hospital General) | `(BASE, {P1,P2,P3,P4})` |
| **Grafo** | Dirigido + ponderado · 12 nodos / 18 aristas | Dirigido + ponderado · 34 estados / 56 transiciones |

### Resultados principales

| Algoritmo | Problema 1 (A → L) | Problema 2 (base → base) |
|---|---|---|
| BFS (amplitud) | 21 min · 5 calles | 26 min |
| Dijkstra | **16 min** (óptimo) | **22 min** (óptimo) |
| A\* | **16 min** (menos estados expandidos) | — |
| Fuerza bruta (4! = 24 órdenes) | — | 22 min → **confirma la optimalidad** |

**Conclusión:** en grafos ponderados, minimizar el número de acciones (BFS) no
garantiza minimizar el coste; Dijkstra y A\* sí encuentran la solución óptima.

## 6. Ejecutar los módulos por separado (opcional)

```bash
python generador_estados.py   # muestra el generador de estados de ambos problemas
python construir_grafos.py    # solo construye los grafos y las figuras
python busqueda.py            # solo ejecuta los algoritmos de búsqueda
```
