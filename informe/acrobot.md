# ACROBAT — Borrador para el informe

## Entorno y representación

Acrobot-v1 simula dos eslabones articulados. El agente observa el seno y el
coseno de los dos ángulos y las dos velocidades angulares. Puede aplicar
un torque de −1, 0 o +1 a la segunda articulación. El episodio termina
cuando el extremo supera la altura objetivo y el entorno da recompensa
0 en ese paso. Los pasos anteriores reciben −1. Si no alcanza el objetivo,
el límite externo trunca el episodio a los 700 pasos. Así, resolver un
episodio en menos pasos aumenta el retorno sin descuento.

Se construyeron dos discretizaciones iniciales de igual tamaño. La grilla
directa divide las cuatro componentes trigonométricas en cuatro intervalos
cada una y cada velocidad en seis intervalos. La angular reconstruye los
ángulos con `atan2`, asigna 12 intervalos a cada ángulo y ocho a cada
velocidad, con mayor resolución cerca de cero. Ambas reservan 9.216 estados
y usan una tabla densa de 27.648 valores, 216 KiB con `float64`. La
representación angular evita reservar celdas para combinaciones de seno y
coseno incompatibles con el círculo unitario. Agrupar estados continuos en
una misma celda puede ocultar diferencias de dinámica relevantes para
los dos algoritmos.
[Validación y decisiones de discretización](../documentación.md)

## Aprendizaje y evaluación

Q-Learning comienza con la tabla en cero. En cada paso elige una acción
al azar con probabilidad ε. En los demás pasos selecciona un máximo de
Q, con desempate uniforme. Después de observar una transición, aplica
`Q(s,a) ← Q(s,a) + α × [objetivo − Q(s,a)]`. El objetivo incluye
`γ × max Q(s',·)` si el estado siguiente admite continuar. Una
terminación usa solo la recompensa. El truncamiento por límite de pasos
cierra el episodio y conserva el valor futuro en la actualización.

Dyna-Q usa esa misma regla para las experiencias del entorno y para
experiencias del modelo aprendido. El modelo conserva la última transición
observada de cada par estado–acción. En cada paso de planificación se
sortea un estado observado y, dentro de él, una acción registrada. Con
n pasos de planificación, cada interacción real produce una actualización
directa y n simuladas. La última transición es una aproximación cuando
dos observaciones continuas caen en una misma celda y llevan a estados
siguientes distintos.
[Diseño de Dyna-Q](../Acrobot/diseno_dyna_q.md)

La evaluación greedy usa la tabla Q fija y las mismas semillas iniciales
de entorno para todas las políticas. El retorno medio sin descuento es la
métrica principal. Se mide también la tasa de éxito, el retorno descontado
con γ de evaluación = 0,99 y la cantidad de pasos entre los episodios
exitosos. Cada réplica de entrenamiento es una unidad independiente para
medir dispersión. La validación permite comparar y seleccionar
configuraciones. Las semillas finales se reservan hasta cerrar la selección.
[Protocolo y semillas](../experimentos/acrobot/protocolo.md)

## Proceso experimental y resultados disponibles

La primera comparación de discretizaciones mantuvo fijas la capacidad
de la tabla, la tasa α = 0,5, el descuento γ = 0,99 y una reducción lineal
de ε de 1 a 0,05 por episodio. Cada grilla se entrenó con tres semillas,
10.000 episodios por réplica y 1.000 episodios de validación greedy por
modelo. Se evaluó además una política aleatoria en las mismas semillas
de validación.

| Política | Retorno medio sin descuento | Éxito en validación | Millones de pasos de entrenamiento por réplica |
| --- | ---: | ---: | ---: |
| Grilla angular | −327,40 ± 96,61 | 97,7 % | 5,34 |
| Grilla directa | −337,91 ± 127,25 | 95,6 % | 6,38 |
| Aleatoria | −691,55 | 6,3 % | No aplica |

Los valores tras ± son desviaciones muestrales entre entrenamientos. La
grilla angular terminó con 3,68 veces más valores Q distintos de cero y
requirió 16,4 % menos pasos durante el entrenamiento. La ventaja media
emparejada en retorno greedy fue 10,51, con una desviación de 184,21.
Las tres réplicas muestran variación suficiente para conservar ambas
grillas en las siguientes pruebas. La tasa de éxito en entrenamiento y el
uso de la tabla motivaron probar una grilla directa con intervalos de
velocidad más finos cerca de cero.
[Registro de corridas y gráfico de A06](../experimentos/acrobot/registro.md#acr-004-a-acr-008--comparación-de-grillas-iteración-1)

## Datos para cerrar el informe

Incorporar los resultados de la segunda iteración de grillas después de su
revisión. Completar la secuencia de hiperparámetros de Q-Learning y las
rondas de Dyna-Q con hipótesis, corridas, resultados y decisiones, incluidas
las variantes descartadas. Agregar la comparación final, el modelo
entregable con su comando de carga y el anexo experimental completo. El
equipo debe cotejar este borrador con el código y las corridas antes de
integrarlo al PDF final.
