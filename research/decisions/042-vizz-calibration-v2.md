# Decisión 042 — propuesta VIZZ-Cal v2

Fecha: 2026-08-24

## Estado

Propuesta de investigación. No se adopta todavía una nueva dependencia ni se
declara precisión humana.

## Decisión

VIZZ conservará WebGazer 3.5.3 como baseline local y comparará una segunda
ruta inspirada en RealEye Light Open, sin copiar su dependencia antes de una
revisión de licencia, modelos y procedencia. La implementación futura se
divide en dos capas:

1. **Protocolo VIZZ-Cal v2 sobre el baseline:** calentamiento central fuera del
   entrenamiento, patrón de 17 objetivos con cobertura de bordes, esquinas y
   zonas intermedias, y captura de una ventana de muestras después de que la
   persona fija la mirada. El orden se registrará y se alternará entre sesiones
   para medir el efecto de secuencia en lugar de asumirlo.
2. **Extractor de calidad y características:** landmarks de ojos/iris, pose de
   cabeza, apertura de cada ojo y crops normalizados por separado. Si un ojo
   está cerrado o la detección pierde confianza, el frame se rechaza o se usa
   un fallback explícito; no se mezcla silenciosamente con el vector de ambos
   ojos.

## Procedimiento propuesto

- 2 s de calentamiento mirando al centro, sin entrenar.
- 17 puntos normalizados aproximadamente en 5%, 25%, 50%, 75% y 95% de la
  pantalla, con 10–15 muestras válidas por punto después de una espera de
  fijación de 500 ms.
- Orden pseudoaleatorio reproducible, con el centro y las esquinas balanceados
  entre sesiones.
- Validación con puntos o repeticiones reservadas que no entrenan el modelo.
- Tres condiciones separadas: ambos ojos abiertos, ojo izquierdo cerrado y ojo
  derecho cerrado. La condición monocular es un test de robustez/oclusión, no
  una medida de exactitud anatómica de cada ojo.

## Métricas de aceptación

Registrar solo métricas volátiles y agregadas de la sesión:

- error euclídeo mediano y percentil 95 en píxeles CSS;
- error normalizado por la diagonal de la pantalla;
- porcentaje de frames válidos y porcentaje con ambos ojos utilizables;
- jitter durante una fijación de 1 s;
- latencia hasta que la predicción entra en una ventana estable;
- exactitud por zonas 3×3 para la adaptación de pantalla.

Los umbrales iniciales serán criterios de ingeniería del experimento, no
umbrales clínicos. Si la validación falla, VIZZ queda en `blocked` y no cambia
colores, tamaño, paneles ni contenido basándose en la mirada.

## Evaluación de alternativas

- **Adoptar RealEye completo ahora:** rechazado temporalmente por AGPL/licencia
  comercial, modelos CDN por defecto y falta de un benchmark independiente en
  nuestro corpus.
- **Cambiar a EyeGestures ahora:** rechazado temporalmente porque su ruta web
  documentada depende de CDN y no aporta benchmark comparable; queda como
  fuente de ideas para fijación, parpadeo y eventos.
- **Usar OpenFace o Pupil Core:** reservado para un comparador offline o una
  referencia hardware; no cumple el objetivo inmediato de un sandbox browser
  local con webcam común.

## Kill tests

- Sin ventana de muestras válida, no se completa la calibración.
- Si un ojo está cerrado, el estado debe mostrar calidad reducida y detener la
  adaptación gaze-contingent.
- Si el rostro sale de la zona o la latencia/jitter excede el criterio de la
  sesión, el resultado es `rejected`.
- Ningún proceso automático solicita cámara, guarda vídeo, guarda coordenadas
  crudas o ejecuta pruebas bajo intoxicación.

La siguiente tarea segura es implementar el experimento 031 como auditoría
comparativa de calibración, no reemplazar WebGazer en producción.
