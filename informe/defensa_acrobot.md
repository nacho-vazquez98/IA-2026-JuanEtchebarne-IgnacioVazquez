# ACROBAT — Práctica para la defensa

Preguntas para ensayar con otro integrante. Respondan primero sobre el
pizarrón o con código cerrado y luego verifiquen la explicación con las
fuentes del repositorio.

## Ambiente, tabla y actualización

1. ¿Qué recibe y qué controla el agente? Describan la observación de seis
   valores, los tres torques y el criterio de altura. Expliquen por qué
   llegar al objetivo en el paso 67 da un retorno de −66 y por qué un
   episodio truncado al paso 700 obtiene −700.
2. ¿Por qué las grillas iniciales tienen el mismo tamaño? Calculen
   `4⁴ × 6² = 12² × 8² = 9.216` estados y multipliquen por tres acciones
   y ocho bytes por valor. Expliquen qué combinaciones reserva la
   directa y qué pasa al discretizar ángulos cerca de ±π.
3. ¿Qué cambia entre una terminación y un truncamiento? Si `Q(s,a) = 0`,
   α = 0,5, γ = 0,9, recompensa −1 y el máximo del sucesor es 2,
   el objetivo de una transición que trunca sin terminar es 0,8 y Q
   pasa a 0,4. Si la transición termina por el objetivo con recompensa
   0, el objetivo es 0. Ambas banderas cierran el episodio y la
   terminación determina el objetivo si las dos coinciden.

[Contrato, discretización y política](../documentación.md#acrobat--acrobot-q-learning-y-dyna-q)

## Planificación y comparación

4. ¿Qué distingue una transición real de una simulada en Dyna-Q?
   Expliquen qué alimenta el modelo, cómo se selecciona la muestra y
   de dónde sale el valor Q de arranque en el objetivo. Con los
   números de la pregunta anterior y un sucesor cuyo máximo queda en
   2, dos actualizaciones simuladas sobre el mismo par llevan Q de
   0,4 a 0,6 y luego a 0,7.
5. ¿Por qué un ambiente determinista puede generar dos sucesores
   discretos para un mismo par estado–acción? Vinculen la respuesta con
   el tamaño de una celda. Expliquen el compromiso entre guardar la
   última transición y estimar frecuencias para varios resultados.
6. ¿Cómo demostrarían que Dyna-Q usa mejor la experiencia? Propongan
   un control con cero pasos simulados, parámetros y semillas
   emparejados, y comparen desempeño por interacciones reales y por
   tiempo de entrenamiento. Justifiquen por qué un mejor retorno con
   más actualizaciones puede tener mayor costo de cómputo.

[Diseño y pruebas numéricas de Dyna-Q](../Acrobot/diseno_dyna_q.md)

## Interpretación de resultados

7. Con los resultados de A06, expliquen por qué la angular tuvo
   mayor éxito durante el entrenamiento y por qué la diferencia greedy
   observada fue imprecisa. Citen el éxito durante el entrenamiento
   (61,32 % y 27,94 %) y las diferencias emparejadas de retorno
   (−169,58, +198,58 y +2,52), en lugar de apoyar la conclusión en un
   solo modelo.
8. ¿Para qué se separan entrenamiento, validación y evaluación final?
   Expliquen qué semillas se usan para elegir parámetros, cómo se evita
   actualizar Q durante la evaluación y por qué 1.000 episodios del
   mismo modelo no equivalen a 1.000 entrenamientos independientes.
9. Carguen un NPZ de una corrida de referencia con el evaluador.
   Identifiquen la grilla, el algoritmo, la semilla y la huella del
   modelo. Expliquen qué datos se necesitan para ejecutar la política
   greedy y cuáles faltan si se quisiera reanudar Dyna-Q con su modelo
   de transiciones.

[Proceso experimental de A06](../experimentos/acrobot/registro.md#acr-004-a-acr-008--comparación-de-grillas-iteración-1)

[Configuración y ejecución de la evaluación](../experimentos/acrobot/protocolo.md)

## Antes del ensayo final

Agregar las preguntas sobre las conclusiones de A07, A11 y A12 cuando
estén disponibles. Hacer una revisión cruzada con COUNTER y practicar
la reproducción del modelo definitivo desde una copia limpia.
