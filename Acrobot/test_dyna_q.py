import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

import gymnasium as gym
import numpy as np

from discretizacion import DiscretizadorAcrobot
from dyna_q import AgenteDynaQ
from experimentos_qlearning import ENTORNO, MAX_PASOS, VERSION_MODELO, entrenar, guardar_resultados
from qlearning import AgenteQLearning


class TestDynaQ(unittest.TestCase):
    def crear_agente(self, n, semilla=42):
        discretizador = SimpleNamespace(forma=(3,), transformar=lambda observacion: observacion)
        return AgenteDynaQ(
            discretizador, 3, alpha=0.5, gamma=0.9, pasos_planificacion=n, semilla=semilla,
        )

    def test_planificacion_reutiliza_el_objetivo_real(self):
        agente = self.crear_agente(2)
        agente.q[1, 0] = 2
        agente.actualizar((0,), 0, -1, (1,), terminado=False)
        self.assertAlmostEqual(agente.q[0, 0], 0.7)
        self.assertEqual((agente.actualizaciones_reales, agente.actualizaciones_simuladas), (1, 2))

    def test_planificacion_usa_el_q_actual_si_el_sucesor_es_el_mismo(self):
        agente = self.crear_agente(2)
        agente.q[0, 0] = 2
        agente.actualizar((0,), 0, -1, (0,), terminado=False)
        self.assertAlmostEqual(agente.q[0, 0], 0.2885)

    def test_reutiliza_el_par_observado_sorteado_y_reemplaza_su_transicion(self):
        agente = self.crear_agente(1)
        agente.q[1, 0] = 2
        agente.actualizar((0,), 1, -1, (1,), terminado=False)
        self.assertAlmostEqual(agente.q[0, 1], 0.6)

        # Se observa otro estado y se planifica sobre el primero.
        with patch.object(agente, "_rng_modelo", Mock()) as rng:
            rng.integers.side_effect = [0, 0]
            agente.actualizar((2,), 2, -1, (1,), terminado=False)
        self.assertAlmostEqual(agente.q[2, 2], 0.4)
        self.assertAlmostEqual(agente.q[0, 1], 0.7)
        self.assertEqual(agente._modelo[(0,)][1], (-1, (1,), False))

        # Una nueva transición del mismo par sustituye el contenido previo.
        with patch.object(agente, "_rng_modelo", Mock()) as rng:
            rng.integers.side_effect = [0, 0]
            agente.actualizar((0,), 1, 0, (2,), terminado=True)
        self.assertEqual(agente._modelo[(0,)][1], (0, (2,), True))
        self.assertEqual(agente._estados_observados, [(0,), (2,)])
        self.assertAlmostEqual(agente.q[0, 1], 0.175)

        # Se puede elegir otra acción registrada en el mismo estado.
        with patch.object(agente, "_rng_modelo", Mock()) as rng:
            rng.integers.side_effect = [0, 1]
            agente.actualizar((0,), 0, -1, (1,), terminado=False)
        self.assertEqual(rng.integers.call_args_list, [call(2), call(2)])
        self.assertAlmostEqual(agente.q[0, 0], 0.6)
        self.assertAlmostEqual(agente.q[0, 1], 0.175)

    def test_ultimo_paso_distingue_truncamiento_y_terminacion_en_ambas_actualizaciones(self):
        for terminado, truncado, recompensa, esperado in (
            (False, True, -1, 1.1),
            (True, False, 0, 0.5),
            (True, True, 0, 0.5),
        ):
            with self.subTest(terminado=terminado, truncado=truncado):
                agente = self.crear_agente(1)
                agente.q[0, 0] = agente.q[1, 0] = 2
                entorno = Mock(spec=gym.Env)
                entorno.reset.return_value = ((0,), {})
                entorno.step.side_effect = [((1,), recompensa, terminado, truncado, {})]
                resultado = agente.aprender_episodio(entorno, epsilon=0, semilla=42)
                self.assertEqual(resultado, (recompensa, 1, terminado, truncado))
                entorno.step.assert_called_once_with(0)
                self.assertEqual(agente._modelo[(0,)][0], (recompensa, (1,), terminado))
                self.assertAlmostEqual(agente.q[0, 0], esperado)

    def test_n_cero_reproduce_qlearning_con_las_mismas_semillas(self):
        with gym.make(ENTORNO, render_mode=None, max_episode_steps=35) as entorno:
            grilla = DiscretizadorAcrobot.angular(entorno.observation_space)
            base = AgenteQLearning(grilla, 3, alpha=0.5, gamma=0.9, semilla=42)
            dyna = AgenteDynaQ(grilla, 3, alpha=0.5, gamma=0.9, pasos_planificacion=0, semilla=42)
            pasos_totales = 0
            for semilla in (10_000, 10_001):
                acciones = []
                paso_real = entorno.step

                def registrar(accion):
                    acciones.append(accion)
                    return paso_real(accion)

                with patch.object(entorno, "step", side_effect=registrar):
                    esperado = base.aprender_episodio(entorno, epsilon=0.3, semilla=semilla)
                    acciones_esperadas = acciones.copy()
                    acciones.clear()
                    observado = dyna.aprender_episodio(entorno, epsilon=0.3, semilla=semilla)
                self.assertEqual(esperado, observado)
                self.assertEqual(acciones, acciones_esperadas)
                pasos_totales += esperado[1]
        np.testing.assert_array_equal(base.q, dyna.q)
        self.assertEqual(dyna._modelo, {})
        self.assertEqual(dyna.actualizaciones_reales, pasos_totales)
        self.assertEqual(dyna.actualizaciones_simuladas, 0)

    def test_los_sorteos_de_planificacion_no_consumen_el_flujo_de_la_politica(self):
        breve = self.crear_agente(1)
        extenso = self.crear_agente(5)
        for agente in (breve, extenso):
            agente.actualizar((0,), 0, -1, (1,), terminado=False)
            agente.q[0] = [0.5, 0.5, 0]
        self.assertNotEqual(breve.actualizaciones_simuladas, extenso.actualizaciones_simuladas)
        self.assertEqual(
            [breve.seleccionar_accion((0,), epsilon=0.3) for _ in range(30)],
            [extenso.seleccionar_accion((0,), epsilon=0.3) for _ in range(30)],
        )

    def test_planificacion_y_tabla_son_reproducibles(self):
        agentes = [self.crear_agente(3) for _ in range(2)]
        for agente in agentes:
            for accion in (1, 0, 2, 2, 1):
                agente.actualizar((accion,), accion, -1, ((accion + 1) % 3,), terminado=False)
        np.testing.assert_array_equal(agentes[0].q, agentes[1].q)
        self.assertEqual(agentes[0]._modelo, agentes[1]._modelo)

    def test_rechaza_pasos_invalidos_y_admite_semilla_opcional(self):
        for pasos in (-1, 1.5, True, None):
            with self.subTest(pasos=pasos), self.assertRaises(ValueError):
                self.crear_agente(pasos)
        agente = self.crear_agente(1, semilla=None)
        agente.actualizar((0,), 0, -1, (1,), terminado=False)
        self.assertEqual(agente.actualizaciones_simuladas, 1)

    def test_guarda_un_modelo_evaluable_en_otro_proceso(self):
        configuracion = {
            "version": VERSION_MODELO, "entorno": ENTORNO, "max_pasos": MAX_PASOS,
            "algoritmo": "dyna-q", "pasos_planificacion": 2, "grilla": "angular",
            "alpha": 0.5, "gamma": 0.9, "semilla_agente": 42,
        }
        script = Path(__file__).with_name("experimentos_qlearning.py").resolve()
        with TemporaryDirectory() as raiz:
            salida = Path(raiz) / "entrenamiento"
            evaluacion = Path(raiz) / "validacion"
            with gym.make(ENTORNO, render_mode=None, max_episode_steps=MAX_PASOS) as entorno:
                grilla = DiscretizadorAcrobot.angular(entorno.observation_space)
                agente = AgenteDynaQ(grilla, 3, alpha=0.5, gamma=0.9, pasos_planificacion=2, semilla=42)
                filas = entrenar(
                    entorno, agente, episodios=2, semilla=10_000, epsilon_inicial=0.5, epsilon_final=0.05,
                )
            pasos = sum(fila["pasos"] for fila in filas)
            self.assertEqual(agente.actualizaciones_reales, pasos)
            self.assertEqual(agente.actualizaciones_simuladas, pasos * 2)
            guardar_resultados(salida, configuracion, filas, {}, modelo=agente)
            modelo = salida / "modelo.npz"
            contenido = modelo.read_bytes()
            subprocess.run(
                [sys.executable, "-B", str(script), "evaluar", "--modelo", str(modelo),
                 "--episodios", "2", "--salida", str(evaluacion)],
                capture_output=True, check=True, timeout=30,
            )
            config = json.loads((evaluacion / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["modelo"]["algoritmo"], "dyna-q")
            self.assertEqual(config["modelo"]["pasos_planificacion"], 2)
            self.assertEqual(config["epsilon"], 0)
            self.assertEqual(config["sha256_modelo"], hashlib.sha256(contenido).hexdigest())
            self.assertEqual(modelo.read_bytes(), contenido)
