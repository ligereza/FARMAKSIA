# Experimento 060 — compilador de experiencia CODE-INE

## Pregunta

¿Puede CODE-INE convertir una intención humana declarada en una estructura de
construcción verificable y, al mismo tiempo, producir una representación con
foco, ritmo, densidad y pausa sin inferir un estado psicológico?

## Decisión

Este experimento abre un camino nuevo para CODE-INE. La unidad no es un botón,
un fragmento de código ni una ventana emergente: es un **plan de construcción
con experiencia**.

```text
intención
  → perfil de entrada declarado
  → mapa contrastivo (equivalente / análogo / diferente / desconocido)
  → residuo semántico
  → máquina de estados declarativa
  → oráculo independiente
  → plan de representación reversible
```

La analogía del fixture parte de una política de juego arcade y la traduce a
un ciclo de trabajo confiable. No se transfieren controles; se transfiere una
relación: objetivo activo, cambio de estado, fallo observable y recuperación
acotada. El experimento deja explícito dónde la analogía se rompe.

## Composición FARMAKSIA

Este vertical slice fija una frontera entre los tres compuestos:

```text
X-ANA-X  → mapa contrastivo y residuo semántico
CODE-INE → máquina de estados, artefacto y oracle
VIZZ     → plan de foco, capas, ritmo, movimiento y pausa
```

Si falta el mapa, CODE-INE no inventa una analogía. Si falta el oracle, no
declara construcción verificada. Si falta VIZZ, el resultado sigue siendo
usable como texto/código estático: la experiencia adaptativa no es un permiso
para ocultar la estructura.

## Qué aporta la capa informática

- `semantic_map`: conserva relaciones y diferencias en vez de colapsarlas en
  una explicación bonita;
- `declarative_state_machine`: produce una estructura inspeccionable antes de
  generar código de una aplicación;
- `objective_oracle.py`: verifica la traza con reglas independientes del
  compilador;
- `dry_run_only`: evita que un tutorial o un agente salte a ejecutar acciones
  reales sin adaptador, permiso y postcondición;
- `complexity_budget`: limita cuántos conceptos y capas pueden competir por el
  foco al mismo tiempo.

## Qué aporta la capa sensorial

La sensación se modela como una política de representación, no como una
lectura del cuerpo:

- foco en la transición activa;
- revelación progresiva `signal → structure → detail`;
- tempo declarado (`deliberate`, `normal` o `fast`);
- movimiento reducido, de trazo o completo;
- peso de atención limitado y sin destellos periódicos;
- señal visible para analogía, residuo, desconocido y verificado;
- pausa contextual cuando la persona declara estar atascada;
- `preview`, `accept`, `revert`, `reduce_motion` y `show_full`.

No se usan cámara, pupila, mouse, teclado, telemetría, red ni inferencia de
ansiedad, intoxicación, diagnóstico, emoción o neuroquímica. La capa puede
representar una experiencia más pausada o más intensa, pero no afirma que una
persona la sienta de una manera determinada.

## Ejecución

Desde la raíz:

```powershell
.\.venv\Scripts\python.exe experiments/060-codeine-experience-compiler/run_experiment.py
.\.venv\Scripts\python.exe experiments/060-codeine-experience-compiler/run_contract_test.py
.\.venv\Scripts\python.exe experiments/060-codeine-experience-compiler/run_kill_test.py
```

## Resultado aceptable

```text
COMPILED_VERIFIED_WITH_RESIDUE
```

`WITH_RESIDUE` es deliberado: una analogía útil no es una equivalencia total.
El estado sólo es válido si la máquina compilada y el oráculo independiente
producen la misma traza y la representación conserva reversibilidad.

## Kill tests

1. Una relación no equivalente sin residuo bloquea la compilación.
2. Alterar la transición de fallo crea una traza distinta de la esperada.
3. Quitar `revert` bloquea la política de representación.
4. Añadir destellos periódicos bloquea la política sensorial.
5. Un evento sin regla independiente queda `BLOCKED`, no se inventa una salida.
6. No se ejecuta código generado ni se autoriza una aplicación real.

## Qué demuestra y qué deja abierto

Demuestra un contrato computacional que une semántica, construcción,
verificación y representación sensorial. No demuestra que la analogía mejore
el aprendizaje, que el ritmo reduzca ansiedad ni que una interfaz sea más
agradable. Esas son hipótesis humanas posteriores y requieren un protocolo
separado, consentimiento y métricas no basadas sólo en auto-reporte.
