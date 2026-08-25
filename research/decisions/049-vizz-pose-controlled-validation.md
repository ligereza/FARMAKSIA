# ADR-049 — VIZZ: validación controlada de pose y condición

## Estado

Implementada como diagnóstico; no modifica el runtime ni el perfil 0.4.

## Protocolo

La validación recoge tres repeticiones de los 12 targets en las condiciones
`with_glasses` y `without_glasses`, con el mismo orden reproducible de targets.
Entre condiciones la UI solicita explícitamente el cambio de lentes. Cada
captura usa la misma ventana estable de 300 ms + 900 ms y persiste solamente:

- características oculares agregadas;
- seis proxies geométricos de pose;
- condición, repetición y target;
- calidad, cantidad válida y MAD.

No se escribe vídeo, no se inicia el overlay y no se sobrescribe
`.vizz-calibration.json`.

## Proxies de pose

El tracker registra, sin afirmar que sean pose 3D clínica:

```text
face_center_x_norm
face_center_y_norm
face_width_norm
face_height_norm
eye_roll_norm
eye_distance_norm
```

Sirven para comprobar si la inversión de yaw sigue a una variación de cabeza,
escala, recorte o inclinación ocular. Para una pose 3D completa todavía serían
necesarios intrínsecos, landmarks faciales suficientes y una estimación
geométrica explícita.

## Criterio de análisis

Comparar modelos anidados y splits por sesión completa:

1. mapper sin pose;
2. mapper con proxies de pose;
3. baseline afín/ridge;
4. polinomio actual.

Separar resultados por condición, fila, target y repetición. Si el efecto de
condición desaparece al controlar pose, no atribuirlo a lentes. Si persiste
con pose estable y landmarks consistentes, dejar abiertas las hipótesis de
óptica, reflejos y detector.

## Kill tests

- No aceptar una explicación causal basada sólo en error interno.
- No dividir frames aleatoriamente entre train y test.
- No permitir que la validación escriba el perfil de runtime.
- Si el modelo con pose no mejora en sesiones no vistas, conservar el mapper
  base y no entrenar aún la MLP.
