# ADR-051 — VIZZ: frontend eye-centric antes de la pantalla

## Estado

Aceptada como arquitectura experimental; todavía no reemplaza las features
del runtime ni el perfil de calibración existente.

## Decisión

La señal de gaze se construirá en dos etapas separadas:

```text
landmarks/iris de ambos ojos
        │
        ├─ punto medio
        ├─ distancia interocular
        ├─ corrección de roll y escala
        └─ pose 3D independiente
                │
                ▼
        vector de mirada en cámara
                │
                ▼
        geometría cámara-monitor + calibración personal
                │
                └─ coordenada de pantalla o UNKNOWN
```

La capa eye-centric elimina sólo transformaciones que puede identificar de la
pareja ocular: traslación, escala isotrópica y roll en el plano. No declara que
un giro 3D de cabeza sea equivalente a una transformación 2D. El yaw/pitch de
la cabeza debe medirse con un estimador independiente o resolverse mediante
geometría de cámara; si queda fuera de dominio, se rechaza la muestra.

## Evidencia actual

El experimento 035 obtuvo error máximo `8,77e-15` bajo escalas 0,5×/1×/2,5×,
traslaciones y roll de 0°/12°/-27°. Un par de ojos degenerado fue rechazado con
`interocular_distance_too_small`.

Esto es una propiedad matemática del transformador sintético, no una medida de
la cámara ni de precisión de pantalla. El experimento 034 confirmó además que
el baseline binocular actual y MobileOne S0 pueden ejecutarse en CUDA, pero
MobileOne trabaja con rostro completo y no sustituye esta representación.

## Próximo experimento

Conectar la normalización a los landmarks que ya produce el tracker, sin
modificar aún las seis features legacy. Para cada frame se conservarán ambos
vectores normalizados, distancia, roll, calidad y razón de `UNKNOWN`; luego se
compararán M0 legacy frente a M1 eye-centric+pose usando sesiones completas y
targets agrupados.

## Kill tests

- Si el detector pierde un ojo o la distancia interocular es degenerada,
  devolver `UNKNOWN`.
- Si escalar/trasladar/rotar una captura real altera la representación más allá
  del umbral preregistrado, no asumir invariancia del detector.
- Si el nuevo frontend mejora sólo el ajuste interno y no la sesión held-out,
  no se conecta al runtime.
- Si se confunde roll 2D con yaw/pitch 3D, detener la interpretación y exigir
  pose independiente.
