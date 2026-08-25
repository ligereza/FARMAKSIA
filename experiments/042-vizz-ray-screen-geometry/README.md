# VIZZ 042 — ojos, pantalla y trazos de luz

Este experimento convierte la idea de VIZZ en un esquema óptico manipulable:
una sola pantalla compartida, tres modelos de ojo y rayos que se recalculan
cada vez que la pantalla cambia de posición.

Los tres modelos son conceptuales:

- Miopía: el foco cae antes de la retina.
- Hipermetropía: el foco queda detrás de la retina.
- Astigmatismo: los dos meridianos tienen focos distintos.

El dibujo representa la inversión óptica en la retina y una reconstrucción
conceptual de orientación por el cerebro. No calcula una receta, no diagnostica
una condición ocular y no utiliza la cámara ni el gaze mapper productivo.

## Ejecutar

Desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe experiments/042-vizz-ray-screen-geometry/ray_screen_simulator.py
```

Controles:

- `←` / `→`: mover la pantalla a izquierda/derecha.
- `↑` / `↓`: moverla arriba/abajo.
- `PageUp` / `PageDown`: acercar/alejar la pantalla.
- `R`: volver al centro.
- `Espacio`: mostrar/ocultar trazos.
- `F`: mostrar/ocultar focos.

También se pueden usar los tres controles deslizantes de la barra derecha.
Todos los modelos siguen la misma pantalla y se vuelven a calcular en cada
cambio; no existen tres pantallas independientes.

## Qué demuestra y qué no

Demuestra la relación geométrica entre posición de pantalla, distancia de
objeto, foco y plano retinal en un modelo de lente delgada. Es un primer
instrumento de pensamiento para el futuro modelo 3D de VIZZ.

No demuestra que una persona tenga exactamente una de estas geometrías, ni que
un ajuste visual reduzca fatiga. La siguiente fase puede reemplazar los
parámetros ilustrativos por una geometría de pantalla y ojos calibrada, y luego
añadir la respuesta subjetiva de `sinreferencia.html`.

## Verificación

```powershell
.\.venv\Scripts\python.exe experiments/042-vizz-ray-screen-geometry/run_contract_test.py
```

El contrato exige que un mismo desplazamiento de pantalla cambie los rayos de
los tres modelos, conserve la inversión retinal y mantenga dos focos para el
modelo astigmático.
