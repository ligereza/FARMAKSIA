role: primary_agent
delegation_scope: Coordinar XIO y MOSAIK/VJ como fuentes separadas, extraer sólo contratos verificables hacia LUCIDA y mantener SVG limitado a la migración Adobe.
delegation_authority: Autorizada por el usuario para mantener vivos ambos agentes y trabajar en ramas separadas.
nested_delegation: forbidden
acceptance_test: Rama identificable, main intacto, tarea implementada con diff acotado, suite relevante ejecutada, commit descriptivo y push sólo de la rama de trabajo.
side_effect_limit: No borrar, resetear ni sobrescribir cambios; no copiar assets, obras, credenciales o corpus privados; no fusionar con LUCIDA.
review_boundary: Revisar rama, diff estadístico, referencias nominales, contratos, tests, artefactos excluidos y estado remoto de main.
status: completed_with_director_fallback

observed_results:
  - XIO: b8f8ba0 y 7a9dad3; 33 unittest; branch codex/xio-transport publicada.
  - MOSAIK: e43422d, 7daa9fb y 206b844; 34 pytest; branch LUCIDA publicada.
  - SVG: migracion Adobe aceptada en LUCIDA/ADOBE da90459; 11 tests, verify, smoke y companion check.
  - LUCIDA: RESOLUME 0864be1 y MULTI fb75553 publicados; ambas ramas se verificaron fuera de sus repositorios fuente.
next_delegation:
  - XIO: extender el gate opcional de capacidades sólo si aparece un caso de routing reproducible; probar compatibilidad hacia atras y no tocar transporte real.
  - MOSAIK: mantener la frontera no-VJ y añadir sólo pruebas que impidan convertir eventos de transporte en fases Resolume; no abrir host ni ejecutar acciones.
  - Director: auditar cada commit por diff, suite, push y ausencia de assets/credenciales antes de extraerlo a LUCIDA o FARMAXIA.
