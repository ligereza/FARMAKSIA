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
