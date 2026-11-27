# Registro de experimentos de Acrobot

El [protocolo de Acrobot](protocolo.md) define las métricas, semillas y
presupuestos por fase. Los resultados crudos están en las carpetas de cada ID.

## ACR-001 — Verificación de entrenamiento, persistencia y evaluación

- **Fecha y autor** — 2026-11-26, Codex en Codex Cloud.
- **Tarea** — A05. Verificar que un modelo entrenado se cargue en otro proceso
  y que el evaluador calcule todas las métricas a partir de las mismas
  trayectorias, tanto con el modelo como con una política aleatoria.
- **Configuración** — Código `275dd12`, grilla angular, α = 0,5 y γ = 0,99
  para Q-Learning. Entrenamiento de 20 episodios con ε lineal de 1 a 0,05,
  semillas de entorno 10.000 a 10.019 y semilla del agente 310.001. Cada
  política se evaluó en las mismas 10 semillas de entorno (100.000 a 100.009)
  y con semilla de política 300.000. El descuento para evaluación fue 0,99
  y el límite, 700 pasos.
- **Evidencia** — [Entrenamiento](ACR-001/entrenamiento/resumen.json),
  [evaluación greedy](ACR-001/validacion/resumen.json) y
  [evaluación aleatoria](ACR-001/aleatorio/resumen.json). El entrenamiento
  duró 1,29 s y produjo una tabla con 2.868 celdas distintas de cero.

| Política de evaluación | Retorno medio | Retorno descontado medio | Éxitos | Pasos medios entre éxitos | Máximo Q inicial medio | Tiempo |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Greedy | −489,2 | −98,52 | 8/10 | 437,5 | −6,16 | 0,51 s |
| Aleatoria | −700,0 | −99,91 | 0/10 | — | — | 0,41 s |

- **Conclusión** — El ciclo completo funcionó y los datos quedaron
  registrados por episodio. La muestra es una prueba de desarrollo.
  La evaluación formal y la referencia aleatoria de P06 usan 1.000 episodios.

## ACR-002 — Primera corrida formal de Q-Learning

- **Fecha y autor** — 2026-11-26, Codex en Codex Cloud.
- **Tarea** — A05. Obtener una primera medición de rendimiento y costo
  del ciclo formal con la grilla angular.
- **Configuración** — Código `82ebb03`, α = 0,5, γ = 0,99, ε lineal de 1 a
  0,05, Acrobot-v1 con 700 pasos como máximo. Entrenamiento de 10.000
  episodios con semillas de entorno 10.000 a 19.999 y semilla de agente
  310.001. Validación greedy en un proceso nuevo con semillas de entorno
  100.000 a 100.999, semilla de política 300.000 y γ de evaluación = 0,99.
- **Entrenamiento** — 503,33 s, retorno promedio −534,94 y 6.138 éxitos de
  10.000. La tabla ocupa 221.184 bytes y terminó con 8.865 valores distintos
  de cero. Los primeros 1.000 episodios tuvieron retorno medio −687,98 y
  85 éxitos. Los últimos 1.000 tuvieron retorno medio −348,76 y 955 éxitos,
  con un ε más bajo.
- **Validación greedy** — 42,39 s, retorno promedio −437,778 (desviación
  estándar por episodio de 117,77), retorno descontado promedio −97,95,
  941 éxitos de 1.000 y 422,34 pasos en promedio entre éxitos. El máximo Q
  inicial medio fue −55,36, 42,59 puntos por encima del retorno descontado
  observado con el mismo γ.
- **Evidencia y verificación** — [Configuración de entrenamiento](ACR-002/entrenamiento/config.json),
  [modelo](ACR-002/entrenamiento/modelo.npz),
  [resumen de validación](ACR-002/validacion/resumen.json) y
  [gráfico de utilidad](ACR-002/validacion/utilidad.png). Se recalcularon
  las métricas a partir de los registros por episodio, se verificó el hash
  del modelo cargado y se comprobaron los valores Q iniciales de las
  1.000 semillas de validación.
- **Conclusión** — El ciclo formal completo tomó aproximadamente 9 min 6 s
  de simulación y actualización. La grilla angular tiene una réplica formal.
  Para comparar grillas en A06, falta usar las dos variantes y las réplicas
  previstas en el protocolo.

## ACR-003 — Referencia aleatoria en validación

- **Fecha y autor** — 2026-11-26, Codex en Codex Cloud.
- **Tarea** — P06. Medir una política uniforme sobre las acciones
  disponibles con el mismo conjunto de validación de ACR-002.
- **Configuración** — Código `82ebb03`, Acrobot-v1 y 700 pasos máximos
  por episodio. 1.000 episodios con semillas de entorno 100.000 a 100.999
  y semilla de política 300.000. γ de evaluación = 0,99.
- **Resultado** — 42,22 s, retorno promedio −691,552 (desviación estándar
  por episodio de 42,18), retorno descontado promedio −99,87, 63 éxitos
  de 1.000 y 566,90 pasos en promedio entre éxitos. Se verificaron las
  métricas desde el CSV y la coincidencia de semillas con ACR-002.
- **Evidencia** — [Configuración](ACR-003/validacion/config.json),
  [resumen](ACR-003/validacion/resumen.json) y [gráfico](ACR-003/validacion/utilidad.png).
- **Comparación** — ACR-002 obtuvo 253,77 puntos más de retorno sin
  descuento y 87,8 puntos porcentuales más de éxito en las mismas semillas.
  La diferencia en retorno descontado fue de 1,92 puntos. Queda reservada
  la evaluación final para después de seleccionar las configuraciones.

## ACR-004 a ACR-008 — Comparación de grillas, iteración 1

- **Fecha y autor** — 2026-11-27, Codex en Codex Cloud.
- **Tarea e hipótesis** — A06, primera iteración. La grilla angular propuesta
  en A02 elimina combinaciones de seno y coseno incompatibles con el círculo
  unitario y refina los bordes de velocidad cerca de cero. Se esperaba que
  esa resolución mejorara el aprendizaje y, posiblemente, el retorno greedy
  al mantener fijo el tamaño nominal de la tabla.
- **Configuración** — Código `2d2aa4f` para las cinco corridas nuevas y
  `82ebb03` para ACR-002. Los archivos del agente, las grillas y el lock
  coinciden en ambos commits. Se mantuvieron α = 0,5, γ = 0,99, ε lineal de
  1 a 0,05 y 700 pasos máximos por episodio. Cada réplica entrenó 10.000
  episodios y se validó con ε = 0 en las mismas 1.000 semillas que ACR-003.
  Las semillas de agente correspondientes a las de entorno 10.000, 20.000
  y 30.000 fueron 310.001, 310.002 y 310.003.

| Corrida | Grilla | Semilla | Éxito en entrenamiento | Éxitos en los últimos 1.000 | Retorno greedy | Éxito greedy | Pasos de entrenamiento |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [ACR-002](ACR-002/) | Angular | 10.000 | 61,38 % | 955 | −437,78 | 94,1 % | 5.355.582 |
| [ACR-004](ACR-004/) | Angular | 20.000 | 61,55 % | 972 | −286,19 | 100,0 % | 5.322.403 |
| [ACR-005](ACR-005/) | Angular | 30.000 | 61,02 % | 953 | −258,23 | 98,9 % | 5.341.121 |
| [ACR-006](ACR-006/) | Directa | 10.000 | 27,94 % | 659 | −268,20 | 98,7 % | 6.386.171 |
| [ACR-007](ACR-007/) | Directa | 20.000 | 27,49 % | 660 | −484,78 | 88,1 % | 6.397.993 |
| [ACR-008](ACR-008/) | Directa | 30.000 | 28,40 % | 674 | −260,75 | 100,0 % | 6.369.273 |

Las métricas agregadas dan el mismo peso a cada réplica. Los pasos por episodio
exitoso se calculan primero dentro de cada réplica y luego se promedian.
El retorno sin descuento incluye la desviación estándar muestral entre réplicas.

| Política | Retorno sin descuento | Retorno descontado | Éxito greedy | Pasos por episodio exitoso | Máximo Q inicial | Millones de pasos de entrenamiento |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Angular | −327,40 ± 96,61 | −93,78 | 97,7 % | 321,28 | −57,17 | 5,34 |
| Directa | −337,91 ± 127,25 | −93,37 | 95,6 % | 327,32 | −76,34 | 6,38 |
| Aleatoria (ACR-003) | −691,55 | −99,87 | 6,3 % | 566,90 | — | — |

- **Entrenamiento** — Con el mismo ε decreciente, la angular obtuvo 61,32 %
  de éxito en promedio y 960 éxitos en los últimos 1.000 episodios por réplica.
  La directa obtuvo 27,94 % y 664,33 éxitos, respectivamente. La angular
  tuvo 16,4 % menos interacciones en los 10.000 episodios porque alcanzó
  el objetivo antes del límite con mayor frecuencia. El panel de entrenamiento
  del gráfico muestra tasas desde cero.
- **Validación emparejada** — Las diferencias de retorno angular menos
  directa fueron −169,58, +198,58 y +2,52 para las semillas 10.000, 20.000 y
  30.000. La media de 10,51 puntos queda muy por debajo de la desviación
  muestral de 184,21 y del error estándar de 106,35 (tres pares). Con
  descuento, la directa queda 0,41 por encima y el error estándar es 3,79.
  La muestra es insuficiente para distinguir las políticas greedy.
- **Uso efectivo de la tabla** — Ambas grillas reservan 9.216 estados y
  27.648 celdas Q. La tabla densa ocupa 221.184 bytes (216 KiB). Al final
  quedaron, en promedio, 8.789 celdas Q con valor distinto de cero en la
  angular y 2.386 en la directa (3,68 veces más en la angular). Los modelos
  comprimidos promediaron 68,8 kB y 20,1 kB, respectivamente. Las celdas
  con valor distinto de cero son un indicador indirecto del uso de la tabla.
  Las combinaciones trigonométricas imposibles y los intervalos de velocidad
  más anchos de la grilla directa son explicaciones plausibles. Para la
  segunda se necesitarían observaciones por estado para medir la ocupación.
- **Costo y tiempos** — Las cinco corridas nuevas tomaron 26 min 29 s de
  reloj con hasta cuatro procesos concurrentes. ACR-002 corrió sola. En las
  cinco corridas nuevas se midió cada fase con `time -p` de Bash. Los
  [tiempos por fase](A06/tiempos_proceso.csv) incluyen el proceso completo
  y registran `real`, `user` y `sys`. El campo `segundos` de los resúmenes
  se mide dentro del programa y empieza con el bucle de episodios.
- **Siguiente iteración de A06** — Mantener la representación directa y
  sus 6 intervalos por velocidad, con bordes en las fracciones
  `[-1, -0.5, -0.125, 0, 0.125, 0.5, 1]` de cada velocidad máxima.
  La hipótesis es que estos bordes aumentarán el uso de la tabla cerca de
  cero y mejorarán la tasa de éxito de entrenamiento frente a la directa
  uniforme. Compararlas con la misma representación, tamaño, parámetros y
  semillas separa el efecto de los bordes de velocidad. La validación
  greedy permitirá comprobar si ese efecto se traslada a la política. Ambas
  grillas iniciales se conservan como referencia y el conjunto final queda
  reservado para después de la selección.
- **Evidencia** — [Comparación visual](A06/comparacion.png),
  [tabla por réplica](A06/replicas.csv) y [agregados](A06/resumen.json).
  Desde `Acrobot/`, el resumen se puede reconstruir con
  `poetry run python comparar_grillas.py --salida /ruta/a/una/carpeta-nueva`.

En Codex Cloud se midió con Bash y el intérprete de la `.venv` de Poetry.
Para reproducir ACR-004 y sus dos mediciones de proceso:

```sh
salida="$(mktemp -d)"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLBACKEND=Agg
(time -p .venv/bin/python -B experimentos_qlearning.py entrenar --grilla angular --episodios 10000 --semilla 20000 --semilla-agente 310002 --alpha 0.5 --gamma 0.99 --epsilon-inicial 1 --epsilon-final 0.05 --salida "$salida/entrenamiento") 2> "$salida/entrenamiento.tiempo"
(time -p .venv/bin/python -B experimentos_qlearning.py evaluar --conjunto validacion --episodios 1000 --modelo "$salida/entrenamiento/modelo.npz" --salida "$salida/validacion") 2> "$salida/validacion.tiempo"
```

## ACR-009 y ACR-010 — Piloto de la segunda iteración de grillas

- **Fecha y autor** — 2026-11-27, Codex en Codex Cloud.
- **Tarea** — A06, iteración 2. Comprobar el ciclo de entrenamiento y evaluación
  de `directa_no_uniforme` y examinar si vale la pena ejecutar el protocolo formal.
- **Hipótesis** — Bordes de velocidad más finos cerca de cero pueden aumentar
  el uso efectivo de la tabla y mejorar el aprendizaje de la grilla directa.
  La variante conserva los senos y cosenos, sus intervalos y seis intervalos
  para cada velocidad. Los bordes de velocidad son las fracciones
  `[-1, -0.5, -0.125, 0, 0.125, 0.5, 1]` de su máximo declarado.
  La tabla tiene 27.648 celdas y ocupa 216 KiB en las dos variantes.
- **Configuración** — Commit `cdab502` para las dos corridas. 100 episodios
  de entrenamiento, semillas de entorno 10.000–10.099 y semilla del agente
  310.001, α = 0,5, γ = 0,99 y ε lineal de 1 a 0,05. Validación greedy en
  otro proceso con las mismas 30 semillas de entorno (100.000–100.029) y
  semilla de la política 300.000. Se usaron 700 pasos máximos por episodio.
  La referencia aleatoria es el subconjunto de ACR-003 con las mismas
  30 semillas de validación.

| Variante | Éxitos en entrenamiento | Celdas Q distintas de cero | Retorno greedy medio | Éxitos greedy | Pasos por episodio exitoso |
| --- | ---: | ---: | ---: | ---: | ---: |
| [ACR-009, directa uniforme](ACR-009/) | 30/100 | 1.505 | −698,90 | 1/30 | 668,00 |
| [ACR-010, directa no uniforme](ACR-010/) | 42/100 | 3.758 | −432,20 | 25/30 | 379,64 |
| [ACR-003, referencia aleatoria](ACR-003/) | — | — | −696,77 | 1/30 | 604,00 |

- **Tiempo** — La directa uniforme tardó 6,61 s en entrenar y 2,12 s en
  validar. La no uniforme tardó 5,81 s y 1,24 s, respectivamente.
- **Verificación** — Se reconstruyeron las métricas de ambos CSV y se
  comprobaron las semillas, la forma de las tablas Q y las huellas de los
  dos modelos. Las configuraciones de entrenamiento difieren solo en la
  grilla. Pasaron 21 pruebas, incluidas dos nuevas para forma, representación
  trigonométrica, repetibilidad, fronteras y saturación.
- **Conclusión** — La variante funcionó y produjo más celdas Q con valor
  distinto de cero y un mejor retorno en este piloto. La única semilla de
  entrenamiento y el horizonte reducido limitan la comparación. La prueba
  formal necesita tres réplicas de 10.000 episodios, emparejadas con
  ACR-006–ACR-008, y 1.000 episodios de validación por réplica. Con ese
  resultado se decidirá qué discretizaciones pasar a A07.

Para reproducir el piloto desde `Acrobot/`, con una carpeta de salida nueva
por variante:

```sh
salida="$(mktemp -d)"
for grilla in directa directa_no_uniforme; do
    poetry run python -B experimentos_qlearning.py entrenar --grilla "$grilla" --episodios 100 --semilla 10000 --semilla-agente 310001 --alpha 0.5 --gamma 0.99 --epsilon-inicial 1 --epsilon-final 0.05 --salida "$salida/$grilla/entrenamiento"
    poetry run python -B experimentos_qlearning.py evaluar --conjunto validacion --episodios 30 --modelo "$salida/$grilla/entrenamiento/modelo.npz" --salida "$salida/$grilla/validacion"
done
```
