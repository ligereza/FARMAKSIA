# Decisión 078 — adopción real de pywinauto/UIA

**Fecha:** 2026-08-27
**Estado:** adoptada como adapter Windows read-only

## Decisión

FARMAKSIA deja de reimplementar la primera capa de lectura de interfaces
Windows y adopta `pywinauto 0.6.9` con backend `uia`, fijado al commit
`f6219c0`. La biblioteca se usa para obtener estructura de ventanas y
controles; no se le entrega autoridad para decidir intenciones, representar
analogías, ejecutar acciones ni declarar éxito.

Microsoft UI Automation expone elementos en un árbol, tipos de control,
propiedades, patrones y eventos. `pywinauto` ofrece un wrapper Python sobre
Win32 y UIA. Es la pieza de infraestructura que necesitábamos para dejar de
simular toda la superficie en fixtures.

## Evidencia

El experimento 076 importó el checkout real en Python 3.13 y enumeró el desktop
local: 6 ventanas y 1.623 controles descendientes en una ejecución, incluyendo
156 botones. No emitió títulos ni inyectó input. El contrato positivo y 7 kill
tests pasaron.

## Qué sí adopta FARMAKSIA

- descubrimiento estructural de ventanas y controles;
- roles/tipos y conteos de controles;
- futura lectura de bounds, estados y capabilities bajo una superficie
  explícitamente autorizada;
- la dependencia y sus transitive dependencies fijadas y registradas.

## Qué no adopta

- no convierte un control en intención humana;
- no garantiza que una acción logró su efecto;
- no sustituye X-ANA-X, CODE-INE, VIZZ ni el ledger de procedencia;
- no habilita clicks, teclado, captura de pantalla ni red por defecto;
- no se usa para inspeccionar silenciosamente aplicaciones fuera del alcance
  declarado.

## Riesgo de mantenimiento

El checkout `master` fue descartado porque importaba `injectlib` sin declarar la
dependencia. El tag 0.6.9 funcionó, pero exige fijar también `pywin32`,
`comtypes` y `six`. Si la dependencia vuelve a romperse o no entrega estructura
útil en una aplicación concreta, se revierte el adapter, no se llena el hueco
con otro modelo sin medir.

## Siguiente decisión

Elegir una aplicación Windows concreta y medir si UIA permite construir un
`SurfaceDescriptor` útil para un overlay. Sólo después comparar con Playwright
para web o Tree-sitter para código; no instalar los tres a la vez.
