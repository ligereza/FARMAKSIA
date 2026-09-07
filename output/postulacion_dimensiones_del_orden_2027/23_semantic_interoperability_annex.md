# Semantic interoperability annex

## Purpose

This annex preserves the broader technical direction without turning the audiovisual application into a commercial software specification. The funded work tests whether a common mathematical state can travel between procedural visuals, LED surfaces and heterogeneous lighting systems.

## Common state

The operator-facing vocabulary is independent of a particular desk:

`phase, tempo, energy, density, direction, topology, palette, transition`

The state is not a universal replacement for fixture channels. It is an intermediate representation. Each adapter declares which dimensions it supports, approximates or cannot express.

## Layout and patch

The installation is represented as a spatial graph. Nodes contain position, fixture profile and capability. Edges contain adjacency, distance or direction. Mapping assigns an observed physical source to a logical node. Patching assigns that logical node to a protocol address and channel schema.

The camera can estimate visible positions, but it cannot infer a DMX address from brightness alone. The robust procedure combines:

- geometric prior: expected line, ring, grid, spiral or controlled irregular pattern;
- projective calibration: homography for a planar arrangement or a calibrated 3D model for depth;
- protocol discovery: RDM when supported;
- active probing: one controlled output change at a time when RDM is unavailable;
- human confirmation when confidence is insufficient.

This is not a promise of universal plug-and-play. It is a measurable route to reduce showfile and patchfile uncertainty.

## Preshow, soundcheck and liveshow

Preshow discovers the scene and produces a layout proposal. Soundcheck tests fixture identity, channel response, timing and safe state. Liveshow freezes the verified mapping and renders semantic states through the available adapters. A wrong or incomplete patch must be recorded as a discrepancy, not silently repaired during live execution.

## Why it belongs to the work

The layout changes the meaning of a sequence. A chase over channel order is not the same as a chase over physical neighbors. A fan based on channel index is not the same as a fan based on vectors and distances. The mapping stage therefore affects the composition, not only the setup labor.

The LED surface is treated as a luminous architecture. It receives the same semantic state as the physical fixtures but may interpret it through pixel density, color, luminance and image formation. The output is not a recorded video placed behind the show; it is a second material expression of the same evolving rule.

## Future transfer

For a commercial or open-source continuation, the same core could target Avolites, grandMA, Resolume, TouchDesigner, Art-Net, sACN, OSC and other backends through separate adapters. For a cultural application, only the controlled backends and the artistic experiment should be promised. The wider interoperability layer remains a transferable result, not an inflated current claim.
