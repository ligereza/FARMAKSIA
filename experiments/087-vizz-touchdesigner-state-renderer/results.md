# Resultados del experimento 087

## Evidencia obtenida

Ejecutado desde la raíz del repositorio:

```text
.\.venv\Scripts\python.exe experiments\087-vizz-touchdesigner-state-renderer\run_contract_test.py
VIZZ_087_CONTRACT=PASS
```

La suite completa también terminó con `SUITE_VALID`, incluyendo el contrato y
la provenance de 087. Durante esa ejecución no se lanzó TouchDesigner.

También pasó `py_compile` sobre `state_router.py`, `host_adapter.py`,
`run_contract_test.py` y `touchdesigner/bootstrap_vizz_renderer.py`; el
`state_schema.json` pudo analizarse como JSON y `git diff --check` no encontró
errores de whitespace.

La inspección de la ayuda offline instalada corrigió dos supuestos del primer
borrador: `Constant CHOP` usa la secuencia `par.const.numBlocks` y cada bloque
expone `par.name`/`par.value`; `Filter CHOP` usa `type`, `width` y los controles
del One Euro, no `filterwidth`. El bootstrap ahora usa esos nombres documentados.

Los casos cubiertos son:

- estado válido minimizado, sin propagar una clave secreta adicional;
- estado vencido, futuro o con confianza baja convertido a `UNKNOWN`;
- esquema, NaN, rectángulo de foco y grupos malformados rechazados;
- pose relativa del tracker convertida sin inventar yaw, pitch ni foco ocular;
- plan visual acotado: parallax pequeño, escala de profundidad moderada y
  contexto basado en foco explícito, manteniendo el contenido crítico nítido;
- salida 046 válida convertida en foco UV, mientras que monitor ambiguo o sin
  intersección permanece `UNKNOWN`;
- bootstrap con transporte inactivo y sin dependencias de captura, input o
  procesos externos.

## Qué demuestra

Existe una frontera de datos pequeña y verificable entre el host de VIZZ y un
renderer TouchDesigner. Un renderer puede recibir pose, interés visual y
actividad agregada sin recibir frames crudos, texto escrito ni comandos.
La política de presentación ya tiene un lugar separado del renderer: puede
rechazar el estado antes de que una expresión de TouchDesigner mueva la escena.

## Qué no demuestra

No se abrió TouchDesigner, no se ejecutó el bootstrap dentro de su runtime y no
se midió latencia, FPS, GPU, licencia, Spout, Maxine ni comportamiento de una
ventana real. Por lo tanto, 087 es preparación de integración, no evidencia de
que el renderer ya funcione en la instalación del usuario.

## Siguiente prueba autorizable

Abrir TouchDesigner manualmente y ejecutar el bootstrap una sola vez con estado
manual. Comprobar que aparecen `manual_state`, `state_filtered`,
`base_surface`, `motion_plane` y `outTOP`; después medir el movimiento de la
superficie con valores sintéticos. Sólo si esa prueba pasa se elegirá la ruta
de imagen WGC→Spout o una alternativa permitida por la licencia.
