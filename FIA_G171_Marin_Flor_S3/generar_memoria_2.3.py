#!/usr/bin/env python3
"""
Genera la memoria de la Actividad 2.3 (Word + PDF).
"""
from __future__ import annotations

import inspect
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

BASE_DIR = Path(__file__).resolve().parent
FIGURAS = BASE_DIR / "figuras"
AZUL = "1B2A4A"


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
    return inspect.getsource(funcion)


def portada(doc):
    for _ in range(4):
        doc.add_paragraph()
    parrafo(doc, "MEMORIA DE ACTIVIDAD", size=16, bold=True,
            align=WD_ALIGN_PARAGRAPH.CENTER, color=AZUL, space_after=4)
    parrafo(doc, "Actividad 2.3 — Búsqueda local",
            size=22, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, color=AZUL,
            space_after=18)
    parrafo(doc, "Implementación y optimización de Hill Climbing y Simulated Annealing "
                 "para la minimización de una ruta de reparto (TSP)",
            size=13, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=40)
    for etiqueta, valor in [
        ("Asignatura:", "Fundamentos de Inteligencia Artificial"),
        ("Estudiante:", "Julissa Marin Flor"),
        ("Docente:", "Javier García Lara"),
        ("Institución:", "Universidad Politécnica de Atlautla"),
        ("Fecha:", "22 de octubre de 2026"),
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


def generar_memoria() -> Path:
    doc = Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Inches(0.9)
        s.left_margin = s.right_margin = Inches(0.9)
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(11)

    portada(doc)

    doc.add_heading("1. Enunciado", level=1)
    parrafo(doc, "Implementar los algoritmos de búsqueda local Hill Climbing y "
                 "Simulated Annealing para optimizar una función real, reportando: "
                 "enunciado, función, objetivo, vecindad, parámetros (T, iteraciones, n), "
                 "gráfica de convergencia y comparación de resultados.")

    doc.add_heading("2. Problema seleccionado", level=1)
    parrafo(doc, "Se seleccionó el problema del viajante de comercio (Traveling Salesperson "
                 "Problem, TSP): encontrar el recorrido que pasa por todas las paradas de "
                 "entrega saliendo y volviendo al almacén, minimizando la distancia total "
                 "recorrida. Es un problema clásico de optimización combinatoria con un "
                 "espacio de búsqueda muy grande, ideal para evaluar algoritmos de búsqueda local.")

    doc.add_heading("3. Función, objetivo y representación", level=1)
    parrafo(doc, "Representación: una ruta es una permutación r = [0, p1, p2, ..., pn] "
                 "donde 0 es el almacén y {p1,...,pn} son las paradas de entrega en orden de visita.")
    parrafo(doc, "Función objetivo (a minimizar):", bold=True)
    parrafo(doc, "f(r) = d(rn, r1) + \u2211_{i=1}^{n-1} d(ri, r_{i+1}), con d(i,j) = distancia euclídea entre puntos.")
    parrafo(doc, "Instancia utilizada: 1 almacén + 20 paradas = 21 puntos, coordenadas aleatorias "
                 "en un plano 2D. Se utiliza la distancia euclídea entre cada par de puntos.")

    doc.add_heading("4. Vecindad", level=1)
    parrafo(doc, "Para generar soluciones vecinas se emplean dos operadores complementarios:")
    vineta(doc, "Intercambio (swap): se seleccionan dos paradas distintas y se intercambian sus posiciones.")
    vineta(doc, "Inversión / 2-opt: se invierte el orden de un segmento aleatorio entre dos paradas, "
                "lo cual suele ser muy eficaz en TSP.")

    doc.add_heading("5. Algoritmos y parámetros", level=1)
    doc.add_heading("5.1 Hill Climbing", level=2)
    parrafo(doc, "Hill Climbing con estrategia de mejor vecino (steepest ascent). "
                 "En cada iteración explora todos los vecinos generados por swap e inversión, "
                 "y si existe alguna mejora acepta el mejor de ellos; en caso contrario se detiene "
                 "por convergencia (máximo sin mejora).")
    tabla(doc, ["Parámetro", "Valor", "Descripción"],
          [["max_iter", "10 000", "Máximo de iteraciones"],
           ["max_sin_mejora", "150", "Criterio de parada por estancamiento"],
           ["Vecindad", "swap + 2-opt", "Operadores explorados"]])

    doc.add_heading("5.2 Simulated Annealing", level=2)
    parrafo(doc, "Simulated Annealing acepta mejoras siempre y acepta empeoramientos con "
                 "probabilidad P(Δ) = exp(-Δ/T). La temperatura disminuye exponencialmente con "
                 "factor alpha.")
    tabla(doc, ["Parámetro", "Valor", "Descripción"],
          [["T0 (Temperatura inicial)", "12.0", "Temperatura inicial"],
           ["Tf (Temperatura final)", "0.001", "Temperatura de parada"],
           ["alpha", "0.995", "Factor de enfriamiento"],
           ["iter_por_T", "80", "Iteraciones por nivel de temperatura"],
           ["Vecindad", "swap o 2-opt (aleatorio)", "Operador seleccionado aleatoriamente"]])

    doc.add_heading("6. Gráficas de convergencia", level=1)
    parrafo(doc, "La gráfica de convergencia muestra la evolución del mejor costo encontrado "
                 "durante la búsqueda, partiendo de la misma ruta inicial aleatoria.")
    figura(doc, "02_3_convergencia.png",
           pie="Figura 1. Gráfica de convergencia — Hill Climbing vs Simulated Annealing")

    doc.add_heading("7. Comparación de rutas y resultados", level=1)
    parrafo(doc, "Se comparan las rutas obtenidas: inicial, Hill Climbing y Simulated Annealing.")
    figura(doc, "02_3_rutas_comparacion.png",
           pie="Figura 2. Comparación visual de rutas (almacén + 20 paradas)")
    parrafo(doc, "También se realiza un análisis estadístico con 30 ejecuciones independientes "
                 "partiendo de rutas aleatorias distintas para cada algoritmo.")
    figura(doc, "02_3_comparacion_estadistica.png",
           pie="Figura 3. Comparación estadística de 30 ejecuciones (boxplot)")

    doc.add_heading("8. Resultados numéricos", level=1)
    tabla(doc, ["Configuración", "Hill Climbing", "Simulated Annealing"],
          [["Misma ruta inicial aleatoria", "43.837", "42.883"],
           ["Con ruta inicial (vecino más próximo)", "42.883", "42.883"],
           ["30 ejecuciones — mínimo", "42.883", "42.883"],
           ["30 ejecuciones — media", "44.613", "43.058"],
           ["30 ejecuciones — mediana", "44.209", "42.883"],
           ["30 ejecuciones — desviación típica", "1.148", "0.275"],
           ["30 ejecuciones — máximo", "47.181", "43.531"]])

    doc.add_heading("9. Análisis y conclusiones", level=1)
    vineta(doc, "Hill Climbing es rápido y eficaz cuando parte de una buena solución inicial, "
                "pero tiende a quedar atrapado en óptimos locales si parte de una ruta aleatoria.")
    vineta(doc, "Simulated Annealing explora más el espacio de búsqueda al aceptar soluciones "
                "peores con cierta probabilidad, lo que le permite escapar de óptimos locales.")
    vineta(doc, "Con rutas iniciales aleatorias, Simulated Annealing obtiene una media mucho "
                "mejor (43.058) frente a Hill Climbing (44.613) y una desviación típica considerablemente "
                "menor (0.275 vs 1.148), lo que demuestra mayor robustez.")
    vineta(doc, "Ambos algoritmos alcanzan el mismo óptimo encontrado (42.883) en las mejores ejecuciones, "
                "pero SA es más consistente entre ejecuciones.")
    vineta(doc, "La combinación de operadores (intercambio + 2-opt) resulta adecuada para este TSP, "
                "permitiendo mejoras significativas respecto a la ruta inicial.")
    parrafo(doc, "En suma, para este problema, Simulated Annealing resulta más adecuado cuando "
                 "no se dispone de una buena solución inicial, mientras que ambos son equivalentes "
                 "partiendo de heurísticas constructivas como el vecino más próximo.")

    doc.add_heading("10. Referencias", level=1)
    referencias = [
        "RUSSELL, S. y NORVIG, P. (2021). Artificial Intelligence: A Modern Approach, "
        "4.ª ed. Pearson. Capítulo 4 (Búsqueda local).",
        "KIRKPATRICK, S., GELATT, C. D. y VECCHI, M. P. (1983). Optimization by Simulated "
        "Annealing. Science, 220(4598), 671–680. DOI: 10.1126/science.220.4598.671.",
        "METROPOLIS, N. et al. (1953). Equation of State Calculations by Fast Computing Machines. "
        "The Journal of Chemical Physics, 21(6), 1087–1092. DOI: 10.1063/1.1699114.",
        "PYTHON SOFTWARE FOUNDATION (s. f.). Python Documentation. Disponible en: "
        "https://docs.python.org/3/",
        "HUNTER, J. D. (2007). Matplotlib: A 2D graphics environment. Computing in Science & "
        "Engineering, 9(3), 90–95. DOI: 10.1109/MCSE.2007.55.",
    ]
    for i, ref in enumerate(referencias, start=1):
        p = doc.add_paragraph()
        b = p.add_run(f"[{i}] ")
        b.bold = True
        b.font.size = Pt(10)
        t = p.add_run(ref)
        t.font.size = Pt(10)
        p.paragraph_format.space_after = Pt(6)

    ia_num = len(referencias) + 1
    p = doc.add_paragraph()
    b = p.add_run(f"[{ia_num}] ")
    b.bold = True
    b.font.size = Pt(10)
    t = p.add_run("OPENCODE (2026). OpenCode: agente de inteligencia artificial para "
                  "programación y análisis [software]. Disponible en: https://opencode.ai. "
                  "Consultado el 22 de octubre de 2026.")
    t.font.size = Pt(10)
    p.paragraph_format.space_after = Pt(6)

    doc.add_heading("Declaración de uso de inteligencia artificial", level=2)
    parrafo(doc, f"Para la elaboración de esta memoria se utilizó la herramienta de "
                 f"inteligencia artificial OpenCode [{ia_num}], como apoyo en la "
                 f"implementación, depuración del código Python, generación de gráficas "
                 f"y maquetación de los archivos Word y PDF. La selección del problema, "
                 f"la calibración de parámetros, la verificación de resultados y la "
                 f"revisión del contenido corresponden a la persona estudiante, quien "
                 f"asume la responsabilidad sobre el material entregado.")

    doc.add_page_break()
    doc.add_heading("Anexo A — Listado del código fuente", level=1)
    parrafo(doc, "Código implementado en la carpeta `codigo/`.", italic=True, size=10)

    import sys
    sys.path.insert(0, str(BASE_DIR / "codigo"))
    import busqueda_local as mod_bl
    import problema_tsp as mod_tsp

    doc.add_heading("A.1 problema_tsp.py — Función objetivo y datos", level=2)
    codigo(doc, fuente_de(mod_tsp.longitud_ruta))
    doc.add_heading("A.2 busqueda_local.py — Hill Climbing", level=2)
    codigo(doc, fuente_de(mod_bl.hill_climbing))
    doc.add_heading("A.3 busqueda_local.py — Simulated Annealing", level=2)
    codigo(doc, fuente_de(mod_bl.simulated_annealing))

    ruta = BASE_DIR / "memoria_actividad_2.3.docx"
    doc.save(ruta)
    print(f"  -> {ruta.name}")
    return ruta


def main():
    print("Generando la memoria de la Actividad 2.3 ...")
    ruta_docx = generar_memoria()
    ruta_pdf = BASE_DIR / "memoria_actividad_2.3.pdf"
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
