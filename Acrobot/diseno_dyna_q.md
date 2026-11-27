# A09 — Diseño de Dyna‑Q para Acrobot

## Aprendizaje y planificación

Una transición del simulador aporta dos tipos de información. El agente puede
usar la recompensa y el estado siguiente para actualizar su tabla Q en ese
momento. También puede guardar lo que ocurrió, consultar ese modelo más
adelante y actualizar nuevamente Q con una transición simulada. En Dyna‑Q
ambas actualizaciones usan la misma regla tabular de Q-Learning. La
planificación intercala esas actualizaciones entre interacciones reales, de
modo que la política pueda aprovechar experiencias anteriores sin aumentar
las llamadas a `entorno.step`. [Sutton y Barto, 2.ª ed., §§ 8.1–8.2, pp. 159–164](https://devslem.github.io/assets/materials/Reinforcement%20Learning%20An%20Introduction%3B%202nd%20Edition.%202018.pdf)

Sea `n` la cantidad de actualizaciones simuladas por paso real. Con `n = 0`
solo queda la actualización directa de Q-Learning. Con `n > 0`, un paso
real produce `1 + n` actualizaciones sobre la misma tabla. El experimento
deberá medir si las actualizaciones adicionales mejoran la política y cuál
es su costo en tiempo y memoria.

## Modelo de transición

La primera versión usa **la última transición real para cada par estado y
acción observado**, como en el Dyna‑Q tabular de la sección 8.2. Las claves
son las tuplas de índices que ya devuelve `DiscretizadorAcrobot`. Cada
entrada almacena `(recompensa, estado_siguiente, terminado)` y se reemplaza
cuando se observa nuevamente ese par. El modelo permanece durante todo el
entrenamiento.

El modelo es disperso. Un mapa por estado contiene solo las acciones
observadas en ese estado, y una lista indexable almacena cada estado una
vez. Para cada actualización simulada se sortea uniformemente un estado
de esa lista y luego una de sus acciones registradas. El sorteo se hace con
reemplazo entre actualizaciones. Esto reproduce la selección en dos etapas
del libro sin recorrer todo el modelo en cada paso. La tabla Q existente
se mantiene densa y el modelo crece en proporción a los pares observados.

Dos observaciones continuas pueden caer en el mismo intervalo de la grilla
y llevar a destinos diferentes con la misma acción. Por eso, la última
transición es una aproximación. En A11 se puede medir la proporción de
revisitas en que cambia el destino, la recompensa o la terminación respecto
de la última observación. Si esa variación es frecuente y el rendimiento
empeora con la planificación, una alternativa es guardar frecuencias por
resultado y muestrear según la distribución empírica. Esa variante requiere
más memoria y hace más costoso cada muestreo.

## Integración con el agente de A04

En A10, una clase `AgenteDynaQ` puede heredar de
[`AgenteQLearning`](qlearning.py) y extender su método `actualizar`. El
`aprender_episodio` existente invoca ese método por cada transición real,
incluida la última, y conserva su flujo de observación, acciones y cierre.
La extensión aplicará la actualización heredada para las transiciones reales
y para las simuladas, mediante `super().actualizar(...)`. Las transiciones
simuladas solo actualizan Q. Las observadas en el entorno también alimentan
el modelo.

```text
al recibir una transición real (s, a, r, s_siguiente, terminado):
    actualizar Q mediante la regla de Q-Learning
    si pasos_planificacion es cero:
        finalizar este paso
    registrar (r, s_siguiente, terminado) en modelo[s][a]
    repetir pasos_planificacion veces:
        elegir un estado observado y una de sus acciones registradas
        recuperar la transición de ese par desde el modelo
        actualizar Q con esa transición mediante la misma regla
```

`pasos_planificacion` es un entero no negativo. El muestreo del modelo tendrá
un generador propio derivado de la semilla del agente. La selección
ε-greedy conserva el generador de A04. Con las mismas semillas y `n = 0`,
la tabla y las trayectorias deben coincidir con las de Q-Learning.

La bandera `terminated` se guarda porque determina el objetivo de Q. Si es
verdadera, el objetivo es la recompensa inmediata. En una transición
truncada solo por el límite de pasos, el objetivo conserva el término
descontado del estado siguiente. El entorno cierra el episodio si indica
alguna de las dos banderas. En el modelo se conserva como terminal cualquier
transición que haya terminado por objetivo, incluso si llegó al límite en
el mismo paso.

Para evaluar basta con la tabla Q, la grilla y los metadatos del modelo.
El NPZ de [A05](experimentos_qlearning.py) puede conservar su estructura,
identificando el algoritmo y `pasos_planificacion` en la configuración.
La evaluación usa la política greedy y deja la tabla fija. El modelo de
transiciones se mantiene en memoria durante el entrenamiento.

## Verificación prevista para A10

| Caso | Resultado esperado |
| --- | --- |
| Mismas semillas, grilla e hiperparámetros con `n = 0` | Q-Learning y Dyna‑Q producen las mismas tablas y resultados por episodio. El modelo queda vacío. |
| Un par registrado, `n = 2`, α = 0,5, γ = 0,9, recompensa −1 y máximo Q siguiente = 2 | Desde Q inicial 0, el objetivo es 0,8. Se obtiene 0,4 con experiencia real y 0,6 y 0,7 con las dos actualizaciones simuladas. |
| Se actualiza otro par real y se fuerza la selección del primer par durante planificación | La experiencia real modifica la entrada del par nuevo. La planificación modifica la entrada del primer par y mantiene fijo el modelo. |
| Dos transiciones reales diferentes para el mismo par | Se conserva la última transición. El muestreo devuelve solamente pares registrados. |
| Terminación, truncamiento y ambas banderas | Los objetivos real y simulado coinciden. El truncamiento solo conserva el valor del sucesor y la terminación usa la recompensa. |
| Entrenamiento breve y evaluación en otro proceso | Se carga el NPZ, se conserva la configuración de planificación y se evalúa sin actualizar Q. |

## Comparación en A11 y A12

La planificación cambia la cantidad de actualizaciones que se hacen por
interacción. Conviene comparar primero `n = 0` con valores positivos pequeños
bajo la misma grilla, semillas, α, γ y exploración. A11 definirá los valores y
el presupuesto según una prueba breve. Se registrarán el retorno de
validación, la tasa de éxito, las interacciones reales, las actualizaciones
simuladas y el tiempo de entrenamiento. Estas medidas permiten comparar la
eficiencia en muestras y el costo de cómputo por separado. La selección y la
evaluación final seguirán el [protocolo de Acrobot](../experimentos/acrobot/protocolo.md).
