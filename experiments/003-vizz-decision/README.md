# Experimento 003 — VIZZ más allá del gráfico

## Pregunta

¿Una representación que integra trayectoria, incertidumbre y alternativas
modifica la decisión humana más que una tabla o un gráfico estático?

## Fixture

`decision-state.json` describe cuatro ramas de un proceso creativo, sus costos,
calidad parcial, incertidumbre y posibilidad de reutilización. El fixture es
pequeño y completamente inspeccionable.

## Condiciones experimentales

1. **Tabla:** valores numéricos sin encoding relacional.
2. **Gráfico estático:** relaciones y trayectoria en una imagen fija.
3. **VIZZ candidato:** vista enlazada con trayectoria, incertidumbre, costo,
   historial y selección de una acción.

Las tres condiciones deben recibir exactamente el mismo estado computacional.
VIZZ puede cambiar el acceso perceptual y la interacción, pero no debe añadir
información que las otras condiciones no reciban.

## Tarea humana

La persona debe elegir entre continuar, cambiar, reutilizar o detenerse, y
explicar qué evidencia motivó la elección. Debe registrar también confianza y
tiempo.

Para permitir una medición controlada, el piloto usa una regla analítica
declarada en `decision-state.json`: `expected_gain + reuse_credit - 0.1 * cost`.
En este fixture la respuesta de referencia es `reuse-C`. Esta regla no pretende
definir valor artístico ni invalidar una preferencia humana distinta; solo
permite medir error en una tarea experimental pequeña.

## Medidas

- decisión correcta según una regla de tarea previamente declarada;
- tiempo hasta decisión;
- error;
- confianza calibrada;
- detección de incertidumbre;
- uso de una relación relevante;
- cambios de decisión durante la interacción;
- explicación y autoridad humana conservada.

La confianza se registra separadamente de la respuesta de referencia. Una
persona puede discrepar de la regla analítica y explicar por qué; esa discrepancia
es un dato, no una falla artística.

## Kill test

VIZZ muere como operador independiente si:

- no mejora decisión, tiempo, error o calibración frente a la vista estática;
- la mejora proviene de información extra y no del modo de representación;
- la persona no puede reconstruir por qué tomó la decisión;
- el sistema sustituye el juicio humano en lugar de externalizar estructura.

## Estado

Las tres condiciones ya fueron generadas y verificadas por paridad de
información. Los resultados automatizados están en `results.md`. La prueba
humana sigue pendiente; el instrumento offline `pilot.html` ya está listo, pero
no se afirma todavía que VIZZ mejore decisiones. `analyze_pilot.py` queda listo
para consumir los JSON exportados sin modificar la evidencia original.
