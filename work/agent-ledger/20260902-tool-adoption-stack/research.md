# Research ledger - 20260902-tool-adoption-stack

run_id: 20260902-tool-adoption-stack
objective: Identify mature open source components that reduce FARMAKSIA implementation time while preserving local contracts, provenance, replay, permissions and replaceability.
scope: LUCIDA surfaces, XIO event fabric, VIZZ perception/calibration, PUPILA semantic assistance, IRIS shared state and release tooling.
state_machine: FRAME -> MAP_CONCEPTS -> SEARCH -> REGISTER_SOURCES -> EXTRACT_CLAIMS -> TEST_MODELS -> SYNTHESIZE -> DECIDE -> LOG_GAPS
status: complete

## Frame

The question was narrowed to components that can be adopted without importing
a general autonomous agent, arbitrary corpus, opaque cloud dependency or
unmeasured resource cost. Existing FARMAKSIA, XIO, MOSAIK/VJ and LUCIDA
contracts remain authoritative.

## Decision criteria

- concrete implementation saving;
- permissive or clearly reviewable license;
- local operation and offline replay;
- explicit failure/fallback behavior;
- contract boundary and replacement path;
- no accidental transfer of raw camera, screen, audio or document payloads.

## Sources

| source_id | source | evidence |
|---|---|---|
| OA-001 | https://github.com/leadedge/Spout2 | Windows GPU texture-sharing SDK; BSD-2-Clause |
| OA-002 | https://resolume.com/support/en/6/syphonspout | Resolume same-computer Spout/Syphon texture sharing and virtual output |
| OA-003 | https://resolume.com/support/en/NDI_inputs_and_outputs | NDI is a network video option with materially higher bandwidth cost |
| OA-004 | https://github.com/python-websockets/websockets | Python WebSocket implementation; BSD-3-Clause |
| OA-005 | https://github.com/websockets/ws | Node WebSocket implementation; MIT |
| OA-006 | https://github.com/cloudevents/spec | Standard event envelope project; Apache-2.0 |
| OA-007 | https://github.com/duckdb/duckdb | Embedded analytical database; MIT |
| OA-008 | https://github.com/python-jsonschema/jsonschema | JSON Schema validation; MIT |
| OA-009 | https://github.com/scikit-learn/scikit-learn | ML and validation primitives; BSD-3-Clause |
| OA-010 | https://github.com/google-ai-edge/mediapipe | Local perception framework; Apache-2.0 code, model terms separate |
| OA-011 | https://github.com/microsoft/onnxruntime | Inference runtime with explicit execution providers; MIT code |
| OA-012 | https://github.com/opencv/opencv | Camera calibration and geometry routines; Apache-2.0 |
| OA-013 | https://github.com/pywinauto/pywinauto | Windows UI Automation/Win32 adapter; BSD-3-Clause |
| OA-014 | https://github.com/networkx/networkx | Graph algorithms and graph data structures; BSD-3-Clause |
| OA-015 | https://github.com/explosion/spaCy | Local NLP pipeline; MIT code, model terms separate |
| OA-016 | https://github.com/yjs/yjs | CRDT collaboration engine; MIT |
| OA-017 | https://github.com/nats-io/nats.docs/blob/master/nats-concepts/jetstream/README.md | Persistent/replayable messaging and retention |
| OA-018 | https://github.com/electron/forge | Electron packaging and distribution; MIT |
| OA-019 | https://github.com/tauri-apps/tauri | Alternate desktop shell; MIT/Apache-2.0 components |
| OA-020 | https://github.com/pytest-dev/pluggy | Hook-based plugin system; MIT |
| OA-021 | https://github.com/obsproject/obs-studio | Mature plugin boundary reference; GPL-2.0+ |

## Claims

| claim_id | source_ids | claim | status | confidence |
|---|---|---|---|---|
| C-001 | OA-001, OA-002 | Same-PC Resolume preview can use shared GPU textures instead of a duplicate video/render path. | supported | high |
| C-002 | OA-003 | Cross-PC video transport has a separate bandwidth/latency cost and should not be confused with XIO metadata transport. | supported | high |
| C-003 | OA-004, OA-005 | Mature WebSocket libraries can provide connection plumbing while XIO retains event identity and policy. | supported | high |
| C-004 | OA-006 | CloudEvents provides a common envelope but does not validate semantic truth or authorization. | supported | high |
| C-005 | OA-007 | DuckDB can accelerate rebuildable local analysis without replacing the append-only evidence log. | supported | high |
| C-006 | OA-008 | JSON Schema can reduce repeated shape validation, but semantic invariants remain local. | supported | high |
| C-007 | OA-009 | scikit-learn is a suitable offline baseline for Ridge, grouped evaluation and metrics; it is not a live GPU tracker. | supported | high |
| C-008 | OA-010, OA-011, OA-012 | VIZZ can be decomposed into perception, geometry and learned mapping adapters with explicit provider reporting. | compatible | medium-high |
| C-009 | OA-013 | Read-only UI Automation can supply desktop context without assuming that a click means comprehension. | compatible | high |
| C-010 | OA-014, OA-015 | PUPILA may use graph and NLP libraries conditionally, but models/assets need independent provenance. | compatible | medium |
| C-011 | OA-016 | Yjs fits shared editable IRIS/PUPILA state, not ordered XIO telemetry or an audit ledger. | compatible | high |
| C-012 | OA-017 | NATS JetStream supplies durable replay and retention, but its operational cost exceeds the first local/LAN slice. | supported | high |
| C-013 | OA-018, OA-019 | Packaging and shell migration are release decisions, not reasons to disturb a working Electron runtime now. | compatible | high |
| C-014 | OA-020, OA-021 | Plugin boundary references are useful, but the current local registries and license boundaries should be preserved. | compatible | high |

## Model comparison

| option | saving | risk | decision |
|---|---|---|---|
| import one universal agent platform | apparent speed | opaque actions, model/data licenses, weak verification | reject |
| build every transport/render/ML primitive locally | control | repeats mature code and delays user-visible result | reject |
| adopt narrow components behind FARMAKSIA contracts | measurable saving and replaceability | integration and license bookkeeping | select |

## Chosen order

1. Spout2 same-PC preview fixture.
2. WebSocket XIO LAN adapter after authentication/cancellation contract.
3. DuckDB read-side analysis over JSONL.
4. scikit-learn offline calibration.
5. MediaPipe/OpenCV/ONNX Runtime GPU fixture.

## Gaps

- Spout2 integration latency and GPU memory on the target machine are not yet measured.
- No live XIO network authentication, expiry or cancellation path has been accepted.
- Model and asset licenses for any future perception/NLP weights remain unregistered.
- VIZZ GPU provider availability must be measured on the actual hardware; configuration alone is insufficient.
- The current worktree contains unrelated user changes and was not modified by this research.

## Stopping rationale

Every requested layer has at least one concrete candidate, license status,
integration boundary, adoption status and failure condition. Further catalog
search is unlikely to change the first pilot order; the next information gain
comes from a measured fixture.

## Repository impact

This run added only research and decision records under FARMAXIA. No external
dependency was installed, no product repository was modified and no model or
dataset was downloaded.
