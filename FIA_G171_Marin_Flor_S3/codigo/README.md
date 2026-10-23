# Actividad 2.3 — Búsqueda local (Hill Climbing y Simulated Annealing)

Implementación y optimización de **Hill Cliding** y **Simulated Annealing** para minimizar la longitud total de un recorrido (TSP) con 1 almacén + 20 paradas. Se reportan gráfica de **convergencia**, comparación visual de rutas, análisis estadístico (30 ejecuciones) y comparación de resultados.

## 1. Requisitos
- **Python 3.10 o superior**
- Bibliotecas: **numpy** y **matplotlib** (se instalan con `requirements.txt`)

## 2. Cómo ejecutar

### Opção 1: Terminal dentro de `codigo/`
```bash
# Crear e activar entorno virtual (opcional, pero recomendado)
python -m venv .venv
# Windows
# .venv\Scripts\activate
# Linux / macOS
# source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

### Opção 2: Visual Studio Code
1. Abrir la carpeta **`FIA_G171_Marin_Flor_S3`** (o mejor **`codigo/`** directamente) en VS Code.
2. Abrir la terminal integrada (`Ctrl + Ñ` o `Terminal → New Terminal`).
3. Instalar dependencias: `pip install -r requirements.txt`
4. Abrir `main.py` y pulsar **Run Python File** o ejecutar `python main.py` en la terminal.

## 3. Qué produce
Al terminar la ejecución se generará:

- `../figuras/02_3_convergencia.png` — Gráfica de **convergencia** (mejor costo encontrado)
- `../figuras/02_3_rutas_comparacion.png` — Comparación visual: ruta inicial / Hill Climbing / Simulated Annealing
- `../figuras/02_3_comparacion_estadistica.png` — Boxplot con **30 ejecuciones** independientes
- `../resultados_ejecucion_2.3.txt` — Resultados numéricos detallados (parámetros, mejores costos, media, mediana, desviación típica)

## 4. Archivos del código
| Archivo | Descripción |
|---|---|
| `problema_tsp.py` | Definición del problema, coordenadas, matriz de distancias euclídeas, función objetivo `longitud_ruta()` y rutas iniciales. |
| `busqueda_local.py` | **Hill Climbing** (mejor vecino, exploración con swap + 2-opt) y **Simulated Annealing** (acepta empeoramientos con probabilidad `exp(-Δ/T)`, enfriamiento exponencial). |
| `graficar.py` | Funciones para generar las gráficas con matplotlib. |
| `main.py` | Script principal: ejecuta ambos algoritmos, hace la comparación estadística, genera gráficas y guarda resultados. |
| `requirements.txt` | Dependencias (`numpy`, `matplotlib`). |

## 5. Parámetros utilizados
| Algoritmo | Parámetros |
|---|---|
| **Hill Climbing** | `max_iter=10000`, `max_sin_mejora=150`, vecindad: intercambio + inversión (2-opt) |
| **Simulated Annealing** | `T0=12.0`, `Tf=0.001`, `alpha=0.995`, `iter_por_T=80`, vecindad: intercambio o inversión (aleatorio) |

## 6. Resultado resumido
Con rutas iniciales aleatorias, **Simulated Annealing** resulta más robusto (menor desviación típica) y obtiene mejores resultados en promedio, aunque ambos algoritmos alcanzan soluciones muy cercanas al óptimo encontrado.

## 7. Ejecutar módulos por separado (opcional)
```bash
python problema_tsp.py   # Muestra datos del problema
python busqueda_local.py # Prueba rápida de los algoritmos
```
