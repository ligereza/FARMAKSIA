# Decisión 084 — Adaptador visual grandMA3 → Titan

Fecha: 2026-08-27
Estado: **adoptar como frente experimental**

## Decisión

FARMAKSIA investigará una transformación de grandMA3 onPC hacia el modelo
mental de Avolites Titan como un **adaptador visual-semántico reversible**.
No será una conversión de showfiles, un clon de grandMA, un plugin de Titan ni
un puente DMX en la primera etapa.

La dirección inicial es:

```text
ventana grandMA3 elegida por el usuario
        ↓ captura pasiva + observación UIA
regiones y estados observables
        ↓ contrato canónico de tareas de iluminación
leyendas, orden y agrupación familiares de Titan
        ↓ preview reversible
usuario decide si la traducción sirve
```

## Por qué este caso sí es un salto

Los dos programas viven en el mismo dominio profesional, pero no organizan la
experiencia de la misma forma. Esto permite una prueba más exigente que una
reordenación de rectángulos: el adaptador debe distinguir el objeto que el
operador manipula del nombre que cada fabricante le da.

El primer mapa es provisional:

- `grandMA3 sequence + cues` → `Titan cue list + cues`;
- `grandMA3 executor` → `Titan playback`;
- `grandMA3 preset` → `Titan palette`;
- `grandMA3 programmer` → `Titan programmer`;
- `grandMA3 views/pools/layouts` → `Titan workspaces`.

El mapa sólo se acepta por tarea y por estado observable. Una analogía de
vocabulario no es prueba de equivalencia.

## Alcance y seguridad

Se permite descargar y observar el software oficial. La descarga actual de
grandMA3 onPC Windows 2.4.2.2 fue verificada fuera del repositorio con SHA-256
`91D16E94B636BC20DE2969AFA5AD2503A0F53AF0083D64ED156D912B995653E0`.

La primera etapa queda limitada a:

- software offline y fixtures sintéticos;
- captura de la ventana seleccionada explícitamente;
- lectura de UIA y geometría cuando esté disponible;
- preview, etiquetas y reordenación visual reversible;
- cero salida DMX, cero conexión a MA-Net/TitanNet, cero fixtures reales;
- cero inyección de input y cero modificación de showfiles;
- estado `UNKNOWN/PARTIAL/UNSUPPORTED` cuando no exista correspondencia.

El paquete descargado no se incorpora al repositorio. No se descargan cracks,
emuladores, instaladores de terceros ni corpus de procedencia desconocida.

## Contrato mínimo que debe implementarse

```text
LightingSurfaceContract {
  source_app, source_version, source_region
  canonical_task
  source_object_kind, source_object_id_observation
  target_vocabulary, target_object_kind
  observed_state, confidence
  reversible_transform
  capability: read_only | preview | input_pending | execute_blocked
  provenance, timestamp
}
```

El `source_object_id_observation` no es un ID interno inventado: puede ser un
rol UIA, un rectángulo estable o una observación manual declarativa. Si sólo
hay píxeles, la confianza baja y el sistema debe abstenerse antes de activar
una acción.

## Métrica de la primera versión

Para cinco tareas: selección, atributo, objeto reutilizable, cue/cue list y
playback/executor, medir:

1. cobertura de regiones identificadas;
2. consistencia de la tarea canónica entre grandMA3 y Titan;
3. error de transformación inversa sobre un fixture sintético;
4. latencia del preview;
5. número de equivalencias declaradas `PARTIAL` o `UNKNOWN`;
6. ausencia de input y salida externa.

El éxito no es “grandMA se ve igual a Titan”. Es que una persona que piensa en
la gramática de Titan pueda localizar la misma tarea en grandMA sin que la
capa oculte diferencias importantes.

## Siguiente acción

1. No instalar todavía el ZIP automáticamente: la descarga está autorizada,
   la instalación modifica Windows y puede introducir componentes/licencias.
2. Preparar el contrato declarativo y un fixture de cinco tareas.
3. Tras una instalación manual/offline de grandMA3 onPC, seleccionar su ventana
   y Titan Simulator con el picker de Windows.
4. Ejecutar el preview read-only y comparar las dos superficies.
5. Sólo si el mapa sobrevive, añadir interacción consentida tarea→control.

La decisión se revisará después de observar ambas UIs reales. Si el usuario
trabaja con grandMA2, se abrirá una variante versionada en vez de reutilizar
silenciosamente este contrato.
