# Resultados 060 — compilador de experiencia CODE-INE

## Registro

- fixture: `fixture.json`
- modo: local, determinista, dry-run
- datos humanos: `false`
- cámara: `false`
- red: `false`
- ejecución de código generado: `false`
- inferencia fisiológica/neuroquímica: `false`

## Evidencia computacional esperada

La traza sintética `start → failure → retry_allowed → success` debe compilar a:

```text
ready → working → blocked → retrying → verified
```

El oráculo independiente debe aceptar esa misma secuencia. El mapa conserva
cinco residuos: tres analogías con límites, una diferencia explícita y una
relación desconocida. El resultado esperado es
`COMPILED_VERIFIED_WITH_RESIDUE`.

## Desconocido

No se sabe todavía si esta representación facilita la comprensión, reduce la
repetición o cambia la experiencia subjetiva. El experimento sólo demuestra
que esas preguntas pueden separarse de la ejecución y medirse con contratos.
