# Integration matrix

| Concern | Native FARMAKSIA implementation | Local reference retained | Boundary |
| --- | --- | --- | --- |
| Canonical event validation | 090 `CanonicalEventBridge` | `reference-local/app/server.py` | metadata-only |
| Replay and derived state | 090 `CanonicalEventReplay` + `TemporalCoordinator` | `reference-local/app/pupila_engine.py` | restart rebuild |
| Independent temporal truth | `temporal_reference.py` | `reference-local/app/temporal_reference.py` | no shared cache |
| Consent and revocation | durable participant epochs | local engine/API tests | old epochs invalidated |
| PUPILA projection | 090 `PupilaView` | local `public/app.js` | read-only |
| LUCIDA projection/render budget | 090 projection and render plan | local `app/lucida_consumer.py` | no host action |
| Future relationships | documented only | local docs | IRIS/VIBECODEINE/VJ/WACHUMA not activated |
