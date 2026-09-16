# Experimento 084 — VIZZ: distancia relativa y escala visual

## Qué prepara

Este experimento prueba la hipótesis concreta de VIZZ: si la persona se
acerca o se aleja de la pantalla, la representación puede cambiar de tamaño
para conservar aproximadamente el mismo tamaño angular.

La tarjeta de crédito queda fuera del algoritmo: una webcam no puede identificar
de forma fiable una tarjeta genérica frente a otros rectángulos. `P0` se sella
explícitamente con la tecla Espacio, cuando el detector facial confirma un
rostro y dos ojos. En cada observación se usan obligatoriamente dos reglas:

```text
regla 1: distancia entre los centros de ambos ojos
regla 2: ancho facial estable entre landmarks laterales
```

Se corrigen de forma limitada yaw/pitch y se fusionan ambas escalas en espacio
logarítmico:

```text
s_ojos  = ojos_actuales_corregidos / ojos_P0_corregidos
s_cara  = cara_actual_corregida / cara_P0_corregida
s       = exp((w1 log(s_ojos) + w2 log(s_cara)) / (w1+w2))
d_actual / d_P0 = 1 / s
```

Si las dos reglas discrepan demasiado, el resultado es `UNKNOWN`; no se elige
silenciosamente una sola. Si yaw/pitch salen del dominio, también se detiene
la estimación. Roll se registra, pero no cambia la longitud euclidiana en este
modelo.

## Cómo verificarlo ahora

Desde `C:\IA\FARMAXIA`:

```text
python experiments/084-vizz-distance-scale-experiment/run_experiment.py
python experiments/084-vizz-distance-scale-experiment/run_contract_test.py
python experiments/084-vizz-distance-scale-experiment/run_kill_test.py
python experiments/084-vizz-distance-scale-experiment/run_analyzer_test.py
```

Estos comandos no encienden cámara, no abren ventanas, no interceptan input y
no modifican la pantalla. Verifican la matemática con datos sintéticos.

Cuando esos tres comandos pasen, la captura humana se inicia explícitamente
con este comando:

```powershell
.\.venv\Scripts\python.exe experiments\084-vizz-distance-scale-experiment\run_capture.py --fullscreen --duration 60
```

Durante `P0` aparece la previsualización de la cámara con el rostro y los dos
puntos oculares. Adopta la distancia que quieras usar como referencia y pulsa
`ESPACIO` sólo cuando veas `ROSTRO + 2 OJOS OK`. Se capturan unos 2 segundos de
las dos reglas faciales; después desaparece la cámara y sólo queda el objetivo.
No hace falta tarjeta, clic ni marco artificial. Nunca se guarda vídeo.
Pulsa `ESC` para detener y guardar el registro en `.vizz-distance-scale-trace.jsonl`.
Después se analiza con:

```powershell
.\.venv\Scripts\python.exe experiments\084-vizz-distance-scale-experiment\analyze_trace.py
```

## Protocolo humano posterior

1. Mantener cámara y pantalla en posiciones fijas. Adopta la distancia personal
   que quieras usar como `P0`.
2. Esperar `ROSTRO + 2 OJOS OK` y pulsar `ESPACIO`. Durante la ventana estable
   se registran `eye_distance_px`, `face_width_px`, roll y calidad.
3. Mostrar el Landolt C. Hacer bloques a distintas distancias. Para validar
   la matemática, anotar también la distancia real con una cinta o marcas
   físicas; sin ella sólo se obtiene distancia relativa.
4. En esta primera captura, mantener la cara aproximadamente orientada hacia
   la cámara mientras cambias de distancia. El tracker actual no entrega aún
   yaw/pitch 3-D; por eso el archivo declara `pose_correction` como no
   disponible y no finge corregirlo. Una futura versión podrá añadir solvePnP
   o landmarks 3-D sin cambiar la lógica de las dos reglas.
5. Comparar dos modos: tamaño fijo y tamaño ajustado. El resultado esperado
   del modo ajustado es que el diámetro en píxeles sea proporcional a la
   distancia: más cerca → menos píxeles; más lejos → más píxeles, conservando
   aproximadamente el ángulo.

El Landolt C permite registrar orientación y tamaño sin depender de una
respuesta subjetiva larga. No es un examen médico ni demuestra reducción de
fatiga. Si aparece molestia, se detiene la prueba.

## Qué significa el fixture

El fixture usa como ejemplo una pantalla de 380×210 mm y 2560×1440 píxeles,
con `P0 = 600 mm` y un objetivo de 100 píxeles. A 450 mm el objetivo pasa a
75 píxeles; a 900 mm pasa a 150 píxeles. Ambos producen casi el mismo ángulo
porque `tamaño_físico / distancia` se mantiene.

Esto demuestra una relación geométrica, no todavía que el ojo humano prefiera
el efecto. La futura captura debe evaluar error de escala, discrepancia entre
las dos reglas, cobertura, latencia y comodidad declarada por la persona.

## Límites y kill tests

- P0 entrega una escala relativa en píxeles. La webcam no mide por sí sola
  milímetros absolutos: para profundidad métrica faltan intrínsecos de cámara
  o una distancia física conocida.
- La corrección coseno es una aproximación de protocolo, no una reconstrucción
  anatómica 3-D.
- Un rostro girado, un ojo ocluido, un landmark inestable o dos escalas
  incompatibles deben producir `UNKNOWN`.
- La tarjeta no se usa como regla: un objeto genérico no aporta identidad ni
  profundidad métrica suficiente para este experimento.
