# Literatura 019 — renderer adaptativo desacoplado

## Síntesis

La investigación respalda una arquitectura de dos capas: un host obtiene
señales y permisos; un renderer transforma una representación visual declarada.
No respalda prometer lectura universal de aplicaciones, profundidad real desde
una webcam ni una interfaz que pueda reordenarse sin conservar semántica e
input.

### Fuentes técnicas adoptadas

- [TouchDesigner 2023.12000](https://derivative.ca/release/202312000/70312):
  versión instalada localmente; incluye cambios de ese build y base para
  comparar el runtime permitido.
- [Face Track CHOP](https://docs.derivative.ca/Face_Track_CHOP): seguimiento de
  cara, landmarks, dirección y rotación con NVIDIA Maxine en Windows; es una
  fuente de pose, no una medición absoluta de distancia ocular.
- [Video Device In TOP](https://docs.derivative.ca/Video_Device_In_TOP):
  entrada directa de cámara; TouchDesigner advierte que una cámara no puede
  compartirse simultáneamente con otra aplicación.
- [OSC In CHOP](https://docs.derivative.ca/OSC_In_CHOP): transporte numérico
  posible, pero se mantiene apagado en el bootstrap preparado para evitar
  abrir una superficie de red sin consentimiento.
- [Syphon Spout In TOP](https://docs.derivative.ca/Syphon_Spout_In_TOP): ruta
  local de texturas compartidas candidata para una imagen GPU→GPU.
- [Screen Grab TOP](https://docs.derivative.ca/Screen_Grab_TOP): útil como
  prototipo de captura, insuficiente como contrato completo de selección y
  privacidad.
- [Perform Mode](https://docs.derivative.ca/Perform_Mode) y
  [Performance Monitor](https://docs.derivative.ca/Performance_Monitor): base
  para separar coste de composición GPU, cooks de CPU y salida.
- [Filter CHOP](https://docs.derivative.ca/Filter_CHOP): el One Euro Filter es
  una opción razonable para reducir jitter sin introducir el retraso de un
  suavizado excesivo.
- [Windows UI Automation](https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-uiautomationoverview):
  árbol de elementos, propiedades, patrones y eventos para una capa semántica
  opcional; no todos los programas exponen la misma información.
- [Windows Graphics Capture](https://learn.microsoft.com/en-us/windows/apps/develop/media-authoring-processing/screen-capture)
  y el [ejemplo oficial de UI Composition](https://github.com/microsoft/Windows.UI.Composition-Win32-Samples):
  base adoptada en el experimento 081 para captura explícita y composición.
- [Motion parallax](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/MMSP09.pdf):
  una pantalla 2D puede producir una señal visual de profundidad mediante
  seguimiento del movimiento, sin afirmar que cambió la geometría física.
- [Focus+context](https://doi.org/10.1145/1456650.1456652) y
  [semantic fisheye](https://journals.sagepub.com/doi/10.1177/154193120705100507):
  antecedentes para asignar más detalle al contexto relevante sin deformar de
  manera uniforme toda la interfaz.

## Consecuencia para VIZZ

El aporte diferencial no es “otro overlay”, sino una política que compone una
representación visual con un contrato verificable:

```text
señales humanas → estado normalizado → plan de representación → renderer GPU
                                      ↘ mapa inverso o preview-only
```

El input humano debe ser la señal primaria de adaptación cuando exista: foco
activo, actividad de teclado, puntero y navegación. La cámara es una señal
opcional y revocable. La escena debe conservar una versión nítida del texto,
aplicar parallax sólo a capas no críticas y marcar como `UNKNOWN` cualquier
semántica que no pueda demostrarse.

## Decisiones negativas

- No instalar MediaPipe, ONNX Runtime o PyTorch dentro de TouchDesigner: la
  instalación local no los incluye y duplicar runtimes elevaría coste y riesgo.
- No usar `Depth TOP` como sensor de profundidad facial: describe profundidad de
  un render, no de la webcam.
- No depender de `Direct Display Out` o `Shared Memory` antes de confirmar la
  edición/licencia y el sistema operativo.
- No comenzar con un agente que reordene interfaces: primero debe existir un
  renderer que ejecute un plan fijo y pueda demostrar reversibilidad.

