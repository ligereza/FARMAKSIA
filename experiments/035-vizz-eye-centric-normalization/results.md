# Resultados VIZZ 035

El experimento sintético produjo `EYE_CENTRIC_VALID`.

- 3 transformaciones probadas: escala 0,5×/1×/2,5×, traslación y roll de
  0°/12°/-27°.
- Error máximo de invariancia: `8,77e-15`.
- Caso degenerado con distancia interocular nula: `UNKNOWN`,
  `interocular_distance_too_small`.
- No se abrieron dispositivos, no hubo cámara, no hubo datos humanos ni se
  guardaron frames.

La evidencia sólo valida la normalización 2D de la pareja ocular. No demuestra
que el detector real conserve landmarks bajo distancia, oclusiones, lentes o
giro 3D de la cabeza.
