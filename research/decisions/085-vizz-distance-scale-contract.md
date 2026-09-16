# Decisión 085 — VIZZ: contrato de distancia relativa y escala visual

## Decisión

El siguiente experimento de VIZZ partirá de una referencia `P0` detectada por
la webcam. La tarjeta de ancho conocido se usa sólo durante ese instante para
validar un cuadrilátero ID-1 y establecer una escala aparente; el runtime
usará siempre dos medidas simultáneas: distancia entre ojos y ancho facial.
Ambas se combinan mediante media geométrica ponderada en logaritmos.

La representación de control será un Landolt C. Para conservar el tamaño
angular aproximado, su diámetro en píxeles será proporcional a la distancia
real relativa: si la persona se acerca, disminuye; si se aleja, aumenta.

## Por qué

Una sola distancia entre ojos puede fallar con oclusión, landmarks inestables o
un giro. Un solo ancho facial puede fallar por expresión, recorte o landmarks.
La combinación no vuelve mágicamente identificable la profundidad, pero permite
detectar desacuerdo y abstenerse. El uso de una media geométrica evita que una
señal en unidades relativas domine por una suma arbitraria.

## Límites

La webcam no entrega milímetros absolutos por sí sola. El rectángulo detectado
calibra la escala aparente de la tarjeta; para profundidad métrica todavía
hacen falta intrínsecos de cámara o una distancia física conocida. Sin eso el
contrato sólo reporta `d/d0`.
La corrección coseno es una aproximación para el fixture y no sustituye un
modelo 3-D de landmarks. Este trabajo no afirma control de la acomodación,
reducción de fatiga ni precisión clínica.

## Siguiente experimento

Después de verificar el fixture, conectar una captura consentida que produzca
resúmenes de ambas reglas, pose, calidad y timestamps. Comparar objetivo fijo
contra objetivo ajustado usando distancia física marcada como referencia y
registrar `UNKNOWN`, latencia, discrepancia y respuesta subjetiva. No comenzar
con aprendizaje profundo hasta demostrar que las dos reglas y el control
geométrico son estables.
