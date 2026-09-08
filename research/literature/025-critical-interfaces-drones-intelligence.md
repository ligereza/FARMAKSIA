# Research 025 — interfaces críticas, drones e inteligencia

**Fecha de corte:** 2026-08-31  
**Pregunta:** ¿Qué pueden enseñarnos las interfaces públicas de sistemas UAS,
análisis de inteligencia y equipos humano-máquina para construir una capa
adaptativa de representación en FARMAXIA, sin convertirla en un sistema de
control, vigilancia o armamento?

## Límite del estudio

Se revisaron fuentes oficiales, repositorios abiertos y un estudio empírico
reciente. “Inteligencia” se usa aquí como análisis de información, trazabilidad
y toma de decisiones bajo incertidumbre. Quedan fuera instrucciones de
adquisición clandestina, evasión, intrusión, selección de blancos, empleo de
armas y control operativo de vehículos reales. El valor transferible está en la
interfaz y en la verificación, no en la capacidad ofensiva del sistema.

## Veredicto

La idea fértil no es copiar una consola militar. Es construir una **capa de
representación de estados y evidencias** que pueda colocarse sobre distintas
aplicaciones:

```text
señales / documentos / eventos
        ↓
estado normalizado + tiempo
        ↓
provenance + incertidumbre + conflictos
        ↓
representación adaptada a tarea y atención
        ↓
input explícito / acción reversible
        ↓
resultado independiente + auditoría
```

Esto conecta los tres frentes sin forzarlos a ser una sola app:

- **VIZZ** decide qué relación merece atención, con qué tamaño, contraste,
  posición, ritmo y modalidad. No inventa el estado ni ejecuta acciones.
- **X-ANA-X** transforma una tarea o procedimiento conocido en una vista
  familiar: alinea etapas, roles, dependencias y diferencias; no superpone
  píxeles al azar.
- **CODE-INE** convierte ese estado en contratos, parches declarativos,
  logs y verificadores. La animación puede expresar transición o incertidumbre,
  pero no reemplaza una prueba.

## Lo que enseñan los sistemas consolidados

### 1. La interfaz es parte de la seguridad, no una capa decorativa

La FAA identifica como problemas de factores humanos para UAS la asignación de
funciones entre piloto y sistema, la información necesaria para reconocer el
estado normal y anormal, la distracción y las limitaciones del observador.
También plantea desarrollar guías mínimas para las estaciones de control.
[FAA, UAS Human Factors Considerations](https://www.faa.gov/sites/faa.gov/files/uas/research_development/information_papers/UAS-Human-Factors-Considerations.pdf)

La consecuencia para FARMAXIA es concreta: cada representación debe declarar
qué queda a cargo del sistema, qué queda a cargo de la persona y qué evidencia
permite revisar la transición. Una interfaz atractiva que oculta el estado es
un fracaso, aunque sea técnicamente fluida.

### 2. Separar vistas reduce la mezcla de tareas

QGroundControl separa vistas de vuelo, planificación, análisis, configuración y
ajustes. En la vista de vuelo muestra estado, acciones, video, telemetría,
actitud y mapa; las acciones importantes requieren una selección y confirmación
contextual. Su documentación también expone estados de conexión, GPS, batería,
radio, telemetría y modo de vuelo como indicadores diferenciados.
[QGroundControl UI Overview](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/getting_started/ui_overview.html)
[QGroundControl Fly View](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/fly_view/fly_view.html)

No debemos copiar el mando de vuelo. Debemos adoptar la decisión de diseño:
**una capa común puede reordenar la presentación, pero no debe mezclar
observación, planificación, acción y análisis posterior en una misma superficie
sin estados visibles**. QGroundControl es una referencia de arquitectura de
interfaz, no una dependencia necesaria del primer prototipo.

### 3. La incertidumbre debe ser visible y explicable

El estándar ICD 203 de ODNI exige expresar la incertidumbre de los juicios y
explicar su base, incluyendo calidad y cantidad de fuentes, vacíos de
conocimiento, supuestos y posibles sesgos.
[ODNI ICD 203](https://www.dni.gov/files/documents/ICD/ICD-203.pdf)

OpenCTI separa el observable —un dato crudo e inmutable— del indicador, que
añade contexto de detección; permite navegar relaciones, historial, contenido,
análisis y avistamientos.
[OpenCTI, Observations](https://docs.opencti.io/latest/usage/exploring-observations/)

MISP estructura eventos, atributos, objetos, relaciones, opiniones, análisis,
correlaciones, filtros y trazas de auditoría; además mantiene API y formatos de
intercambio.
[MISP, repositorio oficial](https://github.com/MISP/MISP)

La adopción conceptual es más importante que instalar esas plataformas:

```text
observable ≠ interpretación ≠ decisión
fuente     ≠ corroboración independiente
alerta     ≠ orden
confianza  ≠ probabilidad de que el mundo sea cierto
```

Una capa FARMAXIA debe poder decir “dos señales apuntan a lo mismo, pero
comparten origen” y evitar que la misma evidencia parezca confirmada dos veces.

### 4. El operador actualiza creencias, no sólo mueve controles

Un estudio de 2026 sobre supervisión de un dron autónomo comparó panel simple,
realce visual, señal háptica y combinación multimodal. Con 30 participantes en
una simulación VR, la condición multimodal obtuvo menor latencia media y mayor
probabilidad local de reportar correctamente cambios; la señal háptica aislada
fue más rápida que el control, pero mostró mayor carga y menor consistencia que
la combinación.
[Sun et al., Frontiers in Robotics and AI, 2026](https://doi.org/10.3389/frobt.2026.1707022)

El hallazgo útil no es “agregar vibración”. Es que cada modalidad puede cumplir
un papel distinto: una señal rápida orienta la atención y otra entrega el
significado. Las señales abstractas sin semántica pueden aumentar el trabajo
mental. En FARMAXIA, color, movimiento, sonido o háptica sólo deben aparecer
cuando tengan una semántica estable, redundancia controlada y una salida
estática equivalente.

### 5. La interfaz debe mostrar relaciones espacio-temporales

Un trabajo de diseño para una constelación de vehículos no armados en búsqueda
y rescate propone representar áreas de búsqueda, posiciones, comunicaciones,
energía, notificaciones y evolución temporal, reduciendo la incertidumbre sobre
la posición de cada activo y dejando al operador influir en su comportamiento.
[Anderson et al., Human Factors and Ergonomics Society, 2021](https://doi.org/10.1177/1071181321651130)

La lección para una interfaz genérica es el paso de “lista de botones” a
**mapa de estado**: qué cambió, qué depende de qué, qué está atrasado, qué
fuente lo respalda y qué decisión queda pendiente.

## Referencias abiertas que sí conviene aprovechar

| Referencia | Adopción para FARMAXIA | No hacer |
|---|---|---|
| QGroundControl | estudiar separación Fly/Plan/Analyze/Setup, indicadores de estado, confirmación contextual y replay de logs | conectar vehículos reales o copiar funciones de control |
| OpenCTI | tomar observable/indicador, relaciones, historial, fuente y marcas de acceso | importar inteligencia o convertir un grafo en “verdad” |
| MISP | tomar eventos, atributos, correlaciones, opiniones, auditoría y formatos portables | descargar corpus de amenazas o integrar sincronización externa |
| OpenTelemetry | usarlo después de congelar el evento FARMAXIA para exportar trazas/medidas | registrar píxeles, cámara o contenido sensible por defecto |
| OpenAdapt / OSWorld | estudiar record→compile→gate→replay→verify y la taxonomía de fallos | usar agentes generales para actuar sin precondición ni verificador |

La investigación respalda adoptar patrones y contratos; no respalda descargar
cinco plataformas pesadas para producir una demostración superficial. El primer
atajo correcto es construir un fixture local que imite el tipo de estado, no
instalar sus bases de datos.

## Modelo matemático de la capa

Representemos el estado real por `z_t`, la evidencia disponible por `e_t`, la
tarea por `τ_t` y el estado de atención por `a_t`. La interfaz observa sólo una
parte y decide una representación `r_t`:

```text
belief_t = P(z_t | e_0:t, r_0:t, actions_0:t)
r_t      = policy(belief_t, τ_t, a_t, budget_visual)
```

Si la representación cambia lo que la persona observa o hace, el sistema ya no
es una simple función de pantalla: es un proceso parcialmente observable y
controlado. Por eso el contrato debe registrar exposición, input y resultado.

Para elegir qué mostrar, una primera política puede maximizar utilidad de tarea
menos costo visual/cognitivo:

```text
score(S) = utilidad_de_decisión(S)
           − λ · costo_de_atención(S)
           − μ · ambigüedad(S)
```

`S` es el conjunto de relaciones mostradas. Los avisos críticos tienen una
restricción dura de visibilidad; no compiten como simples adornos. La selección
puede reutilizar la idea de selección submodular ya explorada en FARMAXIA, pero
la métrica debe premiar corrección y transferencia, no número de clicks ni
tiempo mirando.

Para evidencia correlacionada, cada observación conserva un conjunto de raíces:

```text
evidence_id, root_ids, source, observed_at, valid_until,
derivation, confidence, assumptions, access_marking
```

Dos salidas derivadas del mismo `root_id` aumentan contexto, no independencia.
Una contradicción crea una rama de hipótesis; no se resuelve eligiendo la que
se vea más convincente.

## Propuesta de primer prototipo ambicioso pero controlable

### “Evidence Operations Layer”

Un escenario local y benigno, sin hardware ni control de drones:

1. Un simulador genera eventos temporales de varios sensores, documentos y
   estados de sistema.
2. Cada evento tiene fuente, antigüedad, dependencia, confianza, conflicto y
   costo de verificación.
3. La capa crea tres vistas sobre la misma evidencia:
   - **Situación:** resumen espacial/temporal y cambios recientes.
   - **Explicación:** qué observación respalda cada afirmación y qué falta.
   - **Acción:** sólo acciones reversibles como marcar, comparar, pausar,
     solicitar verificación o volver a una versión anterior.
4. VIZZ adapta saliencia y densidad según tarea, foco y carga observable; si no
   hay señal suficiente, conserva una vista estable.
5. X-ANA-X ofrece una analogía entre dos procedimientos y dibuja explícitamente
   equivalencias, diferencias y límites.
6. CODE-INE registra el plan declarativo, los parches visuales, la exposición y
   el verificador de resultado.

### Prueba que demostraría valor

Comparar una interfaz plana contra la capa adaptativa en tareas donde el usuario
deba:

- detectar qué cambió;
- distinguir evidencia primaria de una derivación repetida;
- encontrar una contradicción;
- explicar qué se sabe, qué se infiere y qué falta;
- recuperar una vista anterior sin perder el estado.

Medir tiempo hasta la actualización correcta, falsos positivos, omisiones,
calidad de la explicación, recuperación, carga subjetiva y latencia. El click
solamente mide exposición o intención local; no prueba comprensión.

## Riesgos y kill tests

- **Persuasión visual:** una animación o color hace que una hipótesis parezca
  más verdadera que otra. Kill test: ocultar el estilo y verificar que la
  decisión conserve su base y nivel de confianza.
- **Corroboración falsa:** varias tarjetas nacen del mismo evento. Kill test:
  duplicar un root y exigir que el nivel de independencia no aumente.
- **Sobrecarga adaptativa:** el layout cambia tanto que el usuario pierde el
  mapa mental. Kill test: alternar incertidumbre y comprobar estabilidad con
  histéresis y retorno manual.
- **Automatización silenciosa:** la capa cambia una aplicación o ejecuta una
  orden sin input explícito. Kill test: todas las mutaciones requieren
  precondición, confirmación y rollback o quedan en modo simulación.
- **Falsa generalización:** una mejora en simulación se presenta como mejora en
  operaciones reales. Kill test: separar evidencia de laboratorio, tareas
  humanas y condiciones operativas; no hacer claims de seguridad militar.

## Decisión de investigación

**Sí adoptar:** el patrón estado→evidencia→representación→input→resultado;
vistas separadas; provenance; incertidumbre explícita; políticas adaptativas
con histéresis; acciones reversibles; evaluación basada en decisiones.

**No adoptar todavía:** control de drones, vigilancia encubierta, captura
continua de pantalla/cámara, corpus de amenazas, agentes autónomos generales,
ML que infiera intención sin verificador o una interfaz que “se sienta
inteligente” sin poder explicar sus fuentes.

**Siguiente paso:** implementar sólo los contratos y un simulador sintético del
Evidence Operations Layer, reutilizando los invariantes de ledger, provenance,
RepresentationPlan y OutcomeVerifier existentes. Si el prototipo no mejora la
actualización correcta y la trazabilidad bajo una carga controlada, se detiene
la línea antes de añadir modelos, hardware o integraciones externas.

