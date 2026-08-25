# Resultados VIZZ 044

Estado: `EXPLORATORY_IMPLEMENTED`.

Verificaciones ejecutadas el 25-08-2026:

- `run_contract_test.py` → `VIZZ_044_OPTICAL_CONTRACT_VALID`.
- `validate_provenance.py` → `PROVENANCE_VALID` (4 entidades, 1 actividad,
  1 consulta).
- prueba de apertura/redibujado Tkinter con el preset de astigmatismo →
  `VIZZ_044_GUI_SMOKE_VALID`.
- suite completa `research/tools/run_suite.py` → `SUITE_VALID`.

La primera versión correcta del modelo comprueba computacionalmente:

- una pupila finita produce varios rayos por punto de pantalla;
- el modelo normal enfoca esos rayos sobre la retina a 72 cm;
- la proyección retinal invierte los signos X/Y;
- miopía e hipermetropía desplazan el foco delante/detrás de la retina;
- una pupila mayor amplifica el desenfoque;
- astigmatismo produce dos distancias focales meridionales.

No se han usado personas, cámara, vídeo ni datos clínicos.
