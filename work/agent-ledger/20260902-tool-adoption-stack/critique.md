# Critique packet - 20260902-tool-adoption-stack

previous_action: build the LUCIDA Python engine before preparing domain inputs
selected_action: delegate_narrow_preparatory_contracts
decision_delta: move from sequential engine-first work to parallel domain preparation plus one central integration owner
verification_signal: XIO already has event, replay and capability boundaries; MOSAIK already has host-neutral proposal and overlay projections; both have published replayable tests, but neither is the LUCIDA engine

## Objective

Create a reusable LUCIDA engine without mixing XIO transport, MOSAIK show
semantics, VIZZ perception, PUPILA learning or IRIS document collaboration.

## Strongest failure mode

If the primary agent invents the engine input shape alone, later adapters will
reshape domain data to fit the engine. That creates a clean-looking but wrong
central abstraction and forces rework across private repositories.

## Alternative failure mode

If XIO and MOSAIK receive the complete future projection and are told to keep
working autonomously, they may add unrelated overlays, transports or semantic
features. The visible activity would increase while the integration boundary
gets less reviewable.

## Selected strategy

Give each agent only the contract it owns:

- XIO: event delivery and replay input.
- MOSAIK: show-domain projection and preview input.
- Primary agent: LUCIDA reducer, priority policy, expiry and RenderPlan.
- VIZZ/PUPILA/IRIS: producers remain separate until their concrete contracts
  are needed.

## Prediction

Qualitative confidence is medium-high that this reduces rework. The biggest
remaining risk is not missing tooling; it is semantic leakage between a
signal, a proposal and a rendered surface. The strategy must be reversed if
the two preparatory fixtures cannot be consumed by one reducer without
application-specific branches.

## Next checkpoint

After one published XIO preparation commit and one published MOSAIK
preparation commit, or after the primary engine consumes two synthetic
contracts. Do not poll continuously and do not integrate unverified work.
