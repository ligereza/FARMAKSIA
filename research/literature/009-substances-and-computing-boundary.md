# Investigación 009 — sustancias, percepción y procesos informáticos

Fecha: 2026-08-23

## Regla de seguridad

FARMAXIA no realizará experimentos de programación bajo intoxicación, no
recomendará sustancias para mejorar productividad y no intentará diagnosticar
consumo mediante webcam, pupila o logs. La farmacología se usa para entender
por qué las metáforas tienen tensiones distintas y para definir límites de
diseño.

## Correspondencias parciales

- Codeína: agonismo opioide μ; puede producir somnolencia, mareo y sedación,
  miosis y deterioro de capacidades necesarias para operar maquinaria. La
  etiqueta oficial advierte también riesgos graves con otros depresores del
  sistema nervioso central:
  https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=5819bdf7-300e-45b8-8f3a-447b53656293&version=29
- Alprazolam/XANAX: modula el sitio benzodiacepínico de GABA-A y aumenta la
  inhibición mediada por GABA; puede afectar sedación, memoria, coordinación y
  operación de maquinaria:
  https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=7538d0d0-346e-4c3e-8f7a-c1cac8ec8ed3
- Ketamina: antagoniza receptores NMDA del sistema glutamatérgico y puede
  producir disociación, distorsiones perceptuales, amnesia y alteración del
  control:
  https://www.dea.gov/factsheets/ketamine
- Cannabis: el uso reciente puede afectar memoria, atención, coordinación,
  juicio, movimiento, tiempo de reacción y percepción temporal:
  https://www.cdc.gov/cannabis/health-effects/brain-health.html

Estas correspondencias no convierten un estado computacional en una réplica
farmacológica. Son restricciones: sedación, amnesia, miosis, disociación o
alteración de atención pueden hacer que una interfaz adaptativa sea menos
fiable, no más segura.

## Consecuencia para VIZZ

La pupila no identifica una droga: depende de luminancia, atención, emoción,
fármacos, edad y otros factores. Un sistema VIZZ que observe mirada o pupila
debe tener consentimiento explícito, procesamiento local, indicador visible y
modo de no registro. Si aparecen señales de deterioro, el comportamiento
responsable es reducir riesgo, conservar el estado y sugerir pausa; no ajustar
la interfaz para permitir operar maquinaria ni continuar una tarea peligrosa.
