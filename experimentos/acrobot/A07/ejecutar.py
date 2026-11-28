"""Genera o ejecuta las corridas de A07 con el CLI de Acrobot."""

import argparse
from itertools import product
from pathlib import Path
import shlex
import subprocess
import sys


REFERENCIA = (0.50, 0.99, 0.05)
REPLICAS = ((10_000, 310_001), (20_000, 310_002), (30_000, 310_003))


def planificar(fase):
    if fase == "piloto":
        variantes = (REFERENCIA, *product((0.25, 0.75), (0.97, 0.995), (0.02, 0.20)))
        corridas = [
            (f"ACR-{numero:03d}", variante, REPLICAS[0])
            for numero, variante in enumerate(variantes, start=14)
        ]
        return 60, 16, corridas

    variantes = {
        "referencia": REFERENCIA,
        "acr-018": (0.25, 0.995, 0.20),
        "acr-020": (0.75, 0.97, 0.20),
        "intermedia": (0.50, 0.985, 0.20),
    }
    corridas = [
        (f"semilla-{semillas[0]}/{nombre}", variante, semillas)
        for semillas in REPLICAS
        for nombre, variante in variantes.items()
    ]
    return 500, 100, corridas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fase", choices=("piloto", "ronda-1"))
    modo = parser.add_mutually_exclusive_group(required=True)
    modo.add_argument("--plan", action="store_true", help="Mostrar los comandos sin ejecutarlos.")
    modo.add_argument("--salida", type=Path, help="Carpeta nueva para los resultados.")
    args = parser.parse_args()

    archivo = Path(__file__).resolve().parents[3] / "Acrobot" / "experimentos_qlearning.py"
    comando = [sys.executable, "-B", str(archivo)]
    salida = args.salida or Path("resultados")
    if args.salida:
        try:
            salida.mkdir(parents=True)
        except FileExistsError:
            parser.error(f"Ya existe {salida}.")

    entrenamientos, validaciones, corridas = planificar(args.fase)
    for nombre, (alpha, gamma, epsilon), (semilla, semilla_agente) in corridas:
        destino = salida / nombre
        entrenar = [
            *comando, "entrenar", "--grilla", "angular", "--episodios", str(entrenamientos),
            "--alpha", str(alpha), "--gamma", str(gamma), "--epsilon-inicial", "1",
            "--epsilon-final", str(epsilon), "--semilla", str(semilla),
            "--semilla-agente", str(semilla_agente), "--salida", str(destino / "entrenamiento"),
        ]
        validar = [
            *comando, "evaluar", "--conjunto", "validacion", "--episodios", str(validaciones),
            "--modelo", str(destino / "entrenamiento" / "modelo.npz"), "--salida",
            str(destino / "validacion"),
        ]
        for comando_fase in (entrenar, validar):
            print(shlex.join(comando_fase), flush=True)
            if args.salida:
                subprocess.run(comando_fase, check=True)


if __name__ == "__main__":
    main()
