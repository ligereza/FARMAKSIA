# Resultados VIZZ 033

## Evidencia obtenida

- El entorno aislado instala Python 3.13, OpenCV 5.0.0, ONNX Runtime GPU
  1.29.0 y las DLL CUDA/cuDNN correspondientes.
- Las sesiones RetinaFace y gaze reales del proyecto open source adoptado
  cargaron con `CUDAExecutionProvider`; la prueba de sesión registró
  `session.disable_cpu_ep_fallback=1` y ejecutó inferencia de forma sintética,
  sin cámara ni datos humanos.
- El flujo ejecutable tiene una única ventana de calibración y un modificador
  nativo click-through sin controles después del sellado.
- La ventana Win32 se probó en un smoke test de creación, actualización de
  bitmap de 1x1 y destrucción; la firma Win64 de `LPARAM` quedó corregida para
  `DefWindowProcW`.

## Evidencia humana exploratoria posterior

Se completó una validación independiente de una repetición por target y
condición: 24/24 muestras, 12 con lentes y 12 sin lentes. La captura tuvo
12--14 muestras válidas por punto, calidad media 0.9947, MAD de features máximo
0.0704 y MAD de pose máximo 0.0013. Esto confirma estabilidad de captura, no
precisión de mirada.

Al aplicar el perfil combinado existente a esa sesión, el error fue de unos
668 px de mediana y 1015 px en P95 sobre una pantalla de 1707x960. El
resultado es exploratorio y no habilita el perfil para precisión de producción.
La evidencia también muestra un desplazamiento entre las features de
calibración y validación, pero no permite atribuirlo todavía a lentes, pose o
etiquetas.

El auditor agrupado por target produjo:

| Modelo y alcance | Mediana | P95 | Estado |
|---|---:|---:|---|
| Perfil existente → validación | 668.4 px | 1014.5 px | diagnóstico |
| M0, calibración → validación | 742.1 px | 1148.9 px | baseline |
| M0, solo validación | 729.5 px | 872.2 px | diagnóstico |
| M1, solo validación, pose | 661.3 px | 886.4 px | no aceptado |
| M2, solo validación, pose + condición | 664.8 px | 886.3 px | no aceptado |

M1 reduce la mediana aproximadamente 9.4% frente a M0, pero empeora el P95;
M2 reduce la mediana aproximadamente 8.9% y tampoco mejora el P95. Ninguno
supera el filtro provisional del 10% en mediana y P95, y ambos son solo
diagnósticos internos porque la calibración no persistió pose.

## Desconocido

No se han medido aún precisión clínica, FPS, latencia, temperatura, asimetría
entre ojos ni efecto perceptual. La calibración persistió features, pero no los
seis proxies de pose; por eso los modelos pose-aware no son identificables
entre sesiones y el auditor los marca `UNKNOWN_NOT_IDENTIFIABLE`.

La siguiente corrección del contrato exige pose válida durante cada ventana de
calibración y persiste `pose`, `max_pose_mad`, `pose_proxy_names` y
`pose_complete`. Esto no altera el perfil existente; prepara la próxima sesión
para que M1/M2 puedan evaluarse entre sesiones sin reconstruir pose a partir de
features oculares.

## Kill tests

- Modelo ausente, CUDA ausente o DLL incompatible: terminar antes de abrir la
  cámara.
- Fallback CPU habilitado: rechazar la sesión.
- Menos de 12 puntos válidos: no sellar perfil.
- Error binocular mayor de 45 grados: ocultar capa y no producir coordenada.
- Perfil con `raw_video` distinto de `false`: rechazar.
- Runtime headless con toolkit visible: contrato inválido.
