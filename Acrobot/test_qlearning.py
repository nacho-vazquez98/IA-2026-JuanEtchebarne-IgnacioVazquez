import unittest
from unittest.mock import Mock

import gymnasium as gym
import numpy as np

from discretizacion import DiscretizadorAcrobot
from qlearning import AgenteQLearning


class TestQLearning(unittest.TestCase):
    def setUp(self):
        self.entorno = gym.make("Acrobot-v1", render_mode=None, max_episode_steps=700)
        self.addCleanup(self.entorno.close)
        self.numero_acciones = self.entorno.action_space.n
        self.discretizador = DiscretizadorAcrobot.directa(self.entorno.observation_space)
        self.agente = AgenteQLearning(
            self.discretizador, self.numero_acciones, alpha=0.5, gamma=0.9, semilla=42
        )
        self.observacion = [1, 0, 1, 0, 0, 0]
        self.siguiente_observacion = [0, 1, 1, 0, 1, 0]
        self.estado = self.discretizador.transformar(self.observacion)
        self.siguiente_estado = self.discretizador.transformar(self.siguiente_observacion)

    def test_greedy_elige_solo_acciones_maximas(self):
        self.agente.q[self.estado] = [-2, 3, 3]
        acciones = {
            self.agente.seleccionar_accion(self.estado, epsilon=0) for _ in range(30)
        }
        self.assertEqual(acciones, {1, 2})
        self.agente.q[self.estado] = [-2, 3, 0]
        self.assertEqual(self.agente.seleccionar_accion(self.estado, epsilon=0), 1)

    def test_exploracion_accede_a_todas_las_acciones(self):
        self.agente.q[self.estado] = [0, 1, 0]
        acciones = {
            self.agente.seleccionar_accion(self.estado, epsilon=1) for _ in range(30)
        }
        self.assertEqual(acciones, {0, 1, 2})
        self.assertTrue(all(map(self.entorno.action_space.contains, acciones)))

    def test_actualizacion_usa_el_maximo_siguiente(self):
        self.agente.q[self.estado] = [0, 2, 5]
        self.agente.q[self.siguiente_estado] = [3, 4, 1]
        self.agente.actualizar(self.estado, 1, -1, self.siguiente_estado, terminado=False)
        np.testing.assert_allclose(self.agente.q[self.estado], [0, 2.3, 5])
        np.testing.assert_array_equal(self.agente.q[self.siguiente_estado], [3, 4, 1])

    def test_final_de_episodio_distingue_terminacion_y_truncamiento(self):
        for terminado, truncado, recompensa, esperado in [
            (False, True, -1, 2.3),
            (True, False, 0, 1.0),
            (True, True, 0, 1.0),
        ]:
            with self.subTest(terminado=terminado, truncado=truncado):
                entorno = Mock(spec=gym.Env)
                entorno.reset.return_value = (self.observacion, {})
                entorno.step.side_effect = [
                    (self.siguiente_observacion, recompensa, terminado, truncado, {})
                ]
                self.agente.q[self.estado] = [0, 2, 1]
                self.agente.q[self.siguiente_estado] = [3, 4, 1]
                resultado = self.agente.aprender_episodio(entorno, epsilon=0, semilla=42)
                self.assertEqual(resultado, (recompensa, 1, terminado, truncado))
                self.assertAlmostEqual(self.agente.q[self.estado + (1,)], esperado)
                entorno.reset.assert_called_once_with(seed=42)
                entorno.step.assert_called_once_with(1)

    def test_rechaza_parametros_y_acciones_invalidos(self):
        for alpha, gamma in [(0, 0.9), (1.1, 0.9), (0.5, -0.1), (0.5, np.nan)]:
            with self.subTest(alpha=alpha, gamma=gamma), self.assertRaises(ValueError):
                AgenteQLearning(self.discretizador, self.numero_acciones, alpha=alpha, gamma=gamma)
        with self.assertRaises(ValueError):
            AgenteQLearning(self.discretizador, 0, alpha=0.5, gamma=0.9)
        with self.assertRaises(ValueError):
            self.agente.seleccionar_accion(self.estado, epsilon=1.1)
        with self.assertRaises(ValueError):
            self.agente.actualizar(self.estado, -1, -1, self.siguiente_estado, terminado=False)

    def test_acrobot_aprende_y_repite_con_ambas_grillas(self):
        for crear in (DiscretizadorAcrobot.directa, DiscretizadorAcrobot.angular):
            with self.subTest(grilla=crear.__name__):
                grilla = crear(self.entorno.observation_space)
                agentes = [
                    AgenteQLearning(grilla, self.numero_acciones, alpha=0.5, gamma=0.9, semilla=42)
                    for _ in range(2)
                ]
                resultados = [
                    agente.aprender_episodio(self.entorno, epsilon=0.2, semilla=42)
                    for agente in agentes
                ]
                self.assertEqual(resultados[0], resultados[1])
                retorno, pasos, terminado, truncado = resultados[0]
                self.assertTrue(terminado or truncado)
                self.assertIn(pasos, range(1, 701))
                self.assertEqual(retorno, -pasos + int(terminado))
                self.assertTrue(np.any(agentes[0].q != 0))
                np.testing.assert_array_equal(agentes[0].q, agentes[1].q)
