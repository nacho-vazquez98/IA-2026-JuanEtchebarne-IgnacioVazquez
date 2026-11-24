# Registro de decisiones del obligatorio de Inteligencia Artificial

Este archivo es una **bitácora técnica compartida** para ACROBAT y COUNTER. Su objetivo es conservar las decisiones importantes y su justificación, como insumo para el informe final que elaborarán y revisarán los estudiantes.

## Reglas de registro

- Registrar únicamente decisiones técnicas importantes, con su motivo, alternativas relevantes, consecuencias y evidencia disponible.
- No inventar métricas, pruebas ni justificaciones a posteriori.
- Antes de incorporar una decisión dudosa, consultar al usuario.
- Agregar nuevas entradas sin reescribir ni eliminar el trabajo del otro integrante.
- Cada modificación debe formar parte de la rama de la feature correspondiente.

## Decisiones

<!--
Modelo sugerido para futuras entradas:

### AAAA-MM-DD — [ACROBAT o COUNTER] — Título de la decisión
- **Tarea:** Axx / Cxx / Pxx / Ixx.
- **Decisión:** ...
- **Justificación:** ...
- **Alternativas consideradas:** ...
- **Impacto o limitaciones:** ...
- **Evidencia / cómo se verificó:** ...
-->

### 2026-11-17 — Entornos de Poetry independientes

- **Tarea** — P03.
- **Decisión** — Conservar los manifiestos, archivos de bloqueo y configuraciones de Poetry provistos para Acrobot y Connect Four. Cada proyecto usa una `.venv` local y mantiene sus versiones resueltas en su propio `poetry.lock`.
- **Motivo** — La consigna pide dos entornos separados. Compartir un entorno o un archivo de bloqueo acoplaría las dependencias. Por ejemplo, Acrobot declara `pygame` para el modo gráfico y Connect Four renderiza el tablero en la terminal.
- **Verificación** — Los dos archivos de bloqueo coinciden con las declaraciones de sus manifiestos, y ambas configuraciones habilitan `.venv` dentro del proyecto. La instalación y la ejecución de los simuladores corresponden a P04.

### 2026-11-17 — ACROBAT — Contrato de Acrobot y discretizaciones iniciales

**P04 y A01.** Se usó Python 3.12.14 y Poetry 2.1.1 en Codex Cloud, con
`poetry check --lock`, `poetry env use "$(command -v python3.12)"` y
`poetry sync --no-interaction` desde `Acrobot/`. El entorno bloqueado instaló
Gymnasium 1.1.1 y NumPy 1.26.4. Se mantuvo el límite de 700 pasos del notebook
y se ejecutó sin renderizado con `poetry run python validar_entorno.py`.

- La observación `float32` es `[cos(θ₁), sin(θ₁), cos(θ₂), sin(θ₂), ω₁, ω₂]`.
  El espacio usa `[-1, 1]` para cada seno y coseno y topes simétricos de
  aproximadamente 12.5664 y 28.2743 rad/s para las velocidades.
- Las acciones `0, 1, 2` aplican torques `−1, 0, +1`. El simulador alcanza
  el objetivo cuando `−cos(θ₁) − cos(θ₁ + θ₂) > 1`. Devuelve `0` en ese
  paso y `−1` en los demás. `TimeLimit` gestiona el truncamiento.
- Con semilla 42, la política aleatoria usó las tres acciones, truncó al
  paso 700 y acumuló −700. Las velocidades observadas fueron
  `[−3.2595, 3.3384]` y `[−6.1731, 6.3617]` rad/s.
- Con la misma semilla, aplicar torque en el sentido de la segunda velocidad
  alcanzó el objetivo al paso 67, con retorno −66 y recompensa final 0.
  Sus velocidades fueron `[−4.3382, 4.0914]` y `[−6.7032, 7.6021]` rad/s.
  Las dos políticas reprodujeron exactamente observaciones, acciones,
  recompensas y banderas al repetir sus corridas.

**A02 y A03.** El notebook consume las observaciones directamente. El repositorio
y Acrobot-v1 no ofrecen una grilla reutilizable. La transformación usa el
`Box` del entorno para obtener los topes y `numpy.searchsorted` para ubicar
cada valor entre bordes configurables.

| Variante | Dimensiones e intervalos | Celdas Q con 3 acciones |
| --- | --- | ---: |
| Directa | 4 intervalos uniformes por seno y coseno en [−1, 1] y 6 por velocidad entre sus topes | 27 648 |
| Angular | 12 intervalos uniformes por ángulo en [−π, π) y 8 por velocidad, con bordes de −1, −0.5, −0.25, −0.125, 0, 0.125, 0.25, 0.5 y 1 veces su tope | 27 648 |

Ambas grillas reservan 9 216 estados y 216 KiB para una tabla densa
`float64` con tres acciones. La directa evita recuperar ángulos, pero
reserva celdas para pares seno/coseno incompatibles con el círculo unitario.
La angular recupera cada ángulo con `atan2`, asigna más resolución a las
velocidades bajas observadas y conserva los topes físicos para trayectorias
futuras. La separación de estados cercanos a lados opuestos de ±π puede
afectar el aprendizaje. Ambas variantes asignan un borde interno al
intervalo de su derecha, saturan valores finitos fuera de rango y
rechazan observaciones de forma incorrecta o con valores no finitos.

`poetry run python -m unittest -v` ejecutó cinco pruebas con éxito. Cubren
extremos, saturación, bordes internos, equivalencia de ±π, entradas inválidas
y claves repetibles para indexar ambas tablas Q en las 769 observaciones de
las dos trayectorias. Las corridas verifican el contrato y muestran rangos
de ejemplo. Queda pendiente medir cobertura y aprendizaje con más semillas
y comparar las variantes en A06.

### 2026-11-22 — ACROBAT — Actualización Q-Learning y fin de episodio

- **Tarea** — A04.
- **Representación** — Una tabla densa `float64` inicializada en cero, con las
  dimensiones del discretizador y un eje final para las acciones de Acrobot.
  El agente usa las claves de A03 tanto para elegir acciones como para actualizar
  la tabla a partir de cada transición observada.
- **Exploración** — En cada paso, con probabilidad ε se elige cualquiera de las
  acciones uniformemente. En el resto de los casos se escoge un máximo de Q,
  con desempate uniforme para evitar favorecer un índice cuando varios valores
  coinciden. El agente tiene su propio generador con semilla opcional. Quien
  ejecuta el episodio aporta ε, lo que permite variar su valor entre episodios
  y elegir solo máximos con ε = 0.
- **Objetivo de la actualización** — Con tasa α, se incorpora una fracción α de
  la diferencia entre el objetivo y el valor Q actual. El objetivo es
  `recompensa + γ × max Q(estado_siguiente, ·)` si el ambiente sigue en un
  estado no terminal y `recompensa` si Gymnasium indica `terminated`.
  Un truncamiento por límite externo cierra el episodio y conserva el valor
  del estado siguiente. Si ambas banderas son verdaderas, el estado es terminal.
- **Evidencia** — `poetry run python -B -m unittest -v` desde `Acrobot/` pasó
  11 pruebas. Se verificaron la actualización numérica, las tres combinaciones
  de fin de episodio, la elección de acciones legales en los extremos de ε y la
  igualdad de la tabla tras repetir la corrida con cada grilla. En una
  comprobación sin renderizado con semilla 42 para agente y entorno, α = 0.5,
  γ = 0.9 y ε = 0.2, ambas grillas completaron 700 pasos por truncamiento con
  retorno −700. La directa actualizó 322 celdas a valores distintos de cero
  (0.072 s) y la angular 477 (0.071 s). Estas corridas verifican que las
  actualizaciones llegan a la tabla. La comparación de desempeño corresponde a
  A06, usando el protocolo de entrenamiento y evaluación de A05.
