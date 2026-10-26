#!/usr/bin/env python3
"""
Genera la memoria de la Actividad 2.4 (DOCX + PDF).

Uso:
    python generar_memoria_2.4.py

El código entregable de la carpeta codigo/ solo usa la biblioteca estándar.
Este script, en cambio, usa matplotlib y python-docx para producir el documento.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Inches, Pt

BASE_DIR = Path(__file__).resolve().parent
CODIGO_DIR = BASE_DIR / "codigo"
FIGURAS_DIR = BASE_DIR / "figuras"
sys.path.insert(0, str(CODIGO_DIR))

from busqueda_ciega import bfs, dfs  # noqa: E402
from laberinto import COLUMNAS, FILAS, INICIO, LABERINTO, META  # noqa: E402

from docx_util import (  # noqa: E402
    BLUE,
    BLUE_BG,
    BORDER,
    BODY_FONT,
    GOLD,
    GRAY,
    GREEN,
    NAVY,
    ORANGE,
    ORANGE_BG,
    PAGE_WIDTH_CM,
    RED,
    TITLE_FONT,
    WHITE,
    _aplicar_fuente,
    anchos_tabla,
    bloque_codigo,
    bordes_tabla,
    callout,
    configurar_estilos,
    configurar_seccion,
    espaciado_letras,
    figura,
    linea_horizontal,
    margenes_celda,
    metadatos,
    numerada,
    rgb,
    sombreado_celda,
    tabla_bonita,
    texto,
    vineta,
)

CENTER = WD_ALIGN_PARAGRAPH.CENTER
JUSTIFY = WD_ALIGN_PARAGRAPH.JUSTIFY
LEFT = WD_ALIGN_PARAGRAPH.LEFT


# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------
def leer_resultados() -> dict[str, tuple[str, str]]:
    datos: dict[str, tuple[str, str]] = {}
    ruta = BASE_DIR / "resultados_ejecucion_2.4.txt"
    if not ruta.exists():
        return datos
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        partes = linea.split(";")
        if len(partes) == 3:
            datos[partes[0].strip()] = (partes[1].strip(), partes[2].strip())
    return datos


def valores() -> dict:
    d = leer_resultados()
    try:
        t_bfs = float(d["Tiempo medio (ms)"][0].replace(",", "."))
        t_dfs = float(d["Tiempo medio (ms)"][1].replace(",", "."))
    except (KeyError, ValueError):
        from busqueda_ciega import medir_tiempo_promedio

        t_bfs = medir_tiempo_promedio(bfs) * 1000
        t_dfs = medir_tiempo_promedio(dfs) * 1000

    r_bfs = bfs()
    r_dfs = dfs()
    V = sum(1 for fila in LABERINTO for c in fila if c != "#")
    E = 0
    for f in range(FILAS):
        for c in range(COLUMNAS):
            if LABERINTO[f][c] == "#":
                continue
            if c + 1 < COLUMNAS and LABERINTO[f][c + 1] != "#":
                E += 1
            if f + 1 < FILAS and LABERINTO[f + 1][c] != "#":
                E += 1
    return {
        "bfs": r_bfs,
        "dfs": r_dfs,
        "t_bfs": t_bfs,
        "t_dfs": t_dfs,
        "V": V,
        "E": E,
        "muros": FILAS * COLUMNAS - V,
        "celdas": FILAS * COLUMNAS,
        "grado": 2 * E / V,
    }


# ---------------------------------------------------------------------------
# Portada
# ---------------------------------------------------------------------------
def _parrafo_panel(cell, txt: str, size: float, color: str,
                   bold: bool = False, space_after: float = 2,
                   space_before: float = 0, spacing: int = 0):
    p = cell.add_paragraph()
    p.alignment = CENTER
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(txt)
    _aplicar_fuente(r, TITLE_FONT, size, color, bold=bold)
    if spacing:
        espaciado_letras(r, spacing)
    return p


def portada(doc: Document) -> None:
    # Panel superior azul marino
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    bordes_tabla(table, outside=False, inside_h=False, inside_v=False)
    anchos_tabla(table, [PAGE_WIDTH_CM])
    cell = table.rows[0].cells[0]
    sombreado_celda(cell, NAVY)
    margenes_celda(cell, top=360, bottom=360, left=260, right=260)
    cell.text = ""

    p0 = cell.paragraphs[0]
    p0.alignment = CENTER
    p0.paragraph_format.space_after = Pt(4)
    r0 = p0.add_run("UNIVERSIDAD POLITÉCNICA DE ATLAUTLA")
    _aplicar_fuente(r0, TITLE_FONT, 9, "C3D7E8", bold=True)
    espaciado_letras(r0, 30)

    _parrafo_panel(cell, "FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL",
                   8.5, "8FB3CC", space_after=18)
    _parrafo_panel(cell, "BÚSQUEDA CIEGA", 33, WHITE, bold=True,
                   space_after=4)
    _parrafo_panel(cell, "BFS y DFS para resolver un laberinto",
                   13.5, GOLD, space_after=14)
    _parrafo_panel(cell, "ACTIVIDAD 2.4", 9.5, GOLD, bold=True,
                   space_after=0, spacing=40)

    linea_horizontal(doc, GOLD, sz=14, space_before=2)
    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(8)

    # Tarjeta de datos
    filas = [
        ("ASIGNATURA", "Fundamentos de Inteligencia Artificial"),
        ("ESTUDIANTE", "Julissa Marin Flor"),
        ("DOCENTE", "Javier García Lara"),
        ("GRUPO", "G171"),
        ("INSTITUCIÓN", "Universidad Politécnica de Atlautla"),
        ("FECHA", "25 de octubre de 2026"),
    ]
    t = doc.add_table(rows=0, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    bordes_tabla(t, color=BORDER, sz=4, outside=False,
                 inside_h=True, inside_v=False)
    anchos_tabla(t, [4.3, 12.3])
    for etiqueta, valor in filas:
        cells = t.add_row().cells
        c0, c1 = cells
        sombreado_celda(c0, "EEF3F8")
        margenes_celda(c0, top=90, bottom=90, left=150, right=90)
        margenes_celda(c1, top=90, bottom=90, left=170, right=90)
        c0.text = ""
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        p0.paragraph_format.line_spacing = 1.0
        r0 = p0.add_run(etiqueta)
        _aplicar_fuente(r0, TITLE_FONT, 8, "55708D", bold=True)
        espaciado_letras(r0, 15)
        c0.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        c1.text = ""
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.line_spacing = 1.0
        r1 = p1.add_run(valor)
        _aplicar_fuente(r1, BODY_FONT, 10.5, NAVY, bold=True)
        c1.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(4)

    # Imagen decorativa
    doc.add_picture(str(FIGURAS_DIR / "00_portada.png"), width=Inches(5.5))
    pimg = doc.paragraphs[-1]
    pimg.alignment = CENTER
    pimg.paragraph_format.space_before = Pt(2)
    pimg.paragraph_format.space_after = Pt(6)

    texto(
        doc,
        "«Elegir un algoritmo es elegir qué precio estamos dispuestos a pagar: "
        "BFS paga memoria para garantizar el camino más corto; DFS paga calidad "
        "para explorar con menos nodos.»",
        size=9.2, italic=True, color=GRAY, align=CENTER, space_after=0,
    )
    doc.add_page_break()


# ---------------------------------------------------------------------------
# Contenido
# ---------------------------------------------------------------------------
def contenido(doc: Document) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Contenido")
    _aplicar_fuente(r, TITLE_FONT, 26, NAVY, bold=True)
    linea_horizontal(doc, GOLD, sz=12)
    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(6)

    items = [
        ("01", "Introducción y objetivo",
         "Contexto, enunciado y alcance de la actividad."),
        ("02", "Representación del problema",
         "Del laberinto al grafo: nodos, aristas y complejidad."),
        ("03", "Búsqueda en amplitud (BFS)",
         "Estrategia, pseudocódigo y propiedades."),
        ("04", "Búsqueda en profundidad (DFS)",
         "Estrategia, pseudocódigo y propiedades."),
        ("05", "Implementación en Python",
         "Estructura del proyecto y ejecución sin dependencias."),
        ("06", "Resultados experimentales",
         "Caminos solución, nodos expandidos y evolución de la frontera."),
        ("07", "Análisis comparativo",
         "Tiempo, nodos expandidos y calidad de la solución."),
        ("08", "Complejidad e idoneidad",
         "Coste temporal y espacial; elección según el problema."),
        ("09", "Conclusiones",
         "Hallazgos principales y recomendaciones."),
        ("10", "Referencias y declaración de IA",
         "Fuentes consultadas y uso de herramientas de IA."),
        ("A", "Anexo A — Código completo",
         "Listado íntegro de los archivos de la carpeta codigo/."),
    ]

    t = doc.add_table(rows=0, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    bordes_tabla(t, color="E3EAF1", sz=4, outside=False,
                 inside_h=True, inside_v=False)
    anchos_tabla(t, [1.7, 14.9])
    for num, titulo, desc in items:
        cells = t.add_row().cells
        c0, c1 = cells
        margenes_celda(c0, top=95, bottom=95, left=90, right=40)
        margenes_celda(c1, top=95, bottom=95, left=60, right=90)
        c0.text = ""
        p0 = c0.paragraphs[0]
        p0.alignment = CENTER
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(num)
        _aplicar_fuente(r0, TITLE_FONT, 15, "AFC7DF", bold=True)

        c1.text = ""
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(1)
        p1.paragraph_format.line_spacing = 1.0
        r1 = p1.add_run(titulo)
        _aplicar_fuente(r1, TITLE_FONT, 10.5, NAVY, bold=True)

        p2 = c1.add_paragraph()
        p2.paragraph_format.space_after = Pt(0)
        p2.paragraph_format.line_spacing = 1.0
        r2 = p2.add_run(desc)
        _aplicar_fuente(r2, BODY_FONT, 8.8, GRAY)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(8)
    callout(
        doc,
        "Cómo leer este documento",
        "Las figuras y tablas están numeradas en orden de aparición. Los "
        "resultados numéricos provienen de ejecutar codigo/main.py; el anexo "
        "incluye el código completo y cada archivo puede abrirse directamente "
        "en Visual Studio Code.",
        color=BLUE, fondo=BLUE_BG,
    )
    doc.add_page_break()


# ---------------------------------------------------------------------------
# Secciones 1 a 5
# ---------------------------------------------------------------------------
def seccion_1(doc: Document, v: dict) -> None:
    doc.add_heading("1. Introducción y objetivo", level=1)
    texto(
        doc,
        "La búsqueda no informada, también llamada búsqueda ciega, resuelve "
        "problemas explorando el espacio de estados sin utilizar conocimiento "
        "adicional sobre cuál estado es más prometedor. Los dos algoritmos "
        "clásicos de esta familia son la búsqueda en amplitud (Breadth-First "
        "Search, BFS) y la búsqueda en profundidad (Depth-First Search, DFS). "
        "Ambos comparten la representación del problema, pero difieren en el "
        "orden en que exploran los nodos y, por tanto, en la calidad de la "
        "solución y en el uso de memoria.",
    )
    texto(
        doc,
        "En esta actividad se implementan BFS y DFS en Python para resolver un "
        f"laberinto de {COLUMNAS} × {FILAS} celdas. El laberinto se modela como "
        "un grafo no dirigido y no ponderado, y el objetivo es encontrar un "
        "camino desde la celda de inicio S hasta la salida E. Además de obtener "
        "la solución, se comparan los algoritmos en términos de camino, nodos "
        "expandidos, aristas evaluadas, tamaño de la frontera y tiempo de "
        "ejecución.",
    )
    texto(
        doc,
        "Objetivo general: implementar y comparar BFS y DFS sobre una misma "
        "instancia, identificando en qué situaciones conviene cada uno.",
        bold=True, space_after=4,
    )
    vineta(doc, "el laberinto como un grafo implícito no ponderado;",
           "Representar: ")
    vineta(doc, "ambos algoritmos con la biblioteca estándar de Python, "
                "sin dependencias externas;", "Implementar: ")
    vineta(doc, "obtener el camino solución, los nodos expandidos, las aristas "
                "evaluadas, la frontera máxima y el tiempo;", "Medir: ")
    vineta(doc, "la complejidad temporal y espacial y emitir una "
                "conclusión sobre la idoneidad de cada algoritmo.",
           "Analizar: ")
    callout(
        doc,
        "Un detalle importante",
        "El código de la carpeta codigo/ no requiere instalar librerías: se "
        "ejecuta con Python 3.10 o superior usando solo la biblioteca estándar. "
        "Las dependencias de este generador (matplotlib y python-docx) se usan "
        "únicamente para elaborar el documento.",
        color=GREEN, fondo="EAF6EF",
    )


def seccion_2(doc: Document, v: dict) -> None:
    doc.add_heading("2. Representación del problema", level=1)
    doc.add_heading("2.1. El laberinto", level=2)
    texto(
        doc,
        f"La instancia es un laberinto de {COLUMNAS} columnas por {FILAS} filas: "
        f"{v['celdas']} celdas en total, de las cuales {v['V']} son transitables "
        f"y {v['muros']} son muros. El inicio está en la celda "
        f"{INICIO} (fila, columna) y la meta en {META}. La Figura 1 muestra el "
        "laberinto completo, con S en verde y E en rojo.",
    )
    figura(doc, FIGURAS_DIR / "01_laberinto.png",
           "Figura 1. Laberinto 31 × 19 utilizado en la actividad.", 6.25)

    doc.add_heading("2.2. Del laberinto al grafo", level=2)
    texto(
        doc,
        "Para aplicar algoritmos de búsqueda, el laberinto se transforma en un "
        "grafo G = (V, E) de la siguiente manera:",
    )
    vineta(doc, "cada celda transitable (incluidas S y E) es un nodo del grafo;",
           "Nodo: ")
    vineta(doc, "dos celdas adyacentes en horizontal o vertical, sin muro entre "
                "ellas, están unidas por una arista;", "Arista: ")
    vineta(doc, "todas las aristas cuestan lo mismo (1 movimiento), por lo que el "
                "grafo es no ponderado y no dirigido.", "Peso: ")
    texto(
        doc,
        f"Con estos datos, el grafo tiene V = {v['V']} nodos y E = {v['E']} "
        f"aristas. El grado medio es 2E/V ≈ {v['grado']:.2f} y el grado máximo es "
        "4, porque cada celda tiene como mucho cuatro vecinos. El grafo no se "
        "almacena en memoria: se genera de forma implícita a partir de la matriz "
        "del laberinto mediante la función vecinos(). La Figura 2 ilustra la "
        "correspondencia entre celdas y nodos.",
    )
    figura(doc, FIGURAS_DIR / "08_grafo.png",
           "Figura 2. El laberinto como grafo: celdas = nodos, pasos = aristas.",
           4.45)

    doc.add_heading("2.3. Un laberinto con bucles", level=2)
    texto(
        doc,
        "La instancia se generó deliberadamente con bucles, es decir, con varios "
        "caminos posibles entre S y E. Si el laberinto fuera perfecto (un único "
        "camino), BFS y DFS encontrarían exactamente la misma ruta y la "
        "diferencia de optimalidad quedaría oculta. Al abrir algunos muros se "
        "crean rutas alternativas: BFS devuelve la más corta y DFS puede devolver "
        "una más larga, que es precisamente lo que se quiere comparar.",
    )
    callout(
        doc,
        "El problema de búsqueda",
        "Estado inicial: S = (1, 1). Acciones: arriba, abajo, izquierda y "
        "derecha. Modelo de transición: moverse a una celda adyacente sin muro. "
        "Test de objetivo: estar en E = (17, 29). Coste: 1 por movimiento.",
        color=BLUE, fondo=BLUE_BG,
    )


def seccion_3(doc: Document, v: dict) -> None:
    r = v["bfs"]
    doc.add_heading("3. Búsqueda en amplitud (BFS)", level=1)
    doc.add_heading("3.1. Idea del algoritmo", level=2)
    texto(
        doc,
        "BFS utiliza una cola FIFO (first in, first out). En cada paso extrae el "
        "nodo descubierto hace más tiempo, es decir, el más cercano al inicio, y "
        "expande todos sus vecinos. De esta forma recorre el grafo por niveles: "
        "primero los nodos a distancia 1, luego los de distancia 2, y así "
        "sucesivamente. La exploración avanza como una oleada desde S.",
    )
    texto(
        doc,
        "En un grafo no ponderado, la primera vez que se extrae la meta de la "
        "cola se ha encontrado el camino con el menor número de aristas. Por eso "
        "BFS es óptimo cuando todas las acciones tienen el mismo coste.",
    )

    doc.add_heading("3.2. Pseudocódigo", level=2)
    bloque_codigo(
        doc,
        "\n".join([
            "BFS(inicio, meta):",
            "    padre <- {inicio: None}",
            "    frontera <- Cola()",
            "    frontera.encolar(inicio)",
            "",
            "    mientras frontera no este vacia:",
            "        actual <- frontera.desencolar()",
            "        si actual = meta:",
            "            terminar",
            "        para cada vecino de actual:",
            "            si vecino no esta en padre:",
            "                padre[vecino] <- actual",
            "                frontera.encolar(vecino)",
            "",
            "    devolver reconstruir_camino(padre, meta)",
        ]),
        size=8.2, color_borde=BLUE,
    )

    doc.add_heading("3.3. Propiedades y complejidad", level=2)
    vineta(doc, "Sí, en grafos finitos con conjunto de visitados.", "¿Es completo? ")
    vineta(doc, "Sí, para grafos no ponderados: devuelve el camino con menos aristas.",
           "¿Es óptimo? ")
    vineta(doc, "O(V + E), porque cada nodo y cada arista se procesan como máximo "
                "una vez.", "Tiempo: ")
    vineta(doc, "O(V), por la cola de frontera y el diccionario de padres.",
           "Espacio: ")
    texto(
        doc,
        f"En esta instancia, BFS expandió {r.expandidos} nodos, alcanzó una "
        f"frontera máxima de {r.frontera_max} nodos y encontró un camino de "
        f"{r.longitud_camino} celdas ({r.coste} movimientos). Es el camino más "
        "corto posible entre S y E.",
    )


def seccion_4(doc: Document, v: dict) -> None:
    r = v["dfs"]
    doc.add_heading("4. Búsqueda en profundidad (DFS)", level=1)
    doc.add_heading("4.1. Idea del algoritmo", level=2)
    texto(
        doc,
        "DFS utiliza una pila LIFO (last in, first out). En cada paso extrae el "
        "nodo descubierto más recientemente y continúa por esa rama hasta que no "
        "puede avanzar; entonces retrocede (backtracking) y prueba otra "
        "alternativa. Su recorrido es profundo y no sigue un orden por niveles.",
    )
    texto(
        doc,
        "DFS encuentra algún camino si el grafo es finito y se lleva un registro "
        "de nodos visitados, pero no garantiza que ese camino sea el más corto. "
        "El resultado depende del orden en que se generan los vecinos: si se "
        "prueba primero una rama larga, la solución puede ser muy inferior a la "
        "de BFS.",
    )

    doc.add_heading("4.2. Pseudocódigo", level=2)
    bloque_codigo(
        doc,
        "\n".join([
            "DFS(inicio, meta):",
            "    padre <- {inicio: None}",
            "    frontera <- Pila()",
            "    frontera.apilar(inicio)",
            "",
            "    mientras frontera no este vacia:",
            "        actual <- frontera.desapilar()",
            "        si actual = meta:",
            "            terminar",
            "        para cada vecino de actual (en orden inverso):",
            "            si vecino no esta en padre:",
            "                padre[vecino] <- actual",
            "                frontera.apilar(vecino)",
            "",
            "    devolver reconstruir_camino(padre, meta)",
        ]),
        size=8.2, color_borde=ORANGE,
    )

    doc.add_heading("4.3. Propiedades y complejidad", level=2)
    vineta(doc, "Sí, en grafos finitos, siempre que se marquen los nodos "
                "visitados para evitar ciclos.", "¿Es completo? ")
    vineta(doc, "No: devuelve el primer camino que encuentra, no necesariamente "
                "el más corto.", "¿Es óptimo? ")
    vineta(doc, "O(V + E), igual que BFS.", "Tiempo: ")
    vineta(doc, "O(V) en búsqueda sobre grafos con conjunto de visitados; en "
                "búsqueda sobre árboles, O(b·m), donde b es el factor de "
                "ramificación y m la profundidad máxima.", "Espacio: ")
    texto(
        doc,
        f"En esta instancia, DFS expandió {r.expandidos} nodos, alcanzó una "
        f"frontera máxima de {r.frontera_max} nodos y encontró un camino de "
        f"{r.longitud_camino} celdas ({r.coste} movimientos), claramente más "
        "largo que el de BFS. No es un camino óptimo.",
    )


def seccion_5(doc: Document, v: dict) -> None:
    doc.add_heading("5. Implementación en Python", level=1)
    doc.add_heading("5.1. Estructura del proyecto", level=2)
    texto(
        doc,
        "El proyecto está organizado en tres módulos y un archivo de arranque. "
        "La separación permite reutilizar la instancia, los algoritmos y la "
        "presentación de resultados de forma independiente.",
    )
    tabla_bonita(
        doc,
        ["Archivo", "Responsabilidad"],
        [
            ["laberinto.py", "Define el laberinto, el inicio, la meta, la función "
                             "de vecinos y la impresión en ASCII."],
            ["busqueda_ciega.py", "Implementa BFS y DFS, mide nodos expandidos, "
                                  "aristas evaluadas, frontera y tiempo."],
            ["main.py", "Ejecuta ambos algoritmos, muestra las soluciones, compara "
                        "los resultados y guarda resultados_ejecucion_2.4.txt."],
            ["README.md", "Instrucciones de ejecución y requisitos."],
            ["requirements.txt", "Sin dependencias externas (solo informativo)."],
        ],
        widths=[4.0, 12.6],
        caption="Tabla 1. Estructura de la carpeta codigo/",
        center_cols=(),
    )

    doc.add_heading("5.2. Fragmentos clave", level=2)
    texto(
        doc,
        "La generación de vecinos es el corazón de la representación implícita. "
        "Solo se devuelven celdas dentro de los límites y sin muro:",
    )
    bloque_codigo(
        doc,
        "\n".join([
            "def vecinos(pos):",
            "    f, c = pos",
            "    for df, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):",
            "        candidato = (f + df, c + dc)",
            "        if es_transitable(candidato):",
            "            yield candidato",
        ]),
        size=7.8, color_borde=BLUE,
    )
    texto(
        doc,
        "El bucle central de BFS usa una cola y marca cada nodo al encolarlo. "
        "Así se evita procesarlo dos veces y se garantiza que el primer camino "
        "encontrado sea el más corto:",
    )
    bloque_codigo(
        doc,
        "\n".join([
            "padre = {inicio: None}",
            "frontera = deque([inicio])",
            "",
            "while frontera:",
            "    actual = frontera.popleft()",
            "    if actual == meta:",
            "        break",
            "    for vecino in vecinos(actual):",
            "        aristas_evaluadas += 1",
            "        if vecino not in padre:",
            "            padre[vecino] = actual",
            "            frontera.append(vecino)",
        ]),
        size=7.8, color_borde=BLUE,
    )
    texto(
        doc,
        "El bucle de DFS es idéntico salvo que utiliza una lista como pila "
        "(pop en el extremo final) y apila los vecinos en orden inverso para "
        "explorar primero arriba, luego abajo, izquierda y derecha:",
    )
    bloque_codigo(
        doc,
        "\n".join([
            "frontera = [inicio]",
            "",
            "while frontera:",
            "    actual = frontera.pop()",
            "    if actual == meta:",
            "        break",
            "    candidatos = list(vecinos(actual))",
            "    aristas_evaluadas += len(candidatos)",
            "    for vecino in reversed(candidatos):",
            "        if vecino not in padre:",
            "            padre[vecino] = actual",
            "            frontera.append(vecino)",
        ]),
        size=7.8, color_borde=ORANGE,
    )

    doc.add_heading("5.3. Ejecución sin dependencias", level=2)
    texto(
        doc,
        "Basta con abrir una terminal dentro de la carpeta codigo/ y ejecutar:",
    )
    bloque_codigo(doc, "python main.py", size=9.0, color_borde=GREEN)
    texto(
        doc,
        "En Visual Studio Code se puede abrir la carpeta codigo/, seleccionar "
        "main.py y pulsar el botón Run Python File (▶) o Ctrl + F5. No es "
        "necesario crear un entorno virtual ni ejecutar pip install: el código "
        "solo importa módulos de la biblioteca estándar (collections, time, "
        "dataclasses, pathlib y typing).",
    )
    callout(
        doc,
        "Salida del programa",
        "El programa imprime el laberinto, las dos soluciones en ASCII, la tabla "
        "comparativa y la conclusión. Además, guarda el archivo "
        "resultados_ejecucion_2.4.txt en la carpeta raíz de la actividad.",
        color=GREEN, fondo="EAF6EF",
    )


# ---------------------------------------------------------------------------
# Secciones 6 a 9
# ---------------------------------------------------------------------------
def seccion_6(doc: Document, v: dict) -> None:
    rb, rd = v["bfs"], v["dfs"]
    doc.add_heading("6. Resultados experimentales", level=1)
    doc.add_heading("6.1. Camino solución", level=2)
    texto(
        doc,
        f"Ambos algoritmos encuentran un camino entre S y E, pero no son "
        f"equivalentes. BFS devuelve una ruta de {rb.longitud_camino} celdas "
        f"({rb.coste} movimientos), mientras que DFS devuelve una de "
        f"{rd.longitud_camino} celdas ({rd.coste} movimientos). La ruta de DFS "
        f"es aproximadamente un {100 * (rd.longitud_camino - rb.longitud_camino) / rb.longitud_camino:.0f}% "
        "más larga que la de BFS.",
    )
    figura(doc, FIGURAS_DIR / "02_solucion_bfs.png",
           "Figura 3. Camino solución obtenido con BFS (azul).", 6.25)
    figura(doc, FIGURAS_DIR / "03_solucion_dfs.png",
           "Figura 4. Camino solución obtenido con DFS (naranja).", 6.25)
    texto(
        doc,
        "La diferencia visual es clara: el camino de BFS avanza de forma directa "
        "hacia la meta, mientras que el de DFS rodea y retrocede por ramas que "
        "no conducen a la salida. Esto no se debe a un error del algoritmo, sino "
        "a su propia estrategia: DFS se compromete con la primera rama que "
        "encuentra y solo cambia cuando esa rama se agota.",
    )

    doc.add_heading("6.2. Orden de exploración", level=2)
    texto(
        doc,
        "Las Figuras 5 y 6 muestran el orden en que se expandió cada nodo. El "
        "color claro indica una expansión temprana y el oscuro, una tardía. En "
        "BFS se aprecian oleadas concéntricas desde S; en DFS se observa una "
        "exploración profunda, con retrocesos cuando una rama no lleva a la meta.",
    )
    figura(doc, FIGURAS_DIR / "04_exploracion_bfs.png",
           "Figura 5. Orden de expansión de BFS: exploración por niveles.", 6.25)
    figura(doc, FIGURAS_DIR / "05_exploracion_dfs.png",
           "Figura 6. Orden de expansión de DFS: exploración profunda con retrocesos.",
           6.25)

    doc.add_heading("6.3. Comparación numérica", level=2)
    texto(
        doc,
        "La Tabla 2 resume las métricas principales. Los tiempos se midieron "
        "con 200 ejecuciones por algoritmo (mejor promedio de 5 lotes) para "
        "reducir el ruido del sistema operativo.",
    )
    tabla_bonita(
        doc,
        ["Métrica", "BFS", "DFS"],
        [
            ["¿Encuentra solución?", "Sí", "Sí"],
            ["Celdas del camino", str(rb.longitud_camino), str(rd.longitud_camino)],
            ["Movimientos (aristas)", str(rb.coste), str(rd.coste)],
            ["Nodos expandidos", str(rb.expandidos), str(rd.expandidos)],
            ["Aristas evaluadas", str(rb.aristas_evaluadas), str(rd.aristas_evaluadas)],
            ["Frontera máxima", str(rb.frontera_max), str(rd.frontera_max)],
            ["Tiempo medio (ms)", f"{v['t_bfs']:.3f}", f"{v['t_dfs']:.3f}"],
            ["¿Camino óptimo?", "Sí", "No"],
        ],
        widths=[7.2, 4.7, 4.7],
        caption="Tabla 2. Comparación de BFS y DFS en el laberinto 31 × 19.",
        center_cols=(1, 2),
    )
    figura(doc, FIGURAS_DIR / "06_comparacion.png",
           "Figura 7. Comparación cuantitativa de las métricas principales.", 6.25)

    doc.add_heading("6.4. Evolución de la frontera", level=2)
    texto(
        doc,
        "La frontera es el conjunto de nodos descubiertos que aún no se han "
        "expandido. Su tamaño máximo es una medida directa del consumo de "
        "memoria. La Figura 8 muestra cómo cambia a lo largo de la búsqueda: "
        "BFS mantiene una frontera relativamente estable, mientras que DFS "
        "presenta picos cuando apila todos los vecinos de un nodo antes de "
        "seguir por una rama.",
    )
    figura(doc, FIGURAS_DIR / "07_frontera.png",
           "Figura 8. Evolución del tamaño de la frontera durante la búsqueda.", 6.25)


def seccion_7(doc: Document, v: dict) -> None:
    rb, rd = v["bfs"], v["dfs"]
    dif_nodos = 100 * (rb.expandidos - rd.expandidos) / rb.expandidos
    dif_aristas = 100 * (rb.aristas_evaluadas - rd.aristas_evaluadas) / rb.aristas_evaluadas
    dif_camino = 100 * (rd.longitud_camino - rb.longitud_camino) / rb.longitud_camino
    dif_frontera = 100 * (rd.frontera_max - rb.frontera_max) / rb.frontera_max
    dif_tiempo = 100 * abs(v["t_dfs"] - v["t_bfs"]) / max(v["t_bfs"], v["t_dfs"])

    doc.add_heading("7. Análisis comparativo", level=1)
    doc.add_heading("7.1. Nodos expandidos y calidad del camino", level=2)
    texto(
        doc,
        f"DFS expandió {rd.expandidos} nodos frente a los {rb.expandidos} de BFS, "
        f"es decir, un {dif_nodos:.1f}% menos. También evaluó menos aristas "
        f"({rd.aristas_evaluadas} frente a {rb.aristas_evaluadas}). Sin embargo, "
        f"esa aparente ventaja tiene un coste alto: su camino es un "
        f"{dif_camino:.1f}% más largo. En otras palabras, DFS hace menos trabajo "
        "para encontrar una solución, pero la solución que encuentra es peor.",
    )
    texto(
        doc,
        "La explicación es estructural. BFS debe expandir todos los nodos con "
        "distancia menor que la de la meta antes de poder garantizar que no "
        "existe un camino más corto. Ese trabajo extra es el precio de la "
        "optimalidad. DFS, en cambio, se detiene en cuanto extrae la meta de la "
        "pila, aunque haya llegado a ella por un recorrido largo.",
    )
    tabla_bonita(
        doc,
        ["Métrica", "BFS", "DFS", "Diferencia"],
        [
            ["Nodos expandidos", str(rb.expandidos), str(rd.expandidos),
             f"−{dif_nodos:.1f}% (DFS)"],
            ["Aristas evaluadas", str(rb.aristas_evaluadas), str(rd.aristas_evaluadas),
             f"−{dif_aristas:.1f}% (DFS)"],
            ["Longitud del camino", str(rb.longitud_camino), str(rd.longitud_camino),
             f"+{dif_camino:.1f}% (DFS)"],
            ["Frontera máxima", str(rb.frontera_max), str(rd.frontera_max),
             f"+{dif_frontera:.1f}% (DFS)"],
            ["Tiempo medio (ms)", f"{v['t_bfs']:.3f}", f"{v['t_dfs']:.3f}",
             f"≈ {dif_tiempo:.1f}%"],
        ],
        widths=[5.4, 3.2, 3.2, 4.8],
        caption="Tabla 3. Diferencias relativas entre BFS y DFS.",
        center_cols=(1, 2, 3),
    )

    doc.add_heading("7.2. Tiempo de ejecución", level=2)
    texto(
        doc,
        f"Los tiempos medidos son prácticamente iguales: {v['t_bfs']:.3f} ms para "
        f"BFS y {v['t_dfs']:.3f} ms para DFS (diferencia ≈ {dif_tiempo:.1f}%). "
        "Esto no significa que los algoritmos tengan el mismo coste teórico en "
        "todos los casos, sino que, en un grafo de solo 290 nodos, ambos son tan "
        "rápidos que el tiempo real está dominado por el ruido del sistema "
        "operativo y por detalles de implementación. Por eso, para comparar el "
        "trabajo realizado se usan métricas deterministas: nodos expandidos y "
        "aristas evaluadas.",
    )
    texto(
        doc,
        "En términos teóricos, ambos recorren cada nodo y cada arista como "
        "máximo una vez, por lo que su complejidad temporal es O(V + E). La "
        "diferencia práctica aparece en el número de nodos que cada estrategia "
        "necesita expandir antes de detenerse, y sobre todo en la calidad del "
        "camino obtenido.",
    )

    doc.add_heading("7.3. Memoria y frontera", level=2)
    texto(
        doc,
        f"En esta instancia, la frontera máxima de BFS fue {rb.frontera_max} "
        f"nodos y la de DFS, {rd.frontera_max}. Es decir, DFS usó un "
        f"{dif_frontera:.1f}% más de frontera, no menos. Este resultado recuerda "
        "que la idea de que «DFS siempre gasta menos memoria» es una "
        "simplificación: en búsqueda sobre grafos con conjunto de visitados, "
        "ambos algoritmos almacenan O(V) información, y el tamaño concreto de la "
        "frontera depende de la forma del grafo y del orden de exploración.",
    )
    texto(
        doc,
        "La ventaja clásica de DFS en memoria aparece en la búsqueda sobre "
        "árboles o en implementaciones recursivas con retroceso, donde la pila "
        "solo contiene el camino actual y su tamaño es O(b·m). En un laberinto "
        "con bucles y con un conjunto de visitados global, esa ventaja se diluye.",
    )
    callout(
        doc,
        "La paradoja de DFS",
        "DFS expande menos nodos y evalúa menos aristas, pero devuelve un camino "
        "casi el doble de largo. BFS paga un poco más de trabajo para garantizar "
        "que la ruta sea la más corta. En un problema de navegación, esa garantía "
        "suele valer más que el ahorro de unas pocas expansiones.",
        color=ORANGE, fondo=ORANGE_BG,
    )


def seccion_8(doc: Document, v: dict) -> None:
    rb, rd = v["bfs"], v["dfs"]
    doc.add_heading("8. Complejidad e idoneidad", level=1)
    doc.add_heading("8.1. Complejidad temporal y espacial", level=2)
    texto(
        doc,
        "La Tabla 4 resume la complejidad de ambos algoritmos. V es el número de "
        "nodos (celdas transitables), E el número de aristas, b el factor de "
        "ramificación y m la profundidad máxima del árbol de búsqueda.",
    )
    tabla_bonita(
        doc,
        ["Algoritmo", "Tiempo", "Espacio", "¿Completo?", "¿Óptimo?"],
        [
            ["BFS", "O(V + E)", "O(V)", "Sí", "Sí (no ponderado)"],
            ["DFS", "O(V + E)", "O(V) en grafos; O(b·m) en árboles", "Sí (con visitados)", "No"],
        ],
        widths=[3.0, 3.0, 4.6, 3.0, 3.0],
        caption="Tabla 4. Complejidad de BFS y DFS.",
        center_cols=(1, 2, 3, 4),
    )
    texto(
        doc,
        "Ambos algoritmos son lineales en el tamaño del grafo porque, gracias al "
        "conjunto de visitados, cada nodo se expande una sola vez y cada arista "
        "se examina como máximo una vez. La diferencia está en la estructura de "
        "la frontera: una cola en BFS y una pila en DFS. Esa diferencia determina "
        "el orden de exploración y, con él, la optimalidad y el uso de memoria.",
    )

    doc.add_heading("8.2. ¿Qué algoritmo conviene según el problema?", level=2)
    texto(
        doc,
        "No existe un algoritmo «mejor» en abstracto: la elección depende de la "
        "pregunta que se hace al problema y de las restricciones de memoria y "
        "tiempo. La Tabla 5 resume los escenarios típicos.",
    )
    tabla_bonita(
        doc,
        ["Problema", "Algoritmo", "Razón"],
        [
            ["Ruta más corta en laberinto o mapa sin pesos", "BFS",
             "Garantiza el camino con menos aristas."],
            ["Detección de ciclos, orden topológico, componentes conexas", "DFS",
             "Recorrido profundo y sencillo de implementar."],
            ["Backtracking (sudoku, N-reinas, planificación)", "DFS",
             "Explora decisiones y retrocede cuando falla."],
            ["Solo se necesita alguna ruta, no la más corta", "DFS",
             "Puede encontrar una solución con menos expansiones."],
            ["Grafo muy ancho y memoria limitada", "DFS*",
             "BFS puede almacenar una frontera enorme; DFS evita esa frontera."],
            ["Ruta mínima con costes distintos", "Dijkstra / A*",
             "BFS solo es óptimo si todas las aristas cuestan lo mismo."],
        ],
        widths=[7.3, 3.2, 6.1],
        caption="Tabla 5. Idoneidad de BFS y DFS según el tipo de problema.",
        first_col_bold=False,
        center_cols=(1,),
    )
    texto(
        doc,
        "* DFS evita la gran frontera de BFS, pero en búsqueda sobre grafos sigue "
        "almacenando el conjunto de visitados y la pila; la ventaja de memoria es "
        "más clara en árboles o en implementaciones recursivas con retroceso.",
        size=8.6, italic=True, color=GRAY, space_after=8,
    )
    texto(
        doc,
        "Para el laberinto de esta actividad, BFS es la opción más adecuada: el "
        "objetivo es la ruta más corta, el grafo es pequeño (290 nodos) y la "
        "memoria no es una restricción. La frontera máxima de 13 nodos es "
        "perfectamente manejable. DFS solo sería preferible si bastara con "
        "cualquier ruta y se quisiera reducir el número de expansiones, pero el "
        "camino un 81% más largo es un mal negocio para un robot, un repartidor "
        "o cualquier aplicación de navegación.",
    )
    texto(
        doc,
        "Si el problema incluyera costes distintos por celda (por ejemplo, barro, "
        "agua o pendiente), BFS dejaría de ser óptimo y habría que usar Dijkstra. "
        "Si además se dispusiera de una heurística admisible, como la distancia "
        "Manhattan hasta la meta, A* encontraría la ruta óptima expandiendo "
        "menos nodos que BFS. Esa comparación queda como extensión natural de "
        "esta actividad.",
    )


def seccion_9(doc: Document, v: dict) -> None:
    rb, rd = v["bfs"], v["dfs"]
    doc.add_heading("9. Conclusiones", level=1)
    numerada(
        doc,
        f"ambos algoritmos resuelven el laberinto, pero solo BFS garantiza el "
        f"camino más corto: {rb.longitud_camino} celdas frente a "
        f"{rd.longitud_camino} de DFS.",
        "Optimalidad: ", space_after=5,
    )
    numerada(
        doc,
        f"DFS expandió un {100 * (rb.expandidos - rd.expandidos) / rb.expandidos:.1f}% "
        f"menos de nodos ({rd.expandidos} frente a {rb.expandidos}) y evaluó un "
        f"{100 * (rb.aristas_evaluadas - rd.aristas_evaluadas) / rb.aristas_evaluadas:.1f}% "
        "menos de aristas, pero pagó ese ahorro con un camino mucho más largo.",
        "Eficiencia: ", space_after=5,
    )
    numerada(
        doc,
        f"en este laberinto, la frontera de DFS ({rd.frontera_max}) fue mayor que "
        f"la de BFS ({rb.frontera_max}). La idea de que DFS siempre usa menos "
        "memoria no se sostiene en búsqueda sobre grafos con conjunto de "
        "visitados; el consumo depende de la instancia.",
        "Memoria: ", space_after=5,
    )
    numerada(
        doc,
        "ambos tienen complejidad O(V + E) en tiempo y O(V) en espacio. Los "
        f"tiempos medidos son prácticamente iguales ({v['t_bfs']:.3f} ms y "
        f"{v['t_dfs']:.3f} ms), así que a esta escala la decisión debe basarse en "
        "la optimalidad y en la forma de la frontera, no en la velocidad.",
        "Complejidad: ", space_after=5,
    )
    numerada(
        doc,
        "para laberintos y rutas mínimas sin pesos, BFS es la elección correcta. "
        "DFS es preferible para exploración exhaustiva, detección de ciclos, "
        "orden topológico, backtracking y situaciones en las que basta con "
        "encontrar alguna solución.",
        "Idoneidad: ", space_after=8,
    )
    texto(
        doc,
        "En definitiva, la elección del algoritmo no depende de cuál es «mejor» "
        "en abstracto, sino de la pregunta que se hace al problema. Si la "
        "pregunta es «¿cuál es el camino más corto?», la respuesta es BFS. Si la "
        "pregunta es «¿existe algún camino?» o «¿qué estados son alcanzables?», "
        "DFS es una herramienta adecuada. Comprender esa diferencia es más "
        "valioso que memorizar una lista de ventajas y desventajas.",
    )


# ---------------------------------------------------------------------------
# Referencias, declaración de IA y anexo
# ---------------------------------------------------------------------------
def referencias(doc: Document) -> None:
    doc.add_heading("10. Referencias", level=1)
    refs = [
        "RUSSELL, S. y NORVIG, P. (2021). Artificial Intelligence: A Modern "
        "Approach, 4.ª ed. Pearson. Capítulo 3 (Solving Problems by Searching).",
        "CORMEN, T. H., LEISERSON, C. E., RIVEST, R. L. y STEIN, C. (2009). "
        "Introduction to Algorithms, 3.ª ed. MIT Press. Capítulo 22 "
        "(Elementary Graph Algorithms).",
        "KNUTH, D. E. (1997). The Art of Computer Programming, Vol. 1: "
        "Fundamental Algorithms, 3.ª ed. Addison-Wesley.",
        "SEDGEWICK, R. y WAYNE, K. (2011). Algorithms, 4.ª ed. Addison-Wesley. "
        "Capítulo 4 (Graphs).",
        "PYTHON SOFTWARE FOUNDATION (s. f.). Python Documentation. Disponible "
        "en: https://docs.python.org/3/",
        "HUNTER, J. D. (2007). Matplotlib: A 2D graphics environment. Computing "
        "in Science & Engineering, 9(3), 90–95. DOI: 10.1109/MCSE.2007.55.",
        "OPENCODE (2026). OpenCode: agente de inteligencia artificial para "
        "programación y análisis [software]. Disponible en: "
        "https://opencode.ai. Consultado el 25 de octubre de 2026.",
    ]
    for i, ref in enumerate(refs, start=1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.85)
        p.paragraph_format.first_line_indent = Cm(-0.85)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.05
        r1 = p.add_run(f"[{i}] ")
        _aplicar_fuente(r1, BODY_FONT, 9.2, NAVY, bold=True)
        r2 = p.add_run(ref)
        _aplicar_fuente(r2, BODY_FONT, 9.2, NAVY)

    doc.add_heading("Declaración de uso de inteligencia artificial", level=2)
    texto(
        doc,
        "Para la elaboración de esta memoria se utilizó la herramienta de "
        "inteligencia artificial OpenCode [7], como apoyo en la implementación "
        "y depuración del código Python, la generación de las figuras y la "
        "maquetación de los archivos Word y PDF. La selección del problema, la "
        "definición del laberinto, la verificación de los resultados y la "
        "revisión del contenido corresponden a la persona estudiante, quien "
        "asume la responsabilidad sobre el material entregado. Todas las cifras "
        "reportadas provienen de ejecutar el código incluido en el anexo.",
        size=9.8,
    )


def anexo(doc: Document) -> None:
    doc.add_page_break()
    doc.add_heading("Anexo A — Código completo", level=1)
    texto(
        doc,
        "A continuación se incluye el listado íntegro de los archivos de la "
        "carpeta codigo/. El código no requiere dependencias externas y puede "
        "ejecutarse directamente con python main.py.",
        size=9.8, italic=True,
    )
    archivos = [
        ("laberinto.py", "Laberinto, vecinos y representación del grafo"),
        ("busqueda_ciega.py", "BFS, DFS y medición de resultados"),
        ("main.py", "Ejecución, comparación y guardado del informe"),
    ]
    for i, (nombre, desc) in enumerate(archivos, start=1):
        doc.add_heading(f"A.{i}. {nombre} — {desc}", level=2)
        codigo = (CODIGO_DIR / nombre).read_text(encoding="utf-8")
        bloque_codigo(doc, codigo, size=6.4,
                      color_borde=BLUE if i != 2 else ORANGE,
                      mantener_junto=False)


# ---------------------------------------------------------------------------
# Generación del documento
# ---------------------------------------------------------------------------
def generar_memoria() -> Path:
    # 1) Resultados actualizados
    print("Ejecutando codigo/main.py ...")
    subprocess.run(
        [sys.executable, str(CODIGO_DIR / "main.py")],
        cwd=str(CODIGO_DIR), check=True, capture_output=True, timeout=180,
    )

    # 2) Figuras
    from graficos_24 import generar_figuras

    generar_figuras()
    v = valores()

    # 3) Documento
    doc = Document()
    configurar_estilos(doc)
    configurar_seccion(doc)
    metadatos(doc)

    portada(doc)
    contenido(doc)
    seccion_1(doc, v)
    seccion_2(doc, v)
    seccion_3(doc, v)
    seccion_4(doc, v)
    seccion_5(doc, v)
    seccion_6(doc, v)
    seccion_7(doc, v)
    seccion_8(doc, v)
    seccion_9(doc, v)
    referencias(doc)
    anexo(doc)

    ruta_docx = BASE_DIR / "FIA_G171_MARIN_FLOR_S4.docx"
    doc.save(ruta_docx)
    print(f"  -> {ruta_docx.name}")
    return ruta_docx


def main() -> None:
    print("Generando la memoria de la Actividad 2.4 ...")
    ruta_docx = generar_memoria()
    ruta_pdf = BASE_DIR / "FIA_G171_MARIN_FLOR_S4.pdf"
    try:
        subprocess.run(
            ["soffice", "--headless", "--norestore", "--convert-to", "pdf",
             "--outdir", str(BASE_DIR), str(ruta_docx)],
            check=True, capture_output=True, timeout=300,
        )
        print(f"  -> {ruta_pdf.name}")
    except FileNotFoundError:
        print("  [aviso] LibreOffice (soffice) no está disponible: no se generó el PDF.")
    except subprocess.CalledProcessError as exc:
        print("  [aviso] fallo al convertir a PDF:")
        print(exc.stderr.decode()[:500])
    print("Listo.")


if __name__ == "__main__":
    main()
