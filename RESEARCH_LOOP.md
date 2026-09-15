# Método de investigación FARMAKSIA

FARMAKSIA convierte preguntas en evidencia reutilizable. No crea una segunda
implementación de los runtimes de X-ANA-X, PUPILA o LUCIDA ni integra una
hipótesis sólo porque sus pruebas locales pasen.

## Ciclo de un experimento

1. Formular una pregunta refutable y declarar qué resultado la detendría.
2. Identificar el consumidor potencial y la frontera que no se debe cruzar.
3. Revisar la fuente y sus derechos antes de incorporar documentación, código
   o datos.
4. Usar fixtures sintéticos o datos con procedencia y permiso explícitos.
5. Separar observación, resultado calculado, hipótesis y limitaciones.
6. Registrar comando reproducible, procedencia, pruebas, resultado y
   desconocidos.
7. Si hay un consumidor real, proponer un contrato pequeño para el repositorio
   dueño; no copiar su runtime ni publicarlo como una capacidad demostrada.

Un experimento termina cuando responde su pregunta, cuando un kill test la
refuta o cuando no existe un consumidor identificable. Una propiedad que ya
pasó con evidencia no se vuelve a preguntar sin un cambio de entrada o de
criterio. El siguiente ciclo debe producir una diferencia verificable; si no,
se archiva la hipótesis y se avanza a otra.

## Fronteras activas

- `X-ANA-X`: motor compartido y contratos canónicos.
- `PUPILA`: asistencia y razonamiento perceptual/visual.
- `LUCIDA`: proyección y adaptadores de aplicaciones.
- `FARMAKSIA`: investigación, evidencia, límites y experimentos.

XIO puede ser una fuente futura de señales; no es una dependencia implícita de
los experimentos. Los resultados offline no prueban rendimiento en personas,
apps anfitrionas, cámaras, red ni hardware real.

## Integraciones recientes

- `090-farmaxia-adaptive-representation-layer`: frontera metadata-only entre
  señales visuales, coordinación PUPILA y proyección LUCIDA.
- `091-lucida-pupila-visual-acceptance`: aceptación offline de rutas explícitas
  hacia el motor LUCIDA.
- `092-pupila-temporal-integration`: replay temporal, expiración, revocación y
  reconstrucción persistente de propuestas.
- `093-iris-representation-ordering`: adaptación de una representación IRIS
  sintética, sin copiar el runtime editorial.

Los identificadores de estudios anteriores se conservan como procedencia; no
determinan los nombres ni las responsabilidades actuales.
