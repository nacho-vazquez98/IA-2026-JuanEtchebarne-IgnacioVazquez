"""Pruebas del simulador (C01) y del arena de partidas (C08/P06).

Ejecutar desde ``ConnectFour/``: ``poetry run python -m unittest -v``
"""
import contextlib
import io
import unittest

from agentes_base import AgenteAleatorio
from arena import JugadaIlegal, aperturas, jugar_contra_stratego, jugar_partida
from board import Board
from connect_four_env import ConnectFourBaseEnv
from play import load_enemy_agent, play_vs_other_agent


class SecuenciaFija:
    """Agente que repite una lista de columnas; sirve para armar partidas exactas."""

    def __init__(self, columnas):
        self.columnas = list(columnas)

    def next_action(self, obs):
        return self.columnas.pop(0)


class ReglasDelSimulador(unittest.TestCase):
    """Comportamientos del código de la cátedra que condicionan las heurísticas."""

    def test_captura_horizontal_convierte_ficha_encerrada(self):
        tablero = Board(6, 7)
        tablero.add_tile(0, 1)
        tablero.add_tile(1, 2)
        tablero.add_tile(2, 1)  # encierra la ficha del jugador 2 en la columna 1
        self.assertEqual(tablero[5][1], 1)

    def test_no_hay_captura_vertical(self):
        tablero = Board(6, 7)
        tablero.add_tile(0, 1)
        tablero.add_tile(0, 2)
        tablero.add_tile(0, 1)
        self.assertEqual(tablero[4][0], 2)

    def test_captura_puede_completar_cuatro_en_linea(self):
        tablero = Board(6, 7)
        for columna, jugador in [(0, 1), (1, 1), (2, 2), (4, 1)]:
            tablero.add_tile(columna, jugador)
        self.assertEqual(tablero.winner, 0)
        tablero.add_tile(3, 1)  # encierra la ficha de la columna 2 y forma 1-1-1-1-1
        self.assertEqual(tablero.winner, 1)

    def test_columna_llena_no_es_accion_posible(self):
        tablero = Board(6, 7)
        for fila in range(6):
            tablero.add_tile(3, 1 + fila % 2)
        self.assertNotIn(3, tablero.get_posible_actions())
        self.assertFalse(tablero.add_tile(3, 1))

    def test_stratego_oficial_se_asigna_internamente_el_jugador_1(self):
        # Stratego(a, d) usa (a % 2) + 1 como su número de jugador.
        self.assertEqual(load_enemy_agent().IlllIIllIII, 1)

    def test_stratego_es_determinista(self):
        a = jugar_contra_stratego(SecuenciaFija([3] * 3 + [2] * 6 + [4] * 6 + [1] * 6 + [5] * 6 + [0] * 6 + [6] * 6))
        b = jugar_contra_stratego(SecuenciaFija([3] * 3 + [2] * 6 + [4] * 6 + [1] * 6 + [5] * 6 + [0] * 6 + [6] * 6))
        self.assertEqual(a.jugadas, b.jugadas)


class Arena(unittest.TestCase):
    def test_coincide_con_play_vs_other_agent(self):
        for semilla in range(5):
            env = ConnectFourBaseEnv(render_mode=None)
            with contextlib.redirect_stdout(io.StringIO()):
                play_vs_other_agent(env, AgenteAleatorio(semilla), AgenteAleatorio(semilla + 100))
            esperado = env._grid.winner
            obtenido = jugar_partida(AgenteAleatorio(semilla), AgenteAleatorio(semilla + 100))
            self.assertEqual(obtenido.ganador, esperado)

    def test_partida_aleatoria_termina_y_es_reproducible(self):
        a = jugar_partida(AgenteAleatorio(7), AgenteAleatorio(8))
        b = jugar_partida(AgenteAleatorio(7), AgenteAleatorio(8))
        self.assertIn(a.ganador, (0, 1, 2))
        self.assertEqual(a.jugadas, b.jugadas)
        self.assertLessEqual(a.cantidad_jugadas, 42)

    def test_apertura_se_aplica_y_no_se_cronometra(self):
        resultado = jugar_partida(AgenteAleatorio(1), AgenteAleatorio(2), apertura=(3, 4))
        self.assertEqual(resultado.jugadas[:2], [3, 4])
        jugadas_de_agentes = len(resultado.tiempos[1]) + len(resultado.tiempos[2])
        self.assertEqual(jugadas_de_agentes, resultado.cantidad_jugadas - 2)

    def test_jugada_ilegal_lanza_excepcion(self):
        with self.assertRaises(JugadaIlegal):
            jugar_partida(SecuenciaFija([0] * 7), SecuenciaFija([1] * 7), apertura=(0, 0, 0, 0, 0, 0))

    def test_aperturas_enumera_todas(self):
        self.assertEqual(len(aperturas(2)), 49)
        self.assertEqual(aperturas(1), [(c,) for c in range(7)])


if __name__ == "__main__":
    unittest.main()
