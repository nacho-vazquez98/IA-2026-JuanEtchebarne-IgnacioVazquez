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

## ACR-004 a ACR-008 — Comparación de grillas

- **Fecha y autor** — 2026-11-27, Codex en Codex Cloud.
- **Tarea** — A06. Completar tres réplicas por grilla junto con ACR-002 y
  comparar contra ACR-003. Se contrasta si representar los ángulos y refinar
  los intervalos de velocidad alrededor de cero mejora el retorno manteniendo
  el tamaño de la tabla.
- **Configuración** — Código `2d2aa4f` para las cinco corridas nuevas y
  `82ebb03` para ACR-002. Los archivos del agente, las grillas y el lock
  coinciden en ambos commits. Se mantuvieron α = 0,5, γ = 0,99, ε lineal de
  1 a 0,05 y 700 pasos máximos por episodio. Cada réplica entrenó 10.000
  episodios y se validó con ε = 0 en las mismas 1.000 semillas que ACR-003.
  Las semillas de agente correspondientes a las de entorno 10.000, 20.000
  y 30.000 fueron 310.001, 310.002 y 310.003.
- **Resultados por réplica** — Cada fila refiere a una única tabla Q
  guardada y a su evaluación greedy en un proceso independiente.

| Corrida | Grilla | Semilla de entrenamiento | Retorno de validación | Éxito | Pasos de entrenamiento | Entrenamiento (s) | Validación (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [ACR-002](ACR-002/) | Angular | 10.000 | −437,78 | 94,1 % | 5.355.582 | 503,3 | 42,4 |
| [ACR-004](ACR-004/) | Angular | 20.000 | −286,19 | 100,0 % | 5.322.403 | 936,3 | 28,2 |
| [ACR-005](ACR-005/) | Angular | 30.000 | −258,23 | 98,9 % | 5.341.121 | 944,2 | 27,0 |
| [ACR-006](ACR-006/) | Directa | 10.000 | −268,20 | 98,7 % | 6.386.171 | 859,9 | 46,6 |
| [ACR-007](ACR-007/) | Directa | 20.000 | −484,78 | 88,1 % | 6.397.993 | 857,3 | 87,6 |
| [ACR-008](ACR-008/) | Directa | 30.000 | −260,75 | 100,0 % | 6.369.273 | 650,7 | 27,8 |

Las métricas agregadas promedian las réplicas de cada grilla. El retorno sin
descuento incluye la desviación estándar muestral entre réplicas.

| Política | Retorno sin descuento | Retorno descontado | Éxito | Pasos entre éxitos | Máximo Q inicial | Millones de pasos de entrenamiento |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Angular | −327,40 ± 96,61 | −93,78 | 97,7 % | 321,28 | −57,17 | 5,34 |
| Directa | −337,91 ± 127,25 | −93,37 | 95,6 % | 327,32 | −76,34 | 6,38 |
| Aleatoria (ACR-003) | −691,55 | −99,87 | 6,3 % | 566,90 | — | — |

- **Diferencias emparejadas** — Retorno de la directa menos retorno de la
  angular por semilla de entrenamiento. 10.000 → 169,58, 20.000 → −198,58, 30.000 → −2,52.
- **Costo** — Ambas grillas usan 9.216 estados y 27.648 celdas Q. La tabla
  densa ocupa 221.184 bytes (216 KiB). La media de pasos de entrenamiento
  angular fue 5.339.702 frente a 6.384.479 para
  la directa. Las cinco corridas nuevas tomaron 26 min 29 s de reloj
  con hasta cuatro procesos concurrentes. ACR-002 corrió sola. Para comparar
  costo de simulación se usan los pasos y se conservan por separado
  [los tiempos por fase](A06/tiempos_proceso.csv).
- **Conclusión** — La grilla angular obtuvo el mayor retorno promedio por
  10,51 puntos y quedó por delante en 2 de los tres
  pares de semillas. La dispersión entre réplicas y el tamaño de la muestra
  se deben tener en cuenta al elegir. Con el retorno descontado, la directa
  obtuvo una media 0,41 puntos mayor. El descuento reduce el peso de las
  demoras tardías y aquí cambia el orden entre variantes. La comparación
  mide el efecto conjunto
  de los bordes de velocidad y la representación angular. Ambas variantes
  se conservan para A07, donde se probará si cambia el orden al ajustar
  los hiperparámetros. El conjunto final queda reservado para la selección.
- **Evidencia** — [Comparación visual](A06/comparacion.png),
  [tabla por réplica](A06/replicas.csv) y [agregados](A06/resumen.json).
  Desde `Acrobot/`, el resumen se puede reconstruir con
  `poetry run python comparar_grillas.py --salida /ruta/a/una/carpeta-nueva`.

Para reproducir una réplica, se sustituyen la grilla y las semillas según su
fila y se usa una carpeta de salida nueva:

```sh
salida="$(mktemp -d)"
poetry run python experimentos_qlearning.py entrenar --grilla angular --semilla 20000 --semilla-agente 310002 --salida "$salida/entrenamiento"
poetry run python experimentos_qlearning.py evaluar --conjunto validacion --modelo "$salida/entrenamiento/modelo.npz" --salida "$salida/validacion"
```
