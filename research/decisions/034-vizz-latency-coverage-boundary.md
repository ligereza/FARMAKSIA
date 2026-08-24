# Decisión 034 — VIZZ no entrega transiciones con cobertura parcial

Fecha: 2026-08-24

## Evidencia

El experimento 024 usó una trayectoria de mirada y eventos completamente
sintéticos:

| Latencia del fixture | Resultado |
|---:|---|
| 0 ms | cobertura completa; `available` |
| 100 ms | cobertura completa; `available` |
| 101 ms | cobertura incompleta; `unavailable` |
| 250 ms | cobertura incompleta; `unavailable` |
| 1000 ms | cobertura incompleta; `unavailable` |

Los casos completos conservaron `c04 → c07`. Los casos incompletos no
publicaron `repetition_entry`, aunque el subconjunto visible pudiera sugerir
una señal.

## Decisión

La compuerta VIZZ → CODE-INE requiere cobertura completa del ancla y de todos
los eventos posteriores necesarios para la consulta declarada. Una
representación focalizada o gaze-contingent con cobertura parcial debe marcar
la consulta como `unavailable`, no rellenar el contexto ni inferir una
transición.

Los milisegundos del experimento son solo una parametrización del fixture. No
son una tolerancia perceptual humana, una especificación de monitor ni una
razón para adoptar hardware.

## Próxima compuerta

Antes de cualquier eye tracking real habría que medir latencia cerrada,
calibración y calidad de datos con consentimiento explícito, además de definir
qué contexto periférico es necesario para la tarea. Hasta entonces VIZZ usa
fixtures locales y el adaptador manual opt-in.
