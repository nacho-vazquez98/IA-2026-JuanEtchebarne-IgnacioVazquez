"""Agentes de referencia (baseline) para COUNTER."""
import random

from agent import Agent
from board import Board


class AgenteAleatorio(Agent):
    """Elige una columna legal al azar con una semilla reproducible."""

    def __init__(self, semilla=None):
        self.semilla = semilla
        self._rng = random.Random(semilla)

    def next_action(self, obs: Board):
        return self._rng.choice(obs.get_posible_actions())

    def heuristic_utility(self, board: Board):
        return 0
