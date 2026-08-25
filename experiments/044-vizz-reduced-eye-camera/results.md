# Resultados VIZZ 044

Estado: `EXPLORATORY_IMPLEMENTED`.

Verificaciones ejecutadas el 25-08-2026:

- `run_contract_test.py` → `VIZZ_044_OPTICAL_CONTRACT_VALID`.
- `validate_provenance.py` → `PROVENANCE_VALID` (4 entidades, 1 actividad,
  1 consulta).
- prueba de apertura/redibujado Tkinter con el preset de astigmatismo →
  `VIZZ_044_GUI_SMOKE_VALID`.
- suite completa `research/tools/run_suite.py` → `SUITE_VALID`.

Corrección visual posterior:

- el tramo pantalla→ojo y el tramo lente→retina usan escalas separadas para
  que la retina no quede comprimida contra la lente;
- las flechas muestran el sentido de propagación en ambos tramos;
- la marca asimétrica `A` se proyecta de arriba-izquierda en pantalla a
  abajo-derecha en retina, además de la nube de muestras.
- la carcasa `CÁMARA / OJO REDUCIDO`, el sensor/retina y el `PUNTO FOCAL`
  aparecen como elementos visuales independientes; el foco normal se marca
  con una cruz ámbar aunque coincida con la retina.

La primera versión correcta del modelo comprueba computacionalmente:

- una pupila finita produce varios rayos por punto de pantalla;
- el modelo normal enfoca esos rayos sobre la retina a 72 cm;
- la proyección retinal invierte los signos X/Y;
- miopía e hipermetropía desplazan el foco delante/detrás de la retina;
- una pupila mayor amplifica el desenfoque;
- astigmatismo produce dos distancias focales meridionales.

No se han usado personas, cámara, vídeo ni datos clínicos.
