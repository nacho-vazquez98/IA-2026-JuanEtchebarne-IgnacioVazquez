# A09 — Diseño de Dyna-Q para Acrobot

## Aprendizaje y planificación

El **aprendizaje por refuerzo directo** actualiza Q con transiciones
del entorno. El **aprendizaje del modelo** registra esas transiciones
y la **planificación** consulta el modelo para actualizar Q nuevamente.
Ambas actualizaciones aplican la misma regla tabular de Q-Learning de un
paso. En Dyna-Q, la planificación en el espacio de estados elige pares
observados al azar, recupera su transición simulada y actualiza la tabla.
Así se aprovechan experiencias anteriores con el mismo número de llamadas
a `entorno.step`. [Sutton y Barto, 2.ª ed., §§ 8.1–8.2, pp. 159–166](https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/10094/Toc.pdf?dl=1)

Sea `n` la cantidad de actualizaciones simuladas por paso real. Con `n = 0`
solo queda la actualización directa de Q-Learning. Con `n > 0`, un paso
real produce `1 + n` actualizaciones sobre la misma tabla. El experimento
deberá medir si las actualizaciones adicionales mejoran la política y cuál
es su costo en tiempo y memoria.

## Modelo de transición

La primera versión usa **la última transición real para cada par estado y
acción observado**, como en el Dyna-Q tabular de la sección 8.2. Las claves
son las tuplas de índices que ya devuelve `DiscretizadorAcrobot`. Cada
entrada almacena `(recompensa, estado_siguiente, terminado)` y se reemplaza
cuando se observa nuevamente ese par. Es un **modelo de muestras** que
devuelve una sola transición por par. Un **modelo de distribución** asignaría
probabilidades a todos los resultados posibles. El modelo permanece durante
todo el entrenamiento cuando la planificación está habilitada.

El modelo es disperso. Un mapa por estado contiene solo las acciones
observadas en ese estado, y una lista indexable almacena cada estado una
vez. Para cada actualización simulada se sortea uniformemente un estado
de esa lista y luego una de sus acciones registradas. El sorteo se hace con
reemplazo entre actualizaciones. Esto reproduce la selección en dos etapas
del libro sin recorrer todo el modelo en cada paso. La tabla Q existente
se mantiene densa y el modelo crece en proporción a los pares observados.

En Gymnasium 1.1.1, Acrobot-v1 tiene `torque_noise_max = 0.0`. Dado el
estado continuo y la acción, el paso físico, la recompensa y la terminación
son deterministas. La semilla cambia el estado de partida. Al discretizar,
estados continuos que comparten una celda pueden conducir a destinos
diferentes con la misma acción. Esta pérdida de información hace que la
última transición sea una aproximación. Los intervalos más anchos de
velocidad de la grilla directa podrían aumentar esa variación. [Código de Acrobot-v1](https://github.com/Farama-Foundation/Gymnasium/blob/v1.1.1/gymnasium/envs/classic_control/acrobot.py)

En A11 se puede medir la proporción de revisitas en que cambia el destino,
la recompensa o la terminación respecto de la última observación. Si esa
variación es frecuente y el rendimiento empeora con la planificación, una
alternativa es guardar frecuencias por resultado. Las frecuencias forman
una distribución empírica de la que se puede extraer una muestra. Esa
variante requiere más memoria y hace más costoso cada muestreo.

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

`pasos_planificacion` es un entero no negativo. Con `n = 0` se omite el
registro del modelo para ahorrar memoria y tiempo. El algoritmo del § 8.2
registra la transición incluso en ese caso. La actualización directa se
mantiene y, con las mismas semillas explícitas, la tabla y las trayectorias
deben coincidir con las de Q-Learning.

La política ε-greedy conserva el generador creado por A04 con
`np.random.default_rng(semilla)`. Para `n > 0`, el modelo utiliza
`np.random.default_rng(np.random.SeedSequence(semilla).spawn(1)[0])`.
Planificar solo consume números del segundo generador. Con `semilla=None`
cada generador obtiene entropía al inicializarse. Las pruebas de equivalencia
y repetibilidad usan una semilla explícita.

Con truncamiento sin terminación, la entrada guarda `terminado=False` y el
objetivo de Q incluye `γ · max Q(siguiente_estado)`. Con terminación, incluso
si coincide con el límite de pasos, la entrada guarda `terminado=True` y
el objetivo es la recompensa. El límite de pasos es externo al simulador.
El bucle de A04 cierra el episodio si cualquiera de las dos banderas es
verdadera.

Para evaluar basta con la tabla Q, la grilla y los metadatos del modelo.
El NPZ de [A05](experimentos_qlearning.py) puede conservar su estructura,
identificando el algoritmo y `pasos_planificacion` en la configuración.
La evaluación usa la política greedy y deja la tabla fija. El modelo de
transiciones se mantiene en memoria durante el entrenamiento. El NPZ se
puede cargar para evaluar. Reanudar una corrida con el mismo modelo de
transición requeriría persistir también ese modelo y sus generadores.

## Verificación prevista para A10

| Caso | Resultado esperado |
| --- | --- |
| Mismas semillas, grilla e hiperparámetros con `n = 0` | Q-Learning y Dyna-Q producen las mismas tablas y resultados por episodio. El modelo queda vacío. |
| Un par registrado, `n = 2`, α = 0,5, γ = 0,9, recompensa −1 y estado siguiente distinto con máximo Q fijo en 2 | Desde Q inicial 0, el objetivo es 0,8. Se obtiene 0,4 con experiencia real y 0,6 y 0,7 con las dos actualizaciones simuladas. |
| Mismos α, γ, recompensa y `n = 2`, con estado siguiente igual al actual y Q de la acción actual en 2 (otras acciones en 0) | Q pasa por 1,4, 0,83 y 0,2885, porque cada actualización usa el máximo vigente del sucesor. |
| Misma semilla y Q fija, `n > 0`, tras consumir distinta cantidad de muestras del modelo | Las secuencias de decisiones ε-greedy coinciden. |
| Se actualiza otro par real y se fuerza la selección del primer par durante planificación | La experiencia real modifica la entrada del par nuevo. La planificación modifica la entrada del primer par y mantiene fijo el modelo. |
| Dos transiciones reales diferentes para el mismo par | Se conserva la última transición. El muestreo devuelve solamente pares registrados. |
| Terminación, truncamiento y ambas banderas | Con truncamiento sin terminación, se registra `terminado=False` y ambos objetivos incluyen el máximo Q descontado del sucesor. Con `terminado=True`, ambos objetivos usan la recompensa. |
| Entrenamiento breve y evaluación en otro proceso | Se carga el NPZ, se conserva la configuración de planificación y se evalúa sin actualizar Q. |

## Comparación en A11 y A12

Para aislar el efecto de la planificación, comparar primero `n = 0` con
valores positivos pequeños bajo la misma grilla, semillas, α, γ y
exploración. A11 definirá los valores y el presupuesto según una prueba breve.

Para medir la **velocidad de aprendizaje**, los CSV de entrenamiento permiten
graficar el retorno por episodio suavizado con una ventana común. También se
prevén evaluaciones greedy de copias de Q tras los episodios 500, 1.000,
2.000 y 5.000, en las mismas 100 semillas de validación (100.000–100.099)
y en un entorno independiente del entrenamiento. Así se puede localizar
cuándo aparece una mejora y observarla también por número acumulado de
interacciones reales. Las semillas finales siguen reservadas para la
evaluación posterior a la selección.

El registro incluirá retorno, éxito, dispersión entre réplicas, tiempo de
entrenamiento, tiempo de evaluación, interacciones reales y actualizaciones
de Q separadas por tipo. Con `T` pasos reales se esperan `T` actualizaciones
directas y `n × T` simuladas. Se reportará el total `(1 + n) × T` para
distinguir eficiencia de muestras de costo computacional.
[Protocolo de Acrobot](../experimentos/acrobot/protocolo.md)
