# Resultados — experimento 082

## Evidencia disponible

El programa nativo se compiló localmente con el mismo SDK, MSVC y paquete
CppWinRT que 081. El contrato estático confirma que el binario usa
`GraphicsCapturePicker.PickSingleItemAsync`, inicializado con su HWND dueño, y
que no contiene enumeración de ventanas, lectura de títulos, input inyectado,
red ni escritura de archivos.

Salida de compilación:

```text
FARMAXIA_082_SELECTED_WINDOW_PREVIEW_CONTRACT_VALID
FARMAXIA_082_BUILD_VALID
```

## Estado honesto

La parte interactiva aún no se ejecutó con una ventana del usuario. El binario
queda esperando deliberadamente el botón **Seleccionar ventana** y una decisión
humana en el picker del sistema. Por lo tanto, todavía no afirmamos:

- que una aplicación concreta de este equipo entregue frames;
- que el preview mantenga una latencia aceptable;
- que la fuente conserve su foco y input durante el preview;
- que el cambio de tamaño o cierre de la fuente se gestione correctamente.

Eso no es un resultado negativo: es una compuerta de consentimiento y evita
convertir una prueba no ejecutada en evidencia.

## Decisión siguiente

Cuando se ejecute manualmente, la primera observación será sólo espejo visual.
Si falla, el reordenamiento queda descartado para esa superficie. Si funciona,
se medirá latencia y frecuencia de frames antes de conectar UIA/OCR o un mapa
de interacción.
