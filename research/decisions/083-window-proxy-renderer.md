# Decisión 083 — renderer proxy visual como núcleo

**Fecha:** 2026-08-27
**Estado:** adoptada experimentalmente
**Frentes:** FARMAKSIA, VIZZ, X-ANA-X, CODE-INE

## Decisión

El núcleo de la capa adaptativa será un renderer proxy visual: una superficie
separada que recibe frames de una ventana autorizada, aplica un plan espacial
de representación y, sólo cuando exista una transformación invertible,
traduce la interacción hacia la fuente.

La integración Python entre dos aplicaciones queda como adaptador opcional,
no como fundamento. Dos aplicaciones pueden tener motores, objetivos y
modelos de estado incompatibles; la capa común es el espacio de representación,
no una falsa API universal.

## Evidencia que cambió la decisión

El experimento 081 utilizó el camino oficial de
[Windows.Graphics.Capture](https://learn.microsoft.com/en-us/windows/apps/develop/media-authoring-processing/screen-capture)
y el ejemplo MIT de
[Microsoft Windows UI Composition](https://github.com/microsoft/Windows.UI.Composition-Win32-Samples).
En esta máquina, una fuente efímera fue capturada, sus cuatro regiones fueron
permutadas y un clic sobre una región reubicada regresó a la coordenada fuente.
El cambio de la fuente produjo un segundo frame que coincidió con el proxy.

El resultado valida una propiedad de ingeniería, no una afirmación sobre
percepción humana ni sobre cualquier aplicación.

## Modelo

Para una imagen fuente `I(x,t)`, el renderer construye:

```text
P(y,t) = R(I(T⁻¹(y),t), plan)
```

El input visible `y` sólo puede enviarse a `x = T⁻¹(y)` si `T` es biyectiva en
esa región. Si el plan oculta, duplica, mezcla o no identifica un área, el
resultado debe ser `UNKNOWN`/preview-only, nunca un clic silencioso.

## Capas

1. **Fuente de píxeles:** Windows Graphics Capture con selección y permiso
   explícitos. No se captura el escritorio global por defecto.
2. **Escena proxy:** regiones, anclas, transformaciones, estilos y estado
   temporal declarativos. La escena no necesita conocer el código fuente de la
   aplicación.
3. **Semántica opcional:** UI Automation, OCR o un plugin pueden proponer qué
   región representa un botón, panel o texto. Ninguna de esas fuentes se acepta
   como verdad sin identidad, versión y verificación.
4. **Input:** preview sin captura primero; interacción sólo con un mapa inverso
   y una política explícita. El HUD permanece pasivo.

## Por qué no basta una capa overlay

Un overlay click-through es correcto para foco, atenuación y ritmo, pero no
puede reordenar la interfaz inferior: sólo dibuja encima. Para cambiar la
gráfica hay que componer una vista proxy. Eso explica por qué las pruebas 057 y
058 eran válidas para un HUD, pero insuficientes para el objetivo actual.

## Próximo slice

Crear una escena proxy de una aplicación real seleccionada por el usuario, en
modo preview, con regiones UIA cuando existan y fallback visual marcado como
incierto. Medir:

- latencia fuente → proxy;
- frames cambiados frente a frames presentados;
- pérdida de regiones y áreas no invertibles;
- exactitud del mapa inverso en un sandbox propio;
- GPU/CPU en quietud y movimiento.

No se debe empezar por un agente que decida el reordenamiento. Primero debe
existir un renderer que aplique fielmente un plan y pueda revertirlo.

## Kill tests

- Si el proxy bloquea una aplicación al no tener modo preview, falla.
- Si el input se envía cuando `T⁻¹` es ambiguo, falla.
- Si se capturan ventanas ajenas a la selección explícita, falla.
- Si la ventana fuente cambia y el proxy no se actualiza, falla.
- Si una vista cambia significado o inventa semántica, no es renderer: queda
  rechazada como adaptación.
