# ADR-046 — VIZZ: ventanas temporales estables antes de la calibración dinámica

## Estado

Aceptada para la base temporal; ampliada por
[ADR-047](047-vizz-single-multicondition-profile.md) para el perfil único
multicondición.

## Contexto

La calibración anterior recogía muestras continuamente mientras un punto
estaba visible y usaba el click únicamente para confirmar el promedio. Eso
permite que frames tomados mientras la persona mira el contador, cambia de
punto o inicia una sacada queden etiquetados con el objetivo anterior. El
problema es contaminación de etiquetas, no sólo ruido.

La orientación matemática recibida distingue entre el objetivo presentado,
la señal auxiliar del mouse y la muestra ocular. También recomienda separar
calibración estática, persecución suave y adaptación personalizada.

## Decisión

1. El objetivo presentado por VIZZ es la única etiqueta de gaze.
2. El mouse sólo arma una ventana de captura y se conserva como señal de
   interacción futura, nunca como ground truth ocular.
3. Cada punto estático usa una ventana fija con:
   - estabilización descartada;
   - captura de duración limitada;
   - umbral de calidad por frame;
   - mínimo de muestras válidas;
   - centro robusto por mediana;
   - rechazo por dispersión MAD excesiva.
4. El texto de estado se oculta durante la captura.
5. El perfil se versiona a `0.3` y declara `static-stable-window-v3`.
   Perfiles anteriores no se reutilizan porque su procedencia temporal no es
   equivalente.
6. El baseline sigue siendo la regresión regularizada existente. La
   trayectoria móvil y una cabeza MLP GPU sólo se aceptarán después de una
   comparación por sesiones o trayectorias no vistas.

## Contrato de captura

```text
WAITING_FOR_CLICK
        │ click cerca del objetivo
        ▼
SETTLING (300 ms, no se guardan muestras)
        ▼
CAPTURING (900 ms, sólo muestras válidas)
        ├─ insuficientes/inestables → retry
        └─ aceptadas → mediana → perfil estático
```

Los valores son hiperparámetros iniciales y deben validarse; no son
constantes fisiológicas. No se persiste vídeo crudo.

## Límites y kill tests

- Si la cámara no entrega suficientes muestras válidas, el punto se repite.
- Si la dispersión robusta supera el umbral, el punto se repite.
- Si un futuro modelo neuronal no mejora al ridge baseline en sesiones no
  vistas, se mantiene el baseline.
- Un split aleatorio por frames no es evidencia válida por fuga temporal.
- El movimiento de cabeza no se considera resuelto todavía: el tracker actual
  expone seis características oculares/geométricas y requiere una futura
  extensión explícita de pose.
- La calibración dinámica, la latencia estimada y la geometría 3D
  multimonitor quedan fuera de esta primera modificación.

## Consecuencia

La próxima calibración del usuario debe ejecutarse otra vez con
`--calibrate`. El cambio sacrifica la comodidad de acumular muestras sin
control, pero produce etiquetas temporales auditables y permite comparar de
forma limpia una futura fase de persecución suave.
