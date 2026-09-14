# Integración con X-ANA-X

## Fuente canónica

La proyección integrada vive en:

https://github.com/ligereza/X-ANA-X/tree/FARMAKSIA

X-ANA-X/FARMAKSIA es la superficie investigativa del motor: hipótesis,
experimentos, contratos, procedencia, kill tests y evidencia. No es el
runtime de escritorio ni el transporte móvil.

## Mapa de ramas de este repositorio

Todas las ramas de investigación desembocan en la única rama de integración
FARMAKSIA de X-ANA-X. La selección debe hacerse por commit y evidencia, no
por copiar el árbol completo sin revisión.

| Rama | Uso | Destino |
|---|---|---|
| main | Base del laboratorio | X-ANA-X/FARMAKSIA |
| fix/provenance-integrity | Procedencia y suite actual | X-ANA-X/FARMAKSIA |
| codex/obras-experimental-rehearsal-farmaxia-root | Snapshot experimental integrado | X-ANA-X/FARMAKSIA |
| codex/direct-iris-public-scope-20260907 | Alcance público de IRIS | X-ANA-X/FARMAKSIA |
| codex/iris-farmaksia-integration | Adaptación IRIS | X-ANA-X/FARMAKSIA |
| codex/public-scope | Alcance público y retiros | X-ANA-X/FARMAKSIA |
| codex/pupila-farmaksia-integration | Puente temporal de asistencia | X-ANA-X/FARMAKSIA |

El snapshot integrado no convierte cada experimento en una función del
runtime. FARMAKSIA entrega evidencia y límites; PUPILA y LUCIDA deciden si
existe un consumidor válido.

## Cómo portar trabajo

- Un experimento nuevo debe conservar su README, entrada, salida y criterio
  de kill.
- Una decisión que cambia el contrato común se porta como decisión explícita
  a X-ANA-X/FARMAKSIA.
- Una hipótesis no se mueve a PUPILA o LUCIDA como capacidad hasta que tenga
  consumidor, prueba y límite verificable.
- Registrar siempre el commit de origen y el commit de integración.

## Validación

Desde la raíz:

python research/tools/run_suite.py

La suite debe declarar los pasos no disponibles por plataforma; un skip
explícito no equivale a una prueba física realizada.
