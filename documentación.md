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

### 2026-11-24 — COUNTER — Rival oficial y protocolo base de partidas

- **Tarea** — C01, P05 y P06.
- **Decisión** — Evaluar contra el Stratego que entrega la cátedra, sin modificarlo: `load_enemy_agent()` (`Stratego(2, 4)`) como jugador 2. Nuestro agente siempre empieza, como en `play_vs_loaded_agent`. Las partidas se juegan con `arena.jugar_partida`, que reproduce los turnos de `play_vs_other_agent` sin imprimir, mide el tiempo por decisión y devuelve el ganador. Los resultados crudos se guardan en `experimentos/counter/CNT-NNN/` y cada corrida se anota en `experimentos/counter/registro.md`.
- **Motivo** — El equipo eligió ceñirse a la configuración de la cátedra. `play_vs_other_agent` imprime el tablero, no devuelve el ganador y no mide tiempos. Para no modificar el código entregado se agregó un módulo aparte que reutiliza el entorno, `Board` y `load_enemy_agent`.
- **Alternativas consideradas** — (B) construir Stratego con el número que corresponde a su turno y alternar quién empieza; (C) evaluar con las dos configuraciones. Se descartaron para no apartarse de lo entregado.
- **Impacto o limitaciones** — `Stratego(a, d)` se asigna el jugador `(a % 2) + 1`, así que el oficial evalúa como si fuera el jugador 1 aunque juega como jugador 2. En CNT-002 esa configuración ganó menos contra un agente aleatorio que la coincidente (86 contra 94 victorias de 100 como jugador 2). Como Stratego es determinista, contra un agente determinista hay una sola partida posible por configuración; se usarán aperturas forzadas y su tamaño se definirá en C08. Además, el simulador tiene una regla de **captura**: una ficha rival encerrada en horizontal o diagonal pasa al jugador que la encierra, y esa captura puede completar un cuatro en línea. Las heurísticas deberán considerarlo.
- **Evidencia** — `test_arena.py` (11 pruebas: reglas de captura, ausencia de captura vertical, determinismo de Stratego, equivalencia con `play_vs_other_agent`). CNT-001: el agente aleatorio gana 14 de 100 partidas contra el Stratego oficial. CNT-002: comparación de las cuatro combinaciones de constructor y turno.
- **Pendiente** — Consultar a los docentes si la asignación de jugador del Stratego oficial es intencional.
