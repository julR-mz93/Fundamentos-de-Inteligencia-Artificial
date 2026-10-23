#!/usr/bin/env python3
"""
Generación de gráficas para la Actividad 2.3.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from problema_tsp import DEPOT, N, PUNTOS, longitud_ruta


def ruta_a_puntos(ruta):
    xs, ys = [], []
    for i in ruta:
        xs.append(PUNTOS[i][0]); ys.append(PUNTOS[i][1])
    xs.append(PUNTOS[ruta[0]][0]); ys.append(PUNTOS[ruta[0]][1])
    return xs, ys


def graficar_rutas(rutas, costos, nombres, salida: Path):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, ruta, c, nombre in zip(axes, rutas, costos, nombres):
        xs, ys = ruta_a_puntos(ruta)
        ax.plot(xs, ys, "-o", linewidth=1.6, markersize=5)
        for i, p in enumerate(PUNTOS):
            ax.scatter(p[0], p[1], s=40, zorder=5)
            if i == 0:
                ax.text(p[0] + 0.12, p[1] + 0.12, "ALMACÉN", fontsize=7)
            else:
                ax.text(p[0] + 0.08, p[1] + 0.08, str(i), fontsize=7)
        ax.set_title(f"{nombre}\nLongitud: {c:.3f}", fontsize=10)
        ax.set_xlabel("X"); ax.set_ylabel("Y")
        ax.grid(True, alpha=0.3)
    fig.suptitle(f"Comparación de rutas — TSP con {N-1} paradas", fontsize=11)
    fig.tight_layout()
    fig.savefig(salida, dpi=150)
    plt.close(fig)


def graficar_convergencia(hist_hc, hist_sa, salida: Path):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(hist_hc, label="Hill Climbing (mejor vecino)", linewidth=1.8)
    ax.plot(hist_sa, label="Simulated Annealing", linewidth=1.8)
    ax.set_xlabel("Iteración / registro")
    ax.set_ylabel("Costo (distancia total)")
    ax.set_title("Gráfica de convergencia — Hill Climbing vs Simulated Annealing")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(salida, dpi=150)
    plt.close(fig)


def graficar_boxplot(costos_hc, costos_sa, salida: Path):
    fig, ax = plt.subplots(figsize=(7, 5))
    bp = ax.boxplot([costos_hc, costos_sa], showmeans=True)
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["Hill Climbing", "Simulated Annealing"])
    ax.set_ylabel("Costo final (distancia total)")
    ax.set_title(f"Comparación estadística (30 ejecuciones, {N-1} paradas)")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(salida, dpi=150)
    plt.close(fig)
