"""Pruebas de las funciones de evaluación (C03).

Ejecutar desde ``ConnectFour/``: ``poetry run python -m unittest -v``
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from agentes_base import AgenteAleatorio
from arena import jugar_partida
from board import Board
from heuristicas import (
    TERMINOS, UTILIDAD_VICTORIA, VENTANAS, FuncionEvaluacion,
    capturas, centro, lineas_de_2, lineas_de_3, lineas_posibles, oponente, utilidad,
)


def tablero(*jugadas):
    """Arma un tablero aplicando (columna, jugador) en orden con las reglas reales."""
    b = Board(6, 7)
    for columna, jugador in jugadas:
        b.add_tile(columna, jugador)
    return b


def grilla(celdas):
    """Tablero con fichas colocadas directamente (sin aplicar capturas)."""
    b = Board(6, 7)
    for (fila, col), jugador in celdas.items():
        b._grid[fila][col] = jugador
        b._empty_spaces -= 1
    return b


def reproducir(secuencia):
    b, jugador = Board(6, 7), 1
    for columna in secuencia:
        b.add_tile(columna, jugador)
        jugador = 2 if jugador == 1 else 1
    return b


class Ventanas(unittest.TestCase):
    def test_hay_69_ventanas_distintas(self):
        self.assertEqual(len(VENTANAS), 69)
        self.assertEqual(len({tuple(sorted(v)) for v in VENTANAS.tolist()}), 69)


class Terminos(unittest.TestCase):
    def test_tablero_vacio_es_neutral(self):
        vacio = Board(6, 7)
        for nombre, f in TERMINOS.items():
            self.assertEqual(f(vacio, 1), 0, nombre)

    def test_terminos_son_antisimetricos(self):
        b = reproducir(jugar_partida(AgenteAleatorio(3), AgenteAleatorio(4)).jugadas[:12])
        for nombre, f in TERMINOS.items():
            self.assertEqual(f(b, 1), -f(b, 2), nombre)

    def test_lineas_posibles_ficha_central(self):
        # Una ficha en la base de la columna central participa en 7 ventanas
        # (4 horizontales, 1 vertical, 1 por cada diagonal) que el rival pierde.
        self.assertEqual(lineas_posibles(tablero((3, 1)), 1), 7)

    def test_lineas_de_2_y_3(self):
        b = tablero((0, 1), (1, 1), (2, 1))
        self.assertGreater(lineas_de_3(b, 1), 0)
        self.assertGreater(lineas_de_2(b, 1), 0)
        self.assertEqual(lineas_de_3(b, 2), -lineas_de_3(b, 1))

    def test_centro(self):
        self.assertEqual(centro(tablero((3, 1), (3, 2), (3, 1)), 1), 1)

    def test_capturas_detecta_terna_jugable(self):
        # Fila base: _ 2 1 1. El jugador 1 captura jugando en la columna 0;
        # el jugador 2 no tiene capturas disponibles.
        b = grilla({(5, 1): 2, (5, 2): 1, (5, 3): 1})
        self.assertEqual(capturas(b, 1), 1)
        b.add_tile(0, 1)
        self.assertEqual(b[5][1], 1)  # la captura predicha ocurre en el simulador

    def test_capturas_ignora_celdas_no_jugables(self):
        # Diagonal (5,0)=1, (4,1)=2, (3,2) vacía pero sin soporte: (4,2) está vacía.
        b = grilla({(5, 0): 1, (5, 1): 1, (4, 1): 2, (5, 2): 1})
        self.assertEqual(capturas(b, 1), 0)
        # Con soporte en (4,2) la celda (3,2) pasa a ser jugable y la captura cuenta.
        b = grilla({(5, 0): 1, (5, 1): 1, (4, 1): 2, (5, 2): 1, (4, 2): 2})
        self.assertEqual(capturas(b, 1), 1)

    def test_capturas_coincide_con_el_simulador(self):
        """En posiciones aleatorias, capturas() = fichas convertidas de verdad.

        Para cada jugador se suma, sobre todas sus jugadas legales, cuántas
        fichas rivales cambian de dueño al aplicar ``add_tile``.
        """
        def convertidas(b, jugador):
            total = 0
            for columna in b.get_posible_actions():
                hijo = b.clone()
                antes = (hijo[:] == oponente(jugador)).sum()
                hijo.add_tile(columna, jugador)
                total += antes - (hijo[:] == oponente(jugador)).sum()
            return total

        for semilla in range(200):
            jugadas = jugar_partida(AgenteAleatorio(semilla), AgenteAleatorio(semilla + 1)).jugadas
            b = reproducir(jugadas[: max(1, len(jugadas) - 1)])
            if b.is_final():
                continue
            self.assertEqual(capturas(b, 1), convertidas(b, 1) - convertidas(b, 2), semilla)

    def test_capturas_no_cuenta_vertical(self):
        b = tablero((0, 1), (0, 2))  # columna 0: 1 abajo, 2 arriba, vacía encima
        self.assertEqual(capturas(b, 1), 0)


class FuncionDeEvaluacion(unittest.TestCase):
    def test_ordena_estados_finales(self):
        """Criterio 1 del teórico: Eval(ganar) > Eval(empate) > Eval(perder)."""
        f = FuncionEvaluacion({t: 1 for t in TERMINOS})
        gana_1 = tablero((0, 1), (0, 1), (0, 1), (0, 1))
        self.assertTrue(gana_1.is_final())
        self.assertEqual(f(gana_1, 1), UTILIDAD_VICTORIA)
        self.assertEqual(f(gana_1, 2), -UTILIDAD_VICTORIA)
        no_final = tablero((0, 1), (1, 2))
        self.assertLess(abs(f(no_final, 1)), UTILIDAD_VICTORIA)

    def test_empate_vale_cero(self):
        b = Board(6, 7)
        b._empty_spaces = 0  # tablero lleno sin ganador
        self.assertEqual(utilidad(b, 1), 0)

    def test_combinacion_lineal(self):
        b = reproducir([3, 2, 3, 4, 2])
        f = FuncionEvaluacion({"lineas_posibles": 2, "centro": -1.5})
        esperado = 2 * lineas_posibles(b, 1) - 1.5 * centro(b, 1)
        self.assertAlmostEqual(f(b, 1), esperado)

    def test_rechaza_pesos_que_alcanzan_la_victoria(self):
        with self.assertRaises(ValueError):
            FuncionEvaluacion({"lineas_posibles": UTILIDAD_VICTORIA})
        with self.assertRaises(ValueError):
            FuncionEvaluacion({"inexistente": 1})

    def test_rechaza_pesos_no_finitos_o_no_numericos(self):
        for peso in (float("nan"), float("inf"), -float("inf"), "1", None, True):
            with self.assertRaises(ValueError, msg=repr(peso)):
                FuncionEvaluacion({"centro": peso})

    def test_pesos_no_se_pueden_modificar_tras_validar_la_cota(self):
        """Evita que un estado no final supere la utilidad de una victoria."""
        f = FuncionEvaluacion({"centro": 1})
        with self.assertRaises(TypeError):
            f.pesos["centro"] = 1_000_001
        b = tablero((3, 1))
        self.assertFalse(b.is_final())
        self.assertEqual(f(b, 1), 1)


class CliExperimento(unittest.TestCase):
    SCRIPT = Path(__file__).with_name("experimentos_heuristicas.py").resolve()

    def ejecutar(self, *argumentos):
        return subprocess.run(
            [sys.executable, "-B", str(self.SCRIPT), "CNT-003", *argumentos],
            capture_output=True, text=True, timeout=120,
        )

    def test_rechaza_sobrescribir_una_corrida_existente(self):
        with TemporaryDirectory() as base:
            existente = Path(base) / "CNT-003"
            existente.mkdir()
            (existente / "resumen.json").write_text("original", encoding="utf-8")
            salida = self.ejecutar("--partidas", "1", "--carpeta-base", base)
            self.assertEqual(salida.returncode, 2, salida.stderr)
            self.assertEqual(sorted(p.name for p in existente.iterdir()), ["resumen.json"])
            self.assertEqual((existente / "resumen.json").read_text(encoding="utf-8"), "original")

    def test_replica_con_otro_id_no_toca_la_original(self):
        with TemporaryDirectory() as base:
            existente = Path(base) / "CNT-003"
            existente.mkdir()
            salida = self.ejecutar("--partidas", "1", "--carpeta-base", base, "--id", "CNT-003-r1")
            self.assertEqual(salida.returncode, 0, salida.stderr)
            self.assertEqual(list(existente.iterdir()), [])
            replica = Path(base) / "CNT-003-r1"
            self.assertTrue((replica / "partidas.csv").is_file())
            config = json.loads((replica / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["id"], "CNT-003-r1")


if __name__ == "__main__":
    unittest.main()
