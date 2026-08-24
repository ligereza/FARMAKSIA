# Experimento 002 — CODE-INE frente a scheduling

## Pregunta

¿Una política de continuación añade decisiones que un scheduler de tareas
predeclaradas no puede expresar?

## Diseño

Cada escenario tiene:

- calidad actual;
- presupuesto restante;
- acciones posibles;
- costo por acción;
- ganancia esperada;
- ganancia realizada;
- límite de reutilización;
- posibilidad de continuar, cambiar, reutilizar o detener.

Se compararán:

1. `FIFO`: ejecuta una cola fija hasta agotar presupuesto.
2. `priority`: ordena por ganancia esperada/costo, pero no puede detenerse ni
   cambiar la cola.
3. `continuation-candidate`: elige una acción, puede cambiar de rama,
   reutilizar o detenerse cuando el valor esperado cae bajo el umbral.

## Escenarios mínimos

- `deep-path`: continuar es razonable.
- `dead-end`: continuar consume presupuesto y cambiar es mejor.
- `reuse-credit`: una representación o resultado previo tiene alto valor de
  reutilización.
- `stop-now`: el costo marginal no justifica seguir.

## Medidas

- calidad final;
- costo consumido;
- presupuesto preservado;
- acciones elegidas;
- cambios de rama;
- reutilizaciones;
- decisiones de stop;
- diferencia frente a FIFO y priority.

## Condición de no-trampa

El baseline no se presentará como un scheduler débil: `priority` tendrá acceso
al mismo costo y ganancia esperada. La diferencia reclamada debe provenir de la
capacidad de cambiar la trayectoria o detenerse, no solo de usar una cola mejor.

## Estado

Primera ejecución completada. Los resultados están en `results.md`. La frontera
operacional frente a un scheduler de cola fija sobrevive, pero la novedad
teórica frente a metarazonamiento y optimal stopping sigue sin demostrarse.
