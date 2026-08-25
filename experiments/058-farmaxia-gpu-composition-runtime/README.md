# 058 - Runtime GPU de composicion para FARMAXIA

Este experimento reemplaza el camino Python/NumPy de `057` para el overlay
continuo. No es una nueva app ni una interfaz independiente: es una capa
transparente sobre el escritorio y las aplicaciones existentes.

## Que cambia

- Ventana Win32 `WS_POPUP` transparente, sin foco y click-through.
- Una sola llamada de z-order al mostrarla; no se reordena por frame.
- Dispositivo D3D11 `Hardware` y shader HLSL de pantalla completa.
- Swap chain DXGI flip-sequential con alpha premultiplicado.
- Arbol retenido DirectComposition: el compositor conserva el visual y el
  proceso solo presenta cuando cambia el plan.
- El estado del foco ocupa un constant buffer pequeno; no se copia una imagen
  RGBA completa desde Python.
- Entrada opcional por stdin con JSONL local; no abre sockets, no usa camara y
  no guarda contenido de pantalla.

## Ejecutar

Desde PowerShell:

```powershell
dotnet run --project experiments/058-farmaxia-gpu-composition-runtime/058-farmaxia-gpu-composition-runtime.csproj -- --duration 10 --hz 30
```

Para probar la ruta retenida sin movimiento:

```powershell
dotnet run --project experiments/058-farmaxia-gpu-composition-runtime/058-farmaxia-gpu-composition-runtime.csproj -- --duration 10 --no-pointer
```

El modo `--stdin` recibe coordenadas fisicas del escritorio virtual, no
coordenadas relativas a un monitor:

```powershell
@('{"type":"focus","x":900,"y":500,"radius_px":320,"dim_alpha":0.12,"ring_alpha":0.04,"marker":false}'; '{"type":"stop"}') | dotnet run --project experiments/058-farmaxia-gpu-composition-runtime/058-farmaxia-gpu-composition-runtime.csproj -- --duration 60 --hz 30 --stdin
```

Los mensajes aceptados son `focus` y `stop`. `x` y `y` son coordenadas del
escritorio virtual de Windows; `radius_px`, `dim_alpha`, `ring_alpha` y
  `marker` son opcionales y se acotan antes de llegar al shader. El renderer
  no captura pantalla: solo recibe coordenadas y parametros del plan.

## Contrato de estabilidad

La condicion de salida de este experimento no es que el proceso compile. Debe
cumplir:

1. Una escena estatica no presenta continuamente.
2. El loop no llama `SetWindowPos` ni modifica el z-order.
3. Una actualizacion de foco cambia solo constantes y presenta como maximo a
   la frecuencia solicitada.
4. No hay alternancia de frames, captura de pantalla ni reconstruccion de
   buffers CPU.
5. El cierre destruye la ventana y libera el dispositivo.

El proceso informa `plans`, `presents`, mensajes y tiempo CPU del proceso. El
porcentaje GPU por motor queda como medicion externa de Windows; no se inventa
una cifra desde el proceso. Para validar consumo se debe comparar el contador
del motor 3D de Windows con `057` bajo el mismo movimiento y duracion.

## Limites

Esto demuestra una ruta de composicion estable, no precision de gaze ni una
politica visual definitiva. `--marker` es diagnostico y esta apagado por
defecto. Una aplicacion en modo fullscreen exclusivo puede no aceptar una
capa DWM. Un cambio de resolucion o layout de monitores requiere recrear el
runtime; la siguiente fase debe escuchar `WM_DISPLAYCHANGE` y versionar el
layout antes de usar coordenadas de gaze.

No se incorpora ningun modelo de deep learning en este renderer. El renderer
recibe un plan semantico ya decidido; esa separacion permite que VIZZ, X-ANA-X
y CODE-INE produzcan representaciones distintas sin dar acceso directo de
ejecucion al compositor.
