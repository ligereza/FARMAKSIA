# Decisión 033 — el puente VIZZ → CODE-INE debe fallar cerrado ante ambigüedad

Fecha: 2026-08-24

## Evidencia

El experimento 023 comparó siete variantes del fixture 022:

- el baseline recuperó `c04 → c07`;
- campo de acción ausente, tiempo no monótono e identificador duplicado
  fueron rechazados;
- eliminar `c04`, bajar su ganancia o cambiar la clase de `c07` mantuvo la
  forma del envelope, pero cambió la transición y se clasificó como
  `ambiguous`.

Las fuentes de observabilidad 010 muestran que la mirada real añadiría
latencia, calibración, calidad de datos y dependencia de hardware/software.
Ninguna de esas variables fue medida aquí.

## Decisión

La interoperabilidad sintética se conserva, pero `available` queda reservado a
una cobertura que coincida con el contrato declarado. Una entrada formalmente
válida no equivale a una observación verdadera: si la cobertura o el objetivo
no están garantizados, el estado debe permanecer `ambiguous` o
`unavailable`. No se autoriza inferir repetición subjetiva, ansiedad,
intoxicación ni neurotransmisores.

No se adopta todavía WebGazer, Pupil Core ni ningún dispositivo. El adaptador
manual permanece opt-in, local y sin captura cruda.

## Kill tests y siguiente compuerta

La suite debe conservar una matriz de 1 caso `available`, 3 `rejected` y 3
`ambiguous`. Una futura tarea humana necesitaría declarar cobertura, objetivo,
consentimiento y un criterio de parada antes de crear datos; el loop continuará
con fixtures sintéticos mientras esa acción no exista.
