run_id: 2026-08-31-lucida-vizz-pupila
objective: Coordinar la separación limpia de XIO y VJ respecto del proyecto base LUCIDA, preservando el eje de cada repositorio, y construir en FARMAXIA un núcleo reutilizable derivado de la extracción ZIGO para VIZZ y PUPILA como capas transparentes, emergentes y multiusuario.
scope: XIO y VJ en ramas separadas; FARMAXIA como espacio de integración conceptual y verificable para VIZZ/PUPILA; extracción ZIGO como referencia técnica, sin copiar obras, assets, credenciales o corpus privados.
core_acceptance_criteria:
  - XIO y VJ trabajan en ramas propias y no alteran main.
  - El cambio de nombres se limita a identidad/documentación/imports necesarios; no cambia el comportamiento central de cada proyecto.
  - VIZZ y PUPILA comparten contratos de eventos, estado, propuesta, consentimiento y replay, pero mantienen módulos distintos.
  - Cada avance tiene prueba o verificación observable y queda registrado.
  - No se afirma que la cámara, el foco o el análisis humano sean exactos sin medición.
authorized_extensions:
  - Diseñar una capa común de interacción transparente, emergente y multiusuario.
  - Añadir adaptadores de teclado, puntero, foco y presencia sólo como señales no invasivas.
status: active

completed:
  - item: Se creó el objetivo autónomo de esta sesión.
    evidence: Goal activo en la sesión principal.
  - item: Se inspeccionó el estado de FARMAXIA, XIO, VJ y SVG.
    evidence: XIO en codex/limen-xio-adapter con cambios sin commit; VJ en codex/limen-vj-adapter limpio; SVG en main con extracción generic-interface-layer sin commit aislado en ese momento.
  - item: Se confirmó que LIMEN existe como código real en XIO y VJ; en SVG la extracción se identifica como generic-interface-layer derivada de ZIGO.
    evidence: Carpetas, imports, documentación y nombres de paquete observables en los repositorios.
  - item: Se implementó el slice 090 derivado de ZIGO con adaptadores separados VIZZ/PUPILA.
    evidence: Cinco pruebas offline pasan; demo produce dos estados VIZZ y una propuesta PUPILA; procedencia 090 valida.
  - item: VJ quedó separado en una rama con identidad propia.
    evidence: C:\IA\VJ en codex/vj-interface-layer, commits 44a1e18 y 6e63ae4, 11 tests, árbol limpio y main intacto.
  - item: XIO quedó separado en una rama con identidad propia después de que el agente no produjera un cambio verificable.
    evidence: C:\IA\XIO en codex/xio-interface-layer, commit cada5d1, package LIMEN renombrado a XIO_LAYER, 10 unittest pasan; los cambios pendientes fuera del paquete permanecen sin stage.
  - item: XIO agregó transporte offline y una regla técnica de idioma ASCII.
    evidence: C:\IA\XIO en codex/xio-transport, commits bbc7534 y 151670d; 19 unittest pasan y XIO_LAYER/tests/test_ascii_contract.py verifica los archivos técnicos.
  - item: VJ consolidó una superficie LUCIDA y agregó una barrera ASCII verificable.
    evidence: C:\IA\VJ en rama LUCIDA, commit e4f835b; lucida/CONTRIBUTING.md, lucida/ascii_guard.py y tests/lucida/test_ascii_guard.py presentes; 14 tests focalizados pasan.
  - item: XIO entregó sesiones multi-peer y el contrato canónico de eventos de aplicaciones.
    evidence: C:\IA\XIO en codex/xio-transport, commits b8f8ba0 y 7a9dad3; handshake, fan-out, deduplicación, OSC/Art-Net, replay JSONL y provenance; 33 unittest pasan y la rama está publicada en origin.
  - item: MOSAIK entregó la frontera OSC inyectable y el replay auditable de LUCIDA.
    evidence: C:\IA\VJ en LUCIDA, commits e43422d, 7daa9fb y 206b844; 34 pytest pasan y la rama está publicada en origin/LUCIDA.
  - item: Se creó y publicó el repositorio LUCIDA con sus tres ramas funcionales.
    evidence: C:\IA\LUCIDA: ADOBE=da90459, RESOLUME=0864be1, MULTI=fb75553; las tres ramas existen en origin y main permanece en eb3e922.
  - item: Se aceptó la migración Adobe aislada derivada del toolkit de SVG.
    evidence: C:\IA\LUCIDA\adobe; 538 archivos en ADOBE, ocho carpetas CHEMSEX, 361 incluidos con hashes verificados, sin node_modules/caches/credenciales; verify, smoke, companion check y 11 tests pasan.
  - item: Se corrigió una dependencia omitida al integrar MOSAIK en RESOLUME.
    evidence: La primera prueba en LUCIDA falló por falta de adapters.vj; se añadió únicamente ese contrato/adapter, y la suite posterior pasó 23 tests con control ASCII limpio.
  - item: MOSAIK/VJ entregó el consumidor XIO para replay de eventos de aplicación.
    evidence: C:\IA\VJ en LUCIDA, commit f4e9f21 publicado en origin/LUCIDA; el consumidor conserva provenance, secuencia y resultados, y la suite pasa 43 tests. La integración corrigió una importación circular con un regression-safe lazy import.
  - item: Se integró el consumidor XIO en la superficie RESOLUME de LUCIDA.
    evidence: C:\IA\LUCIDA/RESOLUME, commit 5c8e104 publicado; la suite offline pasa 32 tests y el branch mantiene proposal-only, sin sockets ni Resolume real.
  - item: Se integró el bridge de eventos de aplicación en la superficie MULTI de LUCIDA.
    evidence: C:\IA\LUCIDA/MULTI, commit 4ed7dc3 publicado; la suite XIO pasa 39 unittest y el bridge valida canal, envelope, schema, deduplicación y secuencia.
  - item: XIO entregó una frontera de capacidad de conectividad inyectable.
    evidence: C:\IA\XIO en codex/xio-transport, commit 61b3bd2 publicado; ConnectivityProbe reutiliza ConnectionStatus para ethernet, wifi, hotspot y router sin abrir sockets ni inventar mediciones. La suite pasa 44 unittest.
  - item: Se integró la capacidad de conectividad en LUCIDA/MULTI.
    evidence: C:\IA\LUCIDA/MULTI, commit fe28c94 publicado; la suite pasa 44 unittest y mantiene la medicion como responsabilidad del host.
  - item: MOSAIK entregó una frontera host-neutral para decisiones de propuestas.
    evidence: C:\IA\VJ en LUCIDA, commits 9b3c2b3 y 6ff293d publicados; ProposalDecision, HostSignalBoundary y receipts de auditoria distinguen accepted/rejected/unknown de ejecucion real. La suite pasa 53 pytest.
  - item: Se integró la frontera host en LUCIDA/RESOLUME.
    evidence: C:\IA\LUCIDA/RESOLUME, commit 2a43ed2 publicado; la suite pasa 42 pytest y conserva proposal-only, replay offline y ausencia de sockets/Resolume real.
  - item: XIO endureció la deduplicación y serialización de ConnectivityStatus.
    evidence: C:\IA\XIO en codex/xio-transport, commit d8a13f0 publicado; la suite completa de XIO_LAYER pasa 55 tests y cubre mediciones stale, replay idempotente y estados malformados sin abrir sockets.
  - item: XIO agregó un gate opcional de capacidades para fan-out.
    evidence: C:\IA\XIO en codex/xio-transport, commit 45132fd publicado; un peer sin la capacidad requerida recibe capability_missing y no se envía el signal; la suite completa pasa 55 tests.
  - item: MOSAIK endureció HostResult y la frontera de eventos no-VJ.
    evidence: C:\IA\VJ en LUCIDA, commits e08b8b9 y e19de67 publicados; HostResult valida campos, round-trip y estados; connectivity.status/transport es rechazado sin inventar fase ni mutar replay; la suite completa pasa 75 tests.
  - item: Se integraron los contratos nuevos en LUCIDA.
    evidence: LUCIDA/MULTI commits 659a90a y 99b9d96, 55 unittest; LUCIDA/RESOLUME commit e2f2cb1, 63 pytest; todos publicados y sin incluir adobe/.
  - item: Se construyó el primer puente real XIO -> VIZZ/PUPILA en FARMAXIA.
    evidence: Experimento 090 valida ApplicationEvent canónico, conserva lineage, elimina payload crudo, bloquea sin consentimiento, deduplica por session/peer/surface y separa sesiones PUPILA; contrato offline pasa 13 tests y el cross-branch check con XIO real pasa.
  - item: XIO corrigió el gate de capacidades para usar la negociación vigente del handshake.
    evidence: C:\IA\XIO en codex/xio-transport, commit 1f543f9 publicado; las capacidades se reemplazan sólo tras handshake aceptado y se limpian al desconectar, revocar o fallar; la suite pasa 57 unittest.
  - item: XIO añadió el registro universal de adaptadores por aplicación.
    evidence: C:\IA\XIO en codex/xio-transport, commit 173e96e publicado; SourceAdapterRegistry enruta tipos declarados, congela capacidades y conserva metadata canónica sin sockets ni SDK de host; la suite pasa 63 unittest.
  - item: MOSAIK/VJ añadió una proyección acotada para la capa invisible de LUCIDA.
    evidence: C:\IA\VJ en LUCIDA, commit e53166e publicado; read_overlay_view entrega estado, capacidades, propuestas y desconocidos sin payload crudo, con orden determinista y proposal_only; la suite pasa 78 pytest.
  - item: Se integró el registro de adaptadores de XIO en LUCIDA/MULTI.
    evidence: C:\IA\LUCIDA/MULTI, commit 660c4f9 publicado; OSC y Art-Net comparten el punto de extensión con futuras apps como Adobe; la suite pasa 58 pytest/subtests y adobe/ quedó fuera del commit.
  - item: MOSAIK/VJ completó la vista de atención acotada para LUCIDA.
    evidence: C:\IA\VJ en rama LUCIDA, commit eb0b97e publicado; la vista mantiene orden determinista, proyeccion read-only y propuesta-only sin payload; la suite pasa 79 pytest.
  - item: FARMAXIA conectó la proyección PUPILA al puente canónico y al replay.
    evidence: Experimento 090, commit 7368d96 publicado en main; cada resultado expone pupilaView y el replay finalPupilaView, con payload y acciones excluidos; contrato offline pasa 17 tests, demo y cross-branch check pasan.
  - item: XIO publicó un snapshot JSON-safe del registro de adaptadores.
    evidence: C:\IA\XIO en codex/xio-transport, commit 5e1be8d publicado; snapshot ordena aplicaciones, tipos y capacidades, devuelve copias aisladas y no expone instancias ni red; la suite completa pasa 66 unittest.
  - item: MOSAIK/VJ publicó el diff incremental de la vista LUCIDA.
    evidence: C:\IA\VJ en rama LUCIDA, commit 828467c publicado; diff_overlay_view valida vistas proyectadas, compara sólo campos seguros y limita cambios; la suite completa pasa 82 pytest.
  - item: LUCIDA/MULTI adoptó el snapshot del registry de XIO.
    evidence: C:\IA\LUCIDA en rama MULTI, commit f016a1c publicado; el contrato y sus pruebas pasan 61 unittest, y adobe/ permanece sin seguimiento.
  - item: XIO extendió el registry con un plan declarativo de rutas.
    evidence: C:\IA\XIO en codex/xio-transport, commit c95fab2 publicado; route_plan informa matched/no_match y candidatos sin ejecutar adapters; la suite completa pasa 73 unittest.
  - item: MOSAIK/VJ expuso el diff de overlay desde el orquestador.
    evidence: C:\IA\VJ en rama LUCIDA, commit 433c3ab publicado; diff_overlay_view acepta estados o mappings, proyecta por la vista acotada y evita metadata privada; la suite completa pasa 85 pytest.
  - item: LUCIDA/MULTI adoptó la consulta de candidatos y su plan declarativo.
    evidence: C:\IA\LUCIDA en rama MULTI, commit 6799f43 publicado; candidates filtra por evento/capacidad y devuelve no-match explícito; la suite pasa 65 unittest.
  - item: FARMAXIA añadió diff incremental para PUPILA.
    evidence: Experimento 090, commit d17146f publicado en main; diff_pupila_view compara sólo campos proyectados y rechaza payloads/acciones; contrato offline pasa 19 tests.

current_state:
  files_or_resources:
    - C:\IA\FARMAXIA
    - C:\IA\XIO
    - C:\IA\VJ
    - C:\IA\svg\agent-toolkit\generic-interface-layer
    - C:\IA\LUCIDA\ADOBE, RESOLUME y MULTI
  tests_and_checks: 090 pasa contrato offline con 19 tests, demo y cross-branch check con XIO real. XIO pasa 73 unittest en c95fab2; MOSAIK/VJ pasa 85 pytest en 433c3ab; LUCIDA/RESOLUME pasa 63 pytest; LUCIDA/MULTI pasa 65 unittest en 6799f43; LUCIDA/ADOBE pasa verify, smoke, companion check y 11 tests. La suite completa de FARMAKSIA se detiene antes de 090 por un hash mismatch preexistente en la procedencia de X-ANA-X 018.
  assumptions: LUCIDA es el proyecto base conceptual; XIO y VJ deben conservar nombres propios de su eje en sus ramas derivadas; ZIGO es el origen histórico, no el nombre de los productos finales.
  open_questions:
    - Nombre definitivo de las ramas derivadas de XIO y VJ.
    - Qué partes mínimas de generic-interface-layer se incorporan a FARMAXIA sin acoplarlo a SVG.
  blockers: Suite global bloqueada en provenance 018; no tocar ese archivo porque contiene cambios previos del usuario. XIO conserva cambios de usuario sin stage. La publicación pesada de ADOBE puede tardar por sus 513 MiB de iconos visuales, pero la rama ya quedó confirmada en origin/ADOBE. Ninguna rama declara todavía integración real con sockets, router, Resolume o Adobe.
  research_refs: Extracción ZIGO en SVG y contratos actuales de XIO/VJ.
  delegation_refs: XIO y VJ recibieron tareas ejecutables con archivo objetivo, suite, commit y push; tras detectar turnos inactivos se corrigió la dirección. XIO entregó 1f543f9 y 173e96e y ahora tiene una tarea activa para publicar un snapshot JSON-safe del registry; MOSAIK entregó abf4220, e53166e y eb0b97e y ahora tiene una tarea activa para calcular parches deterministas de la vista. SVG finalizó la extracción y la verificación de ADOBE se hizo en el repositorio destino. Los cambios de capacidades, conectividad, frontera host, registro de adaptadores, overlay y PUPILA fueron auditados e integrados selectivamente en LUCIDA/FARMAXIA.
  last_critique: La hipótesis evento canónico universal tenía un riesgo real: transportar no implica que un dominio VJ deba interpretarlo como fase. La prueba cross-branch confirmó que la separación correcta es transportar y preservar provenance en MULTI, pero rechazar explícitamente el evento en RESOLUME. El puente 090 adopta el evento sólo como metadata para VIZZ/PUPILA y no reenvía payload crudo.
  estimated_remaining_effort: Medio-bajo para el primer vertical offline; alto para transporte real, overlays y outcomes de aprendizaje. El siguiente avance debe demostrar una ruta de señales de interacción observable y reversible, no más contratos abstractos.
  next_action: Dejar a XIO y MOSAIK dirigiendo sus objetivos amplios y auditarlos por commits y suites, no por duración ni mensajes. Integrar en la siguiente revisión el route_plan de XIO y el diff de MOSAIK en las superficies LUCIDA correspondientes, sin copiar assets. En FARMAXIA, extender el replay con pointer/keyboard/focus y medir la política VIZZ/PUPILA por sesiones; dejar el transporte real fuera hasta fijar autenticación.
  next_checkpoint_trigger: Próxima revisión después de dos commits verificables de agentes o de la siguiente integración de 090.

latest_iteration_2026_09_01:
  selected_action: continue_with_functional_slice
  delegation:
    - XIO continues from dc374bf with a replayable local event source and one LUCIDA/MULTI integration fixture; acceptance is full suite, commit and push.
    - MOSAIK continues from 94bcc81 with a host-neutral overlay consumer smoke path for JSON, diff and revision cursor; acceptance is full suite, commit and push.
  own_change: Experiment 090 now verifies the complete offline path: XIO route_plan, explicit adapter selection, allowlisted handoff, LUCIDA/MULTI application-event envelope, VIZZ/PUPILA replay, interaction metrics, incremental view diffs, and delivery of the prepared handoff into PUPILA.
  evidence: 090 contract passes 19 tests; route handoff reports matched/XIO/prepared, empty projected payload, verified audit, preserved round-trip event, executionAttempted=false, and PUPILA receives one task-classified participant without inventing focus, pointer, or keyboard semantics.
  prediction: The next useful proof is a replay boundary crossing between XIO and LUCIDA, not another standalone schema. Qualitative confidence medium-high.
  next_action: Wait for agent completion or attention, then verify commits and suites once; integrate only the cross-repository fixture that passes.

latest_hito_2026_09_01_route_multi:
  selected_action: prove_multi_participant_handoff
  own_change: Extended the XIO route handoff check with two independently selected and redacted participants sharing one session, room and surface. The replay now verifies participant accumulation, incremental PUPILA view changes and an emergent co-presence proposal.
  evidence: The contract suite passes 19 tests; the route check reports multiAcceptedCount=2, multiParticipantCount=2, multiProposalKind=co-presence, preserved round-trip event IDs, verified audit chain, empty projected payload and executionAttempted=false. The XIO cross-branch replay also passes with 4 accepted events and 1 duplicate.
  prediction: The next high-value boundary is consuming this two-participant view through LUCIDA/MULTI without a GUI or host-specific action. Qualitative confidence medium-high.
  next_action: Run the existing LUCIDA/MULTI fixture against the new multi-participant contract, then commit only if the cross-repository replay preserves both participants, provenance and proposal-only safety.

latest_hito_2026_09_01_lucida_multi:
  selected_action: prove_transport_of_multi_participant_view
  own_change: Extended the LUCIDA/MULTI boundary fixture so three application events are transported and round-tripped before replay: connectivity for peer-1, focused interaction for peer-1 and unfocused interaction for peer-2.
  evidence: The fixture passes with transportedEventCount=3, eventIdsPreserved=true, provenancePreserved=true, farmaxiaAcceptedCount=3, participantCount=2, proposal kind shared-checkpoint, three deterministic view diffs and payloadForwarded=false. The 090 contract remains valid with 19 tests and the XIO cross-branch replay remains valid with 4 accepted events plus 1 duplicate.
  prediction: The offline architecture now demonstrates the intended first integration seam. The next risk is not another envelope but consumer behavior: a host-neutral reader must apply JSON/diff/revision data without blocking or executing actions. Qualitative confidence medium-high.
  next_action: Audit the active MOSAIK/VJ consumer commit and the active XIO source fixture once each has a new verifiable commit; otherwise continue strengthening FARMAXIA replay invariants without opening real network or GUI integrations.

agent_audit_2026_09_01:
  xio: origin/codex/xio-transport at f725626; 90 unittest pass. The checkout contains unrelated user worktree changes and none were staged.
  mosaik_vj: origin/LUCIDA at de2d827; targeted LUCIDA suite passes 93 pytest. The active checkout is IMAGO with 8 tests passing, so no IMAGO changes were treated as LUCIDA integration.
  correction: The first VJ audit accidentally ran from FARMAXIA and produced import-collection mismatches; it was discarded and repeated from a clean LUCIDA worktree.
  decision: Continue only from the published XIO and LUCIDA branches; do not merge IMAGO or unrelated local changes into FARMAXIA.

latest_hito_2026_09_01_pupila_lucida_consumer:
  selected_action: connect_pupila_diff_to_lucida_consumer
  own_change: Added an explicit lossy adapter from the bounded PUPILA view to the generic LUCIDA overlay contract, plus an integration check that feeds the resulting snapshot and diff into the real LUCIDA OverlayConsumer with its revision cursor.
  evidence: The check passes with two consented PUPILA participants, one shared-checkpoint proposal, one LUCIDA delta of four fields, proposal-only safety, no automatic actions, no external side effects and no raw payload forwarding. The FARMAXIA 090 contract remains valid with 19 tests.
  limitation: The adapter intentionally drops participant references, signal coverage, room, activity and source payloads. It is not a semantic claim that participants are host capabilities, and it does not execute or control the host application.
  prediction: The offline cross-repository seam is now demonstrated. The remaining high-risk work is runtime authentication and host rendering, not another schema; keep those out until the consumer contract is reviewed by the agent branch.
  next_action: Audit the next published LUCIDA consumer and XIO fixture commits once, then decide whether to promote this adapter into a shared package or keep it as an experiment boundary.

latest_hito_2026_09_01_atomic_overlay:
  selected_action: verify_atomic_lucida_update_consumption
  own_change: Updated the PUPILA-to-LUCIDA integration check to consume the new atomic update envelope containing view, complete diff and revision cursor. Added a tamper test proving a candidate view mismatch is rejected without mutating the consumer state.
  evidence: The check passes against MOSAIK/LUCIDA 49c982a: two PUPILA participants produce one shared-checkpoint proposal, one atomic update with four fields is applied, the tampered update is rejected atomically, safety remains proposal_only and the 090 contract remains at 19 passing tests.
  prediction: The first offline adapter seam is now robust enough for a review or shared-package decision. Runtime transport and GUI rendering remain separate risks and are not being introduced yet.
  next_action: Check whether XIO has published the replay fixture requested from f725626; if so, audit it once and connect only its deterministic source to the existing bridge.

latest_hito_2026_09_01_xio_handoff_store:
  selected_action: replay_persisted_xio_handoffs
  own_change: Extended the route handoff check to persist prepared XIO handoffs in the published JsonLineHandoffStore, restore them with an explicit caller identity, and feed only the restored redacted events into FARMAXIA.
  evidence: XIO origin/codex/xio-transport e6641ac passes 93 unittest. FARMAXIA route check passes with one restored handoff and two restored multi-participant handoffs; event content remains identical, projected payload keys remain empty, the audit verifies and executionAttempted remains false. The 090 contract remains valid with 19 tests.
  limitation: This proves restart-safe local replay only. It does not authorize delivery, open sockets, or establish authentication for a real network transport.
  prediction: Local persistence is now a usable bridge seam for LUCIDA/MULTI. The next meaningful risk is caller authorization and conflict handling at delivery time; it should be tested with explicit rejection before any real transport is enabled.
  next_action: Build one offline delivery-denial kill test using the restored handoff and a revoked capability, then audit the agent branches again after their next published commits.

latest_hito_2026_09_01_revoked_delivery:
  selected_action: deny_restored_handoff_before_transport
  own_change: Extended the persisted XIO handoff check with a revoked capability kill test. The restored handoff is passed to the delivery boundary, which must reject it before invoking the transport.
  evidence: The route check passes with deliveryStatus=rejected, revokedDeliveryTransportCalls=0, verified audit, one restored handoff and two restored multi-participant handoffs. FARMAXIA 090 remains valid with 19 tests. No socket or host side effect was attempted.
  prediction: The permission boundary behaves correctly for the local path. A real transport should remain disabled until authentication, expiry, replay protection and user-visible acceptance are specified as separate contracts.
  next_action: Audit the next XIO and LUCIDA commits once; if no new commits are ready, consolidate the offline checks into one reproducible integration command instead of adding another feature layer.

latest_hito_2026_09_01_offline_integration_command:
  selected_action: consolidate_offline_integration_checks
  own_change: Added one runner that executes the FARMAXIA contract, XIO route persistence and revoked-delivery boundary, PUPILA-to-LUCIDA atomic consumer check, and optionally the LUCIDA/MULTI transport check. It reports structured pass/fail status and explicitly records that no network, GUI or host action was opened.
  evidence: Core mode passes 3/3 checks. Extended mode passes 4/4 checks with a temporary origin/MULTI checkout: FARMAXIA contract 19 tests, XIO route/persistence/permission pass, LUCIDA atomic consumer pass, and LUCIDA/MULTI transport preserves 3 events, 2 participants and one shared-checkpoint proposal.
  prediction: The first offline vertical is now easy to rerun and audit; adding more abstraction before a real consumer need would have diminishing value. The next decision should be whether to promote the projection into a shared package after the agent branches stabilize.
  next_action: Keep the runner as the acceptance gate and audit the next published XIO/LUCIDA commits once; do not enable real network or GUI integration yet.
