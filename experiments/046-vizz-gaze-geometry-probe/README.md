# Experimento 046 — VIZZ: estado de mirada y geometría de monitores

Fecha: 2026-08-25.

## Objetivo

Implementar la fase 3 del plan: separar percepción, geometría y política
visual antes de modificar el contenido real de la pantalla.

La entrada simulada contiene ambos ojos, un vector de mirada, confianza,
incertidumbre, pose válida y versión del layout. La salida resuelve el rayo
contra los planos físicos de los monitores y produce una coordenada normalizada
`uv`, hipótesis de monitor o `UNKNOWN`.

También expone `distance_m` y permite calcular cobertura angular con
`2 atan(size / (2 * distance))`. Esto evita tratar un escritorio virtual como
un único rectángulo de píxeles.

## Qué prueba

- Un objetivo en el monitor primario.
- El mismo objetivo mundial tras trasladar la cabeza.
- Un objetivo en el segundo monitor.
- Un monitor inclinado respecto de la cámara/frente del usuario.
- Teclado y mouse como contexto, nunca como ground truth ocular.
- Baja confianza, ojo perdido y layout obsoleto.
- Dos monitores superpuestos como ambigüedad explícita.
- Radio seguro que incorpora velocidad, latencia e incertidumbre.

La política devuelve `ADAPTIVE_REGION_DESCRIPTOR` sólo como descripción. El
experimento no abre cámara, no inicia GPU, no modifica ventanas, no captura
vídeo y no altera el escritorio.

## Modelo geométrico

Cada monitor es un rectángulo físico en un plano 3D. El origen del rayo es el
punto medio de ambos ojos y la dirección proviene del estimador de mirada. Para
cada monitor se calcula la intersección positiva con su plano y se acepta sólo
si cae dentro del rectángulo.

```text
E = (E_left + E_right) / 2
P(lambda) = E + lambda * gaze_direction
```

Si no hay intersección, el estado es `UNKNOWN`. Si hay más de una, también. No
se convierte el escritorio virtual con una escala global y no se elige un
monitor silenciosamente.

## Política segura

```text
safe_radius_deg = base_radius_deg
                 + gaze_speed_deg_s * latency_ms / 1000
                 + 2 * uncertainty_deg
```

Es una regla de ingeniería para cubrir error y retardo, no una ley fisiológica.
Una futura implementación puede usarla para decidir el tamaño de una región,
pero este experimento permanece sin renderer. Todo estado inválido usa
`STATIC_FALLBACK` y conserva señales periféricas.

## Ejecutar

```powershell
.\.venv\Scripts\python.exe experiments/046-vizz-gaze-geometry-probe/run_experiment.py
.\.venv\Scripts\python.exe experiments/046-vizz-gaze-geometry-probe/run_contract_test.py
```

## Kill tests

- La traslación de cabeza con el mismo objetivo mundial no puede cambiar `uv`.
- Un monitor obsoleto, una cámara no válida, un ojo perdido o baja confianza
  deben producir `UNKNOWN`.
- Monitores que compiten por el mismo rayo deben producir
  `ambiguous_monitor`, no una elección silenciosa.
- Mouse y teclado no pueden cambiar la etiqueta de mirada.
- La política no puede mutar el contenido en este experimento.
- El radio seguro debe crecer con latencia, velocidad e incertidumbre.

## Límites

Es un contrato sintético de geometría. No mide la precisión de la webcam, no
valida un modelo preentrenado, no demuestra confort o reducción de fatiga y no
es una medición clínica. La siguiente fase será un playback visual controlado;
el overlay real queda bloqueado hasta pasar este contrato.
