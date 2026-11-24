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

### CNT-003 — Costo y correlación de cada término de evaluación (C03)

- **Fecha / autor:** 2026-11-24 · Juan Etchebarne (con Claude Code)
- **Tarea:** C03
- **Pregunta:** el teórico pide que `Eval` (1) ordene bien los estados finales, (2) sea barata de calcular y (3) esté fuertemente correlacionada con las chances reales de ganar. El criterio 1 se verifica con pruebas automáticas (`test_heuristicas.py`). Este experimento mide el 2 y el 3 para cada término por separado, antes de combinarlos.
- **Hipótesis:** `lineas_de_3` (amenazas) debería ser el término más informativo, sobre todo hacia el final de la partida. `lineas_posibles`, el término del ejemplo de ta-te-ti, debería correlacionar positivamente pero con menos fuerza. `capturas` debería aportar porque las capturas pueden completar líneas.
- **Configuración:** 500 partidas `AgenteAleatorio(s)` contra `AgenteAleatorio(10000 + s)`, s = 0–499. Se toman todos los estados no finales después de cada jugada (6 987 posiciones), vistos desde el jugador 1, con el resultado codificado como +1 (victoria), 0 (empate) o −1 (derrota). Etapas por jugadas ya hechas: apertura 1–10, medio 11–20, final 21–42. Costo: promedio de 5 pasadas sobre las posiciones de las partidas 0–49. Commit `83a3f2f`.
  - Comando: `poetry run python experimentos_heuristicas.py CNT-003 --partidas 500`
- **Resultados** (en las partidas: 281 victorias del jugador 1, 219 del jugador 2, ningún empate):

  | Término | r de Pearson | Acierto de signo* | r en la apertura (4 637) | r en el medio (2 079) | r en el final (271) | Costo (µs) |
  |---|---:|---:|---:|---:|---:|---:|
  | `lineas_posibles` | 0,110 | 0,548 | 0,059 | 0,180 | 0,219 | 6,4 |
  | `lineas_de_2` | 0,100 | 0,557 | 0,070 | 0,136 | 0,189 | 8,0 |
  | `lineas_de_3` | 0,207 | 0,691 | 0,187 | 0,265 | 0,328 | 7,8 |
  | `centro` | 0,223 | 0,663 | 0,198 | 0,280 | 0,170 | 2,4 |
  | `capturas` | 0,112 | 0,587 | 0,143 | 0,110 | −0,002 | 17,4 |

  \* Proporción de posiciones con fᵢ ≠ 0 en partidas decididas donde el signo de fᵢ coincide con el ganador. La combinación con los cinco términos y peso 1 cuesta 43,1 µs por evaluación.
- **Tiempo:** 0,9 s.
- **Conclusión:**
  - Todos los términos correlacionan positivamente con ganar, pero ninguno con fuerza (r ≤ 0,23). Era esperable para un término aislado, y es un argumento para combinarlos.
  - `lineas_de_3` y `centro` son los más informativos. `lineas_de_3` mejora a medida que avanza la partida, como se suponía.
  - `centro` pierde peso en el final, y `capturas` aporta en la apertura pero nada en el final (r ≈ 0). Esto sugiere que pesos por etapa podrían ayudar, aunque por ahora no se agregan para mantener el modelo lineal del curso.
  - `lineas_posibles`, el término del curso, informa menos que `lineas_de_3`.
  - En costo, `capturas` es el término más caro (unas 7 veces `centro`), aunque sigue siendo barato en términos absolutos.
- **Limitaciones:** las posiciones vienen de partidas entre agentes aleatorios, que son cortas (14 jugadas en promedio), así que hay pocas posiciones de final. Una correlación de cada término por separado no mide cuánto aporta al combinarse con los demás ni el efecto de la búsqueda. Esto se medirá jugando contra Stratego en C09.
- **Próximo paso:** usar estos resultados para elegir las primeras combinaciones y pesos de C09: partir de `lineas_posibles` sola (la referencia del curso) y agregar `lineas_de_3` y `centro` con más peso. `capturas` se probará como término aparte.
