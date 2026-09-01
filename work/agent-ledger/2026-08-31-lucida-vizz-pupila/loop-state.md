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

current_state:
  files_or_resources:
    - C:\IA\FARMAXIA
    - C:\IA\XIO
    - C:\IA\VJ
    - C:\IA\svg\agent-toolkit\generic-interface-layer
    - C:\IA\LUCIDA\ADOBE, RESOLUME y MULTI
  tests_and_checks: 090 pasa contrato offline con 13 tests, demo y cross-branch check con XIO real. XIO pasa 63 unittest; MOSAIK/VJ pasa 78 pytest; LUCIDA/RESOLUME pasa 63 pytest; LUCIDA/MULTI pasa 58 pytest/subtests; LUCIDA/ADOBE pasa verify, smoke, companion check y 11 tests. La suite completa de FARMAKSIA se detiene antes de 090 por un hash mismatch preexistente en la procedencia de X-ANA-X 018.
  assumptions: LUCIDA es el proyecto base conceptual; XIO y VJ deben conservar nombres propios de su eje en sus ramas derivadas; ZIGO es el origen histórico, no el nombre de los productos finales.
  open_questions:
    - Nombre definitivo de las ramas derivadas de XIO y VJ.
    - Qué partes mínimas de generic-interface-layer se incorporan a FARMAXIA sin acoplarlo a SVG.
  blockers: Suite global bloqueada en provenance 018; no tocar ese archivo porque contiene cambios previos del usuario. XIO conserva cambios de usuario sin stage. La publicación pesada de ADOBE puede tardar por sus 513 MiB de iconos visuales, pero la rama ya quedó confirmada en origin/ADOBE. Ninguna rama declara todavía integración real con sockets, router, Resolume o Adobe.
  research_refs: Extracción ZIGO en SVG y contratos actuales de XIO/VJ.
  delegation_refs: XIO y VJ recibieron tareas ejecutables con archivo objetivo, suite, commit y push; tras detectar turnos inactivos se corrigió la dirección. XIO entregó 1f543f9 y 173e96e; MOSAIK entregó abf4220 y e53166e. SVG finalizó la extracción y la verificación de ADOBE se hizo en el repositorio destino. Los cambios de capacidades, conectividad, frontera host, registro de adaptadores y overlay fueron auditados e integrados selectivamente en LUCIDA.
  last_critique: La hipótesis evento canónico universal tenía un riesgo real: transportar no implica que un dominio VJ deba interpretarlo como fase. La prueba cross-branch confirmó que la separación correcta es transportar y preservar provenance en MULTI, pero rechazar explícitamente el evento en RESOLUME. El puente 090 adopta el evento sólo como metadata para VIZZ/PUPILA y no reenvía payload crudo.
  estimated_remaining_effort: Medio-bajo para el primer vertical offline; alto para transporte real, overlays y outcomes de aprendizaje. El siguiente avance debe demostrar una ruta de señales de interacción observable y reversible, no más contratos abstractos.
  next_action: Mantener XIO en adaptadores por aplicación y MOSAIK en la proyección overlay, ambos con tareas no redundantes. En FARMAXIA, incorporar al bridge 090 el view model acotado y el registry como evidencias de origen, extender replay con señales pointer/keyboard/focus y probar la política VIZZ y la propuesta PUPILA por sesiones; dejar el transporte real fuera hasta fijar autenticación.
  next_checkpoint_trigger: Próxima revisión después de dos commits verificables de agentes o de la siguiente integración de 090.
