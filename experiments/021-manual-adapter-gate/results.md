# Resultados — experimento 021

El adaptador bloqueó la ejecución sin `--consent`, validó tres eventos
abstractos con consentimiento explícito y completó un dry-run sin escribir el
archivo de salida. También rechazó un campo `text` y protegió un archivo
existente contra sobreescritura.

| Compuerta | Resultado |
|---|---|
| consentimiento ausente | bloqueado |
| envelope opt-in | válido, 3 eventos |
| dry-run | válido, 0 archivos creados |
| payload crudo | rechazado |
| salida existente | protegida |

No se inició una sesión real, no se usó red ni dispositivo y no hubo datos
humanos. La herramienta está preparada para una acción deliberada posterior;
su existencia no demuestra que una persona pueda o quiera registrar eventos sin
interrumpir la tarea.
