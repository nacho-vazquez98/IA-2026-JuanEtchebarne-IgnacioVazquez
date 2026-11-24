"""Guardado de resultados crudos de experimentos en ``experimentos/counter/<ID>/``."""
import csv
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parent.parent
CARPETA_EXPERIMENTOS = RAIZ_REPO / "experimentos" / "counter"


def commit_actual():
    try:
        salida = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=RAIZ_REPO, capture_output=True, text=True, check=True,
        )
        # Los resultados de experimentos no cuentan como cambios de código.
        sucio = subprocess.run(
            ["git", "status", "--porcelain", "--", ".", ":(exclude)experimentos"],
            cwd=RAIZ_REPO, capture_output=True, text=True, check=True,
        ).stdout.strip()
        return salida.stdout.strip() + ("-sucio" if sucio else "")
    except (OSError, subprocess.CalledProcessError):
        return "desconocido"


def guardar_corrida(id_experimento, configuracion, filas, resumen, carpeta_base=None):
    """Escribe ``config.json``, ``partidas.csv`` y ``resumen.json``; devuelve la carpeta."""
    carpeta = Path(carpeta_base or CARPETA_EXPERIMENTOS) / id_experimento
    carpeta.mkdir(parents=True, exist_ok=True)

    metadatos = {
        "id": id_experimento,
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "commit": commit_actual(),
        "python": sys.version.split()[0],
        "plataforma": platform.platform(),
        "configuracion": configuracion,
    }
    (carpeta / "config.json").write_text(
        json.dumps(metadatos, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (carpeta / "resumen.json").write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if filas:
        with open(carpeta / "partidas.csv", "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(filas[0].keys()))
            escritor.writeheader()
            escritor.writerows(filas)
    return carpeta
