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

current_state:
  files_or_resources:
    - C:\IA\FARMAXIA
    - C:\IA\XIO
    - C:\IA\VJ
    - C:\IA\svg\agent-toolkit\generic-interface-layer
    - C:\IA\LUCIDA\ADOBE, RESOLUME y MULTI
  tests_and_checks: 090 pasa py_compile, seis contratos offline y procedencia. XIO pasa 39 unittest; MOSAIK/VJ pasa 43 pytest; LUCIDA/RESOLUME pasa 32 pytest; LUCIDA/MULTI pasa 39 unittest; LUCIDA/ADOBE pasa verify, smoke, companion check y 11 tests. La suite completa de FARMAKSIA se detiene antes de 090 por un hash mismatch preexistente en la procedencia de X-ANA-X 018.
  assumptions: LUCIDA es el proyecto base conceptual; XIO y VJ deben conservar nombres propios de su eje en sus ramas derivadas; ZIGO es el origen histórico, no el nombre de los productos finales.
  open_questions:
    - Nombre definitivo de las ramas derivadas de XIO y VJ.
    - Qué partes mínimas de generic-interface-layer se incorporan a FARMAXIA sin acoplarlo a SVG.
  blockers: Suite global bloqueada en provenance 018; no tocar ese archivo porque contiene cambios previos del usuario. XIO conserva cambios de usuario sin stage. La publicación pesada de ADOBE puede tardar por sus 513 MiB de iconos visuales, pero la rama ya quedó confirmada en origin/ADOBE.
  research_refs: Extracción ZIGO en SVG y contratos actuales de XIO/VJ.
  delegation_refs: XIO y VJ recibieron tareas ejecutables con commits, suites y límites de no-main; tras detectar turnos inactivos se reactivaron con entregables concretos. SVG finalizó la extracción y la verificación de ADOBE se hizo en el repositorio destino. La última ronda volvió a activar XIO para un probe de conectividad inyectable y MOSAIK para reforzar el host boundary de Resolume.
  last_critique: La orden anterior de renombrar VJ de forma aislada era técnicamente incompleta: el nombre LIMEN existe en dos repositorios y no debía cambiarse sin contrato común. La acción de menor riesgo es separar primero los ejes y renombrar sólo identidades propias en ramas nuevas.
  estimated_remaining_effort: Medio; separación, publicación e integración mínima ya verificadas. Resta probar la interoperabilidad con un contrato de capacidad de red y endurecer la frontera de host antes de abrir una integración real.
  next_action: Esperar la siguiente entrega ejecutable de XIO y MOSAIK, verificar sus diffs y suites, integrar sólo los contratos compatibles en LUCIDA, y después activar el primer slice verificable de VIZZ/PUPILA sobre eventos replayables sin introducir captura invasiva.
  next_checkpoint_trigger: Después de que ambos agentes respondan o tras la primera revisión de 5 minutos.
