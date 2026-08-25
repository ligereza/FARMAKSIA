# VIZZ 042 — ojos, pantalla y trazos de luz

Este experimento convierte la idea de VIZZ en un esquema óptico manipulable:
una sola pantalla compartida, tres modelos de ojo y haces de rayos que se
recalculan cada vez que la pantalla cambia de posición.

La primera versión era sólo una proyección esquemática. Esta versión usa un
trazado paraxial explícito: cada punto de la pantalla emite varios rayos que
entran por distintas alturas de una abertura finita. En la lente delgada, la
pendiente cambia según `m_salida = m_entrada - altura/f`. Los rayos se
propagan hasta la retina y se prolongan hasta el foco calculado.

Los tres modelos son conceptuales:

- Miopía: el foco cae antes de la retina.
- Hipermetropía: el foco queda detrás de la retina.
- Astigmatismo: los dos meridianos tienen focos distintos.

El dibujo representa la inversión óptica en la retina y una reconstrucción
conceptual de orientación por el cerebro. No calcula una receta, no diagnostica
una condición ocular y no utiliza la cámara ni el gaze mapper productivo.

La base matemática es la ecuación de lente delgada:

```text
1/f = 1/u + 1/v
m = -v/u
```

`u` es la distancia del objeto a la lente, `v` la distancia del foco real y
`m` la magnificación con inversión. El modelo usa óptica paraxial; no simula
superficies corneales, índices de refracción, aberraciones de alto orden ni
acomodación.

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
objeto, foco y plano retinal en un modelo de lente delgada. En la vista
espacial, las líneas punteadas son trayectorias hacia cada ojo; en los paneles
inferiores, las líneas de color son los rayos después de refractarse en la
lente. Es un instrumento de pensamiento para el futuro modelo 3D de VIZZ.

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

## Base de investigación

- [OpenStax: formación de imágenes con lentes](https://openstax.org/books/college-physics/pages/25-6-image-formation-by-lenses): rayos principales, imagen real invertida y reglas de trazado.
- [OpenStax: lentes delgadas](https://openstax.org/books/university-physics-volume-3/pages/2-4-thin-lenses): ecuación `1/f = 1/u + 1/v` y magnificación `m = -v/u`.
- [National Eye Institute: errores refractivos](https://www.nei.nih.gov/eye-health-information/eye-conditions-and-diseases/refractive-errors/types-refractive-errors): relación conceptual entre miopía, hipermetropía, astigmatismo y foco retinal.
- [Modelo computacional de apertura ocular](https://pmc.ncbi.nlm.nih.gov/articles/PMC6597540/): referencia sobre por qué un modelo ocular completo requiere superficies e índices, más allá de una lente delgada.
