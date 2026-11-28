"""Ejecuta la primera ronda exploratoria de Dyna-Q en Acrobot."""

import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean, stdev
from time import perf_counter
from types import SimpleNamespace

import gymnasium as gym

from comparar_grillas import leer_episodios, leer_json
from experimentos_qlearning import (
    ENTORNO,
    GRILLAS,
    MAX_PASOS,
    SEMILLAS_EVALUACION,
    VERSION_MODELO,
    ejecutar_evaluacion,
    entrenar,
    guardar_resultados,
)


NIVELES = (0, 5, 15)
PARES_SEMILLAS = ((10_000, 310_001), (20_000, 310_002), (30_000, 310_003))
EPISODIOS = 500
VALIDACIONES = 100


def ejecutar_corrida(carpeta, clase_agente, n, semilla_entorno, semilla_agente):
    configuracion = {
        "version": VERSION_MODELO, "entorno": ENTORNO, "max_pasos": MAX_PASOS,
        "algoritmo": "dyna-q", "grilla": "angular", "alpha": 0.5, "gamma": 0.99,
        "episodios": EPISODIOS, "semilla_entorno_inicial": semilla_entorno,
        "semilla_agente": semilla_agente, "pasos_planificacion": n,
        "decaimiento": "lineal_por_episodio", "epsilon_inicial": 1.0, "epsilon_final": 0.05,
    }
    with gym.make(ENTORNO, render_mode=None, max_episode_steps=MAX_PASOS) as entorno:
        grilla = GRILLAS[configuracion["grilla"]](entorno.observation_space)
        agente = clase_agente(
            grilla, entorno.action_space.n, alpha=configuracion["alpha"],
            gamma=configuracion["gamma"], pasos_planificacion=n, semilla=semilla_agente,
        )
        inicio = perf_counter()
        filas = entrenar(
            entorno, agente, episodios=EPISODIOS, semilla=semilla_entorno,
            epsilon_inicial=configuracion["epsilon_inicial"],
            epsilon_final=configuracion["epsilon_final"],
        )
        segundos = perf_counter() - inicio

    pasos = sum(fila["pasos"] for fila in filas)
    if (agente.actualizaciones_reales, agente.actualizaciones_simuladas) != (pasos, n * pasos):
        raise ValueError(f"Conteos de actualización inconsistentes en {carpeta}.")
    resumen = {
        "episodios": len(filas), "segundos": segundos,
        "retorno_promedio": mean(fila["retorno"] for fila in filas),
        "tasa_exito": mean(fila["terminado"] for fila in filas),
        "actualizaciones_reales": agente.actualizaciones_reales,
        "actualizaciones_simuladas": agente.actualizaciones_simuladas,
        "bytes_tabla_q": agente.q.nbytes,
    }
    entrenamiento, validacion = carpeta / "entrenamiento", carpeta / "validacion"
    guardar_resultados(entrenamiento, configuracion, filas, resumen, modelo=agente)
    leer_episodios(entrenamiento, semilla_entorno, EPISODIOS)
    modelo = entrenamiento / "modelo.npz"
    huella = hashlib.sha256(modelo.read_bytes()).hexdigest()

    with gym.make(ENTORNO, render_mode=None, max_episode_steps=MAX_PASOS) as entorno:
        medidas = ejecutar_evaluacion(SimpleNamespace(
            modelo=modelo, conjunto="validacion", episodios=VALIDACIONES, salida=validacion,
        ), entorno)
    episodios_validacion = leer_episodios(validacion, SEMILLAS_EVALUACION["validacion"], VALIDACIONES)
    if (leer_json(validacion, "config.json")["sha256_modelo"] != huella
            or hashlib.sha256(modelo.read_bytes()).hexdigest() != huella):
        raise ValueError(f"La huella del modelo no coincide en {carpeta}.")
    return {
        "n": n, "semilla_entorno": semilla_entorno, "semilla_agente": semilla_agente,
        "episodios_entrenamiento": len(filas), "episodios_validacion": VALIDACIONES,
        "pasos_entrenamiento": pasos, "pasos_validacion": sum(int(f["pasos"]) for f in episodios_validacion),
        "actualizaciones_simuladas": agente.actualizaciones_simuladas,
        "segundos_entrenamiento": segundos, "segundos_validacion": medidas["segundos"],
        "retorno_greedy": medidas["retorno_promedio"], "exito_greedy": medidas["tasa_exito"],
    }


def resumir_replicas(filas):
    controles = {fila["semilla_entorno"]: fila["retorno_greedy"] for fila in filas if fila["n"] == 0}
    agregados = []
    for n in NIVELES:
        grupo = [fila for fila in filas if fila["n"] == n]
        retornos = [fila["retorno_greedy"] for fila in grupo]
        diferencias = {
            fila["semilla_entorno"]: fila["retorno_greedy"] - controles[fila["semilla_entorno"]]
            for fila in grupo
        }
        agregados.append({
            "n": n, "retorno_greedy": mean(retornos), "desviacion_muestral_retorno": stdev(retornos),
            "diferencias_por_semilla": diferencias,
            "diferencia_media_frente_a_n0": mean(diferencias.values()),
            "desviacion_muestral_diferencia": stdev(diferencias.values()),
            "exito_greedy": mean(fila["exito_greedy"] for fila in grupo),
            "segundos_por_millon_de_pasos_reales": (
                1_000_000 * sum(fila["segundos_entrenamiento"] for fila in grupo)
                / sum(fila["pasos_entrenamiento"] for fila in grupo)
            ),
        })
    return {"replicas": filas, "agregados": agregados}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    accion = parser.add_mutually_exclusive_group(required=True)
    accion.add_argument("--plan", action="store_true", help="Imprime la matriz sin entrenar.")
    accion.add_argument("--salida", type=Path, help="Carpeta nueva para guardar la ronda.")
    args = parser.parse_args()
    matriz = [(n, entorno, agente) for entorno, agente in PARES_SEMILLAS for n in NIVELES]
    plan = {
        "corridas": [{"n": n, "semilla_entorno": e, "semilla_agente": a} for n, e, a in matriz],
        "grilla": "angular",
        "episodios_entrenamiento_por_corrida": EPISODIOS,
        "episodios_validacion_por_corrida": VALIDACIONES,
        "max_pasos_entrenamiento": len(matriz) * EPISODIOS * MAX_PASOS,
        "max_actualizaciones_simuladas": sum(n for n, _, _ in matriz) * EPISODIOS * MAX_PASOS,
        "max_pasos_validacion": len(matriz) * VALIDACIONES * MAX_PASOS,
    }
    if args.plan:
        print(json.dumps(plan, indent=2))
        return

    try:
        from dyna_q import AgenteDynaQ
    except ModuleNotFoundError as error:
        if error.name != "dyna_q":
            raise
        parser.error("Se requiere dyna_q.py. Actualizá la rama después de que se integre el PR #13 (A10).")

    try:
        args.salida.mkdir()
    except OSError as error:
        parser.error(str(error))

    (args.salida / "plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    filas = []
    for n, entorno, agente in matriz:
        print(f"Corriendo n={n}, semilla de entorno {entorno}", flush=True)
        carpeta = args.salida / f"semilla-{entorno}" / f"n-{n}"
        fila = ejecutar_corrida(carpeta, AgenteDynaQ, n, entorno, agente)
        filas.append(fila)
        print(json.dumps(fila), flush=True)

    resumen = resumir_replicas(filas)
    (args.salida / "resumen.json").write_text(json.dumps(resumen, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
