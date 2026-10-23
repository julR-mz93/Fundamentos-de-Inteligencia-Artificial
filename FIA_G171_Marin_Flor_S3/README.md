# Actividad 2.3 — Búsqueda local (Hill Climbing y Simulated Annealing)

**Alumno:** Julissa Marin Flor  
**Asignatura:** Fundamentos de Inteligencia Artificial  
**Docente:** Javier García Lara  
**Institución:** Universidad Politécnica de Atlautla  
**Fecha:** 22 de octubre de 2026

## Objetivo
Implementar y optimizar los algoritmos **Hill Climbing** y **Simulated Annealing** para resolver un problema de optimización real: el **Problema del Viajante (TSP)** de ruta mínima de reparto.

## Estructura del repositorio
```
FIA_G171_Marin_Flor_S3/
├── memoria_actividad_2.3.pdf   # Memoria (Word/PDF) con todo lo solicitado
├── memoria_actividad_2.3.docx  # Versión editable
├── generar_memoria_2.3.py      # Script para regenerar la memoria
├── resultados_ejecucion_2.3.txt
├── codigo/                     # Código fuente
│   ├── main.py
│   ├── problema_tsp.py
│   ├── busqueda_local.py
│   ├── graficar.py
│   ├── requirements.txt
│   └── README.md
└── figuras/                    # Gráficas generadas
    ├── 02_3_convergencia.png
    ├── 02_3_rutas_comparacion.png
    └── 02_3_comparacion_estadistica.png
```

## Lo que contiene la memoria
- [x] Enunciado
- [x] Función, objetivo y representación
- [x] Vecindad (intercambio + 2-opt)
- [x] Parámetros (T, iteraciones, n)
- [x] Gráfica de convergencia
- [x] Comparación de rutas y resultados
- [x] Análisis estadístico (30 ejecuciones)
- [x] Conclusiones y referencias

## Ejecución rápida
```bash
cd codigo
pip install -r requirements.txt
python main.py
```

## Resultados destacados
Simulated Annealing resulta más robusto frente a óptimos locales y presenta menor variabilidad entre ejecuciones, especialmente partiendo de rutas aleatorias.
