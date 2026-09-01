# Decisión 090 — Derivar una capa común de ZIGO para VIZZ y PUPILA

## Decisión

Adoptar sólo la estructura verificable de la extracción `generic-interface-layer`
de ZIGO: contexto normalizado, señales acotadas, propuestas explícitas,
auditoría encadenada y replay. Implementarla en un slice aislado de FARMAKSIA
con dos adaptadores distintos:

- VIZZ: convierte señales consentidas de una superficie en una política de
  representación no bloqueante.
- PUPILA: compara resúmenes de varios participantes de una misma sala y genera
  una propuesta emergente, reversible y pendiente de aceptación.

## Razón

El mismo motor de contratos puede servir a ambos productos, pero el significado
de sus estados no es el mismo. VIZZ organiza cómo aparece la información;
PUPILA organiza cómo aparece una relación entre usuarios. Mantenerlos como
adaptadores separados permite reutilizar infraestructura sin crear una falsa
interfaz universal.

## Evidencia

- `experiments/090-farmaxia-adaptive-representation-layer/run_contract_test.py`
  pasa cinco pruebas offline.
- La procedencia del experimento valida agentes, actividades, entidades y
  consultas.
- La demo produce dos estados VIZZ y una propuesta PUPILA para dos usuarios de
  la misma sala.

## Límites

- No se guardan frames, vídeo, texto de teclado, credenciales ni documentos.
- VIZZ no interpreta la política como atención, comprensión, rendimiento o
  estado médico.
- PUPILA no envía mensajes, ejecuta acciones ni decide por los usuarios.
- La ventana transparente todavía es un contrato de presentación; no se instala
  una ventana real hasta probar transporte, permisos, cancelación y foco.

## Próxima decisión

Elegir un único transporte loopback para un host real y demostrar primero el
modo observador. El criterio de avance será una prueba de no interferencia y
replay, no la cantidad de funciones añadidas.
