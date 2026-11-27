import unittest

import gymnasium as gym
import numpy as np

from discretizacion import DiscretizadorAcrobot
from validar_entorno import ejecutar_episodio


class TestDiscretizadorAcrobot(unittest.TestCase):
    def setUp(self):
        entorno = gym.make("Acrobot-v1", render_mode=None)
        self.addCleanup(entorno.close)
        self.espacio = entorno.observation_space
        self.acciones = entorno.action_space.n

    def test_extremos_y_saturacion_directa(self):
        grilla = DiscretizadorAcrobot.directa(self.espacio)
        for obs in (self.espacio.low, self.espacio.low - 1):
            self.assertEqual(grilla.transformar(obs), (0,) * 6)
        for obs in (self.espacio.high, self.espacio.high + 1):
            self.assertEqual(grilla.transformar(obs), (3, 3, 3, 3, 5, 5))

    def test_directa_no_uniforme_conserva_forma_y_bordes_trigonometricos(self):
        original = DiscretizadorAcrobot.directa(self.espacio)
        variante = DiscretizadorAcrobot.directa_no_uniforme(self.espacio)
        self.assertEqual(variante.forma, original.forma)
        self.assertEqual(np.prod(variante.forma), 9_216)
        observaciones, _ = ejecutar_episodio()
        for obs in observaciones:
            clave = variante.transformar(obs)
            self.assertEqual(clave[:4], original.transformar(obs)[:4])
            self.assertEqual(clave, variante.transformar(obs.copy()))
            self.assertTrue(all(0 <= i < 6 for i in clave[4:]))

    def test_directa_no_uniforme_respeta_bordes_y_saturacion_en_ambas_velocidades(self):
        grilla = DiscretizadorAcrobot.directa_no_uniforme(self.espacio)
        obs = np.array([1, 0, 1, 0, 0, 0], dtype=np.float64)
        maximos = self.espacio.high[4:].astype(np.float64)
        for indice, fraccion in enumerate((-0.5, -0.125, 0, 0.125, 0.5), start=1):
            with self.subTest(fraccion=fraccion):
                obs[4:] = maximos * fraccion
                self.assertEqual(grilla.transformar(obs)[4:], (indice, indice))
                obs[4:] = np.nextafter(obs[4:], -np.inf)
                self.assertEqual(grilla.transformar(obs)[4:], (indice - 1, indice - 1))
        obs[4:] = -2 * maximos
        self.assertEqual(grilla.transformar(obs)[4:], (0, 0))
        obs[4:] = 2 * maximos
        self.assertEqual(grilla.transformar(obs)[4:], (5, 5))

    def test_borde_interno_y_bordes_configurables(self):
        grilla = DiscretizadorAcrobot([[-1, -0.25, 0.5, 1]] * 6)
        self.assertEqual(grilla.transformar([-0.25] * 6), (1,) * 6)
        self.assertEqual(grilla.transformar([0.5] * 6), (2,) * 6)
        self.assertEqual(grilla.transformar([np.nextafter(0.5, 0)] * 6), (1,) * 6)

    def test_costura_angular_y_saturacion_de_velocidad(self):
        grilla = DiscretizadorAcrobot.angular(self.espacio)
        for signo in (0.0, -0.0):
            obs = (-1, signo, -1, signo, -100, 100)
            self.assertEqual(grilla.transformar(obs), (0, 0, 0, 7))
        self.assertEqual(grilla.transformar((-1, 0.001, -1, -0.001, 0, 0)), (11, 0, 4, 4))

    def test_rechaza_bordes_y_observaciones_invalidos(self):
        for bordes in ([[0, 1]] * 5, [[0, 0]] * 6, [[0, np.inf]] * 6):
            with self.subTest(bordes=bordes), self.assertRaises(ValueError):
                DiscretizadorAcrobot(bordes)
        grilla = DiscretizadorAcrobot.directa(self.espacio)
        for obs in ([0] * 5, [np.nan] * 6, [np.inf] * 6):
            with self.subTest(obs=obs), self.assertRaises(ValueError):
                grilla.transformar(obs)

    def test_estados_reales_son_indices_validos_y_repetibles(self):
        episodios = [ejecutar_episodio(impulso)[0] for impulso in (False, True)]
        for crear_grilla in (DiscretizadorAcrobot.directa, DiscretizadorAcrobot.angular):
            grilla = crear_grilla(self.espacio)
            tabla_q = np.zeros(grilla.forma + (self.acciones,))
            for observaciones in episodios:
                for obs in observaciones:
                    clave = grilla.transformar(obs)
                    self.assertEqual(clave, grilla.transformar(obs.copy()))
                    self.assertEqual(len(clave), len(grilla.forma))
                    for indice, cantidad in zip(clave, grilla.forma):
                        self.assertIn(indice, range(cantidad))
                    self.assertEqual(tabla_q[clave].shape, (self.acciones,))


if __name__ == "__main__":
    unittest.main()
