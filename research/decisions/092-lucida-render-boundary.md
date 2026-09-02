# Decision 092 - LUCIDA render boundary

## Question

Can the generic LUCIDA engine consume the existing VJ overlay contract
directly, or should the renderer use a separate contract?

## Observed contracts

| Contract | Role | Owns | Does not own |
| --- | --- | --- | --- |
| `LucidaOverlayView` | projected application state | phase, capabilities, pending proposals, unknowns, attention | final pixels or host execution |
| `LucidaOverlayCursor` and diffs | incremental state delivery | sequence, event identity, cursor recovery | visual layout |
| `RenderPlan` | reducer output | bounded proposal items, priority and expiry | transport, window policy and host state |
| `LucidaOverlayFrame` | generic visual output | visible elements, transparency, click-through and blocking policy | camera, network, host actions |

## Decision

Do not flatten `LucidaOverlayView` into `RenderPlan`. The VJ view carries
state and cursor semantics that are useful to its own consumer. The generic
engine uses this sequence instead:

```text
source adapter -> EngineEvent -> reducer -> RenderPlan -> OverlayFrame -> host renderer
```

`OverlayFrame` is deliberately smaller than the VJ state view. A host adapter
may render it without importing VJ, Resolume or Adobe state. Source-specific
mapping remains in the source repository, as experiment 090 does for VIZZ and
PUPILA.

## Evidence

- LUCIDA `OverlayFrame` validates bounded elements and fixed safety flags.
- `OverlayFrameConsumer` accepts an initial snapshot, exact duplicates and the
  next revision; it rejects stale, skipped or conflicting revisions atomically.
- FARMAKSIA experiment 091 consumes real redacted states from experiment 090,
  reaches a PUPILA render element and applies the next overlay frame.
- No camera, network, GUI or host action is opened by these checks.

## Consequence

The next real renderer can be implemented once, against `LucidaOverlayFrame`,
while XIO, VIZZ, PUPILA and MOSAIK publish source events independently. The
first host implementation should remain read-only and click-through. Input
acceptance, window focus, GPU composition and host-specific permissions need
separate tests.

## Kill tests

- A VJ state field must not enter the generic frame as an unbounded payload.
- An executable item field must be rejected.
- A frame with blocking or automatic actions enabled must be rejected.
- A duplicate revision with identical digest is a no-op.
- A duplicate revision with changed content is a conflict.
- A missing or skipped revision cannot silently update the consumer.
