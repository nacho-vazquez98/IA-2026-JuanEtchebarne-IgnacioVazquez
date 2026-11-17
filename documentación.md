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
