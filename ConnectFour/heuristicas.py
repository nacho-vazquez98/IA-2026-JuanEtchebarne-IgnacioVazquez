"""Funciones de evaluación para COUNTER (C03).

Notación del teórico (Juegos alternados, S. Yovine):

- ``utilidad(s)``: utilidad del agente en un estado final (ganar, empatar, perder).
- ``Eval(s)``: estimación para estados no finales, como combinación lineal
  ponderada de términos ``Eval(s) = Σ wᵢ · fᵢ(s)``.

Cada término ``fᵢ`` se calcula desde el punto de vista de ``jugador`` como
"lo del jugador menos lo del oponente", igual que ``L_X(s) − L_O(s)`` en el
ejemplo de ta-te-ti. Los términos trabajan sobre las 69 ventanas de 4 celdas
alineadas (horizontales, verticales y diagonales) de un tablero de 6×7.
"""
import math
from numbers import Real
from types import MappingProxyType

import numpy as np

from board import Board

FILAS, COLUMNAS, LARGO = 6, 7, 4
UTILIDAD_VICTORIA = 1_000_000
UTILIDAD_EMPATE = 0


def _ventanas():
    ventanas = []
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            for df, dc in ((0, 1), (1, 0), (1, 1), (-1, 1)):
                celdas = [(fila + i * df, col + i * dc) for i in range(LARGO)]
                if all(0 <= f < FILAS and 0 <= c < COLUMNAS for f, c in celdas):
                    ventanas.append([f * COLUMNAS + c for f, c in celdas])
    return np.array(ventanas)


def _ternas_de_captura():
    """Ternas (a, b, c) consecutivas en horizontal o diagonal.

    La regla de captura de ``Board._add_connectedd_tiles`` no incluye la
    dirección vertical.
    """
    ternas = []
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            for df, dc in ((0, 1), (1, 1), (-1, 1)):
                celdas = [(fila + i * df, col + i * dc) for i in range(3)]
                if all(0 <= f < FILAS and 0 <= c < COLUMNAS for f, c in celdas):
                    ternas.append([f * COLUMNAS + c for f, c in celdas])
    return np.array(ternas)


VENTANAS = _ventanas()            # (69, 4) índices planos
TERNAS = _ternas_de_captura()     # índices planos de ternas horizontales y diagonales
COLUMNA_CENTRAL = COLUMNAS // 2


def oponente(jugador):
    return 2 if jugador == 1 else 1


def _grilla(board: Board):
    return np.asarray(board[:])


def _conteos_por_ventana(grilla, jugador):
    valores = grilla.ravel()[VENTANAS]
    propias = (valores == jugador).sum(axis=1)
    ajenas = (valores == oponente(jugador)).sum(axis=1)
    return propias, ajenas


def _jugables(grilla):
    """Máscara plana de celdas vacías donde caería una ficha en este turno."""
    vacias = grilla == 0
    apoyadas = np.ones_like(vacias)
    apoyadas[:-1, :] = grilla[1:, :] != 0
    return (vacias & apoyadas).ravel()


# --- Términos fᵢ(s), todos "jugador menos oponente" -------------------------

def lineas_posibles(board: Board, jugador: int) -> float:
    """``L_jugador − L_oponente``: ventanas que cada uno todavía puede completar.

    Es la función de evaluación del ejemplo de ta-te-ti del curso.
    """
    propias, ajenas = _conteos_por_ventana(_grilla(board), jugador)
    return float(np.count_nonzero(ajenas == 0) - np.count_nonzero(propias == 0))


def lineas_de_2(board: Board, jugador: int) -> float:
    """Ventanas con 2 fichas propias y 2 vacías, menos las del oponente."""
    propias, ajenas = _conteos_por_ventana(_grilla(board), jugador)
    return float(np.count_nonzero((propias == 2) & (ajenas == 0))
                 - np.count_nonzero((ajenas == 2) & (propias == 0)))


def lineas_de_3(board: Board, jugador: int) -> float:
    """Ventanas con 3 fichas propias y 1 vacía (amenazas), menos las del oponente."""
    propias, ajenas = _conteos_por_ventana(_grilla(board), jugador)
    return float(np.count_nonzero((propias == 3) & (ajenas == 0))
                 - np.count_nonzero((ajenas == 3) & (propias == 0)))


def centro(board: Board, jugador: int) -> float:
    """Fichas propias en la columna central menos las del oponente."""
    columna = _grilla(board)[:, COLUMNA_CENTRAL]
    return float(np.count_nonzero(columna == jugador)
                 - np.count_nonzero(columna == oponente(jugador)))


def capturas(board: Board, jugador: int) -> float:
    """Capturas disponibles en la próxima jugada propia menos las del oponente.

    Una captura disponible es una terna ``[jugable, rival, propia]`` en
    horizontal o diagonal: al jugar en la celda jugable se convierte la ficha
    rival del medio (regla propia de este simulador).
    """
    plana = _grilla(board).ravel()
    jugable = _jugables(_grilla(board))
    a, b, c = TERNAS[:, 0], TERNAS[:, 1], TERNAS[:, 2]

    def disponibles(p):
        q = oponente(p)
        medio = plana[b] == q
        return int(np.count_nonzero(medio & jugable[a] & (plana[c] == p))
                   + np.count_nonzero(medio & jugable[c] & (plana[a] == p)))

    return float(disponibles(jugador) - disponibles(oponente(jugador)))


TERMINOS = {
    "lineas_posibles": lineas_posibles,
    "lineas_de_2": lineas_de_2,
    "lineas_de_3": lineas_de_3,
    "centro": centro,
    "capturas": capturas,
}

# Cota de |fᵢ(s)| para cada término: las 69 ventanas, las 6 celdas de la
# columna central y la cantidad de ternas multiplicada por 2 orientaciones.
COTAS = {
    "lineas_posibles": len(VENTANAS),
    "lineas_de_2": len(VENTANAS),
    "lineas_de_3": len(VENTANAS),
    "centro": FILAS,
    "capturas": 2 * len(TERNAS),
}


def utilidad(board: Board, jugador: int) -> float:
    """Utilidad de un estado final para ``jugador``."""
    if board.winner == jugador:
        return UTILIDAD_VICTORIA
    if board.winner == oponente(jugador):
        return -UTILIDAD_VICTORIA
    return UTILIDAD_EMPATE


class FuncionEvaluacion:
    """``Eval(s) = Σ wᵢ · fᵢ(s)``; en estados finales devuelve ``utilidad(s)``.

    Los pesos se limitan para que ``|Eval(s)|`` nunca alcance la utilidad de
    una victoria. Así se cumple ``Eval(ganar) > Eval(empate) > Eval(perder)``,
    el primer criterio de diseño del teórico.
    """

    def __init__(self, pesos: dict, nombre: str = None):
        desconocidos = set(pesos) - set(TERMINOS)
        if desconocidos:
            raise ValueError(f"Términos desconocidos: {sorted(desconocidos)}")
        normalizados = {}
        for t, w in pesos.items():
            if isinstance(w, bool) or not isinstance(w, Real):
                raise ValueError(f"El peso de {t} debe ser un número real finito: {w!r}")
            # Se pasa a float de Python para que la cota no se desborde con
            # enteros de tamaño fijo (p. ej. np.int64).
            try:
                normalizado = float(w)
            except OverflowError:
                normalizado = math.inf
            if not math.isfinite(normalizado):
                raise ValueError(f"El peso de {t} debe ser un número real finito: {w!r}")
            normalizados[t] = normalizado
        cota = sum(abs(w) * COTAS[t] for t, w in normalizados.items())
        if cota >= UTILIDAD_VICTORIA:
            raise ValueError("Los pesos permiten que Eval alcance la utilidad de una victoria")
        # Vista de solo lectura expuesta por una propiedad sin setter: cambiar un
        # peso después de validar la cota podría hacer que un estado no final
        # supere la utilidad de una victoria.
        self._pesos = MappingProxyType({t: w for t, w in normalizados.items() if w != 0})
        self.nombre = nombre or "+".join(f"{w}*{t}" for t, w in pesos.items() if w != 0)

    @property
    def pesos(self):
        return self._pesos

    def terminos(self, board: Board, jugador: int) -> dict:
        return {t: TERMINOS[t](board, jugador) for t in self.pesos}

    def __call__(self, board: Board, jugador: int) -> float:
        if board.is_final():
            return utilidad(board, jugador)
        return sum(w * TERMINOS[t](board, jugador) for t, w in self.pesos.items())

    def __repr__(self):
        return f"FuncionEvaluacion({self.nombre!r}, {dict(self.pesos)})"
