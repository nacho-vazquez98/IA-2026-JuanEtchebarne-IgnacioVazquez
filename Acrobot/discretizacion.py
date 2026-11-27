"""Transformaciones de observaciones de Acrobot a claves de una tabla Q."""

import numpy as np


class DiscretizadorAcrobot:
    """Usa bordes crecientes por dimensión, incluidos ambos extremos."""

    def __init__(self, bordes, *, usar_angulos=False):
        self._usar_angulos = usar_angulos
        self._bordes = tuple(np.array(eje, dtype=np.float64) for eje in bordes)
        dimensiones = 4 if usar_angulos else 6
        if len(self._bordes) != dimensiones:
            raise ValueError(f"Se requieren bordes para {dimensiones} dimensiones.")
        for eje in self._bordes:
            if (
                eje.ndim != 1
                or eje.size < 2
                or not np.isfinite(eje).all()
                or not np.all(eje[1:] > eje[:-1])
            ):
                raise ValueError("Cada eje requiere al menos dos bordes finitos y crecientes.")

    @classmethod
    def directa(cls, espacio_observacion):
        """Grilla uniforme sobre cosenos, senos y velocidades."""
        intervalos = (4, 4, 4, 4, 6, 6)
        bordes = [
            np.linspace(inferior, superior, cantidad + 1)
            for inferior, superior, cantidad in zip(
                espacio_observacion.low, espacio_observacion.high, intervalos
            )
        ]
        return cls(bordes)

    @classmethod
    def directa_no_uniforme(cls, espacio_observacion):
        """Grilla directa con seis intervalos de velocidad más finos cerca de cero."""
        directa = cls.directa(espacio_observacion)
        fracciones = np.array([-1, -0.5, -0.125, 0, 0.125, 0.5, 1])
        bordes_velocidad = [
            fracciones * float(maximo) for maximo in espacio_observacion.high[4:]
        ]
        return cls((*directa._bordes[:4], *bordes_velocidad))

    @classmethod
    def angular(cls, espacio_observacion):
        """Grilla angular uniforme con intervalos de velocidad más finos cerca de cero."""
        bordes_angulares = np.linspace(-np.pi, np.pi, 13)
        fracciones = np.array([-1, -0.5, -0.25, -0.125, 0, 0.125, 0.25, 0.5, 1])
        bordes_velocidad = [
            fracciones * float(maximo) for maximo in espacio_observacion.high[4:]
        ]
        return cls((bordes_angulares, bordes_angulares, *bordes_velocidad), usar_angulos=True)

    @property
    def forma(self):
        """Forma de la grilla de estados, antes de agregar el eje de acciones."""
        return tuple(eje.size - 1 for eje in self._bordes)

    def transformar(self, observacion):
        """Devuelve una tupla de índices, saturando los extremos de cada eje."""
        valores = np.asarray(observacion, dtype=np.float64)
        if valores.shape != (6,) or not np.isfinite(valores).all():
            raise ValueError("Se requiere una observación de Acrobot con seis valores finitos.")

        if self._usar_angulos:
            angulos = np.arctan2(valores[1:4:2], valores[0:4:2])
            # Ambos representantes del ángulo de la costura deben dar la misma clave.
            angulos[angulos == np.pi] = -np.pi
            valores = np.concatenate((angulos, valores[4:]))

        # Buscar solo bordes internos satura en el primer o último intervalo.
        return tuple(
            int(np.searchsorted(eje[1:-1], valor, side="right"))
            for eje, valor in zip(self._bordes, valores)
        )
