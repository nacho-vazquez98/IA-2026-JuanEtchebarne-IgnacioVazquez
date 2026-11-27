"""Entrenamiento reproducible y evaluación de modelos tabulares de Acrobot."""

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from statistics import mean, pstdev
from tempfile import TemporaryDirectory
from time import perf_counter

import gymnasium as gym
import numpy as np

from discretizacion import DiscretizadorAcrobot
from qlearning import AgenteQLearning
from validar_entorno import MAX_PASOS


ENTORNO = "Acrobot-v1"
EPISODIOS_ENTRENAMIENTO = 10_000
EPISODIOS_EVALUACION = 1_000
SEMILLAS_EVALUACION = {"validacion": 100_000, "final": 200_000}
SEMILLA_POLITICA = 300_000
GAMMA_EVALUACION = 0.99
VERSION_MODELO = 1
GRILLAS = {
    "directa": DiscretizadorAcrobot.directa,
    "angular": DiscretizadorAcrobot.angular,
}


def crear_agente(entorno, configuracion, semilla):
    grilla = GRILLAS[configuracion["grilla"]](entorno.observation_space)
    return AgenteQLearning(
        grilla, entorno.action_space.n,
        alpha=configuracion["alpha"], gamma=configuracion["gamma"], semilla=semilla,
    )


def entrenar(entorno, agente, *, episodios, semilla, epsilon_inicial, epsilon_final):
    """Usa un descenso lineal de ε por episodio y registra el resultado de cada episodio."""
    if episodios < 1:
        raise ValueError("Se requiere al menos un episodio.")
    if semilla < 0 or semilla + episodios > min(SEMILLAS_EVALUACION.values()):
        raise ValueError("Las semillas de entrenamiento deben quedar entre 0 y 99999.")
    if not 0 <= epsilon_final <= epsilon_inicial <= 1:
        raise ValueError("Se requiere 0 <= epsilon_final <= epsilon_inicial <= 1.")

    filas = []
    epsilons = np.linspace(epsilon_inicial, epsilon_final, episodios)
    for indice, epsilon in enumerate(epsilons):
        semilla_entorno = semilla + indice
        retorno, pasos, terminado, truncado = agente.aprender_episodio(
            entorno, epsilon=float(epsilon), semilla=semilla_entorno,
        )
        filas.append({
            "episodio": indice + 1, "semilla": semilla_entorno, "epsilon": float(epsilon),
            "pasos": pasos, "retorno": retorno, "terminado": terminado, "truncado": truncado,
        })
    return filas


def evaluar_episodio(entorno, agente, rng, *, semilla):
    """Mide una trayectoria greedy o aleatoria sin actualizar la tabla Q."""
    observacion, _ = entorno.reset(seed=semilla)
    estado = agente.discretizador.transformar(observacion) if agente else None
    valor_inicial = float(agente.q[estado].max()) if agente else None
    retorno = retorno_descontado = 0.0
    descuento = 1.0
    pasos = 0

    while True:
        if agente is None:
            accion = int(rng.integers(entorno.action_space.n))
        else:
            accion = agente.seleccionar_accion(estado, epsilon=0)
        observacion, recompensa, terminado, truncado, _ = entorno.step(accion)
        retorno += recompensa
        retorno_descontado += descuento * recompensa
        descuento *= GAMMA_EVALUACION
        pasos += 1
        if terminado or truncado:
            return {
                "semilla": semilla, "pasos": pasos, "retorno": retorno,
                "retorno_descontado": retorno_descontado, "max_q_inicial": valor_inicial,
                "terminado": terminado, "truncado": truncado,
            }
        if agente is not None:
            estado = agente.discretizador.transformar(observacion)


def resumir_evaluacion(filas):
    pasos_exitosos = [fila["pasos"] for fila in filas if fila["terminado"]]
    retornos = [fila["retorno"] for fila in filas]
    valores = [fila["max_q_inicial"] for fila in filas if fila["max_q_inicial"] is not None]
    return {
        "episodios": len(filas),
        "retorno_promedio": mean(retornos),
        "desviacion_retorno": pstdev(retornos),
        "retorno_descontado_promedio": mean(fila["retorno_descontado"] for fila in filas),
        "max_q_inicial_promedio": mean(valores) if valores else None,
        "tasa_exito": len(pasos_exitosos) / len(filas),
        "pasos_promedio_exitos": mean(pasos_exitosos) if pasos_exitosos else None,
    }


def cargar_modelo(ruta, entorno, semilla):
    """Reconstruye el agente y comprueba la versión, grilla y forma de la tabla guardada."""
    contenido = ruta.read_bytes()
    with np.load(BytesIO(contenido), allow_pickle=False) as archivo:
        configuracion = json.loads(archivo["configuracion"].item())
        if configuracion["version"] != VERSION_MODELO or configuracion["entorno"] != ENTORNO:
            raise ValueError("Versión o ambiente del modelo incompatible.")
        agente = crear_agente(entorno, configuracion, semilla)
        tabla = archivo["q"]
        if tabla.shape != agente.q.shape or tabla.dtype != agente.q.dtype:
            raise ValueError("La tabla Q no coincide con la grilla o las acciones.")
        if not np.isfinite(tabla).all():
            raise ValueError("La tabla Q contiene valores no finitos.")
        agente.q[:] = tabla
    return agente, configuracion, hashlib.sha256(contenido).hexdigest()


def graficar_utilidad(filas, destino):
    from matplotlib.figure import Figure

    figura = Figure(figsize=(7.2, 4.0), layout="constrained")
    eje = figura.subplots()
    episodios = np.arange(1, len(filas) + 1)
    acumulado = np.cumsum([fila["retorno"] for fila in filas]) / episodios
    eje.plot(episodios, acumulado, color="#24568c", label="Retorno medio acumulado")
    eje.axhline(acumulado[-1], color="#a54d25", linestyle="--",
                label=f"Promedio final: {acumulado[-1]:.2f}")
    eje.set(title="Utilidad del estado inicial en evaluación",
            xlabel="Episodios de evaluación", ylabel="Retorno sin descuento")
    eje.grid(axis="y", alpha=0.25)
    eje.legend()
    figura.savefig(destino, dpi=150)


def guardar_resultados(destino, configuracion, filas, resumen, modelo=None):
    """Publica una carpeta completa de resultados y preserva corridas anteriores."""
    procedencia = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parent,
        capture_output=True, text=True, check=False,
    )
    metadatos = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit": procedencia.stdout.strip() or None,
        "gymnasium": gym.__version__,
        "numpy": np.__version__,
        **configuracion,
    }
    destino.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=destino.parent) as temporal:
        carpeta = Path(temporal) / "corrida"
        carpeta.mkdir()
        for nombre, datos in (("config", metadatos), ("resumen", resumen)):
            (carpeta / f"{nombre}.json").write_text(
                json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
            )
        with (carpeta / "episodios.csv").open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=filas[0].keys(), lineterminator="\n")
            escritor.writeheader()
            escritor.writerows(filas)
        if modelo is None:
            graficar_utilidad(filas, carpeta / "utilidad.png")
        else:
            np.savez_compressed(
                carpeta / "modelo.npz", q=modelo.q, configuracion=json.dumps(configuracion),
            )
        if destino.exists():
            raise FileExistsError(f"Ya existe la carpeta {destino}.")
        carpeta.rename(destino)


def ejecutar_entrenamiento(args, entorno):
    configuracion = {
        "version": VERSION_MODELO,
        "entorno": ENTORNO,
        "max_pasos": MAX_PASOS,
        "algoritmo": "qlearning",
        "grilla": args.grilla,
        "alpha": args.alpha,
        "gamma": args.gamma,
        "episodios": args.episodios,
        "semilla_entorno_inicial": args.semilla,
        "semilla_agente": args.semilla_agente,
        "decaimiento": "lineal_por_episodio",
        "epsilon_inicial": args.epsilon_inicial,
        "epsilon_final": args.epsilon_final,
    }
    agente = crear_agente(entorno, configuracion, args.semilla_agente)
    inicio = perf_counter()
    filas = entrenar(
        entorno, agente, episodios=args.episodios, semilla=args.semilla,
        epsilon_inicial=args.epsilon_inicial, epsilon_final=args.epsilon_final,
    )
    resumen = {
        "episodios": len(filas),
        "segundos": perf_counter() - inicio,
        "retorno_promedio": mean(fila["retorno"] for fila in filas),
        "tasa_exito": sum(fila["terminado"] for fila in filas) / len(filas),
        "celdas_q_no_nulas": int(np.count_nonzero(agente.q)),
        "bytes_tabla_q": agente.q.nbytes,
    }
    guardar_resultados(args.salida, configuracion, filas, resumen, modelo=agente)
    return resumen


def ejecutar_evaluacion(args, entorno):
    if not 1 <= args.episodios <= EPISODIOS_EVALUACION:
        raise ValueError("Se requieren entre 1 y 1000 episodios de evaluación.")
    rng = np.random.default_rng(SEMILLA_POLITICA)
    agente = modelo = huella = None
    if args.modelo is not None:
        agente, modelo, huella = cargar_modelo(args.modelo, entorno, SEMILLA_POLITICA)
    semilla_inicial = SEMILLAS_EVALUACION[args.conjunto]
    inicio = perf_counter()
    filas = []
    for episodio in range(args.episodios):
        fila = evaluar_episodio(entorno, agente, rng, semilla=semilla_inicial + episodio)
        filas.append({"episodio": episodio + 1, **fila})
    resumen = resumir_evaluacion(filas)
    resumen["segundos"] = perf_counter() - inicio
    configuracion = {
        "entorno": ENTORNO, "max_pasos": MAX_PASOS,
        "politica": "greedy" if agente is not None else "aleatoria",
        "epsilon": 0 if agente is not None else None,
        "modelo": modelo, "sha256_modelo": huella,
        "conjunto": args.conjunto, "episodios": args.episodios,
        "semilla_entorno_inicial": semilla_inicial, "semilla_politica": SEMILLA_POLITICA,
        "gamma_evaluacion": GAMMA_EVALUACION,
    }
    guardar_resultados(args.salida, configuracion, filas, resumen)
    return resumen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    comandos = parser.add_subparsers(dest="comando", required=True)
    entrenamiento = comandos.add_parser("entrenar")
    entrenamiento.add_argument("--grilla", choices=GRILLAS, default="angular")
    entrenamiento.add_argument("--episodios", type=int, default=EPISODIOS_ENTRENAMIENTO)
    entrenamiento.add_argument("--semilla", type=int, default=10_000)
    entrenamiento.add_argument("--semilla-agente", type=int, default=310_001)
    entrenamiento.add_argument("--alpha", type=float, default=0.5)
    entrenamiento.add_argument("--gamma", type=float, default=0.99)
    entrenamiento.add_argument("--epsilon-inicial", type=float, default=1)
    entrenamiento.add_argument("--epsilon-final", type=float, default=0.05)
    entrenamiento.add_argument("--salida", type=Path, required=True)
    entrenamiento.set_defaults(ejecutar=ejecutar_entrenamiento)

    evaluacion = comandos.add_parser("evaluar")
    origen = evaluacion.add_mutually_exclusive_group(required=True)
    origen.add_argument("--modelo", type=Path)
    origen.add_argument("--aleatorio", action="store_true")
    evaluacion.add_argument("--conjunto", choices=SEMILLAS_EVALUACION, default="validacion")
    evaluacion.add_argument("--episodios", type=int, default=EPISODIOS_EVALUACION)
    evaluacion.add_argument("--salida", type=Path, required=True)
    evaluacion.set_defaults(ejecutar=ejecutar_evaluacion)

    args = parser.parse_args()
    if args.salida.exists():
        parser.error(f"Ya existe la carpeta {args.salida}.")
    try:
        with gym.make(ENTORNO, render_mode=None, max_episode_steps=MAX_PASOS) as entorno:
            resumen = args.ejecutar(args, entorno)
    except (KeyError, OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(resumen, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
