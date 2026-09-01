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
