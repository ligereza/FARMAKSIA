# Experimento 030 — seguimiento ocular real VIZZ con opt-in local

## Resultado que se intenta obtener

Este experimento añade un adaptador ejecutable para una webcam común. Cuando
una persona marca el consentimiento y pulsa **Iniciar seguimiento**, WebGazer
estima en el navegador un punto de mirada y VIZZ lo dibuja como un marcador
volátil. La calibración usa nueve objetivos visibles que la persona mira y
pulsa.

Esto es una integración técnica, no una validación de precisión, atención,
fatiga, ansiedad, pupila, intoxicación, neurotransmisores, comodidad o salud
ocular. El marcador no es una medición clínica ni una receta óptica.

## Contrato de seguridad

- La cámara está apagada al cargar la página y el consentimiento no está
  marcado por defecto.
- La página carga una copia local de WebGazer.js 3.5.3; no usa CDN ni red
  externa. La política CSP permite únicamente `fetch` al mismo `localhost`
  para los recursos internos que WebGazer pueda necesitar.
- `saveDataAcrossSessions(false)` se fija antes de iniciar. El adaptador no
  guarda vídeo ni coordenadas; solo mantiene el último punto y un contador en
  memoria para la visualización.
- **Detener y borrar estado** elimina el listener, intenta detener las pistas
  de vídeo, termina WebGazer y ejecuta `clearData()` para limpiar la
  calibración local.
- El botón de recalibración borra el modelo antes de volver a aceptar
  objetivos. Sin nueve puntos, el marcador de adaptación permanece bloqueado.
- La automatización de FARMAKSIA no solicita permisos ni inicia dispositivos;
  este experimento solo ejecuta un análisis estático del contrato.

## Cómo ejecutarlo manualmente

WebGazer requiere un contexto seguro en los navegadores habituales. Desde la
raíz del repositorio:

```text
python -m http.server 8000
```

Después abrir:

```text
http://localhost:8000/experiments/030-vizz-webgazer-opt-in/
```

La persona debe revisar el alcance, marcar el consentimiento, pulsar iniciar,
conceder el permiso del navegador y completar los nueve objetivos. Para
terminar, pulsar **Detener y borrar estado** y revocar el permiso en el
navegador si corresponde.

## Dependencia y límites

WebGazer.js 3.5.3 está tomado del proyecto oficial
[brownhci/WebGazer](https://github.com/brownhci/WebGazer), con licencia
GPL-3.0-or-later; el código se conserva en `vendor/` junto a su licencia. La
versión 3.5.3 declara que la maintenance oficial terminó el 24-02-2026, por lo
que esta adopción queda experimental y requiere revisión de licencia antes de
incorporarse a un producto con otra licencia.

La evidencia científica registrada en
[`research/literature/014-vizz-gaze-quality-tools.md`](../../research/literature/014-vizz-gaze-quality-tools.md)
indica que calibración, latencia y calidad de medición deben evaluarse por
separado. Este prototipo todavía no mide error frente a un tracker de
referencia, latencia extremo a extremo ni efectos de lectura o confort en
personas.

## Verificación reproducible

```text
python experiments/030-vizz-webgazer-opt-in/run_contract_test.py
```

La salida esperada es `CONTRACT_TESTS_VALID`. No implica que la cámara se haya
encendido ni que exista una sesión humana.
