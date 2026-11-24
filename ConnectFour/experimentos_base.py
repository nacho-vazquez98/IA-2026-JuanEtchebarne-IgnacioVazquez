"""Experimentos de referencia de COUNTER (P06 y C01).

Uso, desde ``ConnectFour/``:
    poetry run python experimentos_base.py CNT-001 [--partidas 100]
    poetry run python experimentos_base.py CNT-002 [--partidas 100]
"""
import argparse
import math
import statistics
import time

from agentes_base import AgenteAleatorio
from arena import jugar_contra_stratego, jugar_partida
from registro import guardar_corrida
from stratego_agent import Stratego


def intervalo_wilson(exitos, n, z=1.96):
    """Intervalo de confianza del 95 % para una proporción."""
    if n == 0:
        return (0.0, 0.0)
    p = exitos / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    margen = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (round(centro - margen, 4), round(centro + margen, 4))


def fila_partida(experimento, variante, indice, semilla, jugador_evaluado, resultado):
    ganador = resultado.ganador
    if ganador == 0:
        desenlace = "empate"
    elif ganador == jugador_evaluado:
        desenlace = "victoria"
    else:
        desenlace = "derrota"
    tiempos = resultado.tiempos[jugador_evaluado]
    return {
        "experimento": experimento,
        "variante": variante,
        "partida": indice,
        "semilla": semilla,
        "jugador_evaluado": jugador_evaluado,
        "ganador": ganador,
        "desenlace": desenlace,
        "jugadas": resultado.cantidad_jugadas,
        "tiempo_medio_s": round(statistics.fmean(tiempos), 6) if tiempos else 0.0,
        "tiempo_max_s": round(max(tiempos), 6) if tiempos else 0.0,
        "secuencia": " ".join(map(str, resultado.jugadas)),
    }


def resumir(filas):
    resumen = {}
    for variante in dict.fromkeys(f["variante"] for f in filas):
        grupo = [f for f in filas if f["variante"] == variante]
        n = len(grupo)
        victorias = sum(f["desenlace"] == "victoria" for f in grupo)
        resumen[variante] = {
            "partidas": n,
            "victorias": victorias,
            "derrotas": sum(f["desenlace"] == "derrota" for f in grupo),
            "empates": sum(f["desenlace"] == "empate" for f in grupo),
            "tasa_victoria": round(victorias / n, 4),
            "ic95_tasa_victoria": intervalo_wilson(victorias, n),
            "jugadas_promedio": round(statistics.fmean(f["jugadas"] for f in grupo), 2),
            "tiempo_medio_por_jugada_s": round(statistics.fmean(f["tiempo_medio_s"] for f in grupo), 6),
        }
    return resumen


def cnt_001(partidas):
    """Agente aleatorio (jugador 1) contra Stratego oficial (jugador 2)."""
    filas = []
    for semilla in range(partidas):
        resultado = jugar_contra_stratego(AgenteAleatorio(semilla))
        filas.append(fila_partida("CNT-001", "aleatorio_vs_stratego_oficial", semilla, semilla, 1, resultado))
    configuracion = {
        "pregunta": "¿Qué resultado obtiene un agente sin estrategia contra Stratego oficial?",
        "agente": "AgenteAleatorio(semilla) como jugador 1",
        "rival": "load_enemy_agent() = Stratego(2, 4) como jugador 2",
        "semillas": f"0..{partidas - 1}",
        "apertura": "ninguna",
    }
    return configuracion, filas


def cnt_002(partidas):
    """Stratego contra el agente aleatorio, según el argumento del constructor y el turno."""
    filas = []
    for turno in (1, 2):
        for argumento in (1, 2):
            variante = f"Stratego({argumento},4)_como_jugador_{turno}"
            for semilla in range(partidas):
                stratego = Stratego(argumento, 4)
                aleatorio = AgenteAleatorio(semilla)
                if turno == 1:
                    resultado = jugar_partida(stratego, aleatorio)
                else:
                    resultado = jugar_partida(aleatorio, stratego)
                filas.append(fila_partida("CNT-002", variante, semilla, semilla, turno, resultado))
    configuracion = {
        "pregunta": (
            "¿Stratego juega mejor cuando el número de jugador que deriva de su "
            "constructor ((argumento % 2) + 1) coincide con su turno real?"
        ),
        "agente_evaluado": "Stratego(argumento, 4), argumento en {1, 2}, como jugador 1 o 2",
        "rival": "AgenteAleatorio(semilla)",
        "semillas": f"0..{partidas - 1} por variante",
        "apertura": "ninguna",
    }
    return configuracion, filas


EXPERIMENTOS = {"CNT-001": cnt_001, "CNT-002": cnt_002}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experimento", choices=sorted(EXPERIMENTOS))
    parser.add_argument("--partidas", type=int, default=100)
    args = parser.parse_args()

    inicio = time.perf_counter()
    configuracion, filas = EXPERIMENTOS[args.experimento](args.partidas)
    duracion = time.perf_counter() - inicio
    resumen = {"duracion_total_s": round(duracion, 1), "variantes": resumir(filas)}
    carpeta = guardar_corrida(args.experimento, configuracion, filas, resumen)
    print(f"{args.experimento}: {len(filas)} partidas en {duracion:.1f} s -> {carpeta}")
    for variante, datos in resumen["variantes"].items():
        print(f"  {variante}: {datos}")


if __name__ == "__main__":
    main()
