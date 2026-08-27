# Experimento 061 — compromiso progresivo CODE-INE

## Pregunta

¿Puede FARMAKSIA ser útil cuando la intención todavía está formándose y, al
mismo tiempo, aumentar la exigencia antes de construir, ejecutar o declarar
éxito?

## Principio

La verificación gobierna el compromiso, no la representación.

```text
intención informal
  → posibilidades y alternativas
  → comparación y contraste
  → preferencia provisional
  → preview reversible
  → intención comprometida
  → acción con contrato
  → verificación
```

El fixture representa una única sesión en la que una persona comienza sin
saber exactamente qué quiere hacer con una escena 3D. La intención madura sin
destruir revisiones anteriores. No se ejecuta Blender ni se pretende demostrar
que la persona aprendió o produjo una obra mejor.

## Tres ejes

La tarea no se encierra en una etiqueta fija. Cada revisión conserva tres
dimensiones independientes:

```text
intent maturity:       emergent | provisional | committed
outcome verifiability: open | constrained | verifiable
action risk:           representational | reversible | consequential
```

La misma sesión puede comenzar como exploración y terminar como una acción
verificable. También puede volver atrás en una futura versión; la revisión
actual no trata la madurez como una obligación irreversible.

## Qué demuestra

- `Intent` acepta ambigüedad explícita, alternativas y desconocidos;
- cuatro planes pueden ofrecerse antes de elegir una dirección;
- no seleccionar un plan no lo convierte en incorrecto;
- la representación mantiene foco, tempo, movimiento y densidad declarados;
- `preview`, `build` y `execute_if_authorized` aparecen sólo cuando madura la
  intención;
- el contrato final exige precondiciones, postcondiciones, reversibilidad y
  verificador;
- la traza se valida con un oracle independiente.

La métrica `premature_commitment_rate_fixture` sólo describe este fixture
sintético; no es una medición humana ni una demostración de creatividad.

## Ejecución

Desde la raíz:

```powershell
.\.venv\Scripts\python.exe experiments/061-codeine-progressive-commitment/run_experiment.py
.\.venv\Scripts\python.exe experiments/061-codeine-progressive-commitment/run_contract_test.py
.\.venv\Scripts\python.exe experiments/061-codeine-progressive-commitment/run_kill_test.py
```

## Límites y kill tests

1. Comprometer la intención antes de que exista una dirección bloquea el
   experimento.
2. Eliminar alternativas convierte la exploración en convergencia forzada y
   bloquea el contrato.
3. Un parche JSON inválido no puede producir una revisión silenciosa.
4. Un `ActionContract` sin verificador no puede cruzar a construcción final.
5. Una acción consecuencial sin autorización explícita queda bloqueada.
6. Ejecutar o hacer dry-run antes del compromiso queda bloqueado.

No hay cámara, red, datos humanos, ejecución de código generado ni inferencia
de estados psicológicos. La siguiente etapa es renderizar el espacio de
posibilidades y sus revisiones en el renderer local de FARMAKSIA, sin conectar
todavía una aplicación real.
