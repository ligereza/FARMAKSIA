# Resultados — experimento 015

El validador aceptó el envelope seguro por defecto (cero eventos) y el
envelope opt-in con tres eventos abstractos. Rechazó el caso adversarial que
intentaba introducir `text` dentro del payload.

| Caso | Resultado | Eventos | Interpretación |
|---|---:|---:|---|
| captura desactivada | válido | 0 | la ausencia de consentimiento deja el registro vacío |
| opt-in de eventos de tarea | válido | 3 | permite tiempo relativo, fase, acción, ganancia y errores |
| texto crudo | rechazado | — | el contrato no acepta contenido personal |

La prueba no inició dispositivos, no usó red y no recogió datos humanos. La
instrumentación queda preparada como interfaz de eventos, no como capturador de
pantalla, teclado, webcam o mirada. Todavía no sabemos si estos eventos son
suficientes para representar una sesión real ni si una persona encontraría útil
la adaptación resultante.
