# Decisión 068 — Renderer de espacio de representaciones

**Estado:** adoptada como experimento local, no como producto terminado  
**Fecha:** 2026-08-27  
**Frentes:** FARMAKSIA, X-ANA-X, CODE-INE, VIZZ

## Decisión

FARMAKSIA tratará las representaciones como un `RepresentationSpace`: un
conjunto de ramas que proyectan la misma fuente semántica con distintas
organizaciones perceptuales. La rama activa ocupa el centro, pero las ramas no
seleccionadas permanecen visibles como contexto recuperable.

El flujo mínimo es:

```text
intención emergente → explorar → comparar → preview → confirmar → comprometer → revertir
```

La verificación gobierna el compromiso y cualquier ejecución futura; no bloquea
la exploración representacional. Este experimento no ejecuta acciones reales.

## Límites técnicos

- `space.json` es la fuente declarativa del contrato; `renderer.html` es una
  implementación visual local del mismo contrato.
- Las cuatro proyecciones iniciales son mapa de relaciones, ruta guiada,
  analogía contrastiva y superficie completa.
- Toda rama debe declarar qué semántica preserva, qué incertidumbres muestra y
  qué política sensorial usa.
- `compare` requiere dos candidatos explícitos; no existe un ranking silencioso
  de “mejor” representación.
- `commit` requiere confirmación, preview reversible y operación de revertir.
- no se incorporan cámara, eye tracking, overlay del escritorio, red, agentes
  externos ni ejecución de código generado.

## Por qué ahora

La investigación previa de CODE-INE mostró que una intención puede madurar desde
lo emergente a lo verificable, pero faltaba una superficie donde la ambigüedad
fuera una propiedad visible y operable. El renderer hace auditable esa transición
sin fingir que el sistema conoce la intención humana antes de que la persona la
forme.

## Trade-offs

Mantener alternativas usa más espacio visual y puede aumentar la carga de
comparación. Ocultarlas reduciría densidad, pero haría que la primera sugerencia
pareciera autoridad. Se elige la primera opción para proteger exploración,
trazabilidad y reversibilidad.

Cuatro ramas son una fixture de ingeniería, no un número fisiológico. Un sistema
real deberá adaptar el número de ramas a tarea, pantalla y preferencias
explícitas, no a una inferencia opaca de atención.

## Kill tests y próximo punto de revisión

La arquitectura se rechaza si una rama pierde semántica, si las fases tempranas
pueden ejecutar, si el compromiso no pide confirmación, si el preview no revierte
o si el renderer necesita permisos para abrirse.

El siguiente punto de revisión es una evaluación humana sintética y voluntaria:
comparar dos representaciones de la misma tarea y registrar sólo respuestas
declaradas, tiempo de elección y errores observables. No se debe inferir ansiedad,
intoxicación, discapacidad o capacidad cognitiva desde la interfaz.
