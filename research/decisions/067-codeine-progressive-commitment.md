# Decisión 067 — compromiso progresivo para CODE-INE

Fecha: 2026-08-27

## Decisión

FARMAKSIA adoptará una **escalera de compromiso**. La ambigüedad no es un
error cuando el sistema sólo representa, compara o ayuda a formar una
dirección. La exigencia aumenta cuando el sistema recomienda una dirección,
construye, ejecuta o afirma éxito.

```text
REPRESENTAR una posibilidad
  ≠ RECOMENDAR una dirección
  ≠ CONSTRUIR una solución
  ≠ EJECUTAR una acción
  ≠ AFIRMAR éxito
```

La respuesta experta mejora la decisión 066, pero se incorpora con una
precaución: `ActionContract` no será la unidad universal. Gobernará el
compromiso y la ejecución; no bloqueará la exploración reversible.

## Estado de interacción

La sesión no se etiqueta como “novato”, “experto” o una categoría psicológica.
Se representa mediante tres ejes:

```text
intent maturity:
    emergent → provisional → committed

outcome verifiability:
    open → constrained → verifiable

action risk:
    representational | reversible | consequential
```

Estos ejes no forman una sola escala. Una intención puede ser provisional pero
tener un resultado abierto; una representación puede ser clara aunque la
tarea todavía no esté comprometida. La persona puede reformularse en futuras
revisiones; la madurez descriptiva no debe transformarse en una obligación
irreversible.

## Política por fase

| Fase | Puede hacer | No puede hacer sin elevar compromiso |
|---|---|---|
| `EMERGENT` | representar, sugerir, comparar, ramificar | ejecutar o presentar una dirección como definitiva |
| `PROVISIONAL` | comparar, editar, hacer preview, construir borradores | ejecutar cambios no autorizados |
| `COMMITTED` | construir, dry-run, ejecutar si el riesgo y el contrato lo permiten, verificar | afirmar éxito sin evidencia |

Regla principal:

```text
verification gates commitment
verification does not gate reversible representation
```

## Representación ramificada

`RepresentationPlan` deja de ser siempre un único resultado:

```text
RepresentationSpace
  ├─ mapa de relaciones
  ├─ secuencia guiada
  ├─ analogía contrastiva
  └─ vista completa
```

Las ramas no seleccionadas reciben:

```text
not_selected_in_this_context
```

y no:

```text
wrong
```

Cada rama debe conservar los mismos identificadores y declarar foco, tempo,
movimiento, densidad, anclas, desconocidos y reversibilidad. VIZZ puede
renderizar el espacio de posibilidades sin pretender conocer todavía el
objetivo final. X-ANA-X puede ampliar relaciones, contrastes y residuos.

## Revisiones como parches

La intención se conserva como historial versionado. El experimento 061 usa una
implementación local mínima de operaciones compatibles con [RFC 6902](https://www.rfc-editor.org/info/rfc6902): `add`, `replace` y `remove`.

```text
Intent v1
  ├─ patch A → Intent v2A
  └─ patch B → Intent v2B
```

Esto permite comparar, volver atrás, combinar y conservar la trayectoria sin
confundir una revisión abandonada con un resultado incorrecto.

No se añade todavía `python-json-patch` como dependencia: el contrato local es
pequeño y la biblioteca sólo se evaluará cuando existan necesidades de
interoperabilidad o persistencia real.

## Acción y verificación

Cuando la sesión alcanza `COMMITTED`, la ejecución requiere:

```text
preconditions
operation
expected_postconditions
forbidden_postconditions
verification_method
risk_class
reversibility
authorization
```

El flujo conserva la separación:

```text
ProcessVerification
    la representación/acción estaba justificada

OutcomeVerification
    la postcondición ocurrió

EnvironmentStatus
    el entorno permitió o impidió el resultado
```

Una acción puede ser correcta pero fallar por el entorno. Eso no debe
retroalimentar al sistema como una mala analogía o una mala recomendación.

## Composición de los tres compuestos

```text
X-ANA-X
  expande relaciones, alternativas, analogías, contrastes y residuos

VIZZ
  hace perceptibles las posibilidades, anclas, cambios y rutas de regreso

CODE-INE
  formaliza gradualmente, construye previews y exige contrato al ejecutar
```

La composición completa ya no es una tubería que siempre converge:

```text
estado informal
   ↓
posibilidades
   ↓
comparación / reflexión
   ↓
intención provisional
   ↓
preview / rama
   ↓
intención comprometida
   ↓
acción proporcional al riesgo
   ↓
verificación
```

## Experimento 061

El vertical slice está en
`experiments/061-codeine-progressive-commitment/`. Usa una sesión sintética
de cinco revisiones y cuatro planes de representación. El resultado esperado
es:

```text
PROGRESSIVE_COMMITMENT_VERIFIED
```

Esto demuestra sólo que el contrato permite ambigüedad al inicio y rigor al
final. No demuestra creatividad, comprensión, comodidad ni aprendizaje
humano.

## Qué se descarta por ahora

- no se usa `OR-Tools` para ordenar creatividad abierta;
- no se entrena un modelo para adivinar la intención de la persona;
- no se exige UIA, cámara o aplicación real para validar esta capa conceptual;
- no se mide permanencia, clicks o estimulación como objetivo principal;
- no se convierte una elección del usuario en una etiqueta de “correcto”;
- no se ejecuta código generado dentro del experimento.

## Kill tests de dirección

- Si FARMAKSIA bloquea toda intención emergente, se rechaza la arquitectura.
- Si converge a una única propuesta antes de que exista compromiso, aumenta
  `premature_commitment_rate` y se rechaza la política.
- Si una rama no seleccionada se elimina o se marca como errónea sin evidencia,
  se rechaza la representación.
- Si una acción de alto riesgo cruza sin contrato, autorización y verificador,
  se bloquea.
- Si el sistema declara éxito mirando sólo su propia pantalla, la evidencia
  es insuficiente.

## Siguiente frontera

El siguiente experimento debe renderizar el `RepresentationSpace` del 061
usando el renderer local ya existente, con tres controles explícitos:

```text
explorar ramas
comparar
comprometer una dirección
```

Sólo después de comprobar que las ramas, revisiones y reversión permanecen
legibles se conectará una aplicación real. La primera aplicación candidata
será una superficie reversible y observable, no una acción destructiva.
