# Informe de integración 092

## Avance entregable

Se añadió un vertical slice ejecutable: un plan de composición IRIS pasa por
`iris_farmaksia_adapter.py` y produce una representación FARMAKSIA admitida,
con orden autoral, identidad separada por tipo, alternativas, restricciones,
verificación y procedencia. Los contratos negativos demuestran que no se
aceptan órdenes alteradas, selección inexistente, verificación falsa ni
optimalidad estética.

## Decisiones

1. IRIS sigue siendo la autoridad de composición y verificación.
2. FARMAKSIA recibe un resultado normalizado, no el estado interno completo de
   IRIS ni rutas de máquina.
3. `OPTIMAL` se conserva como estado relativo al objetivo declarado.
4. La distinción obra/registro/contexto es parte de identidad, no sólo de UI.

## Verificación ejecutada

- Adaptador: `IRIS_FARMAKSIA_ADAPTER_VERIFIED`.
- Contrato FARMAKSIA: `IRIS_FARMAKSIA_CONTRACT_TESTS_PASSED`.
- La referencia privada de IRIS no se copia ni se ejecuta desde FARMAKSIA;
  su verificación queda a cargo de su propio repositorio.
- Contrato FARMAKSIA existente 068: contrato y kill tests pasaron.
- `pytest -q` global no es utilizable sin una corrección previa del harness:
  durante la colección importa scripts repetidos (`run_contract_test` y
  `run_kill_test`) desde experimentos distintos. No se presenta como fallo de
  esta integración ni se oculta; las pruebas contractuales directas sí pasan.

## Límites

No se afirma interoperabilidad productiva, persistencia, firma, broker,
evaluación humana ni calidad curatorial. Tampoco se incluye el motor privado
de IRIS ni se mezclan cambios locales preexistentes del checkout principal.
