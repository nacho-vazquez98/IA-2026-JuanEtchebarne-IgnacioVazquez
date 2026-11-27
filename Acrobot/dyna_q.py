"""Dyna-Q tabular con planificación a partir de transiciones observadas."""

import numpy as np

from qlearning import AgenteQLearning


class AgenteDynaQ(AgenteQLearning):
    """Reutiliza la actualización de Q-Learning en pasos reales y simulados."""

    def __init__(
        self, discretizador, numero_acciones, *, alpha, gamma, pasos_planificacion, semilla=None
    ):
        if (
            isinstance(pasos_planificacion, bool)
            or not isinstance(pasos_planificacion, (int, np.integer))
            or pasos_planificacion < 0
        ):
            raise ValueError("pasos_planificacion debe ser un entero no negativo.")

        super().__init__(discretizador, numero_acciones, alpha=alpha, gamma=gamma, semilla=semilla)
        self._pasos_planificacion = int(pasos_planificacion)
        self._modelo = {}
        self._estados_observados = []
        self._rng_modelo = None
        if self._pasos_planificacion:
            semilla_modelo = np.random.SeedSequence(semilla).spawn(1)[0]
            self._rng_modelo = np.random.default_rng(semilla_modelo)
        self.actualizaciones_reales = 0
        self.actualizaciones_simuladas = 0

    def actualizar(self, estado, accion, recompensa, siguiente_estado, *, terminado):
        """Aprende de una transición real y luego ejecuta los pasos de planificación."""
        actualizar_q = super().actualizar
        actualizar_q(estado, accion, recompensa, siguiente_estado, terminado=terminado)
        self.actualizaciones_reales += 1
        if self._pasos_planificacion == 0:
            return

        if estado not in self._modelo:
            self._modelo[estado] = {}
            self._estados_observados.append(estado)
        self._modelo[estado][accion] = (recompensa, siguiente_estado, terminado)

        for _ in range(self._pasos_planificacion):
            # Selección uniforme de un estado, luego de una acción registrada en él.
            estado_simulado = self._estados_observados[
                self._rng_modelo.integers(len(self._estados_observados))
            ]
            acciones = self._modelo[estado_simulado]
            accion_simulada = tuple(acciones)[self._rng_modelo.integers(len(acciones))]
            recompensa_simulada, sucesor, terminal = acciones[accion_simulada]
            actualizar_q(
                estado_simulado, accion_simulada, recompensa_simulada, sucesor, terminado=terminal,
            )
            self.actualizaciones_simuladas += 1
