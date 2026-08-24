# Third-party notice — VIZZ 031

This experiment vendors the following open-source runtime assets for a
network-free local browser run:

## `@mediapipe/tasks-vision` 1.0.1

- Copyright: Google LLC and contributors.
- License: Apache License 2.0.
- Source: https://github.com/google-ai-edge/mediapipe
- Package metadata: `vendor/tasks-vision/package.json` was not needed at runtime;
  the pinned package version is recorded in `provenance.json`.

## `onnxruntime-web` 1.29.0

- Copyright: Microsoft Corporation and contributors.
- License: MIT.
- Source: https://github.com/microsoft/onnxruntime
- Bundle: `vendor/ort.webgpu.min.js`.

The application does not load either project from a CDN. License texts and
upstream notices remain the responsibility of the respective projects; this
file records the exact dependency, version, source and license used here.
