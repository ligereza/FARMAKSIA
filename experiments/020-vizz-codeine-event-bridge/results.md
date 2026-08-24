# Resultados — experimento 020

El envelope opt-in VIZZ fue validado y sus tres eventos fueron normalizados al
contrato mínimo CODE-INE. El detector conservó la última mejora `s02` y dejó la
repetición no disponible porque solo existe un evento posterior (`s03`).

El puente descartó `objective_id`, `phase` y `display_condition` porque no son
necesarios para el detector actual; esa pérdida queda declarada y no se
interpreta como pérdida de comprensión humana. Cuando se elimina
`action_class`, el envelope VIZZ todavía puede ser válido, pero el puente
rechaza la conversión para no falsear la consulta de repetición.

No se iniciaron dispositivos, no hubo red ni captura cruda. La compatibilidad
de contratos queda demostrada sobre fixtures sintéticos; todavía no sabemos si
una sesión real puede emitir esas clases de acción sin interrumpirse.
