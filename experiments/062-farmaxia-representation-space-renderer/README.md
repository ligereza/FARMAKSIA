# Experimento 062 — RepresentationSpace renderer

## Pregunta

¿Puede FARMAKSIA mostrar varias interpretaciones de una misma intención sin
convertir la primera sugerencia en una decisión irreversible?

## Qué se implementa

Este vertical slice convierte la decisión [068](../../research/decisions/068-representation-space-renderer.md)
en un renderer local, autocontenido y reversible:

- `Explorar` mantiene una rama central y las demás disponibles como contexto.
- `Comparar` exige dos candidatos explícitos y conserva la semántica de origen.
- `Comprometer` muestra un preview local y exige confirmación antes de marcar la
  dirección como comprometida.
- `Revertir` restaura el estado de representación anterior.
- las políticas de ritmo, densidad y movimiento son declarativas; no hay strobo
  ni animación obligatoria.

Abrir `renderer.html` directamente en un navegador. No necesita servidor,
dependencias, cámara, GPU, permisos, red ni otro programa.

## Contrato reproducible

```powershell
python experiments/062-farmaxia-representation-space-renderer/run_experiment.py
python experiments/062-farmaxia-representation-space-renderer/run_contract_test.py
python experiments/062-farmaxia-representation-space-renderer/run_kill_test.py
```

El fixture es sintético. El resultado demuestra que la arquitectura mantiene
ramas, fases y compuertas; no mide aprendizaje, precisión ocular, comodidad,
ansiedad, rendimiento ni calidad creativa de una persona.

## Kill tests

El contrato debe bloquear si una rama pierde semántica de origen, si explorar o
comparar adquieren ejecución, si falta confirmación, si se referencia una rama
inexistente, si se habilita flashing periódico o si se elimina la reversión.

## Desconocido siguiente

Todavía no sabemos cuántas ramas puede comparar una persona sin sobrecarga, ni
si esta representación mejora una tarea real. La siguiente prueba debe ser una
revisión humana pequeña y voluntaria del renderer con tareas sintéticas, sin
inferir estados mentales ni operar bajo intoxicación.
