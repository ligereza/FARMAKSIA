# NEXT — open work, observations, suggestions

Updated after the 2026-09-13 suite audit. This file is not a contract and
nothing in it overrides `AGENTS.md`, `RESEARCH_LOOP.md` or a decision in
`research/decisions/`.

## Decisions that are the author's, not an agent's

**What `SUITE_VALID` means off Windows.** Experiments 076 to 080 drive real
Windows applications through UI Automation, Excel or COM. `run_suite.py` now
records those unavailable steps as platform-gated skips while continuing their
portable kill tests and provenance checks. The terminal marker therefore means
"everything runnable on this platform passed"; the output retains the exact
Windows-only steps that were not exercised.

**Whether experiment 042 belongs in the suite.** Its README calls it a
historical prototype superseded by 044, and it appears nowhere in
`run_suite.py`. Its manifest is now validated by `unlisted_provenance`, so it
cannot rot unnoticed, but its code is still never exercised.

## Pending, mechanical

**The provenance list is positional.** `run_suite.py` holds 88 paths and every
check reaches them by index, `provenance[N]`. Deleting the six out-of-scope
entries would shift every later index, which is why absence was declared rather
than removed. Migrating to lookup by directory prefix was planned and audited
but never executed: the audit that must precede it checks, for every
`command("provenance NNN", ..., provenance[M])`, that the path at index `M`
really lives under `NNN`. If a single pair is misaligned, stop and report --
rewriting on top of a wrong pairing would freeze it as if correct.

**The 2026-09-13 Linux run is green with declared scope.** With the isolated
OpenCV dependency, `research/tools/run_suite.py` reaches `SUITE_VALID`: 076–080
are recorded as Windows-only skips, their portable kill tests and provenance
checks pass, 081–083 pass locally, and 084–089 remain declared out of scope.

**One historical shadow copy is still unrecoverable.** The manifest entry for
`plataforma__providers.py.before-projection-20260821` names the expected
SHA-256, but the file is absent. Current and rollback provider files were
checked and do not match; do not substitute either one. The archive contract
now records this as an explicit incomplete recovery audit, while the five
available copies remain hash-checked.

**The root language ratchet is clean after the XIO admission pass.** The
untracked XIO files were reviewed, comments/docstrings were translated where
they belonged to active code, and private test identifiers were made English
without changing public payload keys or routes. The direct meter now reports no
new Spanish comments or identifiers; future untracked additions remain subject
to the same gate.

**`results.md` in 042 reports a Tkinter GUI smoke** (`VIZZ_042_GUI_SMOKE_VALID`)
that no checked-in script reproduces; only the headless contract test is
present. Either write the smoke or mark that line unreproducible. The dated
record was left as written rather than edited after the fact.

**`_AbsentModule` lives in `pretrained_gaze.py`** and is imported from
`gpu_tracker.py`. That was chosen over duplicating it, because the import edge
already existed. If a third module needs it, it should move somewhere that is
not an ONNX adapter.

## Observations

The pin dropped from experiment 018 is worth remembering as a shape: it hashed
`research/tools/run_suite.py`, a file that grows with every experiment added,
so the record was guaranteed to rot for unrelated reasons. Experiment 019 pins
`validate_provenance.py` and that pin was kept, because it only moves when
someone edits the validator deliberately -- which is exactly when 019 should be
re-examined. A frozen hash is worth keeping when its target changes for reasons
that concern the experiment, and not otherwise.

`research/handoffs/002` records `XIO_LAYER` duplicated into LUCIDA's `MULTI`
branch, with the measurement but not the consolidation. The open question there
is not technical: what the multi-user consumption frontier should be, if it is
not the transport.

## Not audited

The logic of the 83 experiments beyond their provenance and whatever the suite
exercises. The content of `research/decisions/` and `research/literature/`.
Experiments 090 and 091. `requirements.txt` covers NumPy and headless OpenCV;
ONNX Runtime is optional and the Windows automation packages are named but not
installed, and none of that was tested on Windows.
