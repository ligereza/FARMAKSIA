# Resultados 065

## Resultado reproducible

`CROSS_APPLICATION_EVIDENCE_VERIFIED`

La ejecución local procesó cuatro entregas sintéticas: tres eventos únicos y
una reentrega duplicada. La entrada llegó fuera de orden y el normalizador la
convirtió en la secuencia canónica `ev-mr-open → ev-pipeline-fail →
ev-mr-comment`. El evento repetido no creó una segunda entidad ni una segunda
afirmación.

La representación produjo tres claims con referencias calificadas a proyecto,
tipo e ID. La propuesta de notificación fue `DRY_RUN_ONLY`, con precondición de
versión 42 y confirmación explícita. El verificador independiente consultó el
almacén sintético de GitLab y confirmó: merge request abierta, pipeline fallido,
permiso de publicación disponible y ausencia de efecto externo.

La salida de seguridad confirmó:

```text
network_used=false
external_execution=false
human_data=false
camera_used=false
source_write_attempted=false
```

## Kill tests

`FARMAXIA_065_KILL_TESTS_VALID`

Se bloquearon ocho mutaciones: identidad de proyecto ausente, escritura fuera
de dry-run, claim sin procedencia, precondición obsoleta, reentrega con payload
conflictivo, permiso Mattermost ausente, éxito declarado sin observar efecto y
referencia no calificada.

## Evidencia y límite

Este resultado demuestra una frontera de ingeniería: dos superficies pueden
unirse mediante un modelo intermedio auditable sin convertir la representación
en fuente de verdad. No demuestra todavía interoperabilidad real, OAuth,
firmas de webhooks, resolución institucional de roles, comprensión humana ni
mejora frente a las interfaces nativas.
