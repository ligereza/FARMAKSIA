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
final VIZZ/PUPILA. No es todavía un transporte de red ni un ejecutor de
acciones.

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

Los tests son offline y no abren ventanas, cámaras, aplicaciones externas ni
procesos de usuario. El tercer comando importa sólo los contratos locales de
XIO para probar la frontera real; no abre red.

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
- la capa no bloquea ni captura el input de la aplicación.

## Siguiente hito

Añadir un replay de señales de interacción `pointer`, `keyboard` y `focus`
alimentado por el evento canónico, primero en modo observador. La ventana
transparente y el transporte real quedan fuera hasta demostrar autenticación,
no bloqueo, cancelación y reversibilidad.
