# Experimento 082 — preview pasivo de ventana seleccionada

## Propósito

Extender la prueba 081 desde una ventana creada por el laboratorio hasta una
ventana que el usuario selecciona explícitamente en el selector seguro del
sistema. Esta etapa sólo hace preview; no reordena, no intercepta input y no
guarda píxeles.

La selección la presenta `GraphicsCapturePicker`, no FARMAKSIA. Así el usuario
ve y autoriza el objetivo en la interfaz del sistema. La aplicación no enumera
ventanas, no lee títulos y no intenta adivinar qué programa está activo.

## Ejecutar

```powershell
powershell -ExecutionPolicy Bypass -File experiments/082-farmaxia-selected-window-preview/run_native_build.ps1
```

Para compilar sin abrir una ventana ni pedir selección humana:

```powershell
powershell -ExecutionPolicy Bypass -File experiments/082-farmaxia-selected-window-preview/run_native_build.ps1 -BuildOnly
```

El binario abre una ventana FARMAKSIA con un botón **Seleccionar ventana**.
Después de elegir una aplicación, muestra un preview pasivo. `Esc` o cerrar la
ventana detiene la sesión. No se envían clics ni teclas a la ventana elegida.

La compilación se puede verificar sin abrir el selector:

```powershell
python experiments/082-farmaxia-selected-window-preview/run_contract_test.py
python research/tools/validate_provenance.py experiments/082-farmaxia-selected-window-preview/provenance.json
```

## Por qué esta etapa está separada

El 081 responde si el renderer puede transformar regiones y conservar la
inversa. El 082 responde si puede recibir una fuente externa con consentimiento
sin convertir la observación en control. Si el preview no es estable, no tiene
sentido añadir semántica, analogías o input.

## Coste conocido

Este preview copia frames a memoria CPU para facilitar la inspección. No es el
backend de producción. La ruta GPU de 058 queda reservada para la siguiente
comparación de latencia y consumo; no se declara rendimiento a partir de este
prototipo.

## Kill tests

- Cancelar el selector no inicia captura.
- La fuente seleccionada no recibe input de FARMAKSIA.
- No se enumeran ni persisten títulos, texto o píxeles.
- Cerrar la fuente detiene el preview o lo marca como `UNKNOWN`.
- No se añade reordenamiento hasta que la sincronía de espejo sea verificable.
