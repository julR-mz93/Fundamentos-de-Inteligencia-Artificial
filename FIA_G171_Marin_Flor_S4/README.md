# Actividad 2.4 — Búsqueda ciega (BFS y DFS)

**Alumno:** Julissa Marin Flor  
**Asignatura:** Fundamentos de Inteligencia Artificial  
**Docente:** Javier García Lara  
**Institución:** Universidad Politécnica de Atlautla  
**Grupo:** G171  
**Fecha:** 25 de octubre de 2026

## Objetivo

Implementar y comparar **Búsqueda en Amplitud (BFS)** y **Búsqueda en
Profundidad (DFS)** para resolver un laberinto de **31 × 19 celdas** modelado
como un grafo no dirigido y no ponderado. La comparación incluye el camino
solución, los nodos expandidos, las aristas evaluadas, el tamaño de la frontera
y el tiempo de ejecución.

## Estructura de la entrega

```
FIA_G171_Marin_Flor_S4/
├── FIA_G171_MARIN_FLOR_S4.pdf    # Memoria final (entrega)
├── FIA_G171_MARIN_FLOR_S4.docx   # Versión editable de la memoria
├── generar_memoria_2.4.py        # Genera el DOCX y el PDF
├── graficos_24.py                # Genera las figuras de la memoria
├── docx_util.py                  # Utilidades de maquetación del DOCX
├── resultados_ejecucion_2.4.txt  # Salida de codigo/main.py
├── codigo/                       # Código entregable (solo stdlib)
│   ├── laberinto.py
│   ├── busqueda_ciega.py
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
└── figuras/                      # Figuras usadas en la memoria
```

## Lo que contiene la memoria

- [x] Portada con datos del estudiante
- [x] Introducción y objetivos
- [x] Representación del laberinto como grafo
- [x] BFS: estrategia, pseudocódigo y propiedades
- [x] DFS: estrategia, pseudocódigo y propiedades
- [x] Implementación en Python y ejecución sin dependencias
- [x] Caminos solución de BFS y DFS
- [x] Mapas de exploración y evolución de la frontera
- [x] Tabla comparativa: camino, nodos, aristas, frontera y tiempo
- [x] Análisis de complejidad e idoneidad según el problema
- [x] Conclusiones, referencias y declaración de uso de IA
- [x] Anexo con el código completo

## Ejecución rápida (sin instalar nada)

```bash
cd codigo
python main.py
```

Solo requiere **Python 3.10 o superior**. No hace falta `pip install`: el
código usa únicamente la biblioteca estándar (`collections`, `time`,
`dataclasses`, `pathlib` y `typing`).

En Visual Studio Code: abrir la carpeta `codigo/`, abrir `main.py` y pulsar
**Run Python File** (▶) o `Ctrl + F5`.

## Resultados destacados

| Métrica | BFS | DFS |
|---|---|---|
| Celdas del camino | **47** | 85 |
| Movimientos | **46** | 84 |
| Nodos expandidos | 214 | **175** |
| Aristas evaluadas | 467 | 382 |
| Frontera máxima | **13** | 19 |
| ¿Camino óptimo? | **Sí** | No |

**Conclusión:** BFS garantiza la ruta más corta y es la opción adecuada para
laberintos y mapas sin pesos. DFS expande menos nodos y evalúa menos aristas,
pero devuelve un camino aproximadamente un **81 % más largo** y no garantiza
optimalidad. En esta instancia, la frontera de DFS fue incluso mayor que la de
BFS, porque apila todos los vecinos de cada nodo; el ahorro de memoria de DFS
solo es claro en implementaciones recursivas con retroceso sobre árboles.

## Regenerar la memoria (opcional)

El documento se puede reconstruir con:

```bash
python generar_memoria_2.4.py
```

Este script sí requiere `matplotlib` y `python-docx`, además de LibreOffice
(`soffice`) para exportar el PDF. Esas dependencias son solo para elaborar el
documento; **el código de la carpeta `codigo/` no las usa**.

## Referencias principales

- Russell, S. y Norvig, P. (2021). *Artificial Intelligence: A Modern Approach* (4.ª ed.). Pearson.
- Cormen, T. H. et al. (2009). *Introduction to Algorithms* (3.ª ed.). MIT Press.
- Sedgewick, R. y Wayne, K. (2011). *Algorithms* (4.ª ed.). Addison-Wesley.
- Python Software Foundation. *Python Documentation*. https://docs.python.org/3/
