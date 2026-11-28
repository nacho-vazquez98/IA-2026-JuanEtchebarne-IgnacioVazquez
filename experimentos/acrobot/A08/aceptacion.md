# A08 — Selección y aceptación del modelo de Q-Learning

A08 requiere los resultados formales de A07 para elegir la configuración.
[ACR-002](../ACR-002/) permite probar ahora la carga y ejecución de un modelo
de referencia. El modelo de entrega queda pendiente de la selección.

## Selección con los resultados de A07

1. Comparar las configuraciones confirmadas en A07 bajo el mismo
   [protocolo](../protocolo.md). Usar el retorno medio sin descuento en
   validación y las diferencias emparejadas por semilla de entrenamiento.
   Considerar además la dispersión, la tasa de éxito y el tiempo de cada
   réplica. Incluir las grillas y configuraciones descartadas en el registro.
2. Fijar la configuración y el criterio para identificar el modelo de entrega
   con los datos de validación. Si se conservan las réplicas para la comparación
   de A12, identificar el NPZ de cada una y registrar las semillas correspondientes.
3. Registrar el commit, las versiones, los hiperparámetros, las semillas y la
   huella SHA-256 de cada NPZ elegido. Conservar el CSV por episodio y los
   resúmenes, tiempos y gráficos de los experimentos. Reutilizar el modelo ya
   guardado cuando su configuración y procedencia correspondan a la selección.
4. Comprobar la carga y la política greedy como en el ejemplo siguiente.
   Reservar las semillas 200.000–200.999 para la evaluación final una vez
   fijadas las configuraciones que se van a comparar en A12.

## Comprobación reproducible de carga

Desde la raíz del repositorio, con el entorno de Poetry de Acrobot ya instalado,
crear una carpeta de salida nueva. La prueba carga la tabla en un proceso de
evaluación, verifica su huella y reproduce los primeros 20 episodios de
validación que ya están registrados para el mismo modelo.

```sh
mkdir -p .CODEX
salida="$(mktemp -d "$(pwd)/.CODEX/a08-carga-XXXXXX")"
cd Acrobot
referencia=../experimentos/acrobot/ACR-002
modelo="$referencia/entrenamiento/modelo.npz"
poetry run python -B experimentos_qlearning.py evaluar \
    --modelo "$modelo" --conjunto validacion --episodios 20 \
    --salida "$salida/validacion"
poetry run python -B - "$referencia" "$salida/validacion" <<'PY'
import hashlib
import sys
from pathlib import Path

from comparar_grillas import leer_episodios, leer_json
from experimentos_qlearning import EPISODIOS_EVALUACION, SEMILLAS_EVALUACION

experimento, nueva_validacion = map(Path, sys.argv[1:])
archivada = experimento / "validacion"
modelo = experimento / "entrenamiento" / "modelo.npz"
semilla = SEMILLAS_EVALUACION["validacion"]
cantidad = 20

esperadas = leer_episodios(archivada, semilla, EPISODIOS_EVALUACION)[:cantidad]
observadas = leer_episodios(nueva_validacion, semilla, cantidad)
assert esperadas == observadas, "Los episodios guardados y reproducidos difieren."
huella = hashlib.sha256(modelo.read_bytes()).hexdigest()
for fase in (archivada, nueva_validacion):
    config = leer_json(fase, "config.json")
    assert config["sha256_modelo"] == huella, "La huella del NPZ difiere."
    assert config["politica"] == "greedy" and config["epsilon"] == 0
print(f"{cantidad} episodios idénticos y SHA-256 verificado: {huella}")
PY
```

Para la aceptación del modelo de entrega, usar la carpeta del experimento
seleccionado en `referencia` y repetir la comprobación. El registro completo
de validación de cada candidato formal debe corresponder al mismo NPZ.

## Evidencia de la comprobación

El modelo ACR-002 reprodujo exactamente los 20 episodios de validación con
las semillas 100.000–100.019. En esa muestra obtuvo un retorno medio sin
descuento de −462,85 y alcanzó el objetivo en 19 episodios. Se comprobó que
la huella del archivo coincide con la validación archivada y con la nueva.
La prueba usa el mismo prefijo del CSV de ACR-002 y conserva el modelo en
su ubicación original. [Evidencia y procedencia](verificacion-referencia.json)
