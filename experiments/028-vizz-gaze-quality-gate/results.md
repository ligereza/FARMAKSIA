# Resultados — experimento 028

El experimento sintético conservó la transición base CODE-INE `c04 → c07` y
clasificó diez perfiles:

| Resultado | Casos |
|---|---:|
| `available` | 1 |
| `blocked` | 3 |
| `unavailable` | 5 |
| `rejected` | 2 |

Solo el perfil con consentimiento, procesamiento local, transporte sin red,
calibración válida, error dentro del límite del fixture, latencia dentro del
límite y cobertura completa habilitó la bandera de adaptación.

La falta de consentimiento, el procesamiento remoto y la API de red de Pupil
Core fueron bloqueados por política. La calibración ausente, el error alto, la
latencia alta y la cobertura parcial quedaron no disponibles. Un candidato
desconocido y un campo de latencia mal formado fueron rechazados.

Esto valida una frontera computacional de seguridad y procedencia, no la
precisión de un sensor ni la utilidad de una pantalla adaptativa. No hubo
participantes, webcam, headset, red, coordenadas humanas, parpadeos medidos,
fatiga, pupillometría, intoxicación ni inferencia farmacológica.
