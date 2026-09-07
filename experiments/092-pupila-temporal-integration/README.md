# Experimento 092 - Integracion temporal PUPILA/LUCIDA

This experiment adds a durable temporal shell to the native FARMAKSIA 090
adaptive representation layer. Facts are stored in SQLite; every view is
reconstructed by replay through `CanonicalEventBridge` and
`CanonicalEventReplay`. The shell does not become a second PUPILA semantic
engine.

The coordinator provides:

- a durable monotonic logical clock and explicit, pure snapshots;
- event eligibility by activation, freshness and consent epoch;
- facts separated from derived PUPILA state and LUCIDA projection;
- idempotent proposal decisions and explicit effective reversion records;
- restart-safe reconstruction from the event ledger;
- a read-only, proposal-only, click-through LUCIDA render boundary.

LUCIDA remains a projection only. It performs no host action, captures no
input and receives no raw payload. IRIS and VIBECODEINE remain future source
orchestration boundaries; VJ/LUCIDA remains a future renderer boundary; and
WACHUMA remains a future transport or operational boundary.

Run the focused acceptance check:

```powershell
python experiments/092-pupila-temporal-integration/run_integration.py
```

The local PUPILA/LUCIDA workspace is retained under `reference-local/` as a
labelled source/reference snapshot. It is not imported as runtime code.
