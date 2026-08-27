# Decisión 070 — Selección marginal de ramas

**Estado:** adoptada como política experimental  
**Fecha:** 2026-08-27  
**Frentes:** RepresentationSpace, X-ANA-X, CODE-INE, VIZZ

## Decisión

El número visible de ramas no será una constante universal. Se elegirá un subset
pequeño con `facility_location_greedy`, usando cobertura de necesidades
semánticas, costo de display, presupuesto explícito y ganancia marginal mínima.

`plan-full` funciona como ancla recuperable. Las ramas no seleccionadas no son
incorrectas: se mantienen disponibles para inspección posterior. MMR puede
diagnosticar redundancia y diversidad, pero no ordenará la UI final ni se tratará
como predictor de preferencia.

## Contrato

Cada candidato debe:

- referenciar el contrato de consultas críticas de 063;
- declarar cobertura semántica y costo positivo;
- cubrir sólo necesidades conocidas;
- permanecer sujeto a las invariantes de identidad, relación, incertidumbre y
  procedencia;
- aceptar quedar fuera del subset visible sin ser eliminado.

El selector debe declarar ancla, presupuesto, máximo visible, penalización de
costo, umbral de ganancia marginal y método. Si la ancla no cabe, el sistema
bloquea; no elimina silenciosamente la referencia completa.

## Por qué

Un `k=4` fijo convierte una fixture en una pseudo-ley humana. Un ranking por
clicks puede confundir posición con preferencia y cerrar prematuramente el
espacio. La selección marginal hace explícito qué se gana y qué cuesta cada rama,
manteniendo la exploración reversible.

## Desconocidos

Todavía no sabemos si los pesos semánticos predicen utilidad, si el costo visual
se correlaciona con sobrecarga o si una rama aparentemente redundante aporta una
analogía decisiva. Esas preguntas requieren datos humanos declarados y un diseño
contrabalanceado; no serán inferidas desde selección automática.
