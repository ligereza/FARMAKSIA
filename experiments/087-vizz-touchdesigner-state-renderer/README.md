# Experimento 087 — contrato de estado para renderer TouchDesigner

## Objetivo

Preparar el puente entre el host de VIZZ y TouchDesigner sin abrir ninguna
aplicación. El experimento fija un contrato pequeño, filtrable y auditable para
que el renderer pueda trabajar con pose, foco e interacción sin recibir
captura cruda, texto escrito ni comandos.

Este slice no captura cámara, no selecciona ventanas, no escucha teclado, no
envía input y no crea sockets. Es preparación de código y pruebas puras.

## Arquitectura

```text
host Windows (futuro) → state_router.py → canales normalizados → TouchDesigner
                                     ↘ UNKNOWN si el dato es viejo/inválido
```

Fuentes futuras, siempre con permiso explícito:

1. `manual`: fixture o control local.
2. `face_track`: pose proveniente de Face Track CHOP o del tracker existente.
3. `uia`: semántica de la ventana seleccionada.
4. `input`: actividad de teclado/puntero sin registrar contenido.
5. `combined`: fusión de fuentes ya verificadas.

El estado normalizado se puede transportar después por un mecanismo local. OSC
queda apagado por defecto; este experimento no abre ningún puerto.

`render_policy.py` convierte ese estado en un plan acotado de presentación. La
política usa pose relativa para un parallax pequeño, foco explícito para
contexto y actividad de teclado/puntero como señal de trabajo; no llama a esa
señal “atención” ni la usa para inferir intención. Si falta permiso, selección
de fuente o confianza, devuelve un plan neutral y mantiene el contenido crítico
nítido.

`host_adapter.py` conecta dos fuentes sin mezclarlas: el `pose` del tracker
actual sólo aporta pose relativa; el resultado geométrico 046 es el único que
puede aportar `focus`/`uv`. Si 046 devuelve `ambiguous_monitor` o no hay
intersección, el adaptador baja la confianza y el router produce `UNKNOWN`.

## Contrato visual mínimo

- `head.x/y/z`: posición relativa normalizada; no son milímetros.
- `head.rx/ry/rz`: rotación en grados, acotada.
- `focus.x/y/w/h`: rectángulo de interés en coordenadas 0–1.
- `focus.interest`: fuerza de interés, 0–1.
- `input.keyboard_activity`: actividad agregada, nunca teclas ni texto.
- `input.pointer_*`: posición normalizada y actividad agregada.
- `window.source_rect`: geometría declarada de la fuente; no incluye pixels.
- `permissions`: permisos separados para cámara, captura, overlay e input.

La adaptación debe neutralizarse si el estado es `UNKNOWN`, está vencido,
tiene confianza menor a `0.25`, tiene reloj inconsistente o carece del permiso
que requiere el plan.

## Preparación dentro de TouchDesigner

El archivo `touchdesigner/bootstrap_vizz_renderer.py` se ejecutará más adelante
desde TouchDesigner por el usuario. Construye sólo una red mínima de CHOPs y
TOPs: estado manual, entrada OSC inactiva, selección de estado, filtro y una
superficie visual de prueba. No crea `Window COMP`, `Video Device In TOP`,
`Screen Grab TOP`, cámara, captura de escritorio ni procesos externos.

## Verificación sin aplicaciones

Desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe experiments\087-vizz-touchdesigner-state-renderer\run_contract_test.py
```

El test comprueba normalización, vencimiento, confianza, NaN, aplanado de
canales y que el bootstrap conserve las barreras de privacidad. No prueba la
licencia, el runtime Maxine, Spout ni el comportamiento real de TouchDesigner;
esas preguntas quedan para una sesión posterior autorizada por el usuario.
