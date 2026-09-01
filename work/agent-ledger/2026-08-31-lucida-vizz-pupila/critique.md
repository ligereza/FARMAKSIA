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
next_checkpoint: Comparar respuestas de XIO/VJ y luego inspeccionar sólo diffs de sus ramas.
