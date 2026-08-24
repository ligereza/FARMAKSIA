# Decisión 037 — CODE-INE separa score declarado de objetivo verificado

Fecha: 2026-08-24

El experimento 027 sometió la señal objetiva de CODE-INE a una compuerta de
oráculo separada. Reutilizó la sesión sintética VIZZ 022 y conservó la
transición base `c04 → c07` en todos los perfiles.

## Evidencia

| Perfil | Resultado |
|---|---|
| score y oracle estables | `verified / stable` |
| score y oracle regresan | `verified / regressed` |
| score y oracle se recuperan | `verified / recovered` |
| score sin oracle | `declared_only` |
| score y oracle discrepan | `conflict` |
| oracle incompleto | `unavailable` |
| oracle mal formado | `rejected` |

La matriz completa produjo `verified=3`, `declared_only=1`, `conflict=1`,
`unavailable=1` y `rejected=1`. Los kill tests confirmaron que un score sin
oracle no cruza la compuerta, un conflicto no emite deriva verificada y los
oracles incompletos o inválidos fallan cerrado.

## Decisión

CODE-INE conserva dos capas distintas: una transición base derivada del
evento y un objetivo declarado que solo puede etiquetarse `verified` cuando
coincide con un oracle completo dentro del fixture. La palabra `verified` no
significa que la tarea sea independiente de sesgo, que represente comprensión
humana o que mida ansiedad, intoxicación, sedación, neurotransmisores o
farmacología.

## Siguiente compuerta

Antes de usar `verified` en una sesión futura habrá que especificar quién o qué
produce el oracle, sus criterios de aceptación y su procedencia. No se
incorporan texto personal, captura, eye tracking ni participantes por esta
decisión.
