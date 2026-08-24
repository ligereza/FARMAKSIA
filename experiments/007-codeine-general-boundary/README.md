# Experimento 007 — frontera amplia de CODE-INE

## Pregunta

¿CODE-INE es un operador conceptualmente distinto de un evaluador estándar de
valor de computación cuando incorpora continuación, cambio, reutilización,
detención, autoridad humana, irreversibilidad y valor de opción futura?

## Hipótesis operacional

La política candidata CODE-INE decide sobre acciones autorizadas usando
ganancia esperada, costo, crédito de reutilización, valor de opción e
irreversibilidad. Puede vetar una acción sin autoridad o con riesgo irreversible
por encima del umbral declarado.

El control es un evaluador exhaustivo de utilidad esperada con exactamente los
mismos campos y restricciones. No se le oculta ninguna transición: la
comparación prueba si el nombre añade una capacidad, no si una heurística tiene
un orden de preferencia distinto.

## Diseño

Seis escenarios cubren reutilización segura, opción futura, acción irreversible
vetada, autoridad humana ausente, detención por utilidad negativa y un empate
de reutilización. Se compara la acción elegida, las acciones descartadas y la
razón de descarte.

## Kill test

- Si ambos evaluadores coinciden en los casos sustantivos, CODE-INE no muestra
  una capacidad independiente.
- Si difieren únicamente por un bono, desempate o umbral configurable, la
  diferencia se clasifica como política/parametrización, no como operador nuevo.
- CODE-INE solo sobrevive como hipótesis independiente si conserva una
  propiedad que el evaluador con las mismas restricciones no puede expresar.

No se implementa un operador como API. El arnés solo mide una política
experimental frente a un control explícito.
