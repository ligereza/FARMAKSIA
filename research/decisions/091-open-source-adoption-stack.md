# Decision 091 - adopt open source pieces by layer

Date: 2026-09-02
Status: proposed
Scope: LUCIDA, XIO, VIZZ, PUPILA and IRIS

## Decision

FARMAKSIA will adopt external projects only behind a local contract and only
when the project removes a measured implementation burden. The first adoption
order is:

1. Spout2 for a same-machine LUCIDA/RESOLUME preview pilot.
2. WebSocket transport (`websockets` for Python and native `WebSocket`/`ws`
   for the Electron side) for a real XIO LAN adapter.
3. DuckDB as a rebuildable read-side view over XIO JSONL evidence.
4. scikit-learn for offline VIZZ calibration and grouped evaluation.
5. MediaPipe, OpenCV and ONNX Runtime only after an explicit GPU fixture
   reports the actual execution provider and thermal/latency budget.

CloudEvents and `jsonschema` remain envelope/schema aids, not authorities for
semantics. pywinauto remains a read-only Windows surface adapter. NetworkX,
spaCy, Yjs, NATS JetStream, Electron Forge and pluggy remain conditional.

## Why this is the best shortcut

It removes code in the places where mature libraries are unusually strong:
texture sharing, protocol plumbing, SQL aggregation, regression/evaluation,
landmarks and inference. It does not outsource the hard part of FARMAKSIA:
deciding what a signal means, which surface it belongs to, whether a proposal
is authorized, how it can be replayed and whether an outcome is verified.

## Acceptance gates

An external component may enter a runtime branch only if all are true:

- an adapter contract names its input, output, permissions and shutdown;
- a fixture demonstrates the concrete saving;
- the source, version/tag and license are recorded;
- models, assets and transitive dependencies have separate provenance;
- the path can be replayed without the component or reports the dependency;
- a kill test catches wrong surface identity, fallback, stale data or unsafe
  side effects;
- a minimal replacement path remains possible.

## Immediate non-actions

No dependency is installed in this research cycle. The next implementation
should be one measured pilot, selected by risk:

```text
same-PC Resolume texture preview
    before LAN transport
    before distributed storage
    before live eye-tracking inference
```

That order gives the largest user-visible gain with the smallest chance of
disturbing the working Adobe companion or the existing XIO replay contracts.

## Rejected shortcuts

- A general agent is not a substitute for surface adapters and verifiers.
- NATS is not justified until multiple nodes need durable independent replay.
- Yjs is not an event ledger; it belongs to shared editable state.
- Tauri is not a free performance win; migration must follow a benchmark.
- A permissive library license does not clear its models, data, assets or
  trademarks.

## Evidence record

See [Research 030](../literature/030-open-source-tool-adoption-stack.md).
