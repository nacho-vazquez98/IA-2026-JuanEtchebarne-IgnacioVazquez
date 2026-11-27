# Registro de decisiones del obligatorio de Inteligencia Artificial

Este archivo es una **bitácora técnica compartida** para ACROBAT y COUNTER. Su objetivo es conservar las decisiones importantes y su justificación, como insumo para el informe final que elaborarán y revisarán los estudiantes.

## Reglas de registro

- Registrar únicamente decisiones técnicas importantes, con su motivo, alternativas relevantes, consecuencias y evidencia disponible.
- No inventar métricas, pruebas ni justificaciones a posteriori.
- Antes de incorporar una decisión dudosa, consultar al usuario.
- Agregar nuevas entradas sin reescribir ni eliminar el trabajo del otro integrante.
- Cada modificación debe formar parte de la rama de la feature correspondiente.

## Decisiones

Cada entrada va en la sección de su proyecto: **ACROBAT** o **COUNTER**. Las decisiones que afectan a los dos proyectos van en **Decisiones comunes**. Las entradas nuevas se agregan al final de la sección correspondiente, así cada integrante edita solo la suya.

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

## Decisiones comunes

### 2026-11-17 — Entornos de Poetry independientes

- **Tarea** — P03.
- **Decisión** — Conservar los manifiestos, archivos de bloqueo y configuraciones de Poetry provistos para Acrobot y Connect Four. Cada proyecto usa una `.venv` local y mantiene sus versiones resueltas en su propio `poetry.lock`.
- **Motivo** — La consigna pide dos entornos separados. Compartir un entorno o un archivo de bloqueo acoplaría las dependencias. Por ejemplo, Acrobot declara `pygame` para el modo gráfico y Connect Four renderiza el tablero en la terminal.
- **Verificación** — Los dos archivos de bloqueo coinciden con las declaraciones de sus manifiestos, y ambas configuraciones habilitan `.venv` dentro del proyecto. La instalación y la ejecución de los simuladores corresponden a P04.

## ACROBAT — Acrobot (Q-Learning y Dyna-Q)

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

### 2026-11-26 — ACROBAT — Protocolo de evaluación y persistencia

- **Tareas** — P05 y A05.
- **Métrica** — La utilidad inicial se estima con el retorno observado medio
  sin descuento porque refleja éxitos y duración con la misma escala para
  todas las políticas. En las mismas trayectorias se calcula el retorno
  descontado con γ de evaluación de 0,99, la tasa de éxito y los pasos medios
  entre éxitos. Para los modelos tabulares también se registra el máximo Q
  inicial como diagnóstico.
- **Reproducibilidad** — Se fijaron conjuntos disjuntos de semillas para el
  entrenamiento, la validación y la evaluación final. La tabla se guarda en
  NPZ, con la configuración necesaria para reconstruir su grilla y sus
  hiperparámetros. El evaluador carga el modelo en un proceso independiente y
  no actualiza la tabla. Se usa Matplotlib para generar el gráfico en el
  entorno Poetry de Acrobot.
- **Protocolo** — [Protocolo experimental y comandos](experimentos/acrobot/protocolo.md).

## COUNTER — Connect Four (Minimax, Alpha-Beta y Expectimax)

### 2026-11-24 — COUNTER — Rival oficial y protocolo base de partidas

- **Tarea** — C01, P05 y P06.
- **Decisión** — Evaluar contra el Stratego que entrega la cátedra, sin modificarlo: `load_enemy_agent()` (`Stratego(2, 4)`) como jugador 2. Nuestro agente siempre empieza, como en `play_vs_loaded_agent`. Las partidas se juegan con `arena.jugar_partida`, que reproduce los turnos de `play_vs_other_agent` sin imprimir, mide el tiempo por decisión y devuelve el ganador. Los resultados crudos se guardan en `experimentos/counter/CNT-NNN/` y cada corrida se anota en `experimentos/counter/registro.md`.
- **Motivo** — El equipo eligió ceñirse a la configuración de la cátedra. `play_vs_other_agent` imprime el tablero, no devuelve el ganador y no mide tiempos. Para no modificar el código entregado se agregó un módulo aparte que reutiliza el entorno, `Board` y `load_enemy_agent`.
- **Alternativas consideradas** — (B) construir Stratego con el número que corresponde a su turno y alternar quién empieza; (C) evaluar con las dos configuraciones. Se descartaron para no apartarse de lo entregado.
- **Impacto o limitaciones** — `Stratego(a, d)` se asigna el jugador `(a % 2) + 1`, así que el oficial evalúa como si fuera el jugador 1 aunque juega como jugador 2. En CNT-002 esa configuración ganó menos contra un agente aleatorio que la coincidente (86 contra 94 victorias de 100 como jugador 2). Como Stratego es determinista, contra un agente determinista hay una sola partida posible por configuración; se usarán aperturas forzadas y su tamaño se definirá en C08. Además, el simulador tiene una regla de **captura**: una ficha rival encerrada en horizontal o diagonal pasa al jugador que la encierra, y esa captura puede completar un cuatro en línea. Las heurísticas deberán considerarlo.
- **Evidencia** — `test_arena.py` (11 pruebas: reglas de captura, ausencia de captura vertical, determinismo de Stratego, equivalencia con `play_vs_other_agent`). CNT-001: el agente aleatorio gana 14 de 100 partidas contra el Stratego oficial. CNT-002: comparación de las cuatro combinaciones de constructor y turno.
- **Actualización (2026-11-24)** — Juan Etchebarne confirmó que la asignación de jugador del Stratego oficial es **intencional**. Se mantiene la evaluación contra `load_enemy_agent()` sin cambios, y en el informe se describirá como una característica del rival, no como un error.

### 2026-11-24 — COUNTER — Estructura de las funciones de evaluación

- **Tarea** — C03.
- **Decisión** — Se usa la estructura del teórico: `utilidad(s)` para estados finales (±1 000 000 por ganar o perder, 0 por empate) y, para los demás, `Eval(s) = Σ wᵢ·fᵢ(s)`, implementada en `ConnectFour/heuristicas.py`. Cada término se calcula como "jugador menos oponente", igual que `L_X − L_O` en el ta-te-ti de clase. Los términos son:
  - `lineas_posibles`: el del ejemplo de clase, ventanas de 4 celdas que cada jugador todavía puede completar;
  - `lineas_de_2` y `lineas_de_3`: ventanas con 2 o 3 fichas propias y el resto vacío;
  - `centro`: fichas en la columna central;
  - `capturas`: ternas horizontales o diagonales `[celda jugable, rival, propia]` que permiten capturar en la próxima jugada.
- **Motivo** — Mantener la notación y el modelo lineal ponderado del curso, y tener términos separables para probarlos solos y combinados, como pide la letra. `capturas` se agregó porque el simulador tiene una regla de captura que un Connect Four clásico no tiene.
- **Alternativas consideradas** — Reutilizar la heurística de Stratego: se descartó porque es el código del rival y depende de su número de jugador interno. Pesos distintos según la etapa de la partida: se pospone porque se aparta del modelo del curso; CNT-003 sugiere que podría servir.
- **Impacto o limitaciones** — `FuncionEvaluacion` acepta solo pesos reales finitos (los normaliza a `float` para que la cota no se desborde), los expone como solo lectura y rechaza los que permitan que `|Eval|` alcance la utilidad de una victoria. Así se garantiza `Eval(ganar) > Eval(empate) > Eval(perder)`, el primer criterio de diseño del teórico.
- **Evidencia** — `test_heuristicas.py` (22 pruebas). Una de ellas verifica en posiciones aleatorias que `capturas` coincide exactamente con las fichas que convierte el simulador. CNT-003 mide costo y correlación de cada término: `lineas_de_3` (r = 0,21) y `centro` (r = 0,22) son los más informativos y `lineas_posibles` tiene r = 0,11.
