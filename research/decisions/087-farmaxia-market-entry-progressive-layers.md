# Decisión 087 — mercado disponible y capas progresivas de FARMAKSIA

**Fecha:** 2026-08-29
**Estado:** propuesta de dirección
**Ámbito:** Chile, compras públicas digitales y servicios de atención
**Pregunta:** ¿qué producto puede vender FARMAKSIA sin reemplazar el software existente y cómo puede crecer hacia su visión completa?

## Decisión ejecutiva

La primera oportunidad no es vender una “interfaz universal”, una cámara ni un
chatbot. Es ofrecer una **capa de comprensión y adaptación de flujos** sobre
sistemas que una institución ya utiliza.

La capa debe:

1. observar el flujo real del usuario;
2. detectar fricción observable: espera, error, retroceso, repetición, ayuda o
   abandono;
3. proponer una representación más clara y reversible;
4. comprobar si el flujo terminó correctamente;
5. entregar un informe institucional con evidencia antes/después.

La interfaz transparente es el medio de adaptación. El producto es la relación
entre **estado del flujo, representación y resultado**.

## Qué mostró el mercado

Esta revisión no estima el tamaño total del mercado. Identifica necesidades que
ya aparecen como objetos de compra en Mercado Público.

| Evidencia | Qué se está comprando | Lectura para FARMAKSIA |
|---|---|---|
| [869591-10-LP26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?qs=95%2FFWEC+dXz256RVZ%2FCRJw%3D%3D) y [anuncio de ChileCompra](https://www.chilecompra.cl/2026/08/participa-de-la-licitacion-para-el-servicio-de-diseno-y-desarrollo-del-nuevo-portal-api-de-mercado-publico/) | Capa de datos de negocio, contrato común, gobernanza, versionado, autenticación, cuotas y documentación para unificar ocho mecanismos de compra. | El mercado reconoce valor en una capa intermedia que conecta sistemas y hace sus estados utilizables; no exige reemplazar cada sistema de origen. |
| [Sistema de filas y tótem del Hospital de Coronel](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=1057429-13-LE26) | Gestión de atención presencial mediante tótem y flujo de espera. | Primer caso de uso concreto para medir orientación, elección, espera y abandono. |
| [Sistema de orden de atención de APS de la Armada](https://www.mercadopublico.cl/Procurement/Modules/RFB/StepsProcessAward/PreviewAwardAct.aspx?qs=DssZZuk2JLd+vQ5ZhoxV%2FHYJ1mvwCa9T+DK4fl0p+6M%3D) | Sistema de atención con criterios de precio, experiencia e implementación; adjudicación neta informada de $10.950.000. | Hay presupuesto visible para resolver el flujo, no sólo para comprar diseño visual. |
| [Programa de experiencia y viaje del paciente de Huechuraba](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?qs=BHs1aUO5tf8Ou7D1JzmDCQ%3D%3D) | Capacitación en experiencia, primer contacto y diseño del viaje del paciente. | La institución ya reconoce que el problema es el recorrido completo, no un botón aislado. |
| [Política de calidad y experiencia usuaria de ChileCompra](https://www.chilecompra.cl/wp-content/uploads/2026/01/004-B-Res.-Aprueba-politica-calidad-de-servicio-y-experiencia-usuaria-de-la-DCCP.pdf) | Diseño participativo, accesibilidad, análisis del comportamiento, eficiencia y mejora continua. | El lenguaje institucional compatible con FARMAKSIA es calidad medible del servicio y experiencia usuaria. |
| [Términos de referencia de sistema de atención integrado](https://conveniomarco.mercadopublico.cl/media/chilecompra/files/formattributes/t/r/trf_totem_14.pdf) | Tótem, pantallas, portal web, ficha/agendamiento, reportería, continuidad offline, soporte, autoadministración y SLA. Es una referencia técnica pública anterior, no una licitación 2026. | El punto de integración natural es el flujo completo: presencial, remoto, pantalla, agenda y sistema institucional. |

### Conclusión de mercado

La oportunidad inicial es **B2B/B2G de adaptación y evaluación**, no una app de
consumo. El comprador no necesita que FARMAKSIA “entienda toda la computadora”;
necesita saber dónde sus usuarios se traban y tener una mejora desplegable sin
reconstruir su sistema.

## Producto inicial

### Capa de comprensión operativa

```text
portal / tótem / aplicación existente
              |
              v
      adaptador de superficie
              |
              v
        estado observable
              |
              v
    plan de representación reversible
              |
              v
      overlay o cambio local
              |
              v
       resultado verificable
```

La unidad de trabajo no será una pantalla suelta. Será un **flujo** con inicio,
estados intermedios, errores, salidas y criterios de finalización.

Ejemplo hospitalario mínimo:

```text
llegada → elegir motivo → obtener turno → esperar → ser llamado → confirmar
```

El motor se activa por el input y por el cambio de estado. El mouse, teclado,
foco, selección, tiempo, error y retroceso son señales de interacción. No se
interpretan automáticamente como comprensión, preferencia o discapacidad.

## Capas de posible avance

### Capa 0 — contrato y privacidad

Define qué se puede observar, qué se puede modificar y qué resultado cuenta como
éxito.

- capacidades explícitas: `read_only`, `observe`, `overlay`, `execute_blocked`;
- no cámara, audio ni píxeles persistentes por defecto;
- eventos con timestamp, superficie, estado, fuente y procedencia;
- reversión y apagado del overlay;
- `UNKNOWN` cuando el adaptador no pueda identificar el estado.

**Objetivo:** que la capa sea auditable antes de ser inteligente.

### Capa 1 — observación pasiva

Usa lo que el sistema ya entrega:

- Windows UI Automation para controles, roles, nombres, foco y eventos;
- DOM/ARIA y trazas de navegador para aplicaciones web;
- teclado, mouse, cambios de ventana y tiempos como señales auxiliares;
- captura visual sólo como evidencia temporal y autorizada, no como fuente única.

En el entorno actual ya está disponible `pywinauto 0.6.9`, y el repositorio
cuenta con el adaptador experimental UIA de Windows.

**Objetivo:** construir un mapa del flujo sin cámara y sin modificar la
aplicación.

### Capa 2 — diagnóstico del recorrido

Calcula métricas observables:

- tiempo hasta la primera acción;
- éxito de cada transición;
- errores y reintentos;
- retrocesos y ciclos;
- solicitudes de ayuda o asistencia;
- abandono y tiempo de permanencia;
- proporción de sesiones con final verificable;
- diferencias por dispositivo, versión y punto del flujo.

No se debe reportar “el usuario entendió”. Se reporta “el usuario completó” o
“el sistema no pudo verificar el resultado”. La tasa de finalización debe usar
como denominador todas las transacciones iniciadas, incluidas las fallidas, tal
como se describe en el [Service Manual de GOV.UK](https://www.gov.uk/service-manual/measuring-success/measuring-completion-rate).

**Objetivo:** entregar un mapa de fricción que una institución pueda usar para
decidir.

### Capa 3 — adaptación visual reversible

El renderer puede alterar la presentación sin modificar el código de origen:

- aumentar o reducir densidad;
- ordenar pasos según el estado actual;
- resaltar el próximo control;
- reducir opciones simultáneas sin eliminar las restantes;
- mostrar ayuda contextual;
- adaptar tamaño, contraste, espaciado y lectura;
- devolver siempre a la representación original.

El cambio debe ser declarativo, versionado y condicionado a una precondición.
Para web, los requisitos de accesibilidad deben alinearse con [WCAG 2.2](https://www.w3.org/TR/WCAG22/), incluyendo identificación textual de
errores, instrucciones, ayuda y prevención de envíos equivocados.

**Objetivo:** demostrar que una misma aplicación puede ofrecer distintas rutas
de representación sin convertirse en una segunda aplicación.

### Capa 4 — adaptadores consolidados

Adopción concreta por superficie:

- **Windows:** UI Automation y `pywinauto` para aplicaciones nativas;
- **web:** Playwright/CDP para DOM, foco, snapshots y trazas;
- **accesibilidad web:** `axe-core` como gate estructural, no como prueba de
  comprensión;
- **eventos y métricas:** mapear posteriormente a OpenTelemetry después de
  congelar el contrato local.

La [UI Automation de Microsoft](https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-uiautomationoverview)
expone árboles de elementos, propiedades, patrones y eventos. [Playwright](https://playwright.dev/docs/api/class-tracing)
permite conservar una traza reproducible con snapshots y capturas. [axe-core](https://github.com/dequelabs/axe-core)
automatiza parte de las comprobaciones WCAG y deja explícitos los casos que
requieren revisión manual. [OpenTelemetry](https://opentelemetry.io/docs/concepts/instrumentation/)
servirá para exportar señales cuando su semántica y política de privacidad ya
estén definidas.

**Objetivo:** no crear un parser universal de pantallas; usar la mejor señal
estructurada disponible para cada superficie.

### Capa 5 — X-ANA-X y CODE-INE

Cuando el flujo ya esté identificado:

- **X-ANA-X** traduce una operación desconocida a una relación conocida, usando
  roles, pasos, diferencias y predicciones explícitas;
- **CODE-INE** convierte una propuesta de cambio en un patch inspeccionable,
  con precondición, preview, verificación y rollback;
- la capa común conserva fuente, versión, permisos y resultado.

Así el sistema puede explicar: “este botón cumple el rol de confirmar”, pero no
puede afirmar que dos aplicaciones son equivalentes sólo porque se parecen.

**Objetivo:** pasar de adaptar apariencia a adaptar significado operativo.

### Capa 6 — VIZZ opcional

VIZZ entra después como señal de orientación y atención, no como requisito de
entrada:

- mirada, pose, distancia o mouse pueden ayudar a elegir el foco;
- la cámara debe poder permanecer apagada;
- si la señal es inestable, el sistema vuelve a foco, teclado, mouse o una
  selección explícita;
- jamás se debe bloquear un trámite crítico por una estimación ocular.

**Objetivo:** enriquecer la adaptación sin convertir una webcam en autoridad.

### Capa 7 — evaluación institucional

La salida final para una institución no es una animación. Es un paquete de
decisión:

- mapa del flujo y sus dependencias;
- puntos de fricción priorizados;
- versión original y versión adaptada;
- métricas antes/después;
- incidentes y casos `UNKNOWN`;
- accesibilidad estructural;
- impacto en soporte, tiempo y finalización;
- plan de integración y límites.

## Qué queda fuera del primer producto

- un agente autónomo con permisos de ejecución;
- interpretación universal desde screenshots;
- diagnóstico médico, cognitivo o visual;
- inferir ansiedad, comprensión o discapacidad desde clicks, dwell o mirada;
- reemplazar ficha clínica, agenda, identidad o sistema de turnos;
- aprender una política con datos de una institución sin contrato de datos,
  procedencia y verificación.

## Predicción de viabilidad

Esta es una predicción de ingeniería, no una estimación estadística del mercado:

| Dirección | Viabilidad | Motivo |
|---|---:|---|
| Diagnóstico de flujo web/Windows | Alta | Existen señales estructuradas y herramientas maduras. |
| Overlay reversible sobre un flujo conocido | Media-alta | Requiere identificar estados y manejar excepciones, pero no reemplaza el sistema. |
| Adaptación multiinstitución con contratos de superficie | Media | Escala si cada institución entrega acceso o un adaptador definido. |
| Entender cualquier app sólo mirando la pantalla | Baja | La imagen no garantiza roles, estado, permisos ni resultado. |
| VIZZ como entrada obligatoria | Baja | Introduce permisos, variabilidad y fallos que no son necesarios para el valor inicial. |

La apuesta recomendada es comenzar donde el problema ya tiene presupuesto y
criterios operativos: atención, turnos, admisión y orientación. Después se puede
llevar la misma capa a educación, portales públicos, software técnico y
CODE-INE/X-ANA-X.

## Próximo objetivo de desarrollo

Construir un **adaptador de flujo demostrable** con dos superficies:

1. un flujo web de cuatro estados;
2. una ventana Windows equivalente;
3. el mismo contrato de eventos para ambas;
4. diagnóstico de fricción;
5. un overlay reversible de orientación;
6. pruebas de que no intercepta input ni inventa éxito.

El criterio de avance será poder mostrar el mismo flujo semántico en dos
aplicaciones distintas y explicar, con evidencia, qué cambió, por qué cambió y
si el resultado se verificó.

## Fuentes y límites de la investigación

La revisión se basó en fichas y documentos públicos de ChileCompra, política
institucional, estándares W3C y documentación primaria de las herramientas. Las
licitaciones son evidencia de necesidades y lenguaje de compra; no prueban por
sí solas que FARMAKSIA sea adjudicable ni que una adaptación mejore la
experiencia humana. El siguiente paso comercial requeriría revisar bases
completas, requisitos de proveedor, seguridad, tratamiento de datos y un caso
piloto con una institución.
