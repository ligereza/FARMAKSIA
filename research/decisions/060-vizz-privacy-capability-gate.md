# ADR 060 — VIZZ: compuerta de privacidad y capacidades sin cámara

Fecha: 2026-08-25  
Estado: decisión de arquitectura para la siguiente implementación

## Decisión

VIZZ no asumirá que toda función necesita eye tracking. El producto se
organizará por capacidades explícitas y escalables:

| Nivel | Cámara | Funciones permitidas |
|---|---:|---|
| `NO_CAMERA` | no | layout/EDID de monitores, DPI, teclado agregado opt-in, mouse auxiliar, reglas de contenido y geometría del escritorio |
| `INPUTS_ONLY` | no | actividad de teclado y mouse como contexto de tarea; nunca texto ni identidad de tecla |
| `HEAD_POSE` | opt-in | presencia, encuadre y pose de cabeza; sin gaze ocular |
| `BINOCULAR_EYES` | opt-in explícito | dos rayos oculares relativos, calidad, parpadeo/oclusión y geometría experimental |

La aplicación debe iniciar en `NO_CAMERA`. El usuario activa una capacidad
superior para una sesión concreta, observa un estado inequívoco de cámara
activa y puede detenerla. Si el permiso se deniega o la cámara falla, VIZZ
debe conservar el modo sin cámara en vez de bloquear funciones no oculares.

## Flujo de datos mínimo

```text
camera permission -> frame ephemeral in RAM -> GPU inference
                 -> feature record / UNKNOWN -> release frame + camera handle
```

El frame no debe escribirse a disco, enviarse por red, pasar a un preview ni
entrar en el envelope de interacción. La salida persistible se limita a
vectores, calidad, estados `UNKNOWN`, timestamps monotónicos y contadores de
actividad. Esto es minimización de datos, no una garantía criptográfica de
borrado de memoria: copias internas del driver, GPU o runtime pueden existir
fuera del control de Python.

## Frontera real frente a malware

Transformar el frame en código antes de guardarlo protege contra el propio
VIZZ registrando imágenes, una fuga accidental o una dependencia que intente
subirlas. No puede garantizar protección contra malware que controle el
proceso, el driver, la sesión de Windows o el dispositivo de cámara: ese
malware puede observar antes de la transformación.

Por tanto, la defensa debe componerse de:

- no abrir cámara cuando la función no la necesita;
- comprobar permiso antes de inicializarla y fallar a un modo sin cámara;
- cerrar el handle al terminar y no dejar un worker de captura en background;
- ejecutar localmente, sin red por defecto, sin preview y sin vídeo persistente;
- fijar y verificar hashes de modelos/dependencias;
- mantener logs sin frames, texto, teclas ni contenido de pantalla;
- recomendar tapa/obturador físico cuando el usuario necesite una garantía
  contra software comprometido.

Windows permite denegar la cámara globalmente, para aplicaciones de escritorio
o por aplicación; su documentación recomienda comprobar el acceso antes de
inicializar y ofrecer un fallback cuando se deniega
([Microsoft camera privacy](https://learn.microsoft.com/en-us/windows/apps/develop/camera/camera-privacy-setting)).
La minimización y el procesamiento local siguen la orientación de control de
datos del [NIST Privacy Framework](https://www.nist.gov/privacy-framework/privacy-framework).

## Estado actual de FARMAKSIA

- `031–033` demuestran inferencia GPU y una ruta headless experimental, pero
  `run_vizz.py` todavía es camera-dependent cuando se inicia ese runtime.
- `053` conserva dos rayos relativos sin vídeo.
- `054` audita trazas locales sin reabrir cámara; los archivos del usuario
  permanecen fuera de git.
- Aún no existe un router productivo que mantenga `NO_CAMERA` como estado
  inicial. Esa es la siguiente implementación, no una propiedad ya validada.

## Kill tests

1. Arrancar una función `NO_CAMERA` no importa ni inicializa el proveedor de
   cámara.
2. Permiso denegado deja disponible la función sin cámara y produce un estado
   auditable, no un retry silencioso.
3. Detener `BINOCULAR_EYES` cierra la cámara y no deja worker activo.
4. Ningún artefacto de prueba contiene frames, preview, texto o teclas.
5. La suite funciona sin red y sin corpus arbitrario.
6. La documentación nunca presenta la transformación a vectores como defensa
   completa contra malware con control del sistema.

## Próximo paso

Implementar el router de capacidades y un modo `NO_CAMERA` verificable antes de
modificar el runtime headless. Después, añadir `HEAD_POSE` y
`BINOCULAR_EYES` como activaciones explícitas, manteniendo la geometría y los
kill tests separados.
