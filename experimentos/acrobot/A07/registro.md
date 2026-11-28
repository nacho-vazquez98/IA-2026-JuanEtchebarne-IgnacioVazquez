# A07 — Búsqueda de hiperparámetros de Q-Learning

## ACR-014 a ACR-022 — Piloto factorial en la grilla angular

- **Fecha y autor** — 28/11/2026, Codex en Codex Cloud.
- **Hipótesis** — La tasa de aprendizaje α, el horizonte fijado por γ y
  la exploración al final del entrenamiento pueden cambiar el retorno
  greedy aun con la misma grilla. Un diseño factorial permite comparar
  cada nivel de ε final con los mismos α y γ.
- **Código y entorno** — Commit `bbdb86ebf39a7baf54539f4f8d0a82bfc022e008`,
  Gymnasium 1.1.1, NumPy 1.26.4 y dependencias de `Acrobot/poetry.lock`.
  Las funciones de Acrobot que se usaron y su archivo de bloqueo coinciden
  con el `main` de partida de esta rama (`6350654`).
- **Entrenamiento** — Acrobot-v1 sin renderizado, grilla angular, tope de
  700 interacciones por episodio y 60 episodios por configuración.
  Semillas de entorno 10.000–10.059 y semilla de agente 310.001. El
  episodio de índice `i` desde cero usa
  `ε(i) = 1 + (ε_final − 1) × i / (N − 1)`, con `N = 60`.
- **Validación** — Evaluación greedy en un proceso nuevo, con
  semillas de entorno 100.000–100.015 y semilla 300.000 para el desempate.
  La métrica principal es el retorno medio sin descuento y un valor más
  alto indica un mejor resultado. La [política aleatoria](../ACR-003/)
  obtuvo −693,94 en esas mismas 16 semillas.

| Corrida | α | γ | ε final | Retorno greedy medio | Éxito greedy | Entrenamiento (s) | Validación (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [ACR-014](../ACR-014/) · Referencia A06 | 0,50 | 0,990 | 0,05 | −432,56 | 87,50 % | 4,25 | 0,65 |
| [ACR-015](../ACR-015/) | 0,25 | 0,970 | 0,02 | −448,06 | 81,25 % | 3,59 | 0,76 |
| [ACR-016](../ACR-016/) | 0,25 | 0,970 | 0,20 | −442,94 | 87,50 % | 3,63 | 0,75 |
| [ACR-017](../ACR-017/) | 0,25 | 0,995 | 0,02 | −641,75 | 37,50 % | 3,53 | 1,01 |
| [ACR-018](../ACR-018/) | 0,25 | 0,995 | 0,20 | −329,88 | 93,75 % | 3,41 | 0,54 |
| [ACR-019](../ACR-019/) | 0,75 | 0,970 | 0,02 | −488,94 | 62,50 % | 3,55 | 0,80 |
| [ACR-020](../ACR-020/) | 0,75 | 0,970 | 0,20 | −343,75 | 100,00 % | 3,80 | 0,53 |
| [ACR-021](../ACR-021/) | 0,75 | 0,995 | 0,02 | −700,00 | 0,00 % | 3,62 | 1,08 |
| [ACR-022](../ACR-022/) | 0,75 | 0,995 | 0,20 | −549,19 | 62,50 % | 3,68 | 0,89 |

El piloto duró 51,78 segundos de reloj. Se comprobaron las huellas
de los nueve modelos evaluados y se recalculó el retorno desde los CSV.
El [resumen](resumen_piloto.json) y la [tabla de comparación](comparacion_piloto.csv)
conservan los tiempos, el retorno descontado y las diferencias frente a
las referencias. Las etiquetas `referencia` y `factorial-01` a `factorial-08`
corresponden, en ese orden, a `ACR-014` a `ACR-022`.

- **Resultado** — ACR-018 y ACR-020 superaron a la referencia de Q-Learning
  por 102,69 y 88,81 puntos respectivamente. ε final de 0,20 dio mayor
  retorno que 0,02 en los cuatro pares con los mismos α y γ. ACR-021
  truncó los 16 episodios con un retorno 6,06 puntos menor que el de la
  referencia aleatoria.
- **Decisión** — Replicar ACR-018 y ACR-020 y ensayar una combinación
  intermedia de α y γ con ε final de 0,20. El horizonte abreviado y la
  única semilla de entrenamiento mantienen abierta la selección de
  hiperparámetros.

## Ronda exploratoria con tres semillas

Queda pendiente hasta que se integre el
[PR #12 de A06](https://github.com/nacho-vazquez98/IA-2026-JuanEtchebarne-IgnacioVazquez/pull/12).
Las cuatro configuraciones se prueban en la grilla angular con las mismas
semillas en cada fase.

| Configuración | α | γ | ε final |
| --- | ---: | ---: | ---: |
| Referencia A06 | 0,50 | 0,990 | 0,05 |
| ACR-018 | 0,25 | 0,995 | 0,20 |
| ACR-020 | 0,75 | 0,970 | 0,20 |
| Intermedia | 0,50 | 0,985 | 0,20 |

- **Entrenamiento** — 500 episodios con ε inicial de 1 y descenso lineal
  hasta el ε final de cada combinación. En cada réplica se empareja la
  semilla inicial de entorno con la del agente. Los tres pares son
  10.000/310.001, 20.000/310.002 y 30.000/310.003.
- **Validación** — 100 episodios greedy por réplica en las semillas
  100.000–100.099, con la semilla de desempate del protocolo y ACR-003
  en el mismo subconjunto. Se registra el retorno medio sin descuento,
  la diferencia frente a la referencia en cada réplica, la desviación
  estándar muestral entre réplicas y la tasa de éxito.
- **Presupuesto** — 12 corridas, con un máximo de 4.200.000 interacciones
  de entrenamiento y 840.000 de validación. El tiempo secuencial
  estimado es de 8–15 minutos.
- **Confirmación formal** — Los candidatos de la ronda exploratoria se
  vuelven a contrastar en las grillas angular y directa uniforme con
  10.000 episodios de entrenamiento y 1.000 de validación. Se reutilizan
  los resultados de A06 para controles idénticos. Las semillas finales
  se mantienen reservadas para después de la selección.

Desde `Acrobot/` con el entorno Poetry del proyecto, el lanzador muestra
los comandos exactos de cada fase sin iniciar entrenamiento.

```sh
poetry run python -B ../experimentos/acrobot/A07/ejecutar.py piloto --plan
poetry run python -B ../experimentos/acrobot/A07/ejecutar.py ronda-1 --plan
```

Para ejecutar una fase se indica `--salida` con una carpeta nueva. La
`ronda-1` se ejecuta una vez integrada A06 en `main` y actualizada la rama.

```sh
poetry run python -B ../experimentos/acrobot/A07/ejecutar.py piloto --salida ../.CODEX/a07-piloto-reproducido
poetry run python -B ../experimentos/acrobot/A07/ejecutar.py ronda-1 --salida ../.CODEX/a07-ronda-1
```
