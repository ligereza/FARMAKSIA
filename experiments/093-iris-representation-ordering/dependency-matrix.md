# Matriz de dependencias 093

| Componente | Uso | Dependencia | Estado |
|---|---|---|---|
| IRIS engine/CLI/server/client/tests/docs | Referencia portable del frente IRIS | Node.js 18+ y dependencias declaradas en `iris_reference/package.json` | Incluido como referencia aislada |
| Adaptador | Mapeo semántico a FARMAKSIA | Python estándar | Portable |
| Contratos | Identidad, orden, procedencia | Python estándar | Offline |
| Datos | Fixtures de metadata MAK y media demo | Archivos versionados, sin API ni red | IDs/procedencia conservados; sin medios privados |

El experimento Python no depende de Node. La referencia Node es reproducible de
forma independiente desde `iris_reference/`; `node_modules/`, salidas y
trabajo generado están excluidos del control de versiones.
