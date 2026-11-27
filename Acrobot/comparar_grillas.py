"""Reconstruye la comparación A06 a partir de los resultados crudos de Acrobot."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, stdev

from experimentos_qlearning import (
    EPISODIOS_ENTRENAMIENTO,
    EPISODIOS_EVALUACION,
    GAMMA_EVALUACION,
    MAX_PASOS,
    SEMILLAS_EVALUACION,
    SEMILLA_POLITICA,
    resumir_evaluacion,
)

REPLICAS = {
    "angular": ("ACR-002", "ACR-004", "ACR-005"),
    "directa": ("ACR-006", "ACR-007", "ACR-008"),
}
SEMILLAS = (10_000, 20_000, 30_000)
REFERENCIA = "ACR-003"


def leer_json(carpeta, nombre):
    return json.loads((carpeta / nombre).read_text(encoding="utf-8"))


def leer_episodios(carpeta, primera_semilla, cantidad):
    with (carpeta / "episodios.csv").open(newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    semillas = [int(fila["semilla"]) for fila in filas]
    if semillas != list(range(primera_semilla, primera_semilla + cantidad)):
        raise ValueError(f"Las semillas o la cantidad de episodios no coinciden en {carpeta}.")
    for fila in filas:
        pasos = int(fila["pasos"])
        terminado = fila["terminado"] == "True"
        truncado = fila["truncado"] == "True"
        retorno = float(fila["retorno"])
        if (not 1 <= pasos <= MAX_PASOS or not (terminado or truncado)
                or truncado != (pasos == MAX_PASOS) or retorno != -pasos + terminado):
            raise ValueError(f"Episodio inconsistente en {carpeta}, semilla {fila['semilla']}.")
    return filas


def medir_validacion(carpeta, politica):
    config = leer_json(carpeta, "config.json")
    campos = {
        "politica": politica, "conjunto": "validacion", "max_pasos": MAX_PASOS,
        "gamma_evaluacion": GAMMA_EVALUACION, "semilla_politica": SEMILLA_POLITICA,
    }
    if politica == "greedy":
        campos["epsilon"] = 0
    if any(config[k] != v for k, v in campos.items()):
        raise ValueError(f"Configuración de validación incompatible en {carpeta}.")

    datos = []
    for fila in leer_episodios(carpeta, SEMILLAS_EVALUACION["validacion"], EPISODIOS_EVALUACION):
        retorno = float(fila["retorno"])
        descontado = float(fila["retorno_descontado"])
        esperado = -(1 - GAMMA_EVALUACION ** (-retorno)) / (1 - GAMMA_EVALUACION)
        if not math.isclose(descontado, esperado, abs_tol=1e-10):
            raise ValueError(f"Retorno descontado inconsistente en {carpeta}.")
        valor_q = fila["max_q_inicial"]
        if (politica == "greedy") != bool(valor_q):
            raise ValueError(f"Valor inicial de Q inesperado en {carpeta}.")
        datos.append({
            "pasos": int(fila["pasos"]),
            "terminado": fila["terminado"] == "True",
            "retorno": retorno,
            "retorno_descontado": descontado,
            "max_q_inicial": float(valor_q) if valor_q else None,
        })

    calculado = resumir_evaluacion(datos)
    guardado = leer_json(carpeta, "resumen.json")
    for campo, valor in calculado.items():
        if valor is None:
            coincide = guardado[campo] is None
        else:
            coincide = math.isclose(guardado[campo], valor)
        if not coincide:
            raise ValueError(f"La métrica {campo} no coincide en {carpeta}.")
    return {**calculado, "segundos_validacion": guardado["segundos"]}


def medir_replica(raiz, id_corrida, grilla, semilla, semilla_agente):
    carpeta = raiz / id_corrida / "entrenamiento"
    config = leer_json(carpeta, "config.json")
    campos = {
        "grilla": grilla, "alpha": 0.5, "gamma": 0.99, "epsilon_inicial": 1,
        "epsilon_final": 0.05, "decaimiento": "lineal_por_episodio", "max_pasos": MAX_PASOS,
        "semilla_entorno_inicial": semilla, "semilla_agente": semilla_agente,
    }
    if any(config[k] != v for k, v in campos.items()):
        raise ValueError(f"Configuración de entrenamiento incompatible en {carpeta}.")
    filas = leer_episodios(carpeta, semilla, EPISODIOS_ENTRENAMIENTO)
    epsilons = [float(fila["epsilon"]) for fila in filas]
    if epsilons[0] != 1 or epsilons[-1] != 0.05 or any(
        anterior <= siguiente for anterior, siguiente in zip(epsilons, epsilons[1:])
    ):
        raise ValueError(f"Secuencia de ε incompatible en {carpeta}.")

    resumen = leer_json(carpeta, "resumen.json")
    tabla = carpeta / "modelo.npz"
    validacion = raiz / id_corrida / "validacion"
    hash_modelo = hashlib.sha256(tabla.read_bytes()).hexdigest()
    if hash_modelo != leer_json(validacion, "config.json")["sha256_modelo"]:
        raise ValueError(f"La tabla evaluada difiere del modelo guardado en {carpeta}.")
    return {
        "id": id_corrida,
        "grilla": grilla,
        "semilla_entorno": semilla,
        "semilla_agente": semilla_agente,
        "pasos_entrenamiento": sum(int(fila["pasos"]) for fila in filas),
        "segundos_entrenamiento": resumen["segundos"],
        "bytes_tabla_q": resumen["bytes_tabla_q"],
        "bytes_modelo_npz": tabla.stat().st_size,
        "celdas_q_no_nulas": resumen["celdas_q_no_nulas"],
        **medir_validacion(validacion, "greedy"),
    }


def graficar(replicas, referencia, destino):
    from matplotlib.figure import Figure

    figura = Figure(figsize=(9.8, 4.3), layout="constrained")
    retorno, costo = figura.subplots(1, 2)
    posiciones = [1, 2]
    for indice, semilla in enumerate(SEMILLAS):
        filas = [fila for fila in replicas if fila["semilla_entorno"] == semilla]
        etiqueta = f"Semilla {semilla:,}".replace(",", ".")
        retorno.plot(posiciones, [f["retorno_promedio"] for f in filas], "o-", label=etiqueta)
        costo.plot(posiciones, [f["pasos_entrenamiento"] / 1e6 for f in filas], "o-",
                   color=f"C{indice}")
    retorno.axhline(referencia["retorno_promedio"], linestyle="--", color="#555555",
                    label="Agente aleatorio")
    retorno.set(title="Utilidad media en validación", ylabel="Retorno sin descuento")
    costo.set(title="Interacciones durante el entrenamiento", ylabel="Millones de pasos")
    for eje in (retorno, costo):
        eje.set_xticks(posiciones, ["Angular", "Directa"])
        eje.set_xlim(0.8, 2.2)
        eje.grid(axis="y", alpha=0.25)
    retorno.legend(loc="lower left", bbox_to_anchor=(0.015, 0.075), fontsize="small")
    figura.savefig(destino, dpi=160)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path,
                        default=Path(__file__).resolve().parents[1] / "experimentos/acrobot")
    parser.add_argument("--salida", type=Path, required=True, help="Carpeta nueva para el resumen")
    args = parser.parse_args()
    resultados = [
        medir_replica(args.datos, id_corrida, grilla, semilla, 310_000 + indice)
        for grilla, ids in REPLICAS.items()
        for indice, (id_corrida, semilla) in enumerate(zip(ids, SEMILLAS), start=1)
    ]
    referencia = medir_validacion(args.datos / REFERENCIA / "validacion", "aleatoria")
    agrupado = {}
    metricas = (
        "retorno_promedio", "retorno_descontado_promedio", "tasa_exito",
        "pasos_promedio_exitos", "max_q_inicial_promedio", "pasos_entrenamiento",
    )
    for grilla in REPLICAS:
        filas = [f for f in resultados if f["grilla"] == grilla]
        agrupado[grilla] = {}
        for campo in metricas:
            valores = [f[campo] for f in filas if f[campo] is not None]
            agrupado[grilla][campo] = {
                "media": mean(valores) if valores else None,
                "desviacion_entre_replicas": stdev(valores) if len(valores) >= 2 else None,
            }

    pares = []
    for semilla in SEMILLAS:
        angular, directa = [f for f in resultados if f["semilla_entorno"] == semilla]
        pares.append({
            "semilla_entorno": semilla,
            "retorno_directa_menos_angular": directa["retorno_promedio"] - angular["retorno_promedio"],
        })
    resumen = {"referencia": referencia, "grillas": agrupado, "pares": pares}
    args.salida.mkdir(parents=True)
    with (args.salida / "replicas.csv").open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=resultados[0].keys(), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(resultados)
    (args.salida / "resumen.json").write_text(
        json.dumps(resumen, indent=2) + "\n",
        encoding="utf-8",
    )
    graficar(resultados, referencia, args.salida / "comparacion.png")


if __name__ == "__main__":
    main()
