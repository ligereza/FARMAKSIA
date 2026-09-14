# Conexiones activas de X-ANA-X

## Base

X-ANA-X es el motor de integración. Su rama main contiene el núcleo común;
sus ramas de dominio son PUPILA, FARMAKSIA y LUCIDA.

## Repositorios conectados directamente

| Repositorio | Función en el sistema | Ruta canónica en X-ANA-X |
|---|---|---|
| FARMAKSIA | Investigación, hipótesis, contratos, evidencia y experimentos | rama FARMAKSIA / FARMAKSIA/farmaksia |
| PUPILA | Asistencia, transferencia analógica y representación perceptual | rama PUPILA / PUPILA/assistance y PUPILA/visual |
| LUCIDA | Integración transparente con aplicaciones de escritorio | rama LUCIDA / LUCIDA/ y LUCIDA/resolume/adapter |

La dirección de integración es:

FARMAKSIA aporta evidencia -> X-ANA-X conserva el contrato -> PUPILA decide
la ayuda -> LUCIDA la proyecta hacia una aplicación.

Una mejora del núcleo común entra primero por X-ANA-X/main y después se porta
a las ramas consumidoras. Una mejora de dominio se conserva primero en su
repo separado y luego se porta a la rama homóloga de X-ANA-X.

## Conexión futura

XIO será una fuente móvil y multiusuario de señales, registro y transporte
para LUCIDA/Multi. No es una dependencia del runtime actual y no debe recibir
trabajo de integración hasta que exista un contrato explícito.

## Fuera de la conexión activa

MAK, FLUJO, MAT-SI, WACHUMA e IRIS no son superficies activas conectadas a
X-ANA-X en esta configuración. Sus ideas o resultados solo entran mediante
un commit, contrato o evidencia seleccionada; no se copian como módulos ni
se convierten automáticamente en ramas nuevas.

## Regla de procedencia

Cada cambio portado debe conservar el repo y commit de origen, el destino en
X-ANA-X, las pruebas ejecutadas y los límites que siguen sin verificarse.
