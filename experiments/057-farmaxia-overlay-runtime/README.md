# FARMAKSIA 057 - runtime overlay de representacion

Este es el primer prototipo de la capa adaptativa real. No crea una aplicacion
de contenido, no muestra un panel VIZZ y no inicia camara. Dibuja una capa
transparente sobre el escritorio virtual y deja pasar mouse/teclado a la
aplicacion que esta debajo.

```text
senal local de prueba (puntero)
          |
RepresentationPlan
          |
FocusOverlay nativo click-through
          |
aplicacion existente sin modificaciones
```

La senal del puntero solo sirve para comprobar la arquitectura del overlay. En
las siguientes fases se podra sustituir por un caret de texto, UI Automation,
un adaptador de aplicacion, X-ANA-X o una senal VIZZ con consentimiento.

## Ejecucion

Desde la raiz del repositorio:

```powershell
.\\.venv\\Scripts\\python.exe experiments/057-farmaxia-overlay-runtime/run_overlay.py --duration 60
```

Mientras trabaja, mueve el puntero sobre una aplicacion. Debes ver un anillo
blanco movil alrededor del puntero y una atenuacion visible en la periferia.
El anillo es un marcador diagnostico para comprobar que el overlay funciona;
no representa la UI final de VIZZ. El proceso no captura la pantalla, no abre
camara, no usa red y no ejecuta contenido externo.

Detencion: `Ctrl+C` en la terminal donde se inicio.

## Contrato minimo

El runtime no recibe coordenadas sueltas. Recibe un plan declarativo con:

- `source`: origen de la senal;
- `target_space`: escritorio virtual o ventana;
- `focus`: ancla normalizada;
- `periphery_alpha`: intensidad periferica;
- `focus_radius_px`: radio de foco;
- `expires_at`: limite temporal;
- `reversible`: posibilidad de retirar la capa.

Esto permite que el mismo renderer sirva despues a VIZZ, X-ANA-X y CODE-INE.

## Limitaciones conocidas

- Esta primera version usa el compositor de ventana transparente existente y
  una imagen alpha actualizada desde Python; no es todavia el backend D3D11 de
  alto rendimiento.
- La prueba usa el puntero como senal auxiliar, no como verdad de mirada.
- Aun no interpreta UI Automation, texto, logs ni codigo.
- La geometria se expresa en el escritorio virtual; la semantica de cada
  aplicacion sera un adaptador posterior.
- Una aplicacion elevada con permisos mayores o un fullscreen exclusivo puede
  impedir que un proceso normal dibuje encima; eso es un limite de Windows,
  no una razon para pedir permisos de captura global.

## Kill tests

- Si intercepta un click o una tecla, falla.
- Si se mantiene visible despues de `Ctrl+C`, falla.
- Si requiere camara o red, falla.
- Si el plan no puede expirar o revertirse, falla.
- Si el overlay se comporta como un panel independiente, no es el runtime
  objetivo.
