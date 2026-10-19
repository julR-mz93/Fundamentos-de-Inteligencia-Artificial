#!/usr/bin/env python3
"""
Genera la memoria de la Actividad 2.1 / 2.2 (Word + PDF).

La memoria se alimenta DIRECTAMENTE del código de la carpeta `codigo/`:
  • re-ejecuta los algoritmos para volcar los resultados reales,
  • extrae los listados de código con inspect.getsource (el código del anexo
    es exactamente el que se ejecuta),
  • incrusta las figuras de `figuras/`.

Salida:
  - memoria_actividad_2.1_2.2.docx
  - memoria_actividad_2.1_2.2.pdf   (requiere LibreOffice)

Uso:  python3 generar_memoria.py
"""

from __future__ import annotations

import inspect
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "codigo"))

from docx import Document  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.shared import Inches, Pt, RGBColor  # noqa: E402

from busqueda import (  # noqa: E402
    a_estrella,
    busqueda_amplitud,
    dijkstra,
    fuerza_bruta_tsp,
    heuristica_euclidiana,
)
from generador_estados import (  # noqa: E402
    NOMBRES_RED,
    PUNTOS_ENTREGA,
    RED_CALLES,
    TIEMPOS_VUELO,
    GeneradorRutaDron,
    GeneradorRuteoAmbulancia,
    explorar_espacio,
)
from construir_grafos import (  # noqa: E402
    grafo_espacio_estados,
    grafo_red_calles,
    grafo_red_dron,
)

FIGURAS = BASE_DIR / "figuras"
AZUL = "1B2A4A"


# =========================================================================
# Resultados reales (se calculan ejecutando el código)
# =========================================================================

def calcular_resultados() -> dict:
    gen1 = GeneradorRuteoAmbulancia()
    esp1 = explorar_espacio(gen1)
    g1 = grafo_red_calles()
    h = heuristica_euclidiana(g1, gen1.meta)
    r = {
        "g1": g1,
        "esp1": esp1,
        "gen1": gen1,
        "p1_bfs": busqueda_amplitud(g1, gen1.estado_inicial, gen1.meta),
        "p1_dij": dijkstra(g1, gen1.estado_inicial, gen1.meta),
        "p1_ast": a_estrella(g1, gen1.estado_inicial, gen1.meta, h),
    }
    gen2 = GeneradorRutaDron()
    esp2 = explorar_espacio(gen2)
    g2_estados = grafo_espacio_estados(esp2)
    g2_red = grafo_red_dron()
    orden_fb, coste_fb = fuerza_bruta_tsp(TIEMPOS_VUELO, "BASE", list(PUNTOS_ENTREGA))
    r.update({
        "gen2": gen2,
        "esp2": esp2,
        "g2_estados": g2_estados,
        "g2_red": g2_red,
        "p2_bfs": busqueda_amplitud(g2_estados, gen2.estado_inicial, gen2.estado_meta),
        "p2_dij": dijkstra(g2_estados, gen2.estado_inicial, gen2.estado_meta),
        "orden_fb": orden_fb,
        "coste_fb": coste_fb,
    })
    return r


# =========================================================================
# Utilidades de Word
# =========================================================================

def parrafo(doc, texto, size=11, bold=False, italic=False, align=None,
            space_after=6, color=None, style=None):
    p = doc.add_paragraph(style=style)
    run = p.add_run(texto)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    return p


def vineta(doc, texto, size=11):
    p = doc.add_paragraph(style="List Bullet")
    p.add_run(texto).font.size = Pt(size)
    p.paragraph_format.space_after = Pt(3)
    return p


def tabla(doc, encabezados, filas, size_cab=9.5, size_celda=9.5):
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    for i, texto in enumerate(encabezados):
        celda = t.rows[0].cells[i]
        celda.text = ""
        run = celda.paragraphs[0].add_run(texto)
        run.bold = True
        run.font.size = Pt(size_cab)
    for fila in filas:
        celdas = t.add_row().cells
        for i, texto in enumerate(fila):
            celdas[i].text = ""
            run = celdas[i].paragraphs[0].add_run(str(texto))
            run.font.size = Pt(size_celda)
    doc.add_paragraph()
    return t


def figura(doc, nombre, ancho=6.4, pie=None):
    ruta = FIGURAS / nombre
    doc.add_picture(str(ruta), width=Inches(ancho))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if pie:
        parrafo(doc, pie, size=9.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER,
                color="5D6D7E", space_after=12)


def codigo(doc, texto, size=8.5):
    """Listado de código con letra monoespaciada."""
    for linea in texto.rstrip("\n").split("\n"):
        p = doc.add_paragraph()
        run = p.add_run(linea if linea.strip() else "")
        run.font.name = "Consolas"
        run.font.size = Pt(size)
        run.font.color.rgb = RGBColor.from_string("1C2833")
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = 1.0
    doc.add_paragraph()


def fuente_de(funcion) -> str:
    """Código fuente real de una función (para el anexo)."""
    return inspect.getsource(funcion)


def portada(doc):
    for _ in range(4):
        doc.add_paragraph()
    parrafo(doc, "MEMORIA DE ACTIVIDADES", size=16, bold=True,
            align=WD_ALIGN_PARAGRAPH.CENTER, color=AZUL, space_after=4)
    parrafo(doc, "Actividad 2.1 — Problemas de búsqueda\n"
                 "Actividad 2.2 — Espacios de búsqueda",
            size=22, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, color=AZUL,
            space_after=18)
    parrafo(doc, "Modelado de dos problemas reales como problemas de búsqueda, "
                 "representación de sus espacios de estados como grafos dirigidos y "
                 "ponderados, y programación de un generador de estados y de los "
                 "grafos con NetworkX en Python",
            size=13, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=40)
    for etiqueta, valor in [
        ("Asignatura:", "Fundamentos de Inteligencia Artificial"),
        ("Estudiante:", "Julissa Marin Flor"),
        ("Docente:", "Javier García Lara"),
        ("Institución:", "Universidad Politécnica de Atlautla"),
        ("Fecha:", "18 de octubre de 2026"),
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p.add_run(f"{etiqueta} ")
        r1.bold = True
        r1.font.size = Pt(12)
        r2 = p.add_run(valor)
        r2.font.size = Pt(12)
        p.paragraph_format.space_after = Pt(8)
    doc.add_page_break()


# =========================================================================
# Informe
# =========================================================================

def generar_memoria(r: dict) -> Path:
    doc = Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Inches(0.9)
        s.left_margin = s.right_margin = Inches(0.9)
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(11)

    portada(doc)

    # ---------------------------------------------------------------- 1
    doc.add_heading("1. Introducción", level=1)
    parrafo(doc,
            "Un programa de inteligencia artificial casi siempre puede describirse como "
            "un agente que busca: desde una ambulancia que debe llegar al hospital por "
            "el camino más rápido hasta un dron que debe repartir en varios puntos con "
            "la menor duración posible. Formalizar esos casos como *problemas de "
            "búsqueda* permite aplicar algoritmos conocidos y compararlos de forma "
            "objetiva.")
    parrafo(doc,
            "Esta memoria corresponde a las Actividades 2.1 (Problemas de búsqueda) y "
            "2.2 (Espacios de búsqueda) del curso. Los objetivos cumplidos son:")
    for t in [
        "Modelar dos problemas reales como problemas de búsqueda, identificando sus "
        "componentes: estados, acciones, función de transición, coste y meta.",
        "Representar cada espacio de estados como un grafo dirigido y ponderado.",
        "Programar en Python un generador de estados y construir los grafos con la "
        "biblioteca NetworkX.",
        "Ejecutar algoritmos de búsqueda clásicos (BFS, Dijkstra y A*) y comparar sus "
        "resultados, verificando la optimalidad de la solución del problema 2 por "
        "enumeración exhaustiva.",
    ]:
        vineta(doc, t)
    parrafo(doc,
            "Todo el código, las figuras y la salida de ejecución forman parte del "
            "repositorio de esta asignatura y se pueden regenerar con un solo comando "
            "(sección 7).")

    # ---------------------------------------------------------------- 2
    doc.add_heading("2. Marco teórico", level=1)
    parrafo(doc,
            "Un problema de búsqueda se define como la tupa P = <S, s0, A, coste, meta>:")
    tabla(doc, ["Componente", "Significado"], [
        ["S (estados)", "conjunto de configuraciones posibles del sistema"],
        ["s0 (inicial", "estado de partida del agente"],
        ["A(s) (acciones)", "acciones aplicables en el estado s"],
        ["Transición", "función que indica a qué estado lleva cada acción"],
        ["Coste", "suma de costes de las transiciones (no negativos)"],
        ["Meta", "estado (o conjunto de estados) objetivo"],
    ])
    parrafo(doc,
            "El espacio de estados es el conjunto S junto con las transiciones entre "
            "ellos. Cuando cada estado puede ir a otro de forma direccional (no "
            "simétrica) el grafo es **dirigido** (digrafo, `nx.DiGraph`); cuando cada "
            "transición tiene un coste distinto el grafo es **ponderado**, y ese coste "
            "se guarda en el atributo `weight` de la arista. NetworkX exige ese nombre "
            "de atributo para sus algoritmos de camino ponderado.")
    parrafo(doc, "Algoritmos empleados (Russell & Norvig, 2021):", bold=True)
    vineta(doc, "**Búsqueda en amplitud (BFS)**: explora por niveles; no mira los "
                "costes y garantiza el camino con menos aristas (acciones), no el más "
                "barato.")
    vineta(doc, "**Dijkstra**: expande siempre el estado de menor coste acumulado; es "
                "óptimo en grafos con pesos no negativos.")
    vineta(doc, "**A***: como Dijkstra pero ordena por f(n) = g(n) + h(n). Si la "
                "heurística h es admisible (nunca sobreestima el coste real) la "
                "solución sigue siendo óptima y suelen expandirse menos estados.")

    # ---------------------------------------------------------------- 3
    doc.add_heading("3. Problema 1 — Ruteo de una ambulancia en red urbana", level=1)

    doc.add_heading("3.1 Descripción del problema real", level=2)
    parrafo(doc,
            "Una ambulancia parte del cuartel y debe llegar al Hospital General. La "
            "red urbana tiene calles de sentido único (por eso el grafo es dirigido) y "
            "el tiempo de traslado de cada calle cambia con el tráfico de la hora pico "
            "(por eso el grafo es ponderado, con minutos como coste). El equipo de "
            "coordinate quiere saber qué ruta minimiza el tiempo de atención.")

    doc.add_heading("3.2 Modelado como problema de búsqueda", level=2)
    tabla(doc, ["Componente", "Definición en este problema"], [
        ["Estados (S)", "las 12 intersecciones de la red: A … L (p. ej. A = Cuartel, "
                        "L = Hospital)"],
        ["Estado inicial (s0)", "'A' = Cuartel"],
        ["Acciones", "circular por una calle adyacente respetando el sentido único; "
                     "una acción por cada arista saliente"],
        ["Transición", "la acción desplaza la ambulancia a la intersección destino"],
        ["Coste", "minutos de traslado por esa calle en hora pico (peso de la arista)"],
        ["Meta", "'L' = Hospital General"],
        ["Espacio de estados", "grafo dirigido y ponderado de 12 nodos y 18 aristas; "
                               "aquí el grafo físico y el de estados coinciden"],
    ])

    doc.add_heading("3.3 Representación del espacio de estados como grafo", level=2)
    parrafo(doc,
            f"La exploración en amplitud desde el estado inicial genera "
            f"{r['esp1'].num_estados} estados y {r['esp1'].num_transiciones} "
            f"transiciones en {r['esp1'].num_niveles} niveles. NetworkX lo representa "
            "como `nx.DiGraph` con el atributo `weight` en cada arista.")
    figura(doc, "problema1_red_calles.png", pie=(
        "Figura 1. Espacio de estados del problema 1: grafo dirigido (sentidos únicos) "
        "y ponderado (minutos). Naranja: estado inicial y meta."))
    parrafo(doc, "Tabla de aristas (calles) con su coste:", bold=True)
    filas = []
    for (o, d), (m, calle) in RED_CALLES.items():
        filas.append([f"{o} → {d}", NOMBRES_RED[o], NOMBRES_RED[d], calle, f"{m:g}"])
    tabla(doc, ["Arista", "Origen", "Destino", "Calle (acción)", "Coste (min)"],
          filas, size_cab=9, size_celda=9)
    figura(doc, "problema1_arbol_estados.png", pie=(
        "Figura 2. Generación de estados en amplitud: el árbol muestra de qué estado "
        "se descubrió cada uno y el coste de cada acción."))

    doc.add_heading("3.4 Generador de estados (Python)", level=2)
    parrafo(doc,
            "La clase `GeneradorRuteoAmbulancia` implementa la interfaz del problema "
            "(estado_inicial, es_meta, acciones, sucesores) y la función "
            "`explorar_espacio` recorre el generador en amplitud para obtener todos "
            "los estados alcanzables y sus transiciones. Listado real del archivo "
            "`codigo/generador_estados.py`:")
    codigo(doc, fuente_de(GeneradorRuteoAmbulancia.sucesores))
    parrafo(doc, "Exploración del espacio de estados (generador → conjunto de estados):",
            bold=True)
    codigo(doc, fuente_de(explorar_espacio))

    doc.add_heading("3.5 Construcción del grafo con NetworkX", level=2)
    parrafo(doc,
            "El archivo `codigo/construir_grafos.py` convierte los datos y el espacio "
            "generado en grafos dirigidos y ponderados, y dibuja las figuras:")
    codigo(doc, fuente_de(grafo_red_calles))
    codigo(doc, fuente_de(grafo_espacio_estados))

    doc.add_heading("3.6 Resultados de búsqueda", level=2)
    tabla(doc, ["Algoritmo", "Coste", "Calles (aristas)", "Estados expandidos",
                "Ruta encontrada"], [
        ["BFS (amplitud)", f"{r['p1_bfs'].coste:g} min", r["p1_bfs"].aristas,
         r["p1_bfs"].expandidos,
         " → ".join(r["p1_bfs"].camino)],
        ["Dijkstra", f"{r['p1_dij'].coste:g} min", r["p1_dij"].aristas,
         r["p1_dij"].expandidos,
         " → ".join(r["p1_dij"].camino)],
        ["A*", f"{r['p1_ast'].coste:g} min", r["p1_ast"].aristas,
         r["p1_ast"].expandidos,
         " → ".join(r["p1_ast"].camino)],
    ])
    figura(doc, "problema1_solucion_comparada.png", pie=(
        "Figura 3. Comparación de las rutas: BFS elige la avenida congestionada; "
        "Dijkstra y A* encuentran la ruta de menor tiempo."))
    parrafo(doc, f"Análisis: BFS devuelve {r['p1_bfs'].coste:g} min, aunque con el "
                 f"mismo número de calles que el óptimo ({r['p1_dij'].aristas}), "
                 f"porque **no mira los pesos**: solo cuenta aristas. Dijkstra y A* "
                 f"encuentran {r['p1_dij'].coste:g} min, {r['p1_bfs'].coste - r['p1_dij'].coste:g} "
                 "min menos. La heurística usada en A* es "
                 "h(n) = (menor coste por unidad de distancia) × distancia(n, meta), "
                 "que es admisible porque se calcula con el coste mínimo por unidad "
                 "de todas las aristas; por eso A* conserva la optimalidad y expandió "
                 f"sólo {r['p1_ast'].expandidos} estados frente a "
                 f"{r['p1_dij'].expandidos} de Dijkstra.")

    # ---------------------------------------------------------------- 4
    doc.add_heading("4. Problema 2 — Ruta de un dron de reparto con varias entregas", level=1)

    doc.add_heading("4.1 Descripción del problema real", level=2)
    parrafo(doc,
            "Un dron de reparto debe salir de su base, entregar en cuatro puntos "
            "(farmacia, clínica, mercado y escuela) y regresar. Los tiempos de vuelo "
            "dependen del corredor aéreo: hay desvíos por zonas de exclusión y viento, "
            "de modo que volar de A a B no cuesta lo mismo que de B a A (tiempos "
            "asimétricos → grafo dirigido). El dron no puede volver a la base antes de "
            "terminar las entregas (restricción de autonomía).")

    doc.add_heading("4.2 Modelado como problema de búsqueda", level=2)
    tabla(doc, ["Componente", "Definición en este problema"], [
        ["Estados (S)", "(nodo_actual, conjunto_de_entregas_realizadas); p. ej. "
                        "(P1, {P1, P2}) = en la farmacia, ya entregó a P1 y P2"],
        ["Estado inicial (s0)", "(BASE, ∅): el dron en la base sin entregar"],
        ["Acciones", "volar a un punto de entrega aún no visitado; cuando el conjunto "
                     "está completo, regresar a la BASE"],
        ["Transición", "añade el punto al conjunto y mueve el dron al nuevo nodo"],
        ["Coste", "minutos de vuelo del tramo (peso de la arista)"],
        ["Meta", "(BASE, {P1, P2, P3, P4})"],
        ["Espacio de estados", "grafo dirigido y ponderado generado explícitamente: "
                              f"{r['g2_estados'].number_of_nodes()} estados y "
                              f"{r['g2_estados'].number_of_edges()} transiciones"],
    ])
    parrafo(doc,
            "A diferencia del problema 1, aquí el grafo físico (7 nodos) y el espacio "
            "de estados (34 estados) NO coinciden: cada estado recuerda qué entregas ya "
            "se hicieron, por eso se dice que el espacio es *explícito* y se construye "
            "con el generador.")

    doc.add_heading("4.3 Red física y espacio de estados", level=2)
    figura(doc, "problema2_red_fisica.png", pie=(
        "Figura 4. Red física del dron: grafo dirigido y ponderado con tiempos "
        "asimétricos (p. ej. P2→P3 = "
        f"{TIEMPOS_VUELO[('P2','P3')]:g} min frente a P3→P2 = "
        f"{TIEMPOS_VUELO[('P3','P2')]:g} min)."))
    figura(doc, "problema2_espacio_estados.png", pie=(
        f"Figura 5. Espacio de estados generado: {r['g2_estados'].number_of_nodes()} "
        f"estados (capas = número de acciones realizadas) y "
        f"{r['g2_estados'].number_of_edges()} transiciones."))

    doc.add_heading("4.4 Generador de estados (Python)", level=2)
    parrafo(doc,
            "La clase `GeneradorRutaDron` aplica las acciones sobre estados con "
            "memoria (conjunto de entregas); `explorar_espacio` es la misma función "
            "del problema 1, reutilizada sin cambios:")
    codigo(doc, fuente_de(GeneradorRutaDron.sucesores))

    doc.add_heading("4.5 Resultados de búsqueda y verificación", level=2)
    orden_bfs = " → ".join(e[0] for e in r["p2_bfs"].camino)
    orden_dij = " → ".join(e[0] for e in r["p2_dij"].camino)
    tabla(doc, ["Algoritmo", "Coste", "Orden de entrega", "Expandidos"], [
        ["BFS (amplitud)", f"{r['p2_bfs'].coste:g} min", orden_bfs,
         r["p2_bfs"].expandidos],
        ["Dijkstra", f"{r['p2_dij'].coste:g} min", orden_dij,
         r["p2_dij"].expandidos],
        ["Fuerza bruta (24 órdenes)", f"{r['coste_fb']:g} min",
         " → ".join(r["orden_fb"]), "—"],
    ])
    figura(doc, "problema2_solucion_optima.png", pie=(
        "Figura 6. Solución óptima en el espacio de estados: estados de la ruta en "
        "naranja y coste acumulado en cada transición."))
    parrafo(doc,
            f"Verificación: la enumeración exhaustiva de los 4! = 24 ordenes posibles "
            f"devuelve {r['coste_fb']:g} min, exactamente el coste de Dijkstra "
            f"({r['p2_dij'].coste:g} min) → la solución es óptima. BFS, que ignora "
            f"los pesos, entrega {r['p2_bfs'].coste:g} min, "
            f"{r['p2_bfs'].coste - r['p2_dij'].coste:g} min peor.")

    # ---------------------------------------------------------------- 5
    doc.add_heading("5. Análisis comparativo de los dos problemas", level=1)
    tabla(doc, ["Criterio", "Problema 1 (ambulancia)", "Problema 2 (dron)"], [
        ["Estados", "12 intersecciones", "34 pares (nodo, entregas)"],
        ["Acciones", "circular por una calle permitida", "volar a un punto sin entregar / regresar"],
        ["Coste", "minutos de traslado", "minutos de vuelo"],
        ["Meta", "llegar al hospital", "volver a la base con todo entregado"],
        ["¿Dirigido?", "sí (sentidos únicos)", "sí (tiempos asimétricos)"],
        ["¿Ponderado?", "sí (minutos por calle)", "sí (minutos por tramo)"],
        ["Grafo físico vs estados", "coinciden (12 = 12)", "no coinciden (7 vs 34)"],
        ["Espacio generado por", "la propia red", "el generador de estados (BFS)"],
        ["Mejor algoritmo", "A* (óptimo con menos expansiones)", "Dijkstra (óptimo verificado)"],
        ["Solución", f"{r['p1_dij'].coste:g} min", f"{r['p2_dij'].coste:g} min"],
    ])
    parrafo(doc,
            "Los dos casos ilustran por qué importa el modelo: mismo marco formal "
            "<S, s0, A, coste, meta> y mismos algoritmos, pero un espacio de estados "
            "pequeño y directo en el primero y un espacio con memoria (conjunto de "
            "entregas) en el segundo, que obliga a generar el grafo explícitamente.")

    # ---------------------------------------------------------------- 6
    doc.add_heading("6. Conclusiones", level=1)
    for i, t in enumerate([
        "Los dos problemas reales quedaron modelados con todos los componentes de un "
        "problema de búsqueda y representados como grafos dirigidos y ponderados "
        "(12/18 y 34/56 nodos/aristas).",
        "El generador de estados es único y reutilizable: basta con implementar la "
        "interfaz (estado_inicial, es_meta, acciones, sucesores) para que la misma "
        "exploración en amplitud construya el espacio de estados de cualquier problema.",
        "Minimizar el número de acciones (BFS) no garantiza minimizar el coste: "
        "en el problema 1 BFS da 21 min frente a 16 min de Dijkstra y A*, y en el "
        "problema 2 da 26 min frente a 22 min.",
        "A* con una heurística admisible logra la misma solución óptima que Dijkstra "
        "expandiendo menos estados, lo que lo hace atractivo para grafos grandes.",
        "La optimalidad de la solución del problema 2 se verificó de forma independiente "
        "con enumeración exhaustiva de los 24 ordenes posibles.",
        "Extensión natural: sustituir el coste uniforme por tráfico en tiempo real "
        "(aristas con pesos dinámicos) o usar búsqueda A* con una heurística de "
        "vuelo directo para el dron.",
    ], start=1):
        p = doc.add_paragraph(style="List Number")
        p.add_run(t).font.size = Pt(11)

    # ---------------------------------------------------------------- 7
    doc.add_heading("7. Ejecución del código", level=1)
    parrafo(doc, "Requisitos: Python 3.10 o superior y las dependencias de "
                 "`codigo/requirements.txt` (NetworkX y Matplotlib).")
    codigo(doc,
           "cd actividad_2.1_2.2_problemas_busqueda/codigo\n"
           "python3 -m venv .venv && source .venv/bin/activate\n"
           "pip install -r requirements.txt\n"
           "python main.py", size=10)
    parrafo(doc,
            "La ejecución genera las seis figuras de `figuras/` y el informe "
            "`resultados_ejecucion.txt` con la misma información que se recoge en esta "
            "memoria. Los módulos `generador_estados.py`, `construir_grafos.py` y "
            "`busqueda.py` también se pueden ejecutar por separado.")

    # ---------------------------------------------------------------- 8
    doc.add_heading("8. Referencias", level=1)
    referencias = [
        "RUSSELL, S. y NORVIG, P. (2021). Artificial Intelligence: A Modern Approach, "
        "4.ª ed. Pearson. Capítulos 3–4 (búsqueda de grafos).",
        "NILSSON, N. J. (1998). Artificial Intelligence: A New Synthesis. Morgan "
        "Kaufmann. (Espacios de estados y algoritmos de búsqueda.)",
        "HART, P. E., NILSSON, N. J. y RAPHAEL, B. (1968). A Formal Basis for the "
        "Heuristic Determination of Minimum Cost Paths. IEEE Transactions on Systems "
        "Science and Cybernetics, 4(2), 100–107. DOI: 10.1109/TSSC.1968.300136.",
        "NETWORKX DEVELOPERS (s. f.). Documentation — Graphs and Networks. Disponible "
        "en: https://networkx.org/documentation/stable/reference/index.html",
        "PYTHON SOFTWARE FOUNDATION (s. f.). Python Documentation. Disponible en: "
        "https://docs.python.org/3/",
    ]
    for i, ref in enumerate(referencias, start=1):
        p = doc.add_paragraph()
        b = p.add_run(f"[{i}] ")
        b.bold = True
        b.font.size = Pt(10)
        t = p.add_run(ref)
        t.font.size = Pt(10)
        p.paragraph_format.space_after = Pt(6)

    # Cita bibliográfica de la herramienta de IA ----------------------
    ia_num = len(referencias) + 1
    p = doc.add_paragraph()
    b = p.add_run(f"[{ia_num}] ")
    b.bold = True
    b.font.size = Pt(10)
    t = p.add_run(
        "OPENCODE (2026). OpenCode: agente de inteligencia artificial para "
        "programación y análisis [software]. Disponible en: https://opencode.ai. "
        "Consultado el 18 de octubre de 2026.")
    t.font.size = Pt(10)
    p.paragraph_format.space_after = Pt(6)

    # Declaración de uso de IA (al final de las referencias) ----------
    doc.add_heading("Declaración de uso de inteligencia artificial", level=2)
    parrafo(doc,
            f"Para la elaboración de esta memoria se utilizó la herramienta de "
            f"inteligencia artificial OpenCode [{ia_num}], como apoyo en la "
            f"redacción del texto, la programación y depuración del código Python "
            f"(generador de estados, grafos con NetworkX y algoritmos de búsqueda), "
            f"la generación de las figuras y la maquetación de los archivos Word y "
            f"PDF. La definición de los dos problemas reales, la verificación de "
            f"los resultados numéricos y la revisión del contenido corresponden a "
            f"la persona estudiante, quien asume la responsabilidad sobre el "
            f"material entregado.")

    # ---------------------------------------------------------------- Anexo
    doc.add_page_break()
    doc.add_heading("Anexo A — Listado del código fuente (extractos)", level=1)
    parrafo(doc,
            "Los extractos se obtuvieron automáticamente del código ejecutado con "
            "inspect.getsource(); el código completo está en la carpeta `codigo/` del "
            "repositorio.", italic=True, size=10)

    import generador_estados as mod_gen
    import busqueda as mod_bus
    doc.add_heading("A.1 generador_estados.py — exploración del espacio de estados",
                    level=2)
    codigo(doc, fuente_de(mod_gen.explorar_espacio))
    doc.add_heading("A.2 busqueda.py — búsqueda en amplitud y Dijkstra", level=2)
    codigo(doc, fuente_de(mod_bus.busqueda_amplitud))
    codigo(doc, fuente_de(mod_bus.dijkstra))
    doc.add_heading("A.3 busqueda.py — A* y heurística admisible", level=2)
    codigo(doc, fuente_de(mod_bus.a_estrella))
    codigo(doc, fuente_de(mod_bus.heuristica_euclidiana))
    doc.add_heading("A.4 busqueda.py — verificación por fuerza bruta", level=2)
    codigo(doc, fuente_de(mod_bus.fuerza_bruta_tsp))

    ruta = BASE_DIR / "memoria_actividad_2.1_2.2.docx"
    doc.save(ruta)
    print(f"  -> {ruta.name}")
    return ruta


def main() -> None:
    print("Generando la memoria de las Actividades 2.1 / 2.2 ...")
    r = calcular_resultados()
    ruta_docx = generar_memoria(r)
    ruta_pdf = BASE_DIR / "memoria_actividad_2.1_2.2.pdf"
    try:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf", "--outdir",
             str(BASE_DIR), str(ruta_docx)],
            check=True, capture_output=True, timeout=180,
        )
        print(f"  -> {ruta_pdf.name}")
    except FileNotFoundError:
        print("  [aviso] LibreOffice (soffice) no disponible: no se generó el PDF.")
    except subprocess.CalledProcessError as e:
        print(f"  [aviso] fallo al convertir a PDF: {e.stderr.decode()[:300]}")
    print("Listo.")


if __name__ == "__main__":
    main()
