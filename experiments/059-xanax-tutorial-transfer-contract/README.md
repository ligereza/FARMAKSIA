# Experimento 059 — contrato de transferencia de tutoriales X-ANA-X

## Pregunta

¿Una fuente pública declarada es suficiente para ejecutar un tutorial y puede
unirse de manera segura con un tutorial de otra aplicación?

## Diseño

El experimento usa tarjetas declarativas locales inspiradas en documentación
oficial de Maya y Blender. No descarga contenido, no abre aplicaciones, no usa
red, no observa a una persona y no ejecuta comandos externos. Compara cuatro
casos:

1. una tarjeta suficiente para construir un borrador de enseñanza;
2. una tarjeta sin postcondición, que debe quedar bloqueada;
3. dos tutoriales unidos por un artefacto y un contrato Maya→Blender;
4. dos tutoriales sin puente, que deben quedar bloqueados.

El caso compuesto usa una relación pedagógica `analogous` entre conceptos, pero
la ejecución sólo se habilita por el artefacto, las precondiciones y los
verificadores explícitos.

## Criterio

El resultado válido es:

```text
documento → TEACHING_DRAFT
documento + estado/adapter/verifier → DRY_RUN_READY
dos apps + BridgeContract verificable → COMPOSABLE_DRY_RUN
dos apps sin puente → BRIDGE_BLOCKED
```

Esto no demuestra comprensión humana, eficacia pedagógica ni ejecución real en
Maya o Blender. Es sólo una prueba de contrato para evitar que X-ANA-X salte
desde una explicación a una acción no verificada.

## Ejecutar

```text
python experiments/059-xanax-tutorial-transfer-contract/run_experiment.py
python experiments/059-xanax-tutorial-transfer-contract/run_kill_test.py
python experiments/059-xanax-tutorial-transfer-contract/run_contract_test.py
```
