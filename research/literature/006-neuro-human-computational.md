# Investigación 006 — neurociencia y estados humano-computacionales

Fecha: 2026-08-23

## Pregunta

¿Qué evidencia científica permite estudiar CODEINE y XANAX sin afirmar que
programar o usar una analogía equivale a liberar un neurotransmisor específico?

## Resultado principal

No existe evidencia de un “neurotransmisor del código”. Los estudios directos
de comprensión de código muestran activación de redes ejecutivas,
frontoparietales y de control de errores, no una firma farmacológica única.
La química sirve como contexto y como hipótesis de mecanismo, pero los
prototipos FARMAXIA deben medir comportamiento, tarea y percepción, no inferir
concentraciones cerebrales desde logs.

## Código y comprensión

- Ivanova et al. encontraron que Python y ScratchJr reclutan principalmente el
  sistema de demanda múltiple, más que el sistema lingüístico:
  https://elifesciences.org/articles/58906
- Liu et al. relacionaron la comprensión de código con una red frontoparietal
  usada también en inferencia lógica formal:
  https://elifesciences.org/articles/59340
- La detección de bugs recluta la ínsula y una dinámica de monitorización de
  errores con influencia frontal:
  https://pubmed.ncbi.nlm.nih.gov/35321263/

Esto convierte a “comprender”, “detectar error” y “mantener el objetivo” en
variables más defendibles que “dopamina del programador”.

## Sistemas neuroquímicos relevantes, con cautela

| Sistema | Relación plausible | No permite concluir |
|---|---|---|
| Dopamina | recompensa esperada, error de predicción y disposición a invertir esfuerzo | que una sucesión de commits sea una medición de dopamina |
| Noradrenalina / locus coeruleus | arousal, selección atencional, respuesta a demanda y pupila | que una pupila grande sea ansiedad o concentración por sí sola |
| Acetilcolina | atención y actualización frente a incertidumbre, especialmente en modelos de precisión | que una búsqueda web mida acetilcolina |
| GABA / glutamato | equilibrio inhibición-excitación y control; asociaciones con ansiedad y fármacos | que “calma cognitiva” sea igual a sedación farmacológica |
| Serotonina | modulación de amenaza, aprendizaje y ansiedad en circuitos distribuidos | una explicación unitaria de no entender algo |
| Adenosina y melatonina | presión de sueño y sincronización circadiana, relevantes para sesiones nocturnas | que sean equivalentes a sedación o a un estado artístico |

Fuentes de apoyo: esfuerzo y dopamina,
https://pubmed.ncbi.nlm.nih.gov/26889810/; pupila y locus coeruleus,
https://pubmed.ncbi.nlm.nih.gov/24692319/; incertidumbre y control,
https://pmc.ncbi.nlm.nih.gov/articles/PMC3184613/; consenso sobre la
neurobiología de la ansiedad,
https://pubmed.ncbi.nlm.nih.gov/27419272/.

## Hipótesis operacional para CODEINE

CODEINE puede investigarse como una transición observable entre:

1. producción rápida con mejora verificable;
2. acumulación de actividad con mejora decreciente;
3. repetición, mantenimiento o reparación sin reevaluación del objetivo;
4. pérdida de comprensión o deriva respecto del objetivo inicial.

Variables candidatas: tiempo entre iteraciones, cambios aceptados y revertidos,
tests pasados y fallidos, distancia desde la última mejora significativa,
repetición de herramientas, complejidad, comentarios de objetivo,
interrupciones, consultas externas, errores reintroducidos y proporción entre
creación y mantenimiento.

La variable central no será “velocidad”, sino la relación entre actividad,
mejora y comprensión declarada. El rush productivo requiere ganancia; la
sedación computacional puede tener mucha actividad con ganancia estancada.

## Hipótesis operacional para XANAX

Una analogía puede reducir fricción al permitir recuperar una estructura
conocida, pero también puede producir una sensación de comprensión sin
transferencia correcta. Por eso XANAX debe registrar la cadena:

`confusión → fuente/analogía → mapeo relacional → predicción → verificación → ruptura`

No se usará neuroquímica para afirmar que una explicación “calmó” al usuario.
La primera versión medirá comprensión provisional, transferencia y detección
del punto de ruptura.

## Límite científico

Pupila, ritmo, errores y logs son proxies de estado. Son útiles para generar y
comparar hipótesis, pero no diagnostican ansiedad, intoxicación, dopamina,
noradrenalina ni ningún trastorno. Cualquier medición neurofisiológica humana
futura requeriría protocolo, consentimiento y revisión ética fuera del alcance
del prototipo local.
