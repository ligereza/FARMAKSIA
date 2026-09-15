# FARMAKSIA

FARMAKSIA es el laboratorio de investigación del conjunto de proyectos. Su
entrega principal es conocimiento reutilizable: documentos, datos con
procedencia, hipótesis, experimentos reproducibles y evidencia. No es el
runtime ni la aplicación anfitriona de las integraciones.

## Límites entre proyectos

| Proyecto | Responsabilidad |
|---|---|
| `X-ANA-X` | Motor compartido y contratos canónicos. |
| `PUPILA` | Asistencia y razonamiento perceptual/visual. |
| `LUCIDA` | Proyección hacia interfaces y adaptadores de aplicaciones. |
| `FARMAKSIA` | Investigación, experimentos, procedencia y evaluación. |

FARMAKSIA puede entregar un contrato o evidencia a otro proyecto, pero no
copia su runtime ni convierte una hipótesis en una capacidad validada. Cada
integración debe tener un consumidor definido y conservar su fuente.

## Estructura

- `research/`: literatura, decisiones, preguntas y herramientas de evaluación.
- `experiments/`: pruebas delimitadas con fixture, contrato, resultado y
  procedencia.
- `output/`: material de trabajo que no se incorpora automáticamente al
  software ni a una publicación.
- `LICENSE_POLICY.md`: límites de contenido y derechos.

Los experimentos conservan identificadores estables para que sus resultados
sean rastreables. Los más recientes que conectan superficies del sistema son:

- `090-farmaxia-adaptive-representation-layer`
- `091-lucida-pupila-visual-acceptance`
- `092-pupila-temporal-integration`
- `093-iris-representation-ordering`

Los demás estudios permanecen como evidencia histórica o líneas de
investigación; no definen por sí solos los nombres ni la arquitectura activa.

## Ejecución reproducible

Desde la raíz:

```powershell
python -m pip install -r requirements.txt
python research/tools/run_suite.py
```

Para repetir las integraciones recientes:

```powershell
python experiments/092-pupila-temporal-integration/run_integration.py
python experiments/093-iris-representation-ordering/run_experiment.py
python experiments/093-iris-representation-ordering/run_contract_test.py
```

Los fixtures de laboratorio son sintéticos salvo que una procedencia indique
lo contrario. Un resultado offline no demuestra funcionamiento con una app,
un sensor, una persona o hardware real.
