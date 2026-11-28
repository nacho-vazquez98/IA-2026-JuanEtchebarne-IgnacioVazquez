"""Prueba de desarrollo de A11. Usa el commit bbdb86e del PR 13."""

import json
import sys
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace

raiz = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(raiz / "Acrobot"))

import gymnasium as gym
import numpy as np

from dyna_q import AgenteDynaQ
from experimentos_qlearning import (
    ENTORNO, GRILLAS, MAX_PASOS, SEMILLAS_EVALUACION, VERSION_MODELO,
    ejecutar_evaluacion, entrenar, guardar_resultados,
)

salida = Path(sys.argv[1])
salida.mkdir()
resultados = []
semilla, semilla_agente = 10_000, 310_001
episodios, cortes, validaciones = 12, (6, 12), 4
epsilons = np.linspace(1.0, 0.05, episodios)

for nombre in ("angular", "directa"):
    for n in (0, 5, 15):
        config = {
            "version": VERSION_MODELO, "entorno": ENTORNO, "max_pasos": MAX_PASOS,
            "grilla": nombre, "alpha": 0.5, "gamma": 0.99,
            "algoritmo": "dyna-q", "pasos_planificacion": n,
            "semilla_agente": semilla_agente, "semilla_entorno_inicial": semilla,
            "episodios": episodios, "epsilon_inicial": 1.0, "epsilon_final": 0.05,
        }
        filas, desde, segundos = [], 0, 0.0
        with gym.make(ENTORNO, render_mode=None, max_episode_steps=MAX_PASOS) as entorno:
            grilla = GRILLAS[nombre](entorno.observation_space)
            agente = AgenteDynaQ(
                grilla, entorno.action_space.n, alpha=0.5, gamma=0.99,
                pasos_planificacion=n, semilla=semilla_agente,
            )
            for corte in cortes:
                inicio = perf_counter()
                tramo = entrenar(
                    entorno, agente, episodios=corte - desde, semilla=semilla + desde,
                    epsilon_inicial=float(epsilons[desde]), epsilon_final=float(epsilons[corte - 1]),
                )
                segundos += perf_counter() - inicio
                filas.extend({**fila, "episodio": fila["episodio"] + desde} for fila in tramo)
                desde = corte
                reales = sum(fila["pasos"] for fila in filas)
                simuladas = reales * n
                assert agente.actualizaciones_reales == reales
                assert agente.actualizaciones_simuladas == simuladas
                np.testing.assert_allclose([fila["epsilon"] for fila in filas], epsilons[:corte], rtol=0, atol=1e-15)

                carpeta = salida / nombre / f"n{n}" / f"ep{corte}"
                resumen = {
                    "grilla": nombre, "n": n, "episodios": corte, "reales": reales,
                    "simuladas": simuladas, "segundos_entrenamiento": segundos,
                    "segundos_por_millon_de_pasos_reales": segundos / reales * 1_000_000,
                }
                guardar_resultados(
                    carpeta / "entrenamiento", {**config, "episodios_guardados": corte},
                    filas, resumen, modelo=agente,
                )
                modelo = carpeta / "entrenamiento" / "modelo.npz"
                contenido = modelo.read_bytes()
                with gym.make(ENTORNO, render_mode=None, max_episode_steps=MAX_PASOS) as entorno_validacion:
                    validacion = ejecutar_evaluacion(SimpleNamespace(
                        episodios=validaciones, conjunto="validacion", modelo=modelo,
                        salida=carpeta / "validacion",
                    ), entorno_validacion)
                assert modelo.read_bytes() == contenido
                resultados.append({
                    **resumen, "retorno_greedy": validacion["retorno_promedio"],
                    "exito_greedy": validacion["tasa_exito"], "segundos_validacion": validacion["segundos"],
                })

            if nombre == "angular" and n == 5:
                referencia = AgenteDynaQ(
                    grilla, entorno.action_space.n, alpha=0.5, gamma=0.99,
                    pasos_planificacion=n, semilla=semilla_agente,
                )
                corrida = entrenar(
                    entorno, referencia, episodios=episodios, semilla=semilla,
                    epsilon_inicial=1.0, epsilon_final=0.05,
                )
                np.testing.assert_array_equal(agente.q, referencia.q)
                for con_pausas, sin_pausas in zip(filas, corrida):
                    assert all(con_pausas[k] == sin_pausas[k] for k in sin_pausas if k != "epsilon")

(salida / "resumen.json").write_text(json.dumps({
    "semillas_validacion": list(range(SEMILLAS_EVALUACION["validacion"], SEMILLAS_EVALUACION["validacion"] + validaciones)),
    "grilla_angular_n5_igual_sin_pausas": True,
    "resultados": resultados,
}, indent=2) + "\n")
for fila in resultados:
    if fila["episodios"] == episodios:
        print(
            f"{fila['grilla']:7s} n={fila['n']:2d} reales={fila['reales']:5d} "
            f"simuladas={fila['simuladas']:6d} entrenamiento={fila['segundos_entrenamiento']:.3f}s "
            f"retorno={fila['retorno_greedy']:.1f}"
        )
print("Tabla y episodios iguales en angular n=5 con y sin evaluaciones intermedias.")
