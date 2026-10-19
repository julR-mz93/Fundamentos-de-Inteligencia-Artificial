#!/usr/bin/env python3
"""
Construcción de grafos con NetworkX — Actividades 2.1 y 2.2.

Toma los problemas modelados en generador_estados.py y los representa como
grafos DIRIGIDOS y PONDERADOS (nx.DiGraph con el atributo `weight`), generando
además las figuras de la carpeta ../figuras:

  1. problema1_red_calles.png       red urbana (espacio de estados P1)
  2. problema1_arbol_estados.png    árbol de generación de estados (BFS)
  3. problema1_solucion.png         rutas comparadas (BFS vs Dijkstra/A*)
  4. problema2_red_fisica.png       red física del dron (tiempos asimétricos)
  5. problema2_espacio_estados.png  espacio de estados generado (34 estados)
  6. problema2_solucion.png         solución óptima resaltada en el espacio

Uso directo:  python3 construir_grafos.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch

from generador_estados import (
    BASE,
    NOMBRES_RED,
    POSICIONES_DRON,
    POSICIONES_RED,
    PUNTOS_ENTREGA,
    RED_CALLES,
    TIEMPOS_VUELO,
    GeneradorRutaDron,
    GeneradorRuteoAmbulancia,
    EspacioEstados,
    explorar_espacio,
)

FIGURAS_DIR = Path(__file__).resolve().parent.parent / "figuras"

AZUL = "#1B2A4A"
NARANJA = "#E67E22"
VERDE = "#1E8449"
ROJO = "#C0392B"
MORADO = "#7D3C98"
GRIS = "#7F8C8D"


# --- Wrappers: NetworkX 3.7 ya no acepta `zorder` como argumento, así que lo
# --- aplicamos sobre los artistas devueltos (control del orden de dibujo).
def _aplicar_zorder(artistas, z: int):
    if artistas is None:
        return None
    if isinstance(artistas, dict):
        for a in artistas.values():
            a.set_zorder(z)
    else:
        try:
            artistas.set_zorder(z)
        except AttributeError:
            for a in artistas:
                try:
                    a.set_zorder(z)
                except AttributeError:
                    pass
    return artistas


def _dx_nodes(g, pos, *, zorder=None, **kw):
    coll = getattr(nx, "draw_networkx_nodes")(g, pos, **kw)
    return coll if zorder is None else _aplicar_zorder(coll, zorder)


def _dx_edges(g, pos, *, zorder=None, **kw):
    coll = getattr(nx, "draw_networkx_edges")(g, pos, **kw)
    return coll if zorder is None else _aplicar_zorder(coll, zorder)


def _dx_labels(g, pos, labels=None, *, zorder=None, **kw):
    coll = getattr(nx, "draw_networkx_labels")(g, pos, labels=labels, **kw)
    return coll if zorder is None else _aplicar_zorder(coll, zorder)


def _dx_edge_labels(g, pos, *, zorder=None, **kw):
    coll = getattr(nx, "draw_networkx_edge_labels")(g, pos, **kw)
    return coll if zorder is None else _aplicar_zorder(coll, zorder)



# =========================================================================
# 1. Grafos dirigidos y ponderados
# =========================================================================

def grafo_red_calles() -> nx.DiGraph:
    """Grafo del problema 1: intersecciones (nodos) y calles (aristas dirigidas)."""
    g = nx.DiGraph()
    for nodo, nombre in NOMBRES_RED.items():
        g.add_node(nodo, nombre=nombre, pos=POSICIONES_RED[nodo])
    for (o, d), (minutos, calle) in RED_CALLES.items():
        g.add_edge(o, d, weight=minutos, calle=calle, label=f"{minutos:g}")
    return g


def grafo_red_dron() -> nx.DiGraph:
    """Grafo físico del problema 2: tiempos de vuelo asimétricos entre puntos."""
    g = nx.DiGraph()
    for nodo in [BASE, *PUNTOS_ENTREGA]:
        g.add_node(nodo, nombre=PUNTOS_ENTREGA.get(nodo, "Base"), pos=POSICIONES_DRON[nodo])
    for (o, d), minutos in TIEMPOS_VUELO.items():
        g.add_edge(o, d, weight=minutos, label=f"{minutos:g}")
    return g


def grafo_espacio_estados(espacio: EspacioEstados) -> nx.DiGraph:
    """
    Vuelca la exploración del generador de estados a un grafo dirigido:
    nodos = estados alcanzables, aristas = acciones con su coste (`weight`).
    El atributo `subset` (nivel de profundidad) permite dibujarlo por capas.
    """
    g = nx.DiGraph()
    for estado in espacio.estados:
        g.add_node(estado, subset=espacio.nivel[estado])
    for estado, transiciones in espacio.transiciones.items():
        for tr in transiciones:
            g.add_edge(tr.origen, tr.destino, weight=tr.coste,
                       accion=tr.accion, label=f"{tr.coste:g}")
    return g


# =========================================================================
# 2. Etiquetas y utilidades de dibujo
# =========================================================================

def etiqueta_estado_dron(estado) -> str:
    """Etiqueta compacta de un estado (nodo, entregas) del problema 2."""
    nodo, hechas = estado
    conjunto = "∅" if not hechas else "{" + ",".join(sorted(hechas)) + "}"
    return f"{nodo}\n{conjunto}"


def _dibujar_aristas(g: nx.DiGraph, pos: Dict, con_etiquetas: bool = True,
                     color_arista: str = GRIS, rad: float = 0.16) -> None:
    """Dibuja aristas con flechas; si hay par de aristas opuestas, las curva."""
    dibujadas = set()
    for o, d in g.edges():
        inversa = (d, o) in g.edges()
        estilo = dict(connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>",
                      mutation_scale=13, linewidth=1.3, color=color_arista,
                      shrinkA=13, shrinkB=13, zorder=2)
        if inversa:
            # cada dirección se curva hacia un lado distinto
            lado = rad if (d, o) in dibujadas else -rad
            estilo["connectionstyle"] = f"arc3,rad={lado:.2f}"
        dibujadas.add((o, d))
        plt.gca().add_patch(FancyArrowPatch(posA=pos[o], posB=pos[d], **estilo))
    if con_etiquetas:
        etiquetas = {(o, d): data.get("label", "") for o, d, data in g.edges(data=True)}
        _dx_edge_labels(
            g, pos, edge_labels=etiquetas, font_size=8.5, font_color="#34495E",
            rotate=False, label_pos=0.5, alpha=0.95,
        )


def _dibujar_nodos(g: nx.DiGraph, pos: Dict, *,
                   inicio=None, meta=None, destacados: Iterable = (),
                   tamano: int = 1500, fuente: int = 10,
                   etiquetas: Optional[Dict] = None) -> None:
    destacados = set(destacados)
    comunes = [n for n in g.nodes() if n not in destacados]
    if destacados:
        _dx_nodes(
            g, pos, nodelist=list(destacados), node_color=NARANJA,
            node_size=tamano, edgecolors=AZUL, linewidths=1.4, zorder=4,
        )
    _dx_nodes(
        g, pos, nodelist=comunes, node_color="white", node_size=tamano,
        edgecolors=AZUL, linewidths=1.4, zorder=3,
    )
    if etiquetas is None:
        etiquetas = {n: g.nodes[n].get("nombre", str(n)) for n in g.nodes()}
    _dx_labels(g, pos, etiquetas, font_size=fuente,
                            font_color=AZUL, font_weight="bold", zorder=5)


def _marcar(g: nx.DiGraph, pos: Dict, nodo, texto: str, color: str, dy: float) -> None:
    x, y = pos[nodo]
    plt.text(x, y + dy, texto, fontsize=9, color=color, ha="center",
             fontweight="bold", zorder=6)


# =========================================================================
# 3. Figuras del problema 1
# =========================================================================

def figura_red_calles(g: nx.DiGraph, ruta: Path) -> None:
    """Grafo del espacio de estados del problema 1 (dirigido y ponderado)."""
    pos = {n: d["pos"] for n, d in g.nodes(data=True)}
    plt.figure(figsize=(12.5, 7.4))
    _dibujar_aristas(g, pos, con_etiquetas=True)
    _dibujar_nodos(g, pos, tamano=2100, fuente=10.5)
    _marcar(g, pos, "A", "▲ INICIO", VERDE, 0.42)
    _marcar(g, pos, "L", "★ META", ROJO, -0.55)
    plt.title("Problema 1 — Espacio de estados del ruteo de la ambulancia\n"
              "grafo DIRIGIDO (sentidos únicos) y PONDERADO (minutos de traslado)",
              fontsize=13, fontweight="bold", color=AZUL, pad=14)
    leyenda = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white",
               markeredgecolor=AZUL, markersize=10, label="Estado (intersección)"),
        Line2D([0], [0], color=GRIS, lw=1.5, label="Arista dirigida = calle de sentido único"),
        Line2D([0], [0], marker="$→$", color="w", markersize=10,
               markerfacecolor="w", label="Etiqueta = coste en minutos"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=NARANJA,
               markeredgecolor=AZUL, markersize=10, label="Estados destacados"),
    ]
    plt.legend(handles=leyenda, loc="upper center", bbox_to_anchor=(0.5, -0.03),
               ncol=4, frameon=False, fontsize=9.5)
    plt.tight_layout()
    plt.savefig(ruta, dpi=150, facecolor="white")
    plt.close()
    print(f"  -> {ruta.name}")


def figura_arbol_estados(generador, espacio: EspacioEstados, ruta: Path) -> None:
    """Árbol de generación de estados en amplitud (BFS) para el problema 1."""
    # árbol BFS: cada estado se cuelga de su descubridor
    padre: Dict = {generador.estado_inicial: None}
    aristas = []
    for estado, transiciones in espacio.transiciones.items():
        for tr in transiciones:
            if tr.destino not in padre:
                padre[tr.destino] = estado
                aristas.append((estado, tr.destino, tr.coste))

    g_t = nx.DiGraph()
    g_t.add_nodes_from(espacio.estados)
    g_t.add_edges_from((o, d) for o, d, _ in aristas)
    # capas = niveles; nodos en orden de descubrimiento (BFS) para evitar
    # cruces innecesarios entre aristas
    capas: Dict[int, List] = {}
    for estado in espacio.estados:
        capas.setdefault(espacio.nivel[estado], []).append(estado)
    pos = nx.multipartite_layout(g_t, subset_key=capas, align="vertical", scale=2.4)

    etiquetas = {n: NOMBRES_RED[n] for n in g_t.nodes()}
    plt.figure(figsize=(13, 7.6))
    _dx_edges(
        g_t, pos, arrows=True, arrowstyle="-|>", arrowsize=13,
        edge_color="#5D6D7E", width=1.2, node_size=1600,
        connectionstyle="arc3,rad=0.05", zorder=2,
    )
    _dx_nodes(g_t, pos, node_color="white", node_size=1600,
                           edgecolors=AZUL, linewidths=1.4, zorder=3)
    _dx_labels(g_t, pos, etiquetas, font_size=9.5,
                            font_color=AZUL, font_weight="bold", zorder=4)
    # coste de cada acción en el árbol
    etiquetas_arista = {(o, d): f"{c:g} min" for o, d, c in aristas}
    _dx_edge_labels(g_t, pos, edge_labels=etiquetas_arista,
                                 font_size=8, font_color=NARANJA, rotate=False)
    plt.title("Problema 1 — Generación de estados en amplitud (BFS)\n"
              f"{espacio.num_estados} estados, {len(aristas)} transiciones, "
              f"{espacio.num_niveles} niveles",
              fontsize=13, fontweight="bold", color=AZUL, pad=14)
    # anotación de niveles (por debajo de la capa más baja)
    y_min = min(y for _, y in pos.values())
    y_max = max(y for _, y in pos.values())
    for nivel in range(espacio.num_niveles):
        xs = [pos[n][0] for n in g_t.nodes() if espacio.nivel[n] == nivel]
        if xs:
            plt.text(sum(xs) / len(xs), y_min - 1.7, f"nivel {nivel}",
                     ha="center", fontsize=9.5, color=GRIS, style="italic")
    plt.ylim(y_min - 2.6, y_max + 1.0)
    plt.tight_layout()
    plt.savefig(ruta, dpi=150, facecolor="white")
    plt.close()
    print(f"  -> {ruta.name}")


def figura_solucion_problema1(
    g: nx.DiGraph, rutas: Sequence[Tuple[List[str], str, str, str]], ruta: Path
) -> None:
    """Compara sobre el mismo mapa las rutas devueltas por los algoritmos."""
    pos = {n: d["pos"] for n, d in g.nodes(data=True)}
    plt.figure(figsize=(12.5, 7.4))
    _dibujar_aristas(g, pos, con_etiquetas=True, color_arista="#BDC3C7")
    _dibujar_nodos(g, pos, tamano=2100, fuente=10.5)

    leyenda = []
    for camino, color, etiqueta, estilo in rutas:
        aristas = list(zip(camino, camino[1:]))
        _dx_edges(
            g, pos, edgelist=aristas, edge_color=color, width=3.4,
            arrows=True, arrowstyle="-|>",
            style=estilo, connectionstyle="arc3,rad=0.0", zorder=5,
            node_size=2100, arrowsize=18,
        )
        coste = sum(g[o][d]["weight"] for o, d in aristas)
        leyenda.append(Line2D([0], [0], color=color, lw=3.5, linestyle=estilo,
                              label=f"{etiqueta} — {coste:g} min ({len(aristas)} calles)"))
    _marcar(g, pos, "A", "▲ INICIO", VERDE, 0.42)
    _marcar(g, pos, "L", "★ META", ROJO, -0.55)
    plt.title("Problema 1 — Comparación de rutas: mínimos aristas vs mínimo coste",
              fontsize=13, fontweight="bold", color=AZUL, pad=14)
    plt.legend(handles=leyenda, loc="upper center", bbox_to_anchor=(0.5, -0.03),
               ncol=3, frameon=False, fontsize=10)
    plt.tight_layout()
    plt.savefig(ruta, dpi=150, facecolor="white")
    plt.close()
    print(f"  -> {ruta.name}")


# =========================================================================
# 4. Figuras del problema 2
# =========================================================================

def figura_red_dron(g: nx.DiGraph, ruta: Path) -> None:
    """Red física del dron: 7 nodos, aristas dirigidas y ponderadas (minutos)."""
    pos = {n: d["pos"] for n, d in g.nodes(data=True)}
    plt.figure(figsize=(11.5, 7))
    _dibujar_aristas(g, pos, con_etiquetas=True, rad=0.22)
    _dibujar_nodos(g, pos, tamano=2600, fuente=10.5)
    _marcar(g, pos, "BASE", "▲ BASE", VERDE, 0.45)
    plt.title("Problema 2 — Red física del dron (tiempos de vuelo asimétricos)\n"
              "grafo DIRIGIDO y PONDERADO: un trayecto no cuesta lo mismo que su inverso",
              fontsize=13, fontweight="bold", color=AZUL, pad=14)
    leyenda = [
        Line2D([0], [0], color=GRIS, lw=1.5, label="Arista dirigida = corredor aéreo"),
        Line2D([0], [0], color="#BDC3C7", lw=1.5, label="Etiqueta = minutos de vuelo"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white",
               markeredgecolor=AZUL, markersize=10, label="Punto (nodo del grafo)"),
    ]
    plt.legend(handles=leyenda, loc="upper center", bbox_to_anchor=(0.5, -0.03),
               ncol=3, frameon=False, fontsize=9.5)
    plt.tight_layout()
    plt.savefig(ruta, dpi=150, facecolor="white")
    plt.close()
    print(f"  -> {ruta.name}")


def _dibujar_espacio_dron(g: nx.DiGraph, espacio: EspacioEstados, *,
                          resaltar_aristas: Sequence = (),
                          resaltar_estados: Sequence = (),
                          etiquetas_aristas: Optional[Dict] = None) -> None:
    """Dibuja el espacio de estados del problema 2 por niveles (capas)."""
    capas: Dict[int, List] = {}
    for estado in espacio.estados:
        capas.setdefault(espacio.nivel[estado], []).append(estado)
    pos = nx.multipartite_layout(g, subset_key=capas, align="vertical", scale=3.0)
    cmap = plt.get_cmap("viridis")
    max_nivel = max(espacio.nivel.values())
    resaltar_aristas = [tuple(a) for a in resaltar_aristas]

    _dx_edges(
        g, pos, arrows=True, arrowstyle="-|>", arrowsize=11,
        edge_color="#D5DBDB", width=0.9, node_size=900,
        connectionstyle="arc3,rad=0.06", zorder=2,
        min_source_margin=9, min_target_margin=9,
    )
    if resaltar_aristas:
        _dx_edges(
            g, pos, edgelist=resaltar_aristas, arrows=True, arrowstyle="-|>",
            arrowsize=17, edge_color=VERDE, width=3.0, node_size=900,
            connectionstyle="arc3,rad=0.06", zorder=5,
            min_source_margin=9, min_target_margin=9,
        )
    niveles = [g.nodes[n]["subset"] for n in g.nodes()]
    _dx_nodes(
        g, pos, node_color=[cmap(0.15 + 0.7 * n / max(1, max_nivel)) for n in niveles],
        node_size=900, edgecolors="white", linewidths=1.0, zorder=3,
    )
    if resaltar_estados:
        _dx_nodes(
            g, pos, nodelist=list(resaltar_estados), node_color=NARANJA,
            node_size=1000, edgecolors="white", linewidths=1.5, zorder=4,
        )
    etiquetas = {n: etiqueta_estado_dron(n) for n in g.nodes()}
    _dx_labels(g, pos, etiquetas, font_size=7.4,
                            font_color="white", font_weight="bold", zorder=6)
    if etiquetas_aristas:
        _dx_edge_labels(g, pos, edge_labels=etiquetas_aristas,
                                     font_size=7.5, font_color=VERDE, rotate=False)
    y_min = min(y for _, y in pos.values())
    y_max = max(y for _, y in pos.values())
    for nivel in range(max_nivel + 1):
        xs = [pos[n][0] for n in g.nodes() if g.nodes[n]["subset"] == nivel]
        if xs:
            plt.text(sum(xs) / len(xs), y_min - 2.1, f"nivel {nivel}", ha="center",
                     fontsize=10, color=GRIS, style="italic")
    plt.ylim(y_min - 3.4, y_max + 1.6)
    plt.tight_layout()


def figura_espacio_dron(g: nx.DiGraph, espacio: EspacioEstados, ruta: Path) -> None:
    """Figura del espacio de estados generado para el problema 2."""
    plt.figure(figsize=(15.5, 9))
    _dibujar_espacio_dron(g, espacio)
    plt.title(
        "Problema 2 — Espacio de estados del reparto del dron\n"
        f"{g.number_of_nodes()} estados, {g.number_of_edges()} transiciones; "
        "estado = (nodo actual, entregas realizadas)",
        fontsize=13, fontweight="bold", color=AZUL, pad=14,
    )
    plt.savefig(ruta, dpi=150, facecolor="white")
    plt.close()
    print(f"  -> {ruta.name}")


def figura_solucion_dron(g: nx.DiGraph, espacio: EspacioEstados,
                         camino: Sequence, coste: float, ruta: Path) -> None:
    """Espacio de estados con la solución óptima resaltada y su coste acumulado."""
    aristas = list(zip(camino, camino[1:]))
    acumulado = 0.0
    etiquetas_sol: Dict = {}
    for o, d in aristas:
        acumulado += g[o][d]["weight"]
        etiquetas_sol[(o, d)] = f"{g[o][d]['weight']:g} min\n(acum. {acumulado:g})"

    plt.figure(figsize=(15.5, 9))
    _dibujar_espacio_dron(g, espacio, resaltar_aristas=aristas,
                          resaltar_estados=camino, etiquetas_aristas=etiquetas_sol)
    plt.title(
        "Problema 2 — Solución óptima en el espacio de estados (Dijkstra)\n"
        f"coste total = {coste:g} minutos · estados de la ruta en naranja",
        fontsize=13, fontweight="bold", color=AZUL, pad=14,
    )
    plt.savefig(ruta, dpi=150, facecolor="white")
    plt.close()
    print(f"  -> {ruta.name}")


# =========================================================================
# 5. Programa principal del módulo (sólo grafos y figuras)
# =========================================================================

def main() -> None:
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    print("Construyendo grafos y figuras ...")

    # --- Problema 1 ------------------------------------------------------
    g1 = grafo_red_calles()
    gen1 = GeneradorRuteoAmbulancia()
    esp1 = explorar_espacio(gen1)
    figura_red_calles(g1, FIGURAS_DIR / "problema1_red_calles.png")
    figura_arbol_estados(gen1, esp1, FIGURAS_DIR / "problema1_arbol_estados.png")

    # --- Problema 2 ------------------------------------------------------
    g2 = grafo_red_dron()
    gen2 = GeneradorRutaDron()
    esp2 = explorar_espacio(gen2)
    g2_estados = grafo_espacio_estados(esp2)
    figura_red_dron(g2, FIGURAS_DIR / "problema2_red_fisica.png")
    figura_espacio_dron(g2_estados, esp2, FIGURAS_DIR / "problema2_espacio_estados.png")

    print(
        f"  [datos] P1: {g1.number_of_nodes()} estados / "
        f"{g1.number_of_edges()} transiciones | "
        f"P2: {g2_estados.number_of_nodes()} estados / "
        f"{g2_estados.number_of_edges()} transiciones"
    )


if __name__ == "__main__":
    main()
