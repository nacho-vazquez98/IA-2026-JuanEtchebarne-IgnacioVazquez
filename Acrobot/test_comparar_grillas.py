import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import comparar_grillas as comparador


class ValidacionComparacion(unittest.TestCase):
    def setUp(self):
        temporal = TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)
        self.validacion = self.raiz / "ACR-999" / "validacion"
        self.entrenamiento = self.raiz / "ACR-999" / "entrenamiento"
        self.validacion.mkdir(parents=True)
        self.entrenamiento.mkdir()

    def escribir_json(self, carpeta, nombre, datos):
        (carpeta / nombre).write_text(json.dumps(datos), encoding="utf-8")

    def escribir_episodios(self, carpeta, filas):
        with (carpeta / "episodios.csv").open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=filas[0])
            escritor.writeheader()
            escritor.writerows(filas)

    def test_rechaza_semillas_incompletas(self):
        self.escribir_episodios(self.validacion, [
            {"semilla": 100, "pasos": 2, "retorno": -1, "terminado": True, "truncado": False},
        ])
        with self.assertRaisesRegex(ValueError, "semillas"):
            comparador.leer_episodios(self.validacion, 100, 2)

    def test_rechaza_retorno_o_truncamiento_inconsistente(self):
        fila = {"semilla": 100, "pasos": 2, "retorno": -1, "terminado": True, "truncado": False}
        for cambio in ({"retorno": 0}, {"truncado": True}):
            with self.subTest(cambio=cambio):
                self.escribir_episodios(self.validacion, [{**fila, **cambio}])
                with self.assertRaisesRegex(ValueError, "Episodio inconsistente"):
                    comparador.leer_episodios(self.validacion, 100, 1)

    def test_medir_validacion_verifica_descuento_y_resumen(self):
        self.escribir_json(self.validacion, "config.json", {
            "entorno": comparador.ENTORNO, "episodios": 1,
            "politica": "greedy", "conjunto": "validacion", "epsilon": 0,
            "max_pasos": comparador.MAX_PASOS, "gamma_evaluacion": comparador.GAMMA_EVALUACION,
            "semilla_politica": comparador.SEMILLA_POLITICA,
        })
        fila = {
            "semilla": comparador.SEMILLAS_EVALUACION["validacion"], "pasos": 3,
            "retorno": -2, "retorno_descontado": -1.99, "max_q_inicial": -4,
            "terminado": True, "truncado": False,
        }
        resumen = {
            "episodios": 1, "retorno_promedio": -2, "desviacion_retorno": 0,
            "retorno_descontado_promedio": -1.99, "max_q_inicial_promedio": -4,
            "tasa_exito": 1, "pasos_promedio_exitos": 3, "segundos": 0.1,
        }
        with patch.object(comparador, "EPISODIOS_EVALUACION", 1):
            self.escribir_episodios(self.validacion, [{**fila, "retorno_descontado": -2}])
            with self.assertRaisesRegex(ValueError, "Retorno descontado"):
                comparador.medir_validacion(self.validacion, "greedy")
            self.escribir_episodios(self.validacion, [fila])
            self.escribir_json(self.validacion, "resumen.json", {**resumen, "retorno_promedio": -3})
            with self.assertRaisesRegex(ValueError, "retorno_promedio"):
                comparador.medir_validacion(self.validacion, "greedy")
            self.escribir_json(self.validacion, "resumen.json", resumen)
            self.assertEqual(comparador.medir_validacion(self.validacion, "greedy")["tasa_exito"], 1)

    def test_medir_replica_rechaza_otro_algoritmo_y_hash_alterado(self):
        config = {
            "entorno": comparador.ENTORNO, "version": comparador.VERSION_MODELO,
            "algoritmo": "qlearning", "episodios": 2,
            "grilla": "angular", "alpha": 0.5, "gamma": 0.99, "epsilon_inicial": 1,
            "epsilon_final": 0.05, "decaimiento": "lineal_por_episodio",
            "max_pasos": comparador.MAX_PASOS, "semilla_entorno_inicial": 10, "semilla_agente": 20,
        }
        episodio = {"pasos": 2, "retorno": -1, "terminado": True, "truncado": False}
        self.escribir_episodios(self.entrenamiento, [
            {**episodio, "semilla": 10, "epsilon": 1},
            {**episodio, "semilla": 11, "epsilon": 0.05},
        ])
        self.escribir_json(self.entrenamiento, "resumen.json", {"tasa_exito": 1})
        self.escribir_json(self.validacion, "config.json", {"sha256_modelo": "0" * 64})
        (self.entrenamiento / "modelo.npz").write_bytes(b"otro modelo")
        casos = (("dynaq", "Configuración de entrenamiento"), ("qlearning", "difiere"))
        with patch.object(comparador, "EPISODIOS_ENTRENAMIENTO", 2):
            for algoritmo, mensaje in casos:
                with self.subTest(algoritmo=algoritmo):
                    self.escribir_json(self.entrenamiento, "config.json", {**config, "algoritmo": algoritmo})
                    with self.assertRaisesRegex(ValueError, mensaje):
                        comparador.medir_replica(self.raiz, "ACR-999", "angular", 10, 20)

    def test_cli_rechaza_destino_existente_antes_de_leer_datos(self):
        script = Path(comparador.__file__)
        corrida = subprocess.run(
            [sys.executable, "-B", str(script), "--datos", str(self.raiz / "ausente"),
             "--salida", str(self.validacion)],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(corrida.returncode, 2, corrida.stderr)
        self.assertIn("Ya existe la carpeta", corrida.stderr)
