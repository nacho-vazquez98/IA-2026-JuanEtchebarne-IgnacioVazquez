"""Partidas sin renderizado para experimentar.

Reproduce la secuencia de turnos de ``play.play_vs_other_agent`` (``agente1``
juega primero como jugador 1 y ``agente2`` como jugador 2), pero no imprime el
tablero, devuelve el resultado y mide el tiempo de cada decisión. Con
``apertura`` se fuerzan las primeras jugadas para obtener partidas distintas
entre agentes deterministas.
"""
import itertools
import time
from dataclasses import dataclass, field

from connect_four_env import ConnectFourBaseEnv
from play import load_enemy_agent


class JugadaIlegal(Exception):
    """Un agente o una apertura eligió una columna llena o inexistente."""


@dataclass
class ResultadoPartida:
    ganador: int  # 0 empate, 1 o 2
    jugadas: list = field(default_factory=list)
    tiempos: dict = field(default_factory=lambda: {1: [], 2: []})

    @property
    def cantidad_jugadas(self):
        return len(self.jugadas)


def jugar_partida(agente1, agente2, apertura=(), env=None):
    """Juega una partida completa y devuelve un ``ResultadoPartida``.

    ``apertura`` es una secuencia de columnas que se juegan en orden,
    alternando jugadores desde el jugador 1, antes de consultar a los agentes.
    Esas jugadas forzadas no se cronometran.
    """
    env = env or ConnectFourBaseEnv(render_mode=None)
    obs, _ = env.reset()
    agentes = {1: agente1, 2: agente2}
    resultado = ResultadoPartida(ganador=0)
    jugador = 1
    terminado = False
    pendientes = list(apertura)

    while not terminado:
        if pendientes:
            accion = pendientes.pop(0)
        else:
            inicio = time.perf_counter()
            accion = agentes[jugador].next_action(obs)
            resultado.tiempos[jugador].append(time.perf_counter() - inicio)
        if accion not in obs.get_posible_actions():
            raise JugadaIlegal(f"Jugador {jugador} eligió la columna {accion!r}")
        obs, _, terminado, truncado, _ = env.step(accion)
        terminado = terminado or truncado
        resultado.jugadas.append(int(accion))
        jugador = 2 if jugador == 1 else 1

    resultado.ganador = int(obs.winner)
    return resultado


def jugar_contra_stratego(agente, apertura=(), env=None):
    """Configuración oficial: ``agente`` empieza y Stratego es ``load_enemy_agent()``."""
    return jugar_partida(agente, load_enemy_agent(), apertura=apertura, env=env)


def aperturas(cantidad_jugadas, columnas=7):
    """Todas las secuencias de ``cantidad_jugadas`` columnas, en orden lexicográfico.

    Con pocas jugadas ninguna columna se llena ni hay ganador, así que todas
    son legales en un tablero de 6 filas.
    """
    return [tuple(a) for a in itertools.product(range(columnas), repeat=cantidad_jugadas)]
