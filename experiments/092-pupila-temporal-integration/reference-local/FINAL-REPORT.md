# Informe de verificación

Fecha: 2026-09-06. Estado: motor local persistente y consumidor LUCIDA verificados con replay sintético.

## Comprobado

- Arranque HTTP local y carga de la interfaz.
- Importación y ejecución del replay con el motor real de FARMAKSIA 090.
- Dos participantes aislados por sesión/sala/superficie.
- Duplicado de evento detectado sin aumentar la muestra.
- Propuesta de coordinación generada con aceptación explícita y reversibilidad.
- Proyección LUCIDA sin acciones automáticas, sin payload, no bloqueante y click-through.
- Registro local de aceptar/descartar/revertir.
- Consumidor LUCIDA compatible: 2 participantes, `shared-checkpoint`, 1 actualización aplicada, presupuesto `emit/drop_unchanged/hold_coalesced/emit`, `rawPayloadForwarded=false`.
- SQLite recupera la sesión y conserva el efecto aceptado tras reinicio.
- Reversión efectiva: la proyección pasa de `proposalCount=0` a `proposalCount=1` y el digest/intensidad del plan cambia.
- Cliente HTTP conectado al nuevo contrato: antes 1, aceptar 0, revertir 1.
- Suite nueva: 24 pruebas, incluyendo revocación causal, ruido de puntero, v1→v2, rollback viejo, conflicto de idempotencia, lote parcial, migración, competencia entre dos instancias, stale por silencio, ayuda explícita, vencimiento independiente por hecho, decisión tardía, futuro activable, reloj durable, evaluación explícita, comparación contra oráculo temporal y contrato HTTP.
- Lectura pura: dos snapshots consecutivos no cambian la revisión ni crean filas.
- Coste observado del replay+ingesta por lote: 7 eventos 79.78 ms; 14 205.74 ms; 28 548.26 ms; 56 1665.53 ms. Se conserva como límite conocido del vertical slice; no se cambió semántica para optimizar prematuramente.
- Benchmark mediano de 7 repeticiones: batch/reconcile 73.98 ms vs per-event/reconcile 75.28 ms (1.02x) para 7 eventos; 137.39 vs 173.45 ms (1.26x) para 14; 291.55 vs 419.60 ms (1.44x) para 28; 531.90 vs 1032.22 ms (1.94x) para 56. Esto mide amortización de reconciliación, no una ventaja contra una referencia temporal independiente. La equivalencia de semántica temporal se verifica aparte contra `app/temporal_reference.py`.
- Semántica temporal: `source_timestamp` y reloj de evaluación separados, reloj inyectable sin sleeps, `0 <= edad <= stale_after_ms`, futuros no elegibles, llegadas tardías conservadas como hechos, agenda durable por vencimiento, `active/stale` por participante, stale revoca propuestas y la ayuda conserva identidad/vigencia por solicitud. Pausa sola no genera guía; `decide()` reevalúa antes de aplicar.
- Worker LUCIDA de larga vida: recibe snapshot inicial, cursor/revisión y actualizaciones diferenciales; el ensayo cierra, reinicia y recupera un snapshot invalidado sin reinyectar estado obsoleto.
- SQLite declara `schema_meta.version=3`; la migración añade columnas de soporte, agenda y reloj lógico sin borrar datos y rechaza versiones futuras no soportadas.

## Diferencia frente al baseline

La versión inicial permitía decidir un `proposalId` inventado, trataba `revert` como una entrada de historial y derivaba soporte desde `raw.proposalId`, por lo que un puntero con nuevo ID podía reabrir una propuesta. Esos comportamientos quedaron capturados como casos negativos nuevos: IDs ajenos fallan, rollback viejo entra en conflicto, y el puntero semánticamente equivalente no genera revisión. La comparación histórica es una reproducción del código baseline; la verificación ejecutable actual está en `tests/test_engine.py`.

## No afirmado

No se verificó una acción real en Photoshop, porque esta carpeta no controla ni modifica el entorno Adobe. Tampoco se afirma eficacia humana, sincronización remota, autenticación multiusuario o mejora de curaduría. La rama Adobe no contiene el paquete Python del consumidor; la rama compatible de LUCIDA sí pasó y se conserva como evidencia separada.

## Resultado esperado del ensayo

El fixture produce dos participantes, una propuesta `peer-bridge` y estados de consentimiento por participante. El comando `python -B app\verify_cycle.py` verificó: `1 → accept → 0 → restart → 0 → revert → 1 → nueva evidencia → revisión posterior → revocación → 0`, además de IDs inexistentes, cross-session, versión obsoleta y ausencia de consentimiento. El consumidor VJ aplicó 4 actualizaciones y terminó sin propuesta. La UI hace visible la razón: un participante necesita guía mientras el otro progresa. El host permanece intacto.

## Componentes reutilizados y procedencia

- FARMAKSIA 090: `canonical_event_bridge.py`, `pupila_adapter.py`, `pupila_view.py`, `pupila_lucida_projection.py`, `lucida_render_plan.py`.
- LUCIDA compatible: `C:\IA\VJ`, consumidor de overlay y presupuesto de render.
- Nueva copia/adaptador local: `app/pupila_engine.py`, `app/server.py`, `app/lucida_consumer.py`, `tests/test_engine.py`, `app/verify_cycle.py`.
- No se modificaron los checkouts fuente.

Hashes SHA-256 de la copia local entregada:

- `app/pupila_engine.py`: `9ED212D2B2C559ED73598839BCC5A86845C027EFD5391FD6E9AB3BAE9877C5B4`
- `app/server.py`: `888E6BC86B740C79D882F3124FB3E40EC114FC973D0576C7D7472D8B2DA1570C`
- `app/verify_cycle.py`: `C8238411602804EC7E2C0612D8E67C949AEBFDAF975B70572040C1DE2536E16F`
- `app/lucida_consumer.py`: `6825E8B1259B4FE1F8D51845C95EA8322F9B933A5B18F42A0A0D03FD45E2ABD3`
- `app/benchmark_temporal.py`: `E2BEE0B02DDEF23144DF5815EEE6EC2400669F9E78A9122169CBD7AF3BE24B02`
- `app/temporal_reference.py`: `02988E3FE841AA6D09745AED79742139A4A356F0952FCE0579DD27EB1656D5D4`
- `tests/test_engine.py`: `98D24DEE5A2E98F82705D159E90FC976F6FE4604AA6340EF3D585F162F1F3F7E`
- `tests/test_server.py`: `FDF7E16179A7867A9A27FF5C5856648CFAA7B3D795E977F4091F673BCF3D4789`
