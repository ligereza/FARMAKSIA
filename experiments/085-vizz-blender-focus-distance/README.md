# Experimento 085 — VIZZ: cámara, distancia y plano focal en Blender

## Propósito

Construir una escena controlada para separar tres variables que antes estaban
mezcladas:

1. **distancia del observador a la pantalla**;
2. **tamaño angular de la pantalla** en la cámara;
3. **plano de enfoque** y profundidad de campo.

La escena representa un monitor físico 16:9, un objeto cercano a la persona y
una cámara que representa al observador. El monitor y el objeto cercano están en
planos distintos. La cámara se aleja o se acerca en metros reales de la escena;
Cycles calcula la profundidad de campo mediante la apertura de la cámara.

Esto es una **simulación óptica**, no una afirmación de que Cycles reproduzca
exactamente la acomodación humana. Sirve para construir una intuición y medir
qué cambia geométricamente antes de probar una interfaz real.

## Ejecutar

Desde `C:\IA\FARMAXIA`:

```powershell
$blender = "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
& $blender --background --python experiments\085-vizz-blender-focus-distance\build_scene.py -- --output-dir experiments\085-vizz-blender-focus-distance\output --render
```

El script crea:

- `output\vizz_focus_distance.blend` — escena editable;
- `output\focus_screen_060m.png` — cámara a 0,60 m enfocada en la pantalla;
- `output\focus_near_060m.png` — misma cámara enfocada en el objeto cercano;
- `output\focus_screen_100m.png` — cámara a 1,00 m enfocada en la pantalla;
- `output\scene_manifest.json` — parámetros y límites de la escena.

Para abrir la escena normalmente:

```powershell
& $blender output\vizz_focus_distance.blend
```

## Controles dentro de Blender

Selecciona `VIZZ_CONTROLLER` y modifica sus propiedades personalizadas:

- `observer_distance_m`: distancia de la cámara al plano del monitor;
- `focus_distance_m`: distancia focal independiente de la cámara;
- `focus_offset_m`: `0.0` enfoca la pantalla; `-0.22` enfoca el objeto cercano.

La línea de tiempo tiene marcadores de referencia para 0,45 m, 0,60 m y 1,00 m,
pero no anima esas propiedades: deben seguir siendo controles manuales y no
ser sobrescritos silenciosamente por keyframes.

La cámara conserva la misma orientación hacia el centro del monitor. Por eso
un cambio de distancia modifica el ángulo visual de la pantalla de forma
legible, en vez de esconderlo reajustando automáticamente el encuadre. El
foco es ahora independiente: puede seguir la pantalla o permanecer bloqueado
para hacer visible el desenfoque experimental.

## Lectura matemática mínima

Para un ancho físico de pantalla `W` y distancia `d`, su ancho angular es:

```text
theta = 2 atan(W / (2 d))
```

La profundidad de campo depende además de focal, apertura y círculo de
confusión. Cambiar la distancia no convierte una imagen 2-D en una pantalla
3-D: esta escena añade profundidad real sólo para visualizar qué hace un
sistema óptico cuando existen planos a distintas distancias.

## Límites y kill tests conceptuales

- La cámara no es un ojo humano y el desenfoque de Cycles no prueba comodidad,
  fatiga ni mejora visual.
- Una pantalla real emite luz desde un plano aproximadamente único; el efecto
  de profundidad de esta escena no debe venderse como 3-D sin hardware o una
  técnica de presentación binocular.
- Si se modifica el foco y no cambia el desenfoque en los dos planos, el
  experimento queda invalidado.
- Si se cambia la distancia y el tamaño angular no varía, la cámara está siendo
  reencuadrada de manera incorrecta.
- El modo Cycles puede renderizar en CPU si Blender no tiene un dispositivo GPU
  configurado. No se instala ningún driver ni se fuerza una descarga.

## Documentación técnica consultada

- [Blender 4.5 LTS — Cameras](https://docs.blender.org/manual/en/4.5/render/cameras.html)
- [Blender 4.5 API — CameraDOFSettings](https://docs.blender.org/api/4.5/bpy.types.CameraDOFSettings.html)
- [Blender 4.5 API — Drivers](https://docs.blender.org/api/4.5/bpy.types.Driver.html)
- [Blender 4.5 LTS — Command Line Arguments](https://docs.blender.org/manual/en/4.5/advanced/command_line/arguments.html)
