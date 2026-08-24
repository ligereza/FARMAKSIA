# Auditoría de accesibilidad — piloto VIZZ

Fecha: 2026-08-23  
Estándar de referencia: WCAG 2.1 AA  
Alcance: revisión estática del HTML/JavaScript; no sustituye prueba manual
con teclado, lector de pantalla ni zoom al 200%.

## Hallazgos y correcciones

| Hallazgo | Criterio | Estado |
|---|---|---|
| El documento no declaraba idioma | 3.1.1 | corregido con `lang="es"` |
| Las tarjetas VIZZ respondían solo al clic | 2.1.1, 4.1.2 | corregido con foco, rol botón y Enter/Espacio |
| El estado seleccionado no tenía semántica programática | 4.1.2 | corregido con `aria-pressed` |
| No había foco visible declarado | 2.4.7 | corregido con `:focus-visible` |
| Los controles podían quedar por debajo de un objetivo táctil razonable | 2.5.5 | corregido con altura mínima de 44 px |
| El error de respuesta se comunicaba con `alert` | 3.3.1 | corregido con región `role="alert"` |

## Pendiente de prueba humana

- navegación completa con teclado y orden lógico de foco;
- NVDA o VoiceOver para confirmar nombres y estados anunciados;
- zoom al 200% y reflujo del contenido;
- contraste medido de texto, controles y barras en el navegador real.

La revisión mejora la accesibilidad del instrumento; no demuestra percepción,
comprensión ni eficacia de VIZZ.
