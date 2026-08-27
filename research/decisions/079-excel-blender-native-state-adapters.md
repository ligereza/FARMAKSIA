# Decisión 079 — combinar UIA con estado nativo de Excel y Blender

## Decisión

Adoptar una arquitectura de dos superficies para el primer puente real de
X-ANA-X:

1. `pywinauto/UIA` para foco, ventanas y controles visibles.
2. API nativa de cada aplicación para el estado semántico que UIA no garantiza:
   COM local para Excel y Python API oficial para Blender.

El puente común será un grafo tipado de transiciones, no una correspondencia de
botones ni una capa de screenshots.

## Evidencia

El experimento 077 ejecuta Excel y Blender instalados en la máquina. Excel se
adjunta oculto y se cierra sin crear libros ni escribir datos. Blender se ejecuta
en background con configuración de fábrica, consulta su API y termina sin
guardar archivos. La suite exige que ambas superficies respondan y que las
pruebas adversariales rechacen mutaciones, input, cámara, screenshots, red y
escrituras.

## Razón histórica y técnica

Excel conserva un modelo de celdas, fórmulas y dependencias; Blender conserva un
modelo de escenas, objetos, nodos y evaluación. Sus interfaces visibles son
proyecciones de esos modelos. La analogía robusta debe preservar operaciones y
pre/postcondiciones, no nombres ni posiciones.

## Próxima prueba

Implementar un descriptor común para cinco primitivas: `select`, `inspect`,
`modify`, `commit` y `undo`. La primera tarea debe ser pequeña, reversible y
comprobable en ambas aplicaciones. No aceptar una traducción sólo porque la
interfaz muestra un control parecido.

## Límites

Esta decisión no prueba que Excel y Blender sean semánticamente equivalentes.
Sólo demuestra que existe una ruta técnica para observar sus estados reales sin
capturar datos privados ni automatizar acciones. La equivalencia de una tarea
concreta queda pendiente de validación.
