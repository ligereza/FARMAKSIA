# Decision 063 - Overlay retenido y GPU-first para FARMAXIA

## Estado

Provisional: implementado como experimento `058`; no es aun runtime de
produccion.

## Problema observado

El runtime `057` generaba en Python una imagen BGRA de escritorio completo y
la enviaba repetidamente mediante `UpdateLayeredWindow`. Ademas, el parche de
visibilidad revalidaba el z-order durante el loop. El resultado observado por
el usuario fue strobo. El problema no se trata como una falla de calibracion:
es una mala arquitectura de presentacion para una capa continua.

## Evidencia de research

DirectComposition conserva un arbol de visuales y procesa los cambios en
lotes atomicos al hacer `Commit`; el compositor del escritorio alinea la
composicion con el blanking vertical. Eso permite separar el plan semantico,
que cambia poco, del framebuffer y del scheduling del compositor.

- [DirectComposition architecture and components](https://learn.microsoft.com/en-us/windows/win32/directcomp/architecture-and-components)
- [Using the Visual Layer with Win32](https://learn.microsoft.com/en-us/windows/uwp/composition/using-the-visual-layer-with-win32)
- [Windows.UI.Composition Win32 samples](https://github.com/microsoft/Windows.UI.Composition-Win32-Samples)
- [DirectComposition code samples](https://learn.microsoft.com/en-us/windows/win32/directcomp/directcomposition-code-samples)

Los precedentes de codigo abierto refuerzan la separacion entre compositor y
logica de control: ShaderGlass usa DX11 y sincronizacion VSync para shaders de
escritorio; procmod/overlay usa una capa Direct3D11 transparente, topmost y
click-through; winpane separa un nucleo de alto rendimiento de un controlador
Python JSON-RPC. Se usan como referencias de arquitectura, no como corpus ni
dependencias de FARMAXIA.

- [ShaderGlass](https://github.com/votality/shaderglass)
- [procmod/overlay](https://github.com/procmod/overlay)
- [winpane](https://github.com/peteretelej/winpane)
- [Vortice.Windows](https://github.com/amerkoleci/Vortice.Windows)

## Decision

Adoptar un backend aislado .NET 8 + Vortice 3.8.3 con:

- D3D11 hardware, sin WARP como fallback silencioso.
- DXGI `CreateSwapChainForComposition`, flip-sequential y alpha
  premultiplicado.
- DirectComposition con un solo target/visual topmost.
- Shader de triangulo fullscreen; el CPU actualiza solo un constant buffer.
- Presentacion solo cuando cambia el `RepresentationPlan` y con limite de
  frecuencia.
- stdin JSONL local como frontera inicial con Python; sin red y sin pantalla
  capturada.

## Kill tests

- Si `--no-pointer` aumenta `presents` continuamente, el modo retenido falla.
- Si el source vuelve a contener `UpdateLayeredWindow` o `SetWindowPos` dentro
  del loop, el backend no se acepta.
- Si el shader alterna alpha o color entre frames sin un plan nuevo, se
  rechaza por riesgo de strobo.
- Si la ruta JSONL requiere sockets, camara, captura o ejecucion arbitraria,
  se rechaza por el contrato privacy-first.
- Si el backend solo funciona sobre el escritorio y queda debajo de una
  ventana normal, se rechaza la estrategia topmost/DirectComposition.

## Resultado inicial reproducible

En la maquina de desarrollo, `dotnet build` termina sin errores. Una ejecucion
estatica de 2 segundos informa `plans=1 presents=1`; una ejecucion con cursor
a 30 Hz informa 24 actualizaciones en 2 segundos. Son medidas del proceso de
presentacion, no una medida de utilizacion GPU ni evidencia de precision
ocular. La utilizacion GPU debe medirse con los contadores `GPU Engine` de
Windows en una comparacion controlada frente a `057`.

## Siguiente fase

1. Automatizar el kill test de fuente y el smoke test del proceso.
2. Medir `GPU Engine 3D` y energia/temperatura con una ventana fija y cursor
   quieto/movil.
3. Añadir `WM_DISPLAYCHANGE` y un contrato de layout versionado.
4. Conectar el adaptador Python `057` al JSONL sin activar camara ni red.
5. Solo despues probar planes de VIZZ que representen foco, periferia,
   ritmo y pausas; el renderer no decide por si solo que debe mirar la persona.
