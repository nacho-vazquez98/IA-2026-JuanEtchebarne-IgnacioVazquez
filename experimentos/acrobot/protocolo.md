# Protocolo experimental de Acrobot

## Entrenamiento y evaluación

- Acrobot-v1 se ejecuta sin renderizado y con 700 pasos como máximo por
  episodio, tanto para los agentes aprendidos como para la referencia aleatoria.
- La corrida formal de Q-Learning consta de 10.000 episodios de entrenamiento
  ε-greedy con ε decreciente y 1.000 episodios de evaluación greedy con ε = 0.
  El evaluador mantiene fija la tabla. Las pruebas con menos episodios sirven
  para verificar el ciclo y se identifican como pruebas de desarrollo.
- Para comparar una configuración en A06 y A07, se prevén tres entrenamientos
  independientes, con semillas iniciales de entorno 10.000, 20.000 y 30.000.
  Cada episodio usa la semilla inicial más el índice del episodio desde cero.
  Las semillas correspondientes del agente son 310.001, 310.002 y 310.003.
  Se informa el resultado de cada réplica y la dispersión entre réplicas.
- Cada política se mide en las mismas semillas de entorno. Validación usa
  100.000 a 100.999 para elegir configuraciones. Evaluación final usa 200.000 a
  200.999 y se reserva hasta después de la selección. El flujo aleatorio de
  la política de evaluación usa la semilla 300.000 para el desempate greedy
  y para las acciones del baseline.
- Cada entrenamiento formal tiene un máximo de 7 millones de pasos de
  simulación, y cada evaluación un máximo de 700.000. Se mide la duración de
  las dos fases y se usa la primera corrida formal para presupuestar las
  siguientes. El presupuesto y las condiciones de Dyna-Q se fijarán en A11.

## Métricas

La utilidad del estado inicial se estima por el **retorno promedio sin
descuento**, con el mismo peso para cada episodio. Si el objetivo se alcanza
en el paso `T`, el retorno es `−(T − 1)`; si el episodio solo se trunca, es
`−700`. En cada evaluación se guarda también el gráfico de la media acumulada
de esos retornos y se marca el promedio final.

Las mismas trayectorias sirven para calcular el retorno promedio descontado
con γ de evaluación fijo en 0,99 (Σγᵗrₜ desde t = 0), la tasa de éxito y los pasos promedio
entre éxitos. Los pasos entre éxitos se registran como ausentes si ningún
episodio termina por objetivo. El descuento de evaluación es independiente
del γ de entrenamiento para que los resultados se puedan comparar. Se
considera éxito toda transición con `terminated=True`, incluso si en el
mismo paso se alcanza el límite.

Para agentes tabulares se registra además el promedio de `max Q(s₀, a)`,
estimado al inicio de los mismos episodios. Es un diagnóstico de la tabla
y queda ausente para la referencia aleatoria. La definición del retorno
principal es una decisión del proyecto. D3 pide visualizar la utilidad
promedio y deja abierto su cálculo.

## Registro y reproducción

Se usa un ID `ACR-NNN` por experimento. Su entrada en `registro.md` indica
hipótesis, autor, configuración, resultado y próximo paso. Los archivos de
cada fase quedan en `experimentos/acrobot/ACR-NNN/` con subcarpetas para
entrenamiento y evaluación. Cada fase genera `config.json`,
`episodios.csv` y `resumen.json`. El modelo queda en `modelo.npz` y el gráfico
de evaluación en `utilidad.png`.

Desde `Acrobot/`, con el entorno de Poetry sincronizado, una prueba corta
se ejecuta con dos procesos:

```sh
salida="$(mktemp -d)"
poetry run python experimentos_qlearning.py entrenar --episodios 20 --salida "$salida/entrenamiento"
poetry run python experimentos_qlearning.py evaluar --episodios 10 --modelo "$salida/entrenamiento/modelo.npz" --salida "$salida/validacion"
```

Para una nueva corrida se eligen carpetas de salida nuevas. Los valores
predeterminados de los comandos son los recuentos del protocolo formal.
