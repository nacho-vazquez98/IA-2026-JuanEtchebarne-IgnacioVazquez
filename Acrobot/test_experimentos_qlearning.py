import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

import gymnasium as gym
import numpy as np

from experimentos_qlearning import evaluar_episodio, resumir_evaluacion


class TestExperimentosQLearning(unittest.TestCase):
    def test_retorno_y_exito_se_calculan_de_la_misma_trayectoria(self):
        entorno = Mock(spec=gym.Env)
        entorno.action_space = gym.spaces.Discrete(3)
        entorno.reset.return_value = (None, {})
        entorno.step.side_effect = [
            (None, -1, False, False, {}),
            (None, -1, False, False, {}),
            (None, 0, True, True, {}),
        ]
        fila = evaluar_episodio(entorno, None, np.random.default_rng(42), semilla=100_000)
        self.assertEqual(fila["pasos"], 3)
        self.assertEqual(fila["retorno"], -2)
        self.assertAlmostEqual(fila["retorno_descontado"], -1.99)
        self.assertIsNone(fila["max_q_inicial"])
        resumen = resumir_evaluacion([fila])
        self.assertEqual(resumen["tasa_exito"], 1)
        self.assertEqual(resumen["pasos_promedio_exitos"], 3)

    def test_resumen_sin_exitos_omite_una_media_de_pasos_inexistente(self):
        resumen = resumir_evaluacion([{
            "terminado": False, "retorno": -700, "retorno_descontado": -99,
            "max_q_inicial": -60, "pasos": 700,
        }])
        self.assertEqual(resumen["tasa_exito"], 0)
        self.assertIsNone(resumen["pasos_promedio_exitos"])
        self.assertEqual(resumen["max_q_inicial_promedio"], -60)

    def test_cli_entrena_guarda_y_ejecuta_greedy_en_otro_proceso(self):
        script = Path(__file__).with_name("experimentos_qlearning.py").resolve()
        comando = [sys.executable, "-B", str(script)]
        with TemporaryDirectory() as raiz:
            entrenamiento = Path(raiz) / "entrenamiento"
            evaluacion = Path(raiz) / "evaluacion"
            entrenamiento_cli = [
                *comando, "entrenar", "--episodios", "2", "--salida", str(entrenamiento),
            ]
            subprocess.run(entrenamiento_cli, capture_output=True, check=True, timeout=30)
            modelo = entrenamiento / "modelo.npz"
            antes = modelo.read_bytes()
            self.assertTrue(antes)
            entrenamiento_csv = entrenamiento / "episodios.csv"
            with entrenamiento_csv.open(newline="", encoding="utf-8") as archivo:
                filas = list(csv.DictReader(archivo))
            self.assertEqual([float(fila["epsilon"]) for fila in filas], [1.0, 0.05])

            subprocess.run(
                [*comando, "evaluar", "--episodios", "2", "--modelo", str(modelo),
                 "--salida", str(evaluacion)],
                capture_output=True, check=True, timeout=30,
            )
            config = json.loads((evaluacion / "config.json").read_text(encoding="utf-8"))
            resumen = json.loads((evaluacion / "resumen.json").read_text(encoding="utf-8"))
            self.assertEqual(config["epsilon"], 0)
            self.assertEqual(config["semilla_entorno_inicial"], 100_000)
            self.assertEqual(resumen["episodios"], 2)
            self.assertIsNotNone(resumen["max_q_inicial_promedio"])
            self.assertTrue((evaluacion / "utilidad.png").is_file())
            self.assertEqual(modelo.read_bytes(), antes)

            repetido = subprocess.run(entrenamiento_cli, capture_output=True, timeout=30)
            self.assertEqual(repetido.returncode, 2)
            self.assertEqual(modelo.read_bytes(), antes)
