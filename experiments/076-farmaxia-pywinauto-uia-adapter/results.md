# Resultados 076 — adapter real pywinauto/UIA

**Fecha de ejecución:** 2026-08-27
**Estado:** `PYWINAUTO_UIA_PROBE_VERIFIED`

## Evidencia obtenida

- se descargó el repositorio oficial `pywinauto/pywinauto` desde GitHub y se
  fijó al tag estable `0.6.9`, commit `f6219c0`;
- se instalaron `pywin32 311`, `comtypes 1.4.15` y `six 1.17.0`;
- la importación real funcionó en Python 3.13;
- el backend UIA enumeró ventanas activas del escritorio sin inyectar input;
- una ejecución con inspección de controles observó 6 ventanas y 1.623
  descendientes, con 156 `Button`, 4 `Document`, 1 `Edit` y 24 `Pane`;
- los títulos no se emitieron y `actions_performed` permaneció vacío;
- el contrato positivo y 7 kill tests pasaron.

## Qué cambia

Antes FARMAKSIA modelaba la superficie de una aplicación en fixtures. Ahora
puede obtener una primera representación estructural de una aplicación Windows
real. Esto habilita el siguiente puente: UIA → representación semántica →
X-ANA-X/CODE-INE → overlay VIZZ, sin empezar por screenshot ni eye tracking.

## Fallos y límites

El checkout `master` no fue adoptado porque importaba `injectlib` sin declarar la
dependencia; el tag estable sí funcionó. UIA no garantiza que todos los
controles expongan texto, patrones o semántica suficiente, no cubre cada
aplicación, no demuestra comprensión y no verifica todavía que una acción
externa haya producido su efecto.

## Seguridad

No hubo cámara, captura de pantalla, red, input inyectado, escritura de fuente
ni datos humanos persistidos. La inspección de títulos se usó sólo para filtrar
en memoria y nunca se emitió.

## Próximo objetivo

Usar un target explícito y seguro —una aplicación concreta— para convertir el
árbol UIA en un `SurfaceDescriptor` con roles, estados, bounds y capabilities,
y comprobar si reduce tiempo frente a coordenadas/screenshot. La acción seguirá
siendo dry-run hasta contar con un verificador independiente.
