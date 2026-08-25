# VIZZ 044 — ojo reducido como cámara óptica

Este es el primer modelo que debe preceder a la binocularidad. Representa una
sola pantalla como fuente luminosa y traza una imagen completa hacia una
retina reducida.

## Convención física

```text
pantalla (z = u)  →  pupila/lente (z = 0)  →  retina (z = -r)
```

Los fotones viajan desde la pantalla hacia el ojo. La línea de mirada va en
sentido contrario, del ojo hacia la pantalla. Para cada punto de pantalla se
trazan cinco rayos que atraviesan distintas posiciones de una pupila finita.
En la lente equivalente se usa la forma paraxial:

```text
s_in  = (altura_pupila - altura_fuente) / u
s_out = s_in - altura_pupila / f
altura_retina = altura_pupila + r · s_out
```

La posición del foco se obtiene con:

```text
1/f = 1/u + 1/v
m = -v/u
```

El signo negativo produce la inversión de la imagen. Si el plano retinal no
coincide con `v`, los rayos llegan a distintas posiciones y aparece un
desenfoque proporcional a la abertura de la pupila.

## Ejecutar

```powershell
.\.venv\Scripts\python.exe experiments/044-vizz-reduced-eye-camera/eye_camera_simulator.py
```

La interfaz muestra:

- dos cortes laterales: meridiano horizontal y vertical;
- la pantalla, la pupila/lente, la retina y el haz de rayos;
- el foco antes, sobre o detrás de la retina;
- una vista frontal de la pantalla;
- una vista frontal ampliada de la imagen retinal invertida;
- el efecto de cambiar distancia, desplazamiento y radio pupilar.

## Modelos

- `Normal reducido`: ajustado para enfocar a 72 cm.
- `Miopía conceptual`: foco delante de la retina.
- `Hipermetropía conceptual`: foco detrás de la retina.
- `Astigmatismo conceptual`: poderes diferentes en los meridianos X/Y.

Los parámetros son demostrativos. El ojo real combina córnea, humor acuoso,
pupila, cristalino y retina curva; este experimento reemplaza córnea y
cristalino por una lente equivalente para hacer visible la formación de imagen.
No estima una receta ni diagnostica visión.

## Base de investigación

- [OpenCV: modelo pinhole y proyección perspectiva](https://docs.opencv.org/4.10.0/d9/d0c/group__calib3d.html)
- [OpenStax: formación de imágenes con lentes](https://openstax.org/books/college-physics/pages/25-6-image-formation-by-lenses)
- [National Eye Institute: cómo funciona el ojo](https://www.nei.nih.gov/learn-about-eye-health/healthy-vision/how-eyes-work)
- [Diseño óptico del ojo humano](https://pmc.ncbi.nlm.nih.gov/articles/PMC3972707/)
- [Conoid de Sturm para astigmatismo](https://www.ncbi.nlm.nih.gov/books/NBK587355/)
