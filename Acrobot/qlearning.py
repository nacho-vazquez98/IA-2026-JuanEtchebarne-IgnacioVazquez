"""Agente Q-Learning tabular para Acrobot-v1."""

import numpy as np


class AgenteQLearning:
    """Aprende sobre las claves producidas por un DiscretizadorAcrobot."""

    def __init__(self, discretizador, numero_acciones, *, alpha, gamma, semilla=None):
        if not 0 < alpha <= 1:
            raise ValueError("alpha debe estar en (0, 1].")
        if not 0 <= gamma <= 1:
            raise ValueError("gamma debe estar en [0, 1].")
        if numero_acciones < 1:
            raise ValueError("Se requiere al menos una acción.")

        self.discretizador = discretizador
        self.alpha = alpha
        self.gamma = gamma
        self.q = np.zeros(discretizador.forma + (numero_acciones,), dtype=np.float64)
        self._rng = np.random.default_rng(semilla)

    def seleccionar_accion(self, estado, *, epsilon):
        """Selecciona una acción ε-greedy a partir de una clave discreta."""
        if not 0 <= epsilon <= 1:
            raise ValueError("epsilon debe estar en [0, 1].")

        valores = self.q[estado]
        if epsilon > 0 and self._rng.random() < epsilon:
            return int(self._rng.integers(valores.size))
        mejores = np.flatnonzero(valores == valores.max())
        return int(self._rng.choice(mejores))

    def actualizar(self, estado, accion, recompensa, siguiente_estado, *, terminado):
        """Actualiza Q para una transición entre claves discretas."""
        if not 0 <= accion < self.q.shape[-1]:
            raise ValueError("La acción está fuera de la tabla Q.")

        objetivo = recompensa
        if not terminado:
            objetivo += self.gamma * self.q[siguiente_estado].max()
        indice = estado + (accion,)
        self.q[indice] += self.alpha * (objetivo - self.q[indice])

    def aprender_episodio(self, entorno, *, epsilon, semilla=None):
        """Aprende un episodio y devuelve (retorno, pasos, terminado, truncado).

        La semilla del episodio inicializa el entorno. El agente conserva su
        propio generador aleatorio entre episodios.
        """
        observacion, _ = entorno.reset(seed=semilla)
        estado = self.discretizador.transformar(observacion)
        retorno = 0.0
        pasos = 0
        while True:
            accion = self.seleccionar_accion(estado, epsilon=epsilon)
            observacion, recompensa, terminado, truncado, _ = entorno.step(accion)
            siguiente_estado = self.discretizador.transformar(observacion)
            self.actualizar(estado, accion, recompensa, siguiente_estado, terminado=terminado)
            retorno += recompensa
            pasos += 1
            if terminado or truncado:
                return retorno, pasos, terminado, truncado
            estado = siguiente_estado
