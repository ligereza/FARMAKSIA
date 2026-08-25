# Resultados — Experimento 046

Estado observado: `VIZZ_046_GEOMETRY_CONTRACT_VALID`.

El probe sintético valida la separación mínima entre:

- observación binocular;
- origen y dirección del rayo;
- planos físicos de monitores;
- coordenada normalizada por monitor;
- incertidumbre y radio seguro;
- distancia física y cobertura angular;
- monitor inclinado respecto de la cámara;
- contexto de teclado/mouse;
- política visual y fallback estático.

No se usan datos humanos, cámara, vídeo, red ni mutación del contenido de
pantalla. Los resultados no prueban la precisión de VIZZ en una persona.

Valores sintéticos observados:

- monitor primario: `uv=(0.65, 0.3222)`, distancia `0.7343 m`;
- mismo punto tras trasladar la cabeza: el `uv` permanece igual dentro de
  `1e-9`;
- monitor inclinado: `uv=(0.70, 0.5889)`;
- cobertura angular de fixture 27 pulgadas a 72 cm: `45.104° × 26.268°`;
- baja confianza, layout obsoleto, ojo perdido y monitor ambiguo devuelven
  `UNKNOWN` y `STATIC_FALLBACK`.
