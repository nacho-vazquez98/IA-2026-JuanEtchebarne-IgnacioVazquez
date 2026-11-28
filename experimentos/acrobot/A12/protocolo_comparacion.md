# A12 — Comparación de Q-Learning y Dyna-Q

La comparación final requiere la configuración de Q-Learning consolidada
en A08 y la configuración de Dyna-Q seleccionada en A11. La selección de
ambas se hará con validación. El conjunto final queda reservado para evaluar
modelos y criterios ya fijados.

## Comparaciones

1. **Efecto de planificar.** Comparar Dyna-Q con su control de cero pasos
   simulados usando la misma grilla, α, γ, calendario de ε, presupuesto y
   pares de semillas. Con cero pasos, el diseño reproduce las decisiones
   y actualizaciones de Q-Learning. Esta comparación atribuye las
   diferencias a habilitar el modelo y las actualizaciones simuladas.
2. **Rendimiento de las políticas seleccionadas.** Comparar los modelos de
   A08 y A11 con evaluación idéntica. Si fueron entrenados con grillas,
   otros hiperparámetros o presupuestos diferentes, conservar ese contexto
   al explicar la diferencia. Reportar la referencia aleatoria en el mismo
   conjunto final para dar escala a los retornos.

En ambos casos, el protocolo base es Acrobot-v1 sin renderizado y con
límite de 700 pasos por episodio. Los controles de entrenamiento comparten
semillas de entorno y agente por réplica. El desempate greedy durante la
evaluación usa la semilla 300.000. Se informan las versiones del entorno,
el commit, la cantidad de episodios y la huella de cada modelo.
[Protocolo de Acrobot](../protocolo.md)

## Eficiencia de aprendizaje y costo

- Mostrar curvas de retorno de entrenamiento con la misma ventana y,
  cuando existan, las evaluaciones greedy de las copias de Q en puntos de
  control. El retorno de entrenamiento incluye exploración. Las
  evaluaciones intermedias usan validación y un entorno independiente.
- Mostrar los puntos de control por episodio y por interacciones reales
  acumuladas. Igual cantidad de episodios puede implicar distintos
  números de pasos. Si las copias de Q se guardaron a diferentes
  cantidades de pasos, mostrar las coordenadas observadas y explicitar
  cualquier diferencia de presupuesto. Usar un corte común exacto solo
  cuando haya una política guardada en ese corte.
- Contabilizar T actualizaciones reales y n × T simuladas. Reportar tiempo
  de entrenamiento y de validación por separado, junto con segundos de
  entrenamiento por millón de pasos reales. Medir las comparaciones de
  tiempo en la misma máquina y con la misma política de concurrencia.
  Informar el tamaño de las tablas Q y el de los NPZ por separado. Si se
  mide el modelo disperso, indicar cómo se contó su tamaño.
  [Diseño de Dyna-Q y puntos de control](../../../Acrobot/diseno_dyna_q.md#comparación-en-a11-y-a12)

## Evaluación final y criterio de cierre

Registrar primero los IDs, parámetros, réplicas y huellas a evaluar.
Luego usar `experimentos_qlearning.py evaluar --conjunto final` con
1.000 episodios para cada NPZ y para el control `--aleatorio`. El
entrenamiento y la selección quedan cerrados al empezar esta evaluación.
Para cada réplica registrar las mismas semillas de entorno 200.000 a
200.999, las banderas de terminación y truncamiento, y el retorno de los
episodios.

- Métrica principal de P05: retorno medio sin descuento. Reportar por
  réplica y como media entre réplicas, con desviación muestral entre
  entrenamientos. Para cada par restar el retorno medio de Q-Learning al
  de Dyna-Q y mostrar los valores individuales y su dispersión. Las 1.000
  trayectorias de un modelo comparten la misma Q y no son 1.000 réplicas
  independientes de entrenamiento.
- Acompañar con tasa de éxito, pasos medios entre éxitos y retorno
  descontado con γ de evaluación = 0,99. Usar `max Q(s₀,a)` como
  diagnóstico y mantener la utilidad medida con recompensas.
- Conservar al menos el modelo entregable, las configuraciones, las
  métricas por episodio, el gráfico y un comando comprobado de evaluación
  desde otro proceso. La conclusión debe identificar las configuraciones
  comparadas, el costo y las limitaciones, incluso cuando no aparezca
  una mejora consistente.
