# Decisión 086 — frontera de runtime para VIZZ y TouchDesigner

**Fecha:** 2026-08-28  
**Estado:** propuesta implementable, pendiente de ejecución en TouchDesigner  
**Frentes:** VIZZ, X-ANA-X, CODE-INE

## Decisión

TouchDesigner será el renderer GPU de una escena adaptativa, no la autoridad de
captura, permisos, semántica ni entrada. VIZZ conserva esas responsabilidades
en un host de Windows y entrega a TouchDesigner un estado numérico normalizado.

```text
Windows host                         TouchDesigner
capture consentida ─┐                ┌─ composición GPU
UI Automation       ├─ estado ───────┤  parallax / foco / color
teclado/puntero      ┤  filtrado      └─ salida visual
pose opcional       ─┘
```

El primer producto es un **Focus Layer** pasivo: la aplicación original sigue
siendo la superficie interactiva y VIZZ sólo modifica la presentación. El
segundo producto es un **proxy renderer**: captura una ventana explícitamente
seleccionada y la recompone. El input se habilita sólo en regiones con mapa
inverso verificable.

## Rutas de imagen evaluadas

1. `Video Device In TOP` + `Face Track CHOP`: válido para el sensor visual
   nativo de TouchDesigner en Windows con NVIDIA RTX/Maxine. No debe ser el
   consentimiento de captura de la aplicación ni la única fuente de VIZZ.
2. `Screen Grab TOP`: prototipo rápido de imagen de escritorio, pero no define
   por sí solo la selección ni la frontera de privacidad de una ventana.
3. Windows Graphics Capture → Spout → `Syphon Spout In TOP`: candidato de
   producción para mantener la imagen local en GPU y desacoplar permisos del
   renderer.
4. Windows Graphics Capture → Shared Memory: alternativa cuando la edición y
   licencia de TouchDesigner la permitan; no se adopta como requisito aún.
5. NDI/transportes de red: quedan fuera del primer camino local por latencia,
   configuración y superficie de fallo innecesarias.

## Contrato de estado

El renderer recibe únicamente `state_schema.json`. Sus canales conceptuales
son `head.x/y/z`, `head.rx/ry/rz`, `focus.x/y/w/h`, `focus.interest`, actividad
de teclado/puntero, confianza, rectángulo fuente/monitor y permisos.

- `head.x/y` controlan parallax pequeño y suavizado.
- `head.z` sólo controla una profundidad visual moderada; no se interpreta como
  milímetros ni como profundidad clínica.
- rotación, blur y escala tienen límites fijos para que el texto siga siendo
  legible.
- confianza baja, estado viejo o permiso ausente neutralizan la adaptación.
- el renderer no recibe títulos, texto escrito, frames crudos ni comandos de
  ejecución.

## Por qué esta separación

TouchDesigner resuelve muy bien TOPs, feedback, filtros, composición,
renderizado y salida de performance. Windows resuelve mejor la identidad de la
ventana, UI Automation, permisos de captura, DPI, foco y traducción de input.
Mezclar ambos hace que una falla de renderer pueda convertirse en captura o
input no autorizado.

## Kill tests

1. Cancelar el selector de ventana deja el renderer en `UNKNOWN`/sin imagen.
2. Sin permiso de cámara o captura no se inicia ninguna fuente.
3. Un estado viejo o con confianza baja no mueve la escena.
4. La salida pasiva no roba foco ni bloquea el mouse; un host click-through
   debe usar las reglas de ventana de Windows.
5. Una transformación no biyectiva sólo permite preview; nunca traduce clicks.
6. Cambiar monitor, DPI, resolución u orientación invalida la calibración de
   coordenadas hasta una nueva inspección.
7. Si desaparece el renderer, la aplicación fuente conserva su estado.
8. El bootstrap de TouchDesigner no crea cámara, captura, ventana del sistema,
   proceso externo ni socket activo por defecto.

## Desconocido que queda explícito

- si la edición/licencia del usuario permite Spout, Shared Memory o Direct
  Display Out;
- si el runtime Maxine requerido por Face Track CHOP está disponible;
- latencia real de WGC→Spout→TouchDesigner en esta máquina;
- si UIA expone semántica útil para cada aplicación;
- si el efecto mejora tarea o fatiga: eso exige evaluación humana separada.

