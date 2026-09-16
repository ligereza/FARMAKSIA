# Matriz de dependencias 092

| Componente | Uso | Dependencia | Estado |
|---|---|---|---|
| IRIS engine/CLI/server/client/tests/docs | Referencia integrada | Node.js + `package-lock.json` | Sin `node_modules` |
| Adaptador | Mapeo semántico a FARMAKSIA | Python estándar | Portable |
| Contratos | Identidad, orden, procedencia | Python estándar | Offline |
| Datos | Fixture sintético | Sin API ni red | Sin datos humanos |

No hay rutas absolutas, secretos ni salidas generadas. La referencia reinstala
dependencias con `npm ci`.
