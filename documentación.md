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
