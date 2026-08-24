# Decisión 035 — la condición de display no cambia la semántica ni diagnostica un estado

Fecha: 2026-08-24

## Evidencia

El experimento 025 comparó seis perfiles sintéticos:

- texto completo de día, tarde y noche: cuatro condiciones disponibles en la
  matriz completa, todas con el mismo fingerprint semántico;
- foco nocturno con `c04–c08`: consulta disponible, contexto anterior explícito
  como perdido;
- foco nocturno sin `c04`: `unavailable`;
- campo nocturno: `unavailable`.

Todos los perfiles conservaron o rechazaron la consulta sin alterar los datos.
Ninguno produjo una afirmación fisiológica, farmacológica u óptica.

## Decisión

VIZZ puede tratar luminancia, contraste, escala y composición cromática como
metadatos de presentación. La condición `night` debe representar una
condición de display, no un diagnóstico de pupila, melatonina, fatiga,
ansiedad, intoxicación o consumo de sustancias.

Una receta de lentes no se aplica desde la interfaz. La representación puede
ajustar tamaño y espaciado para una distancia de trabajo declarada, pero la
corrección clínica y el confort quedan fuera de la evidencia computacional.

El foco solo entrega una consulta cuando conserva los elementos requeridos;
los residuos de contexto deben permanecer visibles en el contrato.

## Próxima compuerta

Antes de una evaluación humana se requerirían una tarea concreta,
consentimiento, horario/luminancia controlados y criterios explícitos de
seguridad. No se adopta eye tracking ni se generan datos humanos en este ciclo.
