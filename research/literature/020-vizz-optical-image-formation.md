# VIZZ: formación óptica de imagen antes de la binocularidad

## Pregunta

¿Qué debe representar FARMAXIA antes de intentar explicar dos ojos, disparidad
o confort perceptual?

## Resultado del research

Una pantalla es una fuente luminosa. Para cada punto de pantalla, la luz sale
en muchas direcciones y sólo una parte atraviesa la pupila. La lente cambia la
dirección de ese haz y la retina recibe una proyección. La línea de mirada se
puede dibujar en el sentido opuesto, desde el ojo hacia la pantalla, pero no
debe confundirse con el transporte físico de la luz.

La cámara pinhole expresa la proyección como `s p = A [R|t] P`: los puntos que
comparten un rayo desde el centro de cámara comparten coordenada de imagen. Una
lente convergente forma una imagen real invertida cuando el objeto está más
allá de su distancia focal, con `1/f = 1/u + 1/v` y magnificación negativa.
El ojo real no es un sensor plano: córnea, pupila y cristalino forman la imagen
en una retina curva, y la señal viaja por el nervio óptico. Decir que el
“cerebro da vuelta la imagen” es una abreviatura pedagógica, no una operación
literal sobre un bitmap.

En astigmatismo regular no hay dos focos puntuales independientes: los dos
meridianos tienen potencias distintas y producen dos líneas focales, descritas
por el conoide de Sturm. Por eso el primer modelo VIZZ debe separar meridianos
X/Y y no representar astigmatismo como un único foco.

## Decisión experimental

VIZZ 044 implementa una aproximación paraxial reducida:

```text
pantalla completa → pupila finita → lente equivalente → plano retinal
```

Comprueba la inversión de la imagen y el desenfoque antes de incorporar la
geometría binocular. Es una herramienta de razonamiento y visualización, no
una receta óptica, medición clínica ni evidencia de que una pantalla mejore
la visión.

## Kill tests

- El modelo enfocado debe hacer coincidir los rayos de una pupila finita en la
  retina.
- Un punto positivo en la pantalla debe llegar con coordenadas laterales
  negativas en la retina.
- La pupila mayor debe hacer más visible el desenfoque cuando el foco no está
  en la retina.
- Los dos meridianos del astigmatismo deben tener distancias focales distintas.

## Fuentes primarias y técnicas

- [OpenCV: modelo pinhole y proyección](https://docs.opencv.org/4.10.0/d9/d0c/group__calib3d.html)
- [OpenStax: formación de imágenes por lentes](https://openstax.org/books/college-physics/pages/25-6-image-formation-by-lenses)
- [National Eye Institute: cómo funciona el ojo](https://www.nei.nih.gov/learn-about-eye-health/healthy-vision/how-eyes-work)
- [Critical review del diseño óptico del ojo humano](https://pmc.ncbi.nlm.nih.gov/articles/PMC3972707/)
- [NCBI: conoide de Sturm](https://www.ncbi.nlm.nih.gov/books/NBK587355/)
