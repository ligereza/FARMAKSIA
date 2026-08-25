# VIZZ 045 — cámara óptica de un solo ojo (retirado)

Estado: **retirado**. El último `.py` fue eliminado porque la base visual no
era suficientemente coherente para continuar construyendo sobre ella. La
versión reducida mantenida para contratos educativos es [VIZZ 044](../044-vizz-reduced-eye-camera/).

Este experimento rehace la base monocular en una escena única. No incorpora
binocularidad ni intenta esconder la diferencia entre luz, imagen retinal y
percepción.

## Qué se ve

```text
PANTALLA · objeto A
        ↓ rayos de luz
CÁMARA / OJO REDUCIDO
  apertura + lente → PUNTO FOCAL → sensor / retina
        ↓
RETINA · imagen óptica invertida
```

La pantalla es una fuente de puntos luminosos. Cada punto seleccionado emite
un haz que atraviesa nueve posiciones de una abertura finita. La lente cambia
la pendiente de cada rayo; el sensor/retina intercepta el haz. La GUI dibuja
dos meridianos, horizontal y vertical, una carcasa de cámara explícita, el
plano focal ámbar y una marca `A` asimétrica: arriba-izquierda en pantalla,
abajo-derecha en retina.

## Convención y ecuaciones

```text
pantalla z = u  →  lente z = 0  →  sensor/retina z = -r
```

Para un rayo que atraviesa la abertura en `a` y nace en `s`:

```text
s_in  = (a - s) / u
s_out = s_in - a / f
y_retina = a + r · s_out
```

La posición focal sigue `1/f = 1/u + 1/v`, y la magnificación ideal es
`-v/u`. El signo negativo se comprueba con la marca asimétrica y con el
centroide retinal, no se interpreta como una operación literal del cerebro.

## Contrato de retiro

`run_contract_test.py` verifica que el simulador eliminado no reaparezca y que
la frontera de retiro permanezca documentada. No se ejecuta una GUI desde este
experimento.

## Límites

La córnea y el cristalino se reducen a una lente paraxial equivalente y la
retina se representa como plano. Esto es una visualización auditable, no una
receta, diagnóstico, medición de distancia real ni prueba de reducción de
fatiga. La binocularidad queda fuera hasta validar esta capa.

## Fuentes

- [OpenCV: modelo pinhole y proyección](https://docs.opencv.org/4.10.0/d9/d0c/group__calib3d.html)
- [OpenStax: formación de imágenes por lentes](https://openstax.org/books/college-physics/pages/25-6-image-formation-by-lenses)
- [National Eye Institute: cómo funciona el ojo](https://www.nei.nih.gov/learn-about-eye-health/healthy-vision/how-eyes-work)
- [Diseño óptico del ojo humano](https://pmc.ncbi.nlm.nih.gov/articles/PMC3972707/)
