# Handoff 002 — `XIO_LAYER` duplicado entre XIO y LUCIDA

**Fecha:** 2026-09-07
**Estado:** medido; la decisión queda abierta
**Propósito:** documentar una violación de la regla de responsabilidades con
evidencia suficiente para decidir, sin ejecutar la consolidación

## La regla que se rompió

El mapa de responsabilidades de este repositorio dice, textualmente:

> No se deben copiar implementaciones, assets o configuraciones entre ellos
> sólo porque compartan conceptos.

Y asigna las responsabilidades sin ambigüedad:

| Superficie | Responsabilidad | No es |
|---|---|---|
| XIO | señales, conectividad, registro, selección de adaptadores, handoff y replay | una ventana flotante o un renderer |
| LUCIDA/MULTI | frontera de consumo multiusuario dentro de LUCIDA | la captura o el transporte de red propietario |

## Lo medido

El paquete `XIO_LAYER/` existe en dos repositorios a la vez:

```text
XIO      codex/xio-transport   XIO_LAYER/   56 archivos
LUCIDA   MULTI                 XIO_LAYER/   47 archivos
```

Las 47 rutas de LUCIDA existen todas en XIO. De ellas, **19 son byte-idénticas
y 28 divergen** — 25 de las divergentes son `.py`, e incluyen el núcleo
completo: `core/transport/transport.py`, `core/transport/protocols.py`,
`core/sessions/peer_session.py`, `core/events/log.py`,
`core/events/replay_jsonl.py`, `core/snapshots/checkpoint.py`,
`core/snapshots/projector.py`, `core/audit/ledger.py`,
`core/audit/permissions.py`, `core/contracts/models.py` y siete archivos de
prueba.

Los 9 archivos exclusivos de XIO son precisamente la maquinaria de handoff
—`adapters/handoff.py`, `adapters/handoff_store.py`, `adapters/local_source.py`,
`core/file_lock.py`, sus pruebas y un fixture de registros— es decir, lo que
la tabla de arriba asigna a XIO y no a LUCIDA.

## Dirección de la divergencia

La versión de XIO es más grande en **los 28 archivos**, sin excepción. Al
clasificar por dirección, 6 archivos son adición pura de XIO y 22 aparecen
como divergencia mutua; pero al inspeccionar los diffs, las líneas
"exclusivas" de LUCIDA son los originales que XIO reemplazó por versiones más
estrictas. Ejemplo de `core/transport/protocols.py`, donde LUCIDA tiene:

```python
object.__setattr__(self, "arguments", tuple(deepcopy(self.arguments)))
```

y XIO tiene ese mismo efecto más una comprobación de tipo, el manejo del
`TypeError`, y una validación de que el envelope sea JSON-safe.

**Conclusión de la medición:** no es un fork con intención divergente. La copia
de LUCIDA es una instantánea anterior y menos validada de la de XIO. No se
encontró ninguna capacidad presente en LUCIDA y ausente en XIO.

## La rama `MULTI` no tiene código propio

El hallazgo decisivo no es la divergencia sino el contenido. La rama completa,
en archivos trackeados, es:

```text
.gitignore                1
README.md                 1
multi/                    1   (sólo multi/README.md)
XIO_LAYER/               47
                     ──────
                         50
```

`multi/` —el directorio que debería contener la frontera de consumo
multiusuario de LUCIDA— tiene un solo archivo y es un README. No hay una línea
de código de LUCIDA en la rama, y nada importa `multi/`. Los 39 archivos `.py`
de la rama están todos dentro de `XIO_LAYER/`.

Las 65 pruebas de la rama (más 7 subtests) viven también todas en
`XIO_LAYER/tests/`: son las pruebas de XIO ejercitando el paquete de XIO. La
rama no prueba nada suyo porque no tiene nada suyo.

El propio `multi/README.md` lo dice en su segunda frase:

> This branch contains the router-agnostic transport and peer-session layer
> **extracted from XIO**.

Es decir: la frontera que la tabla asigna a LUCIDA/MULTI no está escrita, y lo
que ocupa la rama es exactamente aquello que la tabla declara que MULTI **no
es** —la captura y el transporte de red—. La duplicación no es que dos
superficies implementaran lo mismo; es que una superficie quedó sin escribir y
en su lugar hay una copia de la otra.

## Lo que no se hizo, y por qué

No se borró la copia de LUCIDA. Quitar 47 archivos de una rama es difícil de
revertir, y la forma de la dependencia —submódulo, paquete instalable, o
contrato vendorizado con su hash— es una decisión de arquitectura con
consecuencias de operación, no un detalle de limpieza. La medición existe para
que sea una decisión y no una corazonada.

## Preguntas abiertas

1. ¿Qué es la frontera de consumo multiusuario de LUCIDA, si no es el
   transporte? Es la pregunta de producto que la rama dejó sin responder, y
   ninguna medición la contesta.
2. ¿Cómo consume LUCIDA la capa de XIO sin copiarla? La regla prohíbe copiar,
   pero no nombra el mecanismo de dependencia: submódulo, paquete instalable,
   o contrato vendorizado con su hash registrado.
3. Las tres ramas `codex/xio-*` de XIO no están mencionadas en su README ni en
   `CAPACIDADES.md`, y `main` no tiene `XIO_LAYER` en absoluto. Antes de
   declarar a XIO como fuente única hay que decidir qué rama de XIO lo es.

## Regla de honestidad

Esta medición demuestra duplicación, dirección de la divergencia, ausencia de
capacidades perdidas y ausencia de código propio en `MULTI`. No demuestra qué
mecanismo de dependencia conviene ni qué debería ser la frontera multiusuario;
eso es una decisión de producto. Tampoco se ejecutó la consolidación: borrar
47 archivos de una rama es difícil de revertir, y la medición existe para que
la decisión sea una decisión y no una corazonada.
