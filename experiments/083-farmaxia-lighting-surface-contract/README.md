# Experimento 083 — contrato de superficie grandMA3 → Titan

## Propósito

Convertir la investigación de interfaz en un contrato verificable para una
capa que haga legible grandMA3 usando el vocabulario operativo de Avolites
Titan. No convierte showfiles, no modifica el motor de iluminación y no
pretende que dos objetos con nombres parecidos sean idénticos.

## Qué se implementó

El contrato cubre exactamente cinco tareas:

1. selección de fixtures o grupos;
2. control de atributos mediante el Programmer;
3. recuperación de un valor reutilizable;
4. lectura de cue y sequence/cue list;
5. identificación del executor/playback que controla una secuencia.

Cada región tiene origen, destino, rol, término de Titan, confianza y estado.
Los rectángulos están normalizados y tienen una transformación inversa; la
prueba no permite solapamientos de destino. Tres correspondencias se marcan
`partial` porque preset/palette, sequence/cue list y executor/playback no son
equivalencias estructurales completas.

## Ejecutar

```powershell
python experiments/083-farmaxia-lighting-surface-contract/run_experiment.py
python experiments/083-farmaxia-lighting-surface-contract/run_contract_test.py
python experiments/083-farmaxia-lighting-surface-contract/run_kill_test.py
python research/tools/validate_provenance.py experiments/083-farmaxia-lighting-surface-contract/provenance.json
```

## Alcance de la evidencia

El resultado es `LIGHTING_SURFACE_CONTRACT_VERIFIED` sobre un fixture
declarativo. No afirma que la UI real de grandMA3 o Titan haya sido observada,
que UIA exponga esos roles, ni que la traducción ayude a un operador humano.
La siguiente etapa es reemplazar regiones declarativas por observaciones
read-only de ventanas seleccionadas con el preview 082.
## Kill tests

- una región de destino solapada es rechazada;
- un task sin término de destino no se presenta como equivalente;
- `UNKNOWN` y `UNSUPPORTED` no pueden recibir confianza positiva;
- la capacidad `execute_blocked` es obligatoria;
- un destino diferente de Titan es rechazado;
- la cobertura incompleta de tareas es rechazada.
