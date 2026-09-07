# PUPILA / LUCIDA — motor local persistente y consumidor LUCIDA

Motor local del ciclo señal → propuesta → decisión → estado → proyección. Reutiliza `CanonicalEventBridge`, `PupilaAdapter`, la vista PUPILA y el plan LUCIDA del experimento 090 mediante importación desde `C:\IA\FARMAXIA`; `app/pupila_engine.py` añade persistencia, orden, consentimiento y ciclo de vida sin modificar ese checkout.

## Ejecutar

Requiere Python 3.10+ en Windows:

```powershell
python -B app\server.py 8765 work\pupila-state.sqlite3
```

Abrir <http://127.0.0.1:8765>. Cerrar con `Ctrl+C`. La app sólo escucha en loopback y no inicia Adobe ni envía comandos.

## Recorrido reproducible

1. El servidor siembra siete eventos sintéticos sólo cuando la sesión no existe.
2. `POST /api/events` ingiere una señal individual; `POST /api/events/batch` conserva el orden recibido y devuelve resultado por elemento (aceptación parcial explícita).
3. `CanonicalEventReplay` reconstruye estados VIZZ/PUPILA desde SQLite; no se confía en estado global en memoria.
4. Las propuestas tienen `proposalId` + `version`; aceptar/rechazar exige sesión, versión y `decisionId` idempotente.
5. Aceptar elimina la propuesta activa de la proyección; revertir una aceptación válida la restaura. Rechazar no se puede revertir.
6. La UI consume el snapshot posterior y muestra el cambio de plan LUCIDA. Ninguna decisión ejecuta una acción Adobe.
7. La frescura usa `source_timestamp` frente a un reloj inyectable; `engine.tick(session_id)` reconcilia silencio/stale y retira propuestas sin inventar actividad mental.

## API mínima

- `GET /api/state?sessionId=pupila-demo` o `GET /api/state?sessionId=pupila-demo&evaluationMs=...` para una previsualización pura en un instante explícito.
- `POST /api/events` con `{event, context, consent}`
- `POST /api/events/batch` con `{events, context, consentByParticipant}`
- `POST /api/consent` con `{sessionId, participantRef, consent}`
- `POST /api/tick` con `{sessionId}` o `{sessionId, evaluationMs}` para materializar vencimientos temporales y publicar una nueva revisión sólo si cambió el estado.
- `POST /api/decision` con `{sessionId, proposalId, proposalVersion, decision, decisionId}`; para revertir, añadir `revertDecisionId` de la aceptación efectiva.

Para medir la ruta incremental frente a replay por evento:

```powershell
python -B app\benchmark_temporal.py
```

Para la aceptación independiente:

```powershell
python -B app\verify_cycle.py
```

La ruta del experimento reutilizado se puede cambiar sin editar código:
`$env:FARMAKSIA_090_ROOT='D:\ruta\al\experimento-090'`. El consumidor VJ se configura en el verificador; la copia falla con un mensaje explícito si una dependencia no existe.

## Evidencia y límites

El seed es `replay` sintético, pero las decisiones, el almacenamiento y la reconstrucción son reales y verificables localmente. No prueba una integración real con Photoshop. El contrato generado conserva `proposal_only`, `reversible`, `blocking=false`, `clickThrough=true` y ausencia de payloads. Los participantes son sintéticos y el replay no demuestra eficacia humana ni coordinación multiusuario remota.

El adaptador de Adobe existente puede integrarse después mediante su bridge explícito; esta carpeta no modifica sus servicios ni sus checkouts.
