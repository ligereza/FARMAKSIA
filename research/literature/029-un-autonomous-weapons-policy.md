# Research 029 — ONU, armas autónomas y control humano significativo

**Fecha de corte:** 2026-08-31  
**Pregunta:** ¿Qué ha pedido la ONU respecto de las armas autónomas y qué
implicación tiene para una capa de interfaz, diálogo y verificación como
FARMAXIA?

## Respuesta corta

Hay que separar tres cosas que suelen mezclarse:

1. **Llamado político:** el Secretario General y el Comité Internacional de
   la Cruz Roja (CICR) han pedido negociar un instrumento jurídicamente
   vinculante.
2. **Resoluciones de la Asamblea General:** expresan orientación política,
   solicitan informes, consultas y trabajo multilateral; no son por sí solas
   el tratado vinculante que se está pidiendo.
3. **Negociación técnica:** el Grupo de Expertos Gubernamentales de la
   Convención sobre Ciertas Armas Convencionales (CCW/GGE) sigue elaborando
   elementos posibles de un instrumento. Su sesión del 31 de agosto al 4 de
   septiembre de 2026 continúa el trabajo y todavía no fija la forma jurídica
   definitiva.

El llamado renovado el 27 de agosto de 2026 pide dos líneas de prohibición:

- sistemas cuyo resultado de fuerza sea impredecible para el operador;
- sistemas autónomos que seleccionen deliberadamente a seres humanos como
  objetivos.

Para los demás sistemas, la dirección que aparece en el proceso de la ONU es
una combinación de restricciones y obligaciones positivas que mantengan
**control y juicio humanos reales**, responsabilidad, previsibilidad y
cumplimiento del derecho internacional humanitario. “Hay una persona mirando
la pantalla” no basta si la interfaz oculta el estado, la persona no entiende
el sistema o no puede intervenir a tiempo.

## Qué está respaldado por documentos de la ONU

La resolución **A/RES/79/62** (2 de diciembre de 2024) afirma que el derecho
internacional, el derecho internacional humanitario, los derechos humanos y el
derecho penal internacional se aplican a estos sistemas. Reafirma que no debe
usarse ningún arma que no pueda emplearse de conformidad con el derecho
internacional humanitario, subraya la importancia del papel humano para la
responsabilidad y la rendición de cuentas, y reconoce un enfoque de dos niveles:
prohibiciones para sistemas inaceptables y regulación para los demás.

La resolución **A/RES/80/57** fue adoptada por la Asamblea General el 1 de
diciembre de 2025, con 164 votos a favor, 6 en contra y 7 abstenciones. Que una
resolución tenga un apoyo amplio no significa que ya exista una prohibición
universal ni un tratado en vigor.

El llamado del Secretario General de 2023 propuso concluir en 2026 un
instrumento vinculante que prohíba los sistemas que funcionen sin control o
supervisión humanos y que no puedan emplearse de conformidad con el derecho
internacional humanitario, y que regule los demás sistemas autónomos.

El comunicado conjunto ONU–CICR del 27 de agosto de 2026 actualiza el sentido
político de esa petición: no esperar a que el problema se resuelva por
incrementos técnicos, sino iniciar una negociación con prohibiciones y
restricciones claras. La sesión del GGE de 2026 tiene el mandato de seguir
formulando elementos de un instrumento **sin prejuzgar todavía su naturaleza**.

Fuentes primarias:

- [ONU–CICR: llamado renovado del 27 de agosto de 2026](https://egypt.un.org/en/321747-un-chief-red-cross-renew-call-rules-lethal-autonomous-weapons)
- [A/RES/79/62, resolución de la Asamblea General de 2024](https://documents.un.org/doc/undoc/gen/n24/391/35/pdf/n2439135.pdf)
- [Registro oficial de A/RES/80/57, resolución de 2025](https://digitallibrary.un.org/record/4095989?ln=en&v=%5B%27pdf%27%5D)
- [A/RES/78/241, primera resolución específica de la Asamblea General, 2023](https://digitallibrary.un.org/record/4033027/)
- [Sesión 2026 del GGE sobre LAWS](https://indico.un.org/event/1019358/)
- [Agenda pública de la sesión del GGE en UN Web TV](https://webtv.un.org/en/asset/k1u/k1uqk11u2f)
- [A/79/88, informe del Secretario General con las posiciones recibidas](https://documents.un.org/doc/undoc/gen/n24/154/32/pdf/n2415432.pdf)

## Qué no debe confundirse

**Autonomía no es lo mismo que automatización.** Un sistema que ordena,
filtra, resalta o calcula una recomendación puede ser automatizado sin decidir
por sí solo un uso letal de la fuerza. El problema regulatorio aumenta cuando
el sistema selecciona o compromete efectos sobre personas sin una decisión
humana significativa.

**Control humano no es un clic decorativo.** El control debe ser informable,
predecible, temporalmente suficiente y capaz de cambiar el resultado. Una
confirmación que aparece después de que el sistema ya comprometió la acción no
es control efectivo.

**Explicación no es justificación.** Mostrar una frase generada por un modelo
no prueba que la salida sea correcta. La interfaz debe exponer evidencia,
incertidumbre, límites, versión del modelo, estado de autorización y opciones
de detener o escalar.

## Traducción para FARMAXIA

Esto no convierte a FARMAXIA en un sistema de armas. Define una frontera
arquitectónica que hace más fuerte su núcleo de interfaz adaptativa:

### CODE-INE — trazabilidad y compromiso

Debe funcionar como un registro reproducible de:

```text
entrada → transformación → evidencia → incertidumbre → propuesta
→ confirmación humana → resultado verificado
```

No debe registrar sólo “acción ejecutada”. Debe conservar qué sabía el sistema,
qué desconocía, qué alternativa propuso, quién tenía capacidad para confirmar,
qué versión produjo la propuesta y si la acción fue cancelada o corregida.

### X-ANA-X — comprensión y reparación

Su función adecuada en contextos críticos es enseñar el estado, comparar
alternativas y reparar una interpretación, no persuadir al operador ni
convertir una analogía en una orden. La analogía termina con:

```text
equivalencia → diferencia → límite → elección explícita
```

El diálogo puede ofrecer “explicar”, “mostrar evidencia”, “mantener espera” o
“escalar”. No debe penalizar la duda ni premiar la velocidad por encima del
resultado verificado.

### VIZZ — atención sin autoridad oculta

La mirada, el mouse, el teclado o el giro de cabeza pueden servir para dirigir
la atención hacia información relevante. No deben convertirse silenciosamente
en autorización de una acción irreversible. La capa visual puede reordenar y
hacer legible el estado, pero tiene que preservar:

- qué está activo;
- qué es una sugerencia y qué es una orden;
- nivel y fuente de incertidumbre;
- consecuencias antes del compromiso;
- ruta visible de pausa, cancelación o escalamiento.

## Experimento seguro y útil

No necesitamos conectar armas, drones ni sistemas reales. Podemos construir un
simulador de operación crítica no letal —por ejemplo, coordinación de rescate
o inspección industrial— con un agente que reciba observaciones incompletas y
proponga estados.

Comparar tres capas:

1. interfaz que muestra sólo la recomendación;
2. interfaz que muestra recomendación, evidencia e incertidumbre;
3. interfaz que además exige confirmación contextual, permite mantener espera
   y conserva un handoff completo.

Inyectar estados normales, ambiguos, contradictorios y cambiantes. Medir:

- reconocimiento correcto del estado;
- falsas certezas;
- decisiones de continuar, esperar o escalar;
- capacidad de corregir una interpretación;
- tiempo y carga de interacción;
- completitud del registro de auditoría;
- diferencia entre “humano presente” y “humano realmente informado”.

El resultado que nos interesa no es que el sistema actúe más rápido. Es que
reduzca compromisos mal entendidos y haga visible cuándo la autonomía del
software excede la comprensión humana.

## Decisión

Adoptar para FARMAXIA un **contrato de control humano significativo** como
requisito transversal de las capas CODE-INE, X-ANA-X y VIZZ. La primera
implementación debe vivir en simulación y en interfaces civiles o industriales
no letales. Cualquier uso posterior en un contexto militar se limita a
investigación pública de interfaz, entrenamiento, auditoría y simulación; no
se implementa selección de objetivos, compromiso de fuerza, control de armas ni
vigilancia encubierta.

### Kill tests

- La interfaz muestra “confirmar”, pero el sistema ya actuó: **falla**.
- El operador no puede distinguir evidencia de inferencia: **falla**.
- La incertidumbre se oculta para aumentar la velocidad: **falla**.
- El modelo no puede reconstruir por qué propuso una acción: **falla**.
- El usuario que pausa correctamente obtiene peor evaluación que quien adivina
  rápido: **falla de incentivo**.
- Cambiar el layout hace desaparecer una advertencia crítica: **falla de
  renderer**.

## Estado de conocimiento

**Conocido:** existe una petición política explícita y reiterada de negociar un
instrumento vinculante; la Asamblea General mantiene el tema en agenda; hay
convergencia amplia sobre la necesidad de control humano y de aplicar el derecho
internacional.

**No resuelto:** definición jurídica universal de “autonomía”, umbral operativo
de “control humano significativo”, alcance exacto de las prohibiciones, foro y
texto final del instrumento, y cómo verificar estos requisitos en sistemas
complejos y adaptativos.

**Implicación:** esa zona no resuelta es precisamente un terreno fértil para
FARMAXIA como infraestructura de evidencia, comprensión, incertidumbre y
auditoría; no como automatizador de la fuerza.

