# Registro de experimentos — COUNTER (Connect Four)

Registro de **todas** las corridas de COUNTER, incluidas las exploratorias, fallidas o descartadas. No se borran ni reescriben entradas: si una conclusión cambia, se agrega una entrada nueva que la corrige. Las decisiones importantes se resumen además en `documentación.md`.

## Protocolo común

- **IDs:** `CNT-NNN`, correlativos. Los resultados crudos de cada corrida están en `experimentos/counter/CNT-NNN/`:
  - `config.json`: configuración, fecha, commit, versión de Python y plataforma;
  - `partidas.csv`: una fila por partida, con la secuencia completa de columnas jugadas;
  - `resumen.json`: totales por variante.
- **Rival oficial:** `load_enemy_agent()` de `play.py`, es decir `Stratego(2, 4)` como **jugador 2**. Nuestro agente **siempre empieza** (jugador 1), igual que en `play_vs_loaded_agent`. Así lo decidió el equipo el 2026-11-24 para ceñirse a la configuración entregada por la cátedra (ver CNT-002 y `documentación.md`).
- **Ejecución:** `arena.jugar_partida` reproduce los turnos de `play_vs_other_agent` sin renderizar. Una prueba automática verifica que da el mismo ganador. Una jugada ilegal interrumpe la corrida con `JugadaIlegal`.
- **Variabilidad:** Stratego es determinista. Contra un agente también determinista, cada configuración produce **una sola partida posible**. Para comparar con más de una partida se usarán aperturas forzadas (`arena.aperturas(k)`, todas las secuencias de `k` columnas iniciales), y la cantidad `k` se fijará en C08. Los agentes con azar usan semillas explícitas.
- **Métricas:** victorias, derrotas y empates desde el punto de vista del agente evaluado; tasa de victoria con intervalo de Wilson al 95 %; cantidad de jugadas; tiempo medio y máximo por decisión (las jugadas forzadas no se cronometran). Más adelante se agregarán nodos expandidos.
- **Formato de cada entrada:** ID · fecha · autor · tarea · pregunta o hipótesis · configuración · resultados · tiempo · conclusión · próximo paso.

---

### CNT-001 — Agente aleatorio contra Stratego oficial (baseline, P06)

- **Fecha / autor:** 2026-11-24 · Juan Etchebarne (con Claude Code)
- **Tarea:** P06
- **Pregunta:** ¿qué resultado obtiene un agente sin estrategia contra el rival oficial? Es el piso con el que se compararán todas las variantes.
- **Configuración:** `AgenteAleatorio(semilla)` como jugador 1 contra `load_enemy_agent()`. Semillas 0–99, sin apertura. Commit `5fd8882`.
  - Comando: `poetry run python experimentos_base.py CNT-001 --partidas 100`
- **Resultados:** 14 victorias, 86 derrotas, 0 empates. Tasa de victoria 0,14 (IC 95 %: 0,085–0,221). Las partidas duran 11,6 jugadas en promedio.
- **Tiempo:** 79,8 s para 100 partidas; Stratego insume casi todo.
- **Conclusión:** el agente aleatorio gana el 14 % de las partidas contra el Stratego oficial y pierde rápido. Cualquier agente propuesto debe superar claramente esa cifra.
- **Próximo paso:** usar este valor como referencia en C09–C11.

### CNT-002 — Número de jugador de Stratego según su constructor (C01)

- **Fecha / autor:** 2026-11-24 · Juan Etchebarne (con Claude Code)
- **Tarea:** C01
- **Hipótesis:** `Stratego(a, d)` toma `(a % 2) + 1` como su número de jugador. Por eso el oficial, `Stratego(2, 4)` jugando como jugador 2, busca y evalúa como si fuera el jugador 1. Si es así, debería jugar peor que cuando su número interno coincide con su turno real.
- **Configuración:** 4 variantes, combinando argumento 1 o 2 con turno de jugador 1 o 2, a profundidad 4. Rival `AgenteAleatorio(semilla)`, semillas 0–99 por variante, sin apertura. Commit `5fd8882`.
  - Comando: `poetry run python experimentos_base.py CNT-002 --partidas 100`
  - Una sonda previa de 40 partidas por variante, en el scratchpad y sin registro crudo, mostró la misma tendencia.
- **Resultados** (desde el punto de vista de Stratego):

  | Variante | ¿Número interno = turno? | Victorias / 100 | IC 95 % |
  |---|---|---:|---|
  | `Stratego(2,4)` como jugador 1 | sí | 100 | 0,963–1,000 |
  | `Stratego(1,4)` como jugador 2 | sí | 94 | 0,875–0,972 |
  | `Stratego(1,4)` como jugador 1 | no | 86 | 0,779–0,915 |
  | `Stratego(2,4)` como jugador 2 (**oficial**) | no | 86 | 0,779–0,915 |

- **Tiempo:** 276,9 s; alrededor de 0,13 s por decisión de Stratego a profundidad 4.
- **Conclusión:** se confirma la hipótesis. Con el número que no coincide, Stratego gana menos contra el mismo rival aleatorio: 86 contra 100 como jugador 1 (intervalos disjuntos) y 86 contra 94 como jugador 2 (intervalos solapados, diferencia menos firme). El Stratego oficial es la variante "no coincidente". Igual gana el 86 % de las partidas contra un agente aleatorio. Las 86 victorias del oficial coinciden exactamente con CNT-001, que usa las mismas semillas, y eso valida la consistencia del arena.
- **Decisión:** se evalúa contra el Stratego oficial sin modificarlo, que es la opción A elegida por el equipo. El hallazgo se reportará en el informe como nota de advertencia.
- **Próximo paso:** consultar a los docentes si la asignación de jugador es intencional (pendiente).

#### Actualización de CNT-002 (2026-11-24)

Juan Etchebarne confirmó que la asignación de jugador del Stratego oficial es **intencional**. Ya no queda nada pendiente sobre este punto. Las conclusiones de CNT-002 se mantienen: el rival oficial es la configuración "no coincidente" y se lo usa sin modificaciones.

#### Nota sobre el commit registrado en CNT-002 (2026-11-24)

El `config.json` de CNT-002 indica `5fd8882-sucio`. El código era el del commit `5fd8882` sin cambios. La marca se debió a que los resultados de CNT-001 todavía no estaban commiteados. Desde el commit que agrega esta nota, `registro.commit_actual()` ignora la carpeta `experimentos/` al decidir si el árbol tiene cambios.
