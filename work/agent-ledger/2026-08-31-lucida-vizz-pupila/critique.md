# Decision critique

previous_action: Renombrar LIMEN a LUCIDA de manera aislada en VJ.
selected_action: change_method
decision_delta: Separar identidad, comportamiento y origen. XIO y VJ recibirán ramas propias con cambio nominal acotado; la integración funcional se hará después en FARMAXIA.
strongest_failure_mode: Cambiar nombres en un solo repositorio puede romper imports, documentación, trazabilidad y el significado de LUCIDA como base común.
expensive_mistake: Sobrescribir cambios de usuario en XIO o convertir la extracción de ZIGO en una copia de obras privadas.
alternatives:
  direct: Editar ahora los tres repositorios; menor latencia, pero alto riesgo de mezclar ejes y perder cambios.
  coordinated: Congelar límites, crear ramas derivadas y verificar referencias antes de integrar; más coordinación inicial, menor retrabajo.
  stop: Esperar definición de nombres; evita cambios, pero no produce el núcleo de VIZZ/PUPILA.
decision: coordinated
reason: La evidencia muestra nombres LIMEN reales en XIO y VJ, mientras que la extracción de SVG tiene otro contexto. La separación por contratos es reversible y permite avanzar sin tocar main.
confidence: alta para el límite de alcance; media para los nombres concretos hasta revisar cada agente.
verification_signal: Cada agente debe devolver rama, diff limitado a identidad, tests y confirmación explícita de que main no cambió.
next_checkpoint: Integrar sólo contratos que crucen una prueba real entre repositorios y auditar los siguientes commits de XIO/VJ.

## Current review

observed_failure: Ambos agentes quedaron idle después de completar una tarea;
una instrucción ambigua podía producir sólo "orden recibida" sin trabajo nuevo.
corrective_action: Enviar tareas con archivo objetivo, cambio mínimo, test
obligatorio, commit y push; verificar el repositorio directamente después.
evidence: XIO produced d8a13f0 and 45132fd; MOSAIK produced e08b8b9 and
e19de67. All four commits were verified against their source trees. The source
XIO branch has 55 passing tests and the source MOSAIK branch has 75 passing
tests.
important_boundary: connectivity.status is valid transport evidence, but it is
not a VJ phase. MULTI transports it; RESOLUME rejects it without mutating
replay; VIZZ/PUPILA consumes only a bounded metadata projection.
selected_next_action: Continue the 090 bridge and keep agent tasks bounded by
capability routing and cross-domain rejection. Do not add a real socket or GUI
until authentication, cancellation and observable outcomes are specified.
forecast: High probability of a stable offline vertical slice; low probability
of meaningful universal-app claims until host adapters and task outcomes exist.

## 2026-09-01 autonomous boundary audit

objective: Keep XIO, LUCIDA, ADOBE, RESOLUME, VIZZ and PUPILA progressing without crossing ownership boundaries.
observed_state: Published XIO 374aafa passes 99 tests in a clean audit worktree. The active XIO checkout has newer uncommitted event-log changes and currently reports 1 failure in 101 tests; that state is not eligible for integration.
observed_state_vj: Published LUCIDA 7d49244 passes 102 tests; FARMAXIA offline integration passes 3/3.
strongest_failure_mode: Treating an active dirty checkout as a published capability would silently integrate an unverified event or transport behavior.
alternatives: Wait for XIO to self-verify; inspect or edit XIO directly; continue FARMAXIA using the last published contract. The first and third preserve ownership and reviewability; direct edits would interfere with the autonomous agent.
selected_action: continue_with_published_contracts
decision_delta: Do not integrate the active XIO working tree until its own test failure is resolved and a new published commit passes in a clean audit.
verification_signal: Clean published XIO worktree passes 99 tests; current FARMAXIA integration passes 3/3; LUCIDA passes 102 tests.
next_checkpoint: Re-audit XIO only after a new published commit; keep VJ/LUCIDA branch-specific and do not merge host-specific code into FARMAXIA.

## 2026-09-01 acceptance provenance repair

observed_failure: The consolidated runner exposed --xio-root, but the route check imported a hard-coded XIO path, so an audit could pass against the wrong checkout.
selected_action: Make the route check load the requested root, assert the loaded package path is inside it, report both paths, and forward the argument from the consolidated runner.
evidence: Exact-root extended integration passed 4/4; clean published XIO b58ccfa passed 103 tests; clean published MOSAIK/LUCIDA ee0f3c9 passed 104 tests; FARMAXIA contract passed 23 tests.
strongest_failure_mode: Python module caching or an invalid checkout could still make provenance ambiguous if the loader did not assert the resolved package path.
decision: accept
reason: The loader runs in a fresh subprocess, inserts the requested checkout first, and rejects a resolved XIO package outside that checkout. The change preserves all application ownership boundaries and does not enable network or host actions.
next_checkpoint: Publish this narrow fix, then audit new agent commits once rather than polling continuously.

## 2026-09-01 agent hito audit after root fix

observed_state: XIO published 04328ae and MOSAIK/LUCIDA published 60b9756. The exact-root FARMAXIA seam passes, but the complete clean XIO suite has one reproducible Windows concurrency failure in the persistence lock.
selected_action: Keep XIO unaccepted and avoid editing its branch; accept the independent LUCIDA audit result and continue using only verified FARMAXIA contracts.
strongest_failure_mode: Treating a passing cross-repository smoke seam as sufficient while a source repository's full persistence suite is red.
evidence: XIO clean suite 105 passed, 1 failed; LUCIDA clean suite 106 passed; FARMAXIA exact-root integration 3/3; no network, GUI or host action.
decision: reject_xio_for_integration
reason: The failure is in the source lock implementation and cannot be resolved by a FARMAXIA adapter without hiding a source defect. The autonomous XIO objective remains active and can repair its own branch.
next_checkpoint: Audit XIO again only after a new published commit; continue the own goal without sending idle prompts.

## 2026-09-01 LUCIDA checkout provenance repair

observed_failure: The LUCIDA consumer runner accepted an explicit root but could import a package from an already loaded or unintended environment path without reporting it.
selected_action: Clear the LUCIDA module cache in the fresh check process, load the requested root first, assert the resolved package path is inside it, and expose both paths in the report.
evidence: Clean MOSAIK/LUCIDA 60b9756 passes 106 tests and the consumer check passes; invalid-root invocation fails; no network, GUI or host action occurs.
strongest_failure_mode: A cross-repository acceptance result could look green while exercising a different LUCIDA checkout.
decision: accept
reason: The loader now makes the source checkout auditable and preserves the role boundary; this is a verification repair, not a host integration.
next_checkpoint: Publish after exact-root contract and negative-path checks; do not add another runtime layer until the external XIO lock failure is resolved.

## 2026-09-01 MULTI dual-root provenance repair

observed_failure: The MULTI fixture carried a copy of XIO_LAYER, and its import order could make --xio-root ineffective even while the command appeared successful.
selected_action: Load and verify XIO first only for the connectivity event, clear the package cache, then load and verify the MULTI checkout for transport and restoration.
evidence: Clean exact-root MULTI check passes; the report distinguishes both package paths and preserves three events, provenance and round trips without forwarding payloads.
strongest_failure_mode: A cross-repository test could report a green MULTI transport while silently using stale XIO code.
decision: accept
reason: The two roots are now independent and auditable, with explicit negative-path validation. No application host or network behavior is introduced.
next_checkpoint: Publish this narrow gate repair, then defer new features until XIO publishes a clean fix for its Windows persistence lock failure.

## 2026-09-01 repaired agent contract acceptance

observed_state: XIO 3944a0b now passes 108 clean tests and MOSAIK/LUCIDA 10810c3 passes 111 clean tests. The earlier XIO lock failure is resolved in the published branch.
selected_action: Reopen XIO for the offline acceptance gate while keeping the gate exact-root and offline.
evidence: FARMAXIA extended integration passes 4/4; the report distinguishes XIO, LUCIDA and MULTI package paths; no network, GUI or host action occurs.
strongest_failure_mode: Mistaking a green offline seam for a live host integration or silently accepting the dirty agent worktree instead of the published commit.
decision: accept_offline_only
reason: Full clean source suites and the exact-root cross-repository checks are green. Live transport, renderer and host-specific behavior remain deliberately outside scope.
next_checkpoint: Keep the agents autonomous and audit only after new commits; define the next host-neutral observable outcome before adding integration code.

## 2026-09-01 render cadence decision

observed_problem: The render plan was safe but had no explicit rate policy, so a future host could recompute visual work for every incoming signal and reproduce the earlier flicker/performance risk.
selected_action: Add a stateless 30 Hz budget decision at the render-plan boundary, with duplicate suppression and coalescing rather than a new host renderer.
alternatives: Emit every event gives lowest visual latency but risks redundant work; fixed sleep would block and complicate cancellation; a pure decision lets LUCIDA schedule or discard without FARMAXIA owning a clock.
strongest_failure_mode: A budget could hide a meaningful visual change or accept an unsafe plan.
evidence: Same plan is dropped; a changed plan at 1 ms is held; the same change at 34 ms emits; invalid timing and unsafe fields fail; consumer integration reports the four expected decisions.
decision: accept_as_host_neutral_policy
reason: The function has no sleep, retained state, GUI, network or host action. It bounds work while leaving scheduling and rendering to LUCIDA.
next_checkpoint: Publish after the full 090 gate passes; only add a real scheduler after LUCIDA defines its runtime tick and cancellation contract.
