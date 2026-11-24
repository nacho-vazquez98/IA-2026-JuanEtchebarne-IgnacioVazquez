# Obligatorio de Inteligencia Artificial — instrucciones compartidas

Este archivo rige para **Claude Code y Codex**. En Codex, `AGENTS.md` debe remitir a él.

## Fuente y alcance
- Leer `Obligatorio_IA_Agosto_2026.pdf`, los códigos base de la cátedra y `PLAN_TAREAS_IA.md` antes de actuar. El enunciado y las interfaces reales prevalecen sobre estas instrucciones.
- **ACROBAT:** discretización de Acrobot, Q-Learning, exploración de hiperparámetros, Dyna-Q (Sutton y Barto, §§8.1–8.2), comparación y al menos un modelo entrenado reutilizable.
- **COUNTER:** Connect Four con Minimax, poda Alpha-Beta, Expectimax, distintas funciones heurísticas ponderadas y pruebas documentadas, incluidas partidas contra Stratego.
- Python y **un entorno Poetry independiente por proyecto**. No inventar requisitos, APIs, mediciones ni resultados.

## Git y colaboración
1. **Antes de cualquier feature:** el primer agente verifica el estado del repositorio y crea el `.gitignore` inicial (si no existe), incluyendo `/.CODEX/`, `/.CLAUDE/`, entornos virtuales, cachés, archivos temporales y secretos. Comprobar que ambas carpetas auxiliares están ignoradas. **Debe crear una rama desde `main`, registrar el `.gitignore`, subir la rama y abrir un Pull Request (PR) hacia `main` en GitHub.** Antes de continuar con otras features, ese PR debe estar revisado, fusionado y reflejado en `main` remoto. Si no hay remoto, acceso a GitHub o condiciones seguras para completar el flujo, consultar al usuario.
2. **El `.gitignore` queda protegido después de su creación inicial:** ningún agente podrá modificarlo por iniciativa propia. Si descubre una omisión, **notificará al usuario**, explicará la regla propuesta y su motivo, y **solo la aplicará tras la aprobación expresa del usuario**. Una vez autorizado, el cambio también debe pasar por una rama y un PR; no eludir esta regla modificando exclusiones locales como sustituto permanente.
3. **Una rama por feature**, siempre creada desde `main` actualizado; nombres sugeridos: `feature/acrobot-discretizacion`, `feature/counter-expectimax`. Trabajar y hacer commits en esa rama y subirla al remoto; **no realizar commits ni pushes directos a `main`**.
4. Cuando la feature esté probada, **abrir un Pull Request en GitHub desde su rama hacia `main`**. El PR debe resumir el objetivo, cambios, pruebas realizadas, resultados y decisiones relevantes. Solicitar revisión del compañero, atender observaciones y verificar los controles disponibles del repositorio. **Integrar únicamente mediante el PR**, una vez revisado y conforme a las aprobaciones/reglas del repositorio; actualizar `main` antes de comenzar la siguiente feature. Resolver conflictos sin sobrescribir trabajo ajeno. No usar `push --force`, `reset --hard` ni borrar ramas/trabajo de terceros sin permiso. Si existe riesgo de pérdida o un conflicto no trivial, consultar.
5. Los archivos auxiliares **propios de los agentes** van exclusivamente en `/.CODEX/` (Codex) o `/.CLAUDE/` (Claude Code). **Ninguno de esos directorios puede quedar trackeado por Git.** Los archivos del proyecto, tests, modelos requeridos e informe van fuera de esas carpetas. No ignorar indiscriminadamente `.pkl`, `.py`, `.ipynb` o resultados necesarios para la entrega.

## Reutilización de funciones y cambios al código existente
1. **Antes de crear cualquier función o utilidad**, buscar implementaciones equivalentes en todo el proyecto y revisar su contrato, parámetros, usos y pruebas. **Si ya existe una función que resuelve la necesidad, reutilizarla** mediante importación o llamada directa; no duplicarla, copiarla ni crear un envoltorio innecesario.
2. Si una función existente puede cubrir el caso con **una modificación pequeña** (por ejemplo, añadir un parámetro opcional para imprimir el resultado), **no modificarla todavía**. Explicar al usuario qué función se encontró, qué cambio se propone, por qué conviene reutilizarla, su compatibilidad e impacto en llamadas y tests; **pedir aprobación explícita antes de editarla**. La autorización cubre solo el cambio descrito.
3. No crear una función duplicada para evitar solicitar autorización. Si ninguna función existente es adecuada, explicar brevemente por qué y crear únicamente la funcionalidad necesaria, con pruebas. Ante dudas sobre reutilización o impacto, consultar.

## Subagentes y orquestación
1. **Preferir la ejecución paralela con subagentes cuando la herramienta lo permita**, siempre que las subtareas sean independientes y exista autorización del usuario. El agente principal actúa como **orquestador responsable**: define el alcance, reparte trabajo, supervisa, integra y valida los resultados.
2. Antes de implementar una feature, preparar un **plan de implementación** con pasos, precedencias, archivos previstos, pruebas y tareas que podrían delegarse sin conflictos. Comunicarlo al usuario. **Si la preferencia de multiagente es `preguntar`, solicitar autorización antes de delegar**, ofreciendo estas opciones: **solo esta vez**, **siempre que sea viable (sin volver a pedir autorización para usar subagentes)** o **no usar subagentes**.
3. Si el usuario elige la opción permanente, registrar `siempre` en el archivo de preferencias del **agente correspondiente**. Desde ese momento, delegar automáticamente cuando convenga sin volver a pedir permiso ni interrumpir solo por el uso de subagentes, hasta que el usuario cambie su preferencia. Se puede comunicar el plan de forma informativa; esto **no elimina las autorizaciones específicas obligatorias** (p. ej. `.gitignore`, modificaciones menores de funciones existentes, cambios destructivos).
4. No asignar cambios simultáneos al mismo archivo sin coordinación. Respetar **una rama por feature**, evitar trabajo concurrente sobre `main` y validar de forma integrada. Si no hay capacidad real de subagentes, informarlo y trabajar sin simular delegaciones.

## Preferencias personales por agente
- Cada agente debe crear en su **primera ejecución**, si todavía no existe, su propio archivo local: `/.CODEX/preferencias.md` para Codex o `/.CLAUDE/preferencias.md` para Claude Code. Estas carpetas y su contenido **no se versionan ni se comparten por Git**; no incluir secretos.
- Mantener allí, como mínimo, `modo_multiagente: preguntar | siempre | nunca` (valor inicial: `preguntar`), `nivel_consultas: normal | frecuente | mínimo` (inicial: `normal`) y otras preferencias que **el usuario indique expresamente**. No deducir preferencias permanentes a partir de una autorización puntual.
- Leer estas preferencias al comenzar cada sesión y actualizarlas cuando el usuario solicite un cambio; si falta una opción o es ambigua, conservar el valor seguro `preguntar`. Cada agente mantiene las preferencias de **su usuario**, sin imponerlas al otro agente.
- `nivel_consultas: mínimo` evita consultas discrecionales, **pero nunca omite aprobaciones exigidas** por este documento ni permite asumir consentimiento ante dudas importantes.

## Decisiones y documentación
- Mantener en la raíz el archivo **`documentación.md`**, versionado y compartido. Registrar durante cada feature las **decisiones técnicas importantes**: qué se decidió, por qué, alternativas consideradas, consecuencias y evidencia disponible (pruebas/resultados), sin inventar información. Ejemplos: discretización, política de exploración, hiperparámetros, planificación de Dyna-Q, heurísticas, profundidades, modelo de adversario, métricas y persistencia.
- **Ante la duda de si corresponde documentar una decisión, consultar al usuario antes de incluirla.** Evitar registrar acciones triviales. Agregar entradas sin reescribir las del otro agente; incluir actualizaciones de `documentación.md` en el commit de la feature.
- `documentación.md` está dividido en secciones por ejercicio: **Decisiones comunes**, **ACROBAT** y **COUNTER**. Cada agente agrega sus entradas **al final de la sección del ejercicio en el que trabaja**. Las decisiones que afectan a ambos proyectos van en *Decisiones comunes*. No se editan ni reordenan las secciones del otro ejercicio. Así se evitan conflictos entre ramas paralelas.
- `documentación.md` es una **bitácora de apoyo**, no reemplaza el informe final, que los estudiantes deben revisar, comprender y elaborar.

## Implementación y validación
- Reutilizar el simulador entregado sin alterar las reglas; favorecer código legible y modular. Antes de implementar, revisar dependencias y alcance de la tarea.
- Separar entrenamiento de evaluación. Registrar configuraciones, semillas (cuando apliquen), corridas, tiempos y métricas para poder comparar alternativas. No adjudicar mejoras sin pruebas. Probar primero ejecuciones breves; consultar antes de entrenamientos extensos no acordados.
- Guardar al menos **un modelo computado de ACROBAT** y probar su carga y ejecución; conservar resultados necesarios para el informe y los gráficos.
- Al cerrar cada feature, comunicar archivos modificados, comandos para ejecutar/probar, resultados, decisiones registradas y pendientes.

## Entrega
- Código Python (`.py` y/o `.ipynb`), modelos computados e informe PDF de **máximo 20 páginas más anexos**, con explicación del método, experimentos, tiempos, resultados, gráficos y dificultades.
- Informar las herramientas de IA generativa usadas y el contexto de uso; todo contenido de IA debe ser verificado por los estudiantes.
- Un único **ZIP de hasta 40 MB**. **Entrega: 10/12/2026 a las 21:00. Defensa: 14/12/2026**, obligatoria y eliminatoria.
