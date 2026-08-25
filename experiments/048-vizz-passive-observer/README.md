# Experimento 048 — VIZZ: observador pasivo y trazabilidad mínima

## Objetivo

Preparar la fase de observación mientras el usuario trabaja sin modificar el
contenido normal. El adaptador recibe un `GazeState` y contexto de interacción,
pero sólo persiste indicadores necesarios para evaluar geometría y tarea.

## Datos que sí persiste

- timestamp monotónico;
- `VALID`/`UNKNOWN` y razón;
- monitor e `uv` si existen;
- confianza, incertidumbre y radio seguro;
- estado de fijación;
- conteo de eventos de teclado, sin identidad de tecla;
- posición del mouse como covariable, nunca como ground truth.

## Datos que no persiste

- vídeo o frames;
- texto escrito;
- identidad de teclas;
- título de ventana;
- contenido de pantalla;
- inferencia de atención, ansiedad, intoxicación o farmacología.

## Ejecutar

```powershell
.\.venv\Scripts\python.exe experiments/048-vizz-passive-observer/run_experiment.py
.\.venv\Scripts\python.exe experiments/048-vizz-passive-observer/run_contract_test.py
```

La integración real con la cámara y el `InteractionTrace` existente queda
bloqueada hasta que 046 tenga un frontend de percepción que entregue el
contrato `GazeState`. Este experimento no inicia dispositivos.
