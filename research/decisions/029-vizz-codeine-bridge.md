# Decisión 029 — VIZZ y CODE-INE pueden compartir eventos mínimos

Fecha: 2026-08-24

## Evidencia

El experimento 020 validó el envelope opt-in VIZZ y convirtió sus tres eventos
al detector CODE-INE usando solo `event_id`, `t_ms`, `action_class`, `gain` y
`errors`. El detector encontró `s02` como última mejora y dejó repetición no
disponible porque solo había un evento posterior.

La eliminación de `action_class` fue rechazada por el puente aunque VIZZ aún
aceptara el envelope. Esto evita que una pérdida de información se convierta
silenciosamente en una conclusión de estado.

## Decisión

Se adopta una frontera de interoperabilidad: una futura instrumentación manual
puede emitir un único envelope VIZZ y alimentar CODE-INE, sin duplicar captura,
sensores o permisos. El puente no rescata CODE-INE como operador ni demuestra
un estado humano; solo reduce duplicación de herramientas y hace explícito el
residuo.

## Próximo objetivo

Preparar un adaptador manual local que requiera consentimiento explícito,
registre solo eventos abstractos y no se ejecute hasta una acción deliberada del
usuario. Verificar después si una secuencia más larga permite repetir el
contrato CODE-INE sin inventar repetición, deriva o neuroquímica.
