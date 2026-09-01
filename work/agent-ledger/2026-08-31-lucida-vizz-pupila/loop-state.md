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

current_state:
  files_or_resources:
    - C:\IA\FARMAXIA
    - C:\IA\XIO
    - C:\IA\VJ
    - C:\IA\svg\agent-toolkit\generic-interface-layer
  tests_and_checks: 090 pasa py_compile, cinco contratos offline y procedencia. La suite completa se detiene antes de 090 por un hash mismatch preexistente en la procedencia de X-ANA-X 018.
  assumptions: LUCIDA es el proyecto base conceptual; XIO y VJ deben conservar nombres propios de su eje en sus ramas derivadas; ZIGO es el origen histórico, no el nombre de los productos finales.
  open_questions:
    - Nombre definitivo de las ramas derivadas de XIO y VJ.
    - Qué partes mínimas de generic-interface-layer se incorporan a FARMAXIA sin acoplarlo a SVG.
  blockers: Suite global bloqueada en provenance 018; no tocar ese archivo porque contiene cambios previos del usuario. XIO tiene cambios de usuario que no deben sobrescribirse.
  research_refs: Extracción ZIGO en SVG y contratos actuales de XIO/VJ.
  delegation_refs: XIO y VJ con límites de no-merge y no-main.
  last_critique: La orden anterior de renombrar VJ de forma aislada era técnicamente incompleta: el nombre LIMEN existe en dos repositorios y no debía cambiarse sin contrato común. La acción de menor riesgo es separar primero los ejes y renombrar sólo identidades propias en ramas nuevas.
  estimated_remaining_effort: Medio; primer hito verificable en una ronda de coordinación y una auditoría de integración.
  next_action: Esperar la respuesta de XIO/VJ y auditar sus ramas nuevas; luego decidir si el siguiente hito de FARMAKSIA es un transporte loopback observador para 090.
  next_checkpoint_trigger: Después de que ambos agentes respondan o tras la primera revisión de 5 minutos.
