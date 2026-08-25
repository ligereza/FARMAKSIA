# Resultados VIZZ 032

## Evidencia

- La máquina tiene una RTX 4070 y el flujo Python puede exigir
  `CUDAExecutionProvider` sin pedir un proveedor CPU.
- El contrato de transición impide arrancar runtime sin perfil sellado.
- Sellar el perfil cierra la interfaz visible y elimina la propiedad de UI.
- El runtime no importa toolkit gráfico ni abre cámara antes de crear la
  sesión CUDA.
- El modificador de contenido es una frontera separada del runtime y no una
  pantalla de VIZZ.

## Desconocido

El entorno Python 3.13 todavía no tiene instalados `onnxruntime-gpu`, OpenCV ni
un modelo ocular ONNX entrenado. No se ha iniciado cámara ni se ha fabricado
una calibración humana. La implementación del overlay transparente y del
extractor ocular CUDA queda para la siguiente etapa.

## Kill tests

- Menos de 12 muestras: no se sella perfil.
- Perfil sin hash de modelo o características: no se sella perfil.
- Runtime sin perfil sellado: se rechaza.
- Sin `CUDAExecutionProvider`: `cuda_unavailable`, sin cámara.
- Intento de importar UI en runtime: contrato inválido.
- `stop`: elimina estado volátil de muestras y perfil en memoria.
