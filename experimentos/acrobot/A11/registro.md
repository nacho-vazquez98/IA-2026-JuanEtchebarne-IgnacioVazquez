# A11 — Experimentación con Dyna-Q

## ACR-023 a ACR-028 — Piloto de planificación

**Fecha y autor** — 27/11/2026, Codex en Codex Cloud. Dyna-Q y las
funciones compartidas de Acrobot se ejecutaron desde
`bbdb86ebf39a7baf54539f4f8d0a82bfc022e008`.

**Hipótesis** — Reutilizar transiciones puede acelerar el aprendizaje por
interacción real y aumentar el costo por paso. El piloto prueba que sea
posible medir ambos efectos con puntos de control y estimar el costo de la
primera ronda.

**Configuración** — Acrobot-v1 sin renderizado y con un máximo de 700 pasos
por episodio. Grillas angular y directa uniforme, con 0, 5 y 15
actualizaciones simuladas por paso real. Cada caso usó α = 0,5, γ = 0,99,
ε lineal de 1 a 0,05 en 12 episodios, semillas de entrenamiento de entorno
10.000 a 10.011 y semilla de agente 310.001. Tras los episodios 6 y 12
se evaluó la tabla Q guardada en un entorno independiente, con ε = 0,
semilla de desempate 300.000 y las cuatro semillas de validación
100.000–100.003.

| Corrida | Grilla | Pasos simulados por paso real | Retorno greedy, episodio 6 | Retorno greedy, episodio 12 | Éxito greedy, episodio 12 | Pasos reales acumulados | Actualizaciones simuladas acumuladas | Tiempo de entrenamiento (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [ACR-023](../ACR-023/) | Angular | 0 | −628,75 | −374,25 | 100 % | 8.020 | 0 | 0,774 |
| [ACR-024](../ACR-024/) | Angular | 5 | −683,00 | −543,75 | 50 % | 8.323 | 41.615 | 1,168 |
| [ACR-025](../ACR-025/) | Angular | 15 | −461,00 | −588,25 | 50 % | 8.372 | 125.580 | 1,787 |
| [ACR-026](../ACR-026/) | Directa uniforme | 0 | −536,00 | −334,75 | 100 % | 8.014 | 0 | 0,815 |
| [ACR-027](../ACR-027/) | Directa uniforme | 5 | −494,00 | −700,00 | 0 % | 7.680 | 38.400 | 1,104 |
| [ACR-028](../ACR-028/) | Directa uniforme | 15 | −700,00 | −276,00 | 100 % | 7.972 | 119.580 | 1,676 |

**Resultado** — A los 12 episodios, el costo de entrenamiento por paso
real fue de 1,41–1,45 veces el del control con cinco actualizaciones
simuladas, y de 2,07–2,21 veces con quince. El retorno cambió entre puntos
de control y grillas. Por ejemplo, directa con quince actualizaciones
pasó de cuatro truncamientos en el primer control a cuatro éxitos en el
segundo. Una semilla de entrenamiento y cuatro episodios de validación
por punto de control son insuficientes para elegir una cantidad de pasos
de planificación.

**Verificación** — Cada punto de control conservó su NPZ y los resultados
por episodio. En la grilla angular con cinco pasos simulados, la
comparación con una corrida continua reprodujo la tabla Q, el retorno, los
pasos y las banderas de todos los episodios. La verificación adicional
queda registrada en el [resumen del piloto](resumen_piloto.json).

**Decisión** — Empezar el estudio con la grilla angular y tres réplicas
emparejadas para estimar la dispersión del efecto de la planificación.
La grilla directa uniforme queda disponible para comprobar si los
resultados se mantienen con otra representación.

### Reproducción del piloto

Con Dyna-Q de A10 disponible, desde `Acrobot/`, usar una carpeta nueva.
El script conserva el procedimiento del piloto y crea subcarpetas por
grilla, cantidad de pasos simulados y punto de control. Los datos
archivados en ACR-023–028 registran el commit original y la huella de cada
modelo.

```sh
poetry run python -B ../experimentos/acrobot/A11/reproducir_piloto.py ../.CODEX/piloto-a11-repeticion
```

## Primera ronda exploratoria — Pendiente de A10

**Hipótesis** — Con el mismo presupuesto de episodios, un número pequeño de
pasos de planificación puede mejorar el retorno greedy. Las mediciones de
interacciones reales, simulaciones y reloj mostrarán el costo de esa
mejora.

**Diseño** — Grilla angular, α = 0,5, γ = 0,99 y decaimiento lineal de
ε = 1 a ε = 0,05 por episodio. Se prueban 0, 5 y 15 pasos de planificación
con las mismas tres parejas de semillas de entorno y agente, 10.000/310.001,
20.000/310.002 y 30.000/310.003. Cada réplica entrena 500 episodios y evalúa
el modelo guardado en 100 episodios greedy, con semillas de entorno
100.000–100.099 y semilla de desempate 300.000. Las semillas de evaluación
final se mantienen reservadas.

**Presupuesto** — Nueve corridas, con hasta 3,15 millones de interacciones
de entrenamiento, 21 millones de actualizaciones simuladas y 630.000 pasos
de validación. El piloto estima alrededor de ocho minutos de entrenamiento
secuencial, antes de validar y escribir resultados. Esta ronda exploratoria
usa un horizonte de ε propio de 500 episodios. La comparación final
requiere un horizonte común para los métodos que se comparen.

**Criterio de análisis** — Medir retorno sin descuento, diferencias
emparejadas frente a cero pasos de planificación, dispersión entre
réplicas, tasa de éxito y segundos por millón de interacciones reales.
Conservar tiempos de cada fase, conteos de actualizaciones y resultados por
episodio para elegir la siguiente prueba. Los resultados de esta primera
ronda determinarán qué niveles de planificación, grillas o hiperparámetros
se probarán a continuación.

### Ejecución de la primera ronda

Desde `Acrobot/`, la opción `--plan` muestra la matriz y el presupuesto
sin entrenar. El comando con `--salida` requiere que se haya integrado el
PR #13. Cada réplica conserva el entrenamiento, la validación y la huella
del modelo. El `resumen.json` de la ronda se escribe cuando finalizan las
nueve réplicas.

```sh
poetry run python -B experimentos_dyna_q.py --plan
poetry run python -B experimentos_dyna_q.py --salida ../experimentos/acrobot/A11/ronda-1
```
