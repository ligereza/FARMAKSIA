# Decisión 054 — límite óptico de VIZZ antes de binocularidad

## Decisión

La siguiente implementación de VIZZ debe ser un ojo reducido tipo cámara:

1. una pantalla plana completa como fuente luminosa;
2. una pupila de abertura finita;
3. una lente equivalente con foco configurable por meridiano;
4. una retina de recepción donde se dibuje la imagen completa;
5. movimiento explícito de la pantalla y recomputación de todos los rayos.

La binocularidad se posterga hasta que estos contratos pasen. Añadir dos ojos
antes de validar una proyección monocular correcta mezclaría inversión óptica,
disparidad, convergencia y acomodo en una sola visualización difícil de auditar.

## Qué sí demuestra

El experimento hace visible la geometría de formación de imagen en un modelo
paraxial: la pantalla emite, el haz pasa por una pupila finita, la lente
converge y el plano retinal recibe una imagen invertida. También permite
comparar foco sobre, delante o detrás de la retina y dos focos meridionales
para un astigmatismo conceptual.

## Qué no demuestra

No estima la receta de una persona, no modela toda la anatomía ocular, no
determina distancia real usuario-monitor y no demuestra reducción de fatiga.
La retina real es curva y la percepción depende de procesamiento neural; la
interfaz es un instrumento de razonamiento, no una prueba clínica.

## Criterio para pasar a dos ojos

Sólo después de mantener invariantes los contratos de VIZZ 044 se puede añadir
un segundo ojo con separación interpupilar, dos centros ópticos y una pantalla
compartida. Ese siguiente modelo deberá reportar por separado convergencia,
acomodación y disparidad, sin afirmar que una imagen estereoscópica es cómoda
por el solo hecho de ser geométricamente consistente.
