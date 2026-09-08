# Research 030 - Open source tool adoption stack

Date: 2026-09-02
Status: reviewed
Scope: LUCIDA, RESOLUME, ADOBE, MULTI, XIO, VIZZ, PUPILA and IRIS

## Question

Which mature open source projects can reduce implementation time without
turning FARMAKSIA into a collection of heavy platforms, opaque models or
unverifiable adapters?

## Method

The review used official repositories, official documentation and license
files. Each candidate was evaluated against four tests:

1. Does it remove concrete code that FARMAKSIA would otherwise have to write?
2. Can it sit behind an existing local contract and be replaced later?
3. Can the healthy path remain local, replayable and observable?
4. Are the code, models, assets and transitive dependencies licensed
   separately and clearly enough for the intended distribution?

The review is bounded to runtime surfaces, application adapters, event
transport, local analysis, perception and semantic assistance. It does not
select a general autonomous computer agent, a corpus or a cloud service.

## Main finding

The useful shortcut is not one universal engine. It is a small stack of
specialized components:

```text
application output or signal
    -> local adapter
    -> FARMAKSIA contract
    -> replay and verifier
    -> LUCIDA surface or offline analysis
```

Large components should carry bytes or provide algorithms. They must not own
the meaning of a claim, the authorization of an action, the provenance ledger
or the final `verified` decision.

## Candidate matrix

| Component | Concrete saving | Best boundary | License | Decision |
|---|---|---|---|---|
| Spout2 | Shares GPU textures between Windows applications, avoiding a second render of the same Resolume composition | LUCIDA/RESOLUME visual input | BSD-2-Clause | **Adopt next for a same-PC pilot** |
| `websockets` | Removes custom WebSocket framing, reconnect and protocol code from a Python LAN adapter | XIO transport client/server | BSD-3-Clause | **Adopt when real LAN transport is enabled** |
| `ws` or native browser `WebSocket` | Provides the Electron-side event channel without inventing a protocol | LUCIDA/MULTI client | MIT for `ws`; native API has no third-party dependency | **Use the native API first; keep `ws` for the Node side** |
| CloudEvents | Gives XIO and LUCIDA a known event envelope and interoperability vocabulary | Event envelope only | Apache-2.0 specification/project | **Already adopted conceptually; keep the FARMAKSIA payload contract** |
| DuckDB | Turns JSONL/session evidence into local SQL analysis without a database server | XIO/FARMAKSIA read-side analytics | MIT | **Adopt for analysis, not as the source log** |
| JSON Schema / `jsonschema` | Replaces repeated shape checks at cross-repository boundaries | Contract gate and fixtures | MIT | **Use as a schema gate; keep semantic invariants in local code** |
| scikit-learn | Supplies tested Ridge, split, metrics and validation primitives for VIZZ calibration | Offline calibration and evaluation | BSD-3-Clause | **Adopt offline first; never use as the live GPU tracker** |
| MediaPipe Face Landmarker | Provides an established local face/eye landmark front end instead of hand-writing landmark extraction | VIZZ feature adapter | Apache-2.0 code; model terms must be checked separately | **Conditional GPU pilot** |
| ONNX Runtime | Runs a small learned mapper through explicit execution providers | VIZZ model adapter | MIT code; model license is separate | **Conditional GPU pilot** |
| OpenCV | Supplies camera geometry, calibration and projection routines | VIZZ geometry adapter | Apache-2.0 | **Use where the existing geometry contract needs it** |
| pywinauto | Reads Windows UI Automation/Win32 context rather than reverse-engineering every desktop surface | PUPILA/VIZZ read-only UI adapter | BSD-3-Clause | **Already present as a bounded adapter** |
| NetworkX | Removes custom path and graph algorithm code for PUPILA relation graphs | PUPILA offline graph analysis | BSD-3-Clause | **Conditional when the graph outgrows local structures** |
| spaCy | Supplies tokenization, tagging and local NLP pipeline pieces for manuals and tutorials | PUPILA document adapter | MIT code; language models have separate terms | **Conditional; no model download by default** |
| Yjs | Supplies CRDT merge and offline collaboration primitives for shared documents | IRIS/PUPILA shared editable state | MIT | **Conditional for real concurrent editing, not telemetry** |
| NATS JetStream | Supplies durable publish/subscribe, replay and retention for many nodes | XIO distributed transport | Apache-2.0 server | **Future scale option; too much for the first LAN slice** |
| Electron Forge | Packages the already-working Electron companion into distributables | LUCIDA release pipeline | MIT | **Adopt before distribution, not before current runtime stabilization** |
| Tauri | Offers a lighter desktop shell for a future measured resource problem | LUCIDA alternate host | MIT/Apache-2.0 components | **Do not migrate now; only revisit after a benchmark** |
| pluggy | Provides a small hook-based Python plugin registry | Python-side extension host | MIT | **Reference/conditional; current registries remain simpler** |
| OBS/libobs | Demonstrates mature source/output/encoder plugin boundaries | Architecture reference for media hosts | GPL-2.0+ | **Reference only; do not embed in LUCIDA** |

## Why the first five matter most

### 1. Spout2 is the best RESOLUME shortcut

Resolume documents composition output, virtual outputs and Spout/Syphon
texture sharing. The same-computer path lets LUCIDA receive a GPU texture
instead of decoding a second video stream or rendering a duplicate composition.
This directly addresses the request for a preview layer that does not gamble
with the live output.

The first adapter must be read-only:

```text
Resolume composition -> Spout sender -> LUCIDA preview surface
```

It must not send cues, alter Advanced Output or become a hidden control path.
NDI remains a cross-machine option only after a bandwidth and latency test;
Resolume documents approximately 150 Mbps as a typical minimum for 1080p60,
which is a different resource problem from local texture sharing.

### 2. WebSocket is the appropriate first XIO transport

XIO already owns event identity, timestamps, replay, deduplication and
capability boundaries. A mature WebSocket library can replace socket framing,
connection lifecycle and backpressure plumbing without replacing those
contracts.

The division should remain:

```text
XIO: event identity, permissions, replay and transport policy
WebSocket: bytes on one connection
LUCIDA: local rendering and user-visible state
```

No raw camera frames, PSDs, audio or screen captures should travel through
this channel by default.

### 3. DuckDB is a read-side accelerator, not a new source of truth

XIO's append-only JSONL evidence remains the authoritative replay input. A
DuckDB database can be rebuilt from that log to answer questions such as:

- which signals arrived before a visible state change;
- where two peers diverged;
- which proposals were exposed, accepted, rejected or left unknown;
- how often a surface changed without a new event.

This saves hand-written aggregation code while preserving recovery: deleting
the derived database does not delete the evidence.

### 4. scikit-learn is the VIZZ calibration shortcut

For the current sample sizes, the useful baseline is Ridge/affine regression,
grouped validation and explicit metrics. scikit-learn provides those tested
primitives. It is an offline analysis dependency, not a promise that a CPU
pipeline can track eyes live or that a model is medically meaningful.

The acceptance gate remains FARMAKSIA's own:

```text
session-held-out test
+ target/trajectory grouping
+ P95 and coverage
+ latency and UNKNOWN rate
+ no silent CPU fallback
```

### 5. MediaPipe plus ONNX Runtime is a two-stage VIZZ path

MediaPipe can provide face/eye landmarks and ONNX Runtime can execute a small
mapper using an explicit GPU execution provider. Their roles must not be
collapsed:

```text
camera frame -> landmarks and pose -> normalized features -> gaze/representation mapper
```

The adapter must report the actual execution provider, model hash, input
shape, frame rate and fallback state. A GPU option selected in configuration
does not count as GPU execution. If the provider is unavailable or nodes fall
back to CPU beyond the thermal budget, the runtime must stop or enter the
declared safe mode.

## Layer assignment

| Product or repo | Adopted external help | What remains ours |
|---|---|---|
| LUCIDA core | Electron now; Electron Forge later; native `WebSocket` or `ws` | Surface lifecycle, transparency, click-through policy, proposal rendering and consent |
| LUCIDA/RESOLUME | Spout2 first; Resolume Spout/virtual-output contract | Preview identity, no-action boundary, GPU budget and acceptance checks |
| LUCIDA/ADOBE | Existing Electron companion; optional Forge packaging | Local catalog, preview, drag/drop, bridge permissions and no silent edits |
| LUCIDA/MULTI | WebSocket client; CloudEvents-shaped envelope | Peer identity, capability, redaction, revision and replay semantics |
| XIO | `websockets` first; NATS only at scale; DuckDB read side | Event source registry, timestamps, deduplication, persistence policy, auth and replay |
| VIZZ | MediaPipe/OpenCV/ONNX Runtime conditionally; scikit-learn offline | Calibration contract, camera/monitor geometry, GPU gate, uncertainty and UNKNOWN policy |
| PUPILA | pywinauto already; NetworkX/spaCy conditionally | Relation mapping, analogy evidence, user control, provenance and learning outcomes |
| IRIS | Yjs only for actual concurrent document editing | Portfolio model, provenance, export, ownership and conflict review |

## License and provenance rule

The license of a repository is only the first row of the inventory. Before a
component is distributed, record:

```text
component name
repository and commit/tag
direct license
transitive licenses
models and weights
assets, fonts and icons
runtime downloads
telemetry and network behavior
replacement path
```

This matters especially for MediaPipe and spaCy: permissive code does not
automatically make every model, language package or asset permissive. It also
matters for Spout2 bindings: the core SDK and a third-party language binding
must be audited separately.

## What is not being adopted

- No Hugging Face weights or datasets.
- No general computer-use agent, VLM or autonomous action loop.
- No NATS server in the first XIO LAN implementation.
- No Tauri migration while Electron/ADOBE is working.
- No CRDT for ordered show telemetry or audit logs.
- No OBS/libobs embedding because its GPL boundary is incompatible with the
  current reusable core.
- No dependency is installed merely because its license is permissive.

## Stopping rule

This research stops when every requested layer has a concrete candidate,
license status, integration boundary and kill test. More repositories would
mostly add alternatives rather than change the first implementation decision.
The next evidence should therefore be a small performance and integration
fixture, not another catalog.

## Sources

- [Spout2](https://github.com/leadedge/Spout2)
- [Resolume Spout/Syphon](https://resolume.com/support/en/6/syphonspout)
- [Resolume NDI](https://resolume.com/support/en/NDI_inputs_and_outputs)
- [Python websockets](https://github.com/python-websockets/websockets)
- [Node ws](https://github.com/websockets/ws)
- [CloudEvents specification](https://github.com/cloudevents/spec)
- [DuckDB](https://github.com/duckdb/duckdb)
- [jsonschema](https://github.com/python-jsonschema/jsonschema)
- [scikit-learn](https://github.com/scikit-learn/scikit-learn)
- [MediaPipe](https://github.com/google-ai-edge/mediapipe)
- [ONNX Runtime](https://github.com/microsoft/onnxruntime)
- [OpenCV](https://github.com/opencv/opencv)
- [pywinauto](https://github.com/pywinauto/pywinauto)
- [NetworkX](https://github.com/networkx/networkx)
- [spaCy](https://github.com/explosion/spaCy)
- [Yjs](https://github.com/yjs/yjs)
- [NATS JetStream](https://github.com/nats-io/nats.docs/blob/master/nats-concepts/jetstream/README.md)
- [Electron Forge](https://github.com/electron/forge)
- [Tauri](https://github.com/tauri-apps/tauri)
- [pluggy](https://github.com/pytest-dev/pluggy)
- [OBS Studio](https://github.com/obsproject/obs-studio)
