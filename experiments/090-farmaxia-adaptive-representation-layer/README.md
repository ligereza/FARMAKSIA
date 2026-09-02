# Experimento 090 — Capa adaptativa VIZZ/PUPILA derivada de ZIGO

## Propósito

Este experimento toma del proyecto histórico ZIGO la estructura reutilizable de
contexto → análisis → propuesta → autorización → resultado → auditoría, pero la
implementa como un slice local y aislado dentro de FARMAKSIA. No copia obras,
assets, modelos, credenciales ni datos del repositorio SVG.

La diferencia funcional es deliberada:

- **VIZZ** convierte señales consentidas de una superficie en una política de
  representación: `quiet`, `anchor`, `guide` o `support`. Es una sugerencia de
  renderizado, no una medición de la mente, la comprensión ni la mirada.
- **PUPILA** recibe estados VIZZ de varios participantes y hace emerger una
  propuesta de coordinación: `peer-bridge`, `shared-checkpoint` o
  `co-presence`. No envía mensajes ni ejecuta acciones automáticamente.
- Una persona sólo entra a la sala PUPILA después de una señal consentida;
  una ausencia de señal no se interpreta como presencia autorizada.

Ambos describen una ventana `transparent-popup`, no una ventana real. En este
primer slice es deliberadamente no bloqueante y click-through; la integración
con una aplicación concreta vendrá después de fijar permisos y transporte.

## Flujo

```text
señal consentida
       ↓
contrato metadata-only
       ↓
VIZZ: política visual local
       ↓
PUPILA: diferencia entre participantes
       ↓
propuesta emergente reversible
       ↓
aceptación explícita (fuera de este slice)
```

## Puente de eventos canónicos

`canonical_event_bridge.py` permite que XIO entregue un evento de aplicación a
VIZZ/PUPILA sin acoplar el experimento a la implementación de XIO. El puente
valida el sobre, conserva la procedencia y transforma sólo un resumen
metadata-only. Nunca copia el `payload` completo: conectividad se convierte en
`presence`, teclado conserva sólo `count` y `shortcut`, y las demás señales
usan campos acotados.

El `event_id` externo es idempotente por `session_id`, `peer_id` y `surface_id`.
PUPILA mantiene además esas tres dimensiones separadas, por lo que dos
sesiones con el mismo `room_id` no se mezclan.

`CanonicalEventReplay` permite reproducir una secuencia de eventos en memoria
y devuelve conteos de aceptados, bloqueados y duplicados junto con el estado
final VIZZ/PUPILA. Cada resultado también incluye `pupilaView`, la proyección
acotada que consumiría una superficie transparente, y el replay la expone como
`finalPupilaView`. No es todavía un transporte de red ni un ejecutor de
acciones.

El replay también entrega `interactionMetrics`: conteos por estado y tipo de
señal, más la última política VIZZ observable por participante. Incluye sólo
metadata acotada de `pointer`, `keyboard`, `focus` y otras señales aceptadas;
nunca conserva texto, coordenadas crudas ni payloads.

Cada resultado incluye `pupilaViewDiffs`, una secuencia determinista de cambios
entre vistas PUPILA consecutivas. Un consumidor puede actualizar sólo los
campos modificados y un duplicado produce un diff vacío; el primer elemento
queda marcado como inicial y no inventa un cambio previo.

`pupila_view.py` proyecta el estado compartido a una superficie compacta para
la futura capa transparente. Ordena participantes y propuestas, limita lo que
se muestra y excluye activity scores, hashes internos, payloads y acciones.
Cada participante puede exponer sólo un resumen de interacción con cantidad
acotada y tipos de señal observados; no expone las coordenadas, el texto ni el
contenido original.
El estado vacio produce una atencion `waiting`, no una accion automatica.
`diff_pupila_view` compara dos proyecciones ya redactadas y devuelve sólo los
cambios seguros, con orden y limite deterministas; no acepta estados internos
ni añade un canal de acciones.

## Qué se adopta de ZIGO

- envelopes versionados y hashes deterministas;
- normalización de contexto incompleto;
- estado separado del cliente visual;
- propuestas explícitas, reversibles y no ejecutables;
- auditoría encadenada y replay offline;
- límites locales sin shell, credenciales ni captura cruda.

## Qué no se adopta todavía

- Electron, UXP, Blender, TouchDesigner o un host específico;
- captura de pantalla o video;
- texto de teclado, contenido de documentos o biometría;
- sincronización remota, cuentas o base de datos;
- inferencia psicológica, rendimiento o aprendizaje.

## Ejecución

Desde `C:\IA\FARMAXIA`:

```powershell
.\.venv\Scripts\python.exe experiments\090-farmaxia-adaptive-representation-layer\run_contract_test.py
.\.venv\Scripts\python.exe experiments\090-farmaxia-adaptive-representation-layer\run_demo.py
.\.venv\Scripts\python.exe experiments\090-farmaxia-adaptive-representation-layer\run_xio_cross_branch_check.py
```

Para verificar el envelope de transporte exacto de LUCIDA/MULTI, ejecutar el
cuarto comando con un checkout local de esa rama:

```powershell
.\.venv\Scripts\python.exe experiments\090-farmaxia-adaptive-representation-layer\run_lucida_multi_check.py --lucida-multi-root C:\IA\LUCIDA
```

Ese comando requiere que la ruta indicada contenga `XIO_LAYER` de la rama
`MULTI`; no cambia ramas ni abre sockets.

El flujo de selección y handoff de XIO se verifica con:

```powershell
.\.venv\Scripts\python.exe experiments\090-farmaxia-adaptive-representation-layer\run_xio_route_handoff_check.py
```

El chequeo exige una ruta coincidente, selecciona el adaptador explícitamente,
redacta el payload mediante una allowlist, conserva el envelope de
`application-event` y sólo prepara el handoff. No entrega ni ejecuta acciones.
El mismo handoff preparado se reproduce después en VIZZ/PUPILA y termina en
una vista de participante; la señal queda clasificada como `task` porque el
contrato universal no inventa que un OSC genérico sea foco, puntero o teclado.

El mismo chequeo prepara además dos handoffs de participantes distintos en la
misma sala y superficie. El replay conserva ambos participantes, genera la
propuesta `co-presence` y entrega el diff de la segunda vista. Esto prueba la
coordinación de la capa multi sin fingir que un evento OSC genérico contiene
significado de foco, comprensión o rendimiento.

Los tests son offline y no abren ventanas, cámaras, aplicaciones externas ni
procesos de usuario. El tercer comando genera un evento de conectividad con los
contratos reales de XIO y lo reproduce junto con `focus`, `pointer` y
`keyboard`, incluyendo un duplicado. Verifica la frontera completa sin abrir
red.

## Kill tests

- una señal sin consentimiento no entra al estado;
- el texto de teclado no se persiste;
- VIZZ no necesita cámara para producir una política básica;
- PUPILA no acepta estados de otra sala;
- una propuesta no contiene una acción ejecutable;
- alterar un evento rompe la cadena de auditoría;
- un evento canónico duplicado no aumenta muestras;
- un evento canónico sin consentimiento no se registra;
- una sesion distinta no hereda participantes de otra sesion;
- el diff de PUPILA no acepta payloads ni altera la frontera read-only;
- la capa no bloquea ni captura el input de la aplicación.

## Siguiente hito

Conectar el fixture de dos participantes a un envelope compartido de
LUCIDA/MULTI y probar su consumo host-neutral. La ventana transparente y el
transporte real quedan fuera hasta demostrar autenticación, no bloqueo,
cancelación y reversibilidad.
