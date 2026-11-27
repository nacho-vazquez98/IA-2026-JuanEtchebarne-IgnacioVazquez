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
