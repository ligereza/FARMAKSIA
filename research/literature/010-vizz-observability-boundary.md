# Investigación 010 — observabilidad, latencia y contexto en VIZZ

Fecha: 2026-08-24

## Resultado

La adaptación dependiente de la mirada no debe tratarse como un simple cambio
de CSS. Un sistema gaze-contingent tiene una latencia de extremo a extremo
formada por eye tracker, software, renderizado, sistema operativo y refresco de
pantalla. Esa latencia puede producir un desplazamiento entre la mirada y la
región representada; debe medirse antes de interpretar una adaptación como
fiel a la mirada.

Fuentes primarias y metodológicas:

- Mathôt et al., método directo para medir latencia de displays
  gaze-contingent: https://pmc.ncbi.nlm.nih.gov/articles/PMC4077667/
- Holmqvist et al., calidad de datos y cadena de medición en eye tracking:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC3996543/
- Macknik et al., medición de latencia cerrada en renderizado gaze-contingent:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC12675766/
- WebGazer.js 3.5.3: inferencia local en navegador, consentimiento de webcam
  y aviso de mantenimiento oficial terminado:
  https://github.com/brownhci/WebGazer
- Pupil: plataforma abierta, pero con hardware dedicado, dependencias nativas
  y API de tiempo real basada en red:
  https://github.com/pupil-labs/pupil

## Consecuencia para el contrato

Una observación puede ser:

1. estructuralmente inválida y rechazable;
2. formalmente válida pero incompleta o semánticamente ambigua;
3. suficientemente cubierta para una consulta computacional declarada.

El contrato no puede convertir por sí solo una etiqueta manual de ganancia,
acción o mirada en verdad sobre la tarea. VIZZ debe conservar el residuo de
información y CODE-INE debe devolver `unavailable` o `ambiguous` cuando la
observación ya no contiene la cobertura necesaria.

La literatura de fatiga visual digital también describe parpadeo reducido,
demanda de visión cercana, sequedad y carga multifactorial; no justifica
inferir fatiga, ansiedad o intoxicación desde una pantalla, pupila o log. La
fuente de síntesis ya registrada en `008-vizz-perceptual-adaptation.md`
permanece separada de este control de observabilidad.

## Decisión de herramientas

No se adopta todavía webcam, WebGazer ni Pupil Core. El experimento 023 usa
solo fixtures locales y validadores Python estándar. La siguiente compuerta
para eye tracking requeriría consentimiento explícito, calibración visible,
medición de latencia, privacidad local y una tarea humana aprobada; ninguna de
esas condiciones se activa automáticamente.
