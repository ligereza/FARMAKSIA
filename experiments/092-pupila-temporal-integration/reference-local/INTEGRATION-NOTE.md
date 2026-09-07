# Nota de integración

## Punto de acople

`app/pupila_engine.py` importa `CanonicalEventBridge`, `CanonicalEventReplay`, `project_pupila_view`, `project_pupila_for_lucida` y `build_lucida_render_plan` desde FARMAKSIA 090. SQLite conserva eventos, consentimientos, propuestas versionadas, decisiones y auditoría. Cada snapshot reconstruye el runtime desde esos datos durables.

El estado de propuesta vigente es el único que cruza a LUCIDA. Las propuestas anteriores quedan `superseded`; una aceptación produce `accepted` y las saca de `pending_proposals`; una reversión válida vuelve a `proposed` y las reintroduce. `reject` queda `rejected` y no es reversible.

El soporte causal no usa IDs de evento como único criterio: se calcula con el tipo de relación, participantes, políticas, foco, cobertura, razón y estados temporales activo/stale. Un puntero nuevo equivalente no crea versión; un cambio de foco/política sí. `source_timestamp` expresa tiempo del evento y el reloj de evaluación es inyectable; sólo `0 <= evaluación - evento <= stale_after_ms` es elegible, por lo que un timestamp futuro no confirma presencia. La llegada tardía puede conservarse como hecho y entra sólo si sigue dentro de la ventana. El silencio sólo vuelve stale la proyección, no se interpreta como inactividad mental. La cache declara `validUntilMs` mediante una agenda durable de expiraciones por hecho; el reloj hacia atrás se acota al último instante evaluado para no revivir decisiones. El replay completo sigue disponible como oráculo.

Las solicitudes `task.help_requested` conservan `event_id` como identidad de petición: dos solicitudes producen dos soportes/propuestas, y cada una caduca por separado. La reconsentimiento inicia una nueva época; hechos de la época anterior no son elegibles. `snapshot()` es lectura pura; `tick()` materializa invalidaciones temporales, y `decide()` reconcilia antes de actuar para que una propuesta vencida no pueda aceptarse por omisión del cliente.

## Adobe / Photoshop

La evidencia local disponible documenta un companion en LUCIDA/ADOBE y un bridge loopback. El vertical slice no afirma que Photoshop esté disponible: trabaja con señales sintéticas declaradas. `app/lucida_consumer.py` ejecuta el `OverlayConsumer` compatible de `C:\IA\VJ` en un worker persistente aislado; la prueba aplica actualizaciones, cierra, reinicia y recupera un snapshot invalidado. Para una prueba con aplicación real, el adaptador debe leer un snapshot validado del bridge y conservar una cola de host separada; la aceptación nunca debe convertirse en ejecución automática.

## Reutilización

IRIS puede consumir el mismo esquema de `context`, `pupila`, `lucida` y `history` para mostrar agrupaciones de archivo, siempre manteniendo procedencia y reversibilidad. La analogía X-ANA-X sólo explica la separación entre relación útil y diferencia; no se usa para inferir estados de personas.

## Procedencia local

La implementación nueva es `app/pupila_engine.py`; el cliente HTTP queda en `app/server.py`. Las pruebas nuevas están en `tests/test_engine.py`, el recorrido completo en `app/verify_cycle.py`, el oráculo temporal en `app/temporal_reference.py` y la medición de amortización en `app/benchmark_temporal.py`. Las funciones FARMAKSIA reutilizadas se identifican en el informe con hash del checkout observado. `FARMAKSIA_090_ROOT` permite cambiar la fuente sin depender de una ruta fija; los ensayos de lectura deben ejecutarse con `python -B`.
