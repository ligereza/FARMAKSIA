# Experimento 078 — transiciones nativas Excel/Blender

Este experimento prueba el primer lenguaje común de X-ANA-X sobre las
aplicaciones reales, sin usar fixtures como sustituto del programa.

Se crean estados efímeros y no guardados:

- Excel: libro en memoria, valores, fórmula, resultado y reversión mediante
  `ClearContents`.
- Blender: objeto temporal, selección, modificación de posición y eliminación
  del objeto antes de terminar el proceso background.

Las mutaciones ocurren sólo dentro de procesos aislados creados por el
experimento. No se abren libros del usuario, no se guardan archivos, no se
inyecta teclado/mouse y no se captura pantalla, cámara o red.

## Reproducir

```powershell
python experiments/078-farmaxia-native-transition-probe/run_experiment.py
python experiments/078-farmaxia-native-transition-probe/run_contract_test.py
python experiments/078-farmaxia-native-transition-probe/run_kill_test.py
```

## Qué demuestra

Excel y Blender pueden expresar una secuencia compatible de alto nivel:

```text
create_entity → select_entity → modify_property → revert
```

Esto no demuestra que cualquier tarea de Excel se traduzca correctamente a
Blender. Demuestra algo más concreto: ambas aplicaciones exponen estados y
transiciones que pueden normalizarse sin reducirlas a clicks o coordenadas.
