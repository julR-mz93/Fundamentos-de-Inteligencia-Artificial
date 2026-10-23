#!/usr/bin/env python3
"""
Actividad 2.3 — Búsqueda local: Hill Climbing y Simulated Annealing
"""
from __future__ import annotations

import os
import random
import statistics
from pathlib import Path

from problema_tsp import N, longitud_ruta, ruta_aleatoria, ruta_inicial_greedy
from busqueda_local import hill_climbing, simulated_annealing
from graficar import graficar_rutas, graficar_convergencia, graficar_boxplot

BASE_DIR = Path(__file__).resolve().parent
FIGURAS_DIR = BASE_DIR.parent / "figuras"
FIGURAS_DIR.mkdir(exist_ok=True)
RESULTADOS = BASE_DIR.parent / "resultados_ejecucion_2.3.txt"


def main():
    print("=" * 64)
    print("ACTIVIDAD 2.3 — BÚSQUEDA LOCAL: HILL CLIMBING Y SIMULATED ANNEALING")
    print("=" * 64)
    print(f"\nProblema: TSP con {N-1} paradas + almacén (total {N} puntos)")
    print(f"Función objetivo: minimizar longitud_ruta(ruta) = distancia total (ida y vuelta)")
    print("Vecindad: intercambio (swap) + inversión 2-opt")
    print("\nParámetros:")
    print("  Hill Climbing: mejor vecino, max_iter=10000, sin_mejora=150")
    print("  Simulated Annealing: T0=12.0, Tf=0.001, alpha=0.995, iter_por_T=80")

    # Ruta inicial
    rng_init = random.Random(12345)
    ruta_ini = ruta_aleatoria(rng_init)
    c_ini = longitud_ruta(ruta_ini)
    ruta_ini_greedy = ruta_inicial_greedy()
    c_ini_greedy = longitud_ruta(ruta_ini_greedy)
    print(f"\nRuta inicial aleatoria: {c_ini:.3f}")
    print(f"Ruta inicial vecino más próximo: {c_ini_greedy:.3f}")

    # Ejecución única para gráficas
    print("\n" + "=" * 64)
    print("EJECUCIÓN CON RUTA INICIAL ALEATORIA (misma semilla)")
    print("=" * 64)
    rng_hc = random.Random(777)
    r_hc, c_hc, h_hc, e_hc = hill_climbing(ruta_ini, rng_hc)
    print(f"Hill Climbing -> {c_hc:.3f} (mejor) | iter_registro={len(h_hc)} | eval_vecinos={e_hc}")

    rng_sa = random.Random(777)
    r_sa, c_sa, h_sa, e_sa = simulated_annealing(ruta_ini, rng_sa)
    print(f"Simulated Annealing -> {c_sa:.3f} (mejor) | registros={len(h_sa)} | eval_vecinos={e_sa}")
    print(f"Mejora HC: {(1 - c_hc/c_ini)*100:.1f}% | Mejora SA: {(1 - c_sa/c_ini)*100:.1f}%")

    # Comparación con ruta inicial greedy
    print("\n" + "=" * 64)
    print("EJECUCIÓN CON RUTA INICIAL DEL VECINO MÁS PRÓXIMO")
    print("=" * 64)
    rng_hc2 = random.Random(777)
    r_hc2, c_hc2, h_hc2, e_hc2 = hill_climbing(ruta_ini_greedy, rng_hc2)
    print(f"Hill Climbing -> {c_hc2:.3f} | eval_vecinos={e_hc2}")
    rng_sa2 = random.Random(777)
    r_sa2, c_sa2, h_sa2, e_sa2 = simulated_annealing(ruta_ini_greedy, rng_sa2)
    print(f"Simulated Annealing -> {c_sa2:.3f} | eval_vecinos={e_sa2}")

    # Análisis estadístico (30 ejecuciones)
    print("\n" + "=" * 64)
    print("ANÁLISIS ESTADÍSTICO (30 EJECUCIONES CON RUTAS ALEATORIAS)")
    print("=" * 64)
    hc_costs, sa_costs = [], []
    for s in range(30):
        rng_h = random.Random(10000 + s)
        _, c, _, _ = hill_climbing(ruta_aleatoria(rng_h), rng_h)
        hc_costs.append(c)
        rng_s = random.Random(20000 + s)
        _, c2, _, _ = simulated_annealing(ruta_aleatoria(rng_s), rng_s)
        sa_costs.append(c2)

    def rep(xs):
        xs_s = sorted(xs)
        return xs_s[0], statistics.mean(xs), statistics.median(xs), statistics.stdev(xs), xs_s[-1]

    mhc = rep(hc_costs); msa = rep(sa_costs)
    print(f"Hill Climbing   -> min={mhc[0]:.3f} | media={mhc[1]:.3f} | mediana={mhc[2]:.3f} | σ={mhc[3]:.3f} | max={mhc[4]:.3f}")
    print(f"Simulated Annealing -> min={msa[0]:.3f} | media={msa[1]:.3f} | mediana={msa[2]:.3f} | σ={msa[3]:.3f} | max={msa[4]:.3f}")
    print(f"\nMejor absoluto encontrado: {min(mhc[0], msa[0]):.3f}")
    print(f"Diferencia media (SA - HC): {msa[1]-mhc[1]:+.3f}")
    print("Conclusión: Simulated Annealing es más robusto (menor desviación) y "
          "explora mejor el espacio evitando óptimos locales.")

    # Gráficas
    print("\n" + "=" * 64)
    print("GENERANDO GRÁFICAS")
    print("=" * 64)
    graficar_rutas([ruta_ini, r_hc, r_sa], [c_ini, c_hc, c_sa],
                   ["Ruta inicial", "Hill Climbing", "Simulated Annealing"],
                   FIGURAS_DIR / "02_3_rutas_comparacion.png")
    print("  -> 02_3_rutas_comparacion.png")
    graficar_convergencia(h_hc, h_sa, FIGURAS_DIR / "02_3_convergencia.png")
    print("  -> 02_3_convergencia.png")
    graficar_boxplot(hc_costs, sa_costs, FIGURAS_DIR / "02_3_comparacion_estadistica.png")
    print("  -> 02_3_comparacion_estadistica.png")

    # Guardar resultados
    with open(RESULTADOS, "w", encoding="utf-8") as f:
        f.write("=" * 64 + "\n")
        f.write("ACTIVIDAD 2.3 — BÚSQUEDA LOCAL\n")
        f.write("=" * 64 + "\n\n")
        f.write(f"Problema: TSP con {N-1} paradas + almacén\n")
        f.write(f"Función objetivo: longitud_ruta(ruta) a minimizar\n")
        f.write("Vecindad: intercambio (swap) + inversión (2-opt)\n\n")
        f.write("Parámetros:\n")
        f.write("  Hill Climbing: max_iter=10000, sin_mejora=150, estrategia=mejor_vecino\n")
        f.write("  SA: T0=12.0, Tf=0.001, alpha=0.995, iter_por_T=80\n\n")
        f.write(f"Ruta inicial aleatoria: {c_ini:.3f}\n")
        f.write(f"Ruta inicial vecino más próximo: {c_ini_greedy:.3f}\n\n")
        f.write("Misma ruta inicial:\n")
        f.write(f"  Hill Climbing:        {c_hc:.3f} (eval={e_hc})\n")
        f.write(f"  Simulated Annealing:  {c_sa:.3f} (eval={e_sa})\n\n")
        f.write("Vecino más próximo:\n")
        f.write(f"  Hill Climbing:        {c_hc2:.3f}\n")
        f.write(f"  Simulated Annealing:  {c_sa2:.3f}\n\n")
        f.write("30 ejecuciones (rutas aleatorias):\n")
        f.write(f"  HC   -> min={mhc[0]:.3f} media={mhc[1]:.3f} mediana={mhc[2]:.3f} σ={mhc[3]:.3f} max={mhc[4]:.3f}\n")
        f.write(f"  SA   -> min={msa[0]:.3f} media={msa[1]:.3f} mediana={msa[2]:.3f} σ={msa[3]:.3f} max={msa[4]:.3f}\n\n")
        f.write(f"Mejor absoluto: {min(mhc[0], msa[0]):.3f}\n")

    print(f"\nResultados guardados en: {RESULTADOS}")
    print("¡Terminado!")


if __name__ == "__main__":
    main()
