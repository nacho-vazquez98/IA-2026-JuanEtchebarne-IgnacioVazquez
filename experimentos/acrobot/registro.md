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
