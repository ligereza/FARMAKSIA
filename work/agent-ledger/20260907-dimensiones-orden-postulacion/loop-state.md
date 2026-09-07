# Autonomous loop state

## Consolidation and delegation - 2026-09-07

Role: primary_agent. User authorized up to two LUNA subagents at medium effort,
consolidation of existing Markdown only, scoped FARMAKSIA push, inspection of MAK
and implementation of capabilities needed by the application. No new Markdown.
The current action supersedes earlier next-action sections below.

- D1: consolidate only dossier Markdown, classify current/historical/alternative
  documents, link replacements in both directions and correct internal conflicts.
  Acceptance: no new Markdown, no broken local links, clear current proposal and
  factual/proposed distinction. No Git, source-media or remote mutations.
- D2: read-only SSH inventory of Claude's latest repo notes and relevant code in
  MAK; return paths, branch/commit/dirty state, observed vs recalled claims and
  one bounded implementation candidate. No remote writes, checkout or fetch.
- Primary: protect public/private boundary, prepare scoped commit/push, integrate
  evidence and assign a separate code slice after inventory. Review deliverables
  once against their acceptance conditions; do not re-read agent conversation.

delegation_scope: dossier consolidation and remote evidence inventory
delegation_authority: explicit_user_request
nested_delegation: disabled
expected_review_boundary: changed-file summary, local links, selected diff and
one functional test per implemented capability
cost_estimate: lower context/review cost than reading every repository in the
primary agent; no numerical saving is claimed before observing the result
observed_review_cost: one compact D2 result reviewed; branches and function paths
identified without re-reading each remote repository in the primary agent

D1 completed the 29-file Markdown consolidation with relative-link checks.
One focused review caught two remaining translation/page-count inconsistencies;
D1 corrected them and recalculated the FUP block lengths. Existing dossier PDF
derivatives were rebuilt and the full local package check passed. The public
checkout uses `-DocumentsOnly` because private media is intentionally excluded.
No claim of official submission follows from either check.

### Latest remote inventory (read-only)

LUNA D2 verified SSH to MAK and the following clean checkouts: FARMAKSIA
`fix/provenance-integrity` at `779ccd6`; VIZZ `fix/readme-honesty` at `0e72bf0`;
PUPILA `fix/ambiguity-consistency` at `8e92179`; XIO `fix/tests-and-scope` at
`e6f6787`; LUCIDA `docs/next` at `8a707ab`; IRIS `docs/next` at `2a2d92e`;
WACHUMA `docs/next` at `62e58e5`. The base MAK checkout is `MAK` at `86c0efb9`
with existing modifications to WACHUMA application documents. Preserve them.

Claude's `NEXT.md` notes are observations, not proof of current functionality.
XIO already has `showcontrol/automap.py`, `timeline.py` and `fabric.py`;
`XIO_LAYER` is present on a different work branch. Next implementation must
reuse the domain plugin rather than duplicate signal transport. Select branch
from actual file availability before editing. No remote checkout changed.

Public publication includes dossier text and reusable verification scripts,
excluding original media, rendered derivatives and private repository code.
The current proposal and historical notes need not share the current runtime
branch: this is why the local and MAK branch identities stay explicit.

## Historical checkpoints

The sections below preserve prior stages and do not override the current
consolidation/delegation section above or the
[current dossier index](../../../output/postulacion_dimensiones_del_orden_2027/README.md).
In particular, the earlier Blender-to-BLE-only framing has been expanded into
the live spatial light work; old next-action sections are historical.

status: activated
run_id: 20260907-dimensiones-orden-postulacion
objective: Concretar una postulacion admisible, defendible y con base cientifica para Dimensiones del Orden.

## Acceptance criteria

- The project is framed as an audiovisual experimental methodology, not as a generic software product.
- Every central claim is backed by a local artifact, an external source, or is explicitly marked as a proposal.
- The simulation-to-hardware experiment has a testable question, variables, measurements, failure criteria, and reproducible records.
- The proposal, process document, budget audit, evidence register, and admissibility gate are internally consistent.
- Unresolved personal, legal, venue, rights, and platform facts remain visible and are not invented.

## Current evidence

- Official call page: Fondart Nacional, Produccion de obras experimentales, Fondo Audiovisual 2027.
- Local bases PDF and current treatment/budget files were read from MAK.
- `flashes5d.blend` has camera rotation keyframes at frames 300 and 790; the complete loop is 491 frames at 30 FPS.
- The submitted MP4 has 491 video frames, 30 FPS, and 16.366667 seconds.
- The Blender scene contains procedural Geometry Nodes, including a 617-node `Curve to Tube` tree and a phase-driven beam group.
- `miracles_star_web.py` currently has 743 lines; the proposal text claiming 989 lines is stale.
- One BLE device is supported by existing code evidence; the multi-device physical rig remains proposed work.

## Selected approach

Build a local, auditable application package around the existing work. The scientific core is a paired representation experiment: deterministic phase field in Blender versus sampled physical light output. Keep the final artistic claim and the engineering claim separate.

## Active files

- `output/postulacion_dimensiones_del_orden_2027/01_project_proposal.md`
- `output/postulacion_dimensiones_del_orden_2027/02_experimental_method.md`
- `output/postulacion_dimensiones_del_orden_2027/03_evidence_register.md`
- `output/postulacion_dimensiones_del_orden_2027/04_budget_audit.md`
- `output/postulacion_dimensiones_del_orden_2027/05_admissibility_gate.md`
- `output/postulacion_dimensiones_del_orden_2027/13_submission_critical_checklist.md`
- `output/postulacion_dimensiones_del_orden_2027/20_curriculum_evidence_map.md`
- `output/postulacion_dimensiones_del_orden_2027/21_applicant_closure_sheet.md`
- `output/postulacion_dimensiones_del_orden_2027/verify_submission_package.ps1`
- `output/postulacion_dimensiones_del_orden_2027/22_jury_brief.md`
- `work/agent-ledger/20260907-dimensiones-orden-postulacion/research.md`

## Immediate next action

Keep the local dossier as the canonical draft, use `17_source_replacement_plan.md` to prevent stale MAK text from re-entering the application, and finish only the platform-level checks that require the applicant's current profile, region, rights, quotations and final dates.

## Checkpoint 1 - dossier drafted and checked

- Added the project proposal, corrected treatment, experimental method, evidence register, budget audit, FUP field map, and admissibility gate under `output/postulacion_dimensiones_del_orden_2027/`.
- Verified dossier arithmetic: current working budget sums to CLP 13,800,000; percentages recompute to 19.83%, 25.36%, 47.83%, and 6.99%.
- Verified stale line count is not used as a project claim; current code evidence is 743 lines.
- Verified camera evidence is consistently described as keyframes 300-790, 491 frames, 30 FPS, 16.366667 seconds.
- Rechecked `flashes5d.blend` directly in Blender 4.5.4: `Camera.002` has only `rotation_euler[2]` animated, with keyframes 300=`3.490658522` rad and 790=`-2.792526722` rad, a `-2*pi` change. This proves one complete 360-degree rotation; the saved scene range 620-790 is only a partial render segment.
- Verified new filenames are ASCII.
- Verified the complementary MP4 is 40.22 MB, 1080x1920, 491 frames, 30 FPS, and below the official 100 MB attachment limit.
- Verified official evaluation weights: technical-financial 40%, curriculum 20%, creative 40%; treatment maximum 20 pages; complementary audiovisual material maximum 5 minutes.
- Added a revision delta and scientific reference list; core proposal/treatment files contain no stale `989` or unsupported first-implementation claim.
- Added an artifact manifest with SHA-256 identifiers for the inspected Blender scene, MP4 and BLE control script.
- Rendered and visually checked `submission_treatment.pdf` (3 A4 pages) and `submission_experimental_method.pdf` (2 A4 pages); both are below the official page limit and were produced without changing MAK.
- Re-rendered the treatment and method PDFs after strengthening the camera evidence; verified they remain 3 and 2 A4 pages respectively.
- Compacted the internal budget audit, re-rendered `submission_budget_audit.pdf`, verified it is now one A4 page, and visually checked the rendered page.
- Detected and resolved a format risk: the source MP4 is vertical 1080x1920, so produced `submission_complementary_1920x1080.mp4` with preserved content and side bars. Verified 1920x1080, 30 FPS, 491 frames, 16.366667 seconds, 13.74 MB.
- Audited the official 2027 contracting guide: the budget must classify actual labor relationships, distinguish responsible allocation from team costs, and use the 2027 honorarios withholding only where an autonomous service genuinely applies.
- Rechecked the official call index and audiovisual FAQ on 2026-09-07. Recorded the extension discrepancy: an older line URL may show 4 September, while the current extension sources report 8 September for ordinary regions and 11 September for the four northern regions. The gate now directs the final check to the extension resolution and platform.
- Added a submission-critical checklist separating ready artifacts from applicant-only facts, rights, quotations, labor classification and platform checks.
- Added an Annex 2 document matrix and concise FUP copy blocks so the remaining work is platform integration rather than conceptual rewriting.
- Read the original MAK budget in read-only mode and created a safer local variant: preserve technical-risk and documentation hours, reduce only direction/capture/editing hours, move CLP 144,000 to installation materials, and lower Personal from 19.8% to 18.78% without changing the total.
- Rendered and visually checked `submission_budget_reconciled.pdf` (2 A4 pages); arithmetic verified at CLP 13,800,000 total.
- Polished the Spanish treatment prose and accents without changing technical identifiers; re-rendered `submission_treatment.pdf` and visually checked all 3 A4 pages.
- Added a local source-replacement plan and ran the final consistency audit: treatment 3 pages, method 2, budget audit 1, reconciled budget 2, complementary video 1920x1080 with 491 frames at 30 FPS, budget total CLP 13,800,000, and no stale claims in the main proposal/treatment/method/FUP blocks.
- Extended the method with a reproducible analysis plan for onset deviation, circular phase error, order accuracy, drop rate and run-level uncertainty; re-rendered and visually checked the method PDF at 3 A4 pages.
- Measured all six FUP copy blocks and recorded their character/word counts without assuming undocumented platform limits.
- Added the final submission sequence with P0-P4 checks, conditional Annex 2 documents, explicit stale-source prevention and receipt preservation.
- Re-read the three authoritative MAK artifact hashes over SSH; they match the manifest, confirming that this workstream made no remote mutation.
- No existing FARMAXIA files were overwritten; the worktree remains dirty from prior user changes.

## Next productive block

Run one final local consistency audit after any requested edits; otherwise keep
the dossier ready for direct FUP transfer without mutating MAK. The curriculum
map now separates verified repository practice from unverified deployment and
proposed grant work.

## Checkpoint 2 - curriculum evidence map

- Read the bounded capability records for MOSAIK and XIO from Windows.
- Added `20_curriculum_evidence_map.md` with candidate evidence, competency,
  limits, and a recommended compact evidence chain.
- Kept MOSAIK and XIO as supporting technical context rather than new project
  deliverables.
- Explicitly excluded claims of public deployment, completed multi-device
  synchronization, awards, clients, or dates that were not verified.
- MAK remained read-only; no remote files or branches were changed.

## Checkpoint 3 - local consistency audit

- Confirmed all core dossier files and rendered submission artifacts exist.
- Searched the core proposal, method, treatment, FUP blocks, budget draft and
  curriculum map for stale or overstated claims. Matches found are only
  explicit warnings or exclusions; no stale claim is being presented as a
  current project fact.
- Confirmed the current local budget remains CLP 13,800,000 and the current
  code evidence remains 743 lines for `miracles_star_web.py`.
- Confirmed the complementary video remains 491 frames at 30 FPS and the
  generated PDF/video artifacts are present.

## Checkpoint 4 - applicant closure sheet

- Added `21_applicant_closure_sheet.md` to separate locally prepared material
  from identity, deadline, rights, venue, quotation and platform actions that
  require the applicant.
- Added a deterministic transfer order and explicit stale-claim safeguards.
- Kept the package bounded to the audiovisual experimental application; no
  unrelated ecosystem project was converted into a grant deliverable.

## Checkpoint 5 - package preflight

- Added `verify_submission_package.ps1`, a local-only pre-upload verifier for
  required artifacts, the 100 MB limit, stale claims, complementary video
  dimensions/duration and treatment page count.
- The verifier never uploads files and never modifies MAK.
- First execution exposed a PowerShell 5 default-parameter issue; fixed the
  script to resolve its own directory and reran it successfully:
  `SUBMISSION_PACKAGE_PASS`.

## Checkpoint 6 - official deadline cross-check

- Rechecked the current official line page on 2026-09-07.
- Recorded the current closure split: 8 September 2026 at 15:00 for ordinary
  regions and 11 September 2026 at 15:00 for Arica, Tarapaca, Antofagasta and
  Atacama.
- Kept the applicant region as unresolved rather than inferring it.

## Checkpoint 7 - scientific reference audit

- Rechecked the audiovisual synchrony sources and the procedural-art source.
- Expanded the references file into a source-to-claim matrix that states what
  each source supports and what it cannot establish for this project.
- Kept the method free of an imported universal perceptual threshold; timing
  tolerances remain declared experimental parameters.

## Checkpoint 8 - jury-facing compression

- Added `22_jury_brief.md` to compress the project into one coherent reading:
  problem, existing evidence, funded experiment, execution logic, limits and
  evaluation criteria.
- Kept unrelated ecosystem projects outside the committed deliverables.

## Checkpoint 9 - verifier portability

- Ran `verify_submission_package.ps1` from the repository root with an explicit
  package path and from the package directory using its default resolution.
- Both executions returned `SUBMISSION_PACKAGE_PASS`.
- Confirmed the check is independent of the current working directory and does
  not contact or mutate MAK.

## Checkpoint 10 - admissibility gate calibration

- Updated the gate to mark only locally verified items as complete: page/time
  limits, artifact provenance, reconciled arithmetic, local attachment sizes,
  visual PDF inspection, stale-claim search and local cross-document checks.
- Kept all platform-dependent actions unchecked: official FUP export, actual
  upload, applicable rights/team documents, final quotations, receipt and
  folio.

## Checkpoint 11 - technical token audit

- Scanned technical tokens inside Markdown code spans across the dossier.
- Result: `ASCII_TECHNICAL_TOKENS_PASS`.
- The audit command itself needed one PowerShell interpolation correction;
  the corrected run passed and no dossier file was changed by that check.

## Checkpoint 12 - budget source separation

- Clarified that `04_budget_audit.md` is the historical/original baseline and
  must not be copied into the official form.
- Marked `16_budget_form_reconciled_draft.md` as the recommended local starting
  point, with Personal at 18.78% of the unchanged total.
- Updated evaluation guidance so the remaining risk is correctly identified as
  labor classification and quotations, not conceptual rewriting.

## Checkpoint 13 - budget audit render

- Regenerated `submission_budget_audit.html` and `submission_budget_audit.pdf`
  from the clarified Markdown source.
- Removed one redundant closing paragraph so the internal audit returns to one
  A4 page.
- Verified the final page visually; the historical baseline and the recommended
  reconciled variant are clearly distinguished.

## Checkpoint 14 - official document boundary

- Re-read the official 2027 bases, Annex 2 and the Fondo Audiovisual FAQ.
- Clarified the local document matrix: the budget form, treatment and
  complementary audiovisual material are evaluation documents; conditional
  rights, team, legal-entity, territory and minors documents are taxative when
  applicable.
- Added an explicit rule not to upload the internal dossier, research notes or
  jury brief as unsolicited additional evidence.

## Known decision boundaries

- Applicant region and current Profile Cultura contents determine the applicable deadline and personal eligibility.
- Real quotations, rights, venue, and final audio choice cannot be fabricated.

## Checkpoint 15 - semantic interoperability reframing

- Reframed the proposal from a narrow Blender-to-BLE comparison to a live audiovisual work with a shared semantic light state.
- Added the operator problem: the work tests whether phase, tempo, energy, density, direction and topology can be translated across heterogeneous systems without forcing a complete re-learning of each console.
- Added layout, mapping and patch as separate concepts. The camera and geometric prior address physical mapping; RDM or active probing address device identity and patch evidence.
- Added preshow, soundcheck and liveshow as three artistic/technical phases rather than only production logistics.
- Added LED surfaces as luminous architecture receiving the same evolving state as the physical fixtures, not merely as playback screens.
- Added measurements for `mapping_accuracy`, `patch_recovery_time_ms`, `semantic_translation_loss`, `operator_task_time_ms` and `safe_state_rate`.
- Added `23_semantic_interoperability_annex.md` for transfer to future commercial, open-source and other cultural applications without inflating the current grant claim.
- Research sources registered: ESTA E1.20 RDM, Open Lighting Architecture, Open Fixture Library, TouchDesigner DMX/OSC documentation and official OUTWORLD presentation.
- Updated treatment, proposal, method, FUP blocks, jury brief, evidence register, budget labels, evaluation alignment and admissibility gate.

## Current next action

Run local consistency and rendering checks against the revised dossier. Recalculate the reconciled budget after label-only changes, render the treatment/method PDFs, run the package verifier, then identify whether any claim or field still requires applicant-only data. Do not add further conceptual scope before this verification.

## Checkpoint 16 - revised package verified

- Regenerated `submission_treatment.html` and `submission_treatment.pdf` from the revised treatment; visual review passed and the PDF is 4 A4 pages.
- Regenerated `submission_experimental_method.html` and `submission_experimental_method.pdf`; visual review passed and the PDF is 4 A4 pages.
- Regenerated `submission_budget_reconciled.html` and `submission_budget_reconciled.pdf`; visual review passed and the PDF is 2 A4 pages.
- Recomputed the budget: CLP 2,592,000 + 3,500,000 + 6,744,000 + 964,000 = CLP 13,800,000.
- Ran `verify_submission_package.ps1`: `SUBMISSION_PACKAGE_PASS`.
- Verified the new mapping, semantic translation, RDM and LED-surface claims are marked as proposed or capability evidence where appropriate; no claim of universal autopatching or completed cross-console interoperability was introduced.

## Checkpoint 17 - call adaptation and scope control

- Rechecked the current official pages for Audiovisual experimental production,
  Fondart Regional creation, Fondart Regional diffusion, Regional formative
  activities and Fondart Nacional research.
- Confirmed the immediate route: Audiovisual experimental production closes on
  8 September 2026 at 15:00 for ordinary regions and 11 September for the
  northern extension regions.
- Confirmed the other current dates: formative activities on 9 September,
  regional creation and diffusion on 11 September for ordinary regions, and
  national research on 14 September for ordinary regions.
- Added `24_call_adaptation_matrix.md`, separating the same artistic core from
  five different call objectives and identifying the evidence each route would
  require.
- Chose Audiovisual experimental production as the canonical application. A
  regional creation variant is viable only with a real venue and exhibition
  plan. Diffusion, formative activity and research remain distinct future
  wrappers rather than superficial rewrites of the production proposal.

## Current next action

Transfer the canonical audiovisual package to the official platform, then close
only applicant-controlled fields: region, profile, dates, rights, venue,
quotations, team and final approval. Do not broaden the technical scope before
the first submission is either sent or blocked by a concrete platform issue.
