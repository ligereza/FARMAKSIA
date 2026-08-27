# Experimento 077 — inventario real Excel/Blender

Este experimento convierte la decisión teórica en una comprobación concreta.
Inspecciona dos aplicaciones instaladas en Windows mediante sus superficies
reales:

- Excel mediante su objeto COM local, sin abrir un libro ni modificar celdas.
- Blender mediante su API Python oficial en modo `--background` y
  `--factory-startup`, sin guardar archivos ni ejecutar operadores.

`pywinauto/UIA` queda como superficie común para foco y estructura visible;
las APIs nativas entregan el estado interno que UIA no puede garantizar.

En la ejecución local verificada, Excel respondió como versión `16.0`, build
`20326.0`, sin libros adjuntos. Blender respondió como versión `5.1.1` y
expuso objetos, escenas, árboles de nodos, sockets, dependency graph y undo/
redo. Las superficies que dependen de un documento Excel abierto quedan
registradas como diferidas, no como ausentes.

## Reproducir

```powershell
python experiments/077-farmaxia-excel-blender-capability-inventory/run_experiment.py
python experiments/077-farmaxia-excel-blender-capability-inventory/run_contract_test.py
python experiments/077-farmaxia-excel-blender-capability-inventory/run_kill_test.py
```

El resultado es un inventario de capacidades, no todavía un traductor entre
aplicaciones. La siguiente etapa debe comparar transiciones equivalentes:
seleccionar, inspeccionar, modificar, confirmar y deshacer.

## Límite deliberado

No se capturan pantallas, cámara, títulos, texto de usuario, teclado ni mouse.
No se ejecutan acciones en ninguna aplicación. La observación no demuestra aún
que una acción de Excel tenga una traducción correcta en Blender; sólo verifica
que existen las dos superficies técnicas desde las cuales construirla.
