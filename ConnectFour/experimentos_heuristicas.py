"""Experimentos sobre funciones de evaluación (C03).

Uso, desde ``ConnectFour/``:
    poetry run python experimentos_heuristicas.py CNT-003 [--partidas 500] [--id CNT-003-r1]

Si la carpeta de salida ya existe, el comando falla sin escribir nada.

CNT-003 aplica los criterios de diseño del teórico a cada término ``fᵢ``:
  (2) costo de cálculo: tiempo medio por evaluación;
  (3) correlación de ``fᵢ(s)`` con el resultado real de la partida.
"""
import argparse
import statistics
import time
from pathlib import Path

import numpy as np

from agentes_base import AgenteAleatorio
from arena import jugar_partida
from board import Board
from heuristicas import TERMINOS, FuncionEvaluacion
from registro import CARPETA_EXPERIMENTOS, guardar_corrida

ETAPAS = (("apertura", 1, 10), ("medio", 11, 20), ("final", 21, 42))


def posiciones_de_partida(jugadas):
    """Estados no finales tras cada jugada, con la cantidad de fichas jugadas."""
    tablero, jugador = Board(6, 7), 1
    for numero, columna in enumerate(jugadas, start=1):
        tablero.add_tile(columna, jugador)
        jugador = 2 if jugador == 1 else 1
        if not tablero.is_final():
            yield numero, tablero.clone()


def correlacion(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) < 3 or x.std() == 0 or y.std() == 0:
        return None
    return round(float(np.corrcoef(x, y)[0, 1]), 4)


def acierto_de_signo(x, y):
    """Proporción de posiciones con fᵢ ≠ 0 y partida decidida en que el signo coincide."""
    pares = [(a, b) for a, b in zip(x, y) if a != 0 and b != 0]
    if not pares:
        return None
    return round(sum((a > 0) == (b > 0) for a, b in pares) / len(pares), 4)


def cnt_003(partidas):
    filas = []
    for semilla in range(partidas):
        resultado = jugar_partida(AgenteAleatorio(semilla), AgenteAleatorio(10_000 + semilla))
        desenlace = {0: 0, 1: 1, 2: -1}[resultado.ganador]  # visto desde el jugador 1
        for numero, tablero in posiciones_de_partida(resultado.jugadas):
            fila = {"partida": semilla, "jugada": numero, "resultado_j1": desenlace}
            fila.update({t: f(tablero, 1) for t, f in TERMINOS.items()})
            filas.append(fila)

    # Costo: tiempo medio de cada término sobre una muestra fija de posiciones.
    muestra = []
    for semilla in range(50):
        jugadas = jugar_partida(AgenteAleatorio(semilla), AgenteAleatorio(10_000 + semilla)).jugadas
        muestra.extend(t for _, t in posiciones_de_partida(jugadas))
    costos = {}
    combinada = FuncionEvaluacion({t: 1 for t in TERMINOS}, nombre="todos_peso_1")
    for nombre, funcion in list(TERMINOS.items()) + [(combinada.nombre, combinada)]:
        inicio = time.perf_counter()
        for _ in range(5):
            for tablero in muestra:
                funcion(tablero, 1)
        costos[nombre] = round((time.perf_counter() - inicio) / (5 * len(muestra)) * 1e6, 2)

    resultados = [f["resultado_j1"] for f in filas]
    resumen_terminos = {}
    for t in TERMINOS:
        valores = [f[t] for f in filas]
        por_etapa = {}
        for etapa, desde, hasta in ETAPAS:
            sub = [f for f in filas if desde <= f["jugada"] <= hasta]
            por_etapa[etapa] = {
                "posiciones": len(sub),
                "correlacion": correlacion([f[t] for f in sub], [f["resultado_j1"] for f in sub]),
            }
        resumen_terminos[t] = {
            "correlacion": correlacion(valores, resultados),
            "acierto_de_signo": acierto_de_signo(valores, resultados),
            "media": round(statistics.fmean(valores), 3),
            "por_etapa": por_etapa,
            "costo_us_por_evaluacion": costos[t],
        }

    ganadores = [f["resultado_j1"] for f in filas if f["jugada"] == 1]
    resumen = {
        "partidas": partidas,
        "posiciones": len(filas),
        "victorias_j1": ganadores.count(1),
        "victorias_j2": ganadores.count(-1),
        "empates": ganadores.count(0),
        "costo_us_combinacion_todos_peso_1": costos[combinada.nombre],
        "terminos": resumen_terminos,
    }
    configuracion = {
        "pregunta": (
            "Criterios 2 y 3 del teórico: ¿cuánto cuesta cada término y qué tan "
            "correlacionado está con el resultado real?"
        ),
        "partidas": f"AgenteAleatorio(s) contra AgenteAleatorio(10000 + s), s = 0..{partidas - 1}",
        "posiciones": "todos los estados no finales después de cada jugada",
        "perspectiva": "jugador 1; resultado +1 victoria, 0 empate, -1 derrota",
        "etapas": {e: [d, h] for e, d, h in ETAPAS},
        "costo": "promedio de 5 pasadas sobre las posiciones de las partidas con semillas 0..49",
        "terminos": list(TERMINOS),
    }
    return configuracion, filas, resumen


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experimento", choices=["CNT-003"])
    parser.add_argument("--partidas", type=int, default=500)
    parser.add_argument(
        "--id", dest="id_salida",
        help="carpeta de salida dentro de experimentos/counter/ (por defecto, el ID del "
             "experimento); para reproducir una corrida registrada usar un ID nuevo, "
             "p. ej. CNT-003-r1",
    )
    parser.add_argument("--carpeta-base", type=Path, default=CARPETA_EXPERIMENTOS)
    args = parser.parse_args()

    # Se rechaza la colisión antes de calcular para no sobrescribir una corrida registrada.
    id_salida = args.id_salida or args.experimento
    if (args.carpeta_base / id_salida).exists():
        parser.error(f"Ya existe {args.carpeta_base / id_salida}; elegí otro --id.")

    inicio = time.perf_counter()
    configuracion, filas, resumen = cnt_003(args.partidas)
    resumen["duracion_total_s"] = round(time.perf_counter() - inicio, 1)
    carpeta = guardar_corrida(id_salida, configuracion, filas, resumen, carpeta_base=args.carpeta_base)
    print(f"{id_salida}: {len(filas)} posiciones en {resumen['duracion_total_s']} s -> {carpeta}")
    for t, datos in resumen["terminos"].items():
        etapas = {e: d["correlacion"] for e, d in datos["por_etapa"].items()}
        print(f"  {t:16} r={datos['correlacion']}  signo={datos['acierto_de_signo']}  "
              f"etapas={etapas}  costo={datos['costo_us_por_evaluacion']} µs")


if __name__ == "__main__":
    main()
