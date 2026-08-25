# Experimento 047 — VIZZ: playback controlado de política visual

## Objetivo

Separar el efecto de una política visual del error del tracker. Esta fase usa
una escena sintética y un foco manual; no abre cámara, no lee el escritorio y
no altera otras ventanas.

## Modos

- `static_full`: contenido completo.
- `static_clean`: baseline estático con menor detalle de fondo.
- `adaptive_protected`: reduce detalle periférico de baja prioridad y conserva
  señales periféricas.
- `adaptive_unprotected`: control de fallo que también degrada una alerta
  periférica.

La posición se expresa en grados visuales aproximados a partir de una pantalla
de 45° × 26°. Es una unidad de playback, no una medición fisiológica.

## Ejecutar

```powershell
.\.venv\Scripts\python.exe experiments/047-vizz-controlled-playback/run_experiment.py
.\.venv\Scripts\python.exe experiments/047-vizz-controlled-playback/run_contract_test.py
Start-Process (Resolve-Path experiments/047-vizz-controlled-playback/playback.html)
```

En la página se puede cambiar el modo y hacer clic para mover el foco simulado.
El experimento debe comprobar primero que la política protegida mantiene la
alerta periférica y que el control no protegido la deteriora.

## Límites

Este playback prueba descriptores y transformaciones locales en una escena
controlada. No prueba que una persona lea mejor, se fatigue menos o prefiera
VIZZ. La comparación humana vendrá sólo después del overlay pasivo y deberá
contrastar contra `static_clean`, no contra una interfaz artificialmente mala.
