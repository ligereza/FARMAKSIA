# Resultados VIZZ 045

Estado: `EXPLORATORY_IMPLEMENTED`.

La escena separa explícitamente pantalla, rayos de luz, cámara/ojo reducido,
apertura, lente, punto focal y sensor/retina. El contrato comprueba la
inversión de la marca asimétrica, foco normal, miopía/hipermetropía conceptual,
desenfoque por pupila y dos meridianos astigmáticos.

No se han usado personas, cámara física, vídeo ni datos clínicos.

Verificaciones ejecutadas:

- `run_contract_test.py` → `VIZZ_045_CAMERA_OPTICAL_CONTRACT_VALID`.
- `validate_provenance.py` → `PROVENANCE_VALID`.
- prueba GUI con foco normal y astigmatismo → `VIZZ_045_CAMERA_GUI_SMOKE_VALID`.
- suite completa → `SUITE_VALID`.
