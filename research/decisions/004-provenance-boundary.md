# Decisión 004 — procedencia como condición de clasificación

Fecha: 2026-08-23

## Hipótesis

No se puede clasificar una transformación como KETAMINE o X-ANA-X si no se
conoce qué entidades fueron entradas, qué actividad las combinó, qué agente
declaró una hipótesis y qué información fue calculada o inventada.

## Evidencia

El manifiesto local registra:

- 10 entidades;
- 6 actividades;
- 3 consultas;
- 2 agentes;
- hashes de `input.svg`, `events.json` y `run_experiment.py`.

El validador acepta el caso íntegro y rechaza una copia temporal cuyo SVG fue
alterado, con `hash mismatch` explícito.

## Decisión

Adoptar el manifiesto JSON local, inspirado en W3C PROV, como herramienta del
laboratorio. No adoptar aún RO-Crate ni OpenLineage como dependencia o backend.

La procedencia se vuelve una precondición de cualquier afirmación posterior:

- dato externo no es información preservada;
- hipótesis humana no es observación computada;
- actividad de transformación no es equivalente al resultado;
- una representación derivada debe declarar residuo y consulta preservada.

## Kill test

La prueba de integridad fue superada: modificar una entrada hace fallar el
validador. La adopción será revertida si el manifiesto se vuelve más costoso de
mantener que la evidencia que aporta o si no puede representar el siguiente
experimento de CODE-INE/VIZZ sin introducir ambigüedad.

## Próximo ciclo

Usar la misma distinción de procedencia para separar scheduling de política de
continuación: registrar qué acciones fueron disponibles, cuál fue su costo,
qué estado era observable y quién autorizó detener o cambiar el proceso.
