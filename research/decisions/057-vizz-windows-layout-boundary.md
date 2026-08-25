# ADR 057 — VIZZ: el layout lógico de Windows no es geometría física

Fecha: 2026-08-25  
Estado: aceptada como infraestructura exploratoria

## Decisión

VIZZ incorporará un probe de solo lectura que enumera los monitores activos de
Windows y conserva sus rectángulos en coordenadas del escritorio virtual. Cada
snapshot recibe una versión determinista; si cambia la configuración lógica,
una calibración anterior deberá quedar obsoleta o revalidarse.

El probe no transforma esos rectángulos, el DPI ni el identificador del monitor
en un plano físico 3D. La salida mantiene `physical_geometry_status=UNKNOWN`
hasta que exista una medición o calibración explícita de tamaño, orientación y
pose del monitor respecto de los ojos/cámara.

## Evidencia

`experiments/050-vizz-windows-display-layout-probe/` enumeró en el host del
laboratorio:

- dos monitores activos;
- escritorio virtual `(0, 0, 3926, 960)`;
- monitor primario `(0, 0, 1707, 960)`;
- monitor secundario `(2560, 0, 3926, 768)`;
- DPI efectivo `96×96` reportado por Windows;
- una región lógica sin monitor entre ambos rectángulos;
- orientación válida para el primario y `UNKNOWN` para el secundario.

Esto confirma que el sistema operativo entrega identidad y coordenadas
lógicas útiles, pero no prueba distancia ojo-pantalla ni permite inferirla.

## Base técnica

La documentación de Microsoft describe los rectángulos de `MONITORINFO` como
coordenadas del escritorio virtual; por eso un monitor puede tener coordenadas
negativas o no compartir el origen del primario. La referencia de High DPI
separa además la escala lógica de las conversiones físico-lógicas. La
configuración de display puede cambiar orientación y modo, por lo que VIZZ
debe versionar el layout en vez de aplicar una escala global permanente.

## Consecuencias

- 049 seguirá cerrado si sólo recibe features de imagen del runtime 033.
- 046 podrá recibir en el futuro planos físicos, pero no se fabrican a partir
  de `monitor_rect`.
- Un punto en el hueco entre monitores debe ser `UNKNOWN`.
- La próxima fase debe medir el tamaño físico de cada pantalla y calibrar su
  plano respecto del punto medio de los ojos, con cámara y pantalla fijas sólo
  durante esa medición; el runtime final no debe suponer que la cabeza queda
  quieta.
- No se afirma todavía mejora de visión, reducción de fatiga ni precisión de
  gaze.

## Kill tests

1. No iniciar cámara, red ni mutación de pantalla.
2. No recortar coordenadas negativas ni imponer una escala global del
   monitor primario.
3. No aceptar geometría física si faltan dimensiones o pose 3D.
4. Invalidar/revisar una calibración cuando cambie `layout_version`.

## Preguntas abiertas

- ¿Qué medición simple y repetible aportará ancho/alto físico sin depender de
  EDID incompleto?
- ¿Cómo estimar la pose de cada plano con el mínimo de puntos y sin usar el
  mouse como verdad ocular?
- ¿Cómo transportar un rayo binocular a un segundo monitor con otra distancia
  u orientación y devolver `UNKNOWN` en el hueco?
