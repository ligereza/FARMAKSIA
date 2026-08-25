# Experimento 056 — renderer de representación generativa

Fecha: 2026-08-25

## Pregunta

¿Puede una misma escena semántica producir experiencias distintas cuando
cambia el plan de representación, sin cambiar la información de origen?

## Idea

Este es el primer renderer de FARMAKSIA. No es una aplicación final ni un
framework de componentes. Es un laboratorio visual local que conserva una
escena fija —un operador aprende a construir y verificar un flujo de mensajes—
y la presenta con cinco lógicas:

| Vista | Compuesto | Qué prioriza |
|---|---|---|
| Panel | baseline | inventario completo y comparación rápida |
| Guía | VIZZ | dónde mirar, qué hacer y qué sigue |
| Mapa | VIZZ + X-ANA-X | relaciones entre objetivo, mensaje, worker y prueba |
| Analogía | X-ANA-X | transferencia entre una fila física y una cola computacional |
| Constructor | CODE-INE | intención, estructura, código, preview y verificación |

La fuente semántica no cambia. Se puede modificar intensidad visual y paso de
revelación para observar cómo cambia la representación.

## Ejecutar

Abrir directamente `renderer.html` en el navegador. No necesita servidor,
dependencias, cámara, red ni API key.

Desde PowerShell:

```powershell
Start-Process (Resolve-Path 'renderer.html')
```

Verificar el contrato:

```powershell
.\.venv\Scripts\python.exe run_contract_test.py
.\.venv\Scripts\python.exe run_experiment.py
```

## Controles

- **Vista:** cambia la lógica de representación, no la escena.
- **Intensidad:** modifica contraste, densidad y énfasis del renderer.
- **Paso:** cambia el punto activo de la guía y del constructor.
- **Movimiento:** permite comparar transiciones con movimiento o en modo
  reducido.
- **Restaurar:** devuelve el plan inicial.

## Contrato

El renderer debe:

- conservar los mismos IDs semánticos en las cinco vistas;
- mostrar explícitamente el plan activo;
- no abrir cámara ni leer pantalla, teclado o mouse;
- no ejecutar código generado;
- no depender de red ni de recursos externos;
- permitir volver al estado inicial;
- declarar desconocidos o ausencias en lugar de inventar relaciones.

## Qué demuestra y qué no

Demuestra que una escena fija puede ser recompuesta como panel, recorrido,
grafo, analogía y flujo de construcción dentro de un mismo contrato visual.

No demuestra todavía que una persona aprenda más rápido, comprenda mejor o
prefiera una vista. Esas preguntas requieren pruebas humanas posteriores. Este
experimento mide primero la capacidad computacional de representar la misma
semántica sin perder su identidad.

## Kill tests

1. Si alguna vista altera los IDs o inventa nodos, el contrato falla.
2. Si el renderer contiene captura de cámara, red o ejecución de código, el
   contrato falla.
3. Si cambiar intensidad cambia la escena semántica, la adaptación contamina
   la fuente.
4. Si el botón de restaurar no devuelve el plan inicial, la transformación no
   es reversible.
5. Si el mapa o la analogía muestran una relación no declarada, la vista debe
   marcarla como no disponible.
