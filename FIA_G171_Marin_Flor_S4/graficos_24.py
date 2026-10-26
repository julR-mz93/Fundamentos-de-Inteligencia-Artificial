#!/usr/bin/env python3
"""
Genera las figuras de la Actividad 2.4 (BFS y DFS sobre un laberinto).

Este script es parte de la elaboración del documento; el código entregable
(carpeta codigo/) NO depende de matplotlib ni de numpy.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_rgb
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

BASE_DIR = Path(__file__).resolve().parent
CODIGO_DIR = BASE_DIR / "codigo"
FIGURAS_DIR = BASE_DIR / "figuras"
FIGURAS_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(CODIGO_DIR))

from busqueda_ciega import bfs, dfs  # noqa: E402
from laberinto import COLUMNAS, FILAS, INICIO, LABERINTO, META  # noqa: E402

# ---------------------------------------------------------------------------
# Paleta y estilo
# ---------------------------------------------------------------------------
NAVY = "#0F2A44"
NAVY_2 = "#163A5C"
BLUE = "#1F6FB2"
BLUE_LIGHT = "#D6E8F7"
ORANGE = "#D9782D"
ORANGE_LIGHT = "#FBE4D2"
TEAL = "#2A9D8F"
GOLD = "#E9C46A"
GREEN = "#2E8B57"
RED = "#C0392B"
GRAY = "#6B7A8A"
GRAY_LIGHT = "#E7EDF3"
WHITE = "#FFFFFF"

plt.rcParams.update(
    {
        "font.family": "Montserrat",
        "font.size": 10.5,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelcolor": NAVY,
        "axes.edgecolor": "#C9D4DE",
        "xtick.color": GRAY,
        "ytick.color": GRAY,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    }
)


# ---------------------------------------------------------------------------
# Utilidades de dibujo
# ---------------------------------------------------------------------------
def _imagen_base(fondo: str = WHITE, muro: str = NAVY) -> np.ndarray:
    """Devuelve una imagen RGB (FILAS x COLUMNAS) con muros y celdas libres."""
    color_fondo = np.array(to_rgb(fondo))
    color_muro = np.array(to_rgb(muro))
    img = np.empty((FILAS, COLUMNAS, 3))
    for f in range(FILAS):
        for c in range(COLUMNAS):
            img[f, c] = color_muro if LABERINTO[f][c] == "#" else color_fondo
    return img


def _pintar_celdas(img: np.ndarray, celdas, colores) -> None:
    for (f, c), color in zip(celdas, colores):
        img[f, c] = to_rgb(color)


def _dibujar_base(ax, img: np.ndarray) -> None:
    ax.imshow(img, interpolation="nearest", zorder=1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-0.6, COLUMNAS - 0.4)
    ax.set_ylim(FILAS - 0.4, -0.6)
    ax.set_aspect("equal")
    for spine in ax.spines.values():
        spine.set_visible(False)


def _marcadores(ax, tamano: int = 230) -> None:
    """Dibuja los marcadores S (inicio) y E (meta)."""
    for (f, c), letra, color in (
        (INICIO, "S", GREEN),
        (META, "E", RED),
    ):
        ax.scatter(
            [c], [f], s=tamano, c=color, edgecolors="white",
            linewidths=2.0, zorder=7,
        )
        ax.text(
            c, f, letra, ha="center", va="center", color="white",
            fontsize=9.5, fontweight="bold", zorder=8,
        )


def _camino(ax, camino, color: str, grosor: float = 3.2) -> None:
    xs = [c for (_, c) in camino]
    ys = [f for (f, _) in camino]
    ax.plot(
        xs, ys, color=color, lw=grosor + 5.0, alpha=0.18,
        solid_capstyle="round", solid_joinstyle="round", zorder=3,
    )
    ax.plot(
        xs, ys, color=color, lw=grosor, alpha=1.0,
        solid_capstyle="round", solid_joinstyle="round", zorder=4,
    )


def _titulo(fig, titulo: str, subtitulo: str | None = None) -> None:
    fig.text(
        0.5, 0.972, titulo, ha="center", va="top",
        fontsize=17, fontweight="bold", color=NAVY,
    )
    if subtitulo:
        fig.text(
            0.5, 0.923, subtitulo, ha="center", va="top",
            fontsize=10.5, color=GRAY,
        )


def _guardar(fig, nombre: str) -> Path:
    ruta = FIGURAS_DIR / nombre
    fig.savefig(ruta, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  -> {ruta.name}")
    return ruta


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------
def figura_portada() -> Path:
    """Banner oscuro y elegante para la portada."""
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    fig.patch.set_facecolor("#0B1B2B")
    ax.set_facecolor("#0B1B2B")

    img = _imagen_base(fondo="#0E2235", muro="#274660")
    _dibujar_base(ax, img)

    r_bfs = bfs()
    _camino(ax, r_bfs.camino, GOLD, grosor=2.6)
    _marcadores(ax, tamano=190)

    # Viñeta suave: un rectángulo semitransparente en los bordes
    for lado, xy, ancho, alto in (
        ("sup", (0, 1), 1, 0.10),
        ("inf", (0, 0), 1, 0.10),
    ):
        ax.add_patch(
            Rectangle(
                xy, ancho, alto, transform=ax.transAxes,
                facecolor="#0B1B2B", edgecolor="none", alpha=0.55, zorder=9,
            )
        )

    ax.set_xlim(-0.6, COLUMNAS - 0.4)
    ax.set_ylim(FILAS - 0.4, -0.6)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    return _guardar(fig, "00_portada.png")


def figura_laberinto() -> Path:
    fig, ax = plt.subplots(figsize=(9.2, 5.9))
    img = _imagen_base(fondo="#FBFCFE", muro=NAVY)
    _dibujar_base(ax, img)
    _marcadores(ax)

    _titulo(
        fig,
        "Laberinto de la actividad",
        "31 columnas × 19 filas · 290 celdas transitables · inicio S y meta E",
    )
    fig.subplots_adjust(left=0.03, right=0.97, top=0.87, bottom=0.04)
    return _guardar(fig, "01_laberinto.png")


def figura_grafo() -> Path:
    """Esquema pequeño: celdas como nodos y adyacencias como aristas."""
    fig, ax = plt.subplots(figsize=(7.6, 5.2))
    ax.set_facecolor("white")

    paredes = {
        (0, 3), (1, 3), (3, 1), (3, 2), (3, 3),
    }
    abiertas = [
        (f, c) for f in range(5) for c in range(6) if (f, c) not in paredes
    ]

    # Aristas
    for f, c in abiertas:
        for df, dc in ((1, 0), (0, 1)):
            v = (f + df, c + dc)
            if v in abiertas:
                ax.plot(
                    [c, v[1]], [f, v[0]], color="#B9C7D4", lw=2.0, zorder=1,
                )

    # Nodos
    for f, c in abiertas:
        ax.add_patch(
            Circle(
                (c, f), 0.20, facecolor="white", edgecolor=NAVY,
                lw=1.8, zorder=3,
            )
        )

    # Muros
    for f, c in paredes:
        ax.add_patch(
            Rectangle(
                (c - 0.42, f - 0.42), 0.84, 0.84,
                facecolor="#DCE4EC", edgecolor="white", lw=1.5, zorder=2,
            )
        )

    ax.scatter([0], [0], s=300, c=GREEN, edgecolors="white", linewidths=2, zorder=5)
    ax.text(0, 0, "S", ha="center", va="center", color="white",
            fontweight="bold", fontsize=9, zorder=6)
    ax.scatter([5], [4], s=300, c=RED, edgecolors="white", linewidths=2, zorder=5)
    ax.text(5, 4, "E", ha="center", va="center", color="white",
            fontweight="bold", fontsize=9, zorder=6)

    # Anotaciones
    ax.annotate(
        "nodo = celda transitable", xy=(2, 2), xytext=(2.7, 3.9),
        fontsize=9.5, color=NAVY,
        arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.5,
                        connectionstyle="arc3,rad=-0.2"),
        zorder=7,
    )
    ax.annotate(
        "arista = movimiento\nentre celdas adyacentes", xy=(4.5, 1),
        xytext=(2.6, 0.2), fontsize=9.5, color=NAVY,
        arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.5,
                        connectionstyle="arc3,rad=0.2"),
        zorder=7,
    )
    ax.text(2.5, -0.95, "Grafo no dirigido y no ponderado (coste 1 por arista)",
            ha="center", fontsize=9.5, color=GRAY, style="italic")

    ax.set_xlim(-0.8, 5.8)
    ax.set_ylim(4.8, -1.2)
    ax.set_aspect("equal")
    ax.axis("off")

    _titulo(
        fig,
        "Del laberinto al grafo",
        "Cada celda libre es un nodo; cada paso permitido, una arista",
    )
    fig.subplots_adjust(left=0.02, right=0.98, top=0.85, bottom=0.02)
    return _guardar(fig, "08_grafo.png")


def _figura_solucion(resultado, color: str, nombre: str,
                     titulo: str, subtitulo: str) -> Path:
    fig, ax = plt.subplots(figsize=(9.2, 5.9))
    img = _imagen_base(fondo="#FBFCFE", muro=NAVY)
    _dibujar_base(ax, img)
    _camino(ax, resultado.camino, color)
    _marcadores(ax)

    _titulo(fig, titulo, subtitulo)
    fig.subplots_adjust(left=0.03, right=0.97, top=0.87, bottom=0.04)
    return _guardar(fig, nombre)


def figura_solucion_bfs(r) -> Path:
    return _figura_solucion(
        r, BLUE, "02_solucion_bfs.png",
        "Solución con BFS",
        f"{r.longitud_camino} celdas · {r.coste} movimientos · "
        f"{r.expandidos} nodos expandidos · camino óptimo",
    )


def figura_solucion_dfs(r) -> Path:
    return _figura_solucion(
        r, ORANGE, "03_solucion_dfs.png",
        "Solución con DFS",
        f"{r.longitud_camino} celdas · {r.coste} movimientos · "
        f"{r.expandidos} nodos expandidos · camino no óptimo",
    )


def _figura_exploracion(resultado, nombre: str, titulo: str,
                        subtitulo: str, color_ini: str, color_fin: str) -> Path:
    fig, ax = plt.subplots(figsize=(9.6, 5.9))
    img = _imagen_base(fondo="#FFFFFF", muro="#D2DCE6")
    cmap = LinearSegmentedColormap.from_list("orden", [color_ini, color_fin])
    n = max(1, len(resultado.orden_expansion))
    colores = [cmap(i / max(1, n - 1)) for i in range(n)]
    _pintar_celdas(img, resultado.orden_expansion, colores)
    _dibujar_base(ax, img)
    _camino(ax, resultado.camino, NAVY, grosor=2.2)
    _marcadores(ax, tamano=200)

    sm = ScalarMappable(norm=Normalize(0, n), cmap=cmap)
    sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, fraction=0.030, pad=0.02, shrink=0.86)
    cb.set_label("orden de expansión", color=GRAY, fontsize=9)
    cb.ax.tick_params(labelsize=8, colors=GRAY)
    cb.outline.set_edgecolor("#D2DCE6")

    _titulo(fig, titulo, subtitulo)
    fig.subplots_adjust(left=0.03, right=0.95, top=0.86, bottom=0.04)
    return _guardar(fig, nombre)


def figura_exploracion_bfs(r) -> Path:
    return _figura_exploracion(
        r, "04_exploracion_bfs.png",
        "Exploración de BFS",
        "Los nodos se expanden por niveles (oleadas): claro = antes, oscuro = después",
        "#D6E8F7", "#0D4F86",
    )


def figura_exploracion_dfs(r) -> Path:
    return _figura_exploracion(
        r, "05_exploracion_dfs.png",
        "Exploración de DFS",
        "DFS se adentra en una rama y retrocede: claro = antes, oscuro = después",
        "#FBE4D2", "#A64B13",
    )


def figura_comparacion(r_bfs, r_dfs, t_bfs_ms: float, t_dfs_ms: float) -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(9.6, 6.4))
    fig.patch.set_facecolor("white")
    fig.suptitle(
        "BFS vs DFS: comparación cuantitativa", fontsize=17,
        fontweight="bold", color=NAVY, y=0.985,
    )

    datos = [
        ("Nodos expandidos", r_bfs.expandidos, r_dfs.expandidos, "{:.0f}"),
        ("Aristas evaluadas", r_bfs.aristas_evaluadas, r_dfs.aristas_evaluadas, "{:.0f}"),
        ("Longitud del camino (celdas)", r_bfs.longitud_camino, r_dfs.longitud_camino, "{:.0f}"),
        ("Tiempo medio (ms)", t_bfs_ms, t_dfs_ms, "{:.3f}"),
    ]
    for ax, (titulo, v_bfs, v_dfs, fmt) in zip(axes.flat, datos):
        valores = [v_bfs, v_dfs]
        barras = ax.bar(
            ["BFS", "DFS"], valores, color=[BLUE, ORANGE],
            width=0.55, edgecolor="white", linewidth=1.5, zorder=3,
        )
        for barra, valor in zip(barras, valores):
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                barra.get_height() + max(valores) * 0.025,
                fmt.format(valor), ha="center", va="bottom",
                fontsize=11, fontweight="bold", color=NAVY,
            )
        ax.set_title(titulo, fontsize=11.5, color=NAVY, pad=8)
        ax.set_ylim(0, max(valores) * 1.22)
        ax.grid(axis="y", color="#E3E9F0", lw=0.9, zorder=0)
        ax.set_axisbelow(True)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
        ax.spines["left"].set_color("#C9D4DE")
        ax.spines["bottom"].set_color("#C9D4DE")
        ax.tick_params(axis="both", labelsize=9.5, colors=NAVY)
        ax.set_ylabel("")

    leyenda = [
        Line2D([0], [0], color=BLUE, lw=8, label="BFS"),
        Line2D([0], [0], color=ORANGE, lw=8, label="DFS"),
    ]
    fig.legend(
        handles=leyenda, loc="lower center", ncol=2, frameon=False,
        fontsize=10, bbox_to_anchor=(0.5, 0.005),
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    return _guardar(fig, "06_comparacion.png")


def figura_frontera(r_bfs, r_dfs) -> Path:
    fig, ax = plt.subplots(figsize=(9.2, 4.9))
    fig.patch.set_facecolor("white")

    x_b = np.arange(1, len(r_bfs.historial_frontera) + 1)
    x_d = np.arange(1, len(r_dfs.historial_frontera) + 1)
    ax.plot(x_b, r_bfs.historial_frontera, color=BLUE, lw=2.4, label="BFS")
    ax.fill_between(x_b, r_bfs.historial_frontera, color=BLUE, alpha=0.12)
    ax.plot(x_d, r_dfs.historial_frontera, color=ORANGE, lw=2.4, label="DFS")
    ax.fill_between(x_d, r_dfs.historial_frontera, color=ORANGE, alpha=0.12)

    max_b = max(r_bfs.historial_frontera)
    max_d = max(r_dfs.historial_frontera)
    ax.scatter([int(np.argmax(r_bfs.historial_frontera)) + 1], [max_b],
               color=BLUE, s=45, zorder=5)
    ax.scatter([int(np.argmax(r_dfs.historial_frontera)) + 1], [max_d],
               color=ORANGE, s=45, zorder=5)
    ax.annotate(
        f"máx. BFS = {max_b}", xy=(int(np.argmax(r_bfs.historial_frontera)) + 1, max_b),
        xytext=(8, 16), textcoords="offset points", fontsize=9.5, color=BLUE,
        fontweight="bold",
    )
    ax.annotate(
        f"máx. DFS = {max_d}", xy=(int(np.argmax(r_dfs.historial_frontera)) + 1, max_d),
        xytext=(8, -22), textcoords="offset points", fontsize=9.5, color=ORANGE,
        fontweight="bold",
    )

    ax.set_xlabel("nodo expandido (paso)")
    ax.set_ylabel("tamaño de la frontera")
    ax.grid(color="#E3E9F0", lw=0.9)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.spines["left"].set_color("#C9D4DE")
    ax.spines["bottom"].set_color("#C9D4DE")
    ax.tick_params(colors=NAVY)
    ax.legend(frameon=False, fontsize=10, loc="upper right")

    fig.suptitle(
        "Evolución de la frontera durante la búsqueda", fontsize=16,
        fontweight="bold", color=NAVY, y=0.975,
    )
    fig.text(
        0.5, 0.905, "Cada punto indica cuántos nodos esperaban ser expandidos",
        ha="center", fontsize=10, color=GRAY,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    return _guardar(fig, "07_frontera.png")


def generar_figuras() -> dict:
    print("Generando figuras ...")
    r_bfs = bfs()
    r_dfs = dfs()

    # Tiempos leídos del informe generado por codigo/main.py (si existe)
    t_bfs_ms, t_dfs_ms = 0.0, 0.0
    informe = BASE_DIR / "resultados_ejecucion_2.4.txt"
    if informe.exists():
        for linea in informe.read_text(encoding="utf-8").splitlines():
            partes = linea.split(";")
            if len(partes) == 3 and partes[0] == "Tiempo medio (ms)":
                t_bfs_ms, t_dfs_ms = float(partes[1]), float(partes[2])
                break
    if t_bfs_ms == 0.0:
        from busqueda_ciega import medir_tiempo_promedio

        t_bfs_ms = medir_tiempo_promedio(bfs) * 1000
        t_dfs_ms = medir_tiempo_promedio(dfs) * 1000

    figura_portada()
    figura_laberinto()
    figura_grafo()
    figura_solucion_bfs(r_bfs)
    figura_solucion_dfs(r_dfs)
    figura_exploracion_bfs(r_bfs)
    figura_exploracion_dfs(r_dfs)
    figura_comparacion(r_bfs, r_dfs, t_bfs_ms, t_dfs_ms)
    figura_frontera(r_bfs, r_dfs)
    return {"bfs": r_bfs, "dfs": r_dfs, "t_bfs": t_bfs_ms, "t_dfs": t_dfs_ms}


if __name__ == "__main__":
    generar_figuras()
    print("Figuras generadas en", FIGURAS_DIR)
